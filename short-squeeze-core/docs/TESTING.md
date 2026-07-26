# Testing

Tests require Python 3.12 and the `test` optional dependency.

```bash
python -m pip install -e ".[test]"
python -m pytest -p no:cacheprovider --basetemp .pytest-run
```

Normal tests are offline and deterministic. They use synthetic providers and must
not call Finviz, NewsAPI, Finnhub, SEC EDGAR, IBKR, or Railway.

Focused release checks:

```bash
python -m pytest tests/app/test_batch15_config.py
python -m pytest tests/app/test_batch15_release_audit.py
python -m pytest tests/app/test_batch15_release_builder.py
python tools/integration_acceptance.py --mode frozen
```

Use a new writable base directory and JUnit path for an authoritative run. Parse
the XML for tests, passed, skipped, failures, errors, and duration.
