"""Write local-bar-intake batch 03 canonical documents to ``build/``.

Deterministic and offline: builds every batch-03 document from in-memory
synthetic bytes and writes them under ``build/acquisition/batch-03/`` (a
gitignored, fully regenerable location). The canonical copies used as
deterministic anchors live under ``tests/fixtures/acquisition/batch03/`` and are
compared by the test suite; this script materializes the same bytes.

Usage (from the repository root)::

    python scripts/generate_batch03_local_bar_intake_outputs.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from squeeze_core.acquisition.batch03 import build_batch03_documents


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "build" / "acquisition" / "batch-03"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    documents = build_batch03_documents()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in documents.items():
        (args.output_dir / name).write_bytes(content)
    print(f"wrote {len(documents)} batch 03 documents to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
