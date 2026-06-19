/* ==========================================================
   CRACMS — Risk Register page logic
   Handles listing/filtering risks, and the add/edit modal that
   talks to POST/PUT/DELETE /api/risks. The score preview here is
   purely cosmetic -- the backend recalculates risk_score and
   risk_level itself and is the source of truth.
   ========================================================== */

let categories = [];
let currentRisks = [];

document.addEventListener("DOMContentLoaded", () => {
  loadCategories();
  loadRisks();

  document.getElementById("btn-add-risk").addEventListener("click", openAddRiskModal);
  document.getElementById("risk-form").addEventListener("submit", handleRiskFormSubmit);

  document.getElementById("risk-likelihood").addEventListener("change", updateScorePreview);
  document.getElementById("risk-impact").addEventListener("change", updateScorePreview);

  document.getElementById("filter-status").addEventListener("change", loadRisks);
  document.getElementById("filter-level").addEventListener("change", loadRisks);
  document.getElementById("filter-category").addEventListener("change", loadRisks);
  document.getElementById("btn-clear-filters").addEventListener("click", () => {
    document.getElementById("filter-status").value = "";
    document.getElementById("filter-level").value = "";
    document.getElementById("filter-category").value = "";
    loadRisks();
  });

  updateScorePreview();
});

/* ---------- Loading data ---------- */

async function loadCategories() {
  try {
    categories = await apiRequest("/risks/categories");
    const options = categories.map((c) => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join("");

    document.getElementById("filter-category").insertAdjacentHTML("beforeend", options);
    document.getElementById("risk-category").insertAdjacentHTML("beforeend", options);
  } catch (err) {
    showToast(`Could not load categories: ${err.message}`, "error");
  }
}

async function loadRisks() {
  const status = document.getElementById("filter-status").value;
  const level = document.getElementById("filter-level").value;
  const categoryId = document.getElementById("filter-category").value;

  const params = new URLSearchParams();
  if (status) params.set("status", status);
  if (level) params.set("risk_level", level);
  if (categoryId) params.set("category_id", categoryId);

  const tbody = document.getElementById("risk-table-body");
  tbody.innerHTML = `<tr><td colspan="10" class="empty-state">Loading…</td></tr>`;

  try {
    currentRisks = await apiRequest(`/risks/?${params.toString()}`);
    renderRiskTable(currentRisks);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="10" class="empty-state">Failed to load risks: ${escapeHtml(err.message)}</td></tr>`;
  }
}

function categoryName(categoryId) {
  const match = categories.find((c) => c.id === categoryId);
  return match ? match.name : "—";
}

/* ---------- Rendering ---------- */

function renderRiskTable(risks) {
  const tbody = document.getElementById("risk-table-body");

  if (!risks.length) {
    tbody.innerHTML = `<tr><td colspan="10" class="empty-state">No risks match these filters. Try "Add Risk" to create one.</td></tr>`;
    return;
  }

  tbody.innerHTML = risks.map((risk) => `
    <tr>
      <td class="code">${escapeHtml(risk.risk_code)}</td>
      <td class="title-cell">
        ${escapeHtml(risk.title)}
        ${risk.description ? `<span class="desc">${escapeHtml(risk.description)}</span>` : ""}
      </td>
      <td>${escapeHtml(categoryName(risk.category_id))}</td>
      <td class="mono">${risk.likelihood} × ${risk.impact}</td>
      <td class="mono">${risk.risk_score}</td>
      <td>${riskLevelBadge(risk.risk_level)}</td>
      <td>${escapeHtml(risk.owner) || "—"}</td>
      <td>${statusBadge(risk.status)}</td>
      <td class="mono">${formatDate(risk.review_date)}</td>
      <td>
        <div class="row-actions">
          <button class="btn btn-ghost btn-sm" onclick="openEditRiskModal(${risk.id})">Edit</button>
          <button class="btn btn-ghost btn-sm" onclick="deleteRisk(${risk.id})">Delete</button>
        </div>
      </td>
    </tr>
  `).join("");
}

/* ---------- Score preview ---------- */

function updateScorePreview() {
  const likelihood = Number(document.getElementById("risk-likelihood").value);
  const impact = Number(document.getElementById("risk-impact").value);
  const score = calculateRiskScore(likelihood, impact);
  const level = calculateRiskLevel(score);

  document.getElementById("score-preview-number").textContent = score;
  document.getElementById("score-preview-badge").innerHTML = riskLevelBadge(level);
}

/* ---------- Modal open/close ---------- */

function openAddRiskModal() {
  document.getElementById("risk-form").reset();
  document.getElementById("risk-id").value = "";
  document.getElementById("risk-modal-title").textContent = "Add Risk";
  updateScorePreview();
  openModal("risk-modal");
}

function openEditRiskModal(riskId) {
  const risk = currentRisks.find((r) => r.id === riskId);
  if (!risk) return;

  document.getElementById("risk-id").value = risk.id;
  document.getElementById("risk-title").value = risk.title || "";
  document.getElementById("risk-description").value = risk.description || "";
  document.getElementById("risk-category").value = risk.category_id || "";
  document.getElementById("risk-asset").value = risk.asset_affected || "";
  document.getElementById("risk-likelihood").value = risk.likelihood;
  document.getElementById("risk-impact").value = risk.impact;
  document.getElementById("risk-owner").value = risk.owner || "";
  document.getElementById("risk-status").value = risk.status;
  document.getElementById("risk-treatment").value = risk.treatment_plan || "";
  document.getElementById("risk-identified-date").value = risk.identified_date || "";
  document.getElementById("risk-review-date").value = risk.review_date || "";

  document.getElementById("risk-modal-title").textContent = `Edit Risk — ${risk.risk_code}`;
  updateScorePreview();
  openModal("risk-modal");
}

/* ---------- Save / Delete ---------- */

async function handleRiskFormSubmit(e) {
  e.preventDefault();

  const riskId = document.getElementById("risk-id").value;
  const payload = {
    title: document.getElementById("risk-title").value,
    description: document.getElementById("risk-description").value,
    category_id: document.getElementById("risk-category").value || null,
    asset_affected: document.getElementById("risk-asset").value,
    likelihood: Number(document.getElementById("risk-likelihood").value),
    impact: Number(document.getElementById("risk-impact").value),
    owner: document.getElementById("risk-owner").value,
    status: document.getElementById("risk-status").value,
    treatment_plan: document.getElementById("risk-treatment").value,
    identified_date: document.getElementById("risk-identified-date").value || null,
    review_date: document.getElementById("risk-review-date").value || null
  };

  try {
    if (riskId) {
      await apiRequest(`/risks/${riskId}`, "PUT", payload);
      showToast("Risk updated.");
    } else {
      await apiRequest("/risks/", "POST", payload);
      showToast("Risk added to register.");
    }
    closeModal("risk-modal");
    loadRisks();
  } catch (err) {
    showToast(`Could not save risk: ${err.message}`, "error");
  }
}

async function deleteRisk(riskId) {
  const risk = currentRisks.find((r) => r.id === riskId);
  if (!confirm(`Delete risk ${risk ? risk.risk_code : ""}? This cannot be undone.`)) return;

  try {
    await apiRequest(`/risks/${riskId}`, "DELETE");
    showToast("Risk deleted.");
    loadRisks();
  } catch (err) {
    showToast(`Could not delete risk: ${err.message}`, "error");
  }
}
