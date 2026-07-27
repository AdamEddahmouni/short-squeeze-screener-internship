"""Construct PointInTimeEvidenceBundles for all 13 IBKR pilot symbols.

Combines:
  - Normalized detection-context bars (via phase3a_freeze.evidence_adapter)
  - Scanner-snapshot metadata (float, price, volume from batch01_discovery_rows.json)
  - Catalyst evidence (NewsAPI, SEC EDGAR -- placeholder)
  - Structural validity metadata

Then runs the Phase 2D readiness evaluation on each bundle.

**Performance note:** ``build_point_in_time_evidence`` calls ``build_conflicts``
which does O(n^2) pair comparisons across all bar observations (~2.7M per
symbol with ~1 200 bars). Expect ~30-60 seconds per symbol.  Total: ~7-13
minutes for all 13 symbols.

Each bundle is written to ``build/acquisition/evidence-bundles/`` immediately
after construction so progress is never lost.  Re-run to resume without
reprocessing completed symbols.

Outcome-blind: no forward bars, no outcome data.

Usage (from repository root)::

    python scripts/acquisition/build_evidence_bundles.py
"""

from __future__ import annotations

import json
import time as time_module
from datetime import datetime, timezone
from pathlib import Path
from decimal import Decimal

from squeeze_core.contracts import (
    AssetClass, DataFreshness, EventType, IngestionMethod,
    MarketSession, Observation, ObservationKind,
    PayloadType, Provenance, Quality, QualityState,
    EntitlementState,
)
from squeeze_core.contracts.payloads import (
    MarketSnapshotPayload,
)
from squeeze_core.evidence.builder import build_point_in_time_evidence
from squeeze_core.evidence.models import CoverageDomain
from squeeze_core.evidence.policy import PointInTimeEvidencePolicy
from squeeze_core.readiness.coverage import build_domain_coverage_snapshot

UTC = timezone.utc

REPO_ROOT = Path(__file__).resolve().parents[2]

# Primary exchanges for each symbol, from Batch 05 contract resolution.
PRIMARY_EXCHANGE: dict[str, str] = {
    "XNCR": "NASDAQ", "PESI": "NASDAQ", "SLS": "NASDAQ", "ZNTL": "NASDAQ",
    "GPRE": "NASDAQ", "SSPC": "BATS", "LBGJ": "NASDAQ", "TRVI": "NASDAQ",
    "LMNX": "NASDAQ", "MGNX": "NASDAQ", "BHVN": "NYSE", "OBE": "AMEX", "AVTX": "NASDAQ",
}
SYMBOLS = sorted(PRIMARY_EXCHANGE.keys())

# Frozen boundary timestamp (all 13 symbols share this detection time).
BOUNDARY_TS = datetime(2026, 7, 18, 13, 37, 55, 17661, tzinfo=UTC)
RETRIEVAL_TS = datetime(2026, 7, 18, 13, 38, 0, tzinfo=UTC)

# Paths
RAW_DIR = REPO_ROOT / "intake" / "local-bars" / "ibkr-batch-05" / "raw"
DISCOVERY_PATH = (
    REPO_ROOT / "intake" / "batches" / "phase-3d-historical-source-collection-01"
    / "normalized" / "batch01_discovery_rows.json"
)
BUILD_DIR = REPO_ROOT / "build" / "acquisition" / "evidence-bundles"


