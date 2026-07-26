"use strict";

const state = {
  rows: [],
  filteredRows: [],
  selected: null,
  summary: null,
  autoTimer: null,
  sortKey: null,
  sortDesc: false,
  mode: "FROZEN",
};

/* ------------------------------------------------------------------ fetching */
/* getJSON, setStatus, ago, CLASS_COLORS, PRESSURE_COLORS, pressureColor — provided by shared.js */

/* ------------------------------------------------------------------ render table */

function cv(row, name) {
  const cell = (row.fields || {})[name];
  return cell && cell.status === "KNOWN" ? cell.value : null;
}

function cf(row, name) {
  return (row.fields || {})[name] || null;
}

function classification(row) {
  const methods = row.methodologies || [];
  const adam = methods.find(function (m) { return m.methodology_id === "adam_evidence_gated_prime.v1"; });
  return adam ? adam.classification : "UNEVALUABLE";
}

function coveragePct(row) {
  const cov = row.methodology_coverage || {};
  return cov.percent != null ? cov.percent : null;
}

function coverageLabel(row) {
  const pct = coveragePct(row);
  if (pct == null) return "\u2014";
  if (pct >= 80) return "HIGH " + pct + "%";
  if (pct >= 60) return "MODERATE " + pct + "%";
  if (pct >= 40) return "LOW " + pct + "%";
  return "INSUFFICIENT " + pct + "%";
}

function coverageCategory(row) {
  const pct = coveragePct(row);
  if (pct == null) return "none";
  if (pct >= 80) return "high";
  if (pct >= 60) return "moderate";
  if (pct >= 40) return "low";
  return "insufficient";
}

function sentimentLabel(row) {
  const s = cf(row, "sentiment");
  if (!s || s.status !== "KNOWN") return null;
  var v = s.value;
  if (v === "positive") return "POSITIVE";
  if (v === "neutral") return "NEUTRAL";
  if (v === "negative") return "NEGATIVE";
  if (v === "mixed" || v === "MIXED") return "MIXED";
  return v ? String(v).toUpperCase() : null;
}

function sentimentColor(label) {
  if (!label) return "#4a5568";
  if (label === "POSITIVE") return "#56d68b";
  if (label === "NEGATIVE") return "#ff7d7d";
  if (label === "MIXED") return "#ffca57";
  return "#8b98a9";
}

function newsCount(row) {
  var n = cf(row, "news_count");
  if (!n || n.status !== "KNOWN") return null;
  return n.value;
}

/* ------------------------------------------------------------------ columns */

var SCANNER_COLUMNS = [
  { label: "SYMBOL", key: "symbol", sortable: true, primary: true },
  { label: "PRICE", key: "price", sortable: true },
  { label: "CHANGE %", key: "percentage_change", sortable: true, emphasis: true },
  { label: "REL VOL", key: "relative_volume", sortable: true },
  { label: "FLOAT", key: "float_shares", sortable: true, secondary: true },
  { label: "SHORT FLOAT %", key: "short_float", sortable: true, secondary: true },
  { label: "SHORT RATIO", key: "short_ratio", sortable: true, secondary: true },
  { label: "DAYS TO COVER", key: "days_to_cover", sortable: true, secondary: true },
  { label: "BORROW", key: "borrow", sortable: false, secondary: true },
  { label: "PRESSURE", key: "pressure", sortable: true, emphasis: true },
  { label: "IGNITION", key: "ignition", sortable: true, emphasis: true },
  { label: "EVIDENCE", key: "evidence_coverage", sortable: true, emphasis: true },
  { label: "NEWS", key: "news", sortable: true },
  { label: "SENTIMENT", key: "sentiment", sortable: true },
  { label: "CLASSIFICATION", key: "classification", sortable: true, emphasis: true },
  { label: "WHY LISTED", key: "why_listed", sortable: false },
  { label: "UPDATED", key: "updated", sortable: true, secondary: true },
];

/* ------------------------------------------------------------------ render table */

function valueFor(row, key) {
  switch (key) {
    case "symbol": return row.symbol;
    case "price": return cv(row, "last") || cv(row, "finviz_price") || cv(row, "finnhub_price");
    case "percentage_change": {
      // 1. Canonical metric from IBKR
      var pc = cv(row, "percentage_change");
      if (pc !== null) return pc;
      // 2. Finviz Elite export change %
      var fvpc = cv(row, "finviz_change_pct");
      if (fvpc !== null) return fvpc;
      // 3. Computed: (last price - previous close) / previous close
      var current = cv(row, "last") || cv(row, "finviz_price") || cv(row, "finnhub_price");
      var prev = cv(row, "previous_close");
      if (current != null && prev != null && prev !== 0) {
        return ((current - prev) / prev) * 100;
      }
      return null;
    }
    case "relative_volume": {
      var rv = cv(row, "relative_volume");
      if (rv !== null) return rv;
      return cv(row, "relative_volume_provider");
    }
    case "float_shares": return cv(row, "float_shares");
    case "short_float": return cv(row, "short_float");
    case "short_ratio": return cv(row, "short_ratio");
    case "days_to_cover": return cv(row, "days_to_cover");
    case "borrow": return cv(row, "borrow_fee") || cv(row, "shortable");
    case "pressure": return row.pressure;
    case "ignition": return row.ignition;
    case "evidence_coverage": return coveragePct(row);
    case "news": return newsCount(row);
    case "sentiment": return sentimentLabel(row);
    case "classification": return classification(row);
    case "why_listed": return (row.why_listed || []).join("; ");
    case "updated": return ago(row.last_updated) || row.last_updated;
    default: return null;
  }
}

