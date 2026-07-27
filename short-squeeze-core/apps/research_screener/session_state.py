"""The current operational screen: candidate store, refresh loop and session history.

Everything here is **ephemeral**. No research registry, no Batch 05 raw artifact, no Batch
08 freeze and no Batch 09 preview is read for mutation or written. Nothing persists beyond
the process except an explicitly requested export.

Refresh policy:

* a failed refresh **retains** the previous snapshot and marks it ``STALE`` with the error;
* a symbol that leaves the scanner keeps its session history and is marked
  ``NO_LONGER_IN_CURRENT_SCANNER`` rather than being destroyed;
* rule-outcome changes are recorded as *research-state changes*, never as signals.
"""

from __future__ import annotations

import os
import threading
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from . import current_eval, discovery as discovery_module
from .finviz_live import select_ranked_finviz_top_n
from .live_providers import ProviderBundle, enrich_candidate as _enrich_candidate
from .provider_session import CurrentBar, LiveProvider, SymbolCollection
from .truth import DataMode, FieldValue, Freshness, ValueStatus, known, missing

#: Default cadences. Both are configurable and both stay inside provider pacing.
DEFAULT_QUOTE_REFRESH_S = int(os.environ.get("QUOTE_REFRESH_SECONDS", "15"))
DEFAULT_SCANNER_REFRESH_S = int(os.environ.get("SCANNER_REFRESH_SECONDS", "180"))
MIN_QUOTE_REFRESH_S = 5
MIN_SCANNER_REFRESH_S = 30

#: How many candidates one refresh cycle touches.
#:
#: Each candidate costs one historical-data request, and the provider allows 60 of those
#: per rolling 10 minutes. At the 30 s default cadence there are 20 cycles in that window,
#: so 3 symbols per cycle is exactly the budget. Candidates are refreshed round-robin, so
#: a 25-name screen sweeps fully about every four minutes and every row carries its own
#: age and freshness. This is a real provider constraint, not a UI choice.
DEFAULT_SYMBOLS_PER_CYCLE = 3

#: Hard max candidates on the CURRENT screen after IBKR + Finviz top-N merge.
CURRENT_SCREEN_CAP = int(os.environ.get("CURRENT_SCREEN_CAP", "30"))
#: Max Finviz-only additions (IBKR first, then Finviz top-up to the cap).
FINVIZ_TOP_N = int(os.environ.get("FINVIZ_TOP_N", "15"))

#: Multiplier applied to refresh cadences when markets are closed.
#: Off-hours, the screener chills out to preserve API quotas (IBKR, NewsAPI, Finnhub).
OFF_HOURS_MULTIPLIER = int(os.environ.get("OFF_HOURS_REFRESH_MULTIPLIER", "4"))

#: Bounded session history, in memory only.
MAX_HISTORY_PER_SYMBOL = 100

#: Presentation-only freshness thresholds. They label a displayed age and never affect a
#: rule outcome. Overridable via FRESHNESS_CURRENT_SECONDS / FRESHNESS_DELAYED_SECONDS env.
FRESH_WITHIN_S = int(os.environ.get("FRESHNESS_CURRENT_SECONDS", "90"))
DELAYED_AFTER_S = int(os.environ.get("FRESHNESS_DELAYED_SECONDS", "600"))

#: Marker for a candidate that has dropped out of the latest scanner result.
NOT_IN_SCAN_LABEL = "NO LONGER IN CURRENT SCANNER"

CURRENT_MODE_LABEL = "CURRENT DISCOVERY"


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _is_market_open() -> bool:
    """True when US equity markets are likely open (Mon-Fri 9:30 AM - 4:00 PM ET).

    Uses ``zoneinfo`` (stdlib 3.9+) to handle DST correctly when available,
    otherwise falls back to a generous fixed UTC window that covers both EST
    and EDT: 13:30-21:00 UTC (8:30 AM - 5:00 PM ET).  The wider window
    intentionally includes pre-/post-market data flow without adding complexity.
    """
    now = _now()
    if now.weekday() > 4:
        return False
    try:
        from zoneinfo import ZoneInfo
        ny_now = now.astimezone(ZoneInfo("America/New_York"))
        market_open = ny_now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = ny_now.replace(hour=16, minute=0, second=0, microsecond=0)
        return market_open <= ny_now <= market_close
    except Exception:
        pass
    # Fallback: wide fixed-UTC window covering both EST and EDT
    market_open = now.replace(hour=13, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=21, minute=0, second=0, microsecond=0)
    return market_open <= now <= market_close


def _market_cadence_multiplier() -> int:
    """Return the refresh-rate multiplier for the current market state.

    1x during market hours (fastest), OFF_HOURS_MULTIPLIER otherwise.
    This conserves API quotas (IBKR 60 req/10min, NewsAPI daily limits) when
    markets are closed while staying responsive during active trading.
    """
    return 1 if _is_market_open() else OFF_HOURS_MULTIPLIER


def _iso(moment: datetime) -> str:
    return moment.astimezone(UTC).isoformat().replace("+00:00", "Z")


def classify_freshness(age_seconds: float | None) -> Freshness:
    if age_seconds is None:
        return Freshness.UNKNOWN_AGE
    if age_seconds <= FRESH_WITHIN_S:
        return Freshness.CURRENT
    if age_seconds <= DELAYED_AFTER_S:
        return Freshness.DELAYED
    return Freshness.STALE


def _quote_data_mode(label: str) -> DataMode:
    """Map the provider's own market-data type onto the display mode. Never inferred."""
    return {
        "REALTIME": DataMode.LIVE,
        "DELAYED": DataMode.DELAYED,
        "FROZEN": DataMode.HISTORICAL,
        "DELAYED_FROZEN": DataMode.DELAYED,
    }.get(label, DataMode.UNAVAILABLE)


@dataclass(slots=True)
class HistoryPoint:
    """One bounded session-history entry for a symbol."""

    at: str
    last: float | None
    counts: dict[str, int]
    research_detection: str
    market_data_mode: str
    freshness: str
    stale: bool


@dataclass(slots=True)
class RuleTransition:
    """A research-state change. Deliberately not called a signal."""

    rule_id: str
    previous_outcome: str
    current_outcome: str
    changed_at: str
    evidence_provider: str | None = None
    evidence_id: str | None = None
    reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "previous_outcome": self.previous_outcome,
            "current_outcome": self.current_outcome,
            "changed_at": self.changed_at,
            "evidence_provider": self.evidence_provider,
            "evidence_id": self.evidence_id,
            "reason": self.reason,
            "label": "Research-state change",
        }


@dataclass(slots=True)
class CandidateState:
    """Everything the application knows about one current candidate, right now."""

    candidate: discovery_module.CurrentDiscoveryCandidate
    collection: SymbolCollection | None = None
    evaluation: current_eval.CurrentEvaluation | None = None
    snapshot_at: str | None = None
    stale: bool = False
    stale_reason: str | None = None
    last_error: str | None = None
    history: list[HistoryPoint] = field(default_factory=list)
    transitions: list[RuleTransition] = field(default_factory=list)
    last_outcomes: dict[str, str] = field(default_factory=dict)
    _sec_data: dict[str, Any] | None = None

    @property
    def symbol(self) -> str:
        return self.candidate.symbol


# ------------------------------------------------------------------- fields


def _not_configured(reason: str, code: str) -> FieldValue:
    return missing(
        ValueStatus.NOT_CONFIGURED, reason, reason_code=code,
        data_mode=DataMode.UNAVAILABLE, freshness=Freshness.NOT_APPLICABLE,
    )


def _unknown(reason: str, code: str, provider: str = "IBKR") -> FieldValue:
    return missing(
        ValueStatus.UNKNOWN, reason, reason_code=code, provider=provider,
        data_mode=DataMode.UNAVAILABLE, freshness=Freshness.NOT_APPLICABLE,
    )


def _permission_unavailable(reason: str, code: str) -> FieldValue:
    return missing(
        ValueStatus.UNAVAILABLE, reason, reason_code=code, provider="IBKR",
        data_mode=DataMode.UNAVAILABLE, freshness=Freshness.NOT_APPLICABLE,
    )


