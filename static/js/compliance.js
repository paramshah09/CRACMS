/* ==========================================================
   CRACMS — Compliance page logic
   Three linked entities: frameworks -> controls -> status.
   The status list returned by the API includes control_id directly,
   so each control is matched to its status record with a simple
   control_id comparison.
   ========================================================== */

let frameworks = [];
let currentControls = [];
let allStatuses = [];
let riskOptions = [];

document.addEventListener("DOMContentLoaded", () => {
  loadFrameworks();
  loadAllStatuses();
  loadRiskOptions();

  document.getElementById("framework-select").addEventListener("change", onFrameworkChange);
  document.getElementById("btn-add-framework").addEventListener("click", () => {
    document.getElementById("framework-form").reset();
    openModal("framework-modal");
  });
  document.getElementById("framework-form").addEventListener("submit", handleFrameworkSubmit);

  document.getElementById("btn-add-control").addEventListener("click", () => {
    document.getElementById("control-form").reset();
    openModal("control-modal");
  });
  document.getElementById("control-form").addEventListener("submit", handleControlSubmit);

  document.getElementById("status-form").addEventListener("submit", handleStatusSubmit);
  document.getElementById("btn-delete-status").addEventListener("click", handleStatusDelete);
});

/* ---------- Frameworks ---------- */

async function loadFrameworks() {
  try {
    frameworks = await apiRequest("/compliance/frameworks");
    const select = document.getElementById("framework-select");
    const currentValue = select.value;
    select.innerHTML = `<option value="">— Select a framework —</option>` +
      frameworks.map((f) => `<option value="${f.id}">${escapeHtml(f.name)}</option>`).join("");
    if (currentValue) select.value = currentValue;
  } catch (err) {
    showToast(`Could not load frameworks: ${err.message}`, "error");
  }
}

async function handleFrameworkSubmit(e) {
  e.preventDefault();
  const payload = {
    name: document.getElementById("framework-name").value,
    version: document.getElementById("framework-version").value,
    description: document.getElementById("framework-description").value
  };
  try {
    const created = await apiRequest("/compliance/frameworks", "POST", payload);
    showToast("Framework added.");
    closeModal("framework-modal");
    await loadFrameworks();
    document.getElementById("framework-select").value = created.id;
    onFrameworkChange();
  } catch (err) {
    showToast(`Could not add framework: ${err.message}`, "error");
  }
}

function onFrameworkChange() {
  const frameworkId = document.getElementById("framework-select").value;
  const addControlBtn = document.getElementById("btn-add-control");

  if (!frameworkId) {
    addControlBtn.disabled = true;
    document.getElementById("controls-heading").textContent = "Controls";
    document.getElementById("controls-table-body").innerHTML =
      `<tr><td colspan="7" class="empty-state">Select a framework above to see its controls.</td></tr>`;
    return;
  }

  addControlBtn.disabled = false;
  const framework = frameworks.find((f) => f.id === Number(frameworkId));
  document.getElementById("controls-heading").textContent = `Controls — ${framework ? framework.name : ""}`;
  loadControlsForFramework(frameworkId);
}

/* ---------- Controls ---------- */

async function loadControlsForFramework(frameworkId) {
  const tbody = document.getElementById("controls-table-body");
  tbody.innerHTML = `<tr><td colspan="7" class="empty-state">Loading…</td></tr>`;

  try {
    currentControls = await apiRequest(`/compliance/controls?framework_id=${frameworkId}`);
    renderControlsTable();
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty-state">Failed to load controls: ${escapeHtml(err.message)}</td></tr>`;
  }
}

async function loadAllStatuses() {
  try {
    allStatuses = await apiRequest("/compliance/status");
    renderControlsTable();
  } catch (err) {
    showToast(`Could not load compliance status records: ${err.message}`, "error");
  }
}

function findStatusForControl(control) {
  return allStatuses.find((s) => s.control_id === control.id) || null;
}

function renderControlsTable() {
  const tbody = document.getElementById("controls-table-body");
  if (!currentControls.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty-state">No controls yet for this framework. Use "Add Control" to create one.</td></tr>`;
    return;
  }

  tbody.innerHTML = currentControls.map((control) => {
    const statusRecord = findStatusForControl(control);
    const statusHtml = statusRecord ? statusBadge(statusRecord.status) : `<span class="badge badge-neutral">Not Assessed</span>`;
    const responsible = statusRecord && statusRecord.responsible_person ? escapeHtml(statusRecord.responsible_person) : "—";
    const lastAssessed = statusRecord ? formatDate(statusRecord.last_assessed_date) : "—";
    const buttonLabel = statusRecord ? "Update" : "Set Status";

    return `
      <tr>
        <td class="code">${escapeHtml(control.control_ref)}</td>
        <td class="title-cell">
          ${escapeHtml(control.control_name)}
          ${control.control_description ? `<span class="desc">${escapeHtml(control.control_description)}</span>` : ""}
        </td>
        <td>${escapeHtml(control.domain) || "—"}</td>
        <td>${statusHtml}</td>
        <td>${responsible}</td>
        <td class="mono">${lastAssessed}</td>
        <td>
          <div class="row-actions">
            <button class="btn btn-ghost btn-sm" onclick="openStatusModal(${control.id}, ${statusRecord ? statusRecord.id : "null"})">${buttonLabel}</button>
          </div>
        </td>
      </tr>`;
  }).join("");
}

