const fs = require("fs");
const path = require("path");
const vm = require("vm");

const htmlPath = path.join(__dirname, "..", "index.html");
const html = fs.readFileSync(htmlPath, "utf8");
const match = html.match(/\/\/ CORE_START([\s\S]*?)\/\/ CORE_END/);
if (!match) throw new Error("Core block not found in index.html");

const sandbox = {
  window: {},
  crypto: { randomUUID: () => "test-submission-id" },
};
vm.createContext(sandbox);
vm.runInContext(match[1], sandbox);

const core = sandbox.window.AIKeieiCore;
const assert = require("assert");

function baseState(computed) {
  return {
    employee_size: "employee_30_99",
    answers: {},
    computed: { ...core.defaultComputed(), ...computed },
  };
}

const resultCases = [
  ["A no CEO no field no admin", { ceo_level: 0, field_level: 0, admin_level: 0 }, "A"],
  ["B CEO active field inactive", { ceo_level: 1, field_level: 0, admin_level: 0 }, "B"],
  ["C field active admin weak size 30+", { employee_size_level: 2, field_level: 1, admin_level: 1 }, "C"],
  ["D small field active admin present", { employee_size_level: 1, ceo_level: 2, field_level: 1, admin_level: 1 }, "D"],
  ["E advanced governed and spread", { ceo_level: 3, field_level: 3, admin_level: 2, admin_role_level: 3, knowledge_spread_level: 3 }, "E"],
  ["C beats D when admin weak", { employee_size_level: 2, ceo_level: 2, field_level: 1, admin_level: 1 }, "C"],
];

for (const [name, computed, expected] of resultCases) {
  assert.strictEqual(core.computeResult(baseState(computed)), expected, name);
}

assert.strictEqual(core.convertEmployeeSize("employee_1_9"), 0);
assert.strictEqual(core.convertEmployeeSize("employee_10_29"), 1);
assert.strictEqual(core.convertEmployeeSize("employee_30_99"), 2);
assert.strictEqual(core.convertEmployeeSize("employee_100_200"), 3);
assert.strictEqual(core.convertEmployeeSize("employee_201_plus"), 4);

assert.strictEqual(core.isECandidate(baseState({ admin_level: 0, api_level: 3 })), false, "admin gate required");
assert.strictEqual(core.isECandidate(baseState({ admin_level: 1, api_level: 1 })), true, "api>=1 candidate");
assert.strictEqual(core.computeResult(baseState({ api_level: 1, admin_level: 1, field_level: 0, ceo_level: 0 })), "A", "api>=1 is not advanced usage");
assert.strictEqual(core.computeResult(baseState({ api_level: 3, admin_level: 2, admin_role_level: 3, knowledge_spread_level: 3 })), "E", "api>=3 can support E");

const branchConfig = {
  choices: [
    { question_id: "q1", value: "ceo_none", ceo_level: 0 },
    { question_id: "q1", value: "ceo_agent", ceo_level: 3 },
    { question_id: "q2", value: "ceo_tool_agent", ceo_tool_level: 3 },
    { question_id: "q3b", value: "api_partial", api_level: 1 },
    { question_id: "q4", value: "field_none", field_level: 0 },
    { question_id: "q5", value: "admin_none", admin_level: 0 },
  ],
  questions: [
    { question_id: "q1", page_type: "diagnosis", question_text: "q1", display_condition_json: "{}", order: 1 },
    { question_id: "q2", page_type: "diagnosis", question_text: "q2", display_condition_json: { "answers.q1": ["ceo_light", "ceo_daily", "ceo_agent"] }, order: 2 },
    { question_id: "q3", page_type: "diagnosis", question_text: "q3", display_condition_json: { "answers.q2": "ceo_tool_chat" }, order: 3 },
    { question_id: "q3b", page_type: "diagnosis", question_text: "q3b", display_condition_json: { or: [{ "answers.q2": ["ceo_tool_agent", "ceo_tool_api", "ceo_tool_mix"] }, { "answers.q3": ["agent_work", "agent_api"] }] }, order: 4 },
    { question_id: "q4", page_type: "diagnosis", question_text: "q4", display_condition_json: "{}", order: 5 },
    { question_id: "q5", page_type: "diagnosis", question_text: "q5", display_condition_json: "{}", order: 6 },
    { question_id: "q6", page_type: "diagnosis", question_text: "q6", display_condition_json: { "computed.e_candidate": true }, order: 7 },
  ],
};

let state = {
  employee_size: "employee_30_99",
  answers: { q1: "ceo_agent", q2: "ceo_tool_agent", q3: null, q3b: "api_partial", q4: "field_none", q5: "admin_none", q6: null },
  computed: core.defaultComputed(),
};
assert.deepEqual(core.buildVisibleQuestions(state, branchConfig).map((q) => q.question_id), ["q1", "q2", "q3b", "q4", "q5"]);

state = {
  ...state,
  answers: { ...state.answers, q1: "ceo_none" },
};
const sanitized = core.sanitizeHiddenAnswers(state, branchConfig);
assert.strictEqual(sanitized.answers.q2, null, "q2 reset after q1 hides it");
assert.strictEqual(sanitized.answers.q3b, null, "q3b reset after q1 hides it");
assert.deepEqual(core.buildVisibleQuestions(sanitized, branchConfig).map((q) => q.question_id), ["q1", "q4", "q5"]);

const steps = core.buildResultSteps("C", {
  result_steps: [
    { result_code: "C", step_order: 20, type: "text", enabled: true, display_condition_json: "{}" },
    { result_code: "C", step_order: 10, type: "article", url: "", enabled: true, display_condition_json: "{}" },
    { result_code: "C", step_order: 15, type: "article", url: "https://example.com", enabled: true, display_condition_json: "{}" },
    { result_code: "C", step_order: 30, type: "youtube", enabled: true, display_condition_json: "{}" },
  ],
}, sanitized);
assert.deepEqual(steps.map((step) => step.step_order), [15, 20], "skip url-less article and unknown type");

console.log("logic tests passed");
