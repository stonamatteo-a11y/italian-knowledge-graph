const state = {
  tree: [],
  nodes: [],
  selectedId: null,
  selectedNode: null,
  isNew: false,
  creationParentId: null,
  dirty: false,
  idManuallyEdited: false,
  expandedIds: new Set(),
  searchRequest: 0,
  populating: false,
  importToken: null,
  importFile: null,
  importPreviewImportable: false,
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
  breadcrumb: document.querySelector("#breadcrumb"),
  addChild: document.querySelector("#add-child"),
  conceptNotice: document.querySelector("#concept-notice"),
  deleteNode: document.querySelector("#delete-node"),
  validateNode: document.querySelector("#validate-node"),
  discardNode: document.querySelector("#discard-node"),
  saveStatus: document.querySelector("#save-status"),
  validationStatus: document.querySelector("#validation-status"),
  validation: document.querySelector("#validation"),
  validationSummary: document.querySelector("#validation-summary"),
  validationErrors: document.querySelector("#validation-errors"),
  importOntology: document.querySelector("#import-ontology"),
  importFile: document.querySelector("#import-file"),
  importDialog: document.querySelector("#import-dialog"),
  closeImport: document.querySelector("#close-import"),
  cancelImport: document.querySelector("#cancel-import"),
  confirmImport: document.querySelector("#confirm-import"),
  importFormat: document.querySelector("#import-format"),
  importFound: document.querySelector("#import-found"),
  importRelationships: document.querySelector("#import-relationships"),
  importMode: document.querySelector("#import-mode"),
  importSections: document.querySelector("#import-sections"),
  openQuality: document.querySelector("#open-quality"),
  prepareContribution: document.querySelector("#prepare-contribution"),
  contributionDialog: document.querySelector("#contribution-dialog"),
  closeContribution: document.querySelector("#close-contribution"),
  contributionContent: document.querySelector("#contribution-content"),
  contributionFilename: document.querySelector("#contribution-filename"),
  exportContribution: document.querySelector("#export-contribution"),
  prepareContributionGit: document.querySelector("#prepare-contribution-git"),
  createGuidedContribution: document.querySelector("#create-guided-contribution"),
  guidedDialog: document.querySelector("#guided-contribution-dialog"),
  closeGuidedContribution: document.querySelector("#close-guided-contribution"),
  guidedDomain: document.querySelector("#guided-domain"),
  guidedArea: document.querySelector("#guided-area"),
  guidedSubarea: document.querySelector("#guided-subarea"),
  guidedNode: document.querySelector("#guided-node"),
  guidedNodeLimit: document.querySelector("#guided-node-limit"),
  guidedFields: document.querySelector("#guided-fields"),
  guidedSummary: document.querySelector("#guided-summary"),
  guidedResult: document.querySelector("#guided-result"),
  guidedResultMessage: document.querySelector("#guided-result-message"),
  openGuidedFolder: document.querySelector("#open-guided-folder"),
  openGuidedDocument: document.querySelector("#open-guided-document"),
  guidedFilename: document.querySelector("#guided-filename"),
  previewGuidedContribution: document.querySelector("#preview-guided-contribution"),
  generateGuidedContribution: document.querySelector("#generate-guided-contribution"),
};

const parentTypes = {
  macroarea: null,
  area: "macroarea",
  sottoarea: "area",
};

const italianLabelCollator = new Intl.Collator("it", {
  sensitivity: "base",
  usage: "sort",
});

function compareByVisibleLabel(left, right) {
  return (
    italianLabelCollator.compare(left.label || "", right.label || "") ||
    italianLabelCollator.compare(left.type || "", right.type || "") ||
    italianLabelCollator.compare(left.id || "", right.id || "")
  );
}

function stableLabelSort(values) {
  return values
    .map((value, index) => ({ value, index }))
    .sort(
      (left, right) =>
        compareByVisibleLabel(left.value, right.value) || left.index - right.index,
    )
    .map(({ value }) => value);
}

function sortTreeForDisplay(nodes) {
  return stableLabelSort(nodes).map((node) => ({
    ...node,
    children: sortTreeForDisplay(node.children || []),
  }));
}

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

function normalizeSearch(value) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("it");
}