def quote_fields(
    state: CandidateState, *, freshness: Freshness, age_seconds: float | None
) -> dict[str, FieldValue]:
    """The quote block. Every price field is separate; none stands in for another."""
    collection = state.collection
    quote = collection.quote if collection else None
    label = quote.market_data_type_label if quote else "UNKNOWN"
    mode = _quote_data_mode(label)
    received = quote.received_at if quote else None

    fields: dict[str, FieldValue] = {}
    price_names = ("last", "bid", "ask", "previous_close", "open", "high", "low")
    for name in price_names:
        value = (quote.prices.get(name) if quote else None)
        if value is None:
            fields[name] = _unknown(
                f"The provider returned no {name.replace('_', ' ')} tick for this contract "
                f"under the current entitlement ({label}). No value was substituted.",
                f"QUOTE_{name.upper()}_UNAVAILABLE",
            )
        else:
            fields[name] = known(
                round(float(value), 4), unit="PRICE", provider="IBKR",
                event_time=received, received_time=received,
                freshness=freshness, data_mode=mode,
                evidence_id=f"quote:{state.symbol}:{name}:{received}",
                readiness="DISPLAY_ONLY_NOT_RULE_EVIDENCE",
            )

    # Raw provider volume: displayed, explicitly unit-unresolved, never rule evidence.
    raw_volume = quote.sizes.get("volume") if quote else None
    if raw_volume is None:
        fields["provider_volume"] = _unknown(
            "No volume tick was returned for this contract.",
            "QUOTE_VOLUME_UNAVAILABLE",
        )
    else:
        fields["provider_volume"] = known(
            float(raw_volume), unit="UNRESOLVED_PROVIDER_UNIT", provider="IBKR",
            event_time=received, received_time=received, freshness=freshness,
            data_mode=mode, evidence_id=f"quote:{state.symbol}:volume:{received}",
            readiness="NOT_ADMISSIBLE_UNRESOLVED_UNIT",
        )

    # Historical close fallback, labelled as exactly what it is.
    bars = collection.bars if collection else []
    if bars:
        # The readiness label must reflect what the evaluator actually did with this
        # level, not what it could do in principle.
        withheld = bool(state.evaluation and state.evaluation.price_scope_reason)
        fields["historical_close"] = known(
            round(float(bars[-1].close), 4), unit="PRICE", provider="IBKR",
            event_time=bars[-1].timestamp_utc, received_time=collection.retrieved_at,
            freshness=freshness, data_mode=DataMode.HISTORICAL,
            evidence_id=f"bar:{state.symbol}:{bars[-1].timestamp_utc}",
            readiness=(
                "WITHHELD_STALE_NOT_ADMISSIBLE_AS_CURRENT_PRICE"
                if withheld else "ADMISSIBLE_AS_CURRENT_PRICE_LEVEL"
            ),
        )
    else:
        fields["historical_close"] = _unknown(
            "The provider returned no completed bars for the current window.",
            "NO_BARS_RETURNED",
        )
    return fields


def short_pressure_fields(
    state: CandidateState, external_providers: ProviderBundle,
) -> dict[str, FieldValue]:
    """Short-pressure evidence including provider-supplied fundamental data."""
    collection = state.collection
    quote = collection.quote if collection else None
    label = quote.market_data_type_label if quote else "UNKNOWN"
    received = quote.received_at if quote else None
    mode = _quote_data_mode(label)

    fields: dict[str, FieldValue] = {}

    # float / shares outstanding from fundamental ratios if available
    fund = quote.fundamentals if quote else {}
    ratios_raw = fund.get("fundamental_ratios", "")
    shares_out = _parse_shares_outstanding(ratios_raw)

    if shares_out is not None:
        fields["shares_outstanding"] = known(
            float(shares_out), unit="SHARES", provider="IBKR",
            event_time=received, received_time=received,
            freshness=Freshness.CURRENT, data_mode=mode,
            evidence_id=f"fundamental:{state.symbol}:shares_outstanding:{received}",
            readiness="DISPLAY_ONLY_PROVIDER_FUNDAMENTAL",
        )
    else:
        fields["shares_outstanding"] = _not_configured(
            "Shares outstanding not available from the provider's fundamental data under "
            "the current entitlement. No value is inferred.",
            "SHARES_OUTSTANDING_NOT_AVAILABLE",
        )

    fv_row = external_providers.finviz_row(state.symbol)
    finviz_at = getattr(external_providers.finviz, "cached_at", None) or _iso(_now())

    if shares_out is None and fv_row is not None and fv_row.shares_outstanding is not None:
        fields["shares_outstanding"] = known(
            float(fv_row.shares_outstanding), unit="SHARES", provider="Finviz Elite",
            event_time=finviz_at, received_time=finviz_at,
            freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
            evidence_id=f"finviz:{state.symbol}:shares_outstanding:{finviz_at}",
            readiness="DISPLAY_ONLY_DISTINCT_FROM_FLOAT",
            provider_field="Shares Out.",
            selection_reason="ONLY_AVAILABLE",
            research_admissibility="RESEARCH_INADMISSIBLE",
        )

    if fv_row is not None and fv_row.float_shares is not None:
        float_provider_field = (
            "Shares Float"
            if "Shares Float" in fv_row.provider_columns
            else "Float"
        )
        fields["float_shares"] = known(
            float(fv_row.float_shares), unit="SHARES", provider="Finviz Elite",
            event_time=finviz_at, received_time=finviz_at,
            freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
            evidence_id=f"finviz:{state.symbol}:float:{finviz_at}",
            readiness="RESEARCH_ADMISSIBLE_PROVIDER_PUBLISHED_FLOAT",
            provider_field=float_provider_field,
            selection_reason="ONLY_AVAILABLE",
            research_admissibility="RESEARCH_ADMISSIBLE",
        )
    else:
        fields["float_shares"] = _not_configured(
            "No float provider is configured, or Finviz did not return float for this symbol. "
            "Shares outstanding from IBKR fundamentals may be available separately.",
            "FLOAT_NOT_CONFIGURED",
        )

    if fv_row is not None and fv_row.short_float_pct is not None:
        fields["short_float"] = known(
            float(fv_row.short_float_pct), unit="PERCENT", provider="Finviz Elite",
            event_time=finviz_at, received_time=finviz_at,
            freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
            evidence_id=f"finviz:{state.symbol}:short_float:{finviz_at}",
            readiness="DISPLAY_AVAILABLE_PROVIDER_SNAPSHOT_NOT_RESEARCH_ADMISSIBLE",
            provider_field="Short Float",
            selection_reason="ONLY_AVAILABLE",
            research_admissibility="RESEARCH_INADMISSIBLE",
        )
    else:
        fields["short_float"] = _not_configured(
            "No published short-interest provider is configured. Short float is not inferred.",
            "SHORT_FLOAT_NOT_CONFIGURED",
        )

    if fv_row is not None and fv_row.short_float_pct is not None:
        fields["published_short_interest"] = known(
            float(fv_row.short_float_pct), unit="PERCENT", provider="Finviz Elite",
            event_time=finviz_at, received_time=finviz_at,
            freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
            evidence_id=f"finviz:{state.symbol}:si_pct:{finviz_at}",
            readiness="RESEARCH_ADMISSIBLE_PROVIDER_SNAPSHOT",
            provider_field="Short Float",
            selection_reason="ONLY_AVAILABLE",
            research_admissibility="RESEARCH_ADMISSIBLE",
        )
    else:
        fields["published_short_interest"] = _not_configured(
            "No published short-interest provider is configured. Finviz Short Float is "
            "not available for this symbol.",
            "SHORT_INTEREST_NOT_CONFIGURED",
        )

    borrow_fee_value = external_providers.borrow_fee_for(state.symbol)
    if borrow_fee_value is not None:
        fields["borrow_fee"] = known(
            float(borrow_fee_value), unit="PERCENT_ANNUALIZED", provider="IBKR",
            event_time=_iso(_now()), received_time=_iso(_now()),
            freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
            evidence_id=f"borrow_fee:{state.symbol}:{_iso(_now())}",
            readiness="RESEARCH_ADMISSIBLE_PROVIDER_SNAPSHOT",
            provider_field="Borrow Fee (Tick 258)",
            selection_reason="SECONDARY_IBKR_REQUEST",
            research_admissibility="RESEARCH_ADMISSIBLE",
        )
    else:
        fields["borrow_fee"] = _not_configured(
            "No borrow-fee provider is configured. The provider's market-data ticks do not "
            "carry a borrow fee under this entitlement.",
            "BORROW_FEE_NOT_CONFIGURED",
        )

    if fv_row is not None and fv_row.short_ratio is not None:
        fields["short_ratio"] = known(
            float(fv_row.short_ratio), unit="RATIO", provider="Finviz Elite",
            event_time=finviz_at, received_time=finviz_at,
            freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
            evidence_id=f"finviz:{state.symbol}:short_ratio:{finviz_at}",
            readiness="DISPLAY_AVAILABLE_NOT_CANONICAL_DAYS_TO_COVER",
            provider_field="Short Ratio",
            selection_reason="ONLY_AVAILABLE",
            research_admissibility="RESEARCH_INADMISSIBLE",
        )
    else:
        fields["short_ratio"] = _not_configured(
            "Finviz Short Ratio is not available.", "SHORT_RATIO_NOT_CONFIGURED",
        )
    if fv_row is not None and fv_row.short_ratio is not None:
        fields["days_to_cover"] = known(
            float(fv_row.short_ratio), unit="DAYS", provider="Finviz Elite",
            event_time=finviz_at, received_time=finviz_at,
            freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
            evidence_id=f"finviz:{state.symbol}:dtc:{finviz_at}",
            readiness="RESEARCH_ADMISSIBLE_PROVIDER_SNAPSHOT",
            provider_field="Short Ratio",
            selection_reason="ONLY_AVAILABLE",
            research_admissibility="RESEARCH_ADMISSIBLE",
        )
    else:
        fields["days_to_cover"] = _not_configured(
            "Canonical days to cover requires published short interest and "
            "admissible average volume. Neither is currently available.",
            "DAYS_TO_COVER_NOT_AVAILABLE",
        )

    # Halt status from generic tick 49
    halted_val = quote.generics.get("halted") if quote else None
    if halted_val is not None:
        halted_bool = bool(halted_val > 0)
        fields["halted"] = known(
            1.0 if halted_bool else 0.0, unit="PROVIDER_HALT_INDICATOR", provider="IBKR",
            event_time=received, received_time=received,
            freshness=Freshness.CURRENT, data_mode=mode,
            evidence_id=f"quote:{state.symbol}:halted:{received}",
            readiness="DISPLAY_ONLY_PROVIDER_INDICATOR",
        )
    else:
        fields["halted"] = _not_configured(
            "Halt status (generic tick 49) not available under the current entitlement.",
            "HALT_NOT_CONFIGURED",
        )

    # Shortability
    indicator = quote.generics.get("shortable_indicator") if quote else None
    if indicator is None:
        fields["shortable"] = _permission_unavailable(
            "The provider returned no shortability tick (generic tick 236) for this "
            "contract under the current entitlement. This is reported as unavailable, "
            "not as zero and not as 'not shortable'.",
            "SHORTABILITY_PERMISSION_UNAVAILABLE",
        )
    else:
        fields["shortable"] = known(
            float(indicator), unit="PROVIDER_SHORTABLE_INDICATOR", provider="IBKR",
            event_time=quote.received_at, received_time=quote.received_at,
            freshness=Freshness.CURRENT, data_mode=mode,
            evidence_id=f"quote:{state.symbol}:shortable:{quote.received_at}",
            readiness="DISPLAY_ONLY_RAW_PROVIDER_INDICATOR",
        )

    shares = quote.sizes.get("shortable_shares") if quote else None
    if shares is None:
        fields["borrow_availability"] = _permission_unavailable(
            "The provider returned no shortable-shares tick for this contract under the "
            "current entitlement. No borrow availability is inferred.",
            "BORROW_AVAILABILITY_PERMISSION_UNAVAILABLE",
        )
    else:
        fields["borrow_availability"] = known(
            float(shares), unit="SHARES", provider="IBKR",
            event_time=quote.received_at, received_time=quote.received_at,
            freshness=Freshness.CURRENT, data_mode=mode,
            evidence_id=f"quote:{state.symbol}:shortable_shares:{quote.received_at}",
            readiness="DISPLAY_ONLY_NOT_RULE_EVIDENCE",
        )
    return fields


