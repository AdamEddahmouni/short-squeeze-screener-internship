"""Phase 3E Stage 2 - Step 6 (Phase 3C descriptive analysis on the IBKR pilot).

Invokes the existing ``analyze-research-dataset`` and ``render-research-analysis-report``
Phase 3C CLIs against the published 13-symbol IBKR pilot registry + research dataset,
producing the five standard cohort analyses and their deterministic Markdown reports.

Output layout (all under ``build/acquisition/stage2/phase_3c/``)::

    analyses/<cohort>_analysis.json
    reports/<cohort>_report.md

The five standard cohorts mirror ``phase-3c-design.md``:

1. ``historical_case_boundary``      (CASE_BOUNDARY, all_case_boundaries.v1)
2. ``historical_unique_symbol``       (UNIQUE_SYMBOL_POLICY_SELECTED_BOUNDARY,
                                       earliest_detection_boundary_per_symbol.v1)
3. ``synthetic``                      (synthetic-only fixtures — produced for software
                                       coverage only; never enters empirical rates)
4. ``all_registered``                 (registry composition + data-quality counts,
                                       all 13 IBKR pilot entries)
5. ``partial_blocked``                (registry partial/blocked/conflicting cases)

Note: the ``synthetic`` cohort is meant for software-coverage fixtures and
expects rows tagged as synthetic in the input dataset. On a historical-only
cohort (such as the IBKR pilot, where ``fixture_classification`` is
``SANITIZED_LOCAL_ARTIFACT`` for every row) the analyzer emits an empty
cohort with a structured empty-cohort diagnostic rather than a failure.
This is a valid Phase 3C descriptive state per the design; the wrapper
captures both the analysis artifact and the report so the operator can
inspect them.

Usage (from ``short-squeeze-core/``)::

    # Default (use the published IBKR pilot artefacts)
    python scripts/acquisition/run_stage2_phase_3c_analysis.py

    # Force a clean re-run
    python scripts/acquisition/run_stage2_phase_3c_analysis.py --force

    # Custom dataset + registry paths
    python scripts/acquisition/run_stage2_phase_3c_analysis.py \\
        --dataset path/to/research_dataset.json \\
        --case-registry path/to/case_registry.json \\
        --output-dir path/to/output/
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from squeeze_core.__main__ import main as cli_main

REPO_ROOT = Path(__file__).resolve().parents[2]
STAGE2_DIR: Path = REPO_ROOT / "build" / "acquisition" / "stage2"
DEFAULT_DATASET: Path = STAGE2_DIR / "phase3b" / "phase_3b_research_dataset.json"
DEFAULT_REGISTRY: Path = STAGE2_DIR / "phase3b" / "case_registry.json"
DEFAULT_OUTPUT_DIR: Path = STAGE2_DIR / "phase_3c"

INTERVAL_POLICY = "phase_3c_interval_policy.v1"
STATISTICS_POLICY = "phase_3c_descriptive_statistics_policy.v1"
SAMPLE_SIZE_POLICY = "phase_3c_sample_size_policy.v1"
CONFIDENCE_LEVEL = "0.95"
DETERMINISTIC_BOUNDARY_POLICY = "earliest_detection_boundary_per_symbol.v1"


@dataclass(frozen=True)
class CohortSpec:
    """One of the five standard Phase 3C cohorts, with its CLI argument block.

    ``cohort``, ``analysis_unit``, and ``boundary_policy`` are passed verbatim
    to ``analyze-research-dataset``. The ``boundary_policy`` is only meaningful
    for cohorts that retain one concrete Phase 3B row per symbol; for cohorts
    that operate at registry level (``all_registered``, ``partial_blocked``,
    ``synthetic``) the boundary policy is irrelevant and ignored by the CLI.
    """

    cohort: str
    analysis_unit: str
    boundary_policy: str
    slug: str

    def analysis_args(self, dataset: Path, registry: Path, output: Path) -> Sequence[str]:
        return (
            "analyze-research-dataset",
            "--dataset", str(dataset),
            "--case-registry", str(registry),
            "--cohort", self.cohort,
            "--analysis-unit", self.analysis_unit,
            "--boundary-policy", self.boundary_policy,
            "--statistics-policy", STATISTICS_POLICY,
            "--interval-policy", INTERVAL_POLICY,
            "--confidence-level", CONFIDENCE_LEVEL,
            "--sample-size-policy", SAMPLE_SIZE_POLICY,
            "--output", str(output),
        )

    def render_args(self, analysis: Path, output: Path) -> Sequence[str]:
        return (
            "render-research-analysis-report",
            "--analysis", str(analysis),
            "--format", "markdown",
            "--output", str(output),
        )


STANDARD_COHORTS: tuple[CohortSpec, ...] = (
    CohortSpec(
        cohort="historical-complete",
        analysis_unit="case-boundary",
        boundary_policy="all_case_boundaries.v1",
        slug="historical_case_boundary",
    ),
    CohortSpec(
        cohort="historical-complete",
        analysis_unit="unique-symbol-policy-selected-boundary",
        boundary_policy=DETERMINISTIC_BOUNDARY_POLICY,
        slug="historical_unique_symbol",
    ),
    CohortSpec(
        cohort="synthetic",
        analysis_unit="case-boundary",
        boundary_policy="all_case_boundaries.v1",
        slug="synthetic",
    ),
    CohortSpec(
        cohort="all-registered",
        analysis_unit="case-boundary",
        boundary_policy="all_case_boundaries.v1",
        slug="all_registered",
    ),
    CohortSpec(
        cohort="partial-blocked",
        analysis_unit="case-boundary",
        boundary_policy="all_case_boundaries.v1",
        slug="partial_blocked",
    ),
)


def _run_cli(args: Sequence[str]) -> int:
    """Invoke the in-process ``squeeze_core.__main__:main`` entrypoint.

    ``args`` is a tuple of CLI tokens (matching the canonical Phase 3C CLI).

    The wrapper catches both ``Exception`` and the ``SystemExit`` that
    canonical CLIs use to signal fatal config errors. ``SystemExit`` is a
    ``BaseException`` subclass (not ``Exception``), so a plain
    ``except Exception`` would not intercept it and a config error would
    still terminate the cohort loop. Both branches synthesise an exit
    code so the per-cohort iteration continues and the summary table
    still materialises.
    """
    try:
        return cli_main(tuple(args))
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 2
        print(f"[step6] CLI SystemExit: code={exc.code!r}", flush=True)
        return code
    except Exception as exc:  # noqa: BLE001 — surface, never abort the cohort loop
        print(
            f"[step6] CLI exception: {type(exc).__name__}: {exc}",
            flush=True,
        )
        return 2


def _rel(path: Path) -> str:
    """Render ``path`` relative to ``REPO_ROOT`` when possible, else absolute.

    Defensive: ``--output-dir`` may legitimately point outside the repo
    (e.g. ``/tmp/...``), and emitting ``str(path.relative_to(REPO_ROOT))``
    would raise ``ValueError`` in that case.
    """
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _process_cohort(
    spec: CohortSpec,
    dataset: Path,
    registry: Path,
    analyses_dir: Path,
    reports_dir: Path,
    *,
    force: bool,
) -> tuple[str | None, str | None, int]:
    """Run one cohort end-to-end. Returns (analysis_rel, report_rel, exit_code).

    Exits the cohort early (``exit_code=0``) if both an analysis.json and a
    report.md already exist and the analysis parses as valid JSON, unless
    ``force`` is set.
    """
    analysis_path = analyses_dir / f"{spec.slug}_analysis.json"
    report_path = reports_dir / f"{spec.slug}_report.md"

    if not force and analysis_path.exists() and report_path.exists():
        try:
            json.loads(analysis_path.read_bytes())
        except (ValueError, json.JSONDecodeError):
            pass
        else:
            print(
                f"[step6] {spec.slug}: skipped (existing analysis + report)",
                flush=True,
            )
            return _rel(analysis_path), _rel(report_path), 0

    rc_analyze = _run_cli(
        spec.analysis_args(dataset, registry, analysis_path)
    )
    report_rel: str | None = _rel(report_path) if rc_analyze == 0 else None
    if rc_analyze != 0:
        print(
            f"[step6] {spec.slug}: analyzer exit={rc_analyze}",
            flush=True,
        )
        return None, report_rel, rc_analyze

    rc_render = _run_cli(spec.render_args(analysis_path, report_path))
    if rc_render != 0:
        print(
            f"[step6] {spec.slug}: report renderer exit={rc_render}",
            flush=True,
        )

    print(
        f"[step6] {spec.slug}: published analysis + report",
        flush=True,
    )
    return _rel(analysis_path), _rel(report_path), rc_render


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 3E Stage 2 Step 6 — Phase 3C descriptive analysis on the "
            "13-symbol IBKR pilot dataset, all five standard cohorts."
        ),
    )
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="Path to the Phase 3B research dataset JSON.",
    )
    parser.add_argument(
        "--case-registry", type=Path, default=DEFAULT_REGISTRY,
        help="Path to the Phase 3B case registry JSON.",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR,
        help="Destination directory for analyses + Markdown reports.",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-run all five cohorts even if outputs already exist.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    dataset: Path = args.dataset
    registry: Path = args.case_registry
    output_dir: Path = args.output_dir
    analyses_dir = output_dir / "analyses"
    reports_dir = output_dir / "reports"

    print("=" * 78)
    print("  Phase 3E Stage 2 - Step 6 (Phase 3C descriptive analysis)")
    print(f"  Dataset:    {dataset}")
    print(f"  Registry:   {registry}")
    print(f"  Output dir: {output_dir}")
    print("=" * 78)

    if not dataset.exists():
        print(f"[step6] MISSING dataset json: {dataset}", flush=True)
        return 2
    if not registry.exists():
        print(f"[step6] MISSING case registry json: {registry}", flush=True)
        return 2

    analyses_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary: dict[str, dict[str, str | int | None]] = {
        spec.slug: {"analysis": None, "report": None, "exit_code": None}
        for spec in STANDARD_COHORTS
    }
    coverage_notes: dict[str, str] = {}

    for spec in STANDARD_COHORTS:
        analysis_rel, report_rel, exit_code = _process_cohort(
            spec, dataset, registry, analyses_dir, reports_dir, force=args.force,
        )
        summary[spec.slug] = {
            "analysis": analysis_rel,
            "report": report_rel,
            "exit_code": exit_code,
        }
        # Emit an operational note for cohorts that load a JSON analysis.
        # The note surfaces empirical-data coverage (e.g. how many symbols
        # the historical-complete cohort retained vs. excluded) so the
        # 1/13 IBKR pilot outcome-coverage finding is visible in operator
        # stdout and not hidden inside the Markdown report's limitations.
        #
        # ``REPO_ROOT / analysis_rel`` resolves correctly even when
        # ``analysis_rel`` is already absolute — pathlib's ``/`` operator
        # drops the LHS whenever the RHS is absolute, so the conditional
        # is unnecessary here.
        if exit_code == 0 and analysis_rel:
            try:
                payload = json.loads((REPO_ROOT / analysis_rel).read_bytes())
            except (OSError, json.JSONDecodeError) as exc:
                # Coverage notes are operator-facing; surface the failure so a
                # rare corrupt analysis file is visible in CI logs rather
                # than silently producing a coverage-less cohort summary.
                print(
                    f"[step6] coverage note unavailable for {spec.slug}: "
                    f"{type(exc).__name__}: {exc}",
                    flush=True,
                )
            else:
                membership = payload.get("cohort_membership") or {}
                included = len(membership.get("included_case_ids") or [])
                excluded = len(membership.get("exclusions") or [])
                if included or excluded:
                    coverage_notes[spec.slug] = (
                        f"included={included}, excluded={excluded}"
                    )

    print("=" * 78)
    print("  Phase 3C cohort summary")
    print("=" * 78)
    for slug, info in summary.items():
        rc = info["exit_code"]
        status = "OK" if rc == 0 else f"FAIL ({rc})"
        note = f"  ({coverage_notes[slug]})" if slug in coverage_notes else ""
        print(f"  {slug:32s} {status}{note}")
    failed = [slug for slug, info in summary.items() if info["exit_code"] != 0]
    print("=" * 78)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
