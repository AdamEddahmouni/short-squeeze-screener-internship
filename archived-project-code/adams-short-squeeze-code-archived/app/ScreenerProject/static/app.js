const REFRESH_INTERVAL_MS = 15000;

const tableBody = document.getElementById("screener-body");
const rowCountEl = document.getElementById("row-count");
const statsStripEl = document.getElementById("stats-strip");
const statusBanner = document.getElementById("status-banner");
const statusText = document.getElementById("status-text");
const detailTemplate = document.getElementById("detail-row-template");
const newsList = document.getElementById("news-list");
const newsCountEl = document.getElementById("news-count");
const newsFilterInput = document.getElementById("news-ticker-filter");
const chartForm = document.getElementById("chart-form");
const chartTickerInput = document.getElementById("chart-ticker-input");
const chartContainer = document.getElementById("chart-container");
const chartRangeEl = document.getElementById("chart-range");
const trackRecordContainer = document.getElementById("track-record-container");
const trackRecordCountEl = document.getElementById("track-record-count");
const corroborationTrackRecordContainer = document.getElementById("corroboration-track-record-container");
const corroborationTrackRecordCountEl = document.getElementById("corroboration-track-record-count");

let lastRows = [];
let sortKey = "squeeze_score";
let sortDir = "desc";
let expandedTicker = null;
let lastHeadlines = [];

// ticker -> [{timestamp, squeeze_score}, ...], refetched every refresh() cycle for whichever
// tickers are currently on the board - re-used by the Trend column's sparkline (below) so a
// second network round-trip isn't needed once a row is already rendered.
const scoreHistoryCache = new Map();

// Fields already shown as their own primary column - everything else in the schema-v1 payload
// goes into the expandable detail row instead of a 29th flat column.
const PRIMARY_FIELDS = new Set([
  "squeeze_score", "ticker", "setup_tier", "price", "change_percent",
  "short_float_percent", "days_to_cover", "ib_borrow_fee_rate", "ttm_squeeze_on",
  "ttm_squeeze_momentum", "ttm_squeeze_fired", "squeeze_confirmed", "sentiment_label",
  "sentiment_confidence", "schema_version",
]);

const DETAIL_LABELS = {
  float_shares: "Float (shares)",
  rel_volume: "Rel. Volume",
  target_percent: "Target %",
  stop_loss_percent: "Stop Loss %",
  shares_short: "Shares Short",
  short_interest_as_of: "Short Interest As Of",
  short_interest_source: "Short Interest Source",
  float_as_of: "Float As Of",
  float_source: "Float Source",
  ib_shortable_shares: "IB Shortable Shares",
  ib_shortable_shares_as_of: "IB Shortable As Of",
  schwab_htb_quantity: "Schwab HTB Qty",
  schwab_htb_rate: "Schwab HTB Rate",
  schwab_is_hard_to_borrow: "Schwab Hard-to-Borrow",
  schwab_htb_as_of: "Schwab HTB As Of",
  ib_borrow_rebate_rate: "IB Borrow Rebate Rate",
  ib_borrow_rate_as_of: "IB Borrow Rate As Of",
  corroboration_score: "Corroboration Score",
  corroborated_by: "Corroborated By",
  quality_flags: "Quality Flags",
  source: "Source",
  timestamp: "Timestamp",
};

// squeeze_score_breakdown is a nested {short_float, borrow_fee, days_to_cover} object, not a flat
// value - shown as its own three rows in the detail grid instead of one field, so a reader can see
// which factor is actually driving squeeze_score instead of just the final composite number.
const SQUEEZE_SCORE_COMPONENT_LABELS = {
  short_float: "Squeeze Score — Short Float Component",
  borrow_fee: "Squeeze Score — Borrow Fee Component",
  days_to_cover: "Squeeze Score — Days-to-Cover Component",
  ttm_squeeze: "Squeeze Score — TTM Squeeze Component",
};

