# Batch 14 Provider Enrichment Results

One clean read-only discovery returned 15 scanner candidates. AACG was then added as a
manual current candidate to demonstrate a known Finviz Float row. Refresh All processed
all 16 tracked candidates in 17.336 seconds and returned partial success.

| Provider | Result |
|---|---|
| Finviz Elite | authenticated; 1,469 rows; 7 candidate matches |
| Finviz fields | 7 Float; 7 Short Float; 7 Relative Volume; 7 Short Ratio |
| Finviz news | 100 cached headlines |
| NewsAPI | authenticated; 76 headlines; news present for 16 candidates |
| Finnhub | authenticated; 16 cached prices, selected only where IBKR quote evidence was absent |
| SEC EDGAR | available; 16 symbol results |
| IBKR | scanner and bars active; PGACR returned no completed bars for one window |
| Halt tick | callback type 49 mapped; no halt value returned under this entitlement |
| Sentiment | deferred; not configured and not used |

Scanner matches were LVWR, NDLS, TC, VIVK, WLDS, and YYAI; AACG was the seventh manual
proof. Unmatched candidates remained unmatched without substitution. No provider
conflict was observed. A failed provider cannot erase another provider's last-good data.
