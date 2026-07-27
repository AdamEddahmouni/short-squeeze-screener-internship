"""Regenerate stale preflight reports for all 13 IBKR symbols.

The existing batch-06 preflight reports were generated before ADR 0066
exempted IBKR UNKNOWN volume-adjustment and timestamp semantics. With
the current code, these bundles should now pass preflight.

Usage: python scripts/acquisition/regenerate_preflight_reports.py

Output: Overwrites intake/local-bars/ibkr-batch-05/semantics/batch-06/<SYMBOL>-detection-context-preflight-report.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from squeeze_core.acquisition.local_bar_intake.models import (
    IntakeManifest,
    ColumnMappingProfile,
)
from squeeze_core.acquisition.historical_data_submission_kit.preflight import (
    run_preflight_from_bytes,
    PreflightReport,
)
from squeeze_core.acquisition.local_bar_intake.semantics import (
    DuplicatePolicy,
    SortExpectation,
    ThousandsSeparatorPolicy,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
BATCH05_DIR = REPO_ROOT / "intake" / "local-bars" / "ibkr-batch-05"
SEMANTICS_DIR = BATCH05_DIR / "semantics" / "batch-06"
RAW_DIR = BATCH05_DIR / "raw"

# All 13 IBKR pilot symbols
SYMBOLS = sorted(
    p.stem.replace("-detection-context-intake-manifest", "")
    for p in SEMANTICS_DIR.glob("*-detection-context-intake-manifest.json")
)
# Align with build_evidence_bundles.py order
PRIMARY_EXCHANGE: dict[str, str] = {
    "XNCR": "NASDAQ", "PESI": "NASDAQ", "SLS": "NASDAQ", "ZNTL": "NASDAQ",
    "GPRE": "NASDAQ", "SSPC": "BATS", "LBGJ": "NASDAQ", "TRVI": "NASDAQ",
    "LMNX": "NASDAQ", "MGNX": "NASDAQ", "BHVN": "NYSE", "OBE": "AMEX", "AVTX": "NASDAQ",
}
SYMBOLS = sorted(PRIMARY_EXCHANGE.keys())


def build_ibkr_profile(symbol: str, bundle_id: str) -> ColumnMappingProfile:
    """Construct the column mapping profile for IBKR detection-context CSVs.

    All 13 IBKR CSVs share the same column layout (from Batch 05 export).
    """
    return ColumnMappingProfile(
        profile_id=f"{bundle_id}::ibkr-csv",
        delimiter=",",
        encoding="utf-8",
        has_header=True,
        timestamp_column="timestamp_utc",
        date_column=None,
        time_column=None,
        timestamp_format=None,
        symbol_column="requested_symbol",
        venue_column=None,
        open_column="open",
        high_column="high",
        low_column="low",
        close_column="close",
        volume_column="volume",
        trade_count_column="bar_count",
        vwap_column="wap",
        currency_column=None,
        decimal_separator=".",
        thousands_separator_policy=ThousandsSeparatorPolicy.DISALLOW,
        null_tokens=("",),
        sort_expectation=SortExpectation.STABLE_SORT_BY_EVENT_START,
        duplicate_policy=DuplicatePolicy.COLLAPSE_IDENTICAL_REJECT_CONFLICTING,
    )


def run_and_write(symbol: str, *, dry_run: bool = False) -> dict:
    """Regenerate preflight for one symbol. Returns a result dict."""
    manifest_path = SEMANTICS_DIR / f"{symbol}-detection-context-intake-manifest.json"
    preflight_path = SEMANTICS_DIR / f"{symbol}-detection-context-preflight-report.json"
    csv_path = RAW_DIR / f"{symbol}-detection-context.csv"

    # Load manifest
    data = json.loads(manifest_path.read_bytes())
    manifest = IntakeManifest.model_validate(data["intake_manifest"])

    # Build profile
    profile = build_ibkr_profile(symbol, manifest.bundle_id)

    # Read CSV
    content = csv_path.read_bytes()

    # Run preflight with current code
    preflight: PreflightReport = run_preflight_from_bytes(manifest, profile, content)

    # Compute deterministic id for the report
    seed = {
        "preflight_contract_version": preflight.preflight_contract_version,
        "bundle_id": preflight.bundle_id,
        "artifact_id": preflight.artifact_id,
        "status": preflight.status.value,
        "reason_codes": tuple(c.value for c in preflight.reason_codes),
        "normalized_bar_count": preflight.normalized_bar_count,
        "rejected_row_count": preflight.rejected_row_count,
        "quarantined_row_count": preflight.quarantined_row_count,
    }
    from squeeze_core.serialization import canonical_hash
    preflight_did = f"preflight-{canonical_hash(seed)[:24]}"

    # Build the output report dict
    report_dict = preflight.model_dump()
    report_dict["deterministic_id"] = preflight_did
    report_json = json.dumps(report_dict, indent=2, ensure_ascii=False, default=str)

    if not dry_run:
        preflight_path.write_text(report_json, encoding="utf-8")

    # Compare with old report
    old_data = json.loads(preflight_path.read_bytes() if not dry_run else "{}")
    old_status = old_data.get("preflight_status") or old_data.get("status", "?")
    old_reasons = old_data.get("reason_codes", [])

    return {
        "symbol": symbol,
        "old_status": old_status,
        "new_status": preflight.status.value,
        "old_reasons": [r if isinstance(r, str) else r.value for r in old_reasons],
        "new_reasons": [c.value for c in preflight.reason_codes],
        "normalized_bar_count": preflight.normalized_bar_count,
        "rejected_row_count": preflight.rejected_row_count,
        "quarantined_row_count": preflight.quarantined_row_count,
        "ready_for_case_association": preflight.ready_for_case_association,
        "changed": old_status != preflight.status.value,
        "output_path": str(preflight_path),
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="Regenerate stale preflight reports for all 13 IBKR symbols."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would change without writing files."
    )
    args = parser.parse_args()

    print("=" * 72)
    print("  Regenerating preflight reports for %d IBKR symbols" % len(SYMBOLS))
    if args.dry_run:
        print("  DRY RUN -- no files will be written")
    print("=" * 72)

    results: list[dict] = []
    all_passed = True

    for symbol in SYMBOLS:
        print()
        try:
            result = run_and_write(symbol, dry_run=args.dry_run)
            results.append(result)

            status_marker = "[PASS]" if result["new_reasons"] == [] else "[FAIL]"
            changed_marker = " *CHANGED*" if result["changed"] else ""
            print("  [%6s] %s  %s%s" % (
                symbol, status_marker, result["new_status"], changed_marker
            ))
            print("         Old: %s" % result["old_status"])
            print("         Old reasons: %s" % result["old_reasons"])
            print("         New reasons: %s" % result["new_reasons"])
            print("         Normalized bars: %d, Rejected: %d, Quarantined: %d" % (
                result["normalized_bar_count"],
                result["rejected_row_count"],
                result["quarantined_row_count"],
            ))
            print("         Ready for case association: %s" % result["ready_for_case_association"])

            if result["new_reasons"]:
                all_passed = False
        except Exception as e:
            print("  [%6s] [ERROR] %s" % (symbol, e))
            all_passed = False

    print()
    print("=" * 72)
    passed = sum(1 for r in results if r["new_reasons"] == [])
    changed = sum(1 for r in results if r["changed"])
    print("  Summary: %d/%d passed preflight, %d reports changed" % (
        passed, len(results), changed
    ))
    if all_passed and not args.dry_run:
        print("  All preflight reports regenerated successfully.")
    elif args.dry_run:
        print("  Dry run complete. Use --dry-run=false to write.")
    else:
        print("  Some symbols have remaining issues.")

    if not args.dry_run:
        out_dir = SEMANTICS_DIR
        print("  Output: %s" % out_dir)

    print("=" * 72)
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
