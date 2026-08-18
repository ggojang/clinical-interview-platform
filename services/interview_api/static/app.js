"use strict";

const MAX_FILE_BYTES = 1024 * 1024;
const FHIR_TRANSLATION_URL = "http://hl7.org/fhir/StructureDefinition/translation";
const FHIR_RENDERING_XHTML_URL = "http://hl7.org/fhir/StructureDefinition/rendering-xhtml";
const FHIR_QUESTIONNAIRE_HIDDEN_URL = "http://hl7.org/fhir/StructureDefinition/questionnaire-hidden";
const FHIR_QUESTIONNAIRE_UNIT_URL = "http://hl7.org/fhir/StructureDefinition/questionnaire-unit";
const FHIR_QUESTIONNAIRE_UNIT_OPTION_URL = "http://hl7.org/fhir/StructureDefinition/questionnaire-unitOption";
const FHIR_QUESTIONNAIRE_ITEM_CONTROL_URL = "http://hl7.org/fhir/StructureDefinition/questionnaire-itemControl";
const FHIR_QUESTIONNAIRE_SLIDER_STEP_URL = "http://hl7.org/fhir/StructureDefinition/questionnaire-sliderStepValue";
const FHIR_MIN_VALUE_URL = "http://hl7.org/fhir/StructureDefinition/minValue";
const FHIR_MAX_VALUE_URL = "http://hl7.org/fhir/StructureDefinition/maxValue";
const SDC_STATUS = {
  status: "not_implemented",
  specification: "HL7 FHIR Structured Data Capture",
  planned_output: "FHIR transaction Bundle",
  reason: "서버의 SDC Extraction adapter가 아직 구현되지 않았습니다. 임상 데이터로 추출된 것처럼 표시하지 않습니다."
};

const state = {
  apiKey: "",
  apiMode: "anonymous_demo",
  mode: "structured",
  displayLocale: "auto",
  sourceVersion: "auto",
  questionnaire: null,
  questionnaireSource: "",
  questionnaireResponse: null,
  handoff: {},
  providers: [],
  sessionId: null,
  adaptivePurpose: "clinical_adaptive",
  adaptiveStarted: false,
  adaptiveBusy: false,
  adaptiveRequestSerial: 0,
  adaptiveHistory: [],
  currentAdaptiveQuestion: null,
  fixedQuestions: [],
  fixedAnswers: [],
  fixedIndex: 0,
  fixedTitle: "",
  structuredAnswers: new Map(),
  valueSetOptions: new Map(),
  valueSetErrors: new Map(),
  terminologyAvailable: false
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const clone = (value) => JSON.parse(JSON.stringify(value));
const pretty = (value) => JSON.stringify(value, null, 2);

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 3200);
}

async function api(path, options = {}) {
  const anonymousPath = path
    .replace(/^\/v1\/llm\/providers$/, "/demo-api/config")
    .replace(/^\/v1\/terminology/, "/demo-api/terminology")
    .replace(/^\/v1\/demo\/resources/, "/demo-api/resources")
    .replace(/^\/v1\/sessions/, "/demo-api/sessions");
  const target = state.apiMode === "authenticated" ? path : anonymousPath;
  const headers = { ...(options.headers || {}) };
  if (state.apiMode === "authenticated") headers.Authorization = `Bearer ${state.apiKey}`;
  if (options.body) headers["Content-Type"] = "application/json";
  const response = await fetch(target, { ...options, headers });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(payload.error?.message || `API 오류 (${response.status})`);
    error.code = payload.error?.code;
    throw error;
  }
  return payload;
}

function setConnected(connected, text) {
  const badge = $("#serviceState");
  badge.classList.toggle("connected", connected);
  badge.lastElementChild.textContent = text;
}

function setMode(mode) {
  state.mode = mode;
  $$(".mode-card").forEach((button) => {
    const active = button.dataset.mode === mode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-checked", String(active));
  });
  $$(".workspace").forEach((workspace) => workspace.classList.remove("active"));
  $(`#${mode}Workspace`).classList.add("active");
  const labels = {
    structured: ["FHIR Questionnaire", "R4 / R5"],
    fixed: ["정형 대화", "Fixed questions"],
    adaptive: ["비정형 대화", "Purpose first"]
  };
  $("#inputPanelTitle").textContent = labels[mode][0];
  $("#inputBadge").textContent = labels[mode][1];
  if (mode === "adaptive") prepareAdaptiveConversation();
  updateOutputs();
  syncRunnerVisibility();
}

function canonical(questionnaire) {
  if (questionnaire?.url) return questionnaire.version ? `${questionnaire.url}|${questionnaire.version}` : questionnaire.url;
  return questionnaire?.id ? `Questionnaire/${questionnaire.id}` : undefined;
}

function walkItems(items, visit) {
  (items || []).forEach((item) => {
    visit(item);
    walkItems(item.item, visit);
  });
}

function isQuestionnaireItemHidden(item) {
  return (item?.extension || []).some((extension) => (
    extension.url === FHIR_QUESTIONNAIRE_HIDDEN_URL && extension.valueBoolean === true
  ));
}

function questionnaireItemControlCode(item) {
  const control = (item?.extension || []).find((extension) => extension.url === FHIR_QUESTIONNAIRE_ITEM_CONTROL_URL);
  return control?.valueCodeableConcept?.coding?.[0]?.code || "";
}

function extensionNumber(item, url) {
  const extension = (item?.extension || []).find((candidate) => candidate.url === url);
  const value = extension ? fhirValue(extension) : undefined;
  return Number.isFinite(Number(value)) ? Number(value) : undefined;
}

function numericControlConfig(item) {
  const minimum = extensionNumber(item, FHIR_MIN_VALUE_URL);
  const maximum = extensionNumber(item, FHIR_MAX_VALUE_URL);
  const explicitStep = extensionNumber(item, FHIR_QUESTIONNAIRE_SLIDER_STEP_URL);
  const step = explicitStep ?? (item?.type === "integer" ? 1 : "any");
  return {
    minimum,
    maximum,
    step,
    slider: questionnaireItemControlCode(item) === "slider"
  };
}

function hasRenderableQuestionnaireContent(item) {
  if (!item || isQuestionnaireItemHidden(item) || !isItemEnabled(item)) return false;
  if (item.type === "group") return (item.item || []).some(hasRenderableQuestionnaireContent);
  return true;
}

function isSliderBoundaryDisplay(item) {
  return item?.type === "display" && ["lower", "upper"].includes(questionnaireItemControlCode(item));
}

function answerBearingItems(questionnaire) {
  const result = [];
  walkItems(questionnaire?.item, (item) => {
    if (!isQuestionnaireItemHidden(item) && !['group', 'display'].includes(item.type)) result.push(item);
  });
  return result;
}

function fhirValue(source, prefix = "value") {
  const key = Object.keys(source || {}).find((name) => name.startsWith(prefix));
  return key ? source[key] : undefined;
}

function valuesEqual(left, right) {
  if (left && right && typeof left === "object" && typeof right === "object") {
    if (left.code !== undefined || right.code !== undefined) {
      return String(left.code ?? "") === String(right.code ?? "")
        && (!left.system || !right.system || left.system === right.system);
    }
    if (left.value !== undefined || right.value !== undefined) return Number(left.value) === Number(right.value);
  }
  return String(left ?? "") === String(right ?? "");
}

function conditionMatches(condition) {
  const answers = state.structuredAnswers.get(condition.question)?.answer || [];
  if (Object.prototype.hasOwnProperty.call(condition, "answerBoolean") && condition.operator === "exists") {
    return (answers.length > 0) === condition.answerBoolean;
  }
  const expected = fhirValue(condition, "answer");
  if (expected === undefined) return false;
  const actual = answers.map((answer) => fhirValue(answer));
  if (!actual.length) return false;
  if (condition.operator === "!=") return actual.every((value) => !valuesEqual(value, expected));
  if (condition.operator === ">" || condition.operator === "<" || condition.operator === ">=" || condition.operator === "<=") {
    return actual.some((value) => {
      const left = Number(value?.value ?? value);
      const right = Number(expected?.value ?? expected);
      if (!Number.isFinite(left) || !Number.isFinite(right)) return false;
      if (condition.operator === ">") return left > right;
      if (condition.operator === "<") return left < right;
      if (condition.operator === ">=") return left >= right;
      return left <= right;
    });
  }
  return actual.some((value) => valuesEqual(value, expected));
}

function isItemEnabled(item) {
  if (!item.enableWhen?.length) return true;
  const matches = item.enableWhen.map(conditionMatches);
  return item.enableBehavior === "any" ? matches.some(Boolean) : matches.every(Boolean);
}

function activeAnswerBearingItems(questionnaire) {
  const result = [];
  const visit = (items, parentEnabled = true) => (items || []).forEach((item) => {
    const enabled = parentEnabled && !isQuestionnaireItemHidden(item) && isItemEnabled(item);
    if (enabled && !["group", "display"].includes(item.type)) result.push(item);
    visit(item.item, enabled);
  });
  visit(questionnaire?.item);
  return result;
}

function pruneDisabledAnswers() {
  let changed = false;
  const visit = (items, parentEnabled = true) => (items || []).forEach((item) => {
    const enabled = parentEnabled && isItemEnabled(item);
    if (!enabled && state.structuredAnswers.delete(item.linkId)) changed = true;
    visit(item.item, enabled);
  });
  do {
    changed = false;
    visit(state.questionnaire?.item);
  } while (changed);
}

