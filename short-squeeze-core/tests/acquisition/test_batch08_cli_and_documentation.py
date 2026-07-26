"""Batch 08 offline CLI behaviour and required-documentation presence."""

from __future__ import annotations

import json
import re
from pathlib import Path

from squeeze_core.acquisition.phase3a_freeze.cli import build_parser, generate, main, verify

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
SYNTHETIC_ROOT = ROOT / "tests" / "fixtures" / "acquisition" / "batch08" / "synthetic-batch05"

REQUIRED_BATCH08_DOCS = {
    "batch-08-phase3a-request-result-freeze-plan.md",
    "batch-08-admissible-evidence-mapping.md",
    "batch-08-phase3a-request-construction.md",
    "batch-08-phase3a-rule-outcome-summary.md",
    "batch-08-leakage-and-determinism-report.md",
    "batch-08-phase3b-publication-readiness-preview.md",
    "batch-08-test-and-verification-report.md",
    "batch-08-professor-brief.md",
    "batch-08-completion-report.md",
    "batch-09-fresh-session-handoff.md",
}

#: A paragraph mentioning a forbidden claim must also negate or disclaim it.
NEGATION = re.compile(
    r"\b(no|not|never|without|absent|cannot|none|neither|nor|lacks?|missing|"
    r"unstarted|forbidden|blocked|rejected|excluded|omitted)\b"
)

FORBIDDEN_CLAIMS = (
    "predictive accuracy",
    "backtest",
    "profit",
    "p&l",
    "buy signal",
    "trade recommendation",
)


def test_all_required_batch08_documents_exist():
    present = {item.name for item in DOCS.iterdir() if item.is_file()}
    assert REQUIRED_BATCH08_DOCS <= present


def test_batch09_handoff_is_a_real_document():
    text = (DOCS / "batch-09-fresh-session-handoff.md").read_text(encoding="utf-8")
    assert len(text) > 4000
    assert "batch/phase-3d-phase3a-freeze-08" in text
    for section in ("Stop conditions", "Forbidden work", "Definition of done"):
        assert section.lower() in text.lower()


def test_batch08_documents_make_no_predictive_or_trading_claim():
    for name in sorted(REQUIRED_BATCH08_DOCS):
        text = (DOCS / name).read_text(encoding="utf-8").lower()
        # Documents may say a thing is absent; they may not claim it. Checked per
        # paragraph, because a negation and its claim are often on different wrapped lines.
        for paragraph in text.split("\n\n"):
            for claim in FORBIDDEN_CLAIMS:
                if claim in paragraph:
                    assert NEGATION.search(paragraph), (
                        f"{name} appears to claim {claim!r}: {paragraph.strip()[:160]}"
                    )


def test_negation_pattern_actually_discriminates():
    """Guard against the disclaimer check degenerating into a tautology."""
    assert NEGATION.search("no p&l capability exists")
    assert NEGATION.search("backtesting is not supported")
    assert not NEGATION.search("this batch reports a backtest of the strategy")
    assert not NEGATION.search("predictive accuracy was measured at 80 percent")


def test_cli_parser_exposes_the_three_offline_commands():
    parser = build_parser()
    for command in (
        "generate-phase3a-freeze",
        "verify-phase3a-freeze",
        "render-phase3a-freeze-report",
    ):
        assert parser.parse_args([command]).command == command


def test_generate_then_verify_round_trips(tmp_path):
    out = tmp_path / "batch-08"
    assert generate(SYNTHETIC_ROOT, out) == 0
    assert len(list((out / "requests").glob("*.json"))) == 13
    assert len(list((out / "results").glob("*.json"))) == 13
    assert len(list((out / "metrics").glob("*.json"))) == 13
    assert len(list((out / "evidence-associations").glob("*.json"))) == 13
    assert len(list((out / "leakage").glob("*.json"))) == 13
    assert (out / "batch-summary.json").exists()
    assert (out / "determinism-anchors.json").exists()
    assert (out / "manifests" / "case-manifest.json").exists()
    assert (out / "sensitivity" / "local-retrieval-receipt-summary.json").exists()
    assert (out / "freeze-report.md").exists()
    assert verify(SYNTHETIC_ROOT, out) == 0


def test_regeneration_is_byte_identical(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    generate(SYNTHETIC_ROOT, first)
    generate(SYNTHETIC_ROOT, second)
    left = sorted(item.relative_to(first) for item in first.rglob("*") if item.is_file())
    right = sorted(item.relative_to(second) for item in second.rglob("*") if item.is_file())
    assert left == right
    for relative in left:
        assert (first / relative).read_bytes() == (second / relative).read_bytes()


def test_verify_reports_a_mismatch_when_bytes_change(tmp_path):
    out = tmp_path / "batch-08"
    generate(SYNTHETIC_ROOT, out)
    target = out / "requests" / "BATCH01_XNCR_20260718.json"
    target.write_bytes(target.read_bytes() + b" ")
    assert verify(SYNTHETIC_ROOT, out) == 1


def test_case_manifest_records_hashes_and_byte_lengths(tmp_path):
    out = tmp_path / "batch-08"
    generate(SYNTHETIC_ROOT, out)
    rows = json.loads((out / "manifests" / "case-manifest.json").read_text(encoding="utf-8"))
    assert len(rows) == 13
    for row in rows:
        assert len(row["phase3a_request_sha256"]) == 64
        assert len(row["phase3a_result_sha256"]) == 64
        assert row["phase3a_request_byte_length"] > 0
        assert row["phase3a_result_byte_length"] > 0


def test_main_returns_two_when_the_private_root_is_absent(tmp_path):
    assert main(["--private-root", str(tmp_path / "nope"), "verify-phase3a-freeze"]) == 2


def test_real_private_outputs_are_gitignored():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "intake/local-bars/" in gitignore