function highlightedText(value, query) {
  const fragment = document.createDocumentFragment();
  if (!query) {
    fragment.append(value);
    return fragment;
  }
  const index = normalizeSearch(value).indexOf(normalizeSearch(query));
  if (index < 0) {
    fragment.append(value);
    return fragment;
  }
  fragment.append(value.slice(0, index));
  const mark = document.createElement("mark");
  mark.textContent = value.slice(index, index + query.length);
  fragment.append(mark, value.slice(index + query.length));
  return fragment;
}

function treeButton(node) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `tree-node type-${node.type}`;
  button.append(highlightedText(node.label, elements.search.value.trim()));
  button.dataset.id = node.id;
  button.title = `${node.id} · ${node.type}`;
  if (node.id === state.selectedId) {
    button.classList.add("selected");
  }
  button.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    selectNode(node.id);
  });
  return button;
}

function treeBranch(node, searching) {
  if (node.children.length === 0) {
    const leaf = document.createElement("div");
    leaf.className = "tree-leaf";
    leaf.append(treeButton(node));
    return leaf;
  }

  const details = document.createElement("details");
  details.dataset.id = node.id;
  details.open = searching || state.expandedIds.has(node.id);
  details.addEventListener("toggle", () => {
    if (searching) {
      return;
    }
    if (details.open) {
      state.expandedIds.add(node.id);
    } else {
      state.expandedIds.delete(node.id);
    }
  });
  const summary = document.createElement("summary");
  summary.append(treeButton(node));
  details.append(summary);
  for (const child of node.children) {
    details.append(treeBranch(child, searching));
  }
  return details;
}

function renderTree() {
  elements.tree.replaceChildren();
  const searching = Boolean(elements.search.value.trim());
  for (const root of state.tree) {
    elements.tree.append(treeBranch(root, searching));
  }
}

