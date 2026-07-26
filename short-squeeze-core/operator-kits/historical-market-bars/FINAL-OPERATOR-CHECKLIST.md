# Final Operator Checklist

Confirm every item before supplying a real bundle. This records declarations
only; it makes no legal determination and computes no outcome.

- [ ] The export was obtained lawfully.
- [ ] I am entitled to use this export under its terms.
- [ ] No credentials are included anywhere in the bundle.
- [ ] The raw file is final and unmodified.
- [ ] SHA-256 and byte length are recorded for the exact raw file.
- [ ] The provider and product/export name are identified.
- [ ] Retrieval time and export time are recorded (distinct from event time).
- [ ] The provider symbol, canonical symbol, and venue are explicit.
- [ ] The bar interval is explicit and supported.
- [ ] The event timezone is explicit (UTC, an explicit offset, or a resolvable zone).
- [ ] Timestamp semantics (START or END) are explicit.
- [ ] Session coverage is explicit.
- [ ] Price adjustment semantics are explicit.
- [ ] Volume adjustment semantics are explicit.
- [ ] Corporate-action handling is explicit.
- [ ] Expected coverage (start and end) is explicit.
- [ ] The mapping profile matches the actual CSV columns.
- [ ] Preflight runs offline.
- [ ] The preflight status is understood, including its disclaimers.
- [ ] No real-case association has occurred.
- [ ] No outcome has been calculated.
- [ ] No Phase 3A or Phase 3B result has been created.
- [ ] No Phase 3E work has begun.

The machine-readable form is `operator-checklist.json` in the batch-04 fixtures.
