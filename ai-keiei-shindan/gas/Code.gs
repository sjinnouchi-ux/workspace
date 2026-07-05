const SPREADSHEET_ID = '1wYT01OGL1-lKzzytLDJi8QIVimq61aVFrS88RIiCR0I';
const CACHE_SECONDS = 600;

const SHEETS = {
  appConfig: 'app_config',
  questions: 'questions',
  choices: 'choices',
  results: 'results',
  resultSteps: 'result_steps',
  submissions: 'submissions',
};

const SHEET_HEADERS = {
  app_config: ['key', 'value', 'notes'],
  questions: ['question_id', 'page_type', 'question_text', 'description', 'is_required', 'display_condition_json', 'order'],
  choices: ['question_id', 'value', 'label', 'ceo_level', 'ceo_tool_level', 'agent_level', 'api_level', 'field_level', 'admin_level', 'admin_role_level', 'knowledge_spread_level', 'order'],
  results: ['result_code', 'phase_name', 'headline'],
  result_steps: ['result_code', 'step_order', 'type', 'headline', 'body_md', 'url', 'link_label', 'next_label', 'display_condition_json', 'enabled'],
  submissions: [
    'timestamp', 'submission_id', 'diagnosis_version', 'company_name', 'industry', 'employee_size',
    'q1_value', 'q2_value', 'q3_value', 'q3b_value', 'q4_value', 'q5_value', 'q6_value', 'q7_value',
    'ceo_level', 'ceo_tool_level', 'agent_level', 'api_level', 'field_level', 'admin_level',
    'admin_role_level', 'knowledge_spread_level', 'advanced_ai_usage',
    'result_code', 'result_headline', 'result_phase', 'raw_payload_json',
    'device_type', 'user_agent',
  ],
};

function doGet(e) {
  const action = (e && e.parameter && e.parameter.action) || 'config';
  if (action !== 'config') return jsonOutput({ ok: false, error: 'unknown_action' });
  return jsonOutput(getConfig());
}

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData && e.postData.contents ? e.postData.contents : '{}');
    if (payload.action && payload.action !== 'submit') {
      return jsonOutput({ ok: false, error: 'unknown_action' });
    }
    const result = saveSubmission(payload);
    return jsonOutput(result);
  } catch (error) {
    return jsonOutput({ ok: false, error: String(error && error.message ? error.message : error) });
  }
}

function getConfig() {
  const cache = CacheService.getScriptCache();
  const cached = cache.get('config');
  if (cached) return JSON.parse(cached);

  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const appConfigWithVersion = rowsToKeyValue_(readRows_(ss, SHEETS.appConfig));
  const diagnosisVersion = appConfigWithVersion.diagnosis_version || '1.0.0';
  const appConfig = Object.assign({}, appConfigWithVersion);
  delete appConfig.diagnosis_version;
  const config = {
    diagnosis_version: diagnosisVersion,
    app_config: appConfig,
    questions: rowsToObjects_(readRows_(ss, SHEETS.questions)).map(normalizeQuestion_),
    choices: rowsToObjects_(readRows_(ss, SHEETS.choices)).map(normalizeChoice_).filter(row => row.question_id && row.value),
    results: rowsToObjects_(readRows_(ss, SHEETS.results)).map(normalizeRow_).filter(row => row.result_code),
    result_steps: rowsToObjects_(readRows_(ss, SHEETS.resultSteps)).map(normalizeResultStep_).filter(row => row.result_code && row.type),
  };
  cache.put('config', JSON.stringify(config), CACHE_SECONDS);
  return config;
}