function inferVersion(questionnaire) {
  if (state.sourceVersion !== "auto") return state.sourceVersion.toUpperCase();
  const profiles = questionnaire?.meta?.profile || [];
  const joined = profiles.join(" ").toLowerCase();
  if (joined.includes("5.0") || joined.includes("/r5")) return "R5";
  if (joined.includes("4.0") || joined.includes("/r4")) return "R4";
  return "미확정";
}

function blankResponse(questionnaire, status = "in-progress") {
  const response = { resourceType: "QuestionnaireResponse", status, item: [] };
  const ref = canonical(questionnaire);
  if (ref) response.questionnaire = ref;
  return response;
}

function setArtifacts(questionnaire, response, source, handoff = {}) {
  state.questionnaire = questionnaire ? clone(questionnaire) : null;
  state.questionnaireResponse = response ? clone(response) : null;
  state.questionnaireSource = typeof source === "string" ? source : pretty(source || {});
  state.handoff = clone(handoff || {});
  updateOutputs();
}

function refreshOutputData() {
  $("#sourceCode").textContent = state.questionnaireSource || "입력 소스가 여기에 표시됩니다.";
  $("#questionnaireCode").textContent = pretty(state.questionnaire || {});
  $("#responseCode").textContent = pretty(state.questionnaireResponse || {});
  $("#extractionCode").textContent = pretty(SDC_STATUS);
  $("#handoffCode").textContent = pretty(state.handoff || {});
  const hasQ = Boolean(state.questionnaire);
  const hasQr = Boolean(state.questionnaireResponse);
  $("#qState").textContent = hasQ ? `${answerBearingItems(state.questionnaire).length}개 문항` : "입력 대기";
  $("#qrState").textContent = hasQr ? state.questionnaireResponse.status : "입력 대기";
  const showHandoff = state.mode === "adaptive"
    && state.adaptivePurpose === "clinical_adaptive"
    && Boolean(Object.keys(state.handoff || {}).length);
  $("#handoffTab").hidden = !showHandoff;
  $("#outputStatus").textContent = state.questionnaireResponse?.status === "completed" ? "완료" : (hasQ ? "Draft" : "대기");
  $("#downloadR4").disabled = !hasQ;
  $("#downloadR5").disabled = !hasQ;
}

function updateOutputs() {
  refreshOutputData();
  renderPreview(state.questionnaire);
  renderResponseEntry(state.questionnaire);
  syncRunnerVisibility();
}

function syncRunnerVisibility() {
  const structured = state.mode === "structured";
  const fixed = state.mode === "fixed" && state.fixedQuestions.length > 0;
  const adaptive = state.mode === "adaptive";
  $("#structuredRunner").classList.toggle("active", structured);
  $("#fixedConversation").hidden = !fixed;
  $("#fixedConversation").classList.toggle("active", fixed);
  $("#adaptiveConversation").hidden = !adaptive;
  $("#adaptiveConversation").classList.toggle("active", adaptive);
  const placeholder = !structured && !fixed && !adaptive;
  $("#conversationPlaceholder").hidden = !placeholder;
  const labels = {
    structured: state.questionnaire ? `${activeAnswerBearingItems(state.questionnaire).length}개 활성 문항` : "준비 전",
    fixed: fixed ? `${Math.min(state.fixedIndex + 1, state.fixedQuestions.length)} / ${state.fixedQuestions.length}` : "시작 대기",
    adaptive: adaptive ? `${state.adaptiveHistory.length}개 답변` : "시작 대기"
  };
  $("#runnerStatus").textContent = labels[state.mode];
}

function append(parent, tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  parent.append(node);
  return node;
}

function browserLocale() {
  if (typeof navigator !== "undefined") {
    return navigator.languages?.[0] || navigator.language || "ko";
  }
  if (typeof document !== "undefined") return document.documentElement?.lang || "ko";
  return "ko";
}

function activeLocale() {
  const selected = state.displayLocale === "auto" ? browserLocale() : state.displayLocale;
  return String(selected || "ko").toLowerCase().replace("_", "-");
}

function localeMatches(candidate, requested) {
  const left = String(candidate || "").toLowerCase().replace("_", "-");
  const right = String(requested || "").toLowerCase().replace("_", "-");
  return left === right || left.split("-")[0] === right.split("-")[0];
}

function extensionValue(extension) {
  const key = Object.keys(extension || {}).find((name) => name.startsWith("value"));
  return key ? extension[key] : undefined;
}

function stripMarkup(value) {
  return String(value || "")
    .replace(/<br\s*\/?\s*>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/\s+/g, " ")
    .trim();
}

function translatedPrimitive(metadata, locale) {
  const translations = (metadata?.extension || []).filter((extension) => extension.url === FHIR_TRANSLATION_URL);
  for (const translation of translations) {
    const language = translation.extension?.find((extension) => extension.url === "lang")?.valueCode;
    const content = translation.extension?.find((extension) => extension.url === "content");
    if (localeMatches(language, locale) && content) return stripMarkup(extensionValue(content));
  }
  return "";
}

function renderingText(metadata) {
  const rendering = (metadata?.extension || []).find((extension) => extension.url === FHIR_RENDERING_XHTML_URL);
  return rendering ? stripMarkup(extensionValue(rendering)) : "";
}

function displayCoding(coding, locale) {
  const translation = translatedPrimitive(coding?._display, locale);
  if (translation) return translation;
  const designation = (coding?.designation || []).find((entry) => localeMatches(entry.language, locale));
  if (designation?.value) return designation.value;
  const rendered = renderingText(coding?._display);
  if (localeMatches(locale, "ko") && /[가-힣]/.test(rendered)) return rendered;
  return coding?.display || coding?.code || pretty(coding || {});
}

function displayAnswer(option, locale = activeLocale()) {
  const key = Object.keys(option || {}).find((name) => name.startsWith("value"));
  const value = key ? option[key] : "";
  if (key === "valueCoding" && value && typeof value === "object") return displayCoding(value, locale);
  if (typeof value === "string") {
    return translatedPrimitive(option[`_${key}`], locale) || value;
  }
  if (value && typeof value === "object") return value.display || value.code || pretty(value);
  return String(value ?? "");
}

function updateDisplayLocale() {
  state.displayLocale = $("#displayLocale").value;
  const locale = activeLocale();
  const label = localeMatches(locale, "ko") ? "한국어" : (localeMatches(locale, "en") ? "English" : locale);
  $("#localeDetail").textContent = `${state.displayLocale === "auto" ? `브라우저 locale ${locale}` : `선택 locale ${locale}`} · ${label} 표현을 우선하고 없으면 원문 display를 유지합니다.`;
  if (state.questionnaire) {
    renderResponseEntry(state.questionnaire);
    renderPreview(state.questionnaire);
  }
}

function syntheticGuidanceFor(text) {
  const value = String(text || "").toLowerCase();
  const identity = /(이름|성명|생년|생일|출생|성별|젠더|연락처|전화|휴대폰|이메일|주소|주민번호|식별자|name|birth|sex|gender|phone|email|address|identifier)/i;
  const clinical = /(진료기록|건강정보|처방전|진단서|퇴원|검사결과|영상|스캔|복용약|약물|병력|수술력|medical record|health record|prescription|diagnosis|discharge|scan|medication)/i;
  if (identity.test(value)) return "데모 안내 · 실제 개인정보 대신 가상값을 입력하세요. 예: 홍길동(가상), 1990-01-01(가상).";
  if (clinical.test(value)) return "데모 안내 · 실제 진료·건강정보나 문서 대신 실제 환자와 무관한 합성 정보를 입력하세요.";
  return "";
}

function answerScalar(answer) {
  const key = Object.keys(answer || {}).find((name) => name.startsWith("value"));
  const value = key ? answer[key] : "";
  if (value && typeof value === "object") return value.value ?? value.code ?? value.display ?? "";
  return value ?? "";
}

function quantityUnitOptions(item) {
  const extensions = item?.extension || [];
  const options = extensions
    .filter((extension) => extension.url === FHIR_QUESTIONNAIRE_UNIT_OPTION_URL && extension.valueCoding)
    .map((extension) => clone(extension.valueCoding));
  if (options.length) return options;
  const fixed = extensions.find((extension) => extension.url === FHIR_QUESTIONNAIRE_UNIT_URL && extension.valueCoding);
  return fixed ? [clone(fixed.valueCoding)] : [];
}

function typedStructuredAnswer(item, raw, unitCoding = null) {
  if (item.type === "integer") return { valueInteger: Number.parseInt(raw, 10) };
  if (item.type === "decimal") return { valueDecimal: Number(raw) };
  if (item.type === "boolean") return { valueBoolean: raw === "true" };
  if (item.type === "date") return { valueDate: raw };
  if (item.type === "dateTime") return { valueDateTime: raw };
  if (item.type === "time") return { valueTime: raw };
  if (item.type === "url") return { valueUri: raw };
  if (item.type === "quantity") {
    const valueQuantity = { value: Number(raw) };
    if (unitCoding) {
      if (unitCoding.display || unitCoding.code) valueQuantity.unit = unitCoding.display || unitCoding.code;
      if (unitCoding.system) valueQuantity.system = unitCoding.system;
      if (unitCoding.code) valueQuantity.code = unitCoding.code;
    }
    return { valueQuantity };
  }
  return { valueString: raw };
}