function fmtNumber(value, digits = 2) {
  if (value === null || value === undefined) return "—";
  const num = Number(value);
  if (Number.isNaN(num)) return "—";
  return num.toFixed(digits);
}

// Matches a full ISO8601 datetime (e.g. "2026-07-17T14:28:33.408565+00:00") but not a bare date
// (e.g. "2026-06-30", short_interest_as_of) - dates have no time-of-day to misread as a timezone,
// so they're left alone.
const ISO_DATETIME_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/;

function fmtValue(value) {
  if (value === null || value === undefined) return "—";
  if (Array.isArray(value)) return value.length ? value.join(", ") : "—";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  // Every *_as_of/timestamp field the API sends is UTC (api_server.py/controller.py) - displaying
  // that raw string looks like it's "in the future" to anyone west of UTC, since UTC is always
  // ahead of local clocks there. Convert to the viewer's own local time, same as the status
  // banner already does for last_updated (new Date(...).toLocaleTimeString()).
  if (typeof value === "string" && ISO_DATETIME_RE.test(value)) {
    const parsed = new Date(value);
    if (!Number.isNaN(parsed.getTime())) return parsed.toLocaleString();
  }
  return String(value);
}

function squeezeBand(score) {
  if (score === null || score === undefined) return { className: "badge-neutral", label: "—" };
  if (score >= 90) return { className: "badge-critical", label: "Extreme" };
  if (score >= 70) return { className: "badge-serious", label: "High" };
  if (score >= 40) return { className: "badge-warning", label: "Moderate" };
  return { className: "badge-good", label: "Low" };
}

function tierBadge(tier) {
  if (tier === "prime") return `<span class="badge badge-good">Prime</span>`;
  if (tier === "subprime") return `<span class="badge badge-warning">Subprime</span>`;
  return `<span class="badge badge-neutral">${fmtValue(tier)}</span>`;
}

function scoreCell(score) {
  const band = squeezeBand(score);
  const pct = score === null || score === undefined ? 0 : Math.max(0, Math.min(100, score));
  return `
    <div class="score-cell">
      <span class="score-value">${score === null || score === undefined ? "—" : fmtNumber(score, 1)}</span>
      <span class="score-track"><span class="score-fill" style="width:${pct}%"></span></span>
    </div>`;
}

// Trend column (2026-07-17): a tiny inline Squeeze Score sparkline so "72" reads as "72, and
// climbing" without clicking into the detail row. Deliberately a stripped-down sibling of
// buildSparkChart (Chart tab, above) rather than a shared helper - this one has no axis labels,
// no reference lines, and a fixed small size meant to sit inside a table cell, so folding it into
// the bigger function would mean threading a bunch of "skip this for the mini version" flags
// through code that's otherwise simple on its own.
function buildMiniSparkline(points) {
  if (!points || points.length < 2) {
    return `<span class="muted sparkline-empty">not enough history yet</span>`;
  }
  const width = 72;
  const height = 24;
  const padding = 3;
  const times = points.map((p) => new Date(p.timestamp).getTime());
  const minTime = Math.min(...times);
  const maxTime = Math.max(...times);
  const span = maxTime - minTime || 1;
  const values = points.map((p) => p.squeeze_score);
  const lo = Math.min(...values);
  const hi = Math.max(...values);
  const valueRange = hi - lo || 1;
  const xForTime = (t) => padding + ((t - minTime) / span) * (width - padding * 2);
  const yForValue = (v) => height - padding - ((v - lo) / valueRange) * (height - padding * 2);
  const path = points.map((p, i) => `${xForTime(times[i])},${yForValue(p.squeeze_score)}`).join(" ");
  // Direction (first point vs. last point in the visible window) drives color, same "sign carried
  // in the visual, not just implied" convention as the Track Record panels' delta-positive/negative.
  const trendClass = values[values.length - 1] >= values[0] ? "sparkline-up" : "sparkline-down";
  return `
    <svg class="sparkline ${trendClass}" viewBox="0 0 ${width} ${height}" role="img" aria-label="Squeeze Score trend">
      <polyline points="${path}"></polyline>
    </svg>`;
}

