const SHEET_NAMES = {
  reports: '通報フォーム',
  aiChatSummaries: 'AIチャット集計',
  settings: '設定',
  refs: '参照',
};

const SUBMISSION_STATUS_OPTIONS = ['未提出', '提出済'];
const SUBMISSION_STATUS_FILTER_OPTIONS = ['すべて', ...SUBMISSION_STATUS_OPTIONS];
const REPORT_HEADERS = [
  '提出状態',
  '受付日時',
  'case_code',
  '企業名',
  '名前',
  'いつ',
  'どこで',
  '誰が',
  '誰に',
  '内容要約',
  '相談希望',
  'LINE userId',
  'report_id',
  'case_id',
  '提出日時',
  '更新日時',
  'メモ',
  '内部フラグ',
];
const REPORT_HEADER_ROW = 15;
const REPORT_DATA_START_ROW = 16;
const AI_CHAT_SUMMARY_HEADERS = [
  'ユーザー名',
  'LINE userId',
  'case_code',
  '開始日時',
  '最終日時',
  '終了区分',
  'ルート',
  'ユーザー発言数',
  'AI応答数',
  '会話ログ',
  'case_id',
];
const AI_CHAT_SUMMARY_HEADER_ROW = 15;
const AI_CHAT_SUMMARY_DATA_START_ROW = 16;

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Kアラート')
    .addItem('期間指定で更新', 'updateReportsBySettings')
    .addItem('全件更新', 'updateAllReports')
    .addItem('提出状態をDBへ反映', 'syncReportSubmissionStatus')
    .addSeparator()
    .addItem('AIチャット集計を更新', 'updateAiChatSummariesBySettings')
    .addSeparator()
    .addItem('企業名候補を更新', 'updateCompanyCandidates')
    .addItem('定時更新トリガーを作成', 'installKAlertReportTrigger')
    .addItem('Supa停止対策トリガーを作成', 'installSupabaseKeepaliveTrigger')
    .addItem('表示固定を調整', 'fixReportSheetViewport')
    .addToUi();
}

function updateReportsBySettings() {
  setupReportSheetControls_();
  const settings = readSettings_();
  const rows = fetchReportsWithFallback_(settings);
  writeReportRows_(rows);
  writeLastUpdated_();
}

function updateAllReports() {
  setupReportSheetControls_();
  const rows = fetchReportsWithFallback_({
    startDate: '',
    endDate: '',
    companyName: '全社',
    status: 'すべて',
  });
  writeReportRows_(rows);
  writeLastUpdated_();
}

function syncReportSubmissionStatus() {
  const updates = readReportSubmissionStatusUpdates_();
  updates.forEach((update) => updateReportSubmissionStatus_(update.reportId, update.status));
  updateReportsBySettings();
}

function updateAiChatSummariesBySettings() {
  deleteDeprecatedAiResponseSheet_();
  setupAiChatSummarySheetControls_();
  const settings = readAiChatSummarySettings_();
  const rows = fetchAiChatSummariesFromFastApi_(settings);
  writeAiChatSummaryRows_(rows);
  writeAiChatSummaryLastUpdated_();
}

function updateCompanyCandidates() {
  const companies = fetchCompaniesWithFallback_();
  const sheet = getSheet_(SHEET_NAMES.refs);
  sheet.getRange(2, 1, Math.max(sheet.getLastRow() - 1, 1), 1).clearContent();
  if (companies.length > 0) {
    sheet.getRange(2, 1, companies.length, 1).setValues(companies.map((name) => [name]));
  }
}

function installKAlertReportTrigger() {
  ScriptApp.getProjectTriggers()
    .filter((trigger) => trigger.getHandlerFunction() === 'updateReportsBySettings')
    .forEach((trigger) => ScriptApp.deleteTrigger(trigger));

  ScriptApp.newTrigger('updateReportsBySettings')
    .timeBased()
    .everyHours(3)
    .create();
}

function keepSupabaseAlive() {
  const props = PropertiesService.getScriptProperties();
  const supabaseUrl = requireProperty_(props, 'SUPABASE_URL').replace(/\/$/, '');
  const anonKey = requireProperty_(props, 'SUPABASE_ANON_KEY');
  const response = UrlFetchApp.fetch(`${supabaseUrl}/rest/v1/rpc/touch_system_heartbeat`, {
    method: 'post',
    contentType: 'application/json',
    headers: {
      apikey: anonKey,
      Authorization: `Bearer ${anonKey}`,
    },
    payload: JSON.stringify({
      p_name: 'k_alert_sheet_gas',
      p_source: 'google_apps_script',
    }),
    muteHttpExceptions: true,
  });
  parseJsonResponse_(response);
}

