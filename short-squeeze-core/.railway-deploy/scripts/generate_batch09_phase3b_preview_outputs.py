"""Regenerate the committed Batch 09 Phase 3B registry-preview fixtures.

Two independent products:

1. **Sanitized real preview** -- the 13-case preview and its canonical field diff, derived
   from the committed Batch 01 registry and the private Batch 08 freeze. Only identifiers,
   hashes, statuses, and policy versions are committed; no licensed OHLCV-derived value ever
   enters a fixture. Requires the private Batch 05/08 tree and is skipped when it is absent.

2. **Synthetic compatibility fixture** -- a fully synthetic registry whose single candidate is
   evaluation-present / outcome-absent, paired with the existing synthetic Phase 3A
   evaluation that already resolves ``PRICE_RANGE`` to ``UNKNOWN``. This carries no real
   symbol and is what the committed compatibility tests run against.

Offline. No network, no ``ibapi``, and no canonical Phase 3B artifact is a write target.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from squeeze_core.acquisition.phase3b_preview.cli import (  # noqa: E402
    DEFAULT_FREEZE_ROOT,
    DEFAULT_OUT_ROOT,
    DEFAULT_SOURCE_REGISTRY,
    generate,
)
from squeeze_core.acquisition.phase3b_preview.contract import (  # noqa: E402
    ADDED_LIMITATIONS,
    PREVIEW_REGISTRY_VERSION,
)
from squeeze_core.research.models import (  # noqa: E402
    AssetClass,
    CandidateCaseRegistry,
    CandidateCaseRegistryEntry,
    CandidateCaseStatus,
    CandidateCaseType,
    FixtureClassification,
    OriginalPlatformStatus,
)
from squeeze_core.serialization import canonical_json_bytes  # noqa: E402

FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "acquisition" / "batch09"
SYNTHETIC_ROOT = FIXTURE_ROOT / "synthetic-preview"
SOURCE_SYNTHETIC_EVALUATION = (
    REPO_ROOT / "tests" / "fixtures" / "research" / "syn_unevaluable_unknown_evaluation.json"
)


def _write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def generate_sanitized_preview() -> bool:
    """Write the sanitized 13-case preview fixtures. Returns False when input is absent."""
    freeze_root = REPO_ROOT / DEFAULT_FREEZE_ROOT
    if not (freeze_root / "batch-summary.json").exists():
        print("private Batch 08 freeze absent; skipping sanitized preview regeneration")
        return False

    generate(
        REPO_ROOT / DEFAULT_SOURCE_REGISTRY, freeze_root, REPO_ROOT / DEFAULT_OUT_ROOT
    )
    private = REPO_ROOT / DEFAULT_OUT_ROOT
    _write(
        FIXTURE_ROOT / "registry-revision-preview.json",
        (private / "candidate-previews.json").read_bytes(),
    )
    _write(
        FIXTURE_ROOT / "registry-field-diff.json",
        (private / "registry-field-diff.json").read_bytes(),
    )
    _write(
        FIXTURE_ROOT / "preview-summary.json",
        (private / "preview-summary.json").read_bytes(),
    )
    _write(
        FIXTURE_ROOT / "phase3c-compatibility.json",
        (private / "phase3c-compatibility.json").read_bytes(),
    )
    _write(
        FIXTURE_ROOT / "preview-summary.md",
        (private / "preview-summary.md").read_bytes(),
    )
    return True


def generate_synthetic_fixture() -> None:
    """Write the synthetic evaluation-present / outcome-absent registry."""
    evaluation = json.loads(SOURCE_SYNTHETIC_EVALUATION.read_text(encoding="utf-8"))
    _write(
        SYNTHETIC_ROOT / "evaluation" / "synthetic_unevaluable_evaluation.json",
        SOURCE_SYNTHETIC_EVALUATION.read_bytes(),
    )

    entry = CandidateCaseRegistryEntry(
        case_id="BATCH09_SYNTHETIC_EVALUATION_ONLY",
        symbol=evaluation["symbol"],
        asset_class=AssetClass.EQUITY,
        case_type=CandidateCaseType.SYNTHETIC_EDGE_CASE,
        # The state Batch 09 previews: evaluation present, outcome absent.
        case_status=CandidateCaseStatus.EVALUATION_ONLY,
        original_platform_status=OriginalPlatformStatus.UNKNOWN,
        detection_time_evidence_id="batch09-synthetic-detection-evidence",
        evaluation_as_of=evaluation["as_of"],
        evaluation_request_path=None,
        evaluation_result_path="../evaluation/synthetic_unevaluable_evaluation.json",
        outcome_observation_path=None,
        original_platform_artifact_ids=("batch09-synthetic-artifact",),
        historical_dataset_ids=(),
        phase_3a_policy_version=evaluation["policy_version"],
        limitations=ADDED_LIMITATIONS,
        fixture_classification=FixtureClassification.SYNTHETIC_EDGE_CASE,
    )
    registry = CandidateCaseRegistry(
        registry_version=PREVIEW_REGISTRY_VERSION, entries=(entry,),
    )
    _write(
        SYNTHETIC_ROOT / "registry" / "synthetic-preview-registry.json",
        canonical_json_bytes(registry) + b"\n",
    )


def main() -> int:
    if SYNTHETIC_ROOT.exists():
        shutil.rmtree(SYNTHETIC_ROOT)
    generate_synthetic_fixture()
    generate_sanitized_preview()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