function sortRows(rows) {
  const sorted = [...rows];
  sorted.sort((a, b) => {
    const av = a[sortKey];
    const bv = b[sortKey];
    if (av === null || av === undefined) return 1;
    if (bv === null || bv === undefined) return -1;
    if (typeof av === "string") {
      return sortDir === "asc" ? av.localeCompare(bv) : bv.localeCompare(av);
    }
    return sortDir === "asc" ? av - bv : bv - av;
  });
  return sorted;
}

function appendDetailItem(dl, label, valueText) {
  // Each dt+dd wrapped in its own grid cell so they stay stacked together - a bare dt/dd
  // auto-flowing into a multi-column grid drifts apart once more than 2 items fit per row
  // (found live 2026-07-16 testing this exact page).
  const item = document.createElement("div");
  item.className = "detail-item";
  const dt = document.createElement("dt");
  dt.textContent = label;
  const dd = document.createElement("dd");
  dd.textContent = valueText;
  item.append(dt, dd);
  dl.append(item);
}

function buildDetailGrid(row) {
  const dl = detailTemplate.content.cloneNode(true).querySelector(".detail-grid");
  for (const [key, value] of Object.entries(row)) {
    if (PRIMARY_FIELDS.has(key)) continue;
    if (key === "squeeze_score_breakdown") {
      for (const [component, label] of Object.entries(SQUEEZE_SCORE_COMPONENT_LABELS)) {
        const subScore = value ? value[component] : null;
        appendDetailItem(dl, label, subScore == null ? "—" : `${fmtNumber(subScore, 0)} / 100`);
      }
      continue;
    }
    appendDetailItem(dl, DETAIL_LABELS[key] || key, fmtValue(value));
  }
  return dl.outerHTML;
}

// Stats strip (2026-07-17): the first thing a reader sees before parsing a single table row -
// how many setups, how strong on average, and which one is leading right now. Recomputed from
// whatever rows renderTable was just given, not a separate fetch.
function renderStats(rows) {
  if (!rows.length) {
    statsStripEl.innerHTML = "";
    return;
  }
  const primeCount = rows.filter((r) => r.setup_tier === "prime").length;
  const subprimeCount = rows.filter((r) => r.setup_tier === "subprime").length;
  const scores = rows.map((r) => r.squeeze_score).filter((s) => s != null);
  const avgScore = scores.length ? scores.reduce((sum, s) => sum + s, 0) / scores.length : null;
  const top = rows.reduce(
    (best, r) => (r.squeeze_score != null && (!best || r.squeeze_score > best.squeeze_score) ? r : best),
    null
  );

  const stats = [
    ["Prime", primeCount],
    ["Subprime", subprimeCount],
    ["Avg Squeeze Score", avgScore != null ? fmtNumber(avgScore, 0) : "—"],
    ["Top Setup", top ? fmtValue(top.ticker) : "—"],
  ];
  statsStripEl.innerHTML = stats
    .map(([label, value]) => `<div class="stat"><span class="stat-value">${value}</span><span class="stat-label">${label}</span></div>`)
    .join("");
}

