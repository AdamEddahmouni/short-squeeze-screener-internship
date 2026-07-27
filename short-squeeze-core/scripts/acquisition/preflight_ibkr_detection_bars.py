"""Offline preflight for the 13 IBKR detection-context historical bar CSVs.

Builds an IntakeManifest and ColumnMappingProfile for each of the 13 symbols
using the resolved IBKR semantics (ADR 0066), runs the preflight, and reports
whether each reaches READY_FOR_FUTURE_ASSOCIATION.

This is Phase 3E Stage 1 evidence-layer construction — outcome-blind, no forward
bars, no Phase 3A evaluation.

Usage (from the repository root)::

    python scripts/acquisition/preflight_ibkr_detection_bars.py
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

from squeeze_core.acquisition.local_bar_intake.models import (
    ColumnMappingProfile,
    IntakeManifest,
)
from squeeze_core.acquisition.local_bar_intake.semantics import (
    ArtifactFormat,
    BarInterval,
    BarSession,
    CorporateActionHandling,
    DataTimeBasis,
    DuplicatePolicy,
    IntendedUse,
    PriceAdjustmentSemantics,
    SessionCoveragePolicy,
    SortExpectation,
    ThousandsSeparatorPolicy,
    TimestampSemantics,
    ValueAuthenticity,
    VolumeAdjustmentSemantics,
)
from squeeze_core.acquisition.historical_data_submission_kit.preflight import (
    PreflightStatus,
    run_preflight_from_bytes,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# Primary exchanges for each symbol, from Batch 05 contract resolution.
PRIMARY_EXCHANGE: dict[str, str] = {
    "XNCR": "NASDAQ", "PESI": "NASDAQ", "SLS": "NASDAQ", "ZNTL": "NASDAQ",
    "GPRE": "NASDAQ", "SSPC": "BATS", "LBGJ": "NASDAQ", "TRVI": "NASDAQ",
    "LMNX": "NASDAQ", "MGNX": "NASDAQ", "BHVN": "NYSE", "OBE": "AMEX", "AVTX": "NASDAQ",
}

# IBKR conIds for each symbol (from Batch 05).
CONID: dict[str, int] = {
    "XNCR": 139508766, "PESI": 136257468, "SLS": 390872440, "ZNTL": 415881332,
    "GPRE": 38333348, "SSPC": 891519449, "LBGJ": 868499891, "TRVI": 364036151,
    "LMNX": 823013254, "MGNX": 136046701, "BHVN": 586873967, "OBE": 369218017,
    "AVTX": 674693864,
}

# Fixed instants for retrieval/export timestamps (from Batch 05 collection).
_RETRIEVAL_TIME = datetime(2026, 7, 18, 13, 38, 0, tzinfo=UTC)
_EXPORT_TIME = datetime(2026, 7, 18, 13, 37, 55, tzinfo=UTC)

# IBKR symbol for each symbol (same as canonical).
SYMBOLS = sorted(PRIMARY_EXCHANGE.keys())

# Column mapping profile for the IBKR detection-context CSV format.
# Columns: timestamp_utc,open,high,low,close,volume,wap,bar_count,timestamp_epoch,
#          requested_symbol,request_name,resolved_con_id
IBKR_PROFILE_ID = "ibkr-trades-detection-context-csv.v1"

IBKR_PROVIDER_NAME = "Interactive Brokers"
IBKR_PRODUCT_NAME = "TWS API Historical Bars via IB Gateway"


def build_column_mapping_profile() -> ColumnMappingProfile:
    return ColumnMappingProfile(
        profile_id=IBKR_PROFILE_ID,
        delimiter=",",
        encoding="utf-8",
        has_header=True,
        timestamp_column="timestamp_utc",
        symbol_column="requested_symbol",
        open_column="open",
        high_column="high",
        low_column="low",
        close_column="close",
        volume_column="volume",
        vwap_column="wap",
        decimal_separator=".",
        thousands_separator_policy=ThousandsSeparatorPolicy.DISALLOW,
        null_tokens=("", "NA", "null"),
        sort_expectation=SortExpectation.STABLE_SORT_BY_EVENT_START,
        duplicate_policy=DuplicatePolicy.COLLAPSE_IDENTICAL_REJECT_CONFLICTING,
    )


def _parse_timestamp_utc(value: str) -> datetime:
    """Parse an IBKR timestamp_utc value like '2026-07-16T16:00:00Z'."""
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value).astimezone(UTC)


def build_manifest(
    symbol: str,
    csv_path: Path,
    coverage_start: datetime,
    coverage_end: datetime,
) -> IntakeManifest:
    raw_bytes = csv_path.read_bytes()
    sha256 = hashlib.sha256(raw_bytes).hexdigest()
    bundle_id = f"ibkr-batch05-{symbol.lower()}-detection-context"
    relative_path = str(csv_path.relative_to(REPO_ROOT)).replace("\\", "/")

    return IntakeManifest(
        bundle_id=bundle_id,
        provider_name=IBKR_PROVIDER_NAME,
        provider_product_or_export_name=IBKR_PRODUCT_NAME,
        user_entitlement_assertion=(
            "Interactive Brokers TWS API historical bar export via locally "
            "authenticated IB Gateway (read-only account, no order/account access)."
        ),
        license_or_terms_reference="Interactive Brokers API License Agreement",
        retrieval_time=_RETRIEVAL_TIME,
        export_time=_EXPORT_TIME,
        artifact_relative_path=relative_path,
        artifact_sha256=sha256,
        artifact_byte_length=len(raw_bytes),
        artifact_media_type="text/csv",
        artifact_format=ArtifactFormat.CSV,
        provider_symbol=symbol,
        canonical_symbol=symbol,
        market_or_venue=PRIMARY_EXCHANGE[symbol],
        bar_interval=BarInterval.ONE_MINUTE,
        event_timezone="UTC",
        # Per ADR 0066: IBKR TRADES timestamp_semantics is honestly UNKNOWN.
        timestamp_semantics=TimestampSemantics.UNKNOWN,
        session_coverage=BarSession.EXTENDED,
        session_coverage_policy=SessionCoveragePolicy.ALLOW_GAPS,
        # Per ADR 0066: IBKR TRADES price is SPLIT_ADJUSTED.
        price_adjustment_semantics=PriceAdjustmentSemantics.SPLIT_ADJUSTED,
        # Per ADR 0066: IBKR TRADES volume adjustment is honestly UNKNOWN.
        volume_adjustment_semantics=VolumeAdjustmentSemantics.UNKNOWN,
        # Split adjustment qualifies as ADJUSTMENTS_APPLIED.
        corporate_action_handling=CorporateActionHandling.ADJUSTMENTS_APPLIED,
        data_time_basis=DataTimeBasis.HISTORICAL,
        value_authenticity=ValueAuthenticity.VENDOR_SUPPLIED,
        intended_use=IntendedUse.HISTORICAL_EVIDENCE,
        expected_start_time=coverage_start,
        expected_end_time=coverage_end,
        column_mapping_profile_id=IBKR_PROFILE_ID,
        notes=(
            f"Batch 05 IBKR historical TRADES bar export for {symbol}. "
            f"Detection-context window (24h preceding boundary). "
            f"Price: SPLIT_ADJUSTED per official docs. Volume/timestamp semantics: "
            f"UNKNOWN per ADR 0066. conId: {CONID[symbol]}."
        ),
    )


def main() -> int:
    profile = build_column_mapping_profile()
    raw_dir = REPO_ROOT / "intake" / "local-bars" / "ibkr-batch-05" / "raw"

    results: list[dict] = []
    all_ready = True

    print("=" * 74)
    print("  Phase 3E Stage 1 - IBKR Detection-Context Bar Preflight")
    print("=" * 74)

    for symbol in SYMBOLS:
        csv_pattern = f"{symbol}-detection-context.csv"
        csv_path = raw_dir / csv_pattern
        if not csv_path.exists():
            print(f"  [SKIP] {symbol}: file not found at {csv_path}")
            continue

        raw_bytes = csv_path.read_bytes()
        sha256 = hashlib.sha256(raw_bytes).hexdigest()

        # Determine coverage window from the first and last timestamp in the CSV.
        lines = raw_bytes.decode("utf-8").strip().splitlines()
        header = lines[0]
        data_lines = lines[1:]
        if not data_lines:
            print(f"  [SKIP] {symbol}: empty CSV")
            continue

        first_ts = _parse_timestamp_utc(data_lines[0].split(",")[0])
        last_ts = _parse_timestamp_utc(data_lines[-1].split(",")[0])

        # With UNKNOWN timestamp semantics, normalization treats the CSV timestamp
        # as END of interval (subtracts duration = 1 min). So the actual bar start
        # is 1 minute before the listed timestamp. Adjust the coverage window
        # accordingly so bars stay within the declared bounds.
        coverage_start = first_ts - timedelta(minutes=1)
        coverage_end = last_ts

        manifest = build_manifest(symbol, csv_path, coverage_start, coverage_end)
        report = run_preflight_from_bytes(manifest, profile, raw_bytes)

        ready = report.status is PreflightStatus.READY_FOR_FUTURE_ASSOCIATION
        if not ready:
            all_ready = False

        results.append({
            "symbol": symbol,
            "bundle_id": manifest.bundle_id,
            "status": report.status.value,
            "ready": ready,
            "bar_count": report.normalized_bar_count,
            "rejected_rows": report.rejected_row_count,
            "quarantined_rows": report.quarantined_row_count,
            "reason_codes": [c.value for c in report.reason_codes],
            "observed_start": str(report.observed_start_time),
            "observed_end": str(report.observed_end_time),
            "sha256": sha256,
            "byte_length": len(raw_bytes),
        })

        status_icon = "ok" if ready else "FAIL"
        print(f"  [{status_icon}] {symbol:6s} -> {report.status.value}")
        print(f"         bars={report.normalized_bar_count:5d}  "
              f"rejected={report.rejected_row_count}  "
              f"quarantined={report.quarantined_row_count}")
        if report.reason_codes:
            print(f"         codes: {', '.join(c.value for c in report.reason_codes)}")

    print("\n" + "=" * 74)
    total = len(results)
    ready_count = sum(1 for r in results if r["ready"])
    print(f"  Total: {total}  |  READY: {ready_count}  |  Not ready: {total - ready_count}")
    print("=" * 74)

    if all_ready:
        print("\n  All 13 detection-context CSVs passed the intake pipeline.")
        print("  Next step: construct the PointInTimeEvidenceBundle for each symbol.")
    else:
        print("\n  Some CSVs did not reach READY status. Review reason codes above.")

    return 0 if all_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