function installSupabaseKeepaliveTrigger() {
  ScriptApp.getProjectTriggers()
    .filter((trigger) => trigger.getHandlerFunction() === 'keepSupabaseAlive')
    .forEach((trigger) => ScriptApp.deleteTrigger(trigger));

  keepSupabaseAlive();

  ScriptApp.newTrigger('keepSupabaseAlive')
    .timeBased()
    .everyHours(6)
    .create();
}

function fixReportSheetViewport() {
  const sheet = getSheet_(SHEET_NAMES.reports);
  sheet.setFrozenRows(13);
  sheet.setFrozenColumns(0);
  setupReportSheetControls_();
}

function readSettings_() {
  const reportSheet = getSheet_(SHEET_NAMES.reports);
  return {
    startDate: formatDateParam_(reportSheet.getRange('A7').getValue()),
    endDate: formatDateParam_(reportSheet.getRange('B7').getValue()),
    companyName: String(reportSheet.getRange('C7').getValue() || '全社'),
    status: String(reportSheet.getRange('D7').getValue() || 'すべて'),
  };
}

function readAiChatSummarySettings_() {
  const sheet = getOrCreateSheet_(SHEET_NAMES.aiChatSummaries);
  return {
    startDate: formatDateParam_(sheet.getRange('A7').getValue()),
    endDate: formatDateParam_(sheet.getRange('B7').getValue()),
  };
}

function fetchReportsWithFallback_(settings) {
  try {
    return fetchReportsFromFastApi_(settings);
  } catch (fastApiError) {
    console.warn(`FastAPI export failed. Falling back to Supabase RPC: ${fastApiError}`);
    return fetchReportsFromSupabaseRpc_(settings);
  }
}

function fetchCompaniesWithFallback_() {
  try {
    return fetchCompaniesFromFastApi_();
  } catch (fastApiError) {
    console.warn(`FastAPI company export failed. Falling back to Supabase RPC: ${fastApiError}`);
    return fetchCompaniesFromSupabaseRpc_();
  }
}

function fetchReportsFromFastApi_(settings) {
  const props = PropertiesService.getScriptProperties();
  const baseUrl = requireProperty_(props, 'K_ALERT_API_BASE_URL').replace(/\/$/, '');
  const adminKey = requireProperty_(props, 'K_ALERT_ADMIN_API_KEY');
  const query = toQueryString_({
    start_date: settings.startDate,
    end_date: settings.endDate,
    company_name: settings.companyName,
    status: settings.status,
    limit: 1000,
  });
  const response = UrlFetchApp.fetch(`${baseUrl}/admin/exports/reports?${query}`, {
    method: 'get',
    headers: { 'X-Admin-Api-Key': adminKey },
    muteHttpExceptions: true,
  });
  const json = parseJsonResponse_(response);
  return json.rows || [];
}

function fetchCompaniesFromFastApi_() {
  const props = PropertiesService.getScriptProperties();
  const baseUrl = requireProperty_(props, 'K_ALERT_API_BASE_URL').replace(/\/$/, '');
  const adminKey = requireProperty_(props, 'K_ALERT_ADMIN_API_KEY');
  const response = UrlFetchApp.fetch(`${baseUrl}/admin/exports/report-companies?limit=1000`, {
    method: 'get',
    headers: { 'X-Admin-Api-Key': adminKey },
    muteHttpExceptions: true,
  });
  const json = parseJsonResponse_(response);
  return json.companies || ['全社'];
}

function fetchAiChatSummariesFromFastApi_(settings) {
  const props = PropertiesService.getScriptProperties();
  const baseUrl = requireProperty_(props, 'K_ALERT_API_BASE_URL').replace(/\/$/, '');
  const adminKey = requireProperty_(props, 'K_ALERT_ADMIN_API_KEY');
  const query = toQueryString_({
    start_date: settings.startDate,
    end_date: settings.endDate,
    limit: 1000,
  });
  const response = UrlFetchApp.fetch(`${baseUrl}/admin/exports/ai-chat-summaries?${query}`, {
    method: 'get',
    headers: { 'X-Admin-Api-Key': adminKey },
    muteHttpExceptions: true,
  });
  const json = parseJsonResponse_(response);
  return json.rows || [];
}

function fetchReportsFromSupabaseRpc_(settings) {
  const props = PropertiesService.getScriptProperties();
  const supabaseUrl = requireProperty_(props, 'SUPABASE_URL').replace(/\/$/, '');
  const anonKey = requireProperty_(props, 'SUPABASE_ANON_KEY');
  const response = UrlFetchApp.fetch(`${supabaseUrl}/rest/v1/rpc/export_reports_for_sheet`, {
    method: 'post',
    contentType: 'application/json',
    headers: {
      apikey: anonKey,
      Authorization: `Bearer ${anonKey}`,
    },
    payload: JSON.stringify({
      p_start_date: settings.startDate || null,
      p_end_date: settings.endDate || null,
      p_company_name: settings.companyName || '全社',
      p_status: settings.status || 'すべて',
      p_limit: 1000,
    }),
    muteHttpExceptions: true,
  });
  return parseJsonResponse_(response);
}

