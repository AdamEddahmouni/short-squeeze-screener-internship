from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"

REQUIRED_BATCH03_DOCS = {
    "batch-03-local-bar-intake-plan.md",
    "batch-03-intake-contract.md",
    "batch-03-validation-and-quarantine-policy.md",
    "batch-03-determinism-and-provenance.md",
    "batch-03-security-and-credential-boundary.md",
    "batch-03-case-association-boundary.md",
    "batch-03-test-and-verification-report.md",
    "batch-03-completion-report.md",
}


def test_all_required_batch03_documents_exist():
    present = {item.name for item in DOCS.iterdir() if item.is_file()}
    assert REQUIRED_BATCH03_DOCS <= present


def test_completion_report_declares_scope_boundary():
    text = (DOCS / "batch-03-completion-report.md").read_text(encoding="utf-8")
    assert "Phase 3E" in text
    assert "06e3a97039a04b7247350bd57ed5f801998fe97b" in text
    assert "batch/phase-3d-local-historical-bar-intake-03" in text


def test_security_boundary_declares_no_credentials_or_network():
    text = (DOCS / "batch-03-security-and-credential-boundary.md").read_text(encoding="utf-8")
    assert "credential" in text.lower()
    assert "network" in text.lower()