function saveSubmission(payload) {
  if (!payload || !payload.submission_id) return { ok: false, error: 'missing_submission_id' };
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    const sheet = ss.getSheetByName(SHEETS.submissions);
    if (!sheet) throw new Error('submissions sheet not found');
    const headers = getHeaders_(sheet);
    const idColumn = headers.indexOf('submission_id') + 1;
    if (idColumn < 1) throw new Error('submission_id header not found');
    const lastRow = sheet.getLastRow();
    if (lastRow > 1) {
      const ids = sheet.getRange(2, idColumn, lastRow - 1, 1).getValues().flat();
      if (ids.indexOf(payload.submission_id) !== -1) {
        return { ok: true, submission_id: payload.submission_id, duplicate: true };
      }
    }
    const rowObject = {
      timestamp: payload.timestamp || new Date().toISOString(),
      submission_id: payload.submission_id,
      diagnosis_version: payload.diagnosis_version || '',
      company_name: payload.company_name || '',
      industry: payload.industry || '',
      employee_size: payload.employee_size || '',
      q1_value: payload.answers && payload.answers.q1 || '',
      q2_value: payload.answers && payload.answers.q2 || '',
      q3_value: payload.answers && payload.answers.q3 || '',
      q3b_value: payload.answers && payload.answers.q3b || '',
      q4_value: payload.answers && payload.answers.q4 || '',
      q5_value: payload.answers && payload.answers.q5 || '',
      q6_value: payload.answers && payload.answers.q6 || '',
      q7_value: payload.answers && payload.answers.q7 || '',
      ceo_level: payload.computed && payload.computed.ceo_level || 0,
      ceo_tool_level: payload.computed && payload.computed.ceo_tool_level || 0,
      agent_level: payload.computed && payload.computed.agent_level || 0,
      api_level: payload.computed && payload.computed.api_level || 0,
      field_level: payload.computed && payload.computed.field_level || 0,
      admin_level: payload.computed && payload.computed.admin_level || 0,
      admin_role_level: payload.computed && payload.computed.admin_role_level || 0,
      knowledge_spread_level: payload.computed && payload.computed.knowledge_spread_level || 0,
      advanced_ai_usage: payload.computed && payload.computed.advanced_ai_usage || false,
      result_code: payload.result && payload.result.result_code || '',
      result_headline: payload.result && payload.result.headline || '',
      result_phase: payload.result && (payload.result.phase_name || payload.result.phase) || '',
      raw_payload_json: JSON.stringify(payload),
      device_type: payload.meta && payload.meta.device_type || '',
      user_agent: payload.meta && payload.meta.user_agent || '',
      answers_json: JSON.stringify(payload.answers || {}),
      computed_json: JSON.stringify(payload.computed || {}),
      config_source: payload.config_source || '',
      created_at: new Date().toISOString(),
    };
    sheet.appendRow(headers.map(header => rowObject[header] !== undefined ? rowObject[header] : ''));
    return { ok: true, submission_id: payload.submission_id };
  } finally {
    lock.releaseLock();
  }
}

function seedSheetsFromJson(jsonText, preserveSubmissions) {
  const seed = typeof jsonText === 'string' ? JSON.parse(jsonText) : jsonText;
  if (!seed) throw new Error('seed is required');
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const keepSubmissions = preserveSubmissions !== false;

  writeSheet_(ss, SHEETS.appConfig, SHEET_HEADERS.app_config, buildAppConfigRows_(seed));
  writeSheet_(ss, SHEETS.questions, SHEET_HEADERS.questions, objectRows_(seed.questions || [], SHEET_HEADERS.questions));
  writeSheet_(ss, SHEETS.choices, SHEET_HEADERS.choices, objectRows_(seed.choices || [], SHEET_HEADERS.choices));
  writeSheet_(ss, SHEETS.results, SHEET_HEADERS.results, objectRows_(seed.results || [], SHEET_HEADERS.results));
  writeSheet_(ss, SHEETS.resultSteps, SHEET_HEADERS.result_steps, objectRows_(seed.result_steps || [], SHEET_HEADERS.result_steps));
  if (keepSubmissions) {
    ensureSubmissionsHeader_(ss);
  } else {
    writeSheet_(ss, SHEETS.submissions, SHEET_HEADERS.submissions, []);
  }
  clearConfigCache();

  return {
    ok: true,
    questions: (seed.questions || []).length,
    choices: (seed.choices || []).length,
    results: (seed.results || []).length,
    result_steps: (seed.result_steps || []).length,
    preserve_submissions: keepSubmissions,
  };
}

