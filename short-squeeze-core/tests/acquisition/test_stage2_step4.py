"""Tests for ``scripts/acquisition/stage2_step4.py`` (Phase 3E Stage 2 Step 4).

These tests build a hermetic fixture root on ``tmp_path`` and monkeypatch
every module-level ``Final`` Path constant on the imported script module
to point at that root. Without these patches, the script's ``REPO_ROOT``
and downstream ``FREEZE_DIR`` / ``OUTCOMES_DIR`` / ``PHASE3B_DIR`` are
bound to the real ``short-squeeze-core/`` directory at import time (via
``Path(__file__).resolve().parents[2]``) and tests would corrupt the
production pipeline artefacts on every run.

Coverage:

* outcome computation — boundary, completeness, Decimal precision
* leakage audit — 6 checks: pass when freeze + outcome manifest are intact
  and separate; fail-closed when they are not.
* Phase 3B publication — registry + batch + dataset produced with the
  expected schema; audit failures block publication.
* CLI ergonomics — ``--step outcomes|audit|publish|all`` (in-process).

Compatibility note for window-boundary tests:
``_window_bars`` uses an *exclusive-of-cutoff* break (`if moment > end_cutoff:
break`), so to land a test bar *inside* the 24-hour window the bar timestamp
must be ``<= 2026-07-22T13:37:55Z``. Tests that need COMPLETE coverage
append a final bar at exactly ``13:37:55Z`` to satisfy the inclusive-edge
requirement.
"""

from __future__ import annotations

import csv
import importlib.util
import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

STEP4_PATH = Path(__file__).resolve().parents[2] / "scripts" / "acquisition" / "stage2_step4.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("_step4", STEP4_PATH)
    assert spec and spec.loader, "stage2_step4.py must import cleanly"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Hermetic-paths fixture
# ---------------------------------------------------------------------------

