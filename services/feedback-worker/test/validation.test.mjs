import test from "node:test";
import assert from "node:assert/strict";
import worker, {normalizeSummary, validateSessionStart, validateSubmission} from "../src/index.js";

function valid() {
  return {
    client_event_id: "123e4567-e89b-12d3-a456-426614174000",
    consent: true,
    consent_version: "feedback-consent.v1",
    gpt_config_version: "1.41.0",
    package_version: "0.1.0",
    rfe_ids: ["rfe.cough"],
    flow_type: "dynamic_rfe",
    completion_status: "completed",
    safety_level: "routine",
    turn_count: 20,
    answered_fact_count: 16,
    data_absent_count: 1,
    clarification_count: 2,
    revision_count: 1,
    additional_comment_count: 0,
    terminology_status: "success",
    knowledge_load_status: "success",
    issue_tags: [],
    rating: 4,
  };
}

function validStart() {
  return {
    client_session_id: "123e4567-e89b-12d3-a456-426614174000",
    event_type: "session_started",
    gpt_config_version: "1.42.0",
  };
}

test("accepts a content-free session start", () => {
  assert.deepEqual(validateSessionStart(validStart()), validStart());
});

test("session start rejects clinical content and identifiers", () => {
  for (const [key, value] of [["reason_for_encounter", "cough"], ["answer", "yes"], ["ip_address", "127.0.0.1"]]) {
    const item = validStart();
    item[key] = value;
    assert.throws(() => validateSessionStart(item), /unsupported field/);
  }
});

test("accepts the structured minimum dataset", () => {
  assert.equal(validateSubmission(valid()).completion_status, "completed");
});

test("rejects raw or unexpected fields", () => {
  const item = valid();
  item.transcript = "not allowed";
  assert.throws(() => validateSubmission(item), /unsupported field/);
});

test("requires explicit consent", () => {
  const item = valid();
  item.consent = false;
  assert.throws(() => validateSubmission(item), /consent/);
});

test("rejects arbitrary free text and invalid identifiers", () => {
  const item = valid();
  item.issue_tags = ["a personal narrative"];
  assert.throws(() => validateSubmission(item), /issue_tags/);
  item.issue_tags = [];
  item.rfe_ids = ["patient.name"];
  assert.throws(() => validateSubmission(item), /rfe_ids/);
});

test("write endpoint requires its separate key", async () => {
  const response = await worker.fetch(
    new Request("https://feedback.test/v1/feedback", {
      method: "POST", body: JSON.stringify(valid()),
    }),
    {FEEDBACK_WRITE_KEY: "a".repeat(32)},
  );
  assert.equal(response.status, 401);
});

test("session-start endpoint persists only fixed content-free columns", async () => {
  const captured = [];
  const db = {
    prepare() {
      return {
        bind(...values) {
          captured.push(...values);
          return {async run() { return {success: true}; }};
        },
      };
    },
  };
  const response = await worker.fetch(
    new Request("https://feedback.test/v1/session-start", {
      method: "POST",
      headers: {"X-Feedback-Key": "w".repeat(32), "content-type": "application/json"},
      body: JSON.stringify(validStart()),
    }),
    {FEEDBACK_WRITE_KEY: "w".repeat(32), RETENTION_DAYS: "90", DB: db},
  );
  assert.equal(response.status, 201);
  assert.equal(captured.length, 5);
  assert.equal(captured[1], validStart().client_session_id);
  assert.equal(captured[3], "session_started");
  assert.equal(captured[4], "1.42.0");
});

test("write endpoint persists only the fixed normalized columns", async () => {
  const captured = [];
  const db = {
    prepare() {
      return {
        bind(...values) {
          captured.push(...values);
          return {async run() { return {success: true}; }};
        },
      };
    },
  };
  const response = await worker.fetch(
    new Request("https://feedback.test/v1/feedback", {
      method: "POST",
      headers: {"X-Feedback-Key": "w".repeat(32), "content-type": "application/json"},
      body: JSON.stringify(valid()),
    }),
    {FEEDBACK_WRITE_KEY: "w".repeat(32), RETENTION_DAYS: "90", DB: db},
  );
  assert.equal(response.status, 201);
  assert.equal(captured.length, 20);
  assert.equal(captured[3], "feedback-consent.v1");
  assert.equal(captured[6], '["rfe.cough"]');
  assert.equal(captured[18], "[]");
  assert.equal(captured.some((value) => typeof value === "object"), false);
});

test("empty aggregate summary uses zero counts instead of null", () => {
  assert.deepEqual(normalizeSummary({
    submissions: 0,
    average_turn_count: null,
    average_rating: null,
    completed: null,
  }), {
    started_sessions: 0,
    submissions: 0,
    average_turn_count: null,
    average_rating: null,
    completed: 0,
    completion_rate_percent: null,
    feedback_submission_rate_percent: null,
  });
});

test("summary reports start-to-feedback submission rate", () => {
  const summary = normalizeSummary({started_sessions: 8, submissions: 2, completed: 1});
  assert.equal(summary.feedback_submission_rate_percent, 25);
  assert.equal(summary.completion_rate_percent, 50);
});