function cellContent(row, col) {
  var td = document.createElement("td");
  td.classList.add("sc-" + col.key);

  if (col.primary) td.classList.add("primary");
  if (col.secondary) td.classList.add("secondary");
  if (col.emphasis) td.classList.add("emphasis");

  var value = valueFor(row, col.key);

  if (col.key === "symbol") {
    var strong = document.createElement("strong");
    strong.textContent = row.symbol;
    td.appendChild(strong);
    if (row.stale) {
      var tag = document.createElement("span");
      tag.className = "pill pill-blocked";
      tag.style.marginLeft = "4px";
      tag.textContent = "STALE";
      tag.title = row.stale_reason || "";
      td.appendChild(tag);
    }
    return td;
  }

  if (col.key === "classification") {
    var cls = value || "UNEVALUABLE";
    var clsSpan = document.createElement("span");
    clsSpan.className = "class-badge";
    clsSpan.style.backgroundColor = CLASS_COLORS[cls] || CLASS_COLORS.UNEVALUABLE;
    clsSpan.textContent = cls.replace(/_/g, " ");
    td.appendChild(clsSpan);
    td.style.whiteSpace = "nowrap";
    return td;
  }

  if (col.key === "pressure" || col.key === "ignition") {
    if (value == null) {
      var insufficient = document.createElement("span");
      insufficient.className = "muted";
      insufficient.textContent = MISSING;
      insufficient.title = "Insufficient evidence";
      td.appendChild(insufficient);
      return td;
    }
    var v = Number(value);
    var color = pressureColor(v);
    var bar = document.createElement("div");
    bar.className = "score-bar";
    bar.style.width = v + "%";
    bar.style.backgroundColor = color;
    var label = document.createElement("span");
    label.className = "score-label";
    label.textContent = v;
    label.style.color = color;
    td.appendChild(bar);
    td.appendChild(label);
    td.title = col.key === "pressure" ? "Short pressure dimension" : "Ignition / momentum dimension";
    td.style.whiteSpace = "nowrap";
    return td;
  }

  if (col.key === "evidence_coverage") {
    var cat = coverageCategory(row);
    var pct = coveragePct(row);
    var evSpan = document.createElement("span");
    evSpan.className = "coverage-pill cov-" + cat;
    evSpan.textContent = coverageLabel(row);
    td.appendChild(evSpan);
    if (pct != null && cat === "insufficient") {
      evSpan.title = "Insufficient evidence coverage";
    }
    return td;
  }

  if (col.key === "sentiment") {
    var sentSpan = document.createElement("span");
    if (!value) {
      sentSpan.textContent = MISSING;
      sentSpan.className = "muted";
    } else {
      sentSpan.textContent = value;
      sentSpan.style.color = sentimentColor(value);
      sentSpan.style.fontWeight = "700";
      sentSpan.style.letterSpacing = "0.04em";
    }
    td.appendChild(sentSpan);
    return td;
  }

  if (col.key === "news") {
    if (value == null) {
      td.textContent = MISSING;
      td.className = td.className + " muted";
      return td;
    }
    td.textContent = value;
    return td;
  }

  if (col.key === "percentage_change") {
    if (value == null) { td.textContent = MISSING; td.className = td.className + " muted"; return td; }
    var changeColor = value >= 0 ? "#56d68b" : "#ff7d7d";
    td.textContent = (value >= 0 ? "+" : "") + value.toFixed(2) + "%";
    td.style.color = changeColor;
    td.style.fontWeight = "700";
    return td;
  }

  if (col.key === "borrow") {
    if (value == null) { td.textContent = MISSING; td.className = td.className + " muted"; return td; }
    var borrowRate = cv(row, "borrow_fee");
    var shortableVal = cv(row, "shortable");
    var parts = [];
    if (borrowRate != null) parts.push(borrowRate + "%");
    if (shortableVal != null) {
      if (shortableVal >= 1) parts.push("S");
      else parts.push("NS");
    }
    td.textContent = parts.length ? parts.join(" ") : MISSING;
    td.title = borrowRate != null ? "Borrow fee: " + borrowRate + "%" : "Borrow fee unavailable";
    return td;
  }

  if (col.key === "why_listed") {
    var reason = value || MISSING;
    td.textContent = reason.length > 60 ? reason.substring(0, 57) + "..." : reason;
    td.title = reason;
    if (!value) td.className = td.className + " muted";
    td.classList.add("why-cell");
    return td;
  }

  if (value === null || value === undefined) {
    td.textContent = MISSING;
    td.className = td.className + " muted";
    return td;
  }

  td.textContent = typeof value === "number" ? Number(value).toLocaleString() : String(value);
  return td;
}

