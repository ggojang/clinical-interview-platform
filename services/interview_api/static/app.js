"use strict";

const MAX_FILE_BYTES = 1024 * 1024;
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
  sourceVersion: "auto",
  questionnaire: null,
  questionnaireSource: "",
  questionnaireResponse: null,
  handoff: {},
  providers: [],
  sessionId: null,
  adaptivePurpose: "clinical_adaptive",
  adaptiveHistory: [],
  currentAdaptiveQuestion: null,
  fixedQuestions: [],
  fixedAnswers: [],
  fixedIndex: 0,
  fixedTitle: ""
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
    .replace(/^\/v1\/demo\/resources/, "/demo-api/resources")
    .replace(/^\/v1\/sessions/, "/demo-api/sessions");
  const target = state.apiMode === "authenticated" ? path : anonymousPath;
  const headers = { ...(options.headers || {}) };
  if (state.apiMode === "authenticated") headers.Authorization = `Bearer ${state.apiKey}`;
  if (options.body) headers["Content-Type"] = "application/json";
  const response = await fetch(target, { ...options, headers });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error?.message || `API 오류 (${response.status})`);
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
    adaptive: ["자유 대화", "Purpose first"]
  };
  $("#inputPanelTitle").textContent = labels[mode][0];
  $("#inputBadge").textContent = labels[mode][1];
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

