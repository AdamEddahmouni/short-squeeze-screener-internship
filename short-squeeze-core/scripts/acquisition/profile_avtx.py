"""Profile build_conflicts performance on a single symbol (AVTX).

Usage: python scripts/acquisition/profile_avtx.py
"""

from __future__ import annotations

import cProfile
import json
import pstats
import sys
import time as time_module
from datetime import datetime, timezone
from pathlib import Path
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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
from squeeze_core.evidence.policy import PointInTimeEvidencePolicy

UTC = timezone.utc

REPO_ROOT = Path(__file__).resolve().parents[2]
BOUNDARY_TS = datetime(2026, 7, 18, 13, 37, 55, 17661, tzinfo=UTC)
RETRIEVAL_TS = datetime(2026, 7, 18, 13, 38, 0, tzinfo=UTC)
RAW_DIR = REPO_ROOT / "intake" / "local-bars" / "ibkr-batch-05" / "raw"

SYMBOL = "AVTX"


def load_bars_profile():
    """Load detection-context bars, build PITE bundle, with cProfile."""
    from squeeze_core.acquisition.phase3a_freeze.evidence_adapter import (
        load_detection_context_bars,
        EvidenceAccessLog,
    )
    from squeeze_core.acquisition.phase3a_freeze.models import (
        ReceiptModelingPolicy, TimestampInterpretation,
    )

    csv_path = RAW_DIR / f"{SYMBOL}-detection-context.csv"
    print(f"Loading bars from {csv_path} ...", flush=True)
    t0 = time_module.time()
    result = load_detection_context_bars(
        csv_path,
        symbol=SYMBOL,
        boundary=BOUNDARY_TS,
        retrieval_completed_at=RETRIEVAL_TS,
        receipt_policy=ReceiptModelingPolicy.LOCAL_RETRIEVAL_RECEIPT,
        interpretation=TimestampInterpretation.LABEL_IS_INTERVAL_START,
        log=EvidenceAccessLog(),
    )
    t1 = time_module.time()
    print(f"Loaded {len(result.observations)} bars in {t1-t0:.1f}s", flush=True)

    # Build minimal snapshot (same as build_evidence_bundles.py would do)
    snapshot = Observation(
        schema_version="1.0.0",
        event_type=EventType.MARKET_SNAPSHOT,
        symbol=SYMBOL,
        asset_class=AssetClass.EQUITY,
        source="archived_scanner_snapshot:test",
        source_record_id=f"batch01_scanner_{SYMBOL}_1",
        source_timestamp=BOUNDARY_TS,
        received_timestamp=BOUNDARY_TS,
        effective_timestamp=BOUNDARY_TS,
        market_session=MarketSession.REGULAR,
        data_freshness=DataFreshness.HISTORICAL,
        observation_kind=ObservationKind.PROVIDER_PUBLISHED,
        quality=Quality(state=QualityState.KNOWN_VALUE),
        payload_type=PayloadType.MARKET_SNAPSHOT,
        payload=MarketSnapshotPayload(
            last_price=Decimal("1.23"),
        ),
        provenance=Provenance(
            provider="test",
            ingestion_method=IngestionMethod.LOADED_FIXTURE,
            origin_kind=ObservationKind.PROVIDER_PUBLISHED,
            normalized=False,
            entitlement_state=EntitlementState.NOT_APPLICABLE,
            provider_metadata={"source": "test", "capture_timestamp": BOUNDARY_TS.isoformat()},
        ),
    )

    observations = result.observations + (snapshot,)
    print(f"Total observations: {len(observations)}", flush=True)

    as_of = max(BOUNDARY_TS, RETRIEVAL_TS)
    policy = PointInTimeEvidencePolicy(
        as_of=as_of,
        maximum_future_skew_ms=60_000,
        allow_stale=True,
        allow_delayed=True,
        allow_unknown_freshness=True,
        include_market_bars_domain=True,
    )

    print("Running build_point_in_time_evidence with cProfile ...", flush=True)
    profiler = cProfile.Profile()
    profiler.enable()
    bundle = build_point_in_time_evidence(
        symbol=SYMBOL,
        observations=observations,
        policy=policy,
    )
    profiler.disable()
    t2 = time_module.time()
    print(f"build_point_in_time_evidence completed in {t2-t1:.1f}s", flush=True)
    print(f"Bundle: {bundle.bundle_id}", flush=True)
    print(f"Included: {bundle.completeness_summary.included_observation_count}", flush=True)
    print(f"Conflicts: {len(bundle.conflicts)}", flush=True)
    print(f"Diagnostics: {len(bundle.diagnostics)}", flush=True)
    print()

    # Print top 40 cumulative time callers
    print("=" * 74)
    print("  Top 40 cumulative-time callers")
    print("=" * 74)
    stats = pstats.Stats(profiler).sort_stats("cumtime")
    stats.print_stats(40)

    print()
    print("=" * 74)
    print("  Top 20 time-per-call (avg) — identifying expensive per-call ops")
    print("=" * 74)
    stats2 = pstats.Stats(profiler).sort_stats("time")
    stats2.print_stats(20)

    print()
    print("=" * 74)
    print("  Top 20 call-count — identifying O(n²) loops")
    print("=" * 74)
    stats3 = pstats.Stats(profiler).sort_stats("ncalls")
    stats3.print_stats(20)

    # Also dump raw stats as JSON for deeper analysis
    import io
    stream = io.StringIO()
    stats4 = pstats.Stats(profiler, stream=stream).sort_stats("cumtime")
    stats4.print_stats(80)
    raw_output = stream.getvalue()
    (REPO_ROOT / "build" / "acquisition" / "profile_avtx_stats.txt").write_text(raw_output)
    print(f"Raw stats written to build/acquisition/profile_avtx_stats.txt")


if __name__ == "__main__":
    load_bars_profile()