function renderHead() {
  var head = el("scanner-head");
  head.textContent = "";
  SCANNER_COLUMNS.forEach(function (col) {
    var th = document.createElement("th");
    th.textContent = col.label;
    if (col.sortable) {
      th.classList.add("sortable");
      th.setAttribute("data-key", col.key);
      if (state.sortKey === col.key) {
        th.classList.add(state.sortDesc ? "sorted-desc" : "sorted-asc");
      }
      th.addEventListener("click", function () {
        if (state.sortKey === col.key) {
          state.sortDesc = !state.sortDesc;
        } else {
          state.sortKey = col.key;
          state.sortDesc = false;
        }
        renderRows(state.filteredRows);
      });
    }
    if (col.primary) th.classList.add("primary");
    if (col.secondary) th.classList.add("secondary");
    if (col.emphasis) th.classList.add("emphasis");
    head.appendChild(th);
  });
}

function sortRows(rows) {
  if (!state.sortKey) return defaultSort(rows);
  var key = state.sortKey;
  var known = [];
  var missing = [];
  rows.forEach(function (row) {
    var v = valueFor(row, key);
    if (v == null || v === undefined) missing.push(row);
    else known.push(row);
  });
  known.sort(function (a, b) {
    var av = valueFor(a, key);
    var bv = valueFor(b, key);
    if (typeof av === "string" && typeof bv === "string") {
      return state.sortDesc ? bv.localeCompare(av) : av.localeCompare(bv);
    }
    var aNum = Number(av) || 0;
    var bNum = Number(bv) || 0;
    return state.sortDesc ? bNum - aNum : aNum - bNum;
  });
  return known.concat(missing);
}

function defaultSort(rows) {
  var order = { PRIME: 0, SUBPRIME: 1, WATCH: 2, CONFLICTED: 3, NOT_QUALIFIED: 4, UNEVALUABLE: 5 };
  return rows.slice().sort(function (a, b) {
    var aCls = classification(a);
    var bCls = classification(b);
    return (order[aCls] || 9) - (order[bCls] || 9) || (b.pressure || 0) - (a.pressure || 0);
  });
}

function renderRows(rows) {
  var body = el("scanner-body");
  body.textContent = "";
  rows = sortRows(rows);
  renderClassificationLegend();
  if (!rows.length) {
    var tr = document.createElement("tr");
    var td = document.createElement("td");
    td.colSpan = SCANNER_COLUMNS.length;
    td.className = "muted";
    td.style.textAlign = "center";
    td.textContent = "No candidates.";
    tr.appendChild(td);
    body.appendChild(tr);
    return;
  }

  var prevCls = null;
  var groupCount = 0;

  rows.forEach(function (row, idx) {
    var cls = classification(row);

    // Count rows in current classification group
    if (cls !== prevCls) {
      // Section divider header
      var div = document.createElement("tr");
      div.className = "cls-divider cls-" + cls;
      var divTd = document.createElement("td");
      divTd.colSpan = SCANNER_COLUMNS.length;
      divTd.textContent = cls.replace(/_/g, " ");
      div.appendChild(divTd);
      body.appendChild(div);
      prevCls = cls;
    }

    var tr = document.createElement("tr");
    tr.className = "clickable cls-" + cls;
    if (state.selected === row.symbol) tr.classList.add("selected");
    tr.addEventListener("click", function () { selectSymbol(row.symbol); });
    SCANNER_COLUMNS.forEach(function (col) {
      tr.appendChild(cellContent(row, col));
    });
    body.appendChild(tr);
  });
}

/* ------------------------------------------------------------------ summary */
function renderClassificationLegend() {
  var legend = el("classification-legend");
  if (!legend) return;
  legend.textContent = "";

  var rows = state.rows;
  var counts = {};
  rows.forEach(function (row) {
    var c = classification(row);
    counts[c] = (counts[c] || 0) + 1;
  });

  var order = ["PRIME", "SUBPRIME", "WATCH", "NOT_QUALIFIED", "UNEVALUABLE", "CONFLICTED", "REFERENCE_DEFINITION_INCOMPLETE"];
  var total = rows.length;

  var totalSpan = document.createElement("span");
  totalSpan.className = "legend-total";
  totalSpan.textContent = total + " Candidates";
  legend.appendChild(totalSpan);

  order.forEach(function (cls) {
    var n = counts[cls] || 0;
    var badge = document.createElement("span");
    badge.className = "legend-badge";
    badge.style.backgroundColor = CLASS_COLORS[cls] || CLASS_COLORS.UNEVALUABLE;
    badge.textContent = cls.replace(/_/g, " ") + " " + n;
    badge.title = n + " candidates classified as " + cls.replace(/_/g, " ");
    legend.appendChild(badge);
  });
}