function itemControlsOthers(linkId) {
  let controls = false;
  walkItems(state.questionnaire?.item, (item) => {
    if (item.enableWhen?.some((condition) => condition.question === linkId)) controls = true;
  });
  return controls;
}

function recordStructuredAnswers(item, answers, rerender = false) {
  const usable = (answers || []).filter(Boolean);
  if (!usable.length) state.structuredAnswers.delete(item.linkId);
  else state.structuredAnswers.set(item.linkId, { linkId: item.linkId, text: item.text, answer: clone(usable) });
  pruneDisabledAnswers();
  if (!state.questionnaireResponse) return;
  state.questionnaireResponse.item = responseItemsFor(state.questionnaire.item, state.structuredAnswers);
  state.questionnaireResponse.status = "in-progress";
  state.handoff = {
    status: "structured_response_in_progress",
    answered_items: state.structuredAnswers.size,
    active_items: activeAnswerBearingItems(state.questionnaire).length,
    response_storage: "browser_memory_only"
  };
  refreshOutputData();
  if (rerender) {
    renderResponseEntry(state.questionnaire);
    renderPreview(state.questionnaire);
    syncRunnerVisibility();
  }
}

function optionsForItem(item) {
  if (item.answerOption?.length) return item.answerOption;
  if (item.answerValueSet && state.valueSetOptions.has(item.answerValueSet)) {
    return state.valueSetOptions.get(item.answerValueSet);
  }
  return [];
}

function appendValueSetState(block, item) {
  if (!item.answerValueSet || item.answerOption?.length) return;
  if (state.valueSetErrors.has(item.answerValueSet)) {
    append(block, "p", state.valueSetErrors.get(item.answerValueSet), "valueset-state error");
  } else if (!state.valueSetOptions.has(item.answerValueSet)) {
    append(block, "p", "용어서버에서 선택지를 확인하는 중입니다.", "valueset-state");
  } else {
    append(block, "p", `용어서버 ValueSet · ${state.valueSetOptions.get(item.answerValueSet).length}개 선택지`, "valueset-state");
  }
}

function conditionalContext(item) {
  const labels = (item.enableWhen || []).map((condition) => {
    const expected = fhirValue(condition, "answer");
    if (condition.operator === "exists") return condition.answerBoolean ? "선행 답변 있음" : "선행 답변 없음";
    if (expected && typeof expected === "object") return displayCoding(expected, activeLocale());
    return expected;
  }).filter((value) => value !== undefined && value !== "");
  return labels.length ? `표시 조건 · ${labels.join(item.enableBehavior === "any" ? " 또는 " : " · ")}` : "";
}

function structuredControl(block, item) {
  const existingAnswers = state.structuredAnswers.get(item.linkId)?.answer || [];
  const options = item.type === "boolean"
    ? [{ valueBoolean: true }, { valueBoolean: false }]
    : optionsForItem(item);
  if (options.length && item.repeats) {
    const choices = append(block, "div", undefined, "repeat-options");
    options.forEach((option, index) => {
      const label = append(choices, "label", undefined, "repeat-option");
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.value = String(index);
      checkbox.checked = existingAnswers.some((answer) => pretty(answer) === pretty(option));
      checkbox.addEventListener("change", () => {
        const selected = [...choices.querySelectorAll("input:checked")].map((input) => options[Number(input.value)]);
        recordStructuredAnswers(item, selected, true);
      });
      label.append(checkbox, document.createTextNode(displayAnswer(option)));
    });
    appendValueSetState(block, item);
    return;
  }
  if (options.length || item.type === "choice" || item.type === "open-choice") {
    const select = document.createElement("select");
    select.setAttribute("aria-label", item.text || item.linkId);
    const blank = document.createElement("option");
    blank.value = "";
    blank.textContent = options.length ? "선택하세요" : "선택지 확인 불가";
    select.append(blank);
    options.forEach((option, index) => {
      const node = document.createElement("option");
      node.value = String(index);
      node.textContent = item.type === "boolean" ? (option.valueBoolean ? "예" : "아니요") : displayAnswer(option);
      if (existingAnswers[0] && pretty(existingAnswers[0]) === pretty(option)) node.selected = true;
      select.append(node);
    });
    select.disabled = !options.length;
    select.addEventListener("change", () => recordStructuredAnswers(
      item,
      select.value === "" ? [] : [options[Number(select.value)]],
      true
    ));
    block.append(select);
    appendValueSetState(block, item);
    return;
  }
  if (item.type === "quantity") {
    const unitOptions = quantityUnitOptions(item);
    const quantity = existingAnswers[0]?.valueQuantity || {};
    const control = append(block, "div", undefined, "quantity-control");
    const input = document.createElement("input");
    input.type = "number";
    input.step = "any";
    input.placeholder = "양";
    input.setAttribute("aria-label", `${item.text || item.linkId} 양`);
    input.value = quantity.value === undefined ? "" : String(quantity.value);
    control.append(input);

    let unitSelect = null;
    if (unitOptions.length === 1) {
      const unit = append(control, "span", displayCoding(unitOptions[0], activeLocale()), "quantity-fixed-unit");
      unit.setAttribute("aria-label", "단위");
    } else if (unitOptions.length > 1) {
      unitSelect = document.createElement("select");
      unitSelect.setAttribute("aria-label", `${item.text || item.linkId} 단위`);
      const blank = document.createElement("option");
      blank.value = "";
      blank.textContent = "단위 선택";
      unitSelect.append(blank);
      unitOptions.forEach((option, index) => {
        const node = document.createElement("option");
        node.value = String(index);
        node.textContent = displayCoding(option, activeLocale());
        const sameSystem = !quantity.system || !option.system || quantity.system === option.system;
        const sameCode = quantity.code ? quantity.code === option.code : quantity.unit === (option.display || option.code);
        if (sameSystem && sameCode) node.selected = true;
        unitSelect.append(node);
      });
      control.append(unitSelect);
    }

    const hint = append(block, "small", unitOptions.length
      ? "양과 단위를 함께 QuestionnaireResponse.valueQuantity로 저장합니다."
      : "서식에 단위가 지정되지 않았습니다. 숫자만 저장됩니다.", "quantity-hint");
    const save = (rerender) => {
      const raw = input.value.trim();
      const unitIndex = unitSelect?.value === "" ? -1 : Number(unitSelect?.value || 0);
      const selectedUnit = unitOptions.length === 1 ? unitOptions[0] : unitOptions[unitIndex];
      const unitMissing = raw !== "" && unitOptions.length > 1 && !selectedUnit;
      hint.textContent = unitMissing
        ? "양을 저장하려면 바로 옆에서 단위를 선택하세요."
        : (unitOptions.length ? "양과 단위를 함께 QuestionnaireResponse.valueQuantity로 저장합니다." : "서식에 단위가 지정되지 않았습니다. 숫자만 저장됩니다.");
      hint.classList.toggle("error", unitMissing);
      recordStructuredAnswers(item, raw === "" || unitMissing ? [] : [typedStructuredAnswer(item, raw, selectedUnit)], rerender);
    };
    input.addEventListener("input", () => save(false));
    if (unitSelect) unitSelect.addEventListener("change", () => save(itemControlsOthers(item.linkId)));
    if (itemControlsOthers(item.linkId)) input.addEventListener("change", () => save(true));
    return;
  }
  if (["integer", "decimal"].includes(item.type) && numericControlConfig(item).slider) {
    const config = numericControlConfig(item);
    const minimum = config.minimum ?? 0;
    const maximum = config.maximum ?? 100;
    const current = existingAnswers[0] ? Number(answerScalar(existingAnswers[0])) : minimum;
    const control = append(block, "div", undefined, "slider-control");
    const input = document.createElement("input");
    input.type = "range";
    input.min = String(minimum);
    input.max = String(maximum);
    input.step = String(config.step);
    input.value = String(Number.isFinite(current) ? current : minimum);
    input.setAttribute("aria-label", item.text || item.linkId);
    const output = document.createElement("output");
    output.value = input.value;
    output.textContent = input.value;
    control.append(input, output);
    const bounds = append(block, "div", undefined, "slider-bounds");
    const lowerText = (item.item || []).find((child) => questionnaireItemControlCode(child) === "lower")?.text || "최소";
    const upperText = (item.item || []).find((child) => questionnaireItemControlCode(child) === "upper")?.text || "최대";
    append(bounds, "span", `${lowerText} ${minimum}`);
    append(bounds, "span", `${upperText} ${maximum}`);
    const save = (rerender) => {
      output.value = input.value;
      output.textContent = input.value;
      recordStructuredAnswers(item, [typedStructuredAnswer(item, input.value)], rerender);
    };
    input.addEventListener("input", () => save(false));
    input.addEventListener("change", () => save(itemControlsOthers(item.linkId)));
    return;
  }
  const input = document.createElement(item.type === "text" ? "textarea" : "input");
  const inputTypes = { integer: "number", decimal: "number", date: "date", dateTime: "datetime-local", time: "time", url: "url" };
  if (input.tagName === "INPUT") input.type = inputTypes[item.type] || "text";
  if (["integer", "decimal"].includes(item.type)) {
    const config = numericControlConfig(item);
    input.step = String(config.step);
    if (config.minimum !== undefined) input.min = String(config.minimum);
    if (config.maximum !== undefined) input.max = String(config.maximum);
  }
  input.placeholder = `${item.type || "string"} 응답`;
  input.value = String(answerScalar(existingAnswers[0]));
  const save = (rerender) => {
    const raw = input.value.trim();
    recordStructuredAnswers(item, raw === "" ? [] : [typedStructuredAnswer(item, raw)], rerender);
  };
  input.addEventListener("input", () => save(false));
  if (itemControlsOthers(item.linkId)) input.addEventListener("change", () => save(true));
  block.append(input);
}