function renderTable(rows) {
  rowCountEl.textContent = rows.length ? `${rows.length} setups` : "";
  renderStats(rows);

  if (!rows.length) {
    tableBody.innerHTML = `<tr class="empty-row"><td colspan="13">No Prime/Subprime setups this cycle.</td></tr>`;
    return;
  }

  const sorted = sortRows(rows);
  tableBody.innerHTML = "";

  for (const row of sorted) {
    const tr = document.createElement("tr");
    tr.className = "data-row";
    tr.dataset.ticker = row.ticker;
    tr.innerHTML = `
      <td>${scoreCell(row.squeeze_score)}</td>
      <td>${buildMiniSparkline(scoreHistoryCache.get(row.ticker))}</td>
      <td><strong>${fmtValue(row.ticker)}</strong></td>
      <td>${tierBadge(row.setup_tier)}</td>
      <td class="num">${row.price != null ? "$" + fmtNumber(row.price) : "—"}</td>
      <td class="num">${row.change_percent != null ? fmtNumber(row.change_percent) + "%" : "—"}</td>
      <td class="num">${row.short_float_percent != null ? fmtNumber(row.short_float_percent) + "%" : "—"}</td>
      <td class="num">${fmtNumber(row.days_to_cover)}</td>
      <td class="num">${row.ib_borrow_fee_rate != null ? fmtNumber(row.ib_borrow_fee_rate) + "%" : "—"}</td>
      <td>${row.ttm_squeeze_fired
        ? '<span class="badge badge-critical">Just Released</span>'
        : (row.ttm_squeeze_on ? '<span class="badge badge-accent">Compressed</span>' : "")}</td>
      <td class="num">${row.ttm_squeeze_momentum != null ? fmtNumber(row.ttm_squeeze_momentum, 2) : "—"}</td>
      <td>${row.squeeze_confirmed ? '<span class="badge badge-good">Confirmed</span>' : ""}</td>
      <td>${row.sentiment_label ? fmtValue(row.sentiment_label) : "—"}</td>
    `;
    tr.addEventListener("click", () => {
      expandedTicker = expandedTicker === row.ticker ? null : row.ticker;
      renderTable(lastRows);
    });
    tableBody.appendChild(tr);

    if (expandedTicker === row.ticker) {
      const detailTr = document.createElement("tr");
      detailTr.className = "detail-row";
      detailTr.innerHTML = `<td colspan="13">${buildDetailGrid(row)}</td>`;
      tableBody.appendChild(detailTr);
    }
  }
}

function setStatus(state, text) {
  statusBanner.dataset.state = state;
  statusText.textContent = text;
}

async function refresh() {
  let health;
  try {
    const healthResponse = await fetch("/health");
    health = await healthResponse.json();
  } catch (err) {
    setStatus("error", "Can't reach the local API");
    return;
  }

  if (health.status === "starting") {
    setStatus("starting", "Waiting for the first scan…");
    return;
  }

  if (health.status === "stale" || health.status === "unavailable") {
    const age = health.snapshot_age_seconds != null ? `${Math.round(health.snapshot_age_seconds)}s old` : "unknown age";
    setStatus(health.status, `Snapshot ${health.status} (${age}) — showing last known data`);
    // Keep whatever's already rendered rather than blanking it.
    return;
  }

  setStatus("ok", `Live — updated ${new Date(health.last_updated).toLocaleTimeString()}`);

  try {
    const screenerResponse = await fetch("/screener");
    lastRows = await screenerResponse.json();
    await loadScoreHistories(lastRows.map((row) => row.ticker));
    renderTable(lastRows);
  } catch (err) {
    setStatus("error", "Failed to load screener data");
  }
}

// Fetches (or refreshes) squeeze-score-history for every ticker currently on the board, so the
// Trend column's sparkline has data before renderTable runs. Reuses the same
// /squeeze-score-history/:ticker route the Chart tab already calls - one extra small request per
// visible ticker per 15s cycle, all local, not worth caching more aggressively than "refetch each
// cycle" for a handful of rows.
async function loadScoreHistories(tickers) {
  await Promise.all(tickers.map(async (ticker) => {
    try {
      const response = await fetch(`/squeeze-score-history/${encodeURIComponent(ticker)}`);
      scoreHistoryCache.set(ticker, await response.json());
    } catch (err) {
      // Non-fatal - that row's sparkline just falls back to "not enough history yet".
    }
  }));
}

