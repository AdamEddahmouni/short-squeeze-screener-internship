"""Batch 04 documentation and operator-kit presence tests."""

from pathlib import Path

from squeeze_core.acquisition.historical_data_submission_kit.kit import KIT_ROOT


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
KIT = ROOT / KIT_ROOT

REQUIRED_BATCH04_DOCS = {
    "batch-04-historical-data-submission-kit-plan.md",
    "batch-04-submission-kit-architecture.md",
    "batch-04-preflight-contract.md",
    "batch-04-operator-workflow.md",
    "batch-04-security-entitlement-and-credential-boundary.md",
    "batch-04-determinism-and-fixture-report.md",
    "batch-04-test-and-verification-report.md",
    "batch-04-completion-report.md",
    "batch-05-fresh-session-handoff.md",
}

REQUIRED_KIT_FILES = {
    "README.md",
    "QUICKSTART.md",
    "EXPORT-CHECKLIST.md",
    "PROVIDER-AND-ENTITLEMENT-GUIDE.md",
    "TIMEZONE-INTERVAL-SESSION-GUIDE.md",
    "ADJUSTMENT-SEMANTICS-GUIDE.md",
    "SHA256-AND-BYTE-LENGTH-GUIDE.md",
    "FOLDER-PLACEMENT-GUIDE.md",
    "PREFLIGHT-GUIDE.md",
    "TROUBLESHOOTING.md",
    "FINAL-OPERATOR-CHECKLIST.md",
}


def test_all_required_batch04_documents_exist():
    present = {item.name for item in DOCS.iterdir() if item.is_file()}
    assert REQUIRED_BATCH04_DOCS <= present


def test_operator_kit_files_exist():
    present = {item.name for item in KIT.iterdir() if item.is_file()}
    assert REQUIRED_KIT_FILES <= present
    assert (KIT / "templates" / "intake-manifest.template.json").is_file()
    assert (KIT / "templates" / "column-mapping-profile.template.json").is_file()
    assert (KIT / "templates" / "case-association.template.json").is_file()
    assert (KIT / "examples" / "synthetic-valid" / "raw" / "synthetic-bars.csv").is_file()
    assert (KIT / "examples" / "synthetic-invalid" / "invalid-scenario-index.json").is_file()


def test_completion_report_declares_scope_boundary():
    text = (DOCS / "batch-04-completion-report.md").read_text(encoding="utf-8")
    assert "Phase 3E" in text
    assert "1c3b9329ea63fbfffe68281542bdf692170d50fc" in text
    assert "batch/phase-3d-historical-data-submission-kit-04" in text


def test_security_boundary_declares_no_credentials_or_network():
    text = (
        DOCS / "batch-04-security-entitlement-and-credential-boundary.md"
    ).read_text(encoding="utf-8")
    assert "credential" in text.lower()
    assert "network" in text.lower()
    assert "entitlement" in text.lower()


def test_preflight_contract_lists_statuses():
    text = (DOCS / "batch-04-preflight-contract.md").read_text(encoding="utf-8")
    for status in (
        "READY_FOR_FUTURE_ASSOCIATION",
        "NOT_READY_QUARANTINED",
        "NOT_READY_REJECTED",
    ):
        assert status in text


def test_batch05_handoff_keeps_next_task_conditional():
    text = (DOCS / "batch-05-fresh-session-handoff.md").read_text(encoding="utf-8")
    assert "without real-case association or outcome capture" in text
    assert "Do not start" in text or "do not start" in text