function renderSummary(rows) {
  var div = el("scanner-summary");
  var counts = {};

  rows.forEach(function (row) {
    var c = classification(row);
    counts[c] = (counts[c] || 0) + 1;
  });
  var parts = [rows.length + " Candidates"];
  if (counts.PRIME) parts.push(counts.PRIME + " Prime");
  if (counts.SUBPRIME) parts.push(counts.SUBPRIME + " Subprime");
  if (counts.WATCH) parts.push(counts.WATCH + " Watch");
  if (counts.UNEVALUABLE) parts.push(counts.UNEVALUABLE + " Unevaluable");
  if (counts.CONFLICTED) parts.push(counts.CONFLICTED + " Conflicted");

  var evaluable = rows.filter(function (row) {
    var c = classification(row);
    return c !== "UNEVALUABLE" && c !== "CONFLICTED";
  }).length;
  if (evaluable > 0) parts.push("Evaluable: " + evaluable);

  var newsRows = rows.filter(function (row) { return newsCount(row) != null; }).length;
  if (newsRows > 0) parts.push("News: " + newsRows);

  div.textContent = parts.join("  \u00b7  ");
  div.title = "Summary of current candidates";
}

function renderBanner(mode) {
  var banners = el("banners");
  banners.textContent = "";
  if (mode === "FROZEN") {
    var b = document.createElement("div");
    b.className = "alert alert-info";
    b.style.cssText = "background:#1a2740;color:#6fa8ff;padding:8px 16px;border-left:3px solid #6fa8ff;margin:8px 0;font-size:13px";
    b.innerHTML = "<strong>FROZEN RESEARCH MODE</strong> &mdash; Showing pre-computed research cases. Live market discovery is pending &mdash; click <strong>Refresh</strong> when IB Gateway is ready.";
    banners.appendChild(b);
  }
}

/* ------------------------------------------------------------------ filters */

function applyFilters(rows) {
  var cls = el("filter-classification").value;
  var sym = el("filter-symbol").value.trim().toUpperCase();
  var minPrice = parseFloat(el("filter-min-price").value) || null;
  var maxPrice = parseFloat(el("filter-max-price").value) || null;
  var minChange = parseFloat(el("filter-min-change").value) || null;
  var minRelvol = parseFloat(el("filter-min-relvol").value) || null;
  var minPressure = parseFloat(el("filter-min-pressure").value) || null;
  var minIgnition = parseFloat(el("filter-min-ignition").value) || null;
  var minCoverage = parseFloat(el("filter-min-coverage").value) || null;
  var newsFilter = el("filter-news").value;
  var sentimentFilter = el("filter-sentiment").value;
  var maxFloat = parseFloat(el("filter-max-float").value) || null;

  return rows.filter(function (row) {
    if (cls && classification(row) !== cls) return false;
    if (sym && row.symbol.indexOf(sym) === -1) return false;
    if (minPrice != null) {
      var p = cv(row, "last");
      if (p == null || p < minPrice) return false;
    }
    if (maxPrice != null) {
      var p2 = cv(row, "last");
      if (p2 == null || p2 > maxPrice) return false;
    }
    if (minChange != null) {
      var c = valueFor(row, "percentage_change");
      if (c == null || c < minChange) return false;
    }
    if (minRelvol != null) {
      var r = valueFor(row, "relative_volume");
      if (r == null || r < minRelvol) return false;
    }
    if (minPressure != null) {
      if (row.pressure == null || row.pressure < minPressure) return false;
    }
    if (minIgnition != null) {
      if (row.ignition == null || row.ignition < minIgnition) return false;
    }
    if (minCoverage != null) {
      var cov = coveragePct(row);
      if (cov == null || cov < minCoverage) return false;
    }
    if (newsFilter === "has") {
      var n = newsCount(row);
      if (n == null || n === 0) return false;
    }
    if (sentimentFilter) {
      var s = sentimentLabel(row);
      if (s !== sentimentFilter) return false;
    }
    if (maxFloat != null) {
      var f = cv(row, "float_shares");
      if (f == null || f > maxFloat) return false;
    }
    return true;
  });
}

/* ------------------------------------------------------------------ detail drawer */

function openDetail(symbol) {
  var overlay = el("detail-overlay");
  overlay.hidden = false;
  overlay.style.display = "flex";
  el("drawer-title").textContent = "Loading " + symbol + "...";
  el("drawer-body").textContent = "";
  buildDetail(symbol);
}

function closeDetail() {
  var overlay = el("detail-overlay");
  if (overlay) {
    overlay.hidden = true;
    overlay.style.display = "none";
  }
  state.selected = null;
  renderRows(state.filteredRows || []);
}

function selectSymbol(symbol) {
  state.selected = symbol;
  renderRows(state.filteredRows);
  openDetail(symbol);
}

function fieldLine(label, value, extra) {
  var div = document.createElement("div");
  div.className = "field-line";
  var k = document.createElement("span");
  k.className = "fl-key";
  k.textContent = label;
  var v = document.createElement("span");
  v.className = "fl-value";
  v.textContent = value === null || value === undefined || value === "" ? MISSING : String(value);
  div.appendChild(k);
  div.appendChild(v);
  if (extra) {
    var e = document.createElement("span");
    e.className = "fl-extra";
    e.textContent = " \u00b7 " + extra;
    div.appendChild(e);
  }
  return div;
}