function renderParentOptions() {
  const requiredType = parentTypes[elements.type.value];
  const current = elements.parent.value;
  elements.parent.replaceChildren();
  const none = document.createElement("option");
  none.value = "";
  none.textContent = t("field.none");
  elements.parent.append(none);
  for (const node of stableLabelSort(state.nodes)) {
    if (
      node.type !== requiredType ||
      (!state.isNew && node.id === state.selectedId)
    ) {
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

function renderBreadcrumb(path = []) {
  elements.breadcrumb.replaceChildren();
  path.forEach((part, index) => {
    if (index > 0) {
      const separator = document.createElement("span");
      separator.textContent = " > ";
      elements.breadcrumb.append(separator);
    }
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = part.label;
    button.addEventListener("click", () => revealNode(part.id));
    elements.breadcrumb.append(button);
  });
}

function renderAddAction() {
  const node = state.selectedNode;
  const childType = node?.child_type || "macroarea";
  const supported = node ? node.child_creation_supported : true;
  elements.addChild.textContent =
    childType === "concetto"
      ? t("action.add_concept")
      : node
        ? t("action.add_child")
        : t("action.add_macroarea");
  elements.addChild.disabled = !supported || state.isNew;
  elements.conceptNotice.hidden = childType !== "concetto";
}

function setDirty(dirty) {
  state.dirty = dirty;
  elements.saveStatus.textContent = dirty ? t("status.unsaved") : t("status.saved");
  elements.saveStatus.className = `save-status ${dirty ? "dirty" : "saved"}`;
}

function populateForm(node, preserveDirty = false) {
  state.populating = true;
  elements.id.value = node.id || "";
  elements.label.value = node.label || "";
  elements.description.value = node.description || "";
  elements.language.value = node.language || "it";
  elements.type.value = node.type || "macroarea";
  renderParentOptions();
  elements.parent.value = node.parent_id || "";
  elements.children.textContent = String(node.children_count || 0);
  elements.path.textContent = node.path?.map((part) => part.label).join(" / ") || "-";
  renderBreadcrumb(node.path || []);
  elements.deleteNode.disabled = state.isNew || !state.selectedId;
  state.populating = false;
  if (!preserveDirty) {
    setDirty(false);
  }
  renderAddAction();
}

async function loadTree(query = elements.search.value.trim()) {
  const requestId = ++state.searchRequest;
  const tree = await request(`/api/tree?q=${encodeURIComponent(query)}`);
  if (requestId !== state.searchRequest) {
    return;
  }
  state.tree = sortTreeForDisplay(tree);
  if (!query) {
    state.nodes = flatten(state.tree);
  }
  renderTree();
}

async function discardWorkingCopy() {
  await request("/api/discard", { method: "POST" });
  setDirty(false);
  state.isNew = false;
  state.creationParentId = null;
  await loadTree("");
}

async function confirmDiscard() {
  if (!state.dirty) {
    return true;
  }
  if (!window.confirm(t("confirm.discard"))) {
    return false;
  }
  await discardWorkingCopy();
  return true;
}

async function selectNode(nodeId, force = false) {
  if (!force && nodeId !== state.selectedId && !(await confirmDiscard())) {
    return;
  }
  const node = await request(`/api/node/${encodeURIComponent(nodeId)}`);
  state.selectedId = nodeId;
  state.selectedNode = node;
  state.isNew = false;
  state.creationParentId = null;
  state.idManuallyEdited = false;
  for (const part of node.path.slice(0, -1)) {
    state.expandedIds.add(part.id);
  }
  populateForm(node);
  renderTree();
}

async function revealNode(nodeId) {
  elements.search.value = "";
  await loadTree("");
  await selectNode(nodeId);
  document.querySelector(`.tree-node[data-id="${CSS.escape(nodeId)}"]`)?.scrollIntoView({
    block: "center",
  });
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
  state.selectedNode = node;
  state.isNew = false;
  state.creationParentId = null;
  await loadTree("");
  populateForm(node, true);
  setDirty(true);
  return node;
}

function validationNodeId(error) {
  return [...state.nodes]
    .sort((left, right) => right.id.length - left.id.length)
    .find((node) => error.includes(node.id))?.id;
}

function showValidation(result, saved = false) {
  elements.validation.className = `validation-panel ${result.valid ? "valid" : "invalid"}`;
  elements.validationSummary.textContent = result.valid
    ? saved
      ? t("validation.passed_saved")
      : t("validation.passed")
    : t("validation.failed");
  elements.validationStatus.textContent = result.valid
    ? t("validation.valid")
    : t("validation.invalid", { count: result.errors.length });
  elements.validationStatus.className = result.valid ? "status-valid" : "status-invalid";
  elements.validationErrors.replaceChildren();
  for (const error of result.errors) {
    const item = document.createElement("li");
    const nodeId = validationNodeId(error);
    if (nodeId) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "validation-link";
      button.textContent = error;
      button.addEventListener("click", () => revealNode(nodeId));
      item.append(button);
    } else {
      item.textContent = error;
    }
    elements.validationErrors.append(item);
  }
  if (!result.valid) {
    elements.validation.open = true;
  }
}

async function runValidation() {
  const result = await request("/api/validate", { method: "POST" });
  showValidation(result);
  return result;
}

function showError(error) {
  showValidation({ valid: false, errors: [error.message] });
}

function openQualityCenter() {
  const qualityWindow = window.open(
    "/static/quality.html",
    "ikg-knowledge-quality-center",
    "popup=yes,resizable=yes,scrollbars=yes,width=1180,height=820",
  );
  qualityWindow?.focus();
}

function contributionList(title, values) {
  const section = document.createElement("section");
  const heading = document.createElement("h3");
  heading.textContent = `${title} (${values.length})`;
  section.append(heading);
  if (values.length) {
    const list = document.createElement("ul");
    for (const value of values) {
      const item = document.createElement("li");
      item.textContent = typeof value === "string" ? value : JSON.stringify(value);
      list.append(item);
    }
    section.append(list);
  }
  return section;
}

function acceptedContributionWarnings() {
  return [
    ...elements.contributionContent.querySelectorAll(
      ".contribution-warning input:checked",
    ),
  ].map((checkbox) => checkbox.value);
}

function updateContributionActions(preview) {
  const warnings = [
    ...elements.contributionContent.querySelectorAll(".contribution-warning input"),
  ];
  const warningsAccepted = warnings.every((checkbox) => checkbox.checked);
  elements.exportContribution.disabled = !preview.preparable || !warningsAccepted;
  elements.prepareContributionGit.hidden = !preview.git.available;
  elements.prepareContributionGit.disabled =
    !preview.preparable ||
    !warningsAccepted ||
    preview.git.blockers.length > 0;
}

function renderContributionPreview(preview) {
  elements.contributionContent.replaceChildren();
  const nodes = preview.changes.nodes;
  const relationships = preview.changes.relationships;
  const summary = document.createElement("dl");
  summary.className = "contribution-summary";
  for (const [label, value] of Object.entries({
    [t("contribution.nodes_added")]: nodes.added.length,
    [t("contribution.nodes_modified")]: nodes.modified.length,
    [t("contribution.nodes_removed")]: nodes.removed.length,
    [t("contribution.relationships_added")]: relationships.added.length,
    [t("contribution.relationships_modified")]: relationships.modified.length,
    [t("contribution.relationships_removed")]: relationships.removed.length,
    [t("contribution.quality_before")]: preview.quality.before,
    [t("contribution.quality_after")]: preview.quality.after,
  })) {
    const item = document.createElement("div");
    const term = document.createElement("dt");
    term.textContent = label;
    const detail = document.createElement("dd");
    detail.textContent = String(value);
    item.append(term, detail);
    summary.append(item);
  }
  elements.contributionContent.append(
    summary,
    contributionList(t("contribution.canonical_files"), preview.files),
    contributionList(t("contribution.blocking_errors"), preview.errors),
    contributionList(t("contribution.excluded"), preview.excluded),
  );

  const warningSection = document.createElement("section");
  const warningHeading = document.createElement("h3");
  warningHeading.textContent = t("contribution.warning_count", {
    count: preview.warnings.length,
  });
  warningSection.append(warningHeading);
  if (preview.warnings.length) {
    const acceptAll = document.createElement("label");
    acceptAll.className = "contribution-accept-all";
    const allCheckbox = document.createElement("input");
    allCheckbox.type = "checkbox";
    acceptAll.append(allCheckbox, document.createTextNode(t("contribution.accept_all")));
    warningSection.append(acceptAll);
    for (const warning of preview.warnings) {
      const label = document.createElement("label");
      label.className = "contribution-warning";
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.value = warning.id;
      checkbox.addEventListener("change", () => updateContributionActions(preview));
      label.append(
        checkbox,
        document.createTextNode(
          `${warning.node_id || t("ontology.name")} · ${warning.title}: ${warning.detail}`,
        ),
      );
      warningSection.append(label);
    }
    allCheckbox.addEventListener("change", () => {
      for (const checkbox of warningSection.querySelectorAll(
        ".contribution-warning input",
      )) {
        checkbox.checked = allCheckbox.checked;
      }
      updateContributionActions(preview);
    });
  }
  elements.contributionContent.append(warningSection);

  if (preview.git.blockers.length) {
    elements.contributionContent.append(
      contributionList(t("contribution.git_blockers"), preview.git.blockers),
    );
  }
  const title = document.createElement("section");
  title.innerHTML = `<h3>${t("contribution.commit_title")}</h3>`;
  const titleValue = document.createElement("code");
  titleValue.textContent = preview.commit_title;
  title.append(titleValue);
  const body = document.createElement("section");
  body.innerHTML = `<h3>${t("contribution.pr_description")}</h3>`;
  const bodyValue = document.createElement("pre");
  bodyValue.textContent = preview.pull_request_body;
  body.append(bodyValue);
  const diff = document.createElement("section");
  diff.innerHTML = `<h3>${t("contribution.canonical_diff")}</h3>`;
  const diffValue = document.createElement("pre");
  diffValue.className = "contribution-diff";
  diffValue.textContent = preview.diff || t("contribution.no_diff");
  diff.append(diffValue);
  elements.contributionContent.append(title, body, diff);
  elements.contributionDialog.dataset.preview = JSON.stringify(preview);
  updateContributionActions(preview);
}

async function openContribution() {
  const preview = await request("/api/contribution/preview");
  renderContributionPreview(preview);
  elements.contributionDialog.showModal();
}

function renderContributionResult(result) {
  elements.contributionContent.replaceChildren();
  const heading = document.createElement("h3");
  heading.textContent = t("contribution.prepared");
  const report = document.createElement("pre");
  report.textContent = JSON.stringify(result, null, 2);
  elements.contributionContent.append(heading, report);
  elements.exportContribution.disabled = true;
  elements.prepareContributionGit.disabled = true;
}

async function refreshContributionAvailability() {
  const status = await request("/api/contribution/status");
  elements.prepareContribution.disabled = !status.changed;
}

function guidedChildren(parentId) {
  return state.nodes.filter((node) => node.parent_id === parentId);
}

function fillGuidedSelect(select, nodes, optional = false) {
  select.replaceChildren();
  if (optional) {
    const empty = document.createElement("option");
    empty.value = "";
    empty.textContent = t("field.all");
    select.append(empty);
  }
  for (const node of stableLabelSort(nodes)) {
    const option = document.createElement("option");
    option.value = node.id;
    option.textContent = node.label;
    select.append(option);
  }
  select.disabled = nodes.length === 0;
}

function updateGuidedHierarchy(level = "domain") {
  if (level === "domain") {
    fillGuidedSelect(elements.guidedArea, guidedChildren(elements.guidedDomain.value), true);
  }
  if (level === "domain" || level === "area") {
    fillGuidedSelect(
      elements.guidedSubarea,
      guidedChildren(elements.guidedArea.value),
      true,
    );
  }
  fillGuidedSelect(
    elements.guidedNode,
    guidedChildren(elements.guidedSubarea.value || elements.guidedArea.value),
    true,
  );
  elements.generateGuidedContribution.disabled = true;
}

function guidedPayload() {
  return {
    domain_id: elements.guidedDomain.value,
    area_id: elements.guidedArea.value || null,
    subarea_id: elements.guidedSubarea.value || null,
    node_id: elements.guidedNode.value || null,
    fields: [...elements.guidedFields.querySelectorAll("input:checked")].map(
      (input) => input.value,
    ),
    node_limit: elements.guidedNodeLimit.value,
    filename: elements.guidedFilename.value.trim(),
  };
}

function showGuidedSummary(summary) {
  const list = document.createElement("dl");
  for (const [label, value] of [
    [t("guided.domain"), summary.domain],
    [t("guided.area"), summary.area || "-"],
    [t("guided.subarea"), summary.subarea || "-"],
    [t("guided.node"), summary.node || "-"],
    [t("guided.available_nodes"), summary.total_nodes],
    [t("guided.included_nodes"), summary.included_nodes],
    [t("guided.excluded_nodes"), summary.excluded_nodes],
    [t("guided.fields"), summary.fields],
    [t("guided.estimated_time"), t("guided.minutes", { count: summary.estimated_minutes })],
    [t("contribution.package"), elements.guidedFilename.value.trim()],
  ]) {
    const row = document.createElement("div");
    const term = document.createElement("dt");
    const detail = document.createElement("dd");
    term.textContent = label;
    detail.textContent = String(value);
    row.append(term, detail);
    list.append(row);
  }
  elements.guidedSummary.replaceChildren(list);
  elements.generateGuidedContribution.disabled = false;
}

async function openGuidedContribution() {
  if (!state.nodes.length) {
    await loadTree("");
  }
  fillGuidedSelect(
    elements.guidedDomain,
    state.nodes.filter((node) => node.type === "macroarea"),
  );
  updateGuidedHierarchy();
  elements.guidedResult.hidden = true;
  elements.guidedDialog.showModal();
}

function renderImportList(title, values, className = "") {
  if (!values.length) {
    return;
  }
  const section = document.createElement("section");
  section.className = className;
  const heading = document.createElement("h3");
  heading.textContent = `${title} (${values.length})`;
  const list = document.createElement("ul");
  for (const value of values) {
    const item = document.createElement("li");
    item.textContent = value;
    list.append(item);
  }
  section.append(heading, list);
  elements.importSections.append(section);
}

function showImportPreview(preview) {
  state.importToken = preview.token;
  state.importPreviewImportable = preview.importable;
  elements.importFormat.textContent = preview.format;
  elements.importFound.textContent = String(preview.nodes_found);
  elements.importRelationships.textContent = String(preview.relationships_found);
  elements.importSections.replaceChildren();
  renderImportList(t("import.information"), [
    ...preview.information,
    t("import.nodes_to_add", { count: preview.nodes_to_add }),
  ]);
  renderImportList(t("import.modifications"), preview.modifications);
  renderImportList(t("import.collisions"), preview.collisions, "import-error");
  renderImportList(t("import.duplicates"), preview.duplicates);
  renderMappingOptions(preview.unmapped_types);
  renderWarningOptions(preview.warning_options);
  renderImportList(t("import.blocking_errors"), preview.errors, "import-error");
  updateImportConfirmation();
  if (!elements.importDialog.open) {
    elements.importDialog.showModal();
  }
}

function updateImportConfirmation() {
  const warnings = [...elements.importSections.querySelectorAll(".warning-choice input")];
  const warningsAccepted = warnings.every((checkbox) => checkbox.checked);
  elements.confirmImport.disabled =
    !state.importPreviewImportable || !warningsAccepted;
}

function renderMappingOptions(types) {
  if (!types.length) {
    return;
  }
  const section = document.createElement("section");
  section.className = "mapping-options";
  const heading = document.createElement("h3");
  heading.textContent = t("import.required_mappings", { count: types.length });
  section.append(heading);
  for (const externalType of types) {
    const row = document.createElement("label");
    row.textContent = externalType;
    const select = document.createElement("select");
    select.dataset.externalType = externalType;
    for (const canonicalType of ["macroarea", "area", "sottoarea"]) {
      const option = document.createElement("option");
      option.value = canonicalType;
      option.textContent = canonicalType;
      select.append(option);
    }
    row.append(select);
    section.append(row);
  }
  const apply = document.createElement("button");
  apply.type = "button";
  apply.textContent = t("import.save_mapping");
  apply.addEventListener("click", async () => {
    if (!state.importFile) {
      return;
    }
    const mappings = Object.fromEntries(
      [...section.querySelectorAll("select")].map((select) => [
        select.dataset.externalType,
        select.value,
      ]),
    );
    try {
      await previewImport(state.importFile, mappings, true);
    } catch (error) {
      showError(error);
    }
  });
  section.append(apply);
  elements.importSections.append(section);
}

function renderWarningOptions(warnings) {
  if (!warnings.length) {
    return;
  }
  const section = document.createElement("section");
  section.className = "import-warning";
  const heading = document.createElement("h3");
  heading.textContent = t("import.warning_count", { count: warnings.length });
  section.append(heading);
  for (const warning of warnings) {
    const label = document.createElement("label");
    label.className = "warning-choice";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = warning.id;
    checkbox.checked = false;
    checkbox.addEventListener("change", updateImportConfirmation);
    label.append(
      checkbox,
      document.createTextNode(t("import.apply_fix", { message: warning.message })),
    );
    section.append(label);
  }
  elements.importSections.append(section);
}

async function previewImport(file, mappings = {}, persistMappings = false) {
  const parameters = new URLSearchParams({
    filename: file.name,
    mode: elements.importMode.value,
    mappings: JSON.stringify(mappings),
    persist_mappings: String(persistMappings),
  });
  const preview = await request(`/api/import/preview?${parameters}`, {
    method: "POST",
    headers: { "Content-Type": "application/octet-stream" },
    body: file,
  });
  showImportPreview(preview);
}

function closeImportDialog() {
  state.importToken = null;
  state.importFile = null;
  state.importPreviewImportable = false;
  elements.importDialog.close();
  elements.importFile.value = "";
}

async function suggestId() {
  if (!state.isNew || state.idManuallyEdited || !elements.label.value.trim()) {
    return;
  }
  const parameters = new URLSearchParams({
    label: elements.label.value.trim(),
  });
  if (elements.parent.value) {
    parameters.set("parent_id", elements.parent.value);
  }
  const suggestion = await request(`/api/suggest-id?${parameters}`);
  if (!state.idManuallyEdited) {
    elements.id.value = suggestion.id;
  }
}

async function startAddChild() {
  if (!(await confirmDiscard())) {
    return;
  }
  const parent = state.selectedNode;
  const type = parent?.child_type || "macroarea";
  if (type === "concetto") {
    return;
  }
  state.isNew = true;
  state.creationParentId = parent?.id || null;
  state.idManuallyEdited = false;
  populateForm(
    {
      type,
      parent_id: state.creationParentId,
      language: "it",
      path: parent?.path || [],
    },
    true,
  );
  elements.parent.value = state.creationParentId || "";
  setDirty(false);
  renderAddAction();
  elements.label.focus();
}

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await stageForm();
    const result = await request("/api/save", { method: "POST" });
    showValidation(result, result.saved);
    setDirty(false);
    await loadTree("");
    await selectNode(state.selectedId, true);
  } catch (error) {
    showError(error);
  }
});