function answerBearingItems(questionnaire) {
  const result = [];
  walkItems(questionnaire?.item, (item) => {
    if (!['group', 'display'].includes(item.type)) result.push(item);
  });
  return result;
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

function updateOutputs() {
  $("#sourceCode").textContent = state.questionnaireSource || "입력 소스가 여기에 표시됩니다.";
  $("#questionnaireCode").textContent = pretty(state.questionnaire || {});
  $("#responseCode").textContent = pretty(state.questionnaireResponse || {});
  $("#extractionCode").textContent = pretty(SDC_STATUS);
  $("#handoffCode").textContent = pretty(state.handoff || {});
  const hasQ = Boolean(state.questionnaire);
  const hasQr = Boolean(state.questionnaireResponse);
  $("#qState").textContent = hasQ ? `${answerBearingItems(state.questionnaire).length}개 문항` : "입력 대기";
  $("#qrState").textContent = hasQr ? state.questionnaireResponse.status : "입력 대기";
  $("#sdcState").textContent = "미구현";
  $("#outputStatus").textContent = hasQ ? "Draft" : "대기";
  $("#downloadR4").disabled = !hasQ;
  $("#downloadR5").disabled = !hasQ;
  renderPreview(state.questionnaire);
}

function append(parent, tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  parent.append(node);
  return node;
}

function displayAnswer(option) {
  const key = Object.keys(option || {}).find((name) => name.startsWith("value"));
  const value = key ? option[key] : "";
  if (value && typeof value === "object") return value.display || value.code || pretty(value);
  return String(value ?? "");
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
  const title = append(root, "div", undefined, "preview-title");
  append(title, "span", `${inferVersion(questionnaire)} · ${questionnaire.status || "draft"}`, "step-label");
  append(title, "h3", questionnaire.title || questionnaire.name || questionnaire.id || "Questionnaire");
  if (questionnaire.description) append(title, "p", questionnaire.description);

  const renderItems = (items, depth = 0) => (items || []).forEach((item) => {
    if (item.type === "group") {
      const group = append(root, "div", item.text || item.linkId, "preview-group");
      group.style.marginLeft = `${Math.min(depth, 3) * 8}px`;
      renderItems(item.item, depth + 1);
      return;
    }
    if (item.type === "display") {
      append(root, "p", item.text || "", "context-copy");
      renderItems(item.item, depth + 1);
      return;
    }
    const block = append(root, "div", undefined, "preview-question");
    append(block, "label", `${item.prefix ? `${item.prefix} ` : ""}${item.text || item.linkId}${item.required ? " *" : ""}`);
    if (item.answerOption?.length) {
      const options = append(block, "div", undefined, "preview-options");
      item.answerOption.slice(0, 12).forEach((option) => append(options, "div", displayAnswer(option), "preview-option"));
    } else {
      const input = document.createElement(item.type === "text" ? "textarea" : "input");
      input.disabled = true;
      input.placeholder = `${item.type || "string"} 응답`;
      block.append(input);
    }
    renderItems(item.item, depth + 1);
  });
  renderItems(questionnaire.item);
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

function parseStructured() {
  const raw = $("#questionnaireJson").value.trim();
  if (!raw) return showToast("Questionnaire JSON을 입력하세요.");
  try {
    const questionnaire = validateQuestionnaire(JSON.parse(raw));
    const response = blankResponse(questionnaire);
    setArtifacts(questionnaire, response, raw, {
      status: "preview_only",
      note: "정형 서식 입력을 브라우저에서 구조 검증했습니다. 서버 저장·SDC Extraction은 수행하지 않았습니다."
    });
    const count = answerBearingItems(questionnaire).length;
    $("#questionnaireMeta").textContent = `${inferVersion(questionnaire)} · ${count}개 응답 문항 · ${canonical(questionnaire) || "canonical 없음"}`;
    selectOutput("preview");
    showToast("구조 검증과 미리보기를 완료했습니다.");
  } catch (error) {
    showToast(`검증 실패: ${error.message}`);
  }
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

function flattenQuestions(questionnaire) {
  return answerBearingItems(questionnaire).map((item) => clone(item));
}

function startFixed(questionnaire, title, source) {
  state.fixedTitle = title;
  state.fixedQuestions = flattenQuestions(questionnaire);
  state.fixedAnswers = [];
  state.fixedIndex = 0;
  $("#fixedConversationTitle").textContent = title;
  $("#fixedChatLog").replaceChildren();
  $("#fixedConversation").hidden = false;
  setArtifacts(questionnaire, blankResponse(questionnaire), source, {
    status: "fixed_conversation_in_progress",
    source_defined: questionnaire.id === "kr-patient-experience-evaluation-5th-2025",
    response_storage: "browser_memory_only"
  });
  askFixedQuestion();
}

function bubble(root, role, text) {
  const node = append(root, "div", text, `bubble ${role}`);
  root.scrollTop = root.scrollHeight;
  return node;
}

function fixedPrompt(question) {
  const options = (question.answerOption || []).map(displayAnswer).filter(Boolean);
  return `${question.text || question.linkId}${options.length ? `\n${options.map((value, index) => `${index + 1}. ${value}`).join("\n")}` : ""}`;
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
    return;
  }
  $("#fixedAnswer").disabled = false;
  $("#fixedAnswerButton").disabled = false;
  bubble($("#fixedChatLog"), "assistant", fixedPrompt(state.fixedQuestions[state.fixedIndex]));
}

function answerValue(question, raw) {
  const normalized = raw.trim();
  const options = question.answerOption || [];
  const numeric = Number.parseInt(normalized, 10);
  const option = Number.isInteger(numeric) && numeric >= 1 && numeric <= options.length
    ? options[numeric - 1]
    : options.find((candidate) => displayAnswer(candidate) === normalized);
  if (option) return clone(option);
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
  state.fixedAnswers.push({ linkId: question.linkId, text: question.text, answer: [answer] });
  const answers = new Map(state.fixedAnswers.map((item) => [item.linkId, item]));
  state.questionnaireResponse.item = responseItemsFor(state.questionnaire.item, answers);
  state.fixedIndex += 1;
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
    selectOutput("preview");
  } catch (error) { showToast(error.message); }
}

function eligibleScreeningGroups(resource, age, sex) {
  const byId = new Map((resource.question_groups || []).map((group) => [group.id, group]));
  const ids = [];
  if (age >= 20) ids.push("kr.nhis.general.common", "kr.nhis.oral.general");
  if (age === 66) ids.push("kr.nhis.general.age66.additional");
  if (age >= 40) ids.push("kr.nhis.cancer.gastric");
  if (age >= 50) ids.push("kr.nhis.cancer.colorectal");
  if (sex === "female" && age >= 40) ids.push("kr.nhis.cancer.breast");
  if (sex === "female" && age >= 20) ids.push("kr.nhis.cancer.cervical");
  if (ids.some((id) => id.startsWith("kr.nhis.cancer."))) ids.splice(ids.indexOf("kr.nhis.general.common") + 1, 0, "kr.nhis.cancer.common");
  return [...new Set(ids)].map((id) => byId.get(id)).filter(Boolean);
}

function screeningQuestionnaire(resource, groups, age, sex, period) {
  return {
    resourceType: "Questionnaire",
    id: "draft-national-health-screening-candidate",
    status: "draft",
    experimental: true,
    title: `국가건강검진 후보 문진 (${period || "시기 미확정"})`,
    description: `만 ${age}세 · 성별정보 ${sex}. 공식 수검자격이 아니라 입력정보에 따른 질문 후보입니다. 간암·폐암은 위험정보가 없어 제외했습니다.`,
    item: groups.map((group) => ({
      linkId: group.id.replaceAll(".", "-"), type: "group", text: group.title?.ko || group.id,
      item: (group.questions || []).map((question) => ({
        linkId: question.id.replaceAll(".", "-"),
        text: question.text?.ko || question.id,
        type: question.answer_type === "choice" ? "choice" : "string",
        answerOption: question.answer_type === "choice"
          ? Object.entries(question.shortcuts || {}).filter(([, value]) => !String(value).startsWith("asked-")).map(([code, display]) => ({ valueCoding: { system: "https://ggojang.github.io/clinical-interview-platform/fhir/CodeSystem/demo-screening-answer", code, display } }))
          : undefined
      }))
    }))
  };
}

async function loadScreening() {
  const age = Number.parseInt($("#screeningAge").value, 10);
  if (!Number.isInteger(age) || age < 0 || age > 120) return showToast("유효한 만 나이를 입력하세요.");
  const sex = $("#screeningSex").value;
  try {
    const resource = await api("/v1/demo/resources/national-health-screening-2026");
    const groups = eligibleScreeningGroups(resource, age, sex);
    if (!groups.length) return showToast("현재 입력값으로 선택된 질문군이 없습니다. 공식 대상 여부를 별도로 확인하세요.");
    const questionnaire = screeningQuestionnaire(resource, groups, age, sex, $("#screeningDate").value);
    state.sourceVersion = "r4";
    startFixed(questionnaire, questionnaire.title, pretty({
      input: { age, sex, period: $("#screeningDate").value },
      selected_group_ids: groups.map((g) => g.id),
      source: resource.id,
      periodicity_applied: false,
      periodicity_reason: "출생연도, 직역, 이전 수검일과 공식 NHIS 자격정보가 제공되지 않음",
      omitted_due_to_missing_risk_information: ["kr.nhis.cancer.liver", "kr.nhis.cancer.lung"]
    }));
    showToast(`${groups.length}개 후보 질문군을 만들었습니다. 공식 대상 여부는 NHIS 확인이 필요합니다.`);
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
  const text = document?.presentation?.text || selected?.text || stateDoc.prompt_ko;
  if (!text) return null;
  return { linkId: selected?.fact_id || selected?.question_ref || `q-${state.adaptiveHistory.length + 1}`, text, type: "string" };
}

function rebuildAdaptiveArtifacts(sourceDocument) {
  const asked = [...state.adaptiveHistory.map((entry) => entry.question)];
  if (state.currentAdaptiveQuestion) asked.push(state.currentAdaptiveQuestion);
  const questionnaire = {
    resourceType: "Questionnaire", id: "adaptive-question-history-draft", status: "draft", experimental: true,
    title: state.adaptivePurpose === "clinical_adaptive" ? "Knowledge 기반 진료 전 문진 이력" : "일반 건강상담 이력",
    description: "실제로 제시된 질문만 포함한 브라우저 생성 초안입니다.",
    item: asked.map((question, index) => ({ linkId: safeLinkId(question.linkId, index), text: question.text, type: "string" }))
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

async function startAdaptive() {
  const opening = $("#adaptiveOpening").value.trim();
  if (!opening) return showToast("시작 내용을 입력하세요.");
  const provider = state.providers.find((item) => item.provider_id === $("#llmProvider").value);
  if (provider?.external_processing && !$("#externalConsent").checked) return showToast("외부 LLM 처리 동의가 필요합니다.");
  const modeSelection = state.adaptivePurpose === "clinical_adaptive" ? "문진 시작" : "일반 건강상담";
  try {
    const payload = { mode_selection: modeSelection, initial_message: opening };
    if (state.apiMode === "authenticated") payload.llm_selection = llmSelectionPayload();
    const document = await api("/v1/sessions", { method: "POST", body: JSON.stringify(payload) });
    state.sessionId = document.session_id;
    state.adaptiveHistory = [];
    state.currentAdaptiveQuestion = adaptiveQuestion(document);
    $("#adaptiveChatLog").replaceChildren();
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
      bubble($("#adaptiveChatLog"), "assistant", state.currentAdaptiveQuestion.text);
      $("#adaptiveAnswer").disabled = false;
      $("#adaptiveAnswerButton").disabled = false;
      $("#completeAdaptive").disabled = false;
    } else {
      bubble($("#adaptiveChatLog"), "assistant", "현재 입력에 맞는 전용 Knowledge 패키지를 찾지 못했습니다. 다른 증상으로 임의 대체하지 않습니다.");
    }
    rebuildAdaptiveArtifacts(document);
  } catch (error) { showToast(error.message); }
}

async function sendAdaptiveAnswer() {
  const input = $("#adaptiveAnswer");
  const answer = input.value.trim();
  if (!answer || !state.sessionId || !state.currentAdaptiveQuestion) return;
  const answered = clone(state.currentAdaptiveQuestion);
  bubble($("#adaptiveChatLog"), "user", answer);
  input.value = "";
  try {
    const document = await api(`/v1/sessions/${state.sessionId}/messages`, { method: "POST", body: JSON.stringify({ message: answer }) });
    state.adaptiveHistory.push({ question: answered, answer });
    state.currentAdaptiveQuestion = adaptiveQuestion(document);
    if (state.currentAdaptiveQuestion) bubble($("#adaptiveChatLog"), "assistant", state.currentAdaptiveQuestion.text);
    else bubble($("#adaptiveChatLog"), "assistant", "현재 Runtime 단계가 종료 또는 확인 대기 상태입니다. 결과를 확인하거나 대화를 종료하세요.");
    $("#adaptiveProgress").textContent = `${state.adaptiveHistory.length}개 답변`;
    rebuildAdaptiveArtifacts(document);
  } catch (error) { showToast(error.message); }
}

async function completeAdaptive() {
  if (!state.sessionId) return;
  try {
    const completed = await api(`/v1/sessions/${state.sessionId}/complete`, { method: "POST", body: "{}" });
    state.sessionId = null;
    state.handoff = completed.result?.clinical_handoff || completed.result || {};
    if (state.questionnaireResponse) state.questionnaireResponse.status = "completed";
    updateOutputs();
    bubble($("#adaptiveChatLog"), "assistant", "세션을 완료하고 서버의 응답 상태를 폐기했습니다. 오른쪽에서 draft handoff를 확인하세요.");
    $("#adaptiveAnswer").disabled = true;
    $("#adaptiveAnswerButton").disabled = true;
    $("#completeAdaptive").disabled = true;
    selectOutput("handoff");
  } catch (error) { showToast(error.message); }
}

function selectOutput(name) {
  $$("[data-output]").forEach((button) => button.classList.toggle("active", button.dataset.output === name));
  $$(".output-view").forEach((view) => view.classList.remove("active"));
  $(`#${name}Output`).classList.add("active");
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
}

function initialize() {
  $$(".mode-card").forEach((button) => button.addEventListener("click", () => setMode(button.dataset.mode)));
  $$("[data-version]").forEach((button) => button.addEventListener("click", () => {
    state.sourceVersion = button.dataset.version;
    $$("[data-version]").forEach((candidate) => candidate.classList.toggle("active", candidate === button));
  }));
  $("#connectButton").addEventListener("click", connect);
  $("#anonymousConnectButton").addEventListener("click", connectAnonymous);
  $("#apiKey").addEventListener("keydown", (event) => { if (event.key === "Enter") connect(); });
  $("#parseQuestionnaire").addEventListener("click", parseStructured);
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
  $("#fixedAnswerButton").addEventListener("click", submitFixedAnswer);
  $("#fixedAnswer").addEventListener("keydown", (event) => { if (event.key === "Enter") submitFixedAnswer(); });

  $$("[data-purpose]").forEach((button) => button.addEventListener("click", () => {
    state.adaptivePurpose = button.dataset.purpose;
    $$("[data-purpose]").forEach((candidate) => {
      const active = candidate === button;
      candidate.classList.toggle("active", active);
      candidate.setAttribute("aria-checked", String(active));
    });
  }));
  $("#llmProvider").addEventListener("change", updateProviderConsent);
  $("#startAdaptive").addEventListener("click", startAdaptive);
  $("#adaptiveAnswerButton").addEventListener("click", sendAdaptiveAnswer);
  $("#adaptiveAnswer").addEventListener("keydown", (event) => { if (event.key === "Enter") sendAdaptiveAnswer(); });
  $("#completeAdaptive").addEventListener("click", completeAdaptive);
  $$("[data-output]").forEach((button) => button.addEventListener("click", () => selectOutput(button.dataset.output)));
  $("#downloadR4").addEventListener("click", () => downloadDraft("r4"));
  $("#downloadR5").addEventListener("click", () => downloadDraft("r5"));
  updateOutputs();
  connectAnonymous();
}

initialize();
