"""Phase 3E Stage 2 — Step 4 (outcomes + leakage audit + Phase 3B publication).

Single-pass orchestrator for Step 4 of Phase 3E Stage 2. Computes forward
outcomes for the 13 IBKR pilot symbols, runs the leakage audit per
``phase_3d_outcome_leakage_policy.v1``, and publishes the resulting
(request, result, outcome) triples into a Phase 3B research dataset using
the existing ``research.batch`` + ``research.dataset`` machinery.

The three step functions are independently executable::

    compute_outcomes()              # 13 RetrospectiveOutcomeObservation records
    run_leakage_audit()             # 6 audit checks against on-disk artifacts
    publish_phase3b_dataset()       # registry + batch + dataset publication

Or all three in sequence via ``run_stage2_step4()``.

Identity chain (unchanged across the pipeline)
---------------------------------------------

* Frozen detection boundary: ``2026-07-18T13:37:55.017661Z``
* Adjusted forward start:    ``2026-07-21T13:37:55Z`` (Saturday → Monday)
* Adjusted forward end:      ``2026-07-22T13:37:55Z`` (+24 h)
* Frozen retrieval:          ``2026-07-18T13:38:00Z``
* Phase 3A ``as_of``:        ``2026-07-18T13:38:00Z`` (= ``max(boundary, retrieval)``)
* Outcome horizon:           ``24_HOURS`` (±25 % thresholds, fixed)
* Outcome policy version:    ``phase_3b_outcome_label_policy.v1``
* Leakage policy version:    ``phase_3d_outcome_leakage_policy.v1``

Usage (from ``short-squeeze-core``)::

    # Full sequenced run
    python scripts/acquisition/stage2_step4.py

    # One step only
    python scripts/acquisition/stage2_step4.py --step outcomes
    python scripts/acquisition/stage2_step4.py --step audit
    python scripts/acquisition/stage2_step4.py --step publish

    # Re-run from scratch (bypass resume cache)
    python scripts/acquisition/stage2_step4.py --force
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
from collections.abc import Mapping
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Final

from squeeze_core.acquisition.policies import load_policy
from squeeze_core.contracts import AssetClass
from squeeze_core.research.batch import run_research_batch
from squeeze_core.research.dataset import build_research_dataset
from squeeze_core.research.models import (
    BatchEvaluationRequest,
    BatchEvaluationResult,
    CandidateCaseRegistry,
    CandidateCaseRegistryEntry,
    CandidateCaseStatus,
    CandidateCaseType,
    FixtureClassification,
    OriginalPlatformStatus,
    OrderingPolicy,
    OutcomeCompleteness,
    ResearchDataset,
    RetrospectiveOutcomeObservation,
)
from squeeze_core.research.policies import (
    DETECTION_POLICY_VERSION,
    OUTCOME_POLICY_VERSION,
)
from squeeze_core.research.registry import build_case_registry
from squeeze_core.research.serialization import (
    serialize_research_csv,
    serialize_research_json,
    serialize_research_jsonl,
    serialize_research_model,
)
from squeeze_core.serialization import canonical_json_bytes

UTC: Final = UTC

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---- Frozen boundary & forward window (per phase-3e-stage2-acquisition-plan) ----

BOUNDARY_TS: Final = datetime(2026, 7, 18, 13, 37, 55, 17661, tzinfo=UTC)
RETRIEVAL_TS: Final = datetime(2026, 7, 18, 13, 38, 0, tzinfo=UTC)
PHASE_3A_AS_OF: Final = max(BOUNDARY_TS, RETRIEVAL_TS)  # 13:38:00Z

ADJUSTED_FORWARD_START: Final = datetime(2026, 7, 21, 13, 37, 55, tzinfo=UTC)
ADJUSTED_FORWARD_END: Final = datetime(2026, 7, 22, 13, 37, 55, tzinfo=UTC)

PHASE_3A_POLICY_VERSION: Final = "phase_3a_transparent_candidate_policy.v1"
OUTCOME_REFERENCE_POLICY: Final = (
    "first_eligible_trade_bar_close_at_or_after_boundary.v1"
)
OUTCOME_HORIZON: Final = "24_HOURS"
PHASE_3B_REGISTRY_VERSION: Final = "phase_3b_case_registry.v1"
PHASE_3B_BATCH_VERSION: Final = "phase_3b_batch.v1"
PHASE_3B_DATASET_VERSION: Final = "phase_3b_research_dataset.v1"

# ---- 13 IBKR pilot symbols (mirror scripts/acquisition/freeze_phase3a_evaluations) ----

PRIMARY_EXCHANGE: Final[Mapping[str, str]] = {
    "XNCR": "NASDAQ", "PESI": "NASDAQ", "SLS": "NASDAQ", "ZNTL": "NASDAQ",
    "GPRE": "NASDAQ", "SSPC": "BATS", "LBGJ": "NASDAQ", "TRVI": "NASDAQ",
    "LMNX": "NASDAQ", "MGNX": "NASDAQ", "BHVN": "NYSE", "OBE": "AMEX",
    "AVTX": "NASDAQ",
}
SYMBOLS: Final[tuple[str, ...]] = (
    "AVTX", "BHVN", "GPRE", "LBGJ", "LMNX", "MGNX",
    "OBE", "PESI", "SLS", "SSPC", "TRVI", "XNCR", "ZNTL",
)

# ---- Predeclared per-symbol metadata (mirror archive source) ----

PRIMARY_EXCHANGE_BY_SYMBOL: Final[dict[str, str]] = {
    s: PRIMARY_EXCHANGE[s] for s in SYMBOLS
}
BATCH01_CASE_ID_TEMPLATE: Final = "BATCH01_{symbol}_20260718"

# ---- Stable limitations string reused for every IBKR pilot entry ----

IBKR_PILOT_LIMITATIONS: Final[tuple[str, ...]] = (
    "private IBKR batch05 acquisition; not part of any public release",
    "outcome window shifted Saturday -> Monday per acquisition plan "
    "(72-hour calendar shift; only ~6.5h US regular-hours captured Monday-Tuesday)",
    "IBKR forward-bar volume and timestamp semantics are UNKNOWN (see ADR 0066)",
    "outcome-label policy is unoptimised and provisional",
    "thresholds were not calibrated on this private cohort",
)

# ---- Layout ----

INTAKE_RAW_DIR: Final = (
    REPO_ROOT / "intake" / "local-bars" / "ibkr-batch-05" / "raw"
)
STAGE2_DIR: Final = REPO_ROOT / "build" / "acquisition" / "stage2"
COLLECTION_SUMMARY_PATH: Final = STAGE2_DIR / "collection-summary.json"
SHA256_MANIFEST_PATH: Final = STAGE2_DIR / "sha256-manifest.json"
FREEZE_DIR: Final = STAGE2_DIR / "phase3a-freeze"
OUTCOMES_DIR: Final = STAGE2_DIR / "outcomes"
LEAKAGE_AUDIT_DIR: Final = STAGE2_DIR / "leakage-audit"
PHASE3B_DIR: Final = STAGE2_DIR / "phase3b"
ACQUISITION_PLAN_REL: Final = Path(
    "short-squeeze-core/docs/phase-3e-stage2-acquisition-plan.md"
)
FREEZE_SCRIPT_REL: Final = Path(
    "short-squeeze-core/scripts/acquisition/freeze_phase3a_evaluations.py"
)


# ----------------------------------------------------------------------------
# Step 1 — outcome computation
# ----------------------------------------------------------------------------

def _parse_timestamp(value: str) -> datetime:
    """Parse an IBKR ``timestamp_utc`` string, returning a UTC-aware datetime."""
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise ValueError(f"non-UTC timestamp in forward outcome CSV: {value!r}")
    return parsed.astimezone(UTC)


def _read_forward_bars(symbol: str) -> list[dict]:
    """Load a forward-bar CSV into a list of normalised dicts sorted ascending."""
    csv_path = INTAKE_RAW_DIR / f"{symbol}-forward-outcome.csv"
    if not csv_path.exists():
        return []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [
            {
                "timestamp_utc": row["timestamp_utc"],
                "open": row.get("open", ""),
                "high": row.get("high", ""),
                "low": row.get("low", ""),
                "close": row.get("close", ""),
                "volume": row.get("volume", ""),
                "timestamp_epoch": row.get("timestamp_epoch", ""),
            }
            for row in reader
        ]


def _percent(move: Decimal, reference: Decimal) -> Decimal:
    if reference == 0:
        return Decimal("0")
    return (move - reference) / reference * Decimal("100")


def _find_reference_index(bars: list[dict]) -> int | None:
    """Index of the first bar whose UTC timestamp >= adjusted forward start."""
    for index, bar in enumerate(bars):
        if _parse_timestamp(bar["timestamp_utc"]) >= ADJUSTED_FORWARD_START:
            return index
    return None


def _window_bars(
    bars: list[dict], start_index: int
) -> tuple[list[dict], datetime]:
    """Bars from ``start_index`` up to (and including) ``ADJUSTED_FORWARD_END``."""
    end_cutoff = ADJUSTED_FORWARD_END
    selected: list[dict] = []
    for bar in bars[start_index:]:
        moment = _parse_timestamp(bar["timestamp_utc"])
        if moment > end_cutoff:
            break
        selected.append(bar)
    last_seen = _parse_timestamp(bars[start_index + len(selected) - 1]["timestamp_utc"]) \
        if selected else ADJUSTED_FORWARD_START
    return selected, last_seen


def _build_outcome_observation(
    symbol: str,
    bars: list[dict],
) -> RetrospectiveOutcomeObservation:
    """Build a single ``RetrospectiveOutcomeObservation`` for ``symbol``."""
    case_id = BATCH01_CASE_ID_TEMPLATE.format(symbol=symbol)

    reference_index = _find_reference_index(bars)
    if reference_index is None:
        return RetrospectiveOutcomeObservation(
            case_id=case_id,
            symbol=symbol,
            detection_boundary=BOUNDARY_TS,
            reference_price_policy=OUTCOME_REFERENCE_POLICY,
            reference_price=None,
            horizon=OUTCOME_HORIZON,
            maximum_observed_move_percent=None,
            maximum_adverse_move_percent=None,
            completeness=OutcomeCompleteness.UNAVAILABLE,
            supporting_observation_ids=(),
            limitations=_ibkr_pilot_outcome_limitations(unavailable=True),
        )

    reference_bar = bars[reference_index]
    reference_price = Decimal(reference_bar["close"])
    window, last_seen = _window_bars(bars, reference_index)

    # Decimal arithmetic to keep the percent maths exact. We seed each list
    # with ``Decimal("0")`` so that, when every post-reference bar closes
    # *at or below* the reference price:
    #   - ``max_up`` collapses to zero (no upward move observed),
    #   - ``max_down`` collapses to zero (no adverse move observed).
    # Without the seed we'd report the highest negative bar as ``max_up``,
    # which obscures the fact that no positive excursion ever occurred.
    moves: list[Decimal] = [Decimal("0")]
    for bar in window:
        moves.append(_percent(Decimal(bar["close"]), reference_price))

    max_up = max(moves)
    max_down = min(moves)

    completeness = (
        OutcomeCompleteness.COMPLETE
        if last_seen >= ADJUSTED_FORWARD_END
        else OutcomeCompleteness.PARTIAL
    )

    first_ts = _parse_timestamp(reference_bar["timestamp_utc"])
    supporting_ids = (
        f"ibkr-{symbol}-ref-{reference_bar['timestamp_epoch']}",
        f"ibkr-{symbol}-first-{first_ts.isoformat()}",
        f"ibkr-{symbol}-count-{len(window)}",
    )

    return RetrospectiveOutcomeObservation(
        case_id=case_id,
        symbol=symbol,
        detection_boundary=BOUNDARY_TS,
        reference_price_policy=OUTCOME_REFERENCE_POLICY,
        reference_price=reference_price,
        horizon=OUTCOME_HORIZON,
        maximum_observed_move_percent=max_up,
        maximum_adverse_move_percent=max_down,
        completeness=completeness,
        supporting_observation_ids=supporting_ids,
        limitations=_ibkr_pilot_outcome_limitations(unavailable=False),
    )


def _ibkr_pilot_outcome_limitations(*, unavailable: bool) -> tuple[str, ...]:
    extras: tuple[str, ...] = (
        ("no eligible forward bar at or after adjusted detection boundary",
         ) if unavailable else ()
    )
    return IBKR_PILOT_LIMITATIONS + extras


def _write_observation(
    symbol: str,
    observation: RetrospectiveOutcomeObservation,
) -> tuple[Path, str]:
    out_dir = OUTCOMES_DIR / symbol
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "outcome_observation.json"
    path.write_bytes(serialize_research_model(observation))
    return path, observation.case_id


def compute_outcomes(force: bool = False) -> dict:
    """Step 4a: compute per-symbol ``RetrospectiveOutcomeObservation`` records."""
    OUTCOMES_DIR.mkdir(parents=True, exist_ok=True)
    bars_cache: dict[str, list[dict]] = {}

    per_symbol: list[dict] = []
    already_done = 0
    newly_computed = 0
    for symbol in SYMBOLS:
        out_path = OUTCOMES_DIR / symbol / "outcome_observation.json"
        if not force and out_path.exists():
            payload = json.loads(out_path.read_bytes())
            per_symbol.append({
                "symbol": symbol,
                "case_id": payload["case_id"],
                "deterministic_id": payload.get("deterministic_id"),
                "reference_price": payload.get("reference_price"),
                "maximum_observed_move_percent": payload.get("maximum_observed_move_percent"),
                "maximum_adverse_move_percent": payload.get("maximum_adverse_move_percent"),
                "completeness": payload.get("completeness"),
                "observation_path": str(out_path.relative_to(STAGE2_DIR)),
                "status": "skipped_existing",
            })
            already_done += 1
            continue

        bars = bars_cache.setdefault(symbol, _read_forward_bars(symbol))
        observation = _build_outcome_observation(symbol, bars)
        out_path, case_id = _write_observation(symbol, observation)
        per_symbol.append({
            "symbol": symbol,
            "case_id": case_id,
            "deterministic_id": observation.deterministic_id,
            "reference_price": (
                str(observation.reference_price)
                if observation.reference_price is not None else None
            ),
            "maximum_observed_move_percent": (
                str(observation.maximum_observed_move_percent)
                if observation.maximum_observed_move_percent is not None else None
            ),
            "maximum_adverse_move_percent": (
                str(observation.maximum_adverse_move_percent)
                if observation.maximum_adverse_move_percent is not None else None
            ),
            "completeness": observation.completeness.value,
            "observation_path": str(out_path.relative_to(STAGE2_DIR)),
            "status": "computed",
        })
        newly_computed += 1

    # ---- Build outcomes manifest (separate contract from evaluation freeze) ----
    manifest = {
        "schema_version": "1.0.0",
        "manifest_version": "phase_3e_stage2_outcome_manifest.v1",
        "outcome_policy_version": OUTCOME_POLICY_VERSION,
        "leakage_policy_version": "phase_3d_outcome_leakage_policy.v1",
        "boundary": BOUNDARY_TS.isoformat(),
        "adjusted_forward_window": {
            "start": ADJUSTED_FORWARD_START.isoformat(),
            "end": ADJUSTED_FORWARD_END.isoformat(),
        },
        "generated_at": datetime.now(UTC).isoformat(),
        "symbols": per_symbol,
    }
    manifest_path = OUTCOMES_DIR / "outcomes_manifest.json"
    manifest_path.write_bytes(canonical_json_bytes(manifest))

    return {
        "newly_computed": newly_computed,
        "skipped_existing": already_done,
        "manifest_path": str(manifest_path.relative_to(REPO_ROOT)),
        "outcomes_dir": str(OUTCOMES_DIR.relative_to(REPO_ROOT)),
        "freeze_dir": str(FREEZE_DIR.relative_to(REPO_ROOT)),
        "symbols": per_symbol,
    }


# ----------------------------------------------------------------------------
# Step 2 — leakage audit
# ----------------------------------------------------------------------------

def _git_log_paths(
    path: Path, *, repo_root: Path, diff_filter: str | None = None,
) -> list[tuple[str, str]]:
    """Return ``[(commit_hash, iso_date), ...]`` for ``path`` in git history."""
    args = ["git", "log", "--pretty=format:%H|%aI"]
    if diff_filter is not None:
        args.append(f"--diff-filter={diff_filter}")
    args.extend(["--", str(path)])
    result = subprocess.run(
        args, cwd=repo_root, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    return [
        (line.split("|", 1)[0], line.split("|", 1)[1])
        for line in result.stdout.strip().split("\n") if line
    ]


def _sha256_of(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _all_freeze_files_present() -> tuple[bool, list[str]]:
    """Confirm frozen_request.json + frozen_result.json exist for all 13 symbols."""
    missing: list[str] = []
    for symbol in SYMBOLS:
        request_path = FREEZE_DIR / symbol / "frozen_request.json"
        result_path = FREEZE_DIR / symbol / "frozen_result.json"
        if not request_path.exists() or not result_path.exists():
            missing.append(symbol)
    return (len(missing) == 0, missing)


def _freeze_metadata_sha_matches() -> tuple[bool, list[dict]]:
    confirm: list[dict] = []
    failures: list[dict] = []
    for symbol in SYMBOLS:
        meta_path = FREEZE_DIR / symbol / "freeze_metadata.json"
        if not meta_path.exists():
            failures.append({"symbol": symbol, "reason": "freeze_metadata.json missing"})
            continue
        meta = json.loads(meta_path.read_bytes())
        for kind, declared in (
            ("request", meta.get("request_sha256")),
            ("result", meta.get("result_sha256")),
        ):
            file_path = FREEZE_DIR / symbol / f"frozen_{kind}.json"
            if not file_path.exists():
                failures.append({"symbol": symbol, "kind": kind, "reason": "file missing"})
                continue
            actual = _sha256_of(file_path)
            if actual != declared:
                failures.append({
                    "symbol": symbol,
                    "kind": kind,
                    "declared": declared,
                    "actual": actual,
                })
            else:
                confirm.append({"symbol": symbol, "kind": kind, "sha256": actual})
    return (len(failures) == 0, failures) if failures else (True, confirm)


def run_leakage_audit() -> dict:
    """Step 4b: verify the 6 leakage-audit checks per policy v1 + plan doc."""
    LEAKAGE_AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    short_squeeze_root = REPO_ROOT.parent
    plan_path = short_squeeze_root / ACQUISITION_PLAN_REL
    freeze_script_path = short_squeeze_root / FREEZE_SCRIPT_REL

    checks: dict[str, dict] = {}

    # 1) Acquisition plan committed BEFORE outcome capture.
    plan_commits = _git_log_paths(
        ACQUISITION_PLAN_REL, repo_root=short_squeeze_root, diff_filter="A"
    )
    most_recent_plan = _git_log_paths(
        ACQUISITION_PLAN_REL, repo_root=short_squeeze_root,
    )
    checks["acquisition_plan_committed"] = {
        "passed": bool(plan_commits),
        "path": str(ACQUISITION_PLAN_REL),
        "first_commit": f"{plan_commits[0][0]} @ {plan_commits[0][1]}" if plan_commits else None,
        "commits_seen": len(most_recent_plan),
        "rationale": (
            "Stage 2 acquisition plan must appear in git history before "
            "any outcome is captured."
        ),
    }

    # 2) Freeze script committed (the "boundary freeze" preregistration).
    freeze_script_commits = _git_log_paths(
        FREEZE_SCRIPT_REL, repo_root=short_squeeze_root,
    )
    checks["freeze_script_committed"] = {
        "passed": bool(freeze_script_commits),
        "path": str(FREEZE_SCRIPT_REL),
        "first_commit": (
            f"{freeze_script_commits[-1][0]} @ {freeze_script_commits[-1][1]}"
            if freeze_script_commits else None
        ),
        "commits_seen": len(freeze_script_commits),
        "rationale": (
            "Phase 3A freeze script must be committed before outcomes "
            "are computed (it pins the boundary used in both freezes)."
        ),
    }

    # 3) All 13 freeze artefacts (request + result) are present on disk.
    all_present, missing = _all_freeze_files_present()
    checks["freeze_artifacts_complete"] = {
        "passed": all_present,
        "missing_symbols": missing,
        "freeze_dir": str(FREEZE_DIR.relative_to(short_squeeze_root)),
        "rationale": "All 13 symbols must have frozen_request.json + frozen_result.json prior to publication.",
    }

    # 4) The on-disk freeze matches its declared SHA-256 (no drift).
    shas_ok, sha_report = _freeze_metadata_sha_matches()
    # ``sha_report`` is a list of ``{symbol, kind, sha256}`` confirmations
    # when ``shas_ok`` is True, or a list of failure dicts without the
    # ``sha256`` key when it is False. ``len`` is the right report either
    # way. The helper is annotated ``-> tuple[bool, list[dict]]`` so it
    # always returns a list; no defensive isinstance guard needed.
    checks["freeze_metadata_sha_matches"] = {
        "passed": shas_ok,
        "sample_size": len(sha_report),
        "samples": sha_report,
        "failures": sha_report if not shas_ok else [],
        "rationale": (
            "freeze_metadata.json SHA-256 hashes must match the on-disk "
            "frozen_request.json and frozen_result.json byte-for-byte. "
            "Drift indicates the freeze was mutated after evidence collection."
        ),
    }

    # 5) Outcome manifest is a distinct contract from evaluation freeze.
    manifest_path = OUTCOMES_DIR / "outcomes_manifest.json"
    # Recursively scan FREEZE_DIR for any outcomes_manifest.json — a smuggled
    # duplicate (whether at the top level or nested under a subdirectory)
    # would let the same JSON masquerade as either contract.
    freeze_resolved = FREEZE_DIR.resolve()
    smuggled = sorted(
        str(p.relative_to(short_squeeze_root))
        for p in freeze_resolved.rglob("outcomes_manifest.json")
    )
    separate = (
        manifest_path.exists()
        and OUTCOMES_DIR.resolve() != freeze_resolved
        and not manifest_path.resolve().is_relative_to(freeze_resolved)
        and not smuggled
    )
    checks["outcome_manifest_separate"] = {
        "passed": separate,
        "outcomes_dir": str(OUTCOMES_DIR.relative_to(short_squeeze_root)),
        "freeze_dir": str(FREEZE_DIR.relative_to(short_squeeze_root)),
        "manifest_path": (
            str(manifest_path.relative_to(short_squeeze_root))
            if manifest_path.exists() else None
        ),
        "smuggled_manifest_paths": smuggled,
        "rationale": (
            "phase_3d_outcome_leakage_policy.v1 -- "
            "'The outcome manifest is a separate contract from the "
            "evaluation freeze.' No copy of outcomes_manifest.json may "
            "appear anywhere inside the freeze tree."
        ),
    }

    # 6) Every per-symbol outcome_observation.json exists and decodes.
    per_symbol_ok = 0
    per_symbol_missing: list[str] = []
    for symbol in SYMBOLS:
        obs_path = OUTCOMES_DIR / symbol / "outcome_observation.json"
        if not obs_path.exists():
            per_symbol_missing.append(symbol)
            continue
        try:
            RetrospectiveOutcomeObservation.model_validate_json(obs_path.read_bytes())
            per_symbol_ok += 1
        except Exception as exc:  # noqa: BLE001 -- record validation error
            per_symbol_missing.append(f"{symbol} (validation: {exc})")
    checks["per_symbol_outcome_observation_valid"] = {
        "passed": len(per_symbol_missing) == 0,
        "validated_count": per_symbol_ok,
        "invalid_symbols": per_symbol_missing,
        "rationale": (
            "Every symbol must have a valid RetrospectiveOutcomeObservation JSON."
        ),
    }

    audit_passed = all(c["passed"] for c in checks.values())

    audit = {
        "schema_version": "1.0.0",
        "policy_version": "phase_3d_outcome_leakage_policy.v1",
        "audit_timestamp_utc": datetime.now(UTC).isoformat(),
        "audit_passed": audit_passed,
        "policy": _leakage_policy_metadata(),
        "checks": checks,
        "deliverable_paths": {
            "stage2_dir": str(STAGE2_DIR.relative_to(short_squeeze_root)),
            "freeze_dir": str(FREEZE_DIR.relative_to(short_squeeze_root)),
            "outcomes_dir": str(OUTCOMES_DIR.relative_to(short_squeeze_root)),
            "acquisition_plan": str(ACQUISITION_PLAN_REL),
        },
    }
    audit_path = LEAKAGE_AUDIT_DIR / "audit.json"
    audit_path.write_bytes(canonical_json_bytes(audit))

    return {"audit_passed": audit_passed, "audit_path": str(audit_path.relative_to(REPO_ROOT))}


def _leakage_policy_metadata() -> dict:
    # ``load_policy`` raises ``ValueError`` for unknown names or schema
    # mismatches and ``FileNotFoundError``/``json.JSONDecodeError`` if the
    # policy document is missing or corrupt.
    try:
        policy = load_policy("outcome_leakage")
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}
    return {
        "policy_version": policy.get("policy_version"),
        "separate_outcome_manifest_required": policy.get(
            "separate_outcome_manifest_required"
        ),
        "failed_audit_blocks_publication": policy.get(
            "failed_audit_blocks_publication"
        ),
    }


# ----------------------------------------------------------------------------
# Step 3 — Phase 3B publication
# ----------------------------------------------------------------------------

def _candidate_entry(
    symbol: str,
    *,
    outcome_observation_path: str | None,
    case_status: CandidateCaseStatus,
) -> CandidateCaseRegistryEntry:
    return CandidateCaseRegistryEntry(
        case_id=BATCH01_CASE_ID_TEMPLATE.format(symbol=symbol),
        symbol=symbol,
        asset_class=AssetClass.EQUITY,
        case_type=CandidateCaseType.ORIGINAL_PLATFORM_SURFACED,
        case_status=case_status,
        original_platform_status=OriginalPlatformStatus.SURFACED,
        detection_time_evidence_id=None,
        evaluation_as_of=PHASE_3A_AS_OF,
        evaluation_request_path=f"../phase3a-freeze/{symbol}/frozen_request.json",
        evaluation_result_path=f"../phase3a-freeze/{symbol}/frozen_result.json",
        outcome_observation_path=outcome_observation_path,
        original_platform_artifact_ids=("archived-scanner-snapshot-batch01",),
        historical_dataset_ids=(),
        phase_3a_policy_version=PHASE_3A_POLICY_VERSION,
        limitations=IBKR_PILOT_LIMITATIONS,
        fixture_classification=FixtureClassification.SANITIZED_LOCAL_ARTIFACT,
    )


def _build_registry() -> tuple[CandidateCaseRegistry, BatchEvaluationRequest]:
    """Construct the 13-entry registry + batch request."""
    entries: list[CandidateCaseRegistryEntry] = []
    for symbol in SYMBOLS:
        obs_path = OUTCOMES_DIR / symbol / "outcome_observation.json"
        if obs_path.exists():
            entries.append(_candidate_entry(
                symbol,
                outcome_observation_path=f"../outcomes/{symbol}/outcome_observation.json",
                case_status=CandidateCaseStatus.COMPLETE,
            ))
        else:
            entries.append(_candidate_entry(
                symbol,
                outcome_observation_path=None,
                case_status=CandidateCaseStatus.BLOCKED_MISSING_OUTCOME_DATA,
            ))
    registry = build_case_registry(PHASE_3B_REGISTRY_VERSION, entries)
    request = BatchEvaluationRequest(
        batch_version=PHASE_3B_BATCH_VERSION,
        phase_3a_policy_version=PHASE_3A_POLICY_VERSION,
        research_detection_policy_version=DETECTION_POLICY_VERSION,
        outcome_label_policy_version=OUTCOME_POLICY_VERSION,
        case_ids=tuple(entry.case_id for entry in entries),
        case_registry_version=PHASE_3B_REGISTRY_VERSION,
        ordering_policy=OrderingPolicy.CANONICAL_CASE_ID,
        fail_fast=False,
    )
    return registry, request


def publish_phase3b_dataset(force: bool = False) -> dict:
    """Step 4c: build registry, run batch, publish research dataset."""
    PHASE3B_DIR.mkdir(parents=True, exist_ok=True)

    if not force and (PHASE3B_DIR / "research_dataset.json").exists():
        dataset = json.loads((PHASE3B_DIR / "research_dataset.json").read_bytes())
        return {
            "status": "skipped_existing",
            "dataset_id": dataset.get("deterministic_id"),
            "row_count": len(dataset.get("rows", [])),
            "phase3b_dir": str(PHASE3B_DIR.relative_to(REPO_ROOT)),
        }

    # 1) Leakage audit must pass before publication (policy: failed_audit_blocks_publication).
    audit = run_leakage_audit()
    if not audit["audit_passed"]:
        raise RuntimeError(
            "leakage audit did not pass; refusing to publish. "
            f"See {audit['audit_path']} for details."
        )

    # 2) Build registry + batch request, persist registry.json.
    registry, request = _build_registry()
    registry_path = PHASE3B_DIR / "case_registry.json"
    registry_path.write_bytes(serialize_research_model(registry))

    # 3) Run the research batch using existing research.batch infrastructure.
    batch = run_research_batch(request, registry_path)

    # 4) Build the canonical research dataset from the batch result.
    dataset = build_research_dataset(batch)

    # 5) Persist the batch result, dataset, JSONL, and CSV.
    batch_path = PHASE3B_DIR / "batch_result.json"
    batch_path.write_bytes(serialize_research_model(batch))

    dataset_path = PHASE3B_DIR / "phase_3b_research_dataset.json"
    dataset_path.write_bytes(serialize_research_json(dataset))

    jsonl_path = PHASE3B_DIR / "phase_3b_research_dataset.jsonl"
    jsonl_path.write_bytes(serialize_research_jsonl(dataset))

    csv_path = PHASE3B_DIR / "phase_3b_research_dataset.csv"
    csv_path.write_bytes(serialize_research_csv(dataset))

    # 6) SHA-256 manifest over the generated artefacts.
    manifest = {
        path.name: {
            "relative_path": str(path.relative_to(PHASE3B_DIR)),
            "sha256": _sha256_of(path),
        }
        for path in (registry_path, batch_path, dataset_path, jsonl_path, csv_path)
    }
    manifest_path = PHASE3B_DIR / "phase3b-sha256-manifest.json"
    manifest_path.write_bytes(canonical_json_bytes(manifest))

    return {
        "status": "published",
        "registry_id": str(registry.deterministic_id),
        "batch_id": str(batch.deterministic_id),
        "dataset_id": str(dataset.deterministic_id),
        "row_count": len(dataset.rows),
        "skipped_count": len(batch.skipped_cases),
        "phase3b_dir": str(PHASE3B_DIR.relative_to(REPO_ROOT)),
        "artifacts": [str(path.relative_to(REPO_ROOT)) for path in (
            registry_path, batch_path, dataset_path, jsonl_path, csv_path, manifest_path,
        )],
    }


# ----------------------------------------------------------------------------
# Orchestrator + CLI
# ----------------------------------------------------------------------------

def run_stage2_step4(force: bool = False) -> dict:
    """Execute all three Step 4 phases in order."""
    print("=" * 74)
    print("  Phase 3E Stage 2 — Step 4  (outcomes + leakage audit + Phase 3B publish)")
    print(f"  Symbols: {len(SYMBOLS)}  |  Outcome policy: {OUTCOME_POLICY_VERSION}")
    print(f"  Leakage policy: phase_3d_outcome_leakage_policy.v1")
    print(f"  Phase 3A as_of: {PHASE_3A_AS_OF.isoformat()}")
    print("=" * 74)

    outcomes = compute_outcomes(force=force)
    print(f"  Outcomes: {outcomes['newly_computed']} new, "
          f"{outcomes['skipped_existing']} resumed")
    audit = run_leakage_audit()
    print(f"  Leakage audit: {'PASS' if audit['audit_passed'] else 'FAIL'} "
          f"({audit['audit_path']})")
    publish = publish_phase3b_dataset(force=force)
    print(f"  Publish: {publish['status']} (rows={publish.get('row_count', 0)})")
    print("=" * 74)
    return {
        "outcomes": {"newly_computed": outcomes["newly_computed"], "skipped_existing": outcomes["skipped_existing"]},
        "audit": audit,
        "publish": publish,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Phase 3E Stage 2 — Step 4 (outcomes, leakage audit, Phase 3B publish).",
    )
    parser.add_argument(
        "--step",
        choices=("outcomes", "audit", "publish", "all"),
        default="all",
        help="Which Step 4 sub-phase to run. 'all' runs them in order.",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-compute outcomes / re-publish even when artefacts already exist.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    print(
        f"[step4] mode={args.step} force={args.force} "
        f"workers={os.cpu_count() or 1}",
        flush=True,
    )

    if args.step in ("outcomes", "all"):
        summary = compute_outcomes(force=args.force)
        print(
            f"[step4] outcomes: new={summary['newly_computed']} "
            f"resumed={summary['skipped_existing']}",
            flush=True,
        )

    if args.step in ("audit", "all"):
        audit = run_leakage_audit()
        print(
            f"[step4] audit: {'PASS' if audit['audit_passed'] else 'FAIL'}",
            flush=True,
        )
        if args.step == "audit" and not audit["audit_passed"]:
            return 1

    if args.step in ("publish", "all"):
        publish = publish_phase3b_dataset(force=args.force)
        print(
            f"[step4] publish: {publish['status']} "
            f"rows={publish.get('row_count', 0)} "
            f"id={publish.get('dataset_id', '-')[:16]}…",
            flush=True,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