def _parse_shares_outstanding(raw: str) -> int | None:
    """Parse IBKR fundamental ratios string for shares outstanding.

    The format is semicolon-separated key=value pairs like:
    MKTCAP=1.5B;SHARESOUT=50M;...
    """
    if not raw:
        return None
    try:
        for part in raw.split(";"):
            part = part.strip()
            if not part:
                continue
            if "=" in part:
                key, val = part.split("=", 1)
                key = key.strip().upper()
                val = val.strip().upper()
                if key in ("SHARESOUT", "SHARES"):
                    return _parse_numeric_suffix(val)
    except Exception:
        return None
    return None


def _parse_numeric_suffix(val: str) -> int | None:
    """Parse values like '50M', '1.5B', '500K', '1234' into integer shares."""
    multipliers = {"K": 1000, "M": 1_000_000, "B": 1_000_000_000, "T": 1_000_000_000_000}
    try:
        if not val:
            return None
        suffix = val[-1].upper()
        if suffix in multipliers:
            return int(float(val[:-1]) * multipliers[suffix])
        return int(float(val))
    except (ValueError, TypeError):
        return None


def catalyst_fields(
    state: CandidateState, external_providers: ProviderBundle,
) -> dict[str, FieldValue]:
    """Catalyst evidence from SEC EDGAR, news aggregation, and optional sentiment."""
    fields: dict[str, FieldValue] = {}

    sec_data = external_providers.sec_for(state.symbol)
    if sec_data is None:
        fields["sec_filings"] = _not_configured(
            "SEC EDGAR has not been refreshed for this symbol in this runtime.",
            "SEC_EDGAR_NOT_REFRESHED",
        )
    elif sec_data.get("error"):
        fields["sec_filings"] = missing(
            ValueStatus.NOT_CONFIGURED, sec_data["error"],
            reason_code="SEC_EDGAR_ERROR", provider="SEC_EDGAR",
            data_mode=DataMode.UNAVAILABLE, freshness=Freshness.NOT_APPLICABLE,
        )
    elif sec_data.get("available"):
        fields["sec_filings"] = known(
            sec_data["catalyst_count"], unit="FILING_COUNT", provider="SEC_EDGAR",
            event_time=sec_data.get("retrieved_at"), received_time=sec_data.get("retrieved_at"),
            freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
            evidence_id=f"sec:{state.symbol}:filings:{sec_data.get('retrieved_at')}",
            readiness="DISPLAY_ONLY_PUBLIC_FILINGS",
        )
        state._sec_data = sec_data
    else:
        fields["sec_filings"] = missing(
            ValueStatus.NOT_CONFIGURED,
            "No SEC filings found for this symbol from the public EDGAR API.",
            reason_code="SEC_FILINGS_NONE", provider="SEC_EDGAR",
            data_mode=DataMode.UNAVAILABLE, freshness=Freshness.NOT_APPLICABLE,
        )

    news_headlines = external_providers.news_for(state.symbol)
    news_providers_seen = sorted({
        str(item.get("provider", "UNKNOWN")) for item in news_headlines
    })

    if news_headlines:
        provider_label = ", ".join(news_providers_seen)
        fields["catalyst"] = _unknown(
            "Headlines are available for display, but headline presence alone is not "
            "canonical catalyst evidence.",
            "CATALYST_HEADLINES_NOT_SUFFICIENT",
            provider=provider_label,
        )
        fields["news_count"] = known(
            len(news_headlines), unit="HEADLINE_COUNT", provider=provider_label,
            event_time=_iso(_now()), received_time=_iso(_now()),
            freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
            evidence_id=f"news:{state.symbol}:count:{_iso(_now())}",
            readiness="DISPLAY_ONLY",
        )
        timestamps = sorted(
            [h.get("timestamp", "") for h in news_headlines if h.get("timestamp")],
            reverse=True,
        )
        if timestamps:
            latest = timestamps[0]
            fields["latest_news_at"] = known(
                latest, unit="TIMESTAMP", provider=provider_label,
                event_time=_iso(_now()), received_time=_iso(_now()),
                freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
                evidence_id=f"news:{state.symbol}:latest:{_iso(_now())}",
                readiness="DISPLAY_ONLY",
            )

        sentiment_result = None
        try:
            analyzer = getattr(external_providers, "_sentiment_analyzer", None)
            if analyzer is not None and getattr(analyzer, "enabled", False):
                sentiment_result = analyzer.analyze_symbol(state.symbol, news_headlines)
        except Exception:
            pass

        if sentiment_result is not None and sentiment_result.get("analyzed_count", 0) > 0:
            fields["sentiment"] = known(
                sentiment_result["dominant_label"], unit="LABEL",
                provider=f"FinBERT ({sentiment_result['model_id']})",
                event_time=sentiment_result["evaluated_at"],
                received_time=_iso(_now()),
                freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
                evidence_id=f"sentiment:{state.symbol}:{_iso(_now())}",
                readiness="DISPLAY_ONLY_EXPERIMENTAL_SENTIMENT",
            )
            fields["sentiment_positive_count"] = known(
                sentiment_result["positive_count"], unit="COUNT", provider="FinBERT",
                event_time=sentiment_result["evaluated_at"], received_time=_iso(_now()),
                freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
                evidence_id=f"sentiment:{state.symbol}:positive:{_iso(_now())}",
                readiness="DISPLAY_ONLY",
            )
            fields["sentiment_neutral_count"] = known(
                sentiment_result["neutral_count"], unit="COUNT", provider="FinBERT",
                event_time=sentiment_result["evaluated_at"], received_time=_iso(_now()),
                freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
                evidence_id=f"sentiment:{state.symbol}:neutral:{_iso(_now())}",
                readiness="DISPLAY_ONLY",
            )
            fields["sentiment_negative_count"] = known(
                sentiment_result["negative_count"], unit="COUNT", provider="FinBERT",
                event_time=sentiment_result["evaluated_at"], received_time=_iso(_now()),
                freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
                evidence_id=f"sentiment:{state.symbol}:negative:{_iso(_now())}",
                readiness="DISPLAY_ONLY",
            )
            fields["sentiment_model_id"] = known(
                sentiment_result["model_id"], unit="MODEL_ID", provider="FinBERT",
                event_time=sentiment_result["evaluated_at"], received_time=_iso(_now()),
                freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
                evidence_id=f"sentiment:{state.symbol}:model:{_iso(_now())}",
                readiness="DISPLAY_ONLY",
            )
        else:
            fields["sentiment"] = _not_configured(
                "Sentiment analysis is not configured or pending. "
                "FinBERT sentiment requires a local model and is not deployed in cloud.",
                "SENTIMENT_NOT_CONFIGURED",
            )
    else:
        fields["catalyst"] = _not_configured(
            "No news headlines found from any configured provider. "
            "SEC EDGAR filings are available separately.",
            "CATALYST_NOT_CONFIGURED",
        )
        fields["news_count"] = _not_configured(
            "No news provider data has been refreshed for this symbol.",
            "NEWS_NOT_CONFIGURED",
        )
        fields["sentiment"] = _not_configured(
            "No sentiment provider is configured. FinBERT sentiment requires a "
            "local model and is not deployed in cloud.",
            "SENTIMENT_NOT_CONFIGURED",
        )

    # Catalyst age: hours since most recent news or SEC filing
    timestamps: list[float] = []
    for item in news_headlines:
        ts = item.get("timestamp") or item.get("published_at")
        if ts:
            try:
                dt = _parse_iso(str(ts), _now())
                timestamps.append(dt.timestamp())
            except (ValueError, TypeError):
                continue
    sec_data = fields.get("sec_filings")
    if sec_data and sec_data.status == ValueStatus.KNOWN:
        try:
            sec_ts = sec_data.event_time
            if sec_ts:
                timestamps.append(_parse_iso(str(sec_ts), _now()).timestamp())
        except (ValueError, TypeError):
            pass
    if timestamps:
        latest_epoch = max(timestamps)
        age_hours = max(0.0, (_now().timestamp() - latest_epoch) / 3600.0)
        fields["catalyst_age_hours"] = known(
            round(age_hours, 2), unit="HOURS", provider="COMPUTED",
            event_time=_iso(_now()), received_time=_iso(_now()),
            freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
            evidence_id=f"catalyst_age:{state.symbol}:{_iso(_now())}",
            readiness="RESEARCH_ADMISSIBLE_COMPUTED_METRIC",
            research_admissibility="RESEARCH_ADMISSIBLE",
        )

    return fields


