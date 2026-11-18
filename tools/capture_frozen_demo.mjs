/**
 * Capture REAL screenshots and a short browser recording from the locally running
 * FROZEN_DEMO server. Never generate mock market rows or synthetic UI captures.
 *
 * Requires: npm install --no-save --no-package-lock playwright@1.56.1
 *           npx playwright install chromium
 * Start first: cd short-squeeze-core && SQUEEZE_APP_MODE=FROZEN_DEMO
 *              python -m apps.research_screener --no-browser
 */
import assert from 'node:assert/strict';
import { mkdir, writeFile, stat } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { chromium } from 'playwright';

const base = (process.env.FROZEN_DEMO_URL || 'http://127.0.0.1:8787').replace(/\/$/, '');
const destination = fileURLToPath(new URL('../docs/portfolio/assets/', import.meta.url));
await mkdir(destination, { recursive: true });

const browser = await chromium.launch({
  ...(process.env.DEMO_CHROME_EXECUTABLE ? { executablePath: process.env.DEMO_CHROME_EXECUTABLE } : {}),
  headless: true,
  args: ['--disable-dev-shm-usage'],
});
let video;
let captureFacts;

try {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1,
    reducedMotion: 'reduce',
    colorScheme: 'dark',
    recordVideo: {
      dir: destination,
      size: { width: 1440, height: 900 },
    },
  });

  const read = async (route) => {
    const response = await context.request.get(base + route, { timeout: 25000 });
    assert.equal(response.status(), 200, route + ' must respond with HTTP 200');
    return response.json();
  };

  const health = await read('/health');
  const frozen = await read('/api/frozen/candidates');
  const methodologies = await read('/api/methodologies');
  const manifest = await read('/api/v1/integration/manifest');

  assert.equal(health.status, 'OK', 'Frozen local server must be healthy');
  assert.equal(frozen.data?.row_count, 13, 'Expected exactly 13 frozen cases');
  assert.deepEqual(
    frozen.data?.outcome_totals,
    { PASS: 97, FAIL: 20, UNKNOWN: 208 },
    'Frozen rule outcome totals must match the versioned fixture',
  );

  const expectedMethodologies = [
    'legacy_prime_setup',
    'peer_reference_methodology',
    'adam_evidence_gated_prime.v1',
  ];
  assert.deepEqual(
    [...(methodologies.data?.methodology_ids || [])].sort(),
    [...expectedMethodologies].sort(),
    'Expected independent methodology identifiers',
  );
  assert.equal(manifest.data?.api_version, '1.0.0');
  assert.equal(manifest.data?.schema_version, 'batch14.integration.v1');
  assert.deepEqual(manifest.data?.prohibited_capabilities, {
    trading: 'UNSUPPORTED',
    orders: 'UNSUPPORTED',
    account_access: 'UNSUPPORTED',
  });

  const page = await context.newPage();
  video = page.video();

  await page.goto(base + '/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForFunction(() => {
    const node = document.querySelector('#scanner-body');
    return !!node && node.querySelectorAll('tr').length > 1
      && !node.innerText.includes('Loading');
  }, { timeout: 30000 });
  assert.match(await page.locator('body').innerText(), /FROZEN/i, 'Scanner must show frozen mode');
  await page.waitForTimeout(900);
  await page.screenshot({ path: resolve(destination, 'scanner.png'), animations: 'disabled' });

  await page.locator('#advanced-link').click();
  await page.waitForURL(/\/advanced$/, { timeout: 30000 });
  await page.waitForFunction(() => {
    const node = document.querySelector('#screener-body');
    return !!node && node.querySelectorAll('tr').length > 1
      && !node.innerText.includes('Loading');
  }, { timeout: 30000 });
  await page.waitForTimeout(800);
  await page.screenshot({ path: resolve(destination, 'advanced-research.png'), animations: 'disabled' });

  await page.locator('#btn-comparison').click();
  await page.locator('#comparison-panel').waitFor({ state: 'visible', timeout: 15000 });
  await page.waitForTimeout(1300);
  await page.screenshot({
    path: resolve(destination, 'methodology-comparison.png'),
    animations: 'disabled',
  });
  await page.waitForTimeout(650);

  captureFacts = {
    source: 'actual local running Short Squeeze Research Screener',
    visualMode: 'FROZEN_DEMO',
    captures: ['scanner.png', 'advanced-research.png', 'methodology-comparison.png', 'frozen-demo-walkthrough.webm'],
    disclaimer: 'Sanitized historical research examples; no live market data, trading or validated forecasting.',
    capturedAtUTC: new Date().toISOString(),
    commit: process.env.GITHUB_SHA || 'local-working-copy',
    data: {
      rowCount: frozen.data.row_count,
      outcomeTotals: frozen.data.outcome_totals,
      methodologyIds: expectedMethodologies,
      apiVersion: manifest.data.api_version,
      schemaVersion: manifest.data.schema_version,
      prohibitedCapabilities: manifest.data.prohibited_capabilities,
    },
  };
  await context.close();
  await video.saveAs(resolve(destination, 'frozen-demo-walkthrough.webm'));
} finally {
  await browser.close();
}

if (!video || !captureFacts) {
  throw new Error('A validated screenshot session did not complete.');
}
const videoFile = resolve(destination, 'frozen-demo-walkthrough.webm');
assert.ok((await stat(videoFile)).size > 1024, 'Recorded walkthrough must not be empty');
await writeFile(
  resolve(destination, 'capture-evidence.json'),
  JSON.stringify(captureFacts, null, 2) + '\n',
  'utf-8',
);
for (const filename of captureFacts.captures) {
  assert.ok((await stat(resolve(destination, filename))).size > 1024, filename + ' must be nonempty');
}
console.log('Captured and validated real frozen-demo images and walkthrough:', captureFacts.data);
