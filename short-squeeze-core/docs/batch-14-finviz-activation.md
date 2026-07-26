# Batch 14 Finviz Activation

Status: **ACTIVE through the official Finviz Elite export endpoint**.

On 2026-07-25 at `23:29:09Z`, a fresh read-only validation returned:

- configured: yes;
- HTTP/export validation: success;
- rows: 1,461;
- columns: 24;
- stale fallback: no;
- credentials, cookies, and authenticated URLs printed or committed: none.

The previously authorized token-refresh tool was audited before use. It is explicit,
local-only, stops for CAPTCHA/MFA, validates the official CSV before atomically changing
the ignored private file, and prints only sanitized status. No refresh was needed for
this verification because the current token remained valid.

Finviz fields keep provider, provider-field, time, freshness, display availability,
research admissibility, selection reason, and conflict state. Short Float is not
substituted for published SI%, and Finviz Relative Volume remains display-only unless
canonical semantics and admissibility are established.