function renderQuestionnaireItems(root, items, { interactive = false, depth = 0 } = {}) {
  (items || []).forEach((item) => {
    if (isQuestionnaireItemHidden(item)) return;
    if (!isItemEnabled(item)) return;
    if (isSliderBoundaryDisplay(item)) return;
    if (item.type === "group") {
      if (!hasRenderableQuestionnaireContent(item)) return;
      const group = append(root, "div", item.text || item.linkId, "preview-group");
      group.style.marginLeft = `${Math.min(depth, 3) * 8}px`;
      renderQuestionnaireItems(root, item.item, { interactive, depth: depth + 1 });
      return;
    }
    if (item.type === "display") {
      append(root, "p", item.text || "", "context-copy");
      renderQuestionnaireItems(root, item.item, { interactive, depth: depth + 1 });
      return;
    }
    const block = append(root, "div", undefined, "preview-question");
    append(block, "label", `${item.prefix ? `${item.prefix} ` : ""}${item.text || item.linkId}${item.required ? " *" : ""}`);
    const context = conditionalContext(item);
    if (context) append(block, "small", context, "conditional-context");
    if (interactive) {
      const guidance = syntheticGuidanceFor(item.text);
      if (guidance) append(block, "p", guidance, "privacy-prompt");
      structuredControl(block, item);
    } else {
      const existing = state.structuredAnswers.get(item.linkId)?.answer || [];
      const options = existing.length ? existing : optionsForItem(item).slice(0, 12);
      if (options.length) {
        const list = append(block, "div", undefined, "preview-options");
        options.forEach((option) => {
          const node = append(list, "div", displayAnswer(option), "preview-option");
          if (existing.some((answer) => pretty(answer) === pretty(option))) node.classList.add("selected");
        });
      } else {
        const input = document.createElement(item.type === "text" ? "textarea" : "input");
        input.disabled = true;
        input.placeholder = `${item.type || "string"} 응답`;
        block.append(input);
        appendValueSetState(block, item);
      }
    }
    renderQuestionnaireItems(root, item.item, { interactive, depth: depth + 1 });
  });
}

function appendQuestionnaireTitle(root, questionnaire) {
  const title = append(root, "div", undefined, "preview-title");
  append(title, "span", `${inferVersion(questionnaire)} · ${questionnaire.status || "draft"}`, "step-label");
  append(title, "h3", questionnaire.title || questionnaire.name || questionnaire.id || "Questionnaire");
  if (questionnaire.description) append(title, "p", questionnaire.description);
}

function renderResponseEntry(questionnaire) {
  const root = $("#responseForm");
  const scrollTop = root.scrollTop;
  root.replaceChildren();
  if (!questionnaire || state.mode !== "structured") {
    const empty = append(root, "div", undefined, "empty-state compact");
    append(empty, "span", "◎");
    append(empty, "strong", "설문을 실행해 주세요");
    append(empty, "small", "Questionnaire를 불러오면 조건에 맞는 문항만 표시됩니다.");
    return;
  }
  appendQuestionnaireTitle(root, questionnaire);
  renderQuestionnaireItems(root, questionnaire.item, { interactive: true });
  root.scrollTop = scrollTop;
}

function renderPreview(questionnaire) {
  const root = $("#formPreview");
  root.replaceChildren();
  if (!questionnaire) {
    const empty = append(root, "div", undefined, "empty-state");
    append(empty, "span", "◎");
    append(empty, "strong", "미리보기 준비 전");
    append(empty, "small", "입력 리소스를 검증하거나 대화를 시작하세요.");
    return;
  }
  appendQuestionnaireTitle(root, questionnaire);
  renderQuestionnaireItems(root, questionnaire.item);
}

function validateQuestionnaire(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("JSON 객체가 필요합니다.");
  if (value.resourceType !== "Questionnaire") throw new Error("resourceType은 Questionnaire여야 합니다.");
  if (!Array.isArray(value.item)) throw new Error("Questionnaire.item 배열이 필요합니다.");
  const ids = new Set();
  walkItems(value.item, (item) => {
    if (!item.linkId || typeof item.linkId !== "string") throw new Error("모든 item에 문자열 linkId가 필요합니다.");
    if (ids.has(item.linkId)) throw new Error(`중복 linkId: ${item.linkId}`);
    ids.add(item.linkId);
  });
  return value;
}

function setTerminologyState(kind, title, detail) {
  const strip = $(".terminology-strip");
  strip.classList.toggle("connected", kind === "connected");
  strip.classList.toggle("error", kind === "error");
  $("#terminologyState").textContent = title;
  $("#terminologyDetail").textContent = detail;
}

async function connectTerminology() {
  setTerminologyState("pending", "용어서버 연결 확인 중", "FHIR CapabilityStatement를 확인합니다.");
  try {
    const status = await api("/v1/terminology/status");
    state.terminologyAvailable = Boolean(status.available);
    if (status.available) {
      setTerminologyState(
        "connected",
        "용어서버 연결됨",
        `${status.software_name || "FHIR terminology server"} · FHIR ${status.fhir_version || "버전 미확인"}`
      );
    } else {
      setTerminologyState("error", "용어서버 미설정", "inline answerOption만 사용할 수 있습니다.");
    }
  } catch (error) {
    state.terminologyAvailable = false;
    setTerminologyState("error", "용어서버 연결 실패", "inline answerOption은 계속 사용할 수 있습니다.");
  }
}

async function loadQuestionnaireValueSets(questionnaire) {
  const canonicals = new Set();
  walkItems(questionnaire?.item, (item) => {
    if (item.answerValueSet && !item.answerOption?.length) canonicals.add(item.answerValueSet);
  });
  if (!canonicals.size) return;
  await Promise.all([...canonicals].map(async (url) => {
    state.valueSetErrors.delete(url);
    try {
      const expansion = await api("/v1/terminology/expand", {
        method: "POST",
        body: JSON.stringify({ url, count: 100 })
      });
      state.valueSetOptions.set(url, (expansion.contains || []).map((concept) => ({ valueCoding: concept })));
      if (!expansion.contains?.length) state.valueSetErrors.set(url, "용어서버가 빈 ValueSet 확장을 반환했습니다.");
    } catch (error) {
      const message = error.code === "valueset_not_found"
        ? "용어서버에서 이 ValueSet을 찾지 못했습니다. 선택지를 임의 생성하지 않습니다."
        : "ValueSet 선택지를 불러오지 못했습니다. 잠시 후 다시 확인하세요.";
      state.valueSetErrors.set(url, message);
    }
  }));
  renderResponseEntry(questionnaire);
  renderPreview(questionnaire);
}

function parseStructured() {
  const raw = $("#questionnaireJson").value.trim();
  if (!raw) return showToast("Questionnaire JSON을 입력하세요.");
  try {
    const questionnaire = validateQuestionnaire(JSON.parse(raw));
    const response = blankResponse(questionnaire);
    state.structuredAnswers = new Map();
    state.valueSetOptions = new Map();
    state.valueSetErrors = new Map();
    setArtifacts(questionnaire, response, raw, {
      status: "structured_response_ready",
      note: "정형 서식 입력을 구조 검증했습니다. 가운데 답변 입력 영역에는 enableWhen 조건을 만족한 문항만 표시합니다. 서버 저장·SDC Extraction은 수행하지 않았습니다."
    });
    $("#completeStructured").disabled = false;
    const count = answerBearingItems(questionnaire).length;
    const activeCount = activeAnswerBearingItems(questionnaire).length;
    $("#questionnaireMeta").textContent = `${inferVersion(questionnaire)} · 전체 ${count}개 / 현재 ${activeCount}개 문항 · ${canonical(questionnaire) || "canonical 없음"}`;
    syncRunnerVisibility();
    selectOutput("source");
    loadQuestionnaireValueSets(questionnaire);
    showToast("구조 검증을 마쳤습니다. 가운데에서 조건에 맞는 문항에 답변하세요.");
  } catch (error) {
    showToast(`검증 실패: ${error.message}`);
  }
}

function completeStructuredResponse() {
  if (!state.questionnaire || !state.questionnaireResponse) return showToast("먼저 Questionnaire를 실행하세요.");
  const missing = activeAnswerBearingItems(state.questionnaire).filter((item) => item.required && !state.structuredAnswers.has(item.linkId));
  if (missing.length) {
    return showToast(`필수 문항 ${missing.length}개에 답변이 필요합니다: ${missing.slice(0, 2).map((item) => item.text || item.linkId).join(", ")}`);
  }
  state.questionnaireResponse.status = "completed";
  state.handoff = {
    status: "structured_response_completed",
    answered_items: state.structuredAnswers.size,
    required_items_complete: true,
    response_storage: "browser_memory_only",
    sdc_extraction: "not_implemented"
  };
  updateOutputs();
  selectOutput("response");
  showToast("응답을 완료했습니다. 결과 확인에 QuestionnaireResponse를 표시합니다.");
}

