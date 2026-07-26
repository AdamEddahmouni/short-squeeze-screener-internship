"""Write the Batch 07 operation-readiness outputs.

Deterministic and offline. Produces two output sets from the SAME code path:

1. Private (real evidence): reads the gitignored Batch 05 provenance manifests under
   ``intake/local-bars/ibkr-batch-05`` (metadata only, never OHLCV) and writes the
   canonical JSON + Markdown report into a gitignored private subdirectory. Not committed
   because it embeds licensed-data provenance (sha256 / coverage of private bars).

2. Committed golden fixture (synthetic evidence): reads the committed synthetic manifests
   under ``tests/fixtures/acquisition/batch07/synthetic-batch05`` and writes the canonical
   JSON + Markdown golden files the test suite compares byte-for-byte.

Usage (from the repository root)::

    python scripts/generate_batch07_operation_readiness_outputs.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from squeeze_core.acquisition.operation_readiness.report import build_report
from squeeze_core.acquisition.operation_readiness.serialization import (
    render_markdown,
    serialize_report,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_BATCH05_ROOT = REPO_ROOT / "intake" / "local-bars" / "ibkr-batch-05"
PRIVATE_OUT_DIR = PRIVATE_BATCH05_ROOT / "operation-readiness"
SYNTHETIC_ROOT = REPO_ROOT / "tests" / "fixtures" / "acquisition" / "batch07" / "synthetic-batch05"
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "acquisition" / "batch07"


def _write(root: Path, json_path: Path, md_path: Path) -> str:
    report = build_report(root)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_bytes(serialize_report(report))
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    return report.deterministic_id or ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-private", action="store_true",
                        help="only regenerate the committed synthetic golden fixture")
    args = parser.parse_args(argv)

    synthetic_id = _write(
        SYNTHETIC_ROOT,
        FIXTURE_DIR / "operation-readiness-report.json",
        FIXTURE_DIR / "operation-readiness-report.md",
    )
    print(f"wrote committed synthetic golden (report_id={synthetic_id})")

    if not args.skip_private and (PRIVATE_BATCH05_ROOT / "requests").exists():
        private_id = _write(
            PRIVATE_BATCH05_ROOT,
            PRIVATE_OUT_DIR / "operation-readiness-report.json",
            PRIVATE_OUT_DIR / "operation-readiness-report.md",
        )
        print(f"wrote private real-evidence report (report_id={private_id})")
    else:
        print("skipped private real-evidence report (root absent or --skip-private)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