elements.validateNode.addEventListener("click", async () => {
  try {
    await stageForm();
    await runValidation();
  } catch (error) {
    showError(error);
  }
});

elements.discardNode.addEventListener("click", async () => {
  try {
    const selectedId = state.isNew ? state.creationParentId : state.selectedId;
    await discardWorkingCopy();
    if (selectedId && state.nodes.some((node) => node.id === selectedId)) {
      await selectNode(selectedId, true);
    } else if (state.tree[0]) {
      await selectNode(state.tree[0].id, true);
    }
  } catch (error) {
    showError(error);
  }
});

elements.addChild.addEventListener("click", () => {
  startAddChild().catch(showError);
});

elements.deleteNode.addEventListener("click", async () => {
  if (!state.selectedId || !state.selectedNode) {
    return;
  }
  const node = state.selectedNode;
  const confirmation = t("confirm.delete", {
    label: node.label,
    id: node.id,
    count: node.descendants_count,
  });
  if (!window.confirm(confirmation)) {
    return;
  }
  try {
    const parentId = node.parent_id;
    await request(`/api/node/${encodeURIComponent(node.id)}`, { method: "DELETE" });
    await runValidation();
    const result = await request("/api/save", { method: "POST" });
    showValidation(result, result.saved);
    setDirty(false);
    state.selectedId = null;
    state.selectedNode = null;
    await loadTree("");
    if (parentId) {
      await selectNode(parentId, true);
    } else if (state.tree[0]) {
      await selectNode(state.tree[0].id, true);
    }
  } catch (error) {
    showError(error);
  }
});

