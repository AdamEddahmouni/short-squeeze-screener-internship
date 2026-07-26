"""Batch 01 discovery-collection utility (NOT part of the deterministic runtime).

This one-off importer reads the archived original-platform scanner export
``screener_snapshot.json`` from the read-only forensic evidence and emits a
sanitized, derived discovery-rows document that the deterministic Phase 3D
curation module (:mod:`squeeze_core.acquisition.batch01`) consumes offline.

Separation rationale (handoff sections 13 and 31): collection code may read
local archived artifacts, but it must stay out of ``squeeze_core`` so the
deterministic curation/regeneration path and the test suite never depend on it
or on the archived evidence being present.

What is preserved vs. dropped
-----------------------------
The raw scanner row carries both *detection-time factual* fields and the
platform's *derived predictions/opinions*. The sanitized rows retain only the
factual detection-time evidence plus provenance, and deliberately DROP the
platform predictions so no score, rank, prime/subprime tier, or forward target
leaks into the new deterministic outputs (handoff section 31):

  dropped: setup_tier, squeeze_score, squeeze_score_breakdown, corroboration_score,
           corroborated_by, squeeze_confirmed, target_percent, stop_loss_percent,
           sentiment_label, sentiment_confidence

The raw artifact itself is never copied into the repository; only its SHA-256
and byte length are recorded, because it embeds provider-derived borrow data
(IB / Schwab / yfinance) that is retained locally but not redistributed.

Usage (run once, from the repository root)::

    python scripts/acquisition/import_batch01_discovery.py \
        --source "<abs path>/app/ScreenerProject/data/screener_snapshot.json" \
        --output intake/batches/phase-3d-historical-source-collection-01/normalized/batch01_discovery_rows.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


RETAINED_DETECTION_FIELDS = (
    "price",
    "float_shares",
    "float_as_of",
    "float_source",
    "rel_volume",
    "change_percent",
    "short_float_percent",
    "short_interest_as_of",
    "short_interest_source",
    "shares_short",
    "days_to_cover",
    "ib_borrow_fee_rate",
    "ib_borrow_rebate_rate",
    "ib_borrow_rate_as_of",
    "ib_shortable_shares",
    "ib_shortable_shares_as_of",
    "schwab_htb_rate",
    "schwab_htb_quantity",
    "schwab_is_hard_to_borrow",
    "schwab_htb_as_of",
    "ttm_squeeze_on",
    "ttm_squeeze_momentum",
    "ttm_squeeze_fired",
    "quality_flags",
    "source",
)
DROPPED_PREDICTION_FIELDS = (
    "corroborated_by",
    "corroboration_score",
    "sentiment_confidence",
    "sentiment_label",
    "setup_tier",
    "squeeze_confirmed",
    "squeeze_score",
    "squeeze_score_breakdown",
    "stop_loss_percent",
    "target_percent",
)
# Detection-time domains whose absence (null) we flag per case so the
# deterministic curation can record honest missingness.
MISSING_DOMAIN_FIELDS = {
    "SHORT_FLOAT_PERCENT": "short_float_percent",
    "DAYS_TO_COVER": "days_to_cover",
    "IB_BORROW_FEE_RATE": "ib_borrow_fee_rate",
    "IB_SHORTABLE_SHARES": "ib_shortable_shares",
    "SCHWAB_HTB_QUANTITY": "schwab_htb_quantity",
}


def sanitize(raw_bytes: bytes) -> dict:
    rows = json.loads(raw_bytes)
    if not isinstance(rows, list) or not rows:
        raise ValueError("scanner snapshot must be a non-empty list of rows")
    timestamps = sorted({row["timestamp"] for row in rows})
    if len(timestamps) != 1:
        raise ValueError(f"expected a single scan timestamp, found: {timestamps}")
    sanitized_rows = []
    for index, row in enumerate(rows, start=1):
        detection = {
            field: row.get(field) for field in RETAINED_DETECTION_FIELDS
        }
        missing = sorted(
            domain
            for domain, field in MISSING_DOMAIN_FIELDS.items()
            if row.get(field) is None
        )
        sanitized_rows.append({
            "ticker": row["ticker"].strip().upper(),
            "observed_at": row["timestamp"],
            "original_order": index,
            "detection_time_evidence": detection,
            "missing_detection_domains": missing,
        })
    sanitized_rows.sort(key=lambda item: item["original_order"])
    return {
        "schema_version": "1.0.0",
        "document": "phase_3d_batch_01_sanitized_discovery_rows",
        "raw_source": {
            "source_class": "ARCHIVED_MARKET_SCANNER",
            "artifact_name": "screener_snapshot.json",
            "archived_relative_path": (
                "archived-project-code/adams-short-squeeze-code-archived/"
                "app/ScreenerProject/data/screener_snapshot.json"
            ),
            "sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "byte_length": len(raw_bytes),
            "capture_timestamp": timestamps[0],
            "classification": "RESTRICTED_LOCAL_ARTIFACT",
            "notes": (
                "Raw provider-embedded scanner export retained read-only in the "
                "local forensic archive; referenced by hash, not copied."
            ),
        },
        "transformation": {
            "retained_detection_fields": list(RETAINED_DETECTION_FIELDS),
            "dropped_prediction_fields": list(DROPPED_PREDICTION_FIELDS),
            "selection": "SOURCE_ORDER_ONLY_SCORE_BLIND",
        },
        "rows": sanitized_rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    document = sanitize(args.source.read_bytes())
    rendered = json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Write LF bytes explicitly so the committed artifact hash is identical on every
    # platform (the repo normalizes text to LF; a CRLF working copy would diverge).
    args.output.write_bytes(rendered.encode("utf-8"))
    print(
        f"wrote {len(document['rows'])} sanitized discovery rows to {args.output} "
        f"(raw sha256 {document['raw_source']['sha256']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