function sampleQuestionnaire() {
  const sample = {
    resourceType: "Questionnaire", id: "demo-symptom-context", status: "draft",
    title: "진료 전 상황 확인 예시",
    item: [
      { linkId: "chief-concern", text: "진료받고 싶은 가장 큰 이유는 무엇인가요?", type: "string", required: true },
      { linkId: "onset", text: "언제 시작되었나요?", type: "string" },
      { linkId: "impact", text: "일상생활에 어떤 영향을 주나요?", type: "text" }
    ]
  };
  $("#questionnaireJson").value = pretty(sample);
  state.sourceVersion = "r4";
  $$("[data-version]").forEach((button) => button.classList.toggle("active", button.dataset.version === "r4"));
  parseStructured();
}

async function readTextFile(file) {
  if (!file) throw new Error("파일을 선택하세요.");
  if (file.size > MAX_FILE_BYTES) throw new Error("파일은 1 MB 이하여야 합니다.");
  return file.text();
}

function refreshFixedQuestions() {
  state.fixedQuestions = activeAnswerBearingItems(state.questionnaire).map((item) => clone(item));
  state.fixedIndex = state.fixedAnswers.length;
}

function fixedAnswerSummary(responseItem) {
  return (responseItem?.answer || []).map((answer) => displayAnswer(answer)).filter(Boolean).join(", ") || "응답 없음";
}

function renderFixedRevisionList() {
  const panel = $("#fixedRevision");
  const list = $("#fixedRevisionList");
  list.replaceChildren();
  panel.hidden = state.fixedAnswers.length === 0;
  state.fixedAnswers.forEach((responseItem, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = `${index + 1}. ${responseItem.text || responseItem.linkId} → ${fixedAnswerSummary(responseItem)}`;
    button.addEventListener("click", () => editFixedAnswer(index));
    list.append(button);
  });
}

function rebuildFixedConversationLog() {
  const log = $("#fixedChatLog");
  log.replaceChildren();
  bubble(log, "notice", `설문: ${state.fixedTitle}\n수정한 문항 이후의 응답은 조건 분기를 다시 계산하기 위해 다시 질문합니다.`);
  const flatItems = answerBearingItems(state.questionnaire);
  state.fixedAnswers.forEach((responseItem, index) => {
    const question = flatItems.find((item) => item.linkId === responseItem.linkId) || responseItem;
    bubble(log, "assistant", fixedPrompt(question, index, state.fixedQuestions.length));
    bubble(log, "user", fixedAnswerSummary(responseItem));
  });
}

function editFixedAnswer(index) {
  if (!Number.isInteger(index) || index < 0 || index >= state.fixedAnswers.length) return;
  state.fixedAnswers = state.fixedAnswers.slice(0, index);
  state.structuredAnswers = new Map(state.fixedAnswers.map((item) => [item.linkId, item]));
  state.questionnaireResponse.item = responseItemsFor(state.questionnaire.item, state.structuredAnswers);
  state.questionnaireResponse.status = "in-progress";
  refreshFixedQuestions();
  rebuildFixedConversationLog();
  renderFixedRevisionList();
  updateOutputs();
  askFixedQuestion();
  $("#fixedAnswer").focus();
}

function startFixed(questionnaire, title, source) {
  state.fixedTitle = title;
  state.fixedAnswers = [];
  state.fixedIndex = 0;
  state.structuredAnswers = new Map();
  $("#fixedConversationTitle").textContent = title;
  $("#fixedChatLog").replaceChildren();
  $("#fixedRevision").open = false;
  $("#fixedConversation").hidden = false;
  setArtifacts(questionnaire, blankResponse(questionnaire), source, {
    status: "fixed_conversation_in_progress",
    source_defined: questionnaire.id === "kr-patient-experience-evaluation-5th-2025"
      || questionnaire.id.startsWith("kr-national-health-screening"),
    response_storage: "browser_memory_only"
  });
  refreshFixedQuestions();
  renderFixedRevisionList();
  syncRunnerVisibility();
  bubble($("#fixedChatLog"), "notice", `설문: ${title}\n현재 답변에 적용되는 문항은 ${state.fixedQuestions.length}개이며, 조건부 문항은 관련 답변에 따라 펼쳐집니다.${questionnaire.description ? `\n${questionnaire.description}` : ""}`);
  askFixedQuestion();
}

function bubble(root, role, text) {
  const node = append(root, "div", text, `bubble ${role}`);
  root.scrollTop = root.scrollHeight;
  return node;
}

function fixedPrompt(question, index, count) {
  const options = (question.answerOption || []).map(displayAnswer).filter(Boolean);
  const units = question.type === "quantity" ? quantityUnitOptions(question) : [];
  const prefix = question.prefix ? `${question.prefix} ` : "";
  const unitGuide = units.length
    ? `\n입력 형식: 숫자 + 단위${units.length > 1 ? ` (${units.map((unit) => unit.display || unit.code).join(" / ")})` : ` (단위: ${units[0].display || units[0].code})`}`
    : "";
  return `[${index + 1}/${count}] ${prefix}${question.text || question.linkId}${options.length ? `\n${options.map((value, optionIndex) => `${optionIndex + 1}. ${value}`).join("\n")}` : ""}${unitGuide}`;
}

function askFixedQuestion() {
  const count = state.fixedQuestions.length;
  $("#fixedProgress").textContent = `${Math.min(state.fixedIndex + 1, count)} / ${count}`;
  if (state.fixedIndex >= count) {
    if (state.questionnaireResponse) state.questionnaireResponse.status = "completed";
    state.handoff = {
      status: "fixed_conversation_completed",
      answered_items: state.fixedAnswers.length,
      note: "브라우저 데모에서 생성된 draft 결과이며 서버 SDC Extraction은 수행되지 않았습니다."
    };
    updateOutputs();
    bubble($("#fixedChatLog"), "assistant", "모든 문항이 끝났습니다. 오른쪽에서 QuestionnaireResponse를 확인하세요.");
    $("#fixedAnswer").disabled = true;
    $("#fixedAnswerButton").disabled = true;
    renderFixedRevisionList();
    selectOutput("response");
    return;
  }
  $("#fixedAnswer").disabled = false;
  $("#fixedAnswerButton").disabled = false;
  renderFixedRevisionList();
  const question = state.fixedQuestions[state.fixedIndex];
  const guidance = syntheticGuidanceFor(question.text);
  if (guidance) bubble($("#fixedChatLog"), "notice", guidance);
  bubble($("#fixedChatLog"), "assistant", fixedPrompt(question, state.fixedIndex, count));
}

function answerValue(question, raw) {
  const normalized = raw.trim();
  const options = question.answerOption || [];
  const numeric = Number.parseInt(normalized, 10);
  const option = Number.isInteger(numeric) && numeric >= 1 && numeric <= options.length
    ? options[numeric - 1]
    : options.find((candidate) => [activeLocale(), "ko", "en"].some((locale) => displayAnswer(candidate, locale) === normalized));
  if (option) return clone(option);
  if (question.type === "quantity") {
    const units = quantityUnitOptions(question);
    const match = normalized.match(/^(-?\d+(?:\.\d+)?)\s*(.*)$/);
    if (match) {
      const requestedUnit = match[2].trim();
      const unit = units.find((candidate) => [candidate.display, candidate.code].includes(requestedUnit))
        || (units.length === 1 ? units[0] : null);
      const valueQuantity = { value: Number(match[1]) };
      if (unit) {
        if (unit.display) valueQuantity.unit = unit.display;
        if (unit.system) valueQuantity.system = unit.system;
        if (unit.code) valueQuantity.code = unit.code;
      }
      return { valueQuantity };
    }
  }
  if (question.type === "integer" && /^-?\d+$/.test(normalized)) return { valueInteger: Number(normalized) };
  if (question.type === "decimal" && /^-?\d+(\.\d+)?$/.test(normalized)) return { valueDecimal: Number(normalized) };
  if (question.type === "boolean" && /^(true|false)$/i.test(normalized)) return { valueBoolean: normalized.toLowerCase() === "true" };
  return { valueString: normalized };
}

function responseItemsFor(questionnaireItems, answersByLinkId) {
  const result = [];
  (questionnaireItems || []).forEach((item) => {
    if (item.type === "display") return;
    if (item.type === "group") {
      const children = responseItemsFor(item.item, answersByLinkId);
      if (children.length) result.push({ linkId: item.linkId, text: item.text, item: children });
      return;
    }
    const answer = answersByLinkId.get(item.linkId);
    if (answer) result.push(clone(answer));
  });
  return result;
}