_sec_cache: dict[str, dict[str, Any]] = {}


def _fetch_sec_filings(symbol: str) -> dict[str, Any]:
    """Fetch SEC EDGAR filings with in-memory cache."""
    cached = _sec_cache.get(symbol)
    if cached is not None:
        return cached
    try:
        from .sec_edgar import get_edgar_client
        client = get_edgar_client()
        result = client.has_recent_catalyst_filing(symbol)
        _sec_cache[symbol] = result
        return result
    except Exception as exc:
        error_result = {
            "available": False, "catalyst_count": 0,
            "most_recent": None, "all_filings": [],
            "cik": None, "company_name": None,
            "error": f"SEC EDGAR not available: {type(exc).__name__}: {exc}",
            "retrieved_at": _iso(_now()), "provider": "SEC_EDGAR",
        }
        _sec_cache[symbol] = error_result
        return error_result


def metric_fields(
    state: CandidateState, external_providers: ProviderBundle,
) -> dict[str, FieldValue]:
    """The two canonical momentum metrics, as evidence-bearing cells."""
    evaluation = state.evaluation
    fields: dict[str, FieldValue] = {}
    if evaluation is not None and evaluation.metric is not None and evaluation.metric.value is not None:
        metric = evaluation.metric
        fields["percentage_change"] = known(
            round(float(metric.value), 4), unit=str(metric.unit), provider="IBKR",
            event_time=_iso(evaluation.as_of), received_time=state.snapshot_at,
            freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
            evidence_id=str(metric.deterministic_id),
            readiness=str(metric.quality.state),
        )
    else:
        reason = "No canonical PERCENTAGE_RETURN could be constructed from current evidence."
        if evaluation is not None and evaluation.metric_unavailable_reason:
            reason = evaluation.metric_unavailable_reason
        elif evaluation is not None and evaluation.metric is not None:
            # The canonical metric record exists but carries no value; report its own
            # diagnostic rather than inventing a reason.
            codes = [
                str(getattr(item, "code", item))
                for item in getattr(evaluation.metric, "diagnostics", ()) or ()
            ]
            reason = (
                "The canonical PERCENTAGE_RETURN record was constructed but carries no "
                "value. Provider diagnostics: " + (", ".join(codes) or "none recorded") + "."
            )
        fields["percentage_change"] = _unknown(reason, "PERCENTAGE_RETURN_UNAVAILABLE")

    fv_row = external_providers.finviz_row(state.symbol)
    finviz_at = getattr(external_providers.finviz, "cached_at", None) or _iso(_now())
    if fv_row is not None and fv_row.rel_volume is not None:
        fields["relative_volume"] = known(
            float(fv_row.rel_volume), unit="RATIO", provider="Finviz Elite",
            event_time=finviz_at, received_time=finviz_at,
            freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
            evidence_id=f"finviz:{state.symbol}:rel_volume:{finviz_at}",
            readiness="RESEARCH_ADMISSIBLE_PROVIDER_SNAPSHOT",
            provider_field="Relative Volume",
            selection_reason="ONLY_AVAILABLE",
            research_admissibility="RESEARCH_ADMISSIBLE",
        )
    else:
        fields["relative_volume"] = _unknown(
            current_eval.CURRENT_VOLUME_RATIONALE, current_eval.CURRENT_VOLUME_STATUS
        )

    bars = state.collection.bars if state.collection else []
    if len(bars) >= 2:
        try:
            from squeeze_core.metrics.bar_acceleration import compute_bar_acceleration
            accel = compute_bar_acceleration(
                [{"open": b.open, "close": b.close} for b in bars],
            )
            if accel.value is not None:
                fields["completed_bar_acceleration"] = known(
                    float(accel.value), unit="PERCENTAGE_POINTS", provider="IBKR",
                    event_time=_iso(evaluation.as_of) if evaluation else _iso(_now()),
                    received_time=state.snapshot_at,
                    freshness=Freshness.CURRENT, data_mode=DataMode.HISTORICAL,
                    evidence_id=f"bar_accel:{state.symbol}:{_iso(_now())}",
                    readiness="RESEARCH_ADMISSIBLE_COMPUTED_METRIC",
                    research_admissibility="RESEARCH_ADMISSIBLE",
                )
        except Exception:
            pass

    return fields


