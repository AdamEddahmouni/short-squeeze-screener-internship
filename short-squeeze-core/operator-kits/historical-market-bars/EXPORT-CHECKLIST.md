# Export Checklist

Before running preflight, confirm the raw export and its declaration:

- [ ] The export was obtained lawfully and you are entitled to use it.
- [ ] The raw file is final and unmodified, placed at `raw/<your-export>.csv`.
- [ ] No credential material appears in any file, name, or value.
- [ ] SHA-256 and byte length are recorded for the exact raw file.
- [ ] `artifact_relative_path` is relative (never absolute).
- [ ] `artifact_format` is CSV and `encoding` is one of: ascii, latin-1, utf-8, utf-8-sig.
- [ ] Provider, product, retrieval time, and export time are declared.
- [ ] Provider symbol, canonical symbol, and venue are explicit.
- [ ] Interval, timezone, timestamp semantics, and session coverage are explicit.
- [ ] Price adjustment, volume adjustment, and corporate-action handling are explicit.
- [ ] Expected coverage start and end are explicit.
- [ ] The mapping profile matches the actual CSV columns.

Then run preflight and review the reason codes against `TROUBLESHOOTING.md`.