function submitFixedAnswer() {
  const input = $("#fixedAnswer");
  const value = input.value.trim();
  if (!value || state.fixedIndex >= state.fixedQuestions.length) return;
  const question = state.fixedQuestions[state.fixedIndex];
  bubble($("#fixedChatLog"), "user", value);
  const answer = answerValue(question, value);
  const responseItem = { linkId: question.linkId, text: question.text, answer: [answer] };
  state.fixedAnswers.push(responseItem);
  state.structuredAnswers.set(question.linkId, responseItem);
  state.questionnaireResponse.item = responseItemsFor(state.questionnaire.item, state.structuredAnswers);
  refreshFixedQuestions();
  input.value = "";
  updateOutputs();
  askFixedQuestion();
}

async function loadPatientExperience() {
  try {
    const questionnaire = await api("/v1/demo/resources/patient-experience-5th-2025");
    validateQuestionnaire(questionnaire);
    state.sourceVersion = "r4";
    startFixed(questionnaire, questionnaire.title || "환자경험평가", pretty(questionnaire));
    selectOutput("questionnaire");
  } catch (error) { showToast(error.message); }
}

function screeningQuestionnaire(forms, age, sex) {
  return {
    resourceType: "Questionnaire",
    id: "kr-national-health-screening-selected-forms-2025",
    status: "draft",
    experimental: true,
    title: `국민건강검진 공식 문진 서식(시험용) · ${forms.map((form) => form.title).join(" · ")}`,
    description: `만 ${age}세 · 성별정보 ${sex}. 국가법령정보센터 건강검진 실시기준 별지 서식의 문항·보기·순서를 보존한 시험용 실행본입니다. 검진 예정일은 문항 선정에 사용하지 않습니다. 실제 수검 자격과 검사항목은 국민건강보험공단 확인이 필요합니다.`,
    derivedFrom: forms.map(canonical).filter(Boolean),
    item: forms.map((form, index) => ({
      linkId: `official-form-${index + 1}`,
      type: "group",
      text: form.title,
      item: clone(form.item || [])
    }))
  };
}

async function loadScreening() {
  const age = Number.parseInt($("#screeningAge").value, 10);
  if (!Number.isInteger(age) || age < 0 || age > 120) return showToast("유효한 만 나이를 입력하세요.");
  const sex = $("#screeningSex").value;
  try {
    const forms = [await api("/v1/demo/resources/national-health-screening-form-1-2025")];
    if ([66, 70, 80].includes(age)) forms.push(await api("/v1/demo/resources/national-health-screening-form-2-2025"));
    forms.forEach(validateQuestionnaire);
    const questionnaire = screeningQuestionnaire(forms, age, sex);
    state.sourceVersion = "r4";
    startFixed(questionnaire, questionnaire.title, pretty({
      input: { age, sex },
      selected_official_forms: forms.map((form) => ({ id: form.id, title: form.title, derived_from: canonical(form) })),
      source: "국가법령정보센터 건강검진 실시기준 별지 제1호·제2호 서식",
      periodicity_applied: false,
      periodicity_reason: "출생연도, 직역, 이전 수검일과 공식 NHIS 자격정보가 제공되지 않음",
      exact_form_content: true,
      source_defined_fixed_questionnaire: true
    }));
    showToast(`${forms.length}개 공식 서식, 총 ${state.fixedQuestions.length}개 응답 항목을 시작합니다.`);
  } catch (error) { showToast(error.message); }
}

function buildTextSurvey() {
  const raw = $("#fixedText").value.trim();
  if (!raw) return showToast("설문 문항 텍스트를 입력하세요.");
  try {
    if (raw.startsWith("{")) {
      const questionnaire = validateQuestionnaire(JSON.parse(raw));
      startFixed(questionnaire, questionnaire.title || "업로드 정형 설문", raw);
      return;
    }
  } catch (error) {
    return showToast(`JSON 설문 검증 실패: ${error.message}`);
  }
  const lines = raw.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  if (!lines.length) return showToast("한 줄 이상의 문항이 필요합니다.");
  const questionnaire = {
    resourceType: "Questionnaire", id: "uploaded-text-survey-draft", status: "draft", experimental: true,
    title: "업로드 텍스트 설문 (구조화 초안)",
    description: "한 줄을 한 개의 string 문항으로 해석한 브라우저 데모입니다. 원문 서식 검토가 필요합니다.",
    item: lines.map((text, index) => ({ linkId: `q-${index + 1}`, text, type: "string" }))
  };
  state.sourceVersion = "r4";
  startFixed(questionnaire, questionnaire.title, raw);
}

function adaptiveQuestion(document) {
  const stateDoc = document?.state || {};
  const selected = stateDoc.adapter_state?.selected_question || stateDoc.selected_question;
  const text = document?.presentation?.text || selected?.stem_text || selected?.text || stateDoc.prompt_ko;
  if (!text) return null;
  const rawOptions = selected?.answer_options?.length ? selected.answer_options : (selected?.preferred_answer_options || []);
  const options = rawOptions.map((option, index) => ({
    input: String(option.input || index + 1),
    label: option.display_ko || option.display || option.coding?.display || String(option.internal_value || option.coding?.code || index + 1).replaceAll("_", " "),
    internalValue: option.internal_value,
    coding: option.coding
  }));
  const answerOption = options.map((option) => option.coding
    ? { valueCoding: clone(option.coding) }
    : { valueString: String(option.internalValue || option.label) });
  return {
    linkId: selected?.fact_id || selected?.question_ref || `q-${state.adaptiveHistory.length + 1}`,
    questionRef: selected?.question_ref || `Q${state.adaptiveHistory.length + 1}`,
    text,
    originalText: selected?.text || text,
    type: options.length ? "choice" : "string",
    options,
    answerOption,
    responseInstruction: selected?.response_instruction_ko || (options.length
      ? "번호로 답하거나, 보기에 없으면 내용을 직접 입력해 주세요."
      : "내용을 자유롭게 입력해 주세요."),
    knowledgeTarget: selected?.target_id,
    knowledgeFact: selected?.fact_id,
    questionTemplate: selected?.template_id,
    sourceLabel: selected
      ? (document?.presentation?.status === "generated" ? "[공동 작업 지식] + [AI 표현]" : "[공동 작업 지식]")
      : "[AI 자체 생성—진단 아님]"
  };
}

function adaptivePrompt(question) {
  const lines = [`[${question.questionRef}] ${question.text}`];
  (question.options || []).forEach((option) => lines.push(`${option.input}. ${option.label}`));
  if (question.responseInstruction) lines.push(`응답 안내: ${question.responseInstruction}`);
  if (question.sourceLabel) lines.push(`출처: ${question.sourceLabel}`);
  return lines.join("\n");
}

function showAdaptiveQuestion(question) {
  const guidance = syntheticGuidanceFor(question.text);
  if (guidance) bubble($("#adaptiveChatLog"), "notice", guidance);
  bubble($("#adaptiveChatLog"), "assistant", adaptivePrompt(question));
  $("#adaptiveProgress").textContent = `${question.questionRef} · Knowledge Runtime`;
  $("#adaptiveAnswer").placeholder = question.options?.length ? "번호 또는 직접 답변" : "답변을 입력하세요";
}

function rebuildAdaptiveArtifacts(sourceDocument) {
  const asked = [...state.adaptiveHistory.map((entry) => entry.question)];
  if (state.currentAdaptiveQuestion) asked.push(state.currentAdaptiveQuestion);
  const questionnaire = {
    resourceType: "Questionnaire", id: "adaptive-question-history-draft", status: "draft", experimental: true,
    title: state.adaptivePurpose === "clinical_adaptive" ? "Knowledge 기반 진료 전 문진 이력" : "일반 건강상담 이력",
    description: "실제로 제시된 질문만 포함한 브라우저 생성 초안입니다.",
    item: asked.map((question, index) => ({
      linkId: safeLinkId(question.linkId, index),
      prefix: question.questionRef,
      text: question.text,
      type: question.type || "string",
      answerOption: question.answerOption?.length ? clone(question.answerOption) : undefined
    }))
  };
  const response = blankResponse(questionnaire);
  response.item = state.adaptiveHistory.map((entry, index) => ({ linkId: safeLinkId(entry.question.linkId, index), text: entry.question.text, answer: [{ valueString: entry.answer }] }));
  const source = { purpose: state.adaptivePurpose, conversation: state.adaptiveHistory, current_question: state.currentAdaptiveQuestion, backend_state: sourceDocument?.state || null };
  setArtifacts(questionnaire, response, pretty(source), state.handoff);
}

function safeLinkId(value, index) {
  const base = String(value || "q").replace(/[^A-Za-z0-9\-.]/g, "-").slice(0, 55) || "q";
  return `${base}-${index + 1}`;
}

function llmSelectionPayload() {
  const providerId = $("#llmProvider").value;
  const provider = state.providers.find((item) => item.provider_id === providerId);
  return {
    provider_id: providerId,
    selected_by: "participant",
    external_processing_consent: Boolean(provider?.external_processing && $("#externalConsent").checked)
  };
}

function adaptiveOpeningPrompt() {
  return state.adaptivePurpose === "clinical_adaptive"
    ? "오늘 진료받으려는 이유를 자유롭게 적어주세요. 증상뿐 아니라 재진, 검사 결과 상담, 복용약 검토, 퇴원 후 상태, 예방 상담도 가능합니다.\n\n질문 출처 표시: [공동 작업 지식]은 검증 중인 compiled Knowledge, [AI 표현]은 임상 의미를 바꾸지 않는 문장 표현만 뜻합니다. 문진 중에는 답변에 대한 의견을 제시하지 않고 완료 후 결과에서 정리합니다."
    : "궁금한 건강 문제나 응급 여부를 판단하는 데 필요한 상황을 자유롭게 적어주세요. 정보 제공 수준이며 진단·치료 결정을 대신하지 않습니다.";
}