# ------------------------------------------------------------------ session


class ScreenerSession:
    """The in-memory current operational screen."""

    def __init__(
        self,
        provider: LiveProvider | None = None,
        *,
        quote_refresh_s: int = DEFAULT_QUOTE_REFRESH_S,
        scanner_refresh_s: int = DEFAULT_SCANNER_REFRESH_S,
        symbols_per_cycle: int = DEFAULT_SYMBOLS_PER_CYCLE,
        external_providers: ProviderBundle | None = None,
    ) -> None:
        self.provider = provider or LiveProvider()
        self.external_providers = external_providers or ProviderBundle.offline()
        self.quote_refresh_s = max(MIN_QUOTE_REFRESH_S, int(quote_refresh_s))
        self.scanner_refresh_s = max(MIN_SCANNER_REFRESH_S, int(scanner_refresh_s))
        self.symbols_per_cycle = max(1, int(symbols_per_cycle))
        self._cursor = 0
        self.profile_id = "BROAD_MOVERS"
        self.auto_refresh = False
        self.states: dict[str, CandidateState] = {}
        self.last_discovery_at: str | None = None
        self.last_refresh_at: str | None = None
        self.next_refresh_at: str | None = None
        self.last_refresh_error: str | None = None
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._policy = None
        self._profiles = None
        #: Wall-clock timestamp of the last discovery scan. Bootstrap seeds this
        #: so ``_loop`` does not immediately rediscover after a successful boot scan.
        self._last_scan_ts: float = 0.0

    # ------------------------------------------------------------- policies

    @property
    def policy(self):
        if self._policy is None:
            self._policy = current_eval.load_policy()
        return self._policy

    @property
    def profiles(self) -> dict[str, discovery_module.DiscoveryProfile]:
        if self._profiles is None:
            self._profiles = discovery_module.build_profiles(self.policy)
        return self._profiles

    # ------------------------------------------------------------ discovery

    def set_profile(self, profile_id: str) -> None:
        if profile_id in self.profiles:
            self.profile_id = profile_id

    def refresh_discovery(self, profile_id: str | None = None) -> dict[str, Any]:
        """Re-run the scanner and rebuild the curated CURRENT screen.

        Finviz Elite export is fetched to warm the enrichment cache, but only a
        ranked top-N of Finviz rows (not already in the IBKR found set) become
        candidates. The active set is rebuilt each discovery from IBKR found +
        Finviz top-N under ``CURRENT_SCREEN_CAP``; history is retained for
        symbols that remain, and manual symbols are always kept.
        """
        profile_id = profile_id or self.profile_id
        profile = self.profiles.get(profile_id)
        if profile is None:
            return {"discovered": 0, "error": f"unknown discovery profile {profile_id!r}"}
        if not profile.uses_provider_scanner:
            self.last_discovery_at = _iso(_now())
            return {"discovered": len(self.states), "manual": True}

        found = self.provider.run_discovery(profile) or []
        now = _iso(_now())
        self.last_discovery_at = now

        # Warm Finviz enrichment cache; select only ranked top-N for candidates.
        finviz_rows: list[Any] = []
        try:
            if self.external_providers.finviz.configured:
                self.external_providers.finviz.fetch_screener(force=True)
                finviz_rows = self.external_providers.finviz.get_cached_rows() or []
        except Exception:
            pass  # Finviz is supplementary; failure must not break IBKR discovery

        with self._lock:
            if not found and not finviz_rows:
                # A scanner failure must not destroy the existing screen.
                for state in self.states.values():
                    state.candidate.in_current_scan = False
                return {
                    "discovered": 0,
                    "error": self.provider.scanner_status.detail,
                    "retained": len(self.states),
                }

            screen_cap = max(1, CURRENT_SCREEN_CAP)
            finviz_top_n = max(0, FINVIZ_TOP_N)

            # IBKR first; truncate if discovery alone exceeds the cap.
            ibkr_candidates = list(found[:screen_cap])
            ibkr_symbols = {candidate.symbol for candidate in ibkr_candidates}

            finviz_slots = max(0, min(finviz_top_n, screen_cap - len(ibkr_candidates)))
            ranked_finviz = select_ranked_finviz_top_n(
                finviz_rows, exclude=ibkr_symbols, limit=finviz_slots,
            )
            finviz_symbols = {row.ticker for row in ranked_finviz if row.ticker}

            selected = ibkr_symbols | finviz_symbols
            manual_symbols = {
                symbol
                for symbol, state in self.states.items()
                if state.candidate.profile_id == "MANUAL_SYMBOL"
            }
            keep = selected | manual_symbols

            previous = self.states
            rebuilt: dict[str, CandidateState] = {}

            for candidate in ibkr_candidates:
                existing = previous.get(candidate.symbol)
                if existing is None:
                    rebuilt[candidate.symbol] = CandidateState(candidate=candidate)
                else:
                    existing.candidate.provider_rank = candidate.provider_rank
                    existing.candidate.discovered_at = candidate.discovered_at
                    existing.candidate.in_current_scan = True
                    existing.candidate.profile_id = candidate.profile_id
                    if existing.candidate.con_id is None:
                        existing.candidate.con_id = candidate.con_id
                    rebuilt[candidate.symbol] = existing

            finviz_added = 0
            for fv_row in ranked_finviz:
                fv_sym = fv_row.ticker
                if not fv_sym or fv_sym in rebuilt:
                    continue
                existing = previous.get(fv_sym)
                if existing is None:
                    rebuilt[fv_sym] = CandidateState(
                        candidate=discovery_module.CurrentDiscoveryCandidate(
                            symbol=fv_sym, profile_id="FINVIZ_SCREENER",
                            long_name=fv_row.company or "",
                        )
                    )
                else:
                    existing.candidate.in_current_scan = True
                    existing.candidate.profile_id = "FINVIZ_SCREENER"
                    if fv_row.company and not existing.candidate.long_name:
                        existing.candidate.long_name = fv_row.company
                    rebuilt[fv_sym] = existing
                finviz_added += 1

            for symbol in manual_symbols:
                if symbol in rebuilt:
                    continue
                state = previous[symbol]
                state.candidate.in_current_scan = symbol in ibkr_symbols
                rebuilt[symbol] = state

            # Drop states no longer selected (old Finviz flood / left the scan).
            self.states = {symbol: rebuilt[symbol] for symbol in rebuilt if symbol in keep}

            return {
                "discovered": len(ibkr_candidates) + finviz_added,
                "ibkr": len(ibkr_candidates),
                "finviz": finviz_added,
                "cap": screen_cap,
                "error": None,
            }

    def add_manual_symbols(self, symbols: list[str]) -> list[str]:
        """Add user-entered tickers. Invalid input is reported, never silently dropped."""
        from .live import InvalidSymbolError, normalize_symbol

        added: list[str] = []
        with self._lock:
            for raw in symbols:
                try:
                    symbol = normalize_symbol(raw)
                except InvalidSymbolError:
                    continue
                if symbol not in self.states:
                    self.states[symbol] = CandidateState(
                        candidate=discovery_module.CurrentDiscoveryCandidate(
                            symbol=symbol, profile_id="MANUAL_SYMBOL"
                        )
                    )
                added.append(symbol)
        return added

    def clear(self) -> None:
        with self._lock:
            self.states.clear()

    # -------------------------------------------------------------- refresh

    def refresh_symbol(self, symbol: str) -> CandidateState | None:
        """One read-only pass. On failure the previous snapshot is retained as STALE."""
        with self._lock:
            state = self.states.get(symbol)
        if state is None:
            return None

        collection = self.provider.collect_symbol(symbol)
        now = _now()
        if not collection.resolved or not collection.bars:
            reason = collection.reason or (
                "The provider accepted the request but returned no completed bars for this "
                "window. No value was substituted."
            )
            with self._lock:
                state.last_error = reason
                if state.collection is not None:
                    # Retain the working snapshot; mark it stale rather than erasing it.
                    state.stale = True
                    state.stale_reason = reason
                else:
                    state.collection = collection
                    state.snapshot_at = _iso(now)
                    state.stale = True
                    state.stale_reason = reason
            return state

        try:
            finviz_row = self.external_providers.finviz_row(symbol)
            finviz_status = self.external_providers.status().get("finviz", {})
            finviz_at_raw = getattr(
                self.external_providers.finviz, "cached_at", None
            )
            finviz_admissible = bool(
                finviz_status.get("fetched")
                and finviz_row is not None
                and finviz_row.float_shares is not None
                and finviz_at_raw
            )
            evaluation = current_eval.evaluate_current(
                symbol, collection.bars, now=now,
                retrieved_at=_parse_iso(collection.retrieved_at, now),
                policy=self.policy,
                finviz_float_shares=(
                    float(finviz_row.float_shares) if finviz_admissible else None
                ),
                finviz_retrieved_at=(
                    _parse_iso(finviz_at_raw, now) if finviz_admissible else None
                ),
            )
        except Exception as exc:  # noqa: BLE001 - evaluation faults degrade, never crash
            with self._lock:
                state.collection = collection
                state.snapshot_at = _iso(now)
                state.stale = True
                state.stale_reason = (
                    f"Current evidence was retrieved but could not be evaluated: "
                    f"{type(exc).__name__}: {exc}"
                )
                state.last_error = state.stale_reason
            return state

        with self._lock:
            state.candidate.con_id = state.candidate.con_id or collection.con_id
            state.candidate.long_name = state.candidate.long_name or collection.long_name
            state.candidate.primary_exchange = (
                state.candidate.primary_exchange or collection.primary_exchange
            )
            state.candidate.currency = state.candidate.currency or collection.currency
            state.collection = collection
            state.evaluation = evaluation
            state.snapshot_at = _iso(now)
            state.stale = False
            state.stale_reason = None
            state.last_error = None
            self._record_transitions(state, evaluation, _iso(now))
            self._record_history(state)
        return state

    def _record_transitions(self, state: CandidateState, evaluation, at: str) -> None:
        current = {item.rule_id: str(item.outcome) for item in evaluation.rule_results}
        results = {item.rule_id: item for item in evaluation.rule_results}
        providers: dict[str, str] = {}
        for item in evaluation.request.input_observations:
            providers[str(item.observation_id)] = item.provenance.provider
        for item in evaluation.request.input_metrics:
            providers[str(item.deterministic_id)] = str(getattr(item, "provider", ""))
        if state.last_outcomes:
            for rule_id, outcome in current.items():
                previous = state.last_outcomes.get(rule_id)
                if previous is not None and previous != outcome:
                    result = results[rule_id]
                    evidence_ids = (
                        list(result.input_metric_ids or ())
                        + list(result.input_observation_ids or ())
                        + list(result.readiness_snapshot_ids or ())
                    )
                    evidence_id = str(evidence_ids[0]) if evidence_ids else None
                    state.transitions.append(
                        RuleTransition(
                            rule_id=rule_id, previous_outcome=previous,
                            current_outcome=outcome, changed_at=at,
                            evidence_provider=providers.get(evidence_id or ""),
                            evidence_id=evidence_id,
                            reason=str(result.explanation_code),
                        )
                    )
            del state.transitions[:-MAX_HISTORY_PER_SYMBOL]
        state.last_outcomes = current

    def _record_history(self, state: CandidateState) -> None:
        row = self.row_for(state)
        last = row["fields"]["last"]["value"]
        if last is None:
            last = row["fields"]["historical_close"]["value"]
        state.history.append(
            HistoryPoint(
                at=state.snapshot_at or _iso(_now()),
                last=last,
                counts=dict(row["phase3a"]["counts"]),
                research_detection=row["research_detection"]["status"],
                market_data_mode=row["market_data_mode"],
                freshness=row["freshness"],
                stale=bool(state.stale),
            )
        )
        del state.history[:-MAX_HISTORY_PER_SYMBOL]

    def refresh_all(self, *, limit: int | None = None) -> dict[str, Any]:
        """Refresh one round-robin slice of the screen, inside the provider pacing budget.

        Also triggers Finviz Elite and NewsAPI provider-side refreshes concurrently
        where safe. Individual failures stay per-symbol.
        """
        with self._lock:
            all_symbols = list(self.states)
        if not all_symbols:
            self.last_refresh_at = _iso(_now())
            return {"refreshed": 0, "errors": [], "at": self.last_refresh_at,
                    "swept": 0, "total": 0}

        take = min(len(all_symbols), limit if limit is not None else self.symbols_per_cycle)
        start = self._cursor % len(all_symbols)
        symbols = [all_symbols[(start + offset) % len(all_symbols)] for offset in range(take)]
        self._cursor = (start + take) % len(all_symbols)
        provider_refresh = self.external_providers.refresh_all(symbols)

        errors: list[dict[str, str]] = []
        for symbol in symbols:
            state = self.refresh_symbol(symbol)
            if state is not None and state.stale and state.stale_reason:
                errors.append({"symbol": symbol, "error": state.stale_reason})
        now = _now()
        self.last_refresh_at = _iso(now)
        self.next_refresh_at = _iso(
            now.replace(microsecond=0)
        ) if not self.auto_refresh else _iso(
            datetime.fromtimestamp(now.timestamp() + self.quote_refresh_s, tz=UTC)
        )
        self.last_refresh_error = errors[0]["error"] if errors else None

        from . import data_logger

        data_logger.log_refresh_event({
            "refreshed": len(symbols), "errors": errors, "at": self.last_refresh_at,
            "total": len(all_symbols), "providers": self.external_providers.status(),
        })
        rows = self.rows()
        if rows:
            data_logger.log_screener_snapshot(rows, label="refresh_cycle")

        return {
            "refreshed": len(symbols), "errors": errors, "at": self.last_refresh_at,
            "swept": len(symbols), "total": len(all_symbols),
            "symbols": symbols,
            "providers": self.external_providers.status(),
            "provider_refresh": provider_refresh,
            "pacing": self.provider.pacing_state()
            if hasattr(self.provider, "pacing_state") else None,
        }

    # ---------------------------------------------------------- auto refresh

    def note_discovery_scan(self, when: float | None = None) -> None:
        """Record that discovery just ran (e.g. bootstrap) so ``_loop`` skips a duplicate."""
        self._last_scan_ts = (
            float(when) if when is not None else datetime.now(tz=UTC).timestamp()
        )

    def start_auto_refresh(self) -> None:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                self.auto_refresh = True
                return
            self._stop.clear()
            self.auto_refresh = True
            self._thread = threading.Thread(
                target=self._loop, name="screener-auto-refresh", daemon=True
            )
            self._thread.start()

    def stop_auto_refresh(self) -> None:
        self.auto_refresh = False
        self._stop.set()

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                now = datetime.now(tz=UTC).timestamp()
                multiplier = _market_cadence_multiplier()
                quote_sleep = self.quote_refresh_s * multiplier
                scan_sleep = self.scanner_refresh_s * multiplier

                profile = self.profiles.get(self.profile_id)
                if (
                    profile is not None
                    and profile.uses_provider_scanner
                    and now - self._last_scan_ts >= scan_sleep
                ):
                    self.refresh_discovery()
                    self._last_scan_ts = now
                self.refresh_all()
            except Exception as exc:  # noqa: BLE001 - the loop must never die
                self.last_refresh_error = f"{type(exc).__name__}: {exc}"
            self._stop.wait(quote_sleep)

    # ------------------------------------------------------------------ rows

    def row_for(self, state: CandidateState) -> dict[str, Any]:
        """One screener row. Every cell carries provenance; missing is never zero."""
        snapshot_at = state.snapshot_at
        now = _now()
        # Freshness describes the *observation*, not the retrieval. Fetching a Friday
        # close on a Saturday is a fresh request over stale evidence, and calling that
        # CURRENT would be exactly the kind of substitution this application refuses.
        observation_at = (
            _iso(state.evaluation.as_of) if state.evaluation is not None else snapshot_at
        )
        age = None
        if observation_at:
            age = (now - _parse_iso(observation_at, now)).total_seconds()
        retrieval_age = None
        if snapshot_at:
            retrieval_age = (now - _parse_iso(snapshot_at, now)).total_seconds()
        freshness = Freshness.STALE if state.stale else classify_freshness(age)

        quote = state.collection.quote if state.collection else None
        market_data_mode = quote.market_data_type_label if quote else "UNKNOWN"

        fields: dict[str, FieldValue] = {}
        fields.update(quote_fields(state, freshness=freshness, age_seconds=age))
        fields.update(metric_fields(state, self.external_providers))
        fields.update(short_pressure_fields(state, self.external_providers))
        fields.update(catalyst_fields(state, self.external_providers))
        fields = _enrich_candidate(
            state.symbol, fields,
            finviz=self.external_providers.finviz_row(state.symbol),
            finnhub_price=self.external_providers.finnhub_price_for(state.symbol),
        )

        evaluation = state.evaluation
        total = len(self.policy.enabled_rule_ids)
        if evaluation is None:
            counts = {"PASS": 0, "FAIL": 0, "UNKNOWN": total, "CONFLICTED": 0,
                      "INSUFFICIENT_DATA": 0, "NOT_APPLICABLE": 0}
            detection = {
                "status": "UNEVALUABLE",
                "reasons": [
                    state.stale_reason
                    or "No current evidence has been retrieved for this candidate yet."
                ],
                "preview_banner": None,
            }
            supported = 0
        else:
            counts = dict(evaluation.counts)
            detection = current_eval.research_detection(evaluation)
            supported = counts.get("PASS", 0) + counts.get("FAIL", 0)

        row = {
            "symbol": state.symbol,
            "case_id": None,
            "candidate_id": None,
            "candidate_key": state.candidate.candidate_key,
            "discovery_profile": state.candidate.profile_id,
            "discovery_source": self.profiles[state.candidate.profile_id].title
            if state.candidate.profile_id in self.profiles
            else state.candidate.profile_id,
            "provider_scanner_order": state.candidate.provider_rank,
            "in_current_scan": state.candidate.in_current_scan,
            "scan_membership_label": None
            if state.candidate.in_current_scan
            else NOT_IN_SCAN_LABEL,
            "first_seen_at": state.candidate.first_seen_at,
            "data_mode": str(_quote_data_mode(market_data_mode)),
            "market_data_mode": market_data_mode,
            "mode_label": CURRENT_MODE_LABEL,
            "fields": {name: value.as_dict() for name, value in fields.items()},
            "phase3a": {
                "counts": counts,
                "total_rules": total,
                "summary": f"{counts.get('PASS', 0)} PASS / {counts.get('FAIL', 0)} FAIL / "
                           f"{counts.get('UNKNOWN', 0)} UNKNOWN",
            },
            "research_detection": detection,
            "outcome": {
                "status": "NOT_APPLICABLE",
                "reasons": [
                    "A current candidate has no forward outcome window by construction."
                ],
            },
            "evidence_coverage": {
                "supported": supported,
                "total": total,
                "label": f"{supported} / {total} rules supported",
            },
            "sec_filings": state._sec_data if state._sec_data else None,
            "freshness": str(freshness),
            "age_seconds": None if age is None else round(age, 1),
            "age_basis": "OBSERVATION_AS_OF_INSTANT",
            "retrieval_age_seconds": None if retrieval_age is None else round(retrieval_age, 1),
            "observation_at": observation_at,
            "last_updated": observation_at,
            "snapshot_at": snapshot_at,
            "stale": bool(state.stale),
            "stale_reason": state.stale_reason,
            "bar_count": len(state.collection.bars) if state.collection else 0,
            "provider": "IBKR",
            "provider_errors": state.collection.provider_errors if state.collection else [],
            "transition_count": len(state.transitions),
            "history_count": len(state.history),
        }
        from .methodologies.projection import project_candidate
        from .trend import trend

        projected = project_candidate(row)
        projected["trend"] = trend(
            [point.last for point in state.history],
            field="last",
        )
        return projected

    def rows(self) -> list[dict[str, Any]]:
        with self._lock:
            states = list(self.states.values())
        return [self.row_for(state) for state in states]

    def detail(self, symbol: str) -> dict[str, Any] | None:
        with self._lock:
            state = self.states.get(symbol.strip().upper())
        if state is None:
            return None
        row = self.row_for(state)
        evaluation = state.evaluation
        rule_order = list(self.policy.enabled_rule_ids)
        if evaluation is None:
            rules = [
                {
                    "rule_id": rule_id, "rule_version": None, "category": "UNKNOWN",
                    "outcome": "UNKNOWN", "observed_value": None, "observed_unit": None,
                    "observed_display": "—", "threshold": "—", "evidence_ids": [],
                    "evidence_display": "—",
                    "explanation_code": "CURRENT_EVIDENCE_NOT_YET_RETRIEVED",
                    "reason": state.stale_reason
                    or "No current evidence has been retrieved for this candidate yet.",
                    "blocking_reason_codes": [],
                    "batch07_admissibility_status": "NOT_ASSESSED",
                    "quality_state": "UNAVAILABLE",
                }
                for rule_id in rule_order
            ]
            chart = {"available": False, "points": [],
                     "reason": "No current bars have been retrieved for this candidate yet."}
        else:
            rules = current_eval.rule_rows(evaluation, rule_order)
            chart = current_eval.chart_points(
                state.collection.bars if state.collection else [], evaluation.as_of
            )

        return {
            "identity": {
                "symbol": state.symbol,
                "case_id": None,
                "candidate_id": None,
                "candidate_key": state.candidate.candidate_key,
                "contract": {
                    "con_id": state.candidate.con_id,
                    "long_name": state.candidate.long_name,
                    "primary_exchange": state.candidate.primary_exchange,
                    "currency": state.candidate.currency,
                },
                "discovery_profile": state.candidate.profile_id,
                "discovery_time": state.candidate.discovered_at,
                "first_seen_at": state.candidate.first_seen_at,
                "as_of_time": _iso(evaluation.as_of) if evaluation else None,
                "snapshot_at": state.snapshot_at,
                "market_data_mode": row["market_data_mode"],
                "data_mode": row["data_mode"],
                "freshness": row["freshness"],
                "mode_label": CURRENT_MODE_LABEL,
                "asset_class": "EQUITY",
                "provider": "IBKR",
            },
            "available": evaluation is not None,
            "reason": state.stale_reason,
            "market_data": row["fields"],
            "rules": rules,
            "phase3a": row["phase3a"],
            "research_detection": row["research_detection"],
            "methodologies": row["methodologies"],
            "methodology_comparison": [
                *row["methodologies"],
                {
                    "methodology_id": "canonical_phase3a",
                    "methodology_label": "CANONICAL PHASE 3A",
                    "pressure": None,
                    "ignition": None,
                    "evidence_coverage": row["evidence_coverage"],
                    "classification": row["phase3a"]["summary"],
                    "evaluable": row["evidence_coverage"]["supported"] > 0,
                    "supporting_evidence": [],
                    "missing_inputs": [],
                    "blocking_reasons": [],
                },
                {
                    "methodology_id": "canonical_research_detection",
                    "methodology_label": "CANONICAL RESEARCH DETECTION",
                    "pressure": None,
                    "ignition": None,
                    "evidence_coverage": row["evidence_coverage"],
                    "classification": row["research_detection"]["status"],
                    "evaluable": row["research_detection"]["status"] != "UNEVALUABLE",
                    "supporting_evidence": [],
                    "missing_inputs": [],
                    "blocking_reasons": row["research_detection"].get("reasons", []),
                },
            ],
            "outcome": row["outcome"],
            "evidence_coverage": row["evidence_coverage"],
            "chart": chart,
            "news": self.external_providers.news_for(state.symbol),
            "sentiment": row["fields"].get("sentiment", {}),
            "evidence_notes": self._evidence_notes(evaluation),
            "missing_evidence": self._missing_evidence(row),
            "transitions": [item.as_dict() for item in reversed(state.transitions[-25:])],
            "history": [asdict(point) for point in state.history[-MAX_HISTORY_PER_SYMBOL:]],
            "provenance": {
                "phase3a_request_id": str(getattr(evaluation.request, "deterministic_id", ""))
                if evaluation else None,
                "phase3a_result_id": str(
                    getattr(evaluation.evaluation, "deterministic_id", "")
                ) if evaluation else None,
                "policy_version": self.policy.policy_version,
                "evaluation_version": self.policy.evaluation_version,
                "provider_scope": list(evaluation.provider_scope) if evaluation else [],
                "price_scope_reason": evaluation.price_scope_reason if evaluation else None,
                "absolute_price_status": (
                    "CURRENT_ABSOLUTE_PRICE_WITHHELD_STALE_OBSERVATION"
                    if evaluation and evaluation.price_scope_reason
                    else current_eval.CURRENT_ABSOLUTE_PRICE_STATUS
                ),
                "absolute_price_rationale": current_eval.CURRENT_ABSOLUTE_PRICE_RATIONALE,
                "absolute_price_constraints": list(
                    current_eval.CURRENT_ABSOLUTE_PRICE_CONSTRAINTS
                ),
                "volume_status": current_eval.CURRENT_VOLUME_STATUS,
                "volume_rationale": current_eval.CURRENT_VOLUME_RATIONALE,
                "percentage_return_window": current_eval.PERCENTAGE_RETURN_WINDOW_LABEL,
                "note": (
                    "This is an ephemeral current snapshot."
                ),
            },
            "bar_count": row["bar_count"],
            "provider_errors": row["provider_errors"],
        }

    def _evidence_notes(self, evaluation) -> list[str]:
        if evaluation is None:
            return []
        return [
            f"{evaluation.included_bar_count} bar(s) were definitely completed at the "
            f"as-of instant and were used as evidence.",
            f"{evaluation.straddling_bar_count} bar(s) straddled the as-of instant and were "
            "excluded, because completion could not be established under both timestamp "
            "interpretations.",
            f"{evaluation.post_boundary_bar_count} bar(s) fell after the as-of instant and "
            "were excluded.",
            f"{evaluation.evidence_bar_count} bar(s) were supplied to the evaluator as "
            f"rule evidence ({current_eval.EVIDENCE_BAR_SELECTION}). "
            + current_eval.EVIDENCE_BAR_SELECTION_RATIONALE,
            current_eval.PERCENTAGE_RETURN_WINDOW_LABEL,
        ]

    def _missing_evidence(self, row: dict[str, Any]) -> list[dict[str, str]]:
        out: list[dict[str, str]] = []
        for name, cell in row["fields"].items():
            if cell["status"] != "KNOWN":
                out.append(
                    {
                        "field": name,
                        "status": cell["status"],
                        "reason_code": cell["missing_reason_code"] or "",
                        "reason": cell["missing_reason"] or "",
                    }
                )
        return out

    # -------------------------------------------------------------- summary

    def summary(self) -> dict[str, Any]:
        rows = self.rows()
        detection_counts: dict[str, int] = {}
        partial = 0
        evaluable: set[str] = set()
        for row in rows:
            status = row["research_detection"]["status"]
            detection_counts[status] = detection_counts.get(status, 0) + 1
            coverage = row["evidence_coverage"]
            if 0 < coverage["supported"] < coverage["total"]:
                partial += 1
        with self._lock:
            for state in self.states.values():
                if state.evaluation is not None:
                    evaluable.update(current_eval.evaluable_rule_ids(state.evaluation))
        return {
            "label": CURRENT_MODE_LABEL,
            "disclaimer": discovery_module.DISCOVERY_DISCLAIMER,
            "candidate_count": len(rows),
            "discovery_profile": self.profile_id,
            "market_data_mode": next(
                (row["market_data_mode"] for row in rows if row["market_data_mode"] != "UNKNOWN"),
                "UNKNOWN",
            ),
            "research_detection_counts": detection_counts,
            "partial_evidence_candidates": partial,
            "evaluable_rules": sorted(evaluable),
            "evaluable_rule_count": len(evaluable),
            "last_discovery_at": self.last_discovery_at,
            "last_refresh_at": self.last_refresh_at,
            "next_refresh_at": self.next_refresh_at,
            "auto_refresh": self.auto_refresh,
            "quote_refresh_seconds": self.quote_refresh_s,
            "scanner_refresh_seconds": self.scanner_refresh_s,
            "symbols_per_cycle": self.symbols_per_cycle,
            "pacing": self.provider.pacing_state()
            if hasattr(self.provider, "pacing_state") else None,
            "last_refresh_error": self.last_refresh_error,
            "providers": self.provider.statuses(),
            "connection": self.provider.connection_info(),
            "note": (
                "Current candidates are kept separate from the 13 frozen research cases and "
                "are never added to the historical research statistics."
            ),
        }


