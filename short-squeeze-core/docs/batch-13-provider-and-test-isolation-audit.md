# Batch 13 Provider and Test Isolation Audit

The takeover WIP loaded `.private/providers.env` implicitly, used global live clients,
called NewsAPI and SEC while rendering rows, and weakened assertions to accept either
live or offline results.

Corrections:

- Private config loads only from an explicitly supplied path.
- A session owns an injected `ProviderBundle`; its default is fully offline.
- External calls occur only during explicit refresh.
- Tests use controlled fakes and strict `NOT CONFIGURED` assertions.
- The pytest network guard permits loopback but records and fails any external DNS,
  connect, or connect-ex attempt, including attempts swallowed by adapters.
- Provider errors retain last-good caches and redact configured secrets.

Semantic boundaries:

- Short Float is not Published Short Interest.
- Short Ratio is not canonical Days to Cover.
- Shares Outstanding is not Float.
- Finviz Relative Volume is displayable but not fed to Phase 3A.
- Headlines do not produce a catalyst PASS.

Normal automated tests load no private configuration and make zero external calls.