function prepareAdaptiveConversation(force = false) {
  if (state.mode !== "adaptive" || state.sessionId || state.adaptiveStarted) return;
  const log = $("#adaptiveChatLog");
  if (force || !log.children.length) {
    log.replaceChildren();
    bubble(log, "assistant", adaptiveOpeningPrompt());
  }
  $("#adaptiveConversationTitle").textContent = state.adaptivePurpose === "clinical_adaptive" ? "진료 전 문진" : "일반 건강상담";
  $("#adaptiveProgress").textContent = "시작 전";
  $("#adaptiveAnswer").placeholder = state.adaptivePurpose === "clinical_adaptive"
    ? "예: 검사 결과 상담을 받고 싶어요"
    : "예: 이 증상이 응급인지 궁금해요";
  $("#adaptiveAnswer").disabled = false;
  $("#adaptiveAnswerButton").disabled = false;
  $("#completeAdaptive").disabled = true;
}

function setAdaptiveBusy(busy, message = "다음 질문을 준비하고 있습니다…") {
  state.adaptiveBusy = busy;
  $("#adaptiveProcessing").hidden = !busy;
  $("#adaptiveProcessingText").textContent = message;
  $("#adaptiveConversation").setAttribute("aria-busy", String(busy));
  const closedAfterStart = state.adaptiveStarted && !state.sessionId;
  $("#adaptiveAnswer").disabled = busy || closedAfterStart;
  $("#adaptiveAnswerButton").disabled = busy || closedAfterStart;
  $("#llmProvider").disabled = busy || state.apiMode !== "authenticated" || state.adaptiveStarted;
  $("#completeAdaptive").disabled = busy || !state.sessionId;
}

async function resetAdaptiveConversation(nextPurpose = state.adaptivePurpose) {
  const previousSessionId = state.sessionId;
  state.adaptiveRequestSerial += 1;
  state.sessionId = null;
  state.adaptivePurpose = nextPurpose;
  state.adaptiveStarted = false;
  state.adaptiveHistory = [];
  state.currentAdaptiveQuestion = null;
  state.handoff = {};
  setAdaptiveBusy(false);
  $("#adaptiveChatLog").replaceChildren();
  prepareAdaptiveConversation(true);
  if (previousSessionId) {
    try { await api(`/v1/sessions/${previousSessionId}`, { method: "DELETE" }); } catch (_) { /* TTL remains the fallback. */ }
  }
}

async function switchAdaptivePurpose(nextPurpose) {
  if (nextPurpose === state.adaptivePurpose && !state.adaptiveStarted && !state.sessionId) return;
  $$('[data-purpose]').forEach((candidate) => {
    const active = candidate.dataset.purpose === nextPurpose;
    candidate.classList.toggle("active", active);
    candidate.setAttribute("aria-checked", String(active));
  });
  $("#adaptivePurposeHelp").textContent = nextPurpose === "clinical_adaptive"
    ? "증상만 입력하는 곳이 아닙니다. 예약 진료의 이유, 재진, 검사결과 상담, 복용약 검토, 퇴원 후 상태 등 의료진에게 미리 전달할 내용을 자유롭게 시작할 수 있습니다."
    : "건강 질문과 현재 상황을 자유롭게 입력합니다. 위험 신호가 의심되면 안전 안내를 제공하지만 진단·치료 결정을 대신하지 않습니다.";
  showToast("이전 비정형 대화를 폐기하고 새 목적의 대화를 시작합니다.");
  await resetAdaptiveConversation(nextPurpose);
}

async function startAdaptive(opening) {
  if (!opening) return showToast("진료 또는 상담을 원하는 이유를 입력하세요.");
  const provider = state.providers.find((item) => item.provider_id === $("#llmProvider").value);
  if (provider?.external_processing && !$("#externalConsent").checked) return showToast("외부 LLM 처리 동의가 필요합니다.");
  const modeSelection = state.adaptivePurpose === "clinical_adaptive" ? "문진 시작" : "일반 건강상담";
  const requestSerial = ++state.adaptiveRequestSerial;
  setAdaptiveBusy(true, state.adaptivePurpose === "clinical_adaptive" ? "Reason for Encounter와 Knowledge를 연결하고 첫 질문을 준비하고 있습니다…" : "건강상담 연결을 준비하고 있습니다…");
  try {
    const payload = { mode_selection: modeSelection, initial_message: opening };
    if (state.apiMode === "authenticated") payload.llm_selection = llmSelectionPayload();
    const document = await api("/v1/sessions", { method: "POST", body: JSON.stringify(payload) });
    if (requestSerial !== state.adaptiveRequestSerial) {
      try { await api(`/v1/sessions/${document.session_id}`, { method: "DELETE" }); } catch (_) { /* TTL remains the fallback. */ }
      return;
    }
    state.sessionId = document.session_id;
    state.adaptiveStarted = true;
    state.adaptiveHistory = [];
    state.currentAdaptiveQuestion = adaptiveQuestion(document);
    $("#adaptiveConversation").hidden = false;
    $("#adaptiveConversationTitle").textContent = state.adaptivePurpose === "clinical_adaptive" ? "진료 전 문진" : "일반 건강상담";
    bubble($("#adaptiveChatLog"), "user", opening);
    if (state.adaptivePurpose === "health_information") {
      bubble($("#adaptiveChatLog"), "assistant", "일반 건강상담 mode는 목적 구분까지 연결되어 있으나, 전용 상담 adapter는 아직 구현되지 않았습니다. 진단·치료 결정을 대신하지 않으며 현재 대화를 계속 수집하지 않습니다.");
      state.handoff = { status: "adapter_pending", mode_id: "health_information", independent_diagnosis_or_treatment: false };
      await api(`/v1/sessions/${state.sessionId}`, { method: "DELETE" });
      state.sessionId = null;
      state.currentAdaptiveQuestion = null;
      $("#adaptiveAnswer").disabled = true;
      $("#adaptiveAnswerButton").disabled = true;
      $("#completeAdaptive").disabled = true;
    } else if (state.currentAdaptiveQuestion) {
      showAdaptiveQuestion(state.currentAdaptiveQuestion);
      $("#adaptiveAnswer").disabled = false;
      $("#adaptiveAnswerButton").disabled = false;
      $("#completeAdaptive").disabled = false;
    } else {
      bubble($("#adaptiveChatLog"), "assistant", "현재 입력에 맞는 전용 Knowledge 패키지를 찾지 못했습니다. 다른 증상으로 임의 대체하지 않습니다.");
    }
    rebuildAdaptiveArtifacts(document);
  } catch (error) { showToast(error.message); }
  finally { if (requestSerial === state.adaptiveRequestSerial) setAdaptiveBusy(false); }
}

async function sendAdaptiveAnswer() {
  const input = $("#adaptiveAnswer");
  const answer = input.value.trim();
  if (!state.adaptiveStarted && !state.sessionId) {
    if (!answer) return showToast("진료 또는 상담을 원하는 이유를 입력하세요.");
    input.value = "";
    await startAdaptive(answer);
    return;
  }
  if (!answer || !state.sessionId || !state.currentAdaptiveQuestion) return;
  const answered = clone(state.currentAdaptiveQuestion);
  bubble($("#adaptiveChatLog"), "user", answer);
  input.value = "";
  const requestSerial = ++state.adaptiveRequestSerial;
  setAdaptiveBusy(true, "답변을 반영하고 다음 Knowledge 질문을 선택하고 있습니다…");
  try {
    const document = await api(`/v1/sessions/${state.sessionId}/messages`, { method: "POST", body: JSON.stringify({ message: answer }) });
    if (requestSerial !== state.adaptiveRequestSerial) return;
    state.adaptiveHistory.push({ question: answered, answer });
    state.currentAdaptiveQuestion = adaptiveQuestion(document);
    if (state.currentAdaptiveQuestion) {
      showAdaptiveQuestion(state.currentAdaptiveQuestion);
    }
    else {
      bubble($("#adaptiveChatLog"), "assistant", "현재 Runtime 단계가 종료 또는 확인 대기 상태입니다. 결과를 확인하거나 대화를 종료하세요.");
      $("#adaptiveProgress").textContent = `${state.adaptiveHistory.length}개 답변`;
    }
    rebuildAdaptiveArtifacts(document);
  } catch (error) { showToast(error.message); }
  finally { if (requestSerial === state.adaptiveRequestSerial) setAdaptiveBusy(false); }
}