function detailSection(title) {
  var h = document.createElement("h3");
  h.textContent = title;
  return h;
}

function detailGrid(children) {
  var div = document.createElement("div");
  div.className = "detail-grid-2col";
  children.forEach(function (c) { div.appendChild(c); });
  return div;
}

async function buildDetail(symbol) {
  var body = el("drawer-body");
  var title = el("drawer-title");
  body.textContent = "";
  title.textContent = "Loading " + symbol + "...";

  var detail;
  try {
    detail = await getJSON("/api/symbol?symbol=" + encodeURIComponent(symbol) + "&mode=" + state.mode);
  } catch (e) {
    body.appendChild(text(document.createElement("p"), "Unavailable: " + e.message));
    return;
  }

  if (detail.error) {
    body.appendChild(text(document.createElement("p"), detail.error));
    return;
  }

  var id = detail.identity || {};
  var row = state.rows.find(function (r) { return r.symbol === symbol; });
  var cls = row ? classification(row) : "UNEVALUABLE";

  title.textContent = id.symbol;
  if (id.contract && id.contract.long_name) {
    title.textContent += " \u2014 " + id.contract.long_name;
  }

  body.appendChild(detailSection("HEADER"));
  body.appendChild(detailGrid([
    fieldLine("Symbol", id.symbol),
    fieldLine("Price", cv(row || {}, "last"), "USD"),
    fieldLine("Change %", cv(row || {}, "percentage_change") != null ? (cv(row || {}, "percentage_change") >= 0 ? "+" : "") + cv(row || {}, "percentage_change").toFixed(2) + "%" : null),
    fieldLine("Classification", cls.replace(/_/g, " ")),
    fieldLine("Why Listed", (row && row.why_listed || []).join("; ")),
    fieldLine("Updated", ago(row && row.last_updated) || (row && row.last_updated)),
  ]));

  body.appendChild(detailSection("SHORT PRESSURE"));
  body.appendChild(detailGrid([
    fieldLine("Float", cv(row || {}, "float_shares") != null ? Number(cv(row || {}, "float_shares")).toLocaleString() : null),
    fieldLine("Short Float", cv(row || {}, "short_float") != null ? cv(row || {}, "short_float") + "%" : null),
    fieldLine("Days to Cover", cv(row || {}, "days_to_cover")),
    fieldLine("Short Ratio", cv(row || {}, "short_ratio")),
    fieldLine("Borrow Fee", cv(row || {}, "borrow_fee") != null ? cv(row || {}, "borrow_fee") + "%" : null),
  ]));

  body.appendChild(detailSection("IGNITION"));
  body.appendChild(detailGrid([
    fieldLine("Change %", cv(row || {}, "percentage_change") != null ? (cv(row || {}, "percentage_change") >= 0 ? "+" : "") + cv(row || {}, "percentage_change").toFixed(2) + "%" : null),
    fieldLine("Relative Volume", cv(row || {}, "relative_volume")),
    fieldLine("Market Mode", id.market_data_mode || id.data_mode),
  ]));

  var advLink = document.createElement("p");
  var advA = document.createElement("a");
  advA.href = "/advanced";
  advA.textContent = "Open Advanced Analysis";
  advA.style.color = "var(--accent)";
  advA.style.fontWeight = "600";
  advLink.appendChild(advA);
  body.appendChild(advLink);
}

/* ------------------------------------------------------------------ screener */

async function loadAndRender(url, mode) {
  var payload;
  try {
    payload = await getJSON(url);
  } catch (e) {
    return null;
  }
  if (!payload || !payload.rows || !payload.rows.length) return null;

  state.rows = payload.rows || [];
  state.summary = payload.summary || null;
  state.mode = mode;

  var filtered = applyFilters(state.rows);
  state.filteredRows = filtered;
  renderSummary(state.rows);
  renderHead();
  renderRows(filtered);

  // Kick off news feed for current candidates
  startNewsFeed();

  return payload;
}

function startAutoRefresh() {
  if (state.autoTimer) { clearInterval(state.autoTimer); state.autoTimer = null; }
  state.autoTimer = setInterval(function () {
    if (state.mode === "CURRENT") {
      loadLiveScanner().catch(function () {});
    }
  }, 30000);
  el("auto-refresh").checked = true;
}

