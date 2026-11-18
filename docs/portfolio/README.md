# Frozen-demo visual assets

**Source of truth:** the running application in FROZEN_DEMO, not recreated artwork.

## Deliverables

- assets/scanner.png — real Scanner screen (browser at the local frozen-demo server).
- assets/advanced-research.png — real Advanced Research screen.
- assets/methodology-comparison.png — real Methodology Comparison tab.
- assets/research-summary.png — actual frozen Research Summary view showing available outcome aggregates.
- assets/frozen-demo-walkthrough.webm — short real browser recording of Scanner, Advanced Research, comparison limitations and Research Summary.
- assets/capture-evidence.json — capture metadata and frozen API validation facts.
- architecture.svg — original source-grounded explanatory diagram, **not** a screenshot.
- methodologies.svg — original explanatory methodology comparison, **not** an application screenshot.
- walkthrough.md — accessible, text-based interactive demonstration.

**Frozen-demo limitation:** the Methodology Comparison tab correctly shows zero server-evaluated rows because the sanitized fixtures lack admissible underlying market fields. Do not edit screenshots to invent values. Use Research Summary for the meaningful frozen evidence demonstration.

These PNG and WebM outputs must be created only by the browser automation against a running FROZEN_DEMO server. If they are absent, the capture job has not successfully completed: **do not replace them with stock graphics or mockups**.

## Generate locally

Prerequisites: Python 3.12, Node 22, npm, internet for first-time dependency/browser installation.

1. Install the app from the root README and start it in FROZEN_DEMO on localhost:8787.
2. From the repository root, install Playwright without modifying package metadata:

   ~~~bash
   npm install --no-save --no-package-lock playwright@1.56.1
   npx playwright install chromium
   ~~~

3. Check the authoritative frozen integration surface:

   ~~~bash
   cd short-squeeze-core
   python tools/integration_acceptance.py --mode frozen
   cd ..
   ~~~

4. With the server still running, capture the authentic browser output:

   ~~~bash
   node tools/capture_frozen_demo.mjs
   ~~~

5. Review every screenshot visually before publishing. The JSON evidence is a *capture record*, not a substitute for app validation.

The GitHub Actions workflow also runs the acceptance check, starts the real frozen app, captures these assets, and commits them to the showcase branch when it has permission. It deliberately does not deploy any public server.

## Source and boundaries

- [Current architecture](../../short-squeeze-core/docs/architecture.md)
- [Methodologies](../../short-squeeze-core/docs/METHODOLOGIES.md)
- [Integration API](../../short-squeeze-core/docs/API.md)
- [Data and validation limitations](../../short-squeeze-core/docs/LIMITATIONS.md)

Frozen candidates are sanitized and deterministic. The demo has no live brokerage/market-data connection, no execution, and no evidence of predictive financial performance. Image captions must describe them as *frozen research*.

## GitHub repository About metadata (manual settings)

The GitHub integration used to curate these files cannot update repository About fields. Set them on the repository page using the About section's edit control:

- **Description:** Read-only short-squeeze research screener with evidence-aware classifications, source provenance, methodology comparisons, and a credential-free demo.
- **Website:** leave empty until an accessible maintained public demo is verified (no assumption that a Railway deployment is healthy).
- **Topics:** python, financial-research, quantitative-research, short-interest, market-data, evidence-based, data-quality, research-software, open-source.
- **Social preview:** upload a reviewed 1280 × 640 crop of the *actual Scanner screenshot* or a source-grounded graphic that clearly states FROZEN DEMO / RESEARCH ONLY. Do not present synthetic data as live market results.

A repository file cannot itself change the About description, topics, or GitHub social-preview setting.
