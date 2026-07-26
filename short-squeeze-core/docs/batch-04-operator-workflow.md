# Batch 04 — Operator Workflow

This mirrors the operator kit's `QUICKSTART.md` in the repository docs so the
end-to-end path is discoverable from either place. The authoritative, always-current
copy is generated into `operator-kits/historical-market-bars/`.

## The ten steps, and where each belongs

1. **Obtain a file lawfully** — you, outside this software. The kit never fetches.
2. **Place the file locally** — `raw/<your-export>.csv` under a bundle root.
3. **Declare provenance and semantics** — fill in the manifest template.
4. **Validate raw bytes** — preflight verifies SHA-256 and byte length.
5. **Validate the manifest** — preflight loads and validates it.
6. **Validate the mapping profile** — preflight loads and validates it.
7. **Parse and normalize bars** — preflight normalizes supported CSV bars.
8. **Review diagnostics** — reason codes and row diagnostics.
9. **Determine readiness** — the preflight status.
10. **Future case association** — *not in this batch*.
11. **Future outcome capture** — *not in this batch*.

Batch 04 performs steps 2–8 and produces a readiness status for step 9. It never
performs steps 10–11.

## Commands

```
squeeze-core historical-bar-hash --file raw/your-export.csv

squeeze-core historical-bar-preflight \
    --root <bundle-root> \
    --manifest <bundle-root>/manifest.json \
    --profile <bundle-root>/profile.json \
    --output <bundle-root>/preflight-report.json

squeeze-core historical-bar-preflight-report \
    --root <bundle-root> \
    --manifest <bundle-root>/manifest.json \
    --profile <bundle-root>/profile.json \
    --output <bundle-root>/preflight-report.json
```

`historical-bar-preflight` returns exit 0 when ready and 1 otherwise, printing the
report to stdout (ready) or stderr (not ready). `historical-bar-preflight-report`
writes the canonical report bytes for archiving.

## Reading the result

- `READY_FOR_FUTURE_ASSOCIATION` — passed the current checks, with the disclaimers
  in the preflight contract.
- `NOT_READY_QUARANTINED` — review diagnostics before relying on the bundle.
- `NOT_READY_REJECTED` — resolve the reason codes using `TROUBLESHOOTING.md`; a
  manifest or mapping correction is always distinct from changing the raw file,
  whose bytes are never rewritten.

## Before supplying a real bundle

Work through `EXPORT-CHECKLIST.md` and `FINAL-OPERATOR-CHECKLIST.md`. Supply only
exports you are entitled to use. Never commit a real licensed export unless you have
explicitly authorized that exact file; the private intake root `intake/local-bars/`
is git-ignored for this reason.