async function loadScanner() {
  setStatus("Loading scanner...");
  var pct = Date.now();

  // 1. Load frozen data FIRST — always instant, never hangs
  var payload = await loadAndRender("/api/screener?mode=FROZEN_RESEARCH", "FROZEN");

  var ms = Date.now() - pct;
  if (payload) {
    setStatus(state.rows.length + " candidates shown [FROZEN RESEARCH] \u00b7 loaded in " + ms + "ms");
    renderBanner("FROZEN");
    resetRefreshTimer();
  } else {
    setStatus("No data available \u00b7 loaded in " + ms + "ms", true);
    renderRows([]);
    renderHead();
    return;
  }

  // 2. Run discovery + try live data — auto-discovers candidates from IBKR
  try {
    // First, trigger discovery
    setStatus("Discovering live candidates from IBKR scanner...");
    var discResp = await fetch("/api/discovery/refresh", { method: "POST" });
    var discData = await discResp.json().catch(function(){ return {}; });

    if (discData.discovered && discData.discovered > 0) {
      // Sync refresh populates Finviz cache globally + loads IBKR evidence
      setStatus(discData.discovered + " candidates found. Loading data...");
      await fetch("/api/live/refresh", { method: "POST" });
      // Second pass to cycle through more symbols with IBKR evidence
      await fetch("/api/live/refresh", { method: "POST" });
      await fetch("/api/live/refresh", { method: "POST" });
    }

    // Now try live screener
    var controller = new AbortController();
    var timeout = setTimeout(function () { controller.abort(); }, 15000);
    var resp = await fetch("/api/screener?mode=CURRENT", { signal: controller.signal });
    clearTimeout(timeout);
    if (resp.ok) {
      var live = await resp.json();
      if (live && live.rows && live.rows.length) {
        state.rows = live.rows;
        state.summary = live.summary || null;
        state.mode = "CURRENT";
        state.filteredRows = applyFilters(state.rows);
        renderSummary(state.rows);
        renderHead();
        renderRows(state.filteredRows);
        updateModeUI("CURRENT");
        renderBanner("CURRENT");
        startNewsFeed();
        resetRefreshTimer();
        setStatus(state.rows.length + " candidates shown [LIVE] \u00b7 " + (Date.now() - pct) + "ms");
        startAutoRefresh();
        el("auto-refresh").checked = true;
      } else {
        setStatus("Discovery complete but no live candidates matched. Showing frozen research.");
      }
    }
  } catch (e) {
    setStatus("Live discovery unavailable: " + (e.message || "timeout") + ". Showing frozen research.");
  }

  // 3. Load provider status bar
  loadProviderStatus();
}

async function refreshNow() {
  if (state.mode === "CURRENT") {
    refreshLive();
  } else {
    setStatus("Refreshing evidence...");
    loadScanner();
  }
}

async function refreshLive() {
  setStatus("Discovering + refreshing live evidence...");
  try {
    await fetch("/api/discovery/refresh", { method: "POST" });
    await fetch("/api/live/refresh", { method: "POST" });
  } catch (e) {
    // Continue anyway
  }
  await loadLiveScanner();
}

async function loadLiveScanner() {
  setStatus("Loading live scanner data...");
  var pct = Date.now();
  try {
    var resp = await fetch("/api/screener?mode=CURRENT");
    if (resp.ok) {
      var live = await resp.json();
      if (live && live.rows && live.rows.length) {
        state.rows = live.rows;
        state.summary = live.summary || null;
        state.mode = "CURRENT";
        state.filteredRows = applyFilters(state.rows);
        renderSummary(state.rows);
        renderHead();
        renderRows(state.filteredRows);
        updateModeUI("CURRENT");
        renderBanner("CURRENT");
        startNewsFeed();
        resetRefreshTimer();
        setStatus(state.rows.length + " candidates [LIVE] \u00b7 " + (Date.now() - pct) + "ms");
        startAutoRefresh();
        return;
      }
    }
    setStatus("Live mode ready but no candidates found. Click Refresh to re-scan.", true);
  } catch (e) {
    setStatus("Live data unavailable: " + (e.message || "error"), true);
  }
}

async function loadFrozenScanner() {
  setStatus("Loading frozen research...");
  var pct = Date.now();
  try {
    var payload = await getJSON("/api/screener?mode=FROZEN_RESEARCH");
    state.rows = payload.rows || [];
    state.summary = payload.summary || null;
    state.mode = "FROZEN";
    state.filteredRows = applyFilters(state.rows);
    renderSummary(state.rows);
    renderHead();
    renderRows(state.filteredRows);
    updateModeUI("FROZEN");
    renderBanner("FROZEN");
    startNewsFeed();
    resetRefreshTimer();
    setStatus(state.rows.length + " candidates [FROZEN] \u00b7 " + (Date.now() - pct) + "ms");
    if (state.autoTimer) { clearInterval(state.autoTimer); state.autoTimer = null; }
    el("auto-refresh").checked = false;
  } catch (e) {
    setStatus("Frozen research unavailable: " + e.message, true);
  }
}

function updateModeUI(mode) {
  var frozenBtn = el("btn-mode-frozen");
  var liveBtn = el("btn-mode-live");
  var indicator = el("mode-indicator");
  if (frozenBtn) frozenBtn.classList.toggle("active", mode === "FROZEN");
  if (liveBtn) liveBtn.classList.toggle("active", mode === "CURRENT");
  if (indicator) {
    if (mode === "CURRENT") {
      indicator.textContent = "\u26a1 LIVE";
      indicator.style.color = "#56d68b";
    } else {
      indicator.textContent = "\u2744 FROZEN";
      indicator.style.color = "#6fa8ff";
    }
  }
}

