/* ==========================================================
   CRACMS — Shared frontend helpers
   Loaded on every page before the page-specific script.
   Centralizes the fetch wrapper, toast notifications, modal
   open/close, and the badge/escaping helpers so each page's
   script can stay focused on its own module's logic.
   ========================================================== */

const API_BASE = "/api";

/* ---------- API wrapper ---------- */

/**
 * Wraps fetch() for talking to the Flask API.
 * Throws an Error with the backend's message on non-2xx responses,
 * so callers can just try/catch and show a toast.
 */
async function apiRequest(path, method = "GET", body = null) {
  const options = {
    method,
    headers: { "Content-Type": "application/json" }
  };
  if (body !== null) {
    options.body = JSON.stringify(body);
  }

  const res = await fetch(`${API_BASE}${path}`, options);
  const isJson = res.headers.get("content-type")?.includes("application/json");
  const data = isJson ? await res.json() : null;

  if (!res.ok) {
    const message = (data && data.error) ? data.error : `Request failed (${res.status})`;
    throw new Error(message);
  }
  return data;
}

/* ---------- Toasts ---------- */

function showToast(message, type = "success") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => toast.remove(), 4000);
}

/* ---------- Escaping ---------- */

/**
 * Escapes user-supplied text before it's inserted via innerHTML.
 * Every field that came from the database (titles, descriptions,
 * notes, etc.) must go through this -- it's the difference between
 * a safe table render and a stored XSS bug.
 */
function escapeHtml(value) {
  if (value === null || value === undefined) return "";
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/* ---------- Formatting ---------- */

function formatDate(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (isNaN(d.getTime())) return value;
  return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

function todayIso() {
  return new Date().toISOString().split("T")[0];
}

/* ---------- Badges ---------- */

// Maps every status string used across the app to a badge color class.
const STATUS_BADGE_MAP = {
  // Risk status
  Open: "info",
  Mitigated: "good",
  Accepted: "neutral",
  Closed: "good",
  // Compliance status
  Compliant: "good",
  "Partially Compliant": "warn",
  "Non-Compliant": "bad",
  "Not Applicable": "neutral",
  // Audit finding status
  "In Progress": "warn",
  Overdue: "bad"
};

const RISK_LEVEL_CLASS = {
  Low: "low",
  Medium: "medium",
  High: "high",
  Critical: "critical"
};

const SEVERITY_CLASS = {
  Low: "low",
  Medium: "medium",
  High: "high",
  Critical: "critical"
};

function riskLevelBadge(level) {
  const cls = RISK_LEVEL_CLASS[level] || "neutral";
  return `<span class="badge badge-${cls}">${escapeHtml(level || "—")}</span>`;
}

function severityBadge(severity) {
  const cls = SEVERITY_CLASS[severity] || "neutral";
  return `<span class="badge badge-${cls}">${escapeHtml(severity || "—")}</span>`;
}

function statusBadge(status) {
  const cls = STATUS_BADGE_MAP[status] || "neutral";
  return `<span class="badge badge-${cls}">${escapeHtml(status || "—")}</span>`;
}

/* ---------- Risk scoring (mirrors utils/risk_calculator.py) ----------
   Used for instant client-side preview only -- the backend recalculates
   and is always the source of truth for stored values. */

function calculateRiskScore(likelihood, impact) {
  return likelihood * impact;
}

function calculateRiskLevel(score) {
  if (score <= 4) return "Low";
  if (score <= 9) return "Medium";
  if (score <= 16) return "High";
  return "Critical";
}

/* ---------- Modal controls ---------- */

function openModal(id) {
  document.getElementById(id).classList.add("open");
}

function closeModal(id) {
  document.getElementById(id).classList.remove("open");
}

// Click on the dark overlay (outside the modal box) closes it.
document.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal-overlay")) {
    e.target.classList.remove("open");
  }
});

// Escape key closes any open modal.
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    document.querySelectorAll(".modal-overlay.open").forEach((m) => m.classList.remove("open"));
  }
});

/* ---------- Nav highlighting ---------- */

document.addEventListener("DOMContentLoaded", () => {
  const path = window.location.pathname;
  document.querySelectorAll(".nav-link").forEach((link) => {
    const page = link.getAttribute("data-page");
    const isDashboard = page === "dashboard" && path === "/";
    const isMatch = path === link.getAttribute("href");
    if (isDashboard || isMatch) link.classList.add("active");
  });
});
