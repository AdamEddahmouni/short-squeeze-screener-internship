"use strict";

const state = {
  rows: [],
  filteredRows: [],
  selected: null,
  summary: null,
  providerCaps: null,
  autoTimer: null,
  sortKey: null,
  sortDesc: false,
  mode: "FROZEN",
  triageFilter: "",
  blockerFilter: null,
  blockerOpen: false,
  newsPanelMode: "default",
  newsMeta: null,
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

function isEvaluable(row) {
  var c = classification(row);
  return c !== "UNEVALUABLE" && c !== "CONFLICTED";
}

function hasMissingCoreShortInterest(row) {
  var core = ["short_float", "days_to_cover", "borrow_fee"];
  return core.some(function (name) {
    var field = cf(row, name);
    return !field || field.status !== "KNOWN";
  });
}

function isInsufficient(row) {
  var cov = coveragePct(row);
  return cov == null || cov < 40 || row.pressure == null || row.ignition == null;
}

function dataQuality(row) {
  return row && row.data_quality ? row.data_quality : {};
}

function bucketCountForRow(row, bucket) {
  var buckets = dataQuality(row).missing_evidence_buckets || [];
  for (var i = 0; i < buckets.length; i += 1) {
    if (buckets[i] && buckets[i].bucket === bucket) {
      return Number(buckets[i].missing_field_count || 0);
    }
  }
  return 0;
}

function hasCause(row, cause) {
  var causes = dataQuality(row).cause_summaries || [];
  return causes.indexOf(cause) !== -1;
}

function missingLabel(field, fallbackLabel) {
  if (!field) {
    return { label: fallbackLabel || "Missing", tip: "No evidence cell returned." };
  }
  if (field.status === "KNOWN") return null;
  var code = String(field.missing_reason_code || "").toUpperCase();
  var reason = String(field.missing_reason || "");
  var reasonLower = reason.toLowerCase();
  var label = field.status.replace(/_/g, " ");
  if (field.status === "NOT_CONFIGURED") {
    if (reasonLower.indexOf("not connected") !== -1 || reasonLower.indexOf("disconnected") !== -1) label = "Provider disconnected";
    else if (code.indexOf("NOT_AVAILABLE") !== -1 || code.indexOf("NOT_CONFIGURED") !== -1) label = "Field not published";
    else label = "Not configured";
  } else if (field.status === "UNAVAILABLE") {
    label = "Permission unavailable";
  } else if (field.status === "UNKNOWN") {
    if (code.indexOf("NO_BARS") !== -1 || code.indexOf("STALE") !== -1) label = "Stale snapshot";
    else label = "Awaiting ticks";
  } else if (field.status === "NOT_COLLECTED") {
    label = "Not collected";
  } else if (field.status === "BLOCKED") {
    label = "Blocked";
  }
  var bits = [];
  bits.push("Status: " + field.status);
  if (field.missing_reason) bits.push(field.missing_reason);
  if (field.missing_reason_code) bits.push("Code: " + field.missing_reason_code);
  if (field.provider) bits.push("Provider: " + field.provider);
  return { label: label, tip: bits.join(" \u00b7 ") };
}

function appendMissingLabel(td, field, fallbackLabel) {
  var m = missingLabel(field, fallbackLabel);
  if (!m) return false;
  var span = document.createElement("span");
  span.className = "muted";
  span.textContent = m.label;
  if (m.tip) span.title = m.tip;
  td.appendChild(span);
  return true;
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
  { label: "DAYS TO COVER", key: "days_to_cover", sortable: true, secondary: true },
  { label: "BORROW", key: "borrow", sortable: true, secondary: true },
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
      appendMissingLabel(td, null, "Insufficient inputs");
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
      var sentField = cf(row, "sentiment");
      sentSpan.textContent = (missingLabel(sentField, "No sentiment") || {}).label || "No sentiment";
      sentSpan.className = "muted";
      sentSpan.title = sentField && sentField.missing_reason ? sentField.missing_reason : "";
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
      appendMissingLabel(td, cf(row, "news_count"), "No headlines");
      td.className = td.className + " muted";
      return td;
    }
    td.textContent = value;
    return td;
  }

  if (col.key === "percentage_change") {
    if (value == null) {
      appendMissingLabel(td, cf(row, "percentage_change"), "No return data");
      td.className = td.className + " muted";
      return td;
    }
    var changeColor = value >= 0 ? "#56d68b" : "#ff7d7d";
    td.textContent = (value >= 0 ? "+" : "") + value.toFixed(2) + "%";
    td.style.color = changeColor;
    td.style.fontWeight = "700";
    return td;
  }

  if (col.key === "borrow") {
    if (value == null) {
      appendMissingLabel(td, cf(row, "borrow_fee") || cf(row, "shortable"), "No borrow data");
      td.className = td.className + " muted";
      return td;
    }
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
    appendMissingLabel(td, cf(row, col.key), "Missing");
    td.className = td.className + " muted";
    return td;
  }

  td.textContent = typeof value === "number" ? Number(value).toLocaleString() : String(value);
  return td;
}

