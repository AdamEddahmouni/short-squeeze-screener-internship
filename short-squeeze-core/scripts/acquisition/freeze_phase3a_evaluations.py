"""Phase 3A evaluation freeze script.

Outputs:
  - build/acquisition/stage2/phase3a-freeze/{SYMBOL}/frozen_request.json
  - build/acquisition/stage2/phase3a-freeze/{SYMBOL}/frozen_result.json
  - build/acquisition/stage2/phase3a-freeze/{SYMBOL}/freeze_metadata.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from squeeze_core.contracts import (
    AssetClass, DataFreshness, EventType, IngestionMethod,
    MarketSession, Observation, ObservationKind,
    PayloadType, Provenance, Quality, QualityState,
    EntitlementState,
)
from squeeze_core.contracts.payloads import MarketSnapshotPayload
from squeeze_core.evaluation.evaluator import evaluate_candidate
from squeeze_core.evaluation.models import RuleEvaluationRequest
from squeeze_core.evaluation.policies import DEFAULT_POLICY_PATH, load_policy
from squeeze_core.serialization import canonical_json_bytes

UTC = timezone.utc

REPO_ROOT = Path(__file__).resolve().parents[2]

PRIMARY_EXCHANGE: dict[str, str] = {
    "XNCR": "NASDAQ", "PESI": "NASDAQ", "SLS": "NASDAQ", "ZNTL": "NASDAQ",
    "GPRE": "NASDAQ", "SSPC": "BATS", "LBGJ": "NASDAQ", "TRVI": "NASDAQ",
    "LMNX": "NASDAQ", "MGNX": "NASDAQ", "BHVN": "NYSE", "OBE": "AMEX", "AVTX": "NASDAQ",
}
SYMBOLS = sorted(PRIMARY_EXCHANGE.keys())

BOUNDARY_TS = datetime(2026, 7, 18, 13, 37, 55, 17661, tzinfo=UTC)
RETRIEVAL_TS = datetime(2026, 7, 18, 13, 38, 0, tzinfo=UTC)

RAW_DIR = REPO_ROOT / "intake" / "local-bars" / "ibkr-batch-05" / "raw"
DISCOVERY_PATH = (
    REPO_ROOT / "intake" / "batches" / "phase-3d-historical-source-collection-01"
    / "normalized" / "batch01_discovery_rows.json"
)
BUNDLES_DIR = REPO_ROOT / "build" / "acquisition" / "evidence-bundles"
OUTPUT_DIR = REPO_ROOT / "build" / "acquisition" / "stage2" / "phase3a-freeze"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_discovery_data() -> dict[str, dict]:
    if not DISCOVERY_PATH.exists():
        return {}
    data = json.loads(DISCOVERY_PATH.read_bytes())
    by_symbol: dict[str, dict] = {}
    for row in data.get("rows", []):
        by_symbol[row["ticker"]] = row["detection_time_evidence"]
    return by_symbol


def build_market_snapshot_observation(
    symbol: str, evidence: dict, index: int
) -> Observation:
    float_shares = evidence.get("float_shares")
    payload = MarketSnapshotPayload(
        last_price=(
            Decimal(str(evidence["price"])) if evidence.get("price") is not None else None
        ),
        change_percent=(
            Decimal(str(evidence["change_percent"]))
            if evidence.get("change_percent") is not None else None
        ),
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Freeze Phase 3A evaluations")
    parser.parse_args(argv)

    print("Loading Phase 3A candidate evaluation policy...")
    policy = load_policy(DEFAULT_POLICY_PATH)
    print(f"Policy version: {policy.policy_version}")
    print(f"Enabled rules: {len(policy.enabled_rule_ids)}")

    discovery_data = load_discovery_data()

    print("Processing symbols...")
    success_count = 0
    
    for symbol in SYMBOLS:
        bundle_path = BUNDLES_DIR / symbol / "bundle.json"
        if not bundle_path.exists():
            print(f"  [{symbol}] Skipping: no evidence bundle found.")
            continue

        print(f"  [{symbol}] Loading evidence and bars...")
        t0 = time.time()
        
        evidence = discovery_data.get(symbol, {})
        snapshot = build_market_snapshot_observation(symbol, evidence, 1)
        bar_observations = load_bars(symbol)
        
        if not bar_observations:
            print(f"  [{symbol}] Skipping: no bars loaded.")
            continue
            
        observations = bar_observations + (snapshot,)
        
        print(f"  [{symbol}] Evaluating {len(observations)} observations...")
        
        request = RuleEvaluationRequest(
            symbol=symbol,
            asset_class=AssetClass.EQUITY,
            as_of=max(BOUNDARY_TS, RETRIEVAL_TS),
            policy_version=policy.policy_version,
            enabled_rule_ids=policy.enabled_rule_ids,
            input_observations=observations,
        )
        
        result = evaluate_candidate(request, policy)
        
        req_bytes = canonical_json_bytes(request)
        res_bytes = canonical_json_bytes(result)
        
        req_hash = _sha256(req_bytes)
        res_hash = _sha256(res_bytes)
        
        out_dir = OUTPUT_DIR / symbol
        out_dir.mkdir(parents=True, exist_ok=True)
        
        (out_dir / "frozen_request.json").write_bytes(req_bytes)
        (out_dir / "frozen_result.json").write_bytes(res_bytes)
        
        metadata = {
            "symbol": symbol,
            "freeze_timestamp_utc": datetime.now(UTC).isoformat(),
            "request_id": result.deterministic_id, 
            "result_id": result.deterministic_id,
            "request_sha256": req_hash,
            "result_sha256": res_hash,
            "observation_count": len(observations),
        }
        
        (out_dir / "freeze_metadata.json").write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )
        
        t1 = time.time()
        print(f"  [{symbol}] Frozen successfully in {t1 - t0:.2f}s (result_id={result.deterministic_id})")
        success_count += 1
        
    print(f"Done. Successfully froze {success_count} symbols.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
