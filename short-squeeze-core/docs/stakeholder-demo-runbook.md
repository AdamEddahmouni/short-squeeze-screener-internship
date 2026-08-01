# Stakeholder Demo Runbook

## Launch

```powershell
.\run_screener.ps1
```

Open `http://127.0.0.1:8787/`.

## Five-minute demonstration

1. Show Frozen Research: 13 cases and exactly 97 PASS / 20 FAIL / 208 UNKNOWN.
2. Switch to Current and run discovery; current candidates never enter the registry.
3. Click **Refresh All Available Evidence**.
4. Open AACG, LVWR, NDLS, TC, VIVK, WLDS, or YYAI.
5. Show `Shares Float`, provider `Finviz Elite`, exact field, times, and admissibility.
6. Show Short Float, Relative Volume, and Short Ratio as display-only.
7. Show capabilities: Finviz export, NewsAPI, Finnhub fallback, SEC, and IBKR. Halt is
   unavailable unless callback tick type 49 is actually returned.
8. Show coverage 11/25, up from 9/25: `FLOAT_MAXIMUM` and
   `PROVIDER_SCOPE_EXPLICIT` are newly evaluable.
9. Export Current JSON/CSV and note the zero-match credential scan.

All current detections remain UNEVALUABLE. Missing data never becomes zero. No current
data fills frozen gaps, no forward outcome is read, and no order/account request exists.

**Phase 3E was not started in Batch 14 and remains unstarted.**

After the meeting, do exactly one next task: obtain written authorization for a
separately scoped Phase 3E design batch.