// Breaking News runs on its own independent cadence in the backend (view.py's
// refresh_breaking_news_tab() has its own timer chain, unrelated to the screener's /health), so
// this polls separately rather than being gated by the screener's health status above.
function renderNews(headlines) {
  const query = newsFilterInput.value.trim().toUpperCase();
  const filtered = query
    ? headlines.filter((item) => (item.tickers || []).some((t) => t.toUpperCase() === query))
    : headlines;

  newsCountEl.textContent = headlines.length ? `${filtered.length} of ${headlines.length}` : "";
  newsList.innerHTML = "";

  if (!filtered.length) {
    const empty = document.createElement("p");
    empty.className = "muted";
    empty.textContent = headlines.length ? "No headlines match that ticker." : "No high-confidence headlines yet.";
    newsList.appendChild(empty);
    return;
  }

  // Headline text/tickers/URLs come from external news sources (yfinance/Finviz/NewsAPI) -
  // built via DOM APIs (textContent, element attributes) rather than innerHTML string
  // interpolation, so nothing in a headline can execute as markup.
  for (const item of filtered) {
    const card = document.createElement("div");
    card.className = "news-item";

    const link = document.createElement("a");
    link.textContent = item.headline || "(no headline)";
    if (item.url) {
      link.href = item.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
    }
    card.appendChild(link);

    const meta = document.createElement("div");
    meta.className = "news-item-meta";
    const tickers = (item.tickers || []).join(", ");
    const confidence = item.confidence_score != null ? Math.round(item.confidence_score * 100) : null;
    meta.textContent = [tickers, confidence != null ? `${confidence}% confidence` : null]
      .filter(Boolean)
      .join(" · ");
    card.appendChild(meta);

    newsList.appendChild(card);
  }
}

async function refreshNews() {
  try {
    const response = await fetch("/news");
    lastHeadlines = await response.json();
    renderNews(lastHeadlines);
  } catch (err) {
    // Non-fatal - the screener status banner already surfaces connectivity problems; the news
    // panel just quietly keeps showing whatever it last had.
  }
}

newsFilterInput.addEventListener("input", () => renderNews(lastHeadlines));