function switchMode(mode) {
  if (mode === "CURRENT") {
    loadLiveScanner();
  } else {
    loadFrozenScanner();
  }
}

async function setAutoRefresh(enabled) {
  try {
    var params = new URLSearchParams({ enabled: enabled ? "true" : "false" });
    await getJSON("/api/live/auto?" + params.toString(), { method: "POST" });
  } catch (e) {
    setStatus("Auto refresh error: " + e.message, true);
  }
  if (state.autoTimer) { clearInterval(state.autoTimer); state.autoTimer = null; }
  if (enabled) {
    state.autoTimer = setInterval(function () { loadScanner(); }, 30000);
  }
  renderRefreshClock();
}

function renderRefreshClock() {
  var node = el("refresh-clock");
  var summary = state.summary;
  if (!summary) { node.textContent = ""; return; }
  var bits = [];
  var lastAt = summary.last_refresh_at;
  if (lastAt) bits.push("Last: " + ago(lastAt));
  if (summary.auto_refresh) bits.push("auto on");
  else bits.push("auto off");
  node.textContent = bits.join(" \u00b7 ");
}

/* ------------------------------------------------------------------ provider status bar */

async function loadProviderStatus() {
  try {
    var caps = await getJSON("/api/capabilities");
    renderProviderBar(caps);
  } catch (e) {
    // Silently skip
  }
}

function renderProviderBar(caps) {
  var bar = el("provider-bar");
  if (!bar) return;
  bar.textContent = "";

  var providers = caps.providers || {};
  var entries = ["IBKR", "Finviz Elite", "NewsAPI", "Finnhub", "SEC_EDGAR", "Finnhub News"];

  entries.forEach(function (id) {
    var info = providers[id] || {};
    var configured = info.configured;
    var connected = info.connected;
    var span = document.createElement("span");
    span.className = "provider-dot";

    var color, label;
    if (connected) {
      color = "#56d68b";
      label = id + " LIVE";
      span.title = (info.detail || "").substring(0, 200);
    } else if (configured) {
      color = "#ffca57";
      label = id + " standby";
      span.title = (info.detail || "Configured, not yet connected").substring(0, 200);
    } else {
      color = "#8b98a9";
      label = id + " off";
      span.title = (info.detail || "Not configured").substring(0, 200);
    }

    span.style.cssText = "display:inline-block;margin:0 8px;font-size:11px;color:" + color + ";font-family:monospace";
    var dot = document.createElement("span");
    dot.style.cssText = "display:inline-block;width:6px;height:6px;border-radius:50%;background:" + color + ";margin-right:3px;vertical-align:middle";
    span.appendChild(dot);
    span.appendChild(document.createTextNode(" " + label));
    bar.appendChild(span);
  });

  bar.style.cssText = "padding:4px 16px;border-bottom:1px solid #1e2d4a;background:#0d1525;font-size:11px";
}

/* ------------------------------------------------------------------ news feed */

var newsFeedTimer = null;
var newsFeedSymbols = [];
var newsFeedFilter = "";
const NEWS_FEED_INTERVAL = 60000;
const NEWS_FEED_MAX_ITEMS = 30;

/* ------------------------------------------------------------------ live countdown timer */

var lastRefreshTime = Date.now();
var countdownTimer = null;

function resetRefreshTimer() {
  lastRefreshTime = Date.now();
  updateTimerDisplay();
  if (!countdownTimer) {
    countdownTimer = setInterval(updateTimerDisplay, 1000);
  }
}

function updateTimerDisplay() {
  var elapsed = Math.floor((Date.now() - lastRefreshTime) / 1000);
  var text = el("timer-text");
  var dot = el("timer-dot");
  if (!text) return;
  if (elapsed < 60) {
    text.textContent = elapsed + "s ago";
  } else if (elapsed < 3600) {
    text.textContent = Math.floor(elapsed / 60) + "m " + (elapsed % 60) + "s ago";
  } else {
    text.textContent = Math.floor(elapsed / 3600) + "h ago";
  }
  // Dot pulses faster as data gets older
  if (dot) {
    if (elapsed < 15) dot.style.background = "#56d68b";
    else if (elapsed < 60) dot.style.background = "#ffca57";
    else dot.style.background = "#ff7d7d";
  }
}

function refreshNewsFeed() {
  if (!state.rows || !state.rows.length) { renderNewsFeed([]); return; }

  // Single request to aggregated endpoint — one call instead of N
  var param = newsFeedFilter ? "classification=" + encodeURIComponent(newsFeedFilter) + "&" : "";
  var url = "/api/news/feed?" + param + "limit=" + NEWS_FEED_MAX_ITEMS;

  getJSON(url).then(function (data) {
    if (!data || !data.headlines) { renderNewsFeed([]); return; }
    newsFeedSymbols = data.symbols || [];
    renderNewsFeed(data.headlines);
    updatePillCounts(data.counts || {});
  }).catch(function () {
    renderNewsFeed([]);
  });
}

