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
  const appConfig = rowsToKeyValue_(readRows_(ss, SHEETS.appConfig));
  const config = {
    diagnosis_version: appConfig.diagnosis_version || '1.0.0',
    app_config: appConfig,
    questions: rowsToObjects_(readRows_(ss, SHEETS.questions)).map(normalizeObject_),
    choices: rowsToObjects_(readRows_(ss, SHEETS.choices)).map(normalizeObject_).filter(row => row.question_id && row.value),
    results: rowsToObjects_(readRows_(ss, SHEETS.results)).map(normalizeObject_).filter(row => row.result_code),
    result_steps: rowsToObjects_(readRows_(ss, SHEETS.resultSteps)).map(normalizeObject_).filter(row => row.result_code && row.type),
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
      submission_id: payload.submission_id,
      diagnosis_version: payload.diagnosis_version || '',
      timestamp: payload.timestamp || new Date().toISOString(),
      company_name: payload.company_name || '',
      industry: payload.industry || '',
      employee_size: payload.employee_size || '',
      answers_json: JSON.stringify(payload.answers || {}),
      computed_json: JSON.stringify(payload.computed || {}),
      result_code: payload.result && payload.result.result_code || '',
      result_phase: payload.result && (payload.result.phase_name || payload.result.phase) || '',
      result_headline: payload.result && payload.result.headline || '',
      config_source: payload.config_source || '',
      user_agent: payload.meta && payload.meta.user_agent || '',
      created_at: new Date().toISOString(),
    };
    sheet.appendRow(headers.map(header => rowObject[header] !== undefined ? rowObject[header] : ''));
    return { ok: true, submission_id: payload.submission_id };
  } finally {
    lock.releaseLock();
  }
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

function normalizeObject_(obj) {
  const normalized = {};
  Object.keys(obj).forEach(key => {
    const value = obj[key];
    if (value === '') {
      normalized[key] = null;
    } else if (value === 'TRUE') {
      normalized[key] = true;
    } else if (value === 'FALSE') {
      normalized[key] = false;
    } else {
      normalized[key] = value;
    }
  });
  return normalized;
}

function getHeaders_(sheet) {
  return sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0].map(String);
}
