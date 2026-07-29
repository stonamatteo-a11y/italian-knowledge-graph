const state = {
  tree: [],
  nodes: [],
  selectedId: null,
  isNew: false,
};

const elements = {
  tree: document.querySelector("#tree"),
  search: document.querySelector("#search"),
  form: document.querySelector("#node-form"),
  id: document.querySelector("#node-id"),
  label: document.querySelector("#node-label"),
  description: document.querySelector("#node-description"),
  parent: document.querySelector("#node-parent"),
  language: document.querySelector("#node-language"),
  type: document.querySelector("#node-type"),
  children: document.querySelector("#children-count"),
  path: document.querySelector("#node-path"),
  newNode: document.querySelector("#new-node"),
  deleteNode: document.querySelector("#delete-node"),
  validateNode: document.querySelector("#validate-node"),
  discardNode: document.querySelector("#discard-node"),
  validation: document.querySelector("#validation"),
  validationSummary: document.querySelector("#validation-summary"),
  validationErrors: document.querySelector("#validation-errors"),
};

const parentTypes = {
  macroarea: null,
  area: "macroarea",
  sottoarea: "area",
};

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = response.status === 204 ? null : await response.json();
  if (!response.ok) {
    const message = payload?.detail || payload?.errors?.join("\n") || response.statusText;
    throw new Error(message);
  }
  return payload;
}

function flatten(nodes, result = []) {
  for (const node of nodes) {
    result.push(node);
    flatten(node.children, result);
  }
  return result;
}

function treeButton(node) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "tree-node";
  button.textContent = node.label;
  button.dataset.id = node.id;
  button.title = `${node.id} · ${node.type}`;
  if (node.id === state.selectedId) {
    button.classList.add("selected");
  }
  button.addEventListener("click", () => selectNode(node.id));
  return button;
}

function treeBranch(node) {
  if (node.children.length === 0) {
    const leaf = document.createElement("div");
    leaf.className = "tree-leaf";
    leaf.append(treeButton(node));
    return leaf;
  }

  const details = document.createElement("details");
  const summary = document.createElement("summary");
  summary.append(treeButton(node));
  details.append(summary);
  for (const child of node.children) {
    details.append(treeBranch(child));
  }
  return details;
}

function renderTree() {
  elements.tree.replaceChildren();
  const query = elements.search.value.trim().toLocaleLowerCase("it");
  if (query) {
    const results = document.createElement("div");
    results.className = "search-results";
    for (const node of state.nodes.filter((item) =>
      [item.id, item.label, item.description].some((value) =>
        value.toLocaleLowerCase("it").includes(query),
      ),
    )) {
      const row = document.createElement("div");
      row.append(treeButton(node));
      const id = document.createElement("small");
      id.textContent = `${node.id} · ${node.type}`;
      row.append(id);
      results.append(row);
    }
    elements.tree.append(results);
    return;
  }

  for (const root of state.tree) {
    elements.tree.append(treeBranch(root));
  }
}

function renderParentOptions() {
  const requiredType = parentTypes[elements.type.value];
  const current = elements.parent.value;
  elements.parent.replaceChildren();
  const none = document.createElement("option");
  none.value = "";
  none.textContent = "None";
  elements.parent.append(none);
  for (const node of state.nodes) {
    if (node.type !== requiredType || node.id === state.selectedId) {
      continue;
    }
    const option = document.createElement("option");
    option.value = node.id;
    option.textContent = `${node.label} (${node.id})`;
    elements.parent.append(option);
  }
  elements.parent.value = requiredType ? current : "";
  elements.parent.disabled = requiredType === null;
}

function populateForm(node) {
  elements.id.value = node.id || "";
  elements.label.value = node.label || "";
  elements.description.value = node.description || "";
  elements.language.value = node.language || "it";
  elements.type.value = node.type || "macroarea";
  renderParentOptions();
  elements.parent.value = node.parent_id || "";
  elements.children.textContent = String(node.children_count || 0);
  elements.path.textContent = node.path?.map((part) => part.label).join(" / ") || "-";
  elements.deleteNode.disabled = state.isNew || !state.selectedId;
}

async function loadTree() {
  state.tree = await request("/api/tree");
  state.nodes = flatten(state.tree);
  renderTree();
}

async function selectNode(nodeId) {
  const node = await request(`/api/node/${encodeURIComponent(nodeId)}`);
  state.selectedId = nodeId;
  state.isNew = false;
  populateForm(node);
  renderTree();
}

function formPayload() {
  return {
    id: elements.id.value.trim(),
    type: elements.type.value,
    label: elements.label.value.trim(),
    description: elements.description.value.trim(),
    parent_id: elements.parent.value || null,
    language: elements.language.value.trim(),
  };
}

async function stageForm() {
  const payload = formPayload();
  const node = state.isNew
    ? await request("/api/node", { method: "POST", body: JSON.stringify(payload) })
    : await request(`/api/node/${encodeURIComponent(state.selectedId)}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
  state.selectedId = node.id;
  state.isNew = false;
  await loadTree();
  populateForm(node);
}

function showValidation(result, saved = false) {
  elements.validation.className = `validation-panel ${result.valid ? "valid" : "invalid"}`;
  elements.validationSummary.textContent = result.valid
    ? saved
      ? "✔ Validation passed · Saved"
      : "✔ Validation passed"
    : "❌ Validation failed";
  elements.validationErrors.replaceChildren();
  for (const error of result.errors) {
    const item = document.createElement("li");
    item.textContent = error;
    elements.validationErrors.append(item);
  }
}

function showError(error) {
  showValidation({ valid: false, errors: [error.message] });
}

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await stageForm();
    const result = await request("/api/save", { method: "POST" });
    showValidation(result, result.saved);
    await loadTree();
    await selectNode(state.selectedId);
  } catch (error) {
    showError(error);
  }
});

elements.validateNode.addEventListener("click", async () => {
  try {
    await stageForm();
    showValidation(await request("/api/validate", { method: "POST" }));
  } catch (error) {
    showError(error);
  }
});

elements.discardNode.addEventListener("click", async () => {
  try {
    await request("/api/discard", { method: "POST" });
    await loadTree();
    if (state.selectedId && state.nodes.some((node) => node.id === state.selectedId)) {
      await selectNode(state.selectedId);
    } else {
      state.selectedId = null;
      state.isNew = true;
      populateForm({});
    }
  } catch (error) {
    showError(error);
  }
});

elements.newNode.addEventListener("click", () => {
  state.selectedId = null;
  state.isNew = true;
  populateForm({ type: "macroarea", language: "it" });
  renderTree();
  elements.id.focus();
});

elements.deleteNode.addEventListener("click", async () => {
  if (!state.selectedId || !window.confirm(`Delete ${state.selectedId}?`)) {
    return;
  }
  try {
    await request(`/api/node/${encodeURIComponent(state.selectedId)}`, { method: "DELETE" });
    const result = await request("/api/save", { method: "POST" });
    showValidation(result, result.saved);
    state.selectedId = null;
    state.isNew = true;
    await loadTree();
    populateForm({});
  } catch (error) {
    showError(error);
  }
});

elements.search.addEventListener("input", renderTree);
elements.type.addEventListener("change", renderParentOptions);

loadTree()
  .then(() => selectNode(state.tree[0].id))
  .catch(showError);
