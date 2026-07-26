from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"

REQUIRED_DOCS = {
    "phase-3d-design.md", "phase-3d-test-plan.md", "phase-3d-acquisition-plan-policy.md",
    "phase-3d-source-and-provider-provenance.md", "phase-3d-artifact-intake.md",
    "phase-3d-identity-resolution.md", "phase-3d-inclusion-and-exclusion-policy.md",
    "phase-3d-detection-boundary-freeze.md", "phase-3d-outcome-leakage-prevention.md",
    "phase-3d-case-curation-workflow.md", "phase-3d-phase3b-publication-adapter.md",
    "phase-3d-biya-migration.md", "phase-3d-progress.md",
}

REQUIRED_ADRS = {
    "0059-acquisition-plans-are-preregistered-before-outcome-review.md",
    "0060-outcome-artifacts-remain-separate.md",
    "0061-missing-historical-evidence-is-never-fabricated.md",
    "0062-current-values-cannot-substitute-for-historical-values.md",
    "0063-excluded-attempts-remain-in-the-ledger.md",
    "0064-unique-security-identity-is-the-empirical-unit.md",
    "0065-phase-3d-does-not-optimize-prior-policies.md",
}


def test_all_required_phase3d_documents_and_adrs_exist():
    assert REQUIRED_DOCS <= {item.name for item in DOCS.iterdir() if item.is_file()}
    assert REQUIRED_ADRS <= {item.name for item in (DOCS / "adr").iterdir() if item.is_file()}


def test_additive_prior_docs_and_readme_reference_phase3d():
    for relative in (
        "README.md", "docs/architecture.md", "docs/testing-and-validation.md",
        "docs/phase-3c-design.md", "docs/phase-3c-progress.md",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "Phase 3D" in text, relative


def test_progress_declares_honest_pilot_and_scope_boundary():
    text = (DOCS / "phase-3d-progress.md").read_text(encoding="utf-8")
    assert "No new complete historical cases" in text
    assert "Phase 3E" in text
    assert "predictive validity" in text