// Stock Chart (2026-07-16): web equivalent of the Tkinter Chart tab's matplotlib plot - user
// enters a ticker, we fetch GET /chart/:ticker (a plain JSON [{timestamp, close}, ...] series,
// core/chart_data.py) and draw it as an inline SVG polyline. No charting library - one line
// series doesn't need one, and it keeps the static/ bundle dependency-free.
//
// Squeeze Score history (2026-07-16) renders as a second, separately-scaled mini chart below the
// price one rather than a second y-axis on the same plot - a dual-axis chart is the #1 documented
// chart-design anti-pattern (two measures of very different scale get visually correlated in a way
// that isn't real). Small multiples sharing the same time axis instead.
function buildSparkChart({ points, valueKey, lineClass, formatValue, minTime, maxTime, minValue, maxValue, referenceLines }) {
  const width = 640;
  const height = 120;
  const padding = { top: 10, right: 16, bottom: 10, left: 52 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const span = maxTime - minTime || 1;
  const xForTime = (t) => padding.left + ((t - minTime) / span) * plotWidth;

  const values = points.map((p) => p[valueKey]);
  let lo = minValue != null ? minValue : Math.min(...values);
  let hi = maxValue != null ? maxValue : Math.max(...values);
  // Widen the range to fit any reference lines (target/stop-loss) so a level well outside the
  // period's actual price range still shows on-chart rather than clipping off the top/bottom.
  for (const ref of referenceLines || []) {
    lo = Math.min(lo, ref.value);
    hi = Math.max(hi, ref.value);
  }
  const valueRange = hi - lo || 1;
  const yForValue = (v) => padding.top + plotHeight - ((v - lo) / valueRange) * plotHeight;

  const path = points
    .map((p) => `${xForTime(new Date(p.timestamp).getTime())},${yForValue(p[valueKey])}`)
    .join(" ");

  // Rendered before the data polyline so the price line stays visually on top where they cross.
  // Label text stays in muted ink rather than the reference line's own color - the word itself
  // ("Target"/"Stop") already names it, so color isn't needed to identify it, and text should
  // wear text tokens rather than series/status color.
  const refLinesSvg = (referenceLines || []).map((ref) => {
    const y = yForValue(ref.value);
    return `
      <line class="chart-reference-line ${ref.lineClass}" x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}"></line>
      <text class="chart-axis-label" x="${width - padding.right}" y="${y - 3}" text-anchor="end">${ref.label}</text>`;
  }).join("");

  return `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="chart">
      <text class="chart-axis-label" x="${padding.left}" y="${padding.top + 4}">${formatValue(hi)}</text>
      <text class="chart-axis-label" x="${padding.left}" y="${height - padding.bottom + 4}">${formatValue(lo)}</text>
      ${refLinesSvg}
      <polyline class="chart-line ${lineClass}" points="${path}"></polyline>
    </svg>`;
}

function buildChartPanel(pricePoints, scorePoints, referenceLines) {
  const priceTimes = pricePoints.map((p) => new Date(p.timestamp).getTime());
  const minTime = Math.min(...priceTimes);
  const maxTime = Math.max(...priceTimes);
  const firstLabel = new Date(pricePoints[0].timestamp).toLocaleDateString();
  const lastLabel = new Date(pricePoints[pricePoints.length - 1].timestamp).toLocaleDateString();

  const priceSvg = buildSparkChart({
    points: pricePoints, valueKey: "close", lineClass: "chart-line-price",
    formatValue: (v) => `$${fmtNumber(v)}`, minTime, maxTime, referenceLines,
  });

  // Only the portion of score history that falls within the price chart's own 5-day window -
  // logging started 2026-07-16, so early on this will legitimately be a partial/empty range.
  const visibleScores = scorePoints.filter((p) => {
    const t = new Date(p.timestamp).getTime();
    return t >= minTime && t <= maxTime;
  });
  const scoreSvg = visibleScores.length
    ? `<p class="chart-subtitle">Squeeze Score</p>
       ${buildSparkChart({
         points: visibleScores, valueKey: "squeeze_score", lineClass: "chart-line-score",
         formatValue: (v) => fmtNumber(v, 0), minTime, maxTime, minValue: 0, maxValue: 100,
       })}`
    : `<p class="muted chart-subtitle">No Squeeze Score history logged yet for this ticker/window.</p>`;

  return `
    <p class="chart-subtitle">Price</p>
    ${priceSvg}
    ${scoreSvg}
    <div class="chart-range-labels"><span>${firstLabel}</span><span>${lastLabel}</span></div>`;
}

// Target/stop-loss reference lines (2026-07-16): computed from the screener's own already-fetched
// row data (lastRows) rather than a new API call - target_percent/stop_loss_percent/price are
// already on the row schema-v1 already sends. Only present when the loaded ticker is currently a
// Prime/Subprime setup this cycle; otherwise there's nothing to draw and the chart is just price.
function targetStopReferenceLines(ticker) {
  const row = lastRows.find((r) => r.ticker === ticker);
  if (!row || row.price == null) return [];

  const lines = [];
  if (row.target_percent != null) {
    const targetPrice = row.price * (1 + row.target_percent / 100);
    lines.push({ value: targetPrice, label: `Target $${fmtNumber(targetPrice)}`, lineClass: "chart-reference-target" });
  }
  if (row.stop_loss_percent != null) {
    const stopPrice = row.price * (1 + row.stop_loss_percent / 100);
    lines.push({ value: stopPrice, label: `Stop $${fmtNumber(stopPrice)}`, lineClass: "chart-reference-stop" });
  }
  return lines;
}

async function loadChart(ticker) {
  chartContainer.innerHTML = `<p class="muted">Loading ${ticker}…</p>`;
  chartRangeEl.textContent = "";

  try {
    const response = await fetch(`/chart/${encodeURIComponent(ticker)}`);
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.detail || `No chart data for ${ticker}`);
    }
    const points = await response.json();
    if (!points.length) throw new Error(`No chart data for ${ticker}`);

    let scorePoints = [];
    try {
      const scoreResponse = await fetch(`/squeeze-score-history/${encodeURIComponent(ticker)}`);
      if (scoreResponse.ok) scorePoints = await scoreResponse.json();
    } catch (err) {
      // Non-fatal - the price chart still renders without the Squeeze Score panel.
    }

    const referenceLines = targetStopReferenceLines(ticker);
    chartContainer.innerHTML = buildChartPanel(points, scorePoints, referenceLines);
    chartRangeEl.textContent = `${ticker} — 5 day, 30 min`;
  } catch (err) {
    chartContainer.innerHTML = `<p class="muted">${err.message}</p>`;
  }
}

chartForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const ticker = chartTickerInput.value.trim().toUpperCase();
  if (ticker) loadChart(ticker);
});

// Track Record (2026-07-16, extended 2026-07-17 for corroboration): turns a backtest evaluator's
// graded results into something visible in the browser rather than only existing as terminal
// output. A plain table, not a chart - a handful of rows of aggregate numbers don't need a
// visualization, and a table reads exactly (per-band n / avg return / hit rate) rather than
// requiring the reader to eyeball a bar height. Shared by both the Squeeze Score and
// Corroboration panels since they're structurally identical, just different band semantics.
// "vs SPY" (also 2026-07-17, core/benchmark.py) answers "compared to what?" - a hit rate alone
// doesn't say whether picks actually beat just holding the market over the same window. Shown as
// "—" for a band where no graded row yet has a benchmark value (e.g. evaluator ran before
// core/benchmark.py existed), not as a misleading 0%.
const SMALL_SAMPLE_THRESHOLD = 10;

// Diverging bar for the "vs SPY" cell (2026-07-17): a number alone ("+2.00%") takes a beat to
// parse as "better than the market" or "worse" - a bar that grows right-from-center for positive
// and left-from-center for negative reads instantly, and a room full of people can see "this band
// clearly beats the market" from the back row. Capped at +/-20% so one outlier band doesn't
// squash every other bar down to a sliver; the number next to it still carries the exact value.
const ALPHA_BAR_CAP_PERCENT = 20;

function alphaBar(alpha) {
  if (typeof alpha !== "number") return "";
  const magnitude = Math.min(Math.abs(alpha), ALPHA_BAR_CAP_PERCENT) / ALPHA_BAR_CAP_PERCENT * 50;
  const positive = alpha >= 0;
  const side = positive ? `left:50%` : `right:50%`;
  return `
    <div class="alpha-bar-track" aria-hidden="true">
      <div class="alpha-bar-center"></div>
      <div class="alpha-bar-fill ${positive ? "alpha-bar-positive" : "alpha-bar-negative"}" style="width:${magnitude}%;${side}"></div>
    </div>`;
}