function renderNewsFeed(headlines) {
  var list = el("news-feed-list");
  var updated = el("news-feed-updated");
  if (!list) return;

  list.textContent = "";
  updated.textContent = new Date().toLocaleTimeString();

  if (!headlines.length) {
    var empty = document.createElement("div");
    empty.className = "news-feed-empty";
    empty.textContent = newsFeedSymbols.length
      ? "No recent headlines for tracked symbols."
      : "Awaiting candidate data…";
    list.appendChild(empty);
    return;
  }

  headlines.forEach(function (item) {
    var row = document.createElement("div");
    row.className = "news-feed-item";
    if (item.url) {
      row.style.cursor = "pointer";
      row.addEventListener("click", function () { window.open(item.url, "_blank"); });
    }

    // Symbol badge
    var badge = document.createElement("span");
    badge.className = "nf-symbol";
    var cls = item.classification || "UNEVALUABLE";
    if (cls === "PRIME") badge.classList.add("sym-PRIME");
    else if (cls === "SUBPRIME") badge.classList.add("sym-SUBPRIME");
    else if (cls === "WATCH") badge.classList.add("sym-WATCH");
    else badge.classList.add("sym-default");
    badge.textContent = item.symbol;
    row.appendChild(badge);

    // Headline text
    var headlineSpan = document.createElement("span");
    headlineSpan.className = "nf-headline";
    headlineSpan.textContent = item.headline.length > 110
      ? item.headline.substring(0, 107) + "..."
      : item.headline;
    if (item.headline.length > 110) headlineSpan.title = item.headline;
    row.appendChild(headlineSpan);

    // Time and source line
    var meta = document.createElement("span");
    meta.className = "nf-time";
    var metaParts = [];
    if (item.time) metaParts.push(ago(item.time));
    if (item.source) metaParts.push(item.source);
    meta.textContent = metaParts.join(" \u00b7 ");
    row.appendChild(meta);

    list.appendChild(row);
  });
}

function startNewsFeed() {
  if (newsFeedTimer) { clearInterval(newsFeedTimer); newsFeedTimer = null; }
  refreshNewsFeed();
  newsFeedTimer = setInterval(refreshNewsFeed, NEWS_FEED_INTERVAL);
}

/* ------------------------------------------------------------------ news feed toggle pills */

function updatePillCounts(counts) {
  var toggles = el("news-feed-toggles");
  if (!toggles) return;
  var total = Object.values(counts).reduce(function (a, b) { return a + b; }, 0);
  toggles.querySelectorAll(".nf-pill").forEach(function (pill) {
    var filter = pill.getAttribute("data-nf-filter") || "";
    var n = filter ? (counts[filter] || 0) : total;
    var label = pill.textContent.replace(/\s*\(\d+\)\s*$/, "");
    pill.innerHTML = label + ' <span class="nf-count">(' + n + ')</span>';
  });
}

function setupNewsFeedToggles() {
  var toggles = el("news-feed-toggles");
  if (!toggles) return;
  toggles.addEventListener("click", function (e) {
    var pill = e.target.closest(".nf-pill");
    if (!pill) return;
    e.preventDefault();

    // Update active state
    toggles.querySelectorAll(".nf-pill").forEach(function (p) {
      p.classList.remove("active");
    });
    pill.classList.add("active");

    // Update filter and refresh
    newsFeedFilter = pill.getAttribute("data-nf-filter") || "";
    refreshNewsFeed();
  });
}

/* ------------------------------------------------------------------ init */

function init() {
  el("btn-refresh-now").addEventListener("click", refreshNow);
  el("auto-refresh").addEventListener("change", function (e) { setAutoRefresh(e.target.checked); });
  el("btn-close-detail").addEventListener("click", closeDetail);
  el("detail-overlay").addEventListener("click", function (e) {
    if (e.target === el("detail-overlay")) closeDetail();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeDetail();
  });

  // Mode toggle buttons
  var frozenBtn = el("btn-mode-frozen");
  var liveBtn = el("btn-mode-live");
  if (frozenBtn) frozenBtn.addEventListener("click", function () { switchMode("FROZEN"); });
  if (liveBtn) liveBtn.addEventListener("click", function () { switchMode("CURRENT"); });

  var filterIds = [
    "filter-classification", "filter-symbol", "filter-min-price", "filter-max-price",
    "filter-min-change", "filter-min-relvol", "filter-min-pressure", "filter-min-ignition",
    "filter-min-coverage", "filter-news", "filter-sentiment", "filter-max-float",
  ];
  filterIds.forEach(function (id) {
    var node = el(id);
    if (!node) return;
    node.addEventListener(id === "filter-symbol" ? "input" : "change", function () {
      state.filteredRows = applyFilters(state.rows);
      renderHead();
      renderRows(state.filteredRows);
    });
  });

  // Start with frozen (instant), then auto-discover live
  loadScanner();
  setupNewsFeedToggles();
  loadProviderStatus();
}

document.addEventListener("DOMContentLoaded", init);