async function handleControlSubmit(e) {
  e.preventDefault();
  const frameworkId = document.getElementById("framework-select").value;
  const payload = {
    framework_id: Number(frameworkId),
    control_ref: document.getElementById("control-ref").value,
    control_name: document.getElementById("control-name").value,
    control_description: document.getElementById("control-description").value,
    domain: document.getElementById("control-domain").value
  };
  try {
    await apiRequest("/compliance/controls", "POST", payload);
    showToast("Control added.");
    closeModal("control-modal");
    loadControlsForFramework(frameworkId);
  } catch (err) {
    showToast(`Could not add control: ${err.message}`, "error");
  }
}

/* ---------- Linked risk dropdown ---------- */

async function loadRiskOptions() {
  try {
    riskOptions = await apiRequest("/risks/");
    const select = document.getElementById("status-linked-risk");
    select.innerHTML = `<option value="">— None —</option>` +
      riskOptions.map((r) => `<option value="${r.id}">${escapeHtml(r.risk_code)} — ${escapeHtml(r.title)}</option>`).join("");
  } catch (err) {
    // Non-critical -- the dropdown just stays empty if this fails.
  }
}

/* ---------- Status modal ---------- */

function openStatusModal(controlId, statusId) {
  const control = currentControls.find((c) => c.id === controlId);
  if (!control) return;

  document.getElementById("status-form").reset();
  document.getElementById("status-control-id").value = controlId;
  document.getElementById("status-control-label").textContent = `${control.control_ref} — ${control.control_name}`;
  document.getElementById("btn-delete-status").style.display = "none";

  if (statusId) {
    const record = allStatuses.find((s) => s.id === statusId);
    document.getElementById("status-modal-title").textContent = "Update Compliance Status";
    document.getElementById("status-id").value = statusId;
    document.getElementById("status-status").value = record.status;
    document.getElementById("status-evidence").value = record.evidence || "";
    document.getElementById("status-responsible").value = record.responsible_person || "";
    document.getElementById("status-linked-risk").value = record.linked_risk_id || "";
    document.getElementById("status-last-assessed").value = record.last_assessed_date || "";
    document.getElementById("status-next-review").value = record.next_review_date || "";
    document.getElementById("status-notes").value = record.notes || "";
    document.getElementById("btn-delete-status").style.display = "inline-flex";
  } else {
    document.getElementById("status-modal-title").textContent = "Set Compliance Status";
    document.getElementById("status-id").value = "";
    document.getElementById("status-last-assessed").value = todayIso();
  }

  openModal("status-modal");
}

async function handleStatusSubmit(e) {
  e.preventDefault();
  const statusId = document.getElementById("status-id").value;
  const payload = {
    control_id: Number(document.getElementById("status-control-id").value),
    status: document.getElementById("status-status").value,
    evidence: document.getElementById("status-evidence").value,
    responsible_person: document.getElementById("status-responsible").value,
    linked_risk_id: document.getElementById("status-linked-risk").value || null,
    last_assessed_date: document.getElementById("status-last-assessed").value || null,
    next_review_date: document.getElementById("status-next-review").value || null,
    notes: document.getElementById("status-notes").value
  };

  try {
    if (statusId) {
      await apiRequest(`/compliance/status/${statusId}`, "PUT", payload);
      showToast("Compliance status updated.");
    } else {
      await apiRequest("/compliance/status", "POST", payload);
      showToast("Compliance status recorded.");
    }
    closeModal("status-modal");
    await loadAllStatuses();
  } catch (err) {
    showToast(`Could not save status: ${err.message}`, "error");
  }
}

async function handleStatusDelete() {
  const statusId = document.getElementById("status-id").value;
  if (!statusId) return;
  if (!confirm("Delete this compliance status record?")) return;

  try {
    await apiRequest(`/compliance/status/${statusId}`, "DELETE");
    showToast("Status record deleted.");
    closeModal("status-modal");
    await loadAllStatuses();
  } catch (err) {
    showToast(`Could not delete status: ${err.message}`, "error");
  }
}