async function completeAdaptive() {
  if (!state.sessionId) return;
  const requestSerial = ++state.adaptiveRequestSerial;
  setAdaptiveBusy(true, "답변을 정리하고 최종 결과를 생성하고 있습니다…");
  try {
    const completed = await api(`/v1/sessions/${state.sessionId}/complete`, { method: "POST", body: "{}" });
    state.sessionId = null;
    state.handoff = completed.result?.clinical_handoff || completed.result || {};
    if (state.questionnaireResponse) state.questionnaireResponse.status = "completed";
    updateOutputs();
    bubble($("#adaptiveChatLog"), "assistant", "문진이 완료되었습니다. 질문 중에는 답변에 대한 의견이나 조언을 제시하지 않았습니다. 이제 오른쪽의 draft 의료인 요약을 확인하고, 진단·치료 판단은 담당 의료진과 상의해 주세요. 위험 신호 안내가 표시되면 해당 안전 안내를 우선하세요.");
    $("#adaptiveAnswer").disabled = true;
    $("#adaptiveAnswerButton").disabled = true;
    $("#completeAdaptive").disabled = true;
    selectOutput("handoff");
  } catch (error) { showToast(error.message); }
  finally { if (requestSerial === state.adaptiveRequestSerial) setAdaptiveBusy(false); }
}

function selectOutput(name) {
  const target = $(`#${name}Output`);
  if (!target) return;
  $$("[data-output]").forEach((button) => button.classList.toggle("active", button.dataset.output === name));
  $$(".output-view").forEach((view) => view.classList.remove("active"));
  target.classList.add("active");
}

function downloadJson(payload, filename) {
  const blob = new Blob([pretty(payload)], { type: "application/fhir+json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function downloadDraft(version) {
  if (!state.questionnaire) return;
  const stem = state.questionnaire.id || "questionnaire";
  const bundle = {
    resourceType: "Bundle",
    type: "collection",
    entry: [state.questionnaire, state.questionnaireResponse].filter(Boolean).map((resource) => ({ resource: clone(resource) }))
  };
  downloadJson(bundle, `${stem}-${version}-draft-bundle-unvalidated.json`);
  showToast(`${version.toUpperCase()} 공통요소 draft를 다운로드합니다. 공식 변환·validator 확인 전입니다.`);
}

async function connect() {
  state.apiKey = $("#apiKey").value;
  if (!state.apiKey) return showToast("API key를 입력하세요.");
  state.apiMode = "authenticated";
  try {
    const providers = await api("/v1/llm/providers");
    await api("/v1/demo/resources");
    await connectTerminology();
    state.providers = (providers.providers || []).filter((item) => item.selectable);
    const select = $("#llmProvider");
    select.replaceChildren();
    select.disabled = false;
    state.providers.forEach((provider) => {
      const option = document.createElement("option");
      option.value = provider.provider_id;
      option.textContent = `${provider.display_name} · ${provider.model}`;
      if (provider.default) option.selected = true;
      select.append(option);
    });
    setConnected(true, "Backend 연결됨");
    showToast("Backend와 연결했습니다. API key는 메모리에만 유지됩니다.");
    updateProviderConsent();
  } catch (error) {
    state.apiKey = "";
    state.apiMode = "anonymous_demo";
    setConnected(false, "연결 실패");
    showToast(error.message);
  }
}

async function connectAnonymous() {
  state.apiKey = "";
  state.apiMode = "anonymous_demo";
  try {
    const configuration = await api("/v1/llm/providers");
    await api("/v1/demo/resources");
    await connectTerminology();
    state.providers = (configuration.providers || []).filter((item) => item.selectable);
    const select = $("#llmProvider");
    select.replaceChildren();
    state.providers.forEach((provider) => {
      const option = document.createElement("option");
      option.value = provider.provider_id;
      option.textContent = `${provider.display_name} · ${provider.model}`;
      select.append(option);
    });
    select.disabled = true;
    setConnected(true, "익명 데모 연결됨");
    showToast("API key 없이 익명 데모를 시작합니다. 실제 개인정보 대신 가상값을 사용하세요.");
    updateProviderConsent();
  } catch (error) {
    setConnected(false, "익명 데모 준비 안됨");
    showToast(error.message);
  }
}

function updateProviderConsent() {
  const provider = state.providers.find((item) => item.provider_id === $("#llmProvider").value);
  $("#externalConsentRow").hidden = !provider?.external_processing;
  if (!provider?.external_processing) $("#externalConsent").checked = false;
  $("#providerPrivacy").textContent = provider?.external_processing
    ? "선택한 상용 LLM에는 질문 표현에 필요한 승인된 question stem만 전송합니다. 환자 답변·임상 Memory는 전송하지 않으며 아래 동의가 필요합니다."
    : "Local LLM은 분리된 내부 환경에서 처리되며 외부 상용 LLM으로 전송하지 않습니다.";
  $("#providerAuthHelp").hidden = Boolean(provider?.external_processing);
}

function shouldSubmitOnEnter(event) {
  return event?.key === "Enter" && !event.isComposing && event.keyCode !== 229 && !event.repeat;
}

function initialize() {
  $$(".mode-card").forEach((button) => button.addEventListener("click", () => setMode(button.dataset.mode)));
  $$("[data-version]").forEach((button) => button.addEventListener("click", () => {
    state.sourceVersion = button.dataset.version;
    $$("[data-version]").forEach((candidate) => candidate.classList.toggle("active", candidate === button));
  }));
  $("#displayLocale").addEventListener("change", updateDisplayLocale);
  $("#connectButton").addEventListener("click", connect);
  $("#apiKey").addEventListener("keydown", (event) => { if (event.key === "Enter") connect(); });
  $("#parseQuestionnaire").addEventListener("click", parseStructured);
  $("#completeStructured").addEventListener("click", completeStructuredResponse);
  $("#loadSample").addEventListener("click", sampleQuestionnaire);
  $("#questionnaireFile").addEventListener("change", async (event) => {
    try { $("#questionnaireJson").value = await readTextFile(event.target.files[0]); parseStructured(); } catch (error) { showToast(error.message); }
  });
  const drop = $("#questionnaireDrop");
  ["dragenter", "dragover"].forEach((name) => drop.addEventListener(name, (event) => { event.preventDefault(); drop.classList.add("dragging"); }));
  ["dragleave", "drop"].forEach((name) => drop.addEventListener(name, (event) => { event.preventDefault(); drop.classList.remove("dragging"); }));
  drop.addEventListener("drop", async (event) => { try { $("#questionnaireJson").value = await readTextFile(event.dataTransfer.files[0]); parseStructured(); } catch (error) { showToast(error.message); } });

  $$("[data-fixed-source]").forEach((button) => button.addEventListener("click", () => {
    $$("[data-fixed-source]").forEach((candidate) => candidate.classList.toggle("active", candidate === button));
    $$(".fixed-options").forEach((option) => option.classList.remove("active"));
    const mapping = { "patient-experience": "patientExperienceOptions", "national-screening": "screeningOptions", upload: "uploadOptions" };
    $(`#${mapping[button.dataset.fixedSource]}`).classList.add("active");
  }));
  $("#loadPatientExperience").addEventListener("click", loadPatientExperience);
  $("#loadScreening").addEventListener("click", loadScreening);
  $("#buildTextSurvey").addEventListener("click", buildTextSurvey);
  $("#fixedTextFile").addEventListener("change", async (event) => { try { $("#fixedText").value = await readTextFile(event.target.files[0]); } catch (error) { showToast(error.message); } });
  $$("[data-upload-kind]").forEach((button) => button.addEventListener("click", () => {
    $$("[data-upload-kind]").forEach((candidate) => candidate.classList.toggle("active", candidate === button));
    $("#textUploadPane").classList.toggle("active", button.dataset.uploadKind === "text");
    $("#imageUploadPane").classList.toggle("active", button.dataset.uploadKind === "image");
  }));
  $("#fixedImageFile").addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (!file || file.size > MAX_FILE_BYTES) return showToast("이미지는 1 MB 이하여야 합니다.");
    const image = document.createElement("img");
    image.alt = "업로드한 설문 이미지 미리보기";
    image.src = URL.createObjectURL(file);
    image.addEventListener("load", () => URL.revokeObjectURL(image.src), { once: true });
    $("#imagePreview").replaceChildren(image);
  });
  let fixedAnswerComposing = false;
  $("#fixedAnswer").addEventListener("compositionstart", () => { fixedAnswerComposing = true; });
  $("#fixedAnswer").addEventListener("compositionend", () => { fixedAnswerComposing = false; });
  $("#fixedAnswerButton").addEventListener("click", () => {
    $("#fixedAnswer").blur();
    window.setTimeout(() => { if (!fixedAnswerComposing) submitFixedAnswer(); }, 0);
  });
  $("#fixedAnswer").addEventListener("keydown", (event) => {
    if (!fixedAnswerComposing && shouldSubmitOnEnter(event)) {
      event.preventDefault();
      submitFixedAnswer();
    }
  });

  $$("[data-purpose]").forEach((button) => button.addEventListener("click", () => switchAdaptivePurpose(button.dataset.purpose)));
  $("#llmProvider").addEventListener("change", updateProviderConsent);
  $("#adaptiveAnswerButton").addEventListener("click", sendAdaptiveAnswer);
  $("#adaptiveAnswer").addEventListener("keydown", (event) => { if (event.key === "Enter") sendAdaptiveAnswer(); });
  $("#completeAdaptive").addEventListener("click", completeAdaptive);
  $$("[data-output]").forEach((button) => button.addEventListener("click", () => selectOutput(button.dataset.output)));
  $("#downloadR4").addEventListener("click", () => downloadDraft("r4"));
  $("#downloadR5").addEventListener("click", () => downloadDraft("r5"));
  updateOutputs();
  updateDisplayLocale();
  connectAnonymous();
}

initialize();