function seedSheetsFromScriptProperty() {
  const jsonText = PropertiesService.getScriptProperties().getProperty('CONFIG_SEED_JSON');
  if (!jsonText) throw new Error('CONFIG_SEED_JSON script property not found');
  return seedSheetsFromJson(jsonText, true);
}

function clearConfigCache() {
  CacheService.getScriptCache().remove('config');
}

function jsonOutput(value) {
  return ContentService
    .createTextOutput(JSON.stringify(value))
    .setMimeType(ContentService.MimeType.JSON);
}

function readRows_(ss, sheetName) {
  const sheet = ss.getSheetByName(sheetName);
  if (!sheet) throw new Error(sheetName + ' sheet not found');
  const range = sheet.getDataRange();
  return range.getValues();
}

function rowsToObjects_(rows) {
  if (!rows || rows.length < 2) return [];
  const headers = rows[0].map(String);
  return rows.slice(1).map(row => {
    const obj = {};
    headers.forEach((header, index) => { obj[header] = row[index]; });
    return obj;
  });
}

function rowsToKeyValue_(rows) {
  const result = {};
  rowsToObjects_(rows).forEach(row => {
    if (row.key) result[row.key] = row.value;
  });
  return result;
}

function normalizeRow_(obj) {
  const normalized = {};
  Object.keys(obj).forEach(key => { normalized[key] = normalizeCell_(obj[key]); });
  return normalized;
}

function normalizeQuestion_(obj) {
  const normalized = normalizeRow_(obj);
  normalized.display_condition_json = parseJsonCell_(normalized.display_condition_json, {});
  return normalized;
}

function normalizeChoice_(obj) {
  const normalized = normalizeRow_(obj);
  Object.keys(normalized).forEach(key => {
    if (normalized[key] === '') delete normalized[key];
  });
  return normalized;
}

function normalizeResultStep_(obj) {
  const normalized = normalizeRow_(obj);
  normalized.display_condition_json = parseJsonCell_(normalized.display_condition_json, {});
  return normalized;
}

function normalizeCell_(value) {
  if (value === 'TRUE') return true;
  if (value === 'FALSE') return false;
  return value;
}

function parseJsonCell_(value, fallback) {
  if (value === '' || value === null || value === undefined) return fallback;
  if (typeof value === 'object') return value;
  try {
    return JSON.parse(value);
  } catch (error) {
    return fallback;
  }
}

function getHeaders_(sheet) {
  return sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0].map(String);
}

function buildAppConfigRows_(seed) {
  const rows = [];
  rows.push(['diagnosis_version', seed.diagnosis_version || '', 'seed']);
  const appConfig = seed.app_config || {};
  Object.keys(appConfig).sort().forEach(key => {
    rows.push([key, valueForCell_(appConfig[key]), 'seed']);
  });
  return rows;
}

function objectRows_(items, headers) {
  return items.map(item => headers.map(header => valueForCell_(item[header])));
}

function valueForCell_(value) {
  if (value === null || value === undefined) return '';
  if (typeof value === 'object') return JSON.stringify(value);
  return value;
}

function writeSheet_(ss, sheetName, headers, rows) {
  const sheet = ss.getSheetByName(sheetName) || ss.insertSheet(sheetName);
  sheet.clearContents();
  const values = [headers].concat(rows);
  sheet.getRange(1, 1, values.length, headers.length).setValues(values);
  sheet.setFrozenRows(1);
  sheet.autoResizeColumns(1, headers.length);
}

function ensureSubmissionsHeader_(ss) {
  const sheet = ss.getSheetByName(SHEETS.submissions) || ss.insertSheet(SHEETS.submissions);
  const hasData = sheet.getLastRow() > 1;
  if (hasData) return;
  sheet.clearContents();
  sheet.getRange(1, 1, 1, SHEET_HEADERS.submissions.length).setValues([SHEET_HEADERS.submissions]);
  sheet.setFrozenRows(1);
}
