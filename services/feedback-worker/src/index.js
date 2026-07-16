const CONSENT_VERSION = "feedback-consent.v1";
const ALLOWED_KEYS = new Set([
  "client_event_id", "consent", "consent_version", "gpt_config_version",
  "package_version", "rfe_ids", "flow_type", "completion_status",
  "safety_level", "turn_count", "answered_fact_count", "data_absent_count",
  "clarification_count", "revision_count", "additional_comment_count",
  "terminology_status", "knowledge_load_status", "issue_tags", "rating",
]);
const ENUMS = {
  flow_type: new Set(["dynamic_rfe", "fixed_questionnaire", "hira_assessment", "preventive", "other"]),
  completion_status: new Set(["completed", "user_ended", "limit_reached", "technical_failure", "safety_handoff", "off_path_ended"]),
  safety_level: new Set(["routine", "urgent", "emergency", "unknown"]),
  terminology_status: new Set(["not_used", "success", "partial", "failed"]),
  knowledge_load_status: new Set(["success", "partial", "failed", "not_applicable"]),
};
const ISSUE_TAGS = new Set([
  "duplicate_numbering", "wrong_option_set", "question_mismatch",
  "missing_history", "missing_required_fact", "repeated_question",
  "misunderstood_question", "routing_error", "source_load_failure",
  "terminology_failure", "usage_limit", "too_long", "other_structured",
]);

function integer(value, name, maximum = 500) {
  if (!Number.isInteger(value) || value < 0 || value > maximum) {
    throw new Error(`${name} must be an integer from 0 to ${maximum}`);
  }
  return value;
}

export function validateSubmission(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) {
    throw new Error("body must be an object");
  }
  for (const key of Object.keys(input)) {
    if (!ALLOWED_KEYS.has(key)) throw new Error(`unsupported field: ${key}`);
  }
  if (input.consent !== true || input.consent_version !== CONSENT_VERSION) {
    throw new Error("explicit current-version consent is required");
  }
  if (!/^[0-9a-f]{8}-[0-9a-f-]{27,36}$/i.test(input.client_event_id || "")) {
    throw new Error("client_event_id must be a UUID");
  }
  if (!/^\d+\.\d+\.\d+$/.test(input.gpt_config_version || "")) {
    throw new Error("gpt_config_version must be semantic version text");
  }
  if (input.package_version != null && !/^\d+\.\d+\.\d+$/.test(input.package_version)) {
    throw new Error("package_version must be semantic version text");
  }
  if (!Array.isArray(input.rfe_ids) || input.rfe_ids.length > 3 ||
      input.rfe_ids.some((item) => typeof item !== "string" || !/^rfe\.[a-z0-9_]{1,80}$/.test(item))) {
    throw new Error("rfe_ids must contain at most three RFE identifiers");
  }
  for (const [name, allowed] of Object.entries(ENUMS)) {
    if (!allowed.has(input[name])) throw new Error(`invalid ${name}`);
  }
  const counts = {};
  for (const name of ["turn_count", "answered_fact_count", "data_absent_count", "clarification_count", "revision_count", "additional_comment_count"]) {
    counts[name] = integer(input[name], name);
  }
  if (!Array.isArray(input.issue_tags) || input.issue_tags.length > 8 ||
      new Set(input.issue_tags).size !== input.issue_tags.length ||
      input.issue_tags.some((item) => !ISSUE_TAGS.has(item))) {
    throw new Error("issue_tags contains an invalid or duplicate value");
  }
  if (input.rating != null && (!Number.isInteger(input.rating) || input.rating < 1 || input.rating > 5)) {
    throw new Error("rating must be an integer from 1 to 5");
  }
  return {
    client_event_id: input.client_event_id.toLowerCase(),
    consent_version: CONSENT_VERSION,
    gpt_config_version: input.gpt_config_version,
    package_version: input.package_version || null,
    rfe_ids: input.rfe_ids,
    flow_type: input.flow_type,
    completion_status: input.completion_status,
    safety_level: input.safety_level,
    ...counts,
    terminology_status: input.terminology_status,
    knowledge_load_status: input.knowledge_load_status,
    issue_tags: input.issue_tags,
    rating: input.rating ?? null,
  };
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {"content-type": "application/json; charset=utf-8", "cache-control": "no-store"},
  });
}

function authorized(request, expected, header) {
  const supplied = request.headers.get(header);
  return typeof expected === "string" && expected.length >= 24 && supplied === expected;
}