def _install_hermetic_paths(
    step4_module, root: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Override every path-bearing module attribute so they point at ``root``."""
    stage2 = root / "build" / "acquisition" / "stage2"
    monkeypatch.setattr(step4_module, "REPO_ROOT", root)
    monkeypatch.setattr(step4_module, "INTAKE_RAW_DIR", root / "intake" / "local-bars" / "ibkr-batch-05" / "raw")
    monkeypatch.setattr(step4_module, "STAGE2_DIR", stage2)
    monkeypatch.setattr(step4_module, "COLLECTION_SUMMARY_PATH", stage2 / "collection-summary.json")
    monkeypatch.setattr(step4_module, "SHA256_MANIFEST_PATH", stage2 / "sha256-manifest.json")
    monkeypatch.setattr(step4_module, "FREEZE_DIR", stage2 / "phase3a-freeze")
    monkeypatch.setattr(step4_module, "OUTCOMES_DIR", stage2 / "outcomes")
    monkeypatch.setattr(step4_module, "LEAKAGE_AUDIT_DIR", stage2 / "leakage-audit")
    monkeypatch.setattr(step4_module, "PHASE3B_DIR", stage2 / "phase3b")


def _stub_preregistration_files(root: Path) -> None:
    """Create the path-relative stubs ``run_leakage_audit`` expects to exist."""
    short_squeeze_root = root.parent
    plan_path = short_squeeze_root / "short-squeeze-core" / "docs" / "phase-3e-stage2-acquisition-plan.md"
    freeze_script_path = (
        short_squeeze_root / "short-squeeze-core" / "scripts" /
        "acquisition" / "freeze_phase3a_evaluations.py"
    )
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text("# stub acquisition plan\n", encoding="utf-8")
    freeze_script_path.parent.mkdir(parents=True, exist_ok=True)
    freeze_script_path.write_text("# stub freeze script\n", encoding="utf-8")


@pytest.fixture
def step4_in_tmp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> object:
    """Return the script module with all paths redirected to ``tmp_path``."""
    root = tmp_path / "short-squeeze-core"
    root.mkdir()
    step4 = _load_module()
    _install_hermetic_paths(step4, root, monkeypatch)
    _stub_preregistration_files(root)

    # Stub the git backend so the leakage-audit checks see a present plan /
    # freeze script in history. The lambda returns a single synthetic commit
    # regardless of ``diff_filter`` for simplicity.
    monkeypatch.setattr(
        step4, "_git_log_paths",
        lambda *a, **kw: [("f" * 40, "2026-07-21T13:00:00+00:00")],
    )
    return step4


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

def _write_forward_csv(rows: list[tuple[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "timestamp_utc", "open", "high", "low", "close", "volume",
            "wap", "bar_count", "timestamp_epoch",
            "requested_symbol", "request_name", "resolved_con_id",
        ])
        for stamp, close in rows:
            epoch = int(datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp())
            writer.writerow([
                stamp, close, close, close, close, "0", close, "0",
                str(epoch), "TST", "ADJUSTED_FORWARD_OUTCOME_24H", "0",
            ])


def _populate_minimal_freeze(step4, symbol: str) -> None:
    """Write a stub Phase 3A freeze so audit check #3 passes."""
    freeze_dir = step4.FREEZE_DIR / symbol
    freeze_dir.mkdir(parents=True, exist_ok=True)
    request_path = freeze_dir / "frozen_request.json"
    result_path = freeze_dir / "frozen_result.json"
    metadata_path = freeze_dir / "freeze_metadata.json"
    request_path.write_bytes(step4.canonical_json_bytes({
        "symbol": symbol, "as_of": step4.PHASE_3A_AS_OF.isoformat(), "kind": "request",
    }))
    result_path.write_bytes(step4.canonical_json_bytes({
        "symbol": symbol, "as_of": step4.PHASE_3A_AS_OF.isoformat(), "kind": "result",
    }))
    meta = {
        "symbol": symbol,
        "freeze_timestamp_utc": datetime.now(UTC).isoformat(),
        "request_id": "stub-req",
        "result_id": "stub-res",
        "request_sha256": step4._sha256_of(request_path),
        "result_sha256": step4._sha256_of(result_path),
        "observation_count": 0,
    }
    metadata_path.write_bytes(json.dumps(meta, indent=2).encode("utf-8"))


def _populate_freeze_for_all(step4) -> None:
    for s in step4.SYMBOLS:
        _populate_minimal_freeze(step4, s)


def _populate_all_forward_csvs(
    step4, rows: list[tuple[str, str]] | None,
) -> None:
    for s in step4.SYMBOLS:
        _write_forward_csv(rows or [], step4.INTAKE_RAW_DIR / f"{s}-forward-outcome.csv")


# ---------------------------------------------------------------------------
# Step 4a — outcomes
# ---------------------------------------------------------------------------

def test_outcomes_no_reference_bar_marks_unavailable(step4_in_tmp) -> None:
    """Bars entirely before the adjusted forward start -> UNAVAILABLE."""
    step4 = step4_in_tmp
    _write_forward_csv(
        [("2026-07-20T21:37:00Z", "10.0"), ("2026-07-20T21:38:00Z", "10.5")],
        step4.INTAKE_RAW_DIR / "AVTX-forward-outcome.csv",
    )
    _populate_all_forward_csvs(step4, [])
    step4.compute_outcomes(force=True)
    obs = step4.RetrospectiveOutcomeObservation.model_validate_json(
        step4.OUTCOMES_DIR.joinpath("AVTX", "outcome_observation.json").read_bytes()
    )
    assert obs.completeness is step4.OutcomeCompleteness.UNAVAILABLE
    assert obs.reference_price is None
    assert obs.detection_boundary == step4.BOUNDARY_TS
    # Confirm the file lives under the hermetic tmp root, NOT the real tree.
    real_root = Path(__file__).resolve().parents[2]
    assert not str(step4.OUTCOMES_DIR).startswith(str(real_root))


def test_outcomes_partial_window_with_no_crossing(step4_in_tmp) -> None:
    """Bars cover part of the window but stop early -> PARTIAL + max_up partial."""
    step4 = step4_in_tmp
    _populate_all_forward_csvs(step4, [])  # empty CSVs for non-target symbols FIRST
    _write_forward_csv([
        ("2026-07-21T13:38:00Z", "19.10"),  # first in-window (reference)
        ("2026-07-21T14:00:00Z", "20.00"),
        ("2026-07-21T15:00:00Z", "21.00"),
        ("2026-07-21T16:00:00Z", "21.50"),
    ], step4.INTAKE_RAW_DIR / "XNCR-forward-outcome.csv")
    step4.compute_outcomes(force=True)
    obs = step4.RetrospectiveOutcomeObservation.model_validate_json(
        step4.OUTCOMES_DIR.joinpath("XNCR", "outcome_observation.json").read_bytes()
    )
    assert obs.reference_price == Decimal("19.10")
    assert obs.completeness is step4.OutcomeCompleteness.PARTIAL
    # 21.50 vs 19.10 -> Decimal('12.56544502617801...')%
    assert obs.maximum_observed_move_percent == pytest.approx(
        Decimal("12.565445026"), abs=Decimal("0.001"),
    )


def test_outcomes_substantial_upward_crossing_detected(step4_in_tmp) -> None:
    """A +30% bar in a complete +24h window produces SUBSTANTIAL_UPWARD_MOVE."""
    step4 = step4_in_tmp
    _populate_all_forward_csvs(step4, [])  # empty CSVs for non-target symbols FIRST
    _write_forward_csv([
        ("2026-07-21T13:38:00Z", "10.00"),  # first in-window (reference)
        ("2026-07-21T14:00:00Z", "13.00"),  # +30% (crosses +25%)
        ("2026-07-21T15:00:00Z", "9.50"),   # -5%
        # Final bar at the inclusive edge of the 24h window — the exclusive
        # `_window_bars` break accepts ``moment <= 13:37:55Z`` and surfaces
        # ``last_seen = 13:37:55Z >= ADJUSTED_FORWARD_END (= 13:37:55Z)`` ->
        # COMPLETE.
        ("2026-07-22T13:37:55Z", "10.20"),
    ], step4.INTAKE_RAW_DIR / "GPRE-forward-outcome.csv")
    step4.compute_outcomes(force=True)
    obs = step4.RetrospectiveOutcomeObservation.model_validate_json(
        step4.OUTCOMES_DIR.joinpath("GPRE", "outcome_observation.json").read_bytes()
    )
    assert obs.reference_price == Decimal("10.00")
    assert obs.maximum_observed_move_percent == Decimal("30")
    assert obs.maximum_adverse_move_percent == Decimal("-5")
    assert obs.completeness is step4.OutcomeCompleteness.COMPLETE


def test_outcomes_reference_price_is_decimal_typed(step4_in_tmp) -> None:
    step4 = step4_in_tmp
    _populate_all_forward_csvs(step4, [])  # empty CSVs for non-target symbols FIRST
    _write_forward_csv([("2026-07-21T13:38:00Z", "7.89")],
                      step4.INTAKE_RAW_DIR / "BHVN-forward-outcome.csv")
    step4.compute_outcomes(force=True)
    obs = step4.RetrospectiveOutcomeObservation.model_validate_json(
        step4.OUTCOMES_DIR.joinpath("BHVN", "outcome_observation.json").read_bytes()
    )
    assert isinstance(obs.reference_price, Decimal)
    assert obs.reference_price == Decimal("7.89")


# ---------------------------------------------------------------------------
# Step 4b — leakage audit
# ---------------------------------------------------------------------------

def test_audit_passes_when_freeze_and_outcome_manifest_are_valid(step4_in_tmp) -> None:
    step4 = step4_in_tmp
    _populate_freeze_for_all(step4)
    _populate_all_forward_csvs(step4, [])
    step4.compute_outcomes(force=True)
    summary = step4.run_leakage_audit()
    payload = json.loads(step4.LEAKAGE_AUDIT_DIR.joinpath("audit.json").read_bytes())
    assert summary["audit_passed"] is True
    assert payload["audit_passed"] is True
    assert all(c["passed"] for c in payload["checks"].values())


def test_audit_fails_when_outcome_manifest_is_inside_freeze_dir(step4_in_tmp) -> None:
    step4 = step4_in_tmp
    _populate_freeze_for_all(step4)
    _populate_all_forward_csvs(step4, [])
    step4.compute_outcomes(force=True)
    # Smuggle the manifest under FREEZE_DIR to fail check #5.
    original_manifest = step4.OUTCOMES_DIR / "outcomes_manifest.json"
    intruder = step4.FREEZE_DIR / "outcomes_manifest.json"
    intruder.write_bytes(original_manifest.read_bytes())
    summary = step4.run_leakage_audit()
    payload = json.loads(step4.LEAKAGE_AUDIT_DIR.joinpath("audit.json").read_bytes())
    assert summary["audit_passed"] is False
    assert payload["checks"]["outcome_manifest_separate"]["passed"] is False


def test_audit_fails_when_freeze_metadata_sha_drifted(step4_in_tmp) -> None:
    step4 = step4_in_tmp
    _populate_freeze_for_all(step4)
    _populate_all_forward_csvs(step4, [])
    step4.compute_outcomes(force=True)
    target = step4.FREEZE_DIR / "AVTX" / "frozen_request.json"
    target.write_bytes(target.read_bytes() + b" ")
    summary = step4.run_leakage_audit()
    payload = json.loads(step4.LEAKAGE_AUDIT_DIR.joinpath("audit.json").read_bytes())
    assert summary["audit_passed"] is False
    assert payload["checks"]["freeze_metadata_sha_matches"]["passed"] is False


# ---------------------------------------------------------------------------
# Step 4c — Phase 3B publication
# ---------------------------------------------------------------------------

def test_publish_blocked_when_audit_fails(step4_in_tmp) -> None:
    step4 = step4_in_tmp
    _populate_freeze_for_all(step4)
    _populate_all_forward_csvs(step4, [])
    step4.compute_outcomes(force=True)
    target = step4.FREEZE_DIR / "PESI" / "frozen_result.json"
    target.write_bytes(target.read_bytes() + b" ")
    with pytest.raises(RuntimeError, match="leakage audit did not pass"):
        step4.publish_phase3b_dataset(force=True)
    # The phase3b directory should not contain the published artefacts.
    assert not list(step4.PHASE3B_DIR.glob("*.json"))
    assert not list(step4.PHASE3B_DIR.glob("*.jsonl"))
    assert not list(step4.PHASE3B_DIR.glob("*.csv"))


def test_publish_produces_registry_batch_and_dataset(step4_in_tmp) -> None:
    step4 = step4_in_tmp
    from squeeze_core.evaluation import CandidateEvaluationResult
    from squeeze_core.evaluation.serialization import serialize_candidate_evaluation
    from tests.research.helpers import BASE_EVALUATION

    # ``BASE_EVALUATION`` is a fully-validated ``CandidateEvaluationResult``
    # with real ``rule_results`` matching the canonical Phase 3A policy.
    # Reusing it (with per-symbol overrides) lets the batch reader in
    # ``squeeze_core.research.batch`` process every entry instead of skipping
    # all 13 due to a stub-evaluation interpreter mismatch. ``model_copy``
    # is the idiomatic Pydantic v2 way to derive a frozen copy with field
    # overrides; the underlying ``BASE_EVALUATION`` is not mutated.
    for s in step4.SYMBOLS:
        freeze_dir = step4.FREEZE_DIR / s
        freeze_dir.mkdir(parents=True, exist_ok=True)
        request_path = freeze_dir / "frozen_request.json"
        result_path = freeze_dir / "frozen_result.json"
        request_path.write_bytes(step4.canonical_json_bytes({
            "symbol": s, "as_of": step4.PHASE_3A_AS_OF.isoformat(), "kind": "request",
        }))
        result = BASE_EVALUATION.model_copy(update={
            "symbol": s,
            "as_of": step4.PHASE_3A_AS_OF,
        })
        result_path.write_bytes(serialize_candidate_evaluation(result))
        # Roundtrip the JSON via Pydantic so the test fails fast if
        # canonical overrides produce a payload the batch reader rejects.
        CandidateEvaluationResult.model_validate_json(result_path.read_bytes())
        meta = {
            "symbol": s,
            "freeze_timestamp_utc": datetime.now(UTC).isoformat(),
            "request_id": f"eval-{s}",
            "result_id": f"eval-{s}",
            "request_sha256": step4._sha256_of(request_path),
            "result_sha256": step4._sha256_of(result_path),
            "observation_count": 0,
        }
        (freeze_dir / "freeze_metadata.json").write_bytes(
            json.dumps(meta, indent=2).encode("utf-8")
        )

    _populate_all_forward_csvs(step4, [])  # -> UNAVAILABLE -> INSUFFICIENT_DATA
    step4.compute_outcomes(force=True)

    publish = step4.publish_phase3b_dataset(force=True)
    assert publish["status"] == "published"
    assert publish["row_count"] == 13

    registry = step4.CandidateCaseRegistry.model_validate_json(
        step4.PHASE3B_DIR.joinpath("case_registry.json").read_bytes()
    )
    assert len(registry.entries) == 13
    batch = step4.BatchEvaluationResult.model_validate_json(
        step4.PHASE3B_DIR.joinpath("batch_result.json").read_bytes()
    )
    dataset = step4.ResearchDataset.model_validate_json(
        step4.PHASE3B_DIR.joinpath("phase_3b_research_dataset.json").read_bytes()
    )
    assert len(dataset.rows) == 13
    # Empty forward CSVs -> UNAVAILABLE observation completeness -> per
    # ``label_outcome`` policy v1, the label is ``OUTCOME_UNKNOWN``.
    assert all(
        r.outcome_label.value == "OUTCOME_UNKNOWN" for r in dataset.rows
    )
    jsonl_bytes = step4.PHASE3B_DIR.joinpath("phase_3b_research_dataset.jsonl").read_bytes()
    assert jsonl_bytes.count(b"\n") == 13
    csv_bytes = step4.PHASE3B_DIR.joinpath("phase_3b_research_dataset.csv").read_bytes()
    assert csv_bytes.count(b"\n") >= 14


# ---------------------------------------------------------------------------
# CLI ergonomics — in-process (NOT subprocess) so monkeypatched Final paths
# stay in effect across the dispatch.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("step", ["outcomes", "audit", "publish", "all"])
def test_cli_step_runs_with_hermetic_root(step4_in_tmp, step: str) -> None:
    """Each ``--step`` subcommand runs and exits 0 in-process for the fixture root."""
    step4 = step4_in_tmp
    # Every audit check post-outcome needs both freezes & per-symbol outcomes;
    # compute_outcomes is a no-op for empty forward CSVs that still produces
    # valid UNAVAILABLE observations.
    _populate_freeze_for_all(step4)
    _populate_all_forward_csvs(
        step4,
        [("2026-07-21T13:38:00Z", "10.00"), ("2026-07-22T13:37:55Z", "10.20")],
    )
    step4.compute_outcomes(force=True)

    rc = step4.main(["--step", step])
    assert rc == 0, f"--step {step} returned non-zero ({rc})"
    # And no real-tree artefact was written by mistake.
    real_root = Path(__file__).resolve().parents[2]
    assert not str(step4.OUTCOMES_DIR).startswith(str(real_root))
    assert not str(step4.PHASE3B_DIR).startswith(str(real_root))