function fetchCompaniesFromSupabaseRpc_() {
  const props = PropertiesService.getScriptProperties();
  const supabaseUrl = requireProperty_(props, 'SUPABASE_URL').replace(/\/$/, '');
  const anonKey = requireProperty_(props, 'SUPABASE_ANON_KEY');
  const response = UrlFetchApp.fetch(
    `${supabaseUrl}/rest/v1/rpc/export_report_companies_for_sheet`,
    {
      method: 'post',
      contentType: 'application/json',
      headers: {
        apikey: anonKey,
        Authorization: `Bearer ${anonKey}`,
      },
      payload: JSON.stringify({ p_limit: 1000 }),
      muteHttpExceptions: true,
    },
  );
  return parseJsonResponse_(response).map((row) => row['企業名']).filter(Boolean);
}

function updateReportSubmissionStatus_(reportId, status) {
  const props = PropertiesService.getScriptProperties();
  const supabaseUrl = requireProperty_(props, 'SUPABASE_URL').replace(/\/$/, '');
  const anonKey = requireProperty_(props, 'SUPABASE_ANON_KEY');
  const response = UrlFetchApp.fetch(
    `${supabaseUrl}/rest/v1/rpc/update_report_submission_status`,
    {
      method: 'post',
      contentType: 'application/json',
      headers: {
        apikey: anonKey,
        Authorization: `Bearer ${anonKey}`,
      },
      payload: JSON.stringify({
        p_report_id: reportId,
        p_submission_status: status,
        p_source: 'google_sheet',
      }),
      muteHttpExceptions: true,
    },
  );
  parseJsonResponse_(response);
}

function writeReportRows_(rows) {
  const sheet = getSheet_(SHEET_NAMES.reports);
  const clearRows = Math.max(sheet.getMaxRows() - REPORT_DATA_START_ROW + 1, 1);
  sheet.getRange(REPORT_HEADER_ROW, 1, 1, REPORT_HEADERS.length).setValues([REPORT_HEADERS]);
  sheet.getRange(REPORT_DATA_START_ROW, 1, clearRows, REPORT_HEADERS.length).clearContent();
  setupReportSheetControls_();
  if (rows.length === 0) return;

  const values = rows.map((row) => REPORT_HEADERS.map((header) => row[header] || ''));
  sheet.getRange(REPORT_DATA_START_ROW, 1, values.length, REPORT_HEADERS.length).setValues(values);
  applySubmissionStatusValidation_(sheet);
}

function writeAiChatSummaryRows_(rows) {
  const sheet = getOrCreateSheet_(SHEET_NAMES.aiChatSummaries);
  setupAiChatSummarySheetControls_();
  const clearRows = Math.max(sheet.getMaxRows() - AI_CHAT_SUMMARY_DATA_START_ROW + 1, 1);
  sheet.getRange(AI_CHAT_SUMMARY_HEADER_ROW, 1, 1, AI_CHAT_SUMMARY_HEADERS.length)
    .setValues([AI_CHAT_SUMMARY_HEADERS]);
  sheet.getRange(AI_CHAT_SUMMARY_DATA_START_ROW, 1, clearRows, AI_CHAT_SUMMARY_HEADERS.length)
    .clearContent();
  if (rows.length === 0) return;

  const values = rows.map((row) => AI_CHAT_SUMMARY_HEADERS.map((header) => row[header] || ''));
  sheet.getRange(AI_CHAT_SUMMARY_DATA_START_ROW, 1, values.length, AI_CHAT_SUMMARY_HEADERS.length)
    .setValues(values);
  sheet.getRange(AI_CHAT_SUMMARY_DATA_START_ROW, 10, values.length, 1).setWrap(true);
  sheet.autoResizeColumns(1, AI_CHAT_SUMMARY_HEADERS.length);
  sheet.setColumnWidth(10, 520);
}

function writeLastUpdated_() {
  const now = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy/MM/dd HH:mm');
  getSheet_(SHEET_NAMES.reports).getRange('N1').setValue(now);
  getSheet_(SHEET_NAMES.settings).getRange('B10').setValue(now);
}

function writeAiChatSummaryLastUpdated_() {
  const now = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy/MM/dd HH:mm');
  getOrCreateSheet_(SHEET_NAMES.aiChatSummaries).getRange('K1').setValue(now);
  getSheet_(SHEET_NAMES.settings).getRange('B12').setValue(now);
}

function getSheet_(name) {
  const sheet = SpreadsheetApp.getActive().getSheetByName(name);
  if (!sheet) throw new Error(`Sheet not found: ${name}`);
  return sheet;
}