async function submit(request, env) {
  if (!authorized(request, env.FEEDBACK_WRITE_KEY, "X-Feedback-Key")) return json({error: "unauthorized"}, 401);
  const declaredLength = Number(request.headers.get("content-length") || "0");
  if (declaredLength > 8192) return json({error: "request_too_large"}, 413);
  let value;
  try {
    const raw = await request.text();
    if (new TextEncoder().encode(raw).byteLength > 8192) {
      return json({error: "request_too_large"}, 413);
    }
    value = validateSubmission(JSON.parse(raw));
  }
  catch (error) { return json({error: "invalid_submission", detail: error.message}, 400); }
  const id = crypto.randomUUID();
  const createdAt = new Date().toISOString();
  try {
    await env.DB.prepare(`INSERT INTO feedback_submissions (
      id, client_event_id, created_at, consent_version, gpt_config_version,
      package_version, rfe_ids_json, flow_type, completion_status, safety_level,
      turn_count, answered_fact_count, data_absent_count, clarification_count,
      revision_count, additional_comment_count, terminology_status,
      knowledge_load_status, issue_tags_json, rating
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`).bind(
      id, value.client_event_id, createdAt, value.consent_version,
      value.gpt_config_version, value.package_version, JSON.stringify(value.rfe_ids),
      value.flow_type, value.completion_status, value.safety_level,
      value.turn_count, value.answered_fact_count, value.data_absent_count,
      value.clarification_count, value.revision_count,
      value.additional_comment_count, value.terminology_status,
      value.knowledge_load_status, JSON.stringify(value.issue_tags), value.rating,
    ).run();
  } catch (error) {
    if (String(error).toLowerCase().includes("unique")) return json({accepted: true, duplicate: true});
    return json({error: "storage_failure"}, 500);
  }
  return json({accepted: true, receipt_id: id, retained_for_days: Number(env.RETENTION_DAYS || 90)}, 201);
}

async function grouped(db, column, since) {
  const result = await db.prepare(`SELECT ${column} AS value, COUNT(*) AS count FROM feedback_submissions WHERE created_at >= ? GROUP BY ${column} ORDER BY count DESC`).bind(since).all();
  return result.results || [];
}

async function stats(request, env) {
  if (!authorized(request, env.FEEDBACK_ADMIN_KEY, "X-Admin-Key")) return json({error: "unauthorized"}, 401);
  const requestedDays = Number.parseInt(new URL(request.url).searchParams.get("days") || "30", 10);
  const days = Number.isFinite(requestedDays) ? Math.min(365, Math.max(1, requestedDays)) : 30;
  const since = new Date(Date.now() - days * 86400000).toISOString();
  const summary = await env.DB.prepare(`SELECT COUNT(*) AS submissions, ROUND(AVG(turn_count), 1) AS average_turn_count, ROUND(AVG(rating), 2) AS average_rating, SUM(CASE WHEN completion_status = 'completed' THEN 1 ELSE 0 END) AS completed FROM feedback_submissions WHERE created_at >= ?`).bind(since).first();
  const rfe = await env.DB.prepare(`SELECT value AS rfe_id, COUNT(*) AS count FROM feedback_submissions, json_each(rfe_ids_json) WHERE created_at >= ? GROUP BY value ORDER BY count DESC`).bind(since).all();
  const issues = await env.DB.prepare(`SELECT value AS issue_tag, COUNT(*) AS count FROM feedback_submissions, json_each(issue_tags_json) WHERE created_at >= ? GROUP BY value ORDER BY count DESC`).bind(since).all();
  const normalizedSummary = summary || {submissions: 0, completed: 0, average_turn_count: null, average_rating: null};
  normalizedSummary.completion_rate_percent = normalizedSummary.submissions
    ? Math.round((normalizedSummary.completed / normalizedSummary.submissions) * 1000) / 10
    : null;
  return json({
    generated_at: new Date().toISOString(), days, since,
    summary: normalizedSummary,
    by_flow_type: await grouped(env.DB, "flow_type", since),
    by_completion_status: await grouped(env.DB, "completion_status", since),
    by_safety_level: await grouped(env.DB, "safety_level", since),
    by_gpt_config_version: await grouped(env.DB, "gpt_config_version", since),
    by_package_version: await grouped(env.DB, "package_version", since),
    by_terminology_status: await grouped(env.DB, "terminology_status", since),
    by_knowledge_load_status: await grouped(env.DB, "knowledge_load_status", since),
    by_rfe: rfe.results || [], by_issue_tag: issues.results || [],
    limitations: ["Only explicitly consented end-of-session submissions are counted.", "Abandoned sessions are not observable.", "No raw answer, transcript, direct identifier, age, sex, or contact field is collected."],
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") return json({status: "ok", privacy_mode: "structured_metrics_only"});
    if (request.method === "POST" && url.pathname === "/v1/feedback") return submit(request, env);
    if (request.method === "GET" && url.pathname === "/v1/admin/stats") return stats(request, env);
    return json({error: "not_found"}, 404);
  },
  async scheduled(_event, env) {
    const days = Math.min(365, Math.max(1, Number(env.RETENTION_DAYS || 90)));
    const cutoff = new Date(Date.now() - days * 86400000).toISOString();
    await env.DB.prepare("DELETE FROM feedback_submissions WHERE created_at < ?").bind(cutoff).run();
  },
};
