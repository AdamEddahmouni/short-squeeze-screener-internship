# Historical Market-Bar Submission Kit

This kit helps you prepare a lawful, local historical market-bar export so it
conforms to the offline intake contracts, and validate it with an **offline
preflight** before any later work. It performs preparation and validation only.

It does **not** download data, call provider APIs, log into accounts, handle
credentials, associate your data with any research case, compute any outcome, or
begin any later phase. You obtain the export yourself, lawfully; the kit records
your entitlement assertion and checks the local files.

## What preflight can and cannot tell you

A `READY_FOR_FUTURE_ASSOCIATION` result means only that your local bundle passed
the current intake and normalization checks. It does **not** mean the data is
accurate, that your license is legally sufficient, that a particular historical
case is covered, that an outcome window is complete, or that any later analysis or
publication may run.

## Read these in order

1. `QUICKSTART.md` — the end-to-end path in a few steps.
2. `PROVIDER-AND-ENTITLEMENT-GUIDE.md` — obtaining a file lawfully and declaring it.
3. `FOLDER-PLACEMENT-GUIDE.md` — where the raw file and declarations go.
4. `SHA256-AND-BYTE-LENGTH-GUIDE.md` — recording exact bytes.
5. `TIMEZONE-INTERVAL-SESSION-GUIDE.md` — declaring time semantics.
6. `ADJUSTMENT-SEMANTICS-GUIDE.md` — declaring price/volume adjustment.
7. `PREFLIGHT-GUIDE.md` — running preflight and reading the report.
8. `TROUBLESHOOTING.md` — what each reason code means and how to respond.
9. `EXPORT-CHECKLIST.md` and `FINAL-OPERATOR-CHECKLIST.md` — confirm before you finish.

## Contents

- `templates/` — blank, fill-in templates for the manifest, mapping profile, and
  (future-only) case association.
- `examples/synthetic-valid/` — a complete, clearly fictional example that passes
  preflight, small enough to read by hand.
- `examples/synthetic-invalid/` — a deterministic index of failing scenarios with
  the reason codes they produce and how to respond.

Everything in this kit is synthetic. No real market data is included.
