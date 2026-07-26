"""Write the Batch 04 submission kit and its canonical fixtures.

Deterministic and offline: every file is built from in-memory synthetic bytes with
fixed instants. Writes the operator-facing kit under
``operator-kits/historical-market-bars/`` and the committed canonical fixtures under
``tests/fixtures/acquisition/batch04/``. Both are fully regenerable and are compared
byte-for-byte by the test suite.

Usage (from the repository root)::

    python scripts/generate_batch04_submission_kit.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from squeeze_core.acquisition.historical_data_submission_kit.kit import (
    KIT_ROOT,
    build_batch04_fixtures,
    build_submission_kit,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KIT_DIR = REPO_ROOT / KIT_ROOT
DEFAULT_FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "acquisition" / "batch04"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit-dir", type=Path, default=DEFAULT_KIT_DIR)
    parser.add_argument("--fixtures-dir", type=Path, default=DEFAULT_FIXTURES_DIR)
    args = parser.parse_args(argv)

    for name, content in build_submission_kit().items():
        target = args.kit_dir.joinpath(*name.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    for name, content in build_batch04_fixtures().items():
        target = args.fixtures_dir / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    print(
        f"wrote kit to {args.kit_dir} and fixtures to {args.fixtures_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