function getOrCreateSheet_(name) {
  const spreadsheet = SpreadsheetApp.getActive();
  return spreadsheet.getSheetByName(name) || spreadsheet.insertSheet(name);
}

function setupReportSheetControls_() {
  const sheet = getSheet_(SHEET_NAMES.reports);
  sheet.getRange('D6').setValue('提出状態');
  const filterRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(SUBMISSION_STATUS_FILTER_OPTIONS, true)
    .setAllowInvalid(false)
    .build();
  sheet.getRange('D7').setDataValidation(filterRule);
  if (!SUBMISSION_STATUS_FILTER_OPTIONS.includes(String(sheet.getRange('D7').getValue() || ''))) {
    sheet.getRange('D7').setValue('すべて');
  }
  applySubmissionStatusValidation_(sheet);
}

function setupAiChatSummarySheetControls_() {
  const sheet = getOrCreateSheet_(SHEET_NAMES.aiChatSummaries);
  sheet.getRange('A1:K1').merge();
  sheet.getRange('A1').setValue('Kアラート AIチャット集計');
  sheet.getRange('A3:K3').merge();
  sheet.getRange('A3').setValue('1行を1相談ケースとして、ユーザー別にAIチャットの会話ログを集計します。終了区分は相談終了・通報完了・途中中断です。');
  sheet.getRange('A6').setValue('開始日');
  sheet.getRange('B6').setValue('終了日');
  sheet.getRange('K6').setValue('最終更新');
  sheet.getRange(AI_CHAT_SUMMARY_HEADER_ROW, 1, 1, AI_CHAT_SUMMARY_HEADERS.length)
    .setValues([AI_CHAT_SUMMARY_HEADERS]);
  sheet.setFrozenRows(13);
  sheet.setFrozenColumns(0);
  sheet.getRange('A1:K1')
    .setBackground('#142d52')
    .setFontColor('#ffd84a')
    .setFontWeight('bold')
    .setFontSize(14);
  sheet.getRange('A6:B6').setBackground('#e8eef7').setFontWeight('bold');
  sheet.getRange(AI_CHAT_SUMMARY_HEADER_ROW, 1, 1, AI_CHAT_SUMMARY_HEADERS.length)
    .setBackground('#142d52')
    .setFontColor('#ffffff')
    .setFontWeight('bold');
}

function deleteDeprecatedAiResponseSheet_() {
  const spreadsheet = SpreadsheetApp.getActive();
  const sheet = spreadsheet.getSheetByName('AI応答抽出');
  if (sheet && spreadsheet.getSheets().length > 1) {
    spreadsheet.deleteSheet(sheet);
  }
}

function applySubmissionStatusValidation_(sheet) {
  const rule = SpreadsheetApp.newDataValidation()
    .requireValueInList(SUBMISSION_STATUS_OPTIONS, true)
    .setAllowInvalid(false)
    .build();
  const rowCount = Math.max(sheet.getMaxRows() - REPORT_DATA_START_ROW + 1, 1);
  sheet.getRange(REPORT_DATA_START_ROW, 1, rowCount, 1).setDataValidation(rule);
}

function readReportSubmissionStatusUpdates_() {
  const sheet = getSheet_(SHEET_NAMES.reports);
  const lastRow = sheet.getLastRow();
  if (lastRow < REPORT_DATA_START_ROW) return [];

  const reportIdColumn = REPORT_HEADERS.indexOf('report_id') + 1;
  const values = sheet
    .getRange(REPORT_DATA_START_ROW, 1, lastRow - REPORT_DATA_START_ROW + 1, reportIdColumn)
    .getValues();

  return values
    .map((row) => ({
      status: String(row[0] || '').trim(),
      reportId: String(row[reportIdColumn - 1] || '').trim(),
    }))
    .filter((row) => row.reportId && SUBMISSION_STATUS_OPTIONS.includes(row.status));
}

function requireProperty_(props, key) {
  const value = props.getProperty(key);
  if (!value) throw new Error(`Script property is not configured: ${key}`);
  return value;
}

function parseJsonResponse_(response) {
  const status = response.getResponseCode();
  const text = response.getContentText();
  if (status < 200 || status >= 300) {
    throw new Error(`HTTP ${status}: ${text}`);
  }
  return JSON.parse(text);
}

function toQueryString_(params) {
  return Object.keys(params)
    .filter((key) => params[key] !== undefined && params[key] !== null && params[key] !== '')
    .map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&');
}

function formatDateParam_(value) {
  if (!value) return '';
  if (Object.prototype.toString.call(value) === '[object Date]') {
    return Utilities.formatDate(value, 'Asia/Tokyo', 'yyyy-MM-dd');
  }
  return String(value).replace(/\//g, '-');
}
