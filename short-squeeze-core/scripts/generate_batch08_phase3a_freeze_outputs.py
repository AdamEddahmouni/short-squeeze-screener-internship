"""Write the Batch 08 Phase 3A freeze outputs.

Deterministic and offline. Produces two output sets from the SAME code path:

1. Committed synthetic golden fixture: builds a small synthetic Batch 05-shaped root under
   ``tests/fixtures/acquisition/batch08/synthetic-batch05`` (raw CSVs plus manifests whose
   hashes are derived from the bytes actually written), freezes it, and writes the
   canonical JSON + Markdown golden files the test suite compares byte-for-byte. Every
   value is synthetic and carries no provider data.

2. Private real-evidence outputs: delegates to the package CLI, which writes into the
   gitignored private root. Never committed, because the artifacts embed
   licensed-data-derived provenance and metrics.

Usage (from the repository root)::

    python scripts/generate_batch08_phase3a_freeze_outputs.py [--skip-private]
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from squeeze_core.acquisition.operation_readiness.evidence_inputs import (
    FROZEN_BOUNDARY,
    FROZEN_COHORT,
)
from squeeze_core.acquisition.phase3a_freeze.cli import (
    DEFAULT_PRIVATE_ROOT,
    FREEZE_SUBDIR,
    generate as generate_private,
)
from squeeze_core.acquisition.phase3a_freeze.freeze import freeze_cohort
from squeeze_core.acquisition.phase3a_freeze.models import ReceiptModelingPolicy
from squeeze_core.acquisition.phase3a_freeze.report import (
    build_freeze_report,
    render_markdown,
    sensitivity_summary,
)
from squeeze_core.acquisition.phase3a_freeze.serialization import serialize

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "acquisition" / "batch08"
SYNTHETIC_ROOT = FIXTURE_DIR / "synthetic-batch05"

#: Small synthetic series: the last label is one interval before the frozen boundary's day
#: start, so every bar is definitely completed under the bidirectional envelope.
SYNTHETIC_BAR_COUNT = 6
SYNTHETIC_LAST_LABEL = datetime(2026, 7, 17, 23, 59, tzinfo=UTC)
CSV_HEADER = (
    "timestamp_utc,open,high,low,close,volume,wap,bar_count,timestamp_epoch,"
    "requested_symbol,request_name,resolved_con_id"
)


def _synthetic_closes(symbol: str) -> list[Decimal]:
    """Deterministic synthetic closes derived from the symbol name only.

    Not sourced from any provider. The first and last values differ so the percentage
    metric has something to compute, and the per-symbol offset makes some cases land above
    and some below the 10 percent threshold.
    """
    seed = sum(ord(ch) for ch in symbol) % 7
    base = Decimal(5) + Decimal(seed)
    step = Decimal(seed) / Decimal(10) + Decimal("0.10")
    return [base + step * Decimal(index) for index in range(SYNTHETIC_BAR_COUNT)]


def _rows(symbol: str, request_name: str) -> list[str]:
    closes = _synthetic_closes(symbol)
    rows: list[str] = []
    for index, close in enumerate(closes):
        label = SYNTHETIC_LAST_LABEL - timedelta(
            minutes=(SYNTHETIC_BAR_COUNT - 1 - index)
        )
        text = f"{close:.2f}"
        rows.append(
            ",".join(
                [
                    label.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    text,
                    text,
                    text,
                    text,
                    "0",
                    text,
                    "0",
                    str(int(label.timestamp())),
                    symbol,
                    request_name,
                    "900000000",
                ]
            )
        )
    return rows


def _csv_bytes(symbol: str, request_name: str) -> bytes:
    return ("\n".join([CSV_HEADER, *_rows(symbol, request_name)]) + "\n").encode("utf-8")


def _sha_len(payload: bytes) -> tuple[str, int]:
    return hashlib.sha256(payload).hexdigest(), len(payload)


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=1, sort_keys=False) + "\n", encoding="utf-8", newline="\n"
    )


def build_synthetic_root(root: Path) -> None:
    """Write the synthetic Batch 05-shaped root, hashes derived from the real bytes."""
    requests: list[dict] = []
    artifacts: list[dict] = []
    sha_manifest: dict[str, dict] = {}

    for symbol, _case_id in FROZEN_COHORT:
        for request_name, suffix, day in (
            ("DETECTION_CONTEXT_PRECEDING_24H", "detection-context", "20260718"),
            ("FROZEN_FORWARD_24H", "frozen-forward-24h", "20260719"),
        ):
            payload = _csv_bytes(symbol, request_name)
            relative = f"raw/{symbol}-{suffix}.csv"
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
            sha256, byte_length = _sha_len(payload)
            requests.append(
                {
                    "symbol": symbol,
                    "request_name": request_name,
                    "bar_size_setting": "1 min",
                    "duration_str": "86400 S",
                    "end_datetime": f"{day} 13:37:55 UTC",
                    "format_date": 2,
                    "use_rth": 0,
                    "what_to_show": "TRADES",
                    "first_timestamp_utc": (
                        SYNTHETIC_LAST_LABEL
                        - timedelta(minutes=SYNTHETIC_BAR_COUNT - 1)
                    ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "last_timestamp_utc": SYNTHETIC_LAST_LABEL.strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    "bar_count": SYNTHETIC_BAR_COUNT,
                    "error_codes": [],
                    "notes": ["SYNTHETIC_FIXTURE"],
                    "status": "HISTORICAL_REQUEST_SUCCESS",
                    "retrieval_started_at": "2026-07-23T20:00:00Z",
                    "retrieval_completed_at": "2026-07-23T20:00:01Z",
                }
            )
            artifacts.append(
                {
                    "symbol": symbol,
                    "request_name": request_name,
                    "csv_relative_path": relative,
                    "csv_sha256": sha256,
                    "csv_byte_length": byte_length,
                    "jsonl_sha256": hashlib.sha256(payload + b"jsonl").hexdigest(),
                    "jsonl_byte_length": byte_length * 2,
                }
            )
            sha_manifest[relative] = {"sha256": sha256, "byte_length": byte_length}

    _write_json(root / "requests" / "request-manifest.json", requests)
    _write_json(root / "provenance" / "artifact-manifest.json", artifacts)
    _write_json(root / "provenance" / "sha256-manifest.json", sha_manifest)


def write_synthetic_golden(root: Path, fixture_dir: Path) -> str:
    """Freeze the synthetic root and write the committed golden JSON + Markdown."""
    primary = freeze_cohort(root)
    alternative = freeze_cohort(
        root, receipt_policy=ReceiptModelingPolicy.LOCAL_RETRIEVAL_RECEIPT
    )
    cases = tuple(item.record for item in primary)
    report = build_freeze_report(
        cases,
        receipt_policy=ReceiptModelingPolicy.PROVIDER_AVAILABILITY_AS_RECEIPT,
        boundary_time=FROZEN_BOUNDARY,
        sensitivity=sensitivity_summary(
            cases,
            tuple(item.record for item in alternative),
            ReceiptModelingPolicy.LOCAL_RETRIEVAL_RECEIPT,
        ),
    )
    fixture_dir.mkdir(parents=True, exist_ok=True)
    (fixture_dir / "phase3a-freeze-report.json").write_bytes(serialize(report))
    (fixture_dir / "phase3a-freeze-report.md").write_text(
        render_markdown(report), encoding="utf-8", newline="\n"
    )
    return report.deterministic_id or ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-private",
        action="store_true",
        help="only regenerate the committed synthetic golden fixture",
    )
    args = parser.parse_args(argv)

    build_synthetic_root(SYNTHETIC_ROOT)
    synthetic_id = write_synthetic_golden(SYNTHETIC_ROOT, FIXTURE_DIR)
    print(f"wrote committed synthetic golden (report_id={synthetic_id})")

    private_root = REPO_ROOT / DEFAULT_PRIVATE_ROOT
    if not args.skip_private and (private_root / "raw").exists():
        generate_private(private_root, private_root / FREEZE_SUBDIR)
    else:
        print("skipped private real-evidence freeze (root absent or --skip-private)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
