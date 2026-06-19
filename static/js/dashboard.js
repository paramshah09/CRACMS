/* ==========================================================
   CRACMS — Dashboard page logic
   Pulls a single payload from GET /api/dashboard/stats and renders
   the KPI cards plus three summary sections (Risk Levels,
   Compliance Statistics, Audit Statistics) from it.

   This matches the current dashboard_routes.py response shape
   exactly: { total_risks, open_risks, closed_risks, risks_by_level,
   compliance_stats: {...}, audit_stats: {...} }. There is no risk
   heat map data in this response, so that widget has been removed
   rather than left rendering empty.
   ========================================================== */

const RISK_LEVEL_ORDER = ["Critical", "High", "Medium", "Low"];
const RISK_LEVEL_VARS = {
  Low: "--risk-low",
  Medium: "--risk-medium",
  High: "--risk-high",
  Critical: "--risk-critical"
};

document.addEventListener("DOMContentLoaded", loadDashboard);

async function loadDashboard() {
  try {
    const stats = await apiRequest("/dashboard/stats");
    renderKpis(stats);
    renderRiskLevels(stats.risks_by_level, stats.total_risks);
    renderComplianceStats(stats.compliance_stats);
    renderAuditStats(stats.audit_stats);
  } catch (err) {
    showToast(`Could not load dashboard: ${err.message}`, "error");
  }
}

/* ---------- KPI cards ---------- */

function renderKpis(stats) {
  document.getElementById("kpi-total-risks").textContent = stats.total_risks;
  document.getElementById("kpi-open-risks").textContent = stats.open_risks;
  document.getElementById("kpi-closed-risks").textContent = stats.closed_risks;
  document.getElementById("kpi-total-controls").textContent = stats.compliance_stats.total_controls;
  document.getElementById("kpi-compliant-controls").textContent = stats.compliance_stats.compliant_controls;
  document.getElementById("kpi-total-findings").textContent = stats.audit_stats.total_findings;
  document.getElementById("kpi-overdue-findings").textContent = stats.audit_stats.overdue_findings;
}

/* ---------- Shared bar-list renderer ---------- */

function renderBarList(containerId, rows) {
  const container = document.getElementById(containerId);
  if (!rows.length) {
    container.innerHTML = `<p class="empty-state">No data yet.</p>`;
    return;
  }
  container.innerHTML = rows.map((row) => `
    <div class="bar-row">
      <span class="bar-label">${escapeHtml(row.label)}</span>
      <div class="bar-track"><div class="bar-fill" style="width: ${row.percent}%; background: ${row.color};"></div></div>
      <span class="bar-value">${row.valueText}</span>
    </div>
  `).join("");
}

/* ---------- Risk Levels summary ---------- */

function renderRiskLevels(risksByLevel, totalRisks) {
  const rows = RISK_LEVEL_ORDER.map((level) => {
    const count = (risksByLevel && risksByLevel[level]) || 0;
    const percent = totalRisks > 0 ? Math.round((count / totalRisks) * 100) : 0;
    return {
      label: level,
      percent,
      color: `var(${RISK_LEVEL_VARS[level]})`,
      valueText: String(count)
    };
  });
  renderBarList("risk-levels-list", rows);
}

/* ---------- Compliance Statistics summary ---------- */

function renderComplianceStats(complianceStats) {
  const total = complianceStats.total_controls;

  // Percentages are relative to total_controls, not to each other --
  // they won't necessarily add up to 100%, since a control can have
  // no status record yet (not counted in any of the three buckets).
  const rows = [
    { label: "Compliant", count: complianceStats.compliant_controls, color: "var(--risk-low)" },
    { label: "Partially Compliant", count: complianceStats.partially_compliant_controls, color: "var(--risk-medium)" },
    { label: "Non-Compliant", count: complianceStats.non_compliant_controls, color: "var(--risk-critical)" }
  ].map((row) => ({
    label: row.label,
    percent: total > 0 ? Math.round((row.count / total) * 100) : 0,
    color: row.color,
    valueText: String(row.count)
  }));

  renderBarList("compliance-stats-list", rows);
}

/* ---------- Audit Statistics summary ---------- */

function renderAuditStats(auditStats) {
  const total = auditStats.total_findings;

  const rows = [
    { label: "Open", count: auditStats.open_findings, color: "var(--info)" },
    { label: "Closed", count: auditStats.closed_findings, color: "var(--risk-low)" },
    { label: "Overdue", count: auditStats.overdue_findings, color: "var(--risk-critical)" }
  ].map((row) => ({
    label: row.label,
    percent: total > 0 ? Math.round((row.count / total) * 100) : 0,
    color: row.color,
    valueText: String(row.count)
  }));

  renderBarList("audit-stats-list", rows);
}