elements.search.addEventListener("input", () => {
  loadTree().catch(showError);
});
elements.importOntology.addEventListener("click", async () => {
  if (await confirmDiscard()) {
    elements.importFile.click();
  }
});
elements.openQuality.addEventListener("click", () => {
  openQualityCenter();
});
elements.prepareContribution.addEventListener("click", () => {
  openContribution().catch(showError);
});
elements.closeContribution.addEventListener("click", () => {
  elements.contributionDialog.close();
});
elements.exportContribution.addEventListener("click", async () => {
  try {
    const result = await request("/api/contribution/package", {
      method: "POST",
      body: JSON.stringify({
        filename: elements.contributionFilename.value.trim(),
        accepted_warning_ids: acceptedContributionWarnings(),
      }),
    });
    renderContributionResult(result);
  } catch (error) {
    showError(error);
  }
});
elements.prepareContributionGit.addEventListener("click", async () => {
  try {
    const result = await request("/api/contribution/git", {
      method: "POST",
      body: JSON.stringify({
        accepted_warning_ids: acceptedContributionWarnings(),
      }),
    });
    renderContributionResult(result);
  } catch (error) {
    showError(error);
  }
});
elements.createGuidedContribution.addEventListener("click", () => {
  openGuidedContribution().catch(showError);
});
elements.closeGuidedContribution.addEventListener("click", () => {
  elements.guidedDialog.close();
});
elements.guidedDomain.addEventListener("change", () => updateGuidedHierarchy("domain"));
elements.guidedArea.addEventListener("change", () => updateGuidedHierarchy("area"));
elements.guidedSubarea.addEventListener("change", () => updateGuidedHierarchy("subarea"));
elements.guidedNode.addEventListener("change", () => {
  elements.generateGuidedContribution.disabled = true;
});
elements.guidedNodeLimit.addEventListener("change", () => {
  elements.generateGuidedContribution.disabled = true;
});
elements.guidedFields.addEventListener("change", () => {
  elements.generateGuidedContribution.disabled = true;
});
elements.previewGuidedContribution.addEventListener("click", async () => {
  try {
    showGuidedSummary(
      await request("/api/contribution/guided/preview", {
        method: "POST",
        body: JSON.stringify(guidedPayload()),
      }),
    );
  } catch (error) {
    showError(error);
  }
});
elements.generateGuidedContribution.addEventListener("click", async () => {
  try {
    const result = await request("/api/contribution/guided/package", {
      method: "POST",
      body: JSON.stringify(guidedPayload()),
    });
    elements.guidedResult.hidden = false;
    elements.guidedResultMessage.textContent = t("guided.success", {
      path: result.path,
      count: result.included_nodes,
    });
    elements.guidedResult.dataset.filename = result.filename;
  } catch (error) {
    showError(error);
  }
});
for (const [button, target] of [
  [elements.openGuidedFolder, "folder"],
  [elements.openGuidedDocument, "document"],
]) {
  button.addEventListener("click", async () => {
    try {
      const parameters = new URLSearchParams({
        filename: elements.guidedResult.dataset.filename,
        target,
      });
      await request(`/api/contribution/guided/open?${parameters}`, { method: "POST" });
    } catch (error) {
      showError(error);
    }
  });
}
elements.importFile.addEventListener("change", () => {
  const file = elements.importFile.files[0];
  if (file) {
    state.importFile = file;
    previewImport(file).catch(showError);
  }
});
elements.closeImport.addEventListener("click", closeImportDialog);
elements.cancelImport.addEventListener("click", closeImportDialog);
elements.confirmImport.addEventListener("click", async () => {
  if (!state.importToken) {
    return;
  }
  try {
    const result = await request("/api/import/confirm", {
      method: "POST",
      body: JSON.stringify({
        token: state.importToken,
        mode: elements.importMode.value,
        accepted_warnings: [
          ...elements.importSections.querySelectorAll(".warning-choice input:checked"),
        ].map((checkbox) => checkbox.value),
      }),
    });
    closeImportDialog();
    state.selectedId = null;
    state.selectedNode = null;
    await loadTree("");
    if (state.tree[0]) {
      await selectNode(state.tree[0].id, true);
    }
    showValidation({ valid: true, errors: [] }, true);
    const report = result.report;
    elements.validationSummary.textContent = t("import.completed", {
      count: report.summary.nodes_added,
    });
    elements.validationErrors.replaceChildren();
    for (const [label, value] of [
      [t("report.file"), report.file],
      [t("report.format"), report.format],
      [t("report.parser"), report.parser],
      [t("report.files_modified"), report.files_modified.join(", ")],
    ]) {
      const item = document.createElement("li");
      item.textContent = `${label}: ${value}`;
      elements.validationErrors.append(item);
    }
  } catch (error) {
    showError(error);
  }
});
elements.type.addEventListener("change", renderParentOptions);
elements.label.addEventListener("input", () => {
  suggestId().catch(showError);
});
elements.id.addEventListener("input", () => {
  if (!state.populating && state.isNew) {
    state.idManuallyEdited = true;
  }
});
elements.form.addEventListener("input", () => {
  if (!state.populating) {
    setDirty(true);
  }
});
elements.form.addEventListener("change", () => {
  if (!state.populating) {
    setDirty(true);
  }
});
window.addEventListener("beforeunload", (event) => {
  if (state.dirty) {
    event.preventDefault();
    event.returnValue = "";
  }
});
window.addEventListener("message", (event) => {
  if (
    event.origin === window.location.origin &&
    event.data?.type === "ikg:navigate-node" &&
    typeof event.data.nodeId === "string"
  ) {
    revealNode(event.data.nodeId).catch(showError);
  }
});

initializeI18n().then(() => {
  loadTree("")
    .then(async () => {
      if (state.tree[0]) {
        await selectNode(state.tree[0].id, true);
      }
      await runValidation();
    })
    .catch(showError);
  refreshContributionAvailability().catch(showError);
  window.setInterval(() => {
    refreshContributionAvailability().catch(showError);
  }, 2000);
});
