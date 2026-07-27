"use strict";

/* Shared utilities for the Short Squeeze Research Screener.
 *
 * This module contains no metric computation, no rule evaluation, no score,
 * no probability, and no ranking. It provides only DOM helpers, fetch utilities,
 * and presentation-only formatting shared across views.
 */

const MISSING = "\u2014";
const N_A = "N/A";

const newsCache = {};

const CLASS_COLORS = {
  PRIME: "#56d68b",
  SUBPRIME: "#6fa8ff",
  WATCH: "#ffca57",
  NOT_QUALIFIED: "#ff7d7d",
  UNEVALUABLE: "#8b98a9",
  CONFLICTED: "#cbb6f0",
  REFERENCE_DEFINITION_INCOMPLETE: "#9aa8bc",
};

const PRESSURE_COLORS = {
  high: "#56d68b",
  mid: "#ffca57",
  low: "#ff7d7d",
  none: "#8b98a9",
};

function pressureColor(v) {
  if (v == null) return PRESSURE_COLORS.none;
  if (v >= 70) return PRESSURE_COLORS.high;
  if (v >= 50) return PRESSURE_COLORS.mid;
  return PRESSURE_COLORS.low;
}

const el = (id) => document.getElementById(id);
const text = (node, value) => { node.textContent = value; return node; };

async function getJSON(url, options) {
  const response = await fetch(url, options);
  const payload = await response.json().catch(() => ({ error: `HTTP ${response.status}` }));
  if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
  return payload;
}

function setStatus(message, isError) {
  const node = el("status-line");
  if (!node) return;
  const isScanner = document.body && document.body.classList.contains("scanner");
  const msg = String(message || "");
  let show = true;
  if (isScanner) {
    show = !!(
      msg
      && (isError
        || /loading|refreshing|awaiting|discovering|unavailable|error|ready but/i.test(msg))
    );
    if (!show) {
      node.textContent = "";
      node.setAttribute("hidden", "");
      return;
    }
    node.removeAttribute("hidden");
  }
  node.textContent = msg;
  node.style.color = isError ? "#ff9d9d" : "";
}

function ago(iso) {
  if (!iso) return null;
  try {
    const diff = (Date.now() - new Date(iso).getTime()) / 1000;
    if (diff < 60) return Math.round(diff) + "s ago";
    if (diff < 3600) return Math.round(diff / 60) + "m ago";
    if (diff < 86400) return Math.round(diff / 3600) + "h ago";
    return Math.round(diff / 86400) + "d ago";
  } catch (e) {
    return iso;
  }
}

async function getCachedNews(symbol) {
  const cached = newsCache[symbol];
  if (cached && (Date.now() - cached.at < 60000)) return cached.data;
  try {
    const newsUrl = "/api/news/symbol?symbol=" + encodeURIComponent(symbol);
    const payload = await getJSON(newsUrl);
    const data = payload && payload.data != null ? payload.data : payload;
    newsCache[symbol] = { data: data, at: Date.now() };
    return data;
  } catch (e) {
    return null;
  }
}

function showToast(message, isError, durationMs) {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.style.cssText = "position:fixed;bottom:16px;right:16px;z-index:9999;display:flex;flex-direction:column;gap:8px;";
    document.body.appendChild(container);
  }
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = message;
  toast.style.cssText = [
    "padding:10px 16px;border-radius:4px;font-size:13px;max-width:400px;",
    "box-shadow:0 2px 12px rgba(0,0,0,.4);animation:toast-in .25s ease-out;",
    isError ? "background:#2a1616;color:#ff9d9d;border:1px solid #cc4b4b;" : "background:#12291d;color:#7fe0a6;border:1px solid #2f9e5e;"
  ].join("");
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity .3s";
    setTimeout(() => toast.remove(), 300);
  }, durationMs || 4000);
}

const styleSheet = document.createElement("style");
styleSheet.textContent = "@keyframes toast-in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}";
document.head.appendChild(styleSheet);
