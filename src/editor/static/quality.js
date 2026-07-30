const state = {
  report: null,
  serialized: "",
  activeView: "dashboard",
  loading: false,
};

const elements = {
  tabs: document.querySelector("#quality-tabs"),
  content: document.querySelector("#quality-content"),
  refresh: document.querySelector("#refresh-quality"),
  status: document.querySelector("#refresh-status"),
};

async function loadReport(force = false) {
  if (state.loading) {
    return;
  }
  state.loading = true;
  try {
    const response = await fetch("/api/quality/report", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const report = await response.json();
    const serialized = JSON.stringify(report);
    if (force || serialized !== state.serialized) {
      state.report = report;
      state.serialized = serialized;
      renderActiveView();
      elements.status.textContent = "Aggiornato automaticamente";
    }
  } catch (error) {
    elements.status.textContent = `Errore: ${error.message}`;
  } finally {
    state.loading = false;
  }
}

function goToNode(nodeId) {
  if (!nodeId || !window.opener || window.opener.closed) {
    return;
  }
  window.opener.postMessage(
    { type: "ikg:navigate-node", nodeId },
    window.location.origin,
  );
  window.opener.focus();
}

function nodeButton(nodeId) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "node-action";
  button.textContent = "Vai al nodo";
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    goToNode(nodeId);
  });
  return button;
}

function metricGrid(values) {
  const metrics = document.createElement("dl");
  metrics.className = "metric-grid";
  for (const [label, value] of Object.entries(values)) {
    const item = document.createElement("div");
    const term = document.createElement("dt");
    term.textContent = label;
    const detail = document.createElement("dd");
    detail.textContent = String(value);
    item.append(term, detail);
    metrics.append(item);
  }
  return metrics;
}

function renderDashboard() {
  const layout = document.createElement("section");
  layout.className = "score-layout";
  const summary = document.createElement("div");
  summary.className = "score-summary";
  const score = document.createElement("strong");
  score.textContent = String(state.report.score);
  const label = document.createElement("span");
  label.textContent = "Knowledge Quality Score / 100";
  const progress = document.createElement("progress");
  progress.max = 100;
  progress.value = state.report.score;
  summary.append(score, label, progress);

  const dimensions = document.createElement("div");
  dimensions.className = "dimension-list";
  for (const [name, value] of Object.entries(state.report.dimensions)) {
    const row = document.createElement("div");
    row.className = "dimension-row";
    const dimensionName = document.createElement("span");
    dimensionName.textContent = name;
    const dimensionProgress = document.createElement("progress");
    dimensionProgress.max = 100;
    dimensionProgress.value = value;
    const output = document.createElement("output");
    output.textContent = `${value}/100`;
    row.append(dimensionName, dimensionProgress, output);
    dimensions.append(row);
  }
  layout.append(summary, dimensions);
  elements.content.append(
    layout,
    metricGrid({
      errori: state.report.statistics.errors,
      warning: state.report.statistics.warnings,
      nodi: state.report.statistics.nodes,
      relazioni: state.report.statistics.relationships,
    }),
  );
}

function renderIssueTable(issues, emptyText) {
  if (!issues.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = emptyText;
    elements.content.append(empty);
    return;
  }
  const table = document.createElement("table");
  table.className = "quality-table";
  table.innerHTML =
    "<thead><tr><th>Livello</th><th>Categoria</th><th>Nodo</th><th>Controllo</th><th>Dettaglio</th><th></th></tr></thead>";
  const body = document.createElement("tbody");
  for (const issue of issues) {
    const row = document.createElement("tr");
    if (issue.node_id) {
      row.dataset.nodeId = issue.node_id;
      row.addEventListener("dblclick", () => goToNode(issue.node_id));
    }
    for (const value of [
      issue.severity,
      issue.category,
      issue.node_id || "-",
      issue.title,
      issue.detail,
    ]) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    }
    row.firstElementChild.className = `severity-${issue.severity}`;
    const action = document.createElement("td");
    if (issue.node_id) {
      action.append(nodeButton(issue.node_id));
    }
    row.append(action);
    body.append(row);
  }
  table.append(body);
  elements.content.append(table);
}

function renderActivity() {
  const rows = [...state.report.activity].reverse().map((event) => ({
    severity: "",
    category: `#${event.sequence}`,
    node_id: event.node_id,
    title: event.action,
    detail: event.detail,
  }));
  renderIssueTable(rows, "Nessuna attività nella sessione");
}

function renderChecklist() {
  const list = document.createElement("section");
  list.className = "checklist";
  for (const check of state.report.checklist) {
    const item = document.createElement("article");
    item.className = check.passed ? "passed" : "failed";
    const status = document.createElement("span");
    status.className = "check-status";
    status.textContent = check.passed ? "PASS" : "FAIL";
    const label = document.createElement("strong");
    label.textContent = check.label;
    item.append(status, label);
    if (check.node_ids.length) {
      const nodeId = check.node_ids[0];
      item.dataset.nodeId = nodeId;
      item.addEventListener("dblclick", () => goToNode(nodeId));
      item.append(nodeButton(nodeId));
    }
    list.append(item);
  }
  elements.content.append(list);
}

function renderActiveView() {
  if (!state.report) {
    return;
  }
  elements.content.replaceChildren();
  for (const button of elements.tabs.querySelectorAll("button")) {
    button.classList.toggle("active", button.dataset.view === state.activeView);
  }
  if (state.activeView === "dashboard") {
    renderDashboard();
  } else if (state.activeView === "errors") {
    renderIssueTable(state.report.errors, "Nessun errore");
  } else if (state.activeView === "warnings") {
    renderIssueTable(state.report.warnings, "Nessun warning");
  } else if (state.activeView === "coverage") {
    elements.content.append(metricGrid(state.report.coverage));
    renderIssueTable(
      state.report.warnings.filter((issue) => issue.category === "copertura"),
      "Copertura completa",
    );
  } else if (state.activeView === "statistics") {
    elements.content.append(metricGrid(state.report.statistics));
  } else if (state.activeView === "activity") {
    renderActivity();
  } else if (state.activeView === "checklist") {
    renderChecklist();
  }
  elements.content.focus();
}

elements.tabs.addEventListener("click", (event) => {
  const button = event.target.closest("[data-view]");
  if (!button) {
    return;
  }
  state.activeView = button.dataset.view;
  renderActiveView();
});
elements.refresh.addEventListener("click", () => loadReport(true));
window.addEventListener("focus", () => loadReport());
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) {
    loadReport();
  }
});

loadReport(true);
window.setInterval(loadReport, 2000);