function renderTrackRecordTable(container, countEl, summary, { bandColumnLabel, emptyMessage }) {
  countEl.textContent = summary.length ? `${summary.length} band(s) graded` : "";

  if (!summary.length) {
    container.innerHTML = `<p class="muted">${emptyMessage}</p>`;
    return;
  }

  const totalN = summary.reduce((sum, row) => sum + row.n, 0);
  const rows = summary.map((row) => {
    const deltaClass = row.avg_change_percent >= 0 ? "delta-positive" : "delta-negative";
    const sign = row.avg_change_percent >= 0 ? "+" : "";
    const hasAlpha = typeof row.avg_alpha_percent === "number";
    const alphaClass = hasAlpha ? (row.avg_alpha_percent >= 0 ? "delta-positive" : "delta-negative") : "";
    const alphaSign = hasAlpha && row.avg_alpha_percent >= 0 ? "+" : "";
    const alphaText = hasAlpha ? `${alphaSign}${fmtNumber(row.avg_alpha_percent)}%` : "—";
    return `
      <tr>
        <td>${row.score_band}</td>
        <td class="num">${row.n}</td>
        <td class="num ${deltaClass}">${sign}${fmtNumber(row.avg_change_percent)}%</td>
        <td class="num ${alphaClass}">
          <div class="alpha-cell">
            <span>${alphaText}</span>
            ${alphaBar(hasAlpha ? row.avg_alpha_percent : null)}
          </div>
        </td>
        <td class="num">${fmtNumber(row.hit_rate_percent, 1)}%</td>
      </tr>`;
  }).join("");

  // Small-sample honesty: always state how many picks the numbers above are actually based on,
  // and say plainly when that's still too few to mean anything - a percentage on its own looks
  // more authoritative than a 2-pick sample actually is.
  const caveat = totalN < SMALL_SAMPLE_THRESHOLD
    ? `Based on ${totalN} graded pick${totalN === 1 ? "" : "s"} total — too few yet to draw reliable conclusions.`
    : `Based on ${totalN} graded picks total.`;

  container.innerHTML = `
    <table class="track-record-table">
      <thead>
        <tr>
          <th scope="col">${bandColumnLabel}</th>
          <th scope="col" class="num">Picks</th>
          <th scope="col" class="num">Avg Return</th>
          <th scope="col" class="num" title="Avg return minus SPY's return over the same holding period">vs SPY</th>
          <th scope="col" class="num">Hit Rate</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
    <p class="muted track-record-caveat">${caveat}</p>`;
}

function renderTrackRecord(summary) {
  renderTrackRecordTable(trackRecordContainer, trackRecordCountEl, summary, {
    bandColumnLabel: "Squeeze Score",
    emptyMessage: "No graded outcomes yet — picks need to age at least a day before they're scored.",
  });
}

function renderCorroborationTrackRecord(summary) {
  renderTrackRecordTable(corroborationTrackRecordContainer, corroborationTrackRecordCountEl, summary, {
    bandColumnLabel: "Corroboration Score",
    emptyMessage: "No graded outcomes yet — picks need to age at least a day before they're scored.",
  });
}

async function refreshTrackRecord() {
  try {
    const response = await fetch("/squeeze-score-track-record");
    renderTrackRecord(await response.json());
  } catch (err) {
    // Non-fatal - the panel just keeps showing whatever it last had, same as refreshNews().
  }
}

async function refreshCorroborationTrackRecord() {
  try {
    const response = await fetch("/corroboration-track-record");
    renderCorroborationTrackRecord(await response.json());
  } catch (err) {
    // Non-fatal - the panel just keeps showing whatever it last had.
  }
}

document.querySelectorAll("th.sortable").forEach((th) => {
  th.addEventListener("click", () => {
    const key = th.dataset.sort;
    if (sortKey === key) {
      sortDir = sortDir === "asc" ? "desc" : "asc";
    } else {
      sortKey = key;
      sortDir = "desc";
    }
    document.querySelectorAll("th.sortable").forEach((el) => el.classList.remove("sort-asc", "sort-desc"));
    th.classList.add(sortDir === "asc" ? "sort-asc" : "sort-desc");
    renderTable(lastRows);
  });
});

refresh();
refreshNews();
refreshTrackRecord();
refreshCorroborationTrackRecord();
setInterval(refresh, REFRESH_INTERVAL_MS);
setInterval(refreshNews, REFRESH_INTERVAL_MS);
setInterval(refreshTrackRecord, REFRESH_INTERVAL_MS);
setInterval(refreshCorroborationTrackRecord, REFRESH_INTERVAL_MS);