def _serialisable(obj) -> object:
    """Recurse through a Pydantic / dataclass tree to plain dicts + primitives."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, "model_dump"):
        return _serialisable(obj.model_dump())
    if isinstance(obj, dict):
        return {k: _serialisable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialisable(item) for item in obj]
    if isinstance(obj, set):
        return sorted(_serialisable(item) for item in obj)
    if isinstance(obj, bytes):
        return obj.hex()
    return str(obj)


def load_discovery_data() -> dict[str, dict]:
    """Load scanner-snapshot metadata for each symbol."""
    data = json.loads(DISCOVERY_PATH.read_bytes())
    by_symbol: dict[str, dict] = {}
    for row in data["rows"]:
        by_symbol[row["ticker"]] = row["detection_time_evidence"]
    return by_symbol


def build_market_snapshot_observation(
    symbol: str, evidence: dict, index: int
) -> Observation:
    """Create a MARKET_SNAPSHOT Observation from scanner snapshot evidence."""
    float_shares = evidence.get("float_shares")
    payload = MarketSnapshotPayload(
        last_price=(
            Decimal(str(evidence["price"])) if evidence.get("price") is not None else None
        ),
        change_percent=(
            Decimal(str(evidence["change_percent"]))
            if evidence.get("change_percent") is not None else None
        ),
        # volume and average_volume are not available in the scanner snapshot data.
        volume=None,
        average_volume=None,
        relative_volume=(
            Decimal(str(evidence["rel_volume"]))
            if evidence.get("rel_volume") is not None else None
        ),
        float_shares=(
            int(float_shares) if float_shares is not None else None
        ),
        shares_outstanding=None,
        short_float_percent=(
            Decimal(str(evidence["short_float_percent"]))
            if evidence.get("short_float_percent") is not None else None
        ),
        short_ratio_days=(
            Decimal(str(evidence["days_to_cover"]))
            if evidence.get("days_to_cover") is not None else None
        ),
        exchange=PRIMARY_EXCHANGE.get(symbol),
    )
    src_provider = evidence.get("source", "unknown")
    return Observation(
        schema_version="1.0.0",
        event_type=EventType.MARKET_SNAPSHOT,
        symbol=symbol,
        asset_class=AssetClass.EQUITY,
        source=f"archived_scanner_snapshot:{src_provider}",
        source_record_id=f"batch01_scanner_{symbol}_{index}",
        source_timestamp=BOUNDARY_TS,
        received_timestamp=BOUNDARY_TS,
        effective_timestamp=BOUNDARY_TS,
        market_session=MarketSession.REGULAR,
        data_freshness=DataFreshness.HISTORICAL,
        observation_kind=ObservationKind.PROVIDER_PUBLISHED,
        quality=Quality(state=QualityState.KNOWN_VALUE),
        payload_type=PayloadType.MARKET_SNAPSHOT,
        payload=payload,
        provenance=Provenance(
            provider="Archived original-platform squeeze scanner",
            ingestion_method=IngestionMethod.LOADED_FIXTURE,
            origin_kind=ObservationKind.PROVIDER_PUBLISHED,
            normalized=False,
            entitlement_state=EntitlementState.NOT_APPLICABLE,
            provider_metadata={
                "source": src_provider,
                "capture_timestamp": BOUNDARY_TS.isoformat(),
            },
        ),
    )


def load_bars(symbol: str) -> tuple[Observation, ...]:
    """Load detection-context bars as Observations using the Phase 3A freeze adapter."""
    from squeeze_core.acquisition.phase3a_freeze.evidence_adapter import (
        load_detection_context_bars,
        EvidenceAccessLog,
    )
    from squeeze_core.acquisition.phase3a_freeze.models import (
        ReceiptModelingPolicy, TimestampInterpretation,
    )

    csv_path = RAW_DIR / f"{symbol}-detection-context.csv"
    if not csv_path.exists():
        return ()

    result = load_detection_context_bars(
        csv_path,
        symbol=symbol,
        boundary=BOUNDARY_TS,
        retrieval_completed_at=RETRIEVAL_TS,
        receipt_policy=ReceiptModelingPolicy.LOCAL_RETRIEVAL_RECEIPT,
        interpretation=TimestampInterpretation.LABEL_IS_INTERVAL_START,
        log=EvidenceAccessLog(),
    )
    return result.observations


def try_load_catalyst_evidence(symbol: str) -> tuple[Observation, ...]:
    """Attempt to load catalyst evidence (NewsAPI, SEC EDGAR).

    Returns empty tuple when not available (offline mode).
    NewsAPI and SEC EDGAR require online provider access which is not available
    in this outcome-blind offline pipeline. Catalyst evidence acquisition will
    be performed in a separate step with the existing adapter infrastructure
    (squeeze_core.adapters.news, squeeze_core.adapters.sec_edgar).
    """
    # Placeholder: returns empty. Catalyst evidence is deferred to a future step.
    # When online acquisition is available, call:
    #   news_adapter.fetch(symbol, before=BOUNDARY_TS)
    #   sec_adapter.fetch(symbol, before=BOUNDARY_TS)
    return ()


def readiness_summary(symbol: str, bundle) -> dict:
    """Phase 2D readiness summary for one bundle."""
    requested = (
        CoverageDomain.MARKET_BARS,
        CoverageDomain.CANDIDATE_SNAPSHOT,
        CoverageDomain.NEWS,
        CoverageDomain.SEC_FILINGS,
    )
    coverage = build_domain_coverage_snapshot(bundle, requested_domains=requested)

    return {
        "symbol": symbol,
        "bundle_id": bundle.bundle_id,
        "observation_count": len(bundle.observations),
        "included_count": bundle.completeness_summary.included_observation_count,
        "excluded_count": bundle.completeness_summary.excluded_observation_count,
        "present_domains": [
            (sc.domain.value, sc.state.value) for sc in bundle.source_coverage
        ],
        "missing_domains": [
            sc.domain.value for sc in bundle.source_coverage
            if sc.state.value == "MISSING"
        ],
        "coverage": {
            "present": [d.value for d in coverage.present_domains],
            "missing": [d.value for d in coverage.missing_domains],
        },
        "freshness": _serialisable(bundle.freshness_summary),
        "diagnostic_count": len(bundle.diagnostics),
    }


def process_symbol(
    symbol: str,
    discovery_data: dict[str, dict],
    *,
    force: bool = False,
) -> dict | None:
    """Build one evidence bundle, write it to disk, and return the readiness summary."""
    build_dir = BUILD_DIR / symbol
    bundle_path = build_dir / "bundle.json"
    summary_path = build_dir / "summary.json"
    metadata_path = build_dir / "build-metadata.json"

    # Resume check -- skip if already complete.
    if not force and bundle_path.exists() and summary_path.exists():
        summary = json.loads(summary_path.read_bytes())
        print(f"  [{symbol:6s}] SKIP (already built: {summary.get('bundle_id', '?')})")
        return summary

    t_start = time_module.time()
    print(f"  [{symbol:6s}] Loading bars ... ", end="", flush=True)
    bar_observations = load_bars(symbol)
    if not bar_observations:
        print("NO BARS -- skipped")
        return None

    evidence = discovery_data.get(symbol, {})
    snapshot = build_market_snapshot_observation(symbol, evidence, 1)
    catalyst = try_load_catalyst_evidence(symbol)
    observations = bar_observations + (snapshot,) + catalyst

    print(f"{len(bar_observations)} bars, building PITE bundle ... ", end="", flush=True)

    as_of = max(BOUNDARY_TS, RETRIEVAL_TS)
    policy = PointInTimeEvidencePolicy(
        as_of=as_of,
        maximum_future_skew_ms=60_000,
        allow_stale=True,
        allow_delayed=True,
        allow_unknown_freshness=True,
        include_market_bars_domain=True,
    )

    bundle = build_point_in_time_evidence(
        symbol=symbol,
        observations=observations,
        policy=policy,
    )
    print("readiness ... ", end="", flush=True)
    summary = readiness_summary(symbol, bundle)
    t_done = time_module.time()

    build_dir.mkdir(parents=True, exist_ok=True)
    bundle_path.write_text(
        json.dumps(_serialisable(bundle.model_dump()), indent=2, ensure_ascii=False)
    )
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )
    metadata_path.write_text(
        json.dumps({
            "symbol": symbol,
            "built_at": datetime.now(UTC).isoformat(),
            "elapsed_s": round(t_done - t_start, 1),
        }, indent=2)
    )

    print(f"done ({t_done - t_start:.1f}s)")
    print(f"         Bundle: {bundle.bundle_id}")
    print(f"         Observations: {bundle.completeness_summary.included_observation_count} "
          f"included / {bundle.completeness_summary.excluded_observation_count} excluded")
    present = [d for d in bundle.source_coverage if d.state.value == "PRESENT"]
    missing = [d for d in bundle.source_coverage if d.state.value == "MISSING"]
    if present:
        print(f"         Present domains: {', '.join(d.domain.value for d in present)}")
    if missing:
        print(f"         Missing domains: {', '.join(d.domain.value for d in missing)}")
    fresh = bundle.freshness_summary
    print(f"         Freshness: {fresh.historical_count} historical, "
          f"{fresh.live_count} live, {fresh.delayed_count} delayed, "
          f"{fresh.stale_count} stale")
    print(f"         Written to: {build_dir}")

    return summary


def main() -> int:
    discovery_data = load_discovery_data()
    results: list[dict] = []
    all_ok = True

    print("=" * 74)
    print("  Phase 3E Stage 1 - Evidence Bundle Construction")
    print("  (O(n^2) conflict detection; expect ~30-60s per symbol)")
    print("  Re-run to resume without reprocessing completed symbols.")
    print("=" * 74)
    print(f"  Boundary:         {BOUNDARY_TS.isoformat()}")
    print(f"  Symbols:          {', '.join(SYMBOLS)}")
    print(f"  Discovery data:   {len(discovery_data)} symbols loaded")
    print(f"  Output directory: {BUILD_DIR}")
    print()

    for symbol in SYMBOLS:
        summary = process_symbol(symbol, discovery_data)
        if summary is None:
            all_ok = False
        else:
            results.append(summary)
        print()

    print("=" * 74)
    ok_count = len(results)
    print(f"  Summary: {ok_count}/{len(SYMBOLS)} bundles built")
    if ok_count == len(SYMBOLS):
        print("  All evidence bundles constructed successfully.")
        print("  Ready for Phase 3A evaluation pipeline.")
    else:
        print(f"  {len(SYMBOLS) - ok_count} symbols were skipped (no bars found).")
    print(f"  Output: {BUILD_DIR}")
    print("=" * 74)

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
