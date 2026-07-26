"""Write outcome-acquisition batch 02 artifacts to ``build/``.

Deterministic and offline: reads the committed batch-01 sanitized discovery rows
(the batch-02 cases are inherited unchanged) and writes every batch-02 document
under ``build/acquisition/batch-02/`` (a gitignored, fully regenerable location).
The canonical copies used as deterministic anchors live under
``tests/fixtures/acquisition/batch02/`` and are compared by the test suite; this
script simply materializes the same bytes into the deliverable path.

Usage (from the repository root)::

    python scripts/acquisition/generate_batch02_outputs.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from squeeze_core.acquisition.batch02 import build_batch02_documents


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROWS = (
    REPO_ROOT
    / "intake" / "batches" / "phase-3d-historical-source-collection-01"
    / "normalized" / "batch01_discovery_rows.json"
)
DEFAULT_OUTPUT = REPO_ROOT / "build" / "acquisition" / "batch-02"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=Path, default=DEFAULT_ROWS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    documents = build_batch02_documents(args.rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in documents.items():
        (args.output_dir / name).write_bytes(content)
    print(f"wrote {len(documents)} batch 02 documents to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
