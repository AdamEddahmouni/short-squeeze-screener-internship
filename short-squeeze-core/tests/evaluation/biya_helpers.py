import json
from datetime import UTC, datetime
from pathlib import Path

from squeeze_core.contracts import AssetClass, EventType, Observation, Quality, QualityState
from squeeze_core.evaluation import RuleEvaluationRequest
from squeeze_core.evaluation.policies import lookup_policy
from squeeze_core.evidence import CoverageDomain
from squeeze_core.readiness import (
    DomainCoverageSnapshot, EvidenceConflictSummary, InputSufficiencyResult,
    StructuralState,
)


ROOT = Path(__file__).resolve().parents[2]
OUTCOME_FIXTURES = ROOT / "tests" / "fixtures" / "validation" / "outcome_amendment"
EARLIEST = datetime(2026, 7, 17, 14, 23, 58, tzinfo=UTC)
LATEST = datetime(2026, 7, 17, 16, 54, 58, tzinfo=UTC)
POLICY = lookup_policy("phase_3a_transparent_candidate_policy.v1")


def _jsonl(name: str) -> tuple[Observation, ...]:
    return tuple(
        Observation.model_validate(json.loads(line))
        for line in (OUTCOME_FIXTURES / name).read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _public_historical_projection(
    observation: Observation, availability_time: datetime | None = None
) -> Observation:
    """Project asserted public availability without changing the anchored observation ID.

    The Phase 2V files retain the 2026-07-21 local acquisition time.  Their provider
    metadata separately asserts publication-time availability.  Phase 3A uses that
    assertion only for retrospective point-in-time research and never claims that the
    original platform received the record.
    """
    moment = availability_time or observation.source_timestamp
    return observation.model_copy(update={
        "source_timestamp": moment,
        "received_timestamp": moment,
        "effective_timestamp": moment,
    })


def historical_detection_observations(as_of: datetime) -> tuple[Observation, ...]:
    bars_with_end = tuple(
        (
            item,
            datetime.fromisoformat(
                str(item.provenance.provider_metadata["bar_end"]).replace("Z", "+00:00")
            ),
        )
        for item in _jsonl("biya_market_bars_intraday.jsonl")
    )
    bars = tuple((item, bar_end) for item, bar_end in bars_with_end if bar_end <= as_of)
    # A single latest completed bar is sufficient for the price/availability rules and
    # prevents any post-boundary outcome bar from entering the request.
    latest_bar, latest_bar_end = max(bars, key=lambda pair: pair[1])
    news = _jsonl("biya_news.jsonl")
    action = _jsonl("biya_corporate_actions.jsonl")
    return tuple(
        _public_historical_projection(item, latest_bar_end if item is latest_bar else None)
        for item in (latest_bar, *news, *action)
    )


def _quality(as_of: datetime) -> Quality:
    return Quality(state=QualityState.KNOWN_VALUE, evaluated_at=as_of)


def readiness(as_of: datetime):
    requested = (
        CoverageDomain.BORROW_AVAILABILITY,
        CoverageDomain.BORROW_FEE,
        CoverageDomain.MARKET_BARS,
        CoverageDomain.NEWS,
        CoverageDomain.PUBLISHED_SHORT_INTEREST,
    )
    coverage = DomainCoverageSnapshot(
        symbol="BIYA", asset_class=AssetClass.EQUITY, as_of=as_of,
        requested_domains=requested,
        present_domains=(CoverageDomain.MARKET_BARS, CoverageDomain.NEWS),
        unavailable_domains=(
            CoverageDomain.BORROW_AVAILABILITY,
            CoverageDomain.BORROW_FEE,
            CoverageDomain.PUBLISHED_SHORT_INTEREST,
        ),
        quality=_quality(as_of),
    )
    conflicts = EvidenceConflictSummary(
        symbol="BIYA", asset_class=AssetClass.EQUITY, as_of=as_of,
        conflict_count=0, quality=_quality(as_of),
    )
    sufficiency = InputSufficiencyResult(
        operation="candidate-evaluation", policy_version="phase_3a_biya_readiness.v1",
        symbol="BIYA", asset_class=AssetClass.EQUITY, as_of=as_of,
        structural_state=StructuralState.INSUFFICIENT,
        insufficient_history_inputs=("relative-volume-history",),
        quality=_quality(as_of),
    )
    return coverage, conflicts, sufficiency


def request(as_of: datetime, *, observations: tuple[Observation, ...] | None = None):
    inputs = historical_detection_observations(as_of) if observations is None else observations
    return RuleEvaluationRequest(
        symbol="BIYA", asset_class=AssetClass.EQUITY, as_of=as_of,
        policy_version=POLICY.policy_version,
        enabled_rule_ids=POLICY.enabled_rule_ids,
        provider_scope=("yahoo-chart", "yahoo-search"),
        input_observations=inputs,
        input_readiness_results=readiness(as_of),
    )


def by_rule(evaluation):
    return {item.rule_id: item for item in evaluation.rule_results}