var SORT_DESC_FIRST_KEYS = [
  "percentage_change", "pressure", "ignition", "relative_volume",
  "short_float", "days_to_cover", "news",
];

var CLASSIFICATION_SORT_ORDER = {
  PRIME: 0, SUBPRIME: 1, WATCH: 2, CONFLICTED: 3, NOT_QUALIFIED: 4, UNEVALUABLE: 5,
};

var SENTIMENT_SORT_ORDER = {
  POSITIVE: 0, MIXED: 1, NEUTRAL: 2, NEGATIVE: 3,
};

function sortValueFor(row, key) {
  if (key === "updated") {
    var ts = row.last_updated ? Date.parse(row.last_updated) : NaN;
    return Number.isFinite(ts) ? ts : null;
  }
  if (key === "classification") {
    var cls = classification(row);
    return CLASSIFICATION_SORT_ORDER[cls] != null ? CLASSIFICATION_SORT_ORDER[cls] : 9;
  }
  if (key === "sentiment") {
    var label = sentimentLabel(row);
    if (!label) return null;
    return SENTIMENT_SORT_ORDER[label] != null ? SENTIMENT_SORT_ORDER[label] : 9;
  }
  return valueFor(row, key);
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
          if (state.sortDesc) {
            state.sortKey = null;
            state.sortDesc = false;
          } else {
            state.sortDesc = true;
          }
        } else {
          state.sortKey = col.key;
          state.sortDesc = SORT_DESC_FIRST_KEYS.indexOf(col.key) !== -1;
        }
        renderHead();
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
    var v = sortValueFor(row, key);
    if (v == null || v === undefined) missing.push(row);
    else known.push(row);
  });
  known.sort(function (a, b) {
    var av = sortValueFor(a, key);
    var bv = sortValueFor(b, key);
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
    return (order[aCls] || 9) - (order[bCls] || 9)
      || ((b.pressure || 0) + (b.ignition || 0)) - ((a.pressure || 0) + (a.ignition || 0));
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
  var showClassDividers = !state.sortKey || state.sortKey === "classification";

  rows.forEach(function (row, idx) {
    var cls = classification(row);

    if (showClassDividers && cls !== prevCls) {
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
  renderReadiness(rows);
  renderDataQuality(rows);
  renderTriageFilters(rows);
  renderBlockerPanel(rows);
}

function renderReadiness(rows) {
  var transportNode = el("transport-ready");
  var classNode = el("classification-ready");
  if (!transportNode || !classNode) return;
  var summaryProviders = (state.summary && state.summary.providers) || {};
  var providers = Object.keys(summaryProviders).length
    ? summaryProviders
    : ((state.providerCaps && state.providerCaps.providers) || {});
  var providerIds = Object.keys(providers);
  var connectedCount = providerIds.filter(function (id) {
    var provider = providers[id] || {};
    return !!(provider.connected || provider.connection_ready);
  }).length;
  var transportReady = state.mode === "CURRENT" && connectedCount > 0;
  transportNode.textContent = transportReady ? "TRANSPORT LIVE" : "TRANSPORT LIMITED";
  transportNode.className = "ready-badge " + (transportReady ? "ok" : "none");
  transportNode.title = transportReady
    ? connectedCount + " providers connected."
    : "Live data path is not confirmed. Connected providers: " + connectedCount + ".";

  var readiness = (state.summary && state.summary.readiness) || null;
  var evaluable = readiness
    ? Number(readiness.actionable_candidate_count || 0)
    : rows.filter(isEvaluable).length;
  var candidateCount = readiness
    ? Number(readiness.candidate_count || rows.length)
    : rows.length;
  var ratio = candidateCount ? Math.round((evaluable / candidateCount) * 100) : 0;
  var classReady = evaluable > 0;
  classNode.textContent = classReady ? "CLASSIFICATION READY" : "CLASSIFICATION BLOCKED";
  classNode.className = "ready-badge " + (classReady ? "ok" : "bad");
  classNode.title = evaluable + "/" + candidateCount + " evaluable candidates (" + ratio + "%).";
}

function renderDataQuality(rows) {
  var strip = el("data-quality-strip");
  if (!strip) return;
  strip.textContent = "";
  if (!rows.length) return;

  var readiness = (state.summary && state.summary.readiness) || null;
  var candidateCount = readiness ? Number(readiness.candidate_count || rows.length) : rows.length;
  var actionableCount = readiness ? Number(readiness.actionable_candidate_count || 0) : rows.filter(isEvaluable).length;
  var unevaluableCount = readiness ? Number(readiness.unevaluable_candidate_count || 0) : rows.filter(function (row) { return classification(row) === "UNEVALUABLE"; }).length;
  var staleRows = rows.filter(function (row) { return !!row.stale; });
  var insufficientRows = rows.filter(isInsufficient);
  var missingCoreRows = rows.filter(hasMissingCoreShortInterest);

  var chips = [
    { text: "Evaluable " + actionableCount + "/" + candidateCount },
    { text: "Stale " + staleRows.length, tone: staleRows.length ? "warn" : "" },
    { text: "Insufficient " + insufficientRows.length, tone: insufficientRows.length ? "warn" : "" },
    { text: "Missing core SI " + missingCoreRows.length, tone: missingCoreRows.length ? "bad" : "" },
  ];
  if (unevaluableCount) {
    chips.push({
      text: "UNEVALUABLE " + unevaluableCount,
      tone: "bad",
      title: buildUnevaluableDiagnostics(rows),
    });
  }

  chips.forEach(function (chip) {
    var span = document.createElement("span");
    span.className = "quality-chip" + (chip.tone ? " " + chip.tone : "");
    span.textContent = chip.text;
    if (chip.title) span.title = chip.title;
    strip.appendChild(span);
  });
}

function buildUnevaluableDiagnostics(rows) {
  var readiness = (state.summary && state.summary.readiness) || null;
  if (readiness && (readiness.top_unevaluable_causes || []).length) {
    return ["Top UNEVALUABLE causes (backend):"]
      .concat(readiness.top_unevaluable_causes.map(function (item) {
        return item.cause + ": " + item.candidate_count;
      }))
      .join("\n");
  }
  return "UNEVALUABLE diagnostics are unavailable in summary.readiness.";
}

function renderBanner(mode) {
  var banners = el("banners");
  banners.textContent = "";
  if (mode === "FROZEN") {
    var b = document.createElement("div");
    b.className = "alert alert-info";
    b.style.cssText = "background:#1a2740;color:#6fa8ff;padding:8px 16px;border-left:3px solid #6fa8ff;margin:8px 0;font-size:13px";
    b.innerHTML = "<strong>FROZEN RESEARCH MODE</strong> &mdash; Showing pre-computed research cases. Live market discovery unavailable on this deployment.";
    banners.appendChild(b);
  }
  // In live mode (or empty string), no banner — clean interface for Railway
}

function renderTriageFilters(rows) {
  var wrap = el("triage-filters");
  if (!wrap) return;
  wrap.textContent = "";
  var defs = [
    { id: "", label: "All", count: rows.length },
    { id: "evaluable", label: "Evaluable", count: rows.filter(isEvaluable).length },
    { id: "stale", label: "Stale", count: rows.filter(function (row) { return !!row.stale; }).length },
    { id: "insufficient", label: "Insufficient", count: rows.filter(isInsufficient).length },
    { id: "missing_core_si", label: "Missing Core SI", count: rows.filter(hasMissingCoreShortInterest).length },
  ];
  defs.forEach(function (def) {
    var btn = document.createElement("button");
    btn.className = "triage-btn" + (state.triageFilter === def.id ? " active" : "");
    btn.type = "button";
    btn.setAttribute("data-triage", def.id);
    btn.textContent = def.label + " (" + def.count + ")";
    wrap.appendChild(btn);
  });
}

function aggregateRowBlockers(rows) {
  var causeCounts = {};
  var bucketCounts = {};
  rows.forEach(function (row) {
    var dq = dataQuality(row);
    (dq.cause_summaries || []).forEach(function (cause) {
      causeCounts[cause] = (causeCounts[cause] || 0) + 1;
    });
    (dq.missing_evidence_buckets || []).forEach(function (bucketItem) {
      var key = bucketItem.bucket;
      if (!key) return;
      bucketCounts[key] = (bucketCounts[key] || 0) + Number(bucketItem.missing_field_count || 0);
    });
  });
  var causes = Object.keys(causeCounts).map(function (key) {
    return { key: key, count: causeCounts[key] };
  }).sort(function (a, b) { return b.count - a.count || a.key.localeCompare(b.key); });
  var buckets = Object.keys(bucketCounts).map(function (key) {
    return { key: key, count: bucketCounts[key] };
  }).sort(function (a, b) { return b.count - a.count || a.key.localeCompare(b.key); });
  return { causes: causes, buckets: buckets };
}

function renderBlockerPanel(rows) {
  var content = el("blocker-content");
  var toggle = el("blocker-toggle");
  if (!content || !toggle) return;
  toggle.setAttribute("aria-expanded", state.blockerOpen ? "true" : "false");
  content.hidden = !state.blockerOpen;
  content.textContent = "";
  if (!state.blockerOpen) return;

  var agg = aggregateRowBlockers(rows);
  if (!agg.causes.length && !agg.buckets.length) {
    var empty = document.createElement("span");
    empty.className = "muted";
    empty.textContent = "No blocker diagnostics available.";
    content.appendChild(empty);
    return;
  }

  function buildGroup(title, type, items) {
    var group = document.createElement("div");
    group.className = "blocker-group";
    var heading = document.createElement("p");
    heading.className = "blocker-group-title";
    heading.textContent = title;
    group.appendChild(heading);

    var list = document.createElement("div");
    list.className = "blocker-list";
    items.forEach(function (item) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "blocker-chip";
      if (state.blockerFilter && state.blockerFilter.type === type && state.blockerFilter.key === item.key) {
        btn.classList.add("active");
      }
      btn.setAttribute("data-blocker-type", type);
      btn.setAttribute("data-blocker-key", item.key);
      btn.textContent = item.key + " (" + item.count + ")";
      list.appendChild(btn);
    });
    group.appendChild(list);
    return group;
  }

  content.appendChild(buildGroup("Cause Summaries", "cause", agg.causes));
  content.appendChild(buildGroup("Missing Buckets", "bucket", agg.buckets));
  if (state.blockerFilter) {
    var clearBtn = document.createElement("button");
    clearBtn.type = "button";
    clearBtn.className = "blocker-chip blocker-chip-clear";
    clearBtn.setAttribute("data-blocker-clear", "1");
    clearBtn.textContent = "Clear blocker filter";
    content.appendChild(clearBtn);
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
      var p = valueFor(row, "price");
      if (p == null || p < minPrice) return false;
    }
    if (maxPrice != null) {
      var p2 = valueFor(row, "price");
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
    if (state.triageFilter === "evaluable" && !isEvaluable(row)) return false;
    if (state.triageFilter === "stale" && !row.stale) return false;
    if (state.triageFilter === "insufficient" && !isInsufficient(row)) return false;
    if (state.triageFilter === "missing_core_si" && !hasMissingCoreShortInterest(row)) return false;
    if (state.blockerFilter) {
      if (state.blockerFilter.type === "cause" && !hasCause(row, state.blockerFilter.key)) return false;
      if (state.blockerFilter.type === "bucket" && bucketCountForRow(row, state.blockerFilter.key) <= 0) return false;
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
    fieldLine("Borrow Fee", cv(row || {}, "borrow_fee") != null ? cv(row || {}, "borrow_fee") + "%" : null),
  ]));

  body.appendChild(detailSection("IGNITION"));
  body.appendChild(detailGrid([
    fieldLine("Change %", cv(row || {}, "percentage_change") != null ? (cv(row || {}, "percentage_change") >= 0 ? "+" : "") + cv(row || {}, "percentage_change").toFixed(2) + "%" : null),
    fieldLine("Relative Volume", cv(row || {}, "relative_volume")),
    fieldLine("Market Mode", id.market_data_mode || id.data_mode),
  ]));

  var headlines = Array.isArray(detail.news) ? detail.news : [];
  if (!headlines.length) {
    var newsPayload = await getCachedNews(symbol);
    if (newsPayload && Array.isArray(newsPayload.headlines)) {
      headlines = newsPayload.headlines;
    }
  }
  body.appendChild(detailSection("NEWS"));
  var newsWrap = document.createElement("div");
  newsWrap.className = "detail-news-list";
  if (!headlines.length) {
    newsWrap.appendChild(text(document.createElement("p"), "No headlines available."));
    newsWrap.classList.add("muted");
  } else {
    headlines.slice(0, 12).forEach(function (item) {
      var line = document.createElement("div");
      line.className = "news-headline-line";
      var title = item.headline || item.title || "";
      if (item.url) {
        var link = document.createElement("a");
        link.href = item.url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = title;
        line.appendChild(link);
      } else {
        line.textContent = title;
      }
      if (item.timestamp) {
        var meta = document.createElement("span");
        meta.className = "muted";
        meta.style.marginLeft = "8px";
        meta.textContent = ago(item.timestamp) || item.timestamp;
        line.appendChild(meta);
      }
      newsWrap.appendChild(line);
    });
  }
  body.appendChild(newsWrap);

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

  // 1. Render frozen instantly so the page isn't blank — but DON'T show the frozen banner
  var frozenPromise = loadAndRender("/api/screener?mode=FROZEN_RESEARCH", "FROZEN");

  // 2. In parallel, run live discovery — this populates the session asynchronously
  var livePromise = (async function () {
    try {
      var discResp = await fetch("/api/discovery/refresh", { method: "POST" });
      var discData = await discResp.json().catch(function(){ return {}; });
      if (discData.discovered && discData.discovered > 0) {
        await fetch("/api/live/refresh", { method: "POST" });
      }
      var controller = new AbortController();
      var timeout = setTimeout(function () { controller.abort(); }, 15000);
      var resp = await fetch("/api/screener?mode=CURRENT", { signal: controller.signal });
      clearTimeout(timeout);
      if (resp.ok) {
        var live = await resp.json();
        if (live && live.rows && live.rows.length) {
          return { ok: true, data: live };
        }
      }
      return { ok: false, reason: "No live candidates returned from screener" };
    } catch (e) {
      return { ok: false, reason: (e.message || "error") };
    }
  })();

  // 3. Wait for frozen to render first so user sees data instantly
  var frozenPayload = await frozenPromise;
  if (frozenPayload) {
    setStatus("Frozen ready \u00b7 discovering live candidates...");
    resetRefreshTimer();
  } else {
    setStatus("Awaiting data...", true);
    renderRows([]);
    renderHead();
  }

  // 4. Now wait for live to finish — if it succeeded, swap in live data
  var liveResult = await livePromise;
  if (liveResult.ok && liveResult.data) {
    state.rows = liveResult.data.rows;
    state.summary = liveResult.data.summary || null;
    state.mode = "CURRENT";
    state.filteredRows = applyFilters(state.rows);
    renderSummary(state.rows);
    renderHead();
    renderRows(state.filteredRows);
    updateModeUI("CURRENT");
    renderBanner("");
    startNewsFeed();
    resetRefreshTimer();
    setStatus(state.rows.length + " candidates [LIVE] \u00b7 " + (Date.now() - pct) + "ms");
    startAutoRefresh();
    el("auto-refresh").checked = true;
  } else {
    // Live didn't produce rows — keep frozen visible with a clean banner
    if (frozenPayload) {
      renderBanner("FROZEN");
      var ms = Date.now() - pct;
      setStatus(state.rows.length + " candidates [FROZEN] \u00b7 " + ms + "ms \u00b7 live: " + (liveResult.reason || "unavailable"));
    }
  }

  // 5. Load provider status bar
  loadProviderStatus();
  loadCadenceStatus();
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
  var cadence = state.cadence;
  if (cadence && cadence.discovery) {
    var disc = cadence.discovery;
    var cap = disc.target_screen_cap || disc.current_screen_cap;
    if (cap) {
      bits.push((disc.candidate_count || 0) + "/" + cap + " screen");
    }
    if (disc.estimated_full_sweep_minutes) {
      bits.push("~ " + disc.estimated_full_sweep_minutes + "m IBKR sweep");
    }
  }
  node.textContent = bits.join(" \u00b7 ");
}

async function loadCadenceStatus() {
  try {
    state.cadence = await getJSON("/api/discovery/cadence");
    renderRefreshClock();
  } catch (e) {
    // optional status hint
  }
}

/* ------------------------------------------------------------------ provider status bar */

async function loadProviderStatus() {
  try {
    var caps = await getJSON("/api/capabilities");
    state.providerCaps = caps;
    renderProviderBar(caps);
    renderReadiness(state.rows || []);
    renderNewsFeedHealth();
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
    state.newsMeta = {
      scanned: data.symbols_scanned || 0,
      fetched: data.symbols_fetched || 0,
      lastSuccessAt: new Date().toISOString(),
      lastError: "",
    };
    renderNewsFeed(data.headlines);
    updatePillCounts(data.counts || {});
    renderNewsFeedHealth();
  }).catch(function () {
    state.newsMeta = state.newsMeta || {};
    state.newsMeta.lastError = "News request failed.";
    renderNewsFeed([]);
    renderNewsFeedHealth();
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
    var meta = state.newsMeta || {};
    if (!newsFeedSymbols.length) {
      empty.textContent = "Awaiting candidate data before requesting headlines.";
    } else if (meta.scanned && meta.fetched === 0) {
      empty.textContent = "Providers returned no headlines for scanned candidates.";
    } else {
      empty.textContent = "No recent headlines for tracked symbols.";
    }
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

function renderNewsFeedHealth() {
  var node = el("news-feed-health");
  if (!node) return;
  var providers = (state.providerCaps && state.providerCaps.providers) || {};
  var newsApi = providers.NewsAPI || {};
  var finnhubNews = providers["Finnhub News"] || {};
  var bits = [];
  if (newsApi.connected || finnhubNews.connected) bits.push("provider live");
  else if (newsApi.configured || finnhubNews.configured) bits.push("provider standby");
  else bits.push("provider off");
  if (state.newsMeta && state.newsMeta.scanned != null) {
    bits.push("scanned " + state.newsMeta.scanned);
  }
  if (state.newsMeta && state.newsMeta.fetched != null) {
    bits.push("with headlines " + state.newsMeta.fetched);
  }
  if (state.newsMeta && state.newsMeta.lastSuccessAt) {
    bits.push("last fetch " + ago(state.newsMeta.lastSuccessAt));
  }
  if (state.newsMeta && state.newsMeta.lastError) {
    bits.push(state.newsMeta.lastError);
  }
  node.textContent = bits.join(" \u00b7 ");
}

function refreshCollectorsHealth() {
  var node = el("collectors-health");
  if (!node) return;
  getJSON("/api/collectors/status").then(function (payload) {
    var data = (payload && payload.data) || payload || {};
    var bits = [];
    var configured = (data.collectors || []).filter(function (c) { return c.configured; });
    bits.push(configured.length + " collectors active");
    bits.push(data.running ? "scheduler on" : "scheduler idle");
    if (data.last_tick_at) bits.push("last tick " + ago(data.last_tick_at));
    if (data.symbols_last_tick && data.symbols_last_tick.length) {
      bits.push("touched " + data.symbols_last_tick.length);
    }
    if (data.top_gap_bucket) bits.push("gap " + data.top_gap_bucket);
    node.textContent = bits.join(" \u00b7 ");
  }).catch(function () {
    node.textContent = "collectors status unavailable";
  });
}

function startCollectorsHealth() {
  refreshCollectorsHealth();
  if (state.collectorTimer) { clearInterval(state.collectorTimer); }
  state.collectorTimer = setInterval(refreshCollectorsHealth, 45000);
}

function startNewsFeed() {
  if (newsFeedTimer) { clearInterval(newsFeedTimer); newsFeedTimer = null; }
  refreshNewsFeed();
  newsFeedTimer = setInterval(refreshNewsFeed, NEWS_FEED_INTERVAL);
  startCollectorsHealth();
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

function applyNewsPanelMode(mode) {
  state.newsPanelMode = mode || "default";
  var main = document.querySelector(".scanner-main");
  if (main) {
    main.classList.remove("news-panel-compact", "news-panel-wide", "news-panel-collapsed");
    if (state.newsPanelMode === "compact") main.classList.add("news-panel-compact");
    if (state.newsPanelMode === "wide") main.classList.add("news-panel-wide");
    if (state.newsPanelMode === "collapsed") main.classList.add("news-panel-collapsed");
  }
  var controls = el("news-panel-controls");
  if (controls) {
    controls.querySelectorAll(".news-panel-btn").forEach(function (btn) {
      btn.classList.toggle("active", (btn.getAttribute("data-news-panel") || "default") === state.newsPanelMode);
    });
  }
}

function setupNewsPanelControls() {
  var controls = el("news-panel-controls");
  if (!controls) return;
  controls.addEventListener("click", function (e) {
    var btn = e.target.closest(".news-panel-btn");
    if (!btn) return;
    e.preventDefault();
    applyNewsPanelMode(btn.getAttribute("data-news-panel") || "default");
  });
  applyNewsPanelMode(state.newsPanelMode);
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

  var triage = el("triage-filters");
  if (triage) {
    triage.addEventListener("click", function (e) {
      var btn = e.target.closest(".triage-btn");
      if (!btn) return;
      state.triageFilter = btn.getAttribute("data-triage") || "";
      state.filteredRows = applyFilters(state.rows);
      renderSummary(state.rows);
      renderHead();
      renderRows(state.filteredRows);
    });
  }

  var blockerToggle = el("blocker-toggle");
  if (blockerToggle) {
    blockerToggle.addEventListener("click", function () {
      state.blockerOpen = !state.blockerOpen;
      renderBlockerPanel(state.rows);
    });
  }
  var blockerContent = el("blocker-content");
  if (blockerContent) {
    blockerContent.addEventListener("click", function (e) {
      var clear = e.target.closest("[data-blocker-clear]");
      if (clear) {
        state.blockerFilter = null;
      } else {
        var chip = e.target.closest(".blocker-chip");
        if (!chip) return;
        var type = chip.getAttribute("data-blocker-type");
        var key = chip.getAttribute("data-blocker-key");
        if (!type || !key) return;
        if (state.blockerFilter && state.blockerFilter.type === type && state.blockerFilter.key === key) {
          state.blockerFilter = null;
        } else {
          state.blockerFilter = { type: type, key: key };
        }
      }
      state.filteredRows = applyFilters(state.rows);
      renderSummary(state.rows);
      renderHead();
      renderRows(state.filteredRows);
    });
  }

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
      renderSummary(state.rows);
      renderHead();
      renderRows(state.filteredRows);
    });
  });

  // Start with frozen (instant), then auto-discover live
  loadScanner();
  setupNewsFeedToggles();
  setupNewsPanelControls();
  loadProviderStatus();
  loadCadenceStatus();
}

document.addEventListener("DOMContentLoaded", init);