def _parse_iso(value: str | None, fallback: datetime) -> datetime:
    if not value:
        return fallback
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return fallback


_SESSION: ScreenerSession | None = None
_SESSION_LOCK = threading.Lock()


def get_session() -> ScreenerSession:
    """The process-wide current screen. Created lazily; never touches a provider here."""
    global _SESSION
    with _SESSION_LOCK:
        if _SESSION is None:
            from .live_providers import get_runtime
            _SESSION = ScreenerSession(external_providers=get_runtime())
        return _SESSION


def reset_session(session: ScreenerSession | None = None) -> ScreenerSession:
    """Replace the process-wide session. Used by tests and by an explicit UI reset."""
    global _SESSION
    with _SESSION_LOCK:
        if _SESSION is not None:
            _SESSION.stop_auto_refresh()
        if session is not None:
            _SESSION = session
        else:
            from .live_providers import get_runtime
            _SESSION = ScreenerSession(external_providers=get_runtime())
        return _SESSION


def discovery_cadence() -> dict[str, Any]:
    """Return the current discovery cadence and market state.

    Reports whether US markets are open, the base and effective refresh
    intervals (adjusted for market hours), and the next scheduled refresh
    and discovery times.  The UI uses this to show a live status badge.
    """
    now = _now()
    market_open = _is_market_open()
    multiplier = _market_cadence_multiplier()
    session = get_session()

    # Determine day label and next market open for context
    weekday_name = now.strftime("%A")
    if now.weekday() > 4:
        day_label = "Weekend"
    else:
        day_label = "Weekday"

    # Compute next market open (approximately 9:30 AM ET = 14:30 UTC)
    candidate = now
    while True:
        candidate = candidate.replace(hour=14, minute=30, second=0, microsecond=0)
        if candidate > now and candidate.weekday() <= 4:
            break
        candidate += timedelta(days=1)

    return {
        "generated_at": _iso(now),
        "market": {
            "is_open": market_open,
            "state": "OPEN" if market_open else "CLOSED",
            "day": weekday_name,
            "day_type": day_label,
            "next_open_at": _iso(candidate),
            "cadence_multiplier": multiplier,
            "cadence_mode": "FULL_SPEED" if multiplier == 1 else "CONSERVATIVE",
        },
        "refresh": {
            "auto_refresh": session.auto_refresh,
            "base_quote_refresh_s": session.quote_refresh_s,
            "effective_quote_refresh_s": session.quote_refresh_s * multiplier,
            "base_scanner_refresh_s": session.scanner_refresh_s,
            "effective_scanner_refresh_s": session.scanner_refresh_s * multiplier,
            "symbols_per_cycle": session.symbols_per_cycle,
            "last_refresh_at": session.last_refresh_at,
            "next_refresh_at": session.next_refresh_at,
        },
        "discovery": {
            "profile": session.profile_id,
            "last_discovery_at": session.last_discovery_at,
            "candidate_count": len(session.states),
        },
        "api_quota": {
            "ibkr_budget_note": (
                f"IBKR allows 60 requests per rolling 10 minutes. "
                f"At {session.quote_refresh_s * multiplier}s per cycle with "
                f"{session.symbols_per_cycle} symbols/cycle, the effective rate is "
                f"{session.symbols_per_cycle * 60 / (session.quote_refresh_s * multiplier):.1f} "
                f"requests per 10 minutes."
            ),
            "off_hours_multiplier": OFF_HOURS_MULTIPLIER,
        },
    }


__all__ = [
    "CURRENT_MODE_LABEL",
    "CURRENT_SCREEN_CAP",
    "DEFAULT_QUOTE_REFRESH_S",
    "DEFAULT_SCANNER_REFRESH_S",
    "FINVIZ_TOP_N",
    "MAX_HISTORY_PER_SYMBOL",
    "NOT_IN_SCAN_LABEL",
    "CandidateState",
    "HistoryPoint",
    "RuleTransition",
    "ScreenerSession",
    "classify_freshness",
    "discovery_cadence",
    "get_session",
    "reset_session",
]
