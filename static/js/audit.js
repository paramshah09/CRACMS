/* ==========================================================
   CRACMS — Audit Findings page logic
   Handles listing/filtering findings and the add/edit modal.
   Field names here match the corrected audit_findings schema:
   title, description, severity, linked_risk_id, owner,
   remediation_plan, due_date, status. There is no longer a
   "related control" relationship -- that feature was removed
   along with the related_control_id column.

   "Overdue" highlighting in the table is computed client-side
   from due_date -- the stored `status` value is only changed
   when someone explicitly sets it, matching how a real audit
   tracker keeps a deliberate status history.
   ========================================================== */

let currentFindings = [];
let riskOptionsForFindings = [];

document.addEventListener("DOMContentLoaded", () => {
  loadFindings();
  loadRiskOptionsForFindings();

  document.getElementById("btn-add-finding").addEventListener("click", openAddFindingModal);
  document.getElementById("finding-form").addEventListener("submit", handleFindingSubmit);

  document.getElementById("filter-status").addEventListener("change", loadFindings);
  document.getElementById("filter-severity").addEventListener("change", loadFindings);
  document.getElementById("btn-clear-filters").addEventListener("click", () => {
    document.getElementById("filter-status").value = "";
    document.getElementById("filter-severity").value = "";
    loadFindings();
  });
});

/* ---------- Loading lookups ---------- */

async function loadRiskOptionsForFindings() {
  try {
    riskOptionsForFindings = await apiRequest("/risks/");
    const select = document.getElementById("finding-risk");
    select.innerHTML = `<option value="">— None —</option>` +
      riskOptionsForFindings.map((r) => `<option value="${r.id}">${escapeHtml(r.risk_code)} — ${escapeHtml(r.title)}</option>`).join("");
  } catch (err) {
    // Non-critical
  }
}

/* ---------- Listing ---------- */

async function loadFindings() {
  const status = document.getElementById("filter-status").value;
  const severity = document.getElementById("filter-severity").value;

  const params = new URLSearchParams();
  if (status) params.set("status", status);
  if (severity) params.set("severity", severity);

  const tbody = document.getElementById("findings-table-body");
  tbody.innerHTML = `<tr><td colspan="7" class="empty-state">Loading…</td></tr>`;

  try {
    currentFindings = await apiRequest(`/audit-findings/?${params.toString()}`);
    renderFindingsTable(currentFindings);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty-state">Failed to load findings: ${escapeHtml(err.message)}</td></tr>`;
  }
}

function isOverdue(finding) {
  if (!finding.due_date || finding.status === "Closed") return false;
  return finding.due_date < todayIso();
}

function renderFindingsTable(findings) {
  const tbody = document.getElementById("findings-table-body");
  if (!findings.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty-state">No findings match these filters. Use "Add Finding" to log one.</td></tr>`;
    return;
  }

  tbody.innerHTML = findings.map((finding) => {
    const overdue = isOverdue(finding);
    const dateStyle = overdue ? `color: var(--risk-critical); font-weight: 600;` : "";
    return `
      <tr>
        <td class="code">${escapeHtml(finding.finding_code)}</td>
        <td class="title-cell">
          ${escapeHtml(finding.title)}
          ${finding.description ? `<span class="desc">${escapeHtml(finding.description)}</span>` : ""}
        </td>
        <td>${severityBadge(finding.severity)}</td>
        <td>${statusBadge(finding.status)}${overdue ? ' <span class="badge badge-bad">Overdue</span>' : ""}</td>
        <td>${escapeHtml(finding.owner) || "—"}</td>
        <td class="mono" style="${dateStyle}">${formatDate(finding.due_date)}</td>
        <td>
          <div class="row-actions">
            <button class="btn btn-ghost btn-sm" onclick="openEditFindingModal(${finding.id})">Edit</button>
            <button class="btn btn-ghost btn-sm" onclick="deleteFinding(${finding.id})">Delete</button>
          </div>
        </td>
      </tr>`;
  }).join("");
}

/* ---------- Modal open/close ---------- */

function openAddFindingModal() {
  document.getElementById("finding-form").reset();
  document.getElementById("finding-id").value = "";
  document.getElementById("finding-modal-title").textContent = "Add Finding";
  openModal("finding-modal");
}

function openEditFindingModal(findingId) {
  const finding = currentFindings.find((f) => f.id === findingId);
  if (!finding) return;

  document.getElementById("finding-id").value = finding.id;
  document.getElementById("finding-title").value = finding.title || "";
  document.getElementById("finding-severity").value = finding.severity;
  document.getElementById("finding-description").value = finding.description || "";
  document.getElementById("finding-status").value = finding.status;
  document.getElementById("finding-owner").value = finding.owner || "";
  document.getElementById("finding-risk").value = finding.linked_risk_id || "";
  document.getElementById("finding-remediation").value = finding.remediation_plan || "";
  document.getElementById("finding-due-date").value = finding.due_date || "";

  document.getElementById("finding-modal-title").textContent = `Edit Finding — ${finding.finding_code}`;
  openModal("finding-modal");
}

/* ---------- Save / Delete ---------- */

async function handleFindingSubmit(e) {
  e.preventDefault();

  const findingId = document.getElementById("finding-id").value;
  const payload = {
    title: document.getElementById("finding-title").value,
    description: document.getElementById("finding-description").value,
    severity: document.getElementById("finding-severity").value,
    linked_risk_id: document.getElementById("finding-risk").value || null,
    status: document.getElementById("finding-status").value,
    owner: document.getElementById("finding-owner").value,
    remediation_plan: document.getElementById("finding-remediation").value,
    due_date: document.getElementById("finding-due-date").value || null
  };

  try {
    if (findingId) {
      await apiRequest(`/audit-findings/${findingId}`, "PUT", payload);
      showToast("Finding updated.");
    } else {
      await apiRequest("/audit-findings/", "POST", payload);
      showToast("Finding logged.");
    }
    closeModal("finding-modal");
    loadFindings();
  } catch (err) {
    showToast(`Could not save finding: ${err.message}`, "error");
  }
}

async function deleteFinding(findingId) {
  const finding = currentFindings.find((f) => f.id === findingId);
  if (!confirm(`Delete finding ${finding ? finding.finding_code : ""}? This cannot be undone.`)) return;

  try {
    await apiRequest(`/audit-findings/${findingId}`, "DELETE");
    showToast("Finding deleted.");
    loadFindings();
  } catch (err) {
    showToast(`Could not delete finding: ${err.message}`, "error");
  }
}
