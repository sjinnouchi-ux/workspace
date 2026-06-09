const SHEET_NAME = 'アラート';
const TRIGGER_WORD = 'Kアラート';
const START_TRIGGER_TEXTS = ['相談する'];
const REPORT_LINK_TRIGGER_TEXTS = ['通報する'];
const DEVELOPMENT_TRIGGER_TEXTS = ['大人の保健室'];
const REQUIRED_FIELDS = ['when', 'where', 'who', 'toWhom', 'what', 'how'];
const INTRO_MESSAGE = 'こんにちは。このLINEのチャット内容は匿名報告として取り扱われますのでご安心ください。必要に応じて皆様に危害が及ばないように担当者より対応させていただきます。今回はどのような事象がありましたか？';
const COMPLETE_MESSAGE = '報告ありがとうございます。';
const AI_ERROR_MESSAGE = '記録しました。確認後に対応します。';
const DEVELOPMENT_MESSAGE = '開発中です。';
const REPORT_LINK_TITLE = '通報する';
const REPORT_LINK_BODY = '匿名での報告となりますので、安心して報告してください';
const REPORT_LINK_BUTTON = '報告画面を開く';
const REPORT_LINK_URL_MISSING_MESSAGE = '報告画面URLが未設定です。管理者へ確認してください。';
const LIFF_REPORT_SHEET_ID = 1527545544;
const LIFF_REPORT_ALLOWED_CONSULTATION = ['希望する', '希望しない'];

function doGet() {
  return jsonOutput({
    ok: true,
    service: 'k-alert-test',
    message: 'KアラートGAS is running.'
  });
}

function doPost(e) {
  try {
    const payload = parseJsonBody(e);

    if (payload.source === 'liff_report') {
      return handleLiffReportSubmission(payload);
    }

    const events = payload.events || [];
    if (events.length === 0) {
      return jsonOutput({ handled: false, reason: 'no_events' });
    }

    const event = events[0];
    if (!event.message || event.message.type !== 'text') {
      return jsonOutput({ handled: false, reason: 'not_text' });
    }

    const userId = event.source && event.source.userId ? event.source.userId : 'unknown';
    const text = event.message.text.trim();
    const session = getSession(userId);
    const start = getStartPayload(text);

    if (isReportLinkTrigger(text)) {
      replyReportLinkCard(event.replyToken);
      return jsonOutput({ handled: true, mode: 'report_link' });
    }

    if (isDevelopmentTrigger(text)) {
      replyLine(event.replyToken, DEVELOPMENT_MESSAGE);
      return jsonOutput({ handled: true, mode: 'development' });
    }

    if (session && start.isStart && !start.content) {
      startReportSession(event, userId);
      return jsonOutput({ handled: true, mode: 'restart' });
    }

    if (!start.isStart && !session) {
      return jsonOutput({ handled: false, reason: 'not_k_alert' });
    }

    if (session) {
      if (session.status === 'waiting_initial') {
        handleInitialReport(event, userId, text, session);
      } else {
        handleFollowUp(event, userId, session, text);
      }
      return jsonOutput({ handled: true, mode: 'follow_up' });
    }

    if (!start.content) {
      startReportSession(event, userId);
      return jsonOutput({ handled: true, mode: 'intro' });
    }

    handleInitialReport(event, userId, start.content, null);
    return jsonOutput({ handled: true, mode: 'initial' });
  } catch (err) {
    console.error(err);
    return jsonOutput({ handled: true, error: err.message });
  }
}

function handleLiffReportSubmission(payload) {
  const report = normalizeLiffReportPayload(payload);
  const sheet = getLiffReportSheet();
  ensureLiffReportHeader(sheet);
  const nextNo = getNextLiffReportNo(sheet);

  sheet.appendRow([
    nextNo,
    report.companyName,
    report.reporterName,
    report.input1,
    report.input2,
    report.input3,
    report.freeText,
    report.consultationRequest
  ]);

  return jsonOutput({
    ok: true,
    handled: true,
    mode: 'liff_report',
    no: nextNo
  });
}

function normalizeLiffReportPayload(payload) {
  const report = payload.report || {};
  const normalized = {
    companyName: normalizeField(report.companyName),
    reporterName: normalizeField(report.reporterName),
    input1: normalizeField(report.input1),
    input2: normalizeField(report.input2),
    input3: normalizeField(report.input3),
    freeText: normalizeField(report.freeText),
    consultationRequest: normalizeField(report.consultationRequest)
  };

  const requiredFields = ['companyName', 'input1', 'input2', 'input3', 'freeText', 'consultationRequest'];
  const missing = requiredFields.filter(function(field) {
    return !normalized[field];
  });
  if (missing.length > 0) {
    throw new Error('Missing required LIFF report fields: ' + missing.join(','));
  }

  if (LIFF_REPORT_ALLOWED_CONSULTATION.indexOf(normalized.consultationRequest) === -1) {
    throw new Error('Invalid consultationRequest: ' + normalized.consultationRequest);
  }

  return normalized;
}

function normalizeField(value) {
  return value === null || value === undefined ? '' : value.toString().trim();
}

function getLiffReportSheet() {
  const ss = SpreadsheetApp.openById(getRequiredProperty('SPREADSHEET_ID'));
  const sheets = ss.getSheets();
  for (let i = 0; i < sheets.length; i++) {
    if (sheets[i].getSheetId() === LIFF_REPORT_SHEET_ID) return sheets[i];
  }
  throw new Error('LIFF report sheet was not found: ' + LIFF_REPORT_SHEET_ID);
}

function ensureLiffReportHeader(sheet) {
  const headers = [
    'No',
    '企業名',
    '名前（任意）',
    '入力１',
    '入力２',
    '入力３',
    'その他（自由記載）',
    '相談受付希望'
  ];
  const current = sheet.getRange(1, 1, 1, headers.length).getValues()[0];
  if (current.join('') === '') {
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    sheet.setFrozenRows(1);
  }
}

function getNextLiffReportNo(sheet) {
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return 1;
  const values = sheet.getRange(2, 1, lastRow - 1, 1).getValues();
  const maxNo = values.reduce(function(max, row) {
    const no = Number(row[0]);
    return Number.isFinite(no) && no > max ? no : max;
  }, 0);
  return maxNo + 1;
}

function startReportSession(event, userId) {
  saveSession(userId, {
    status: 'waiting_initial',
    introMessage: INTRO_MESSAGE
  });
  replyLine(event.replyToken, INTRO_MESSAGE);
}

function handleInitialReport(event, userId, text, session) {
  const initialComment = text.trim();
  if (!initialComment) {
    startReportSession(event, userId);
    return;
  }

  const sheet = getAlertSheet();
  const rowNumber = appendInitialRow(sheet, initialComment);
  if (session && session.introMessage) {
    appendConversationLog(sheet, rowNumber, 'bot', session.introMessage);
  }
  appendConversationLog(sheet, rowNumber, 'user', initialComment);
  analyzeAndReply(event, userId, sheet, rowNumber, initialComment, '', null);
}

function analyzeAndReply(event, userId, sheet, rowNumber, initialComment, followUpText, current) {
  let analysis;
  try {
    analysis = analyzeComment(initialComment, followUpText, current);
  } catch (err) {
    console.error(err);
    sheet.getRange(rowNumber, 12).setValue('AI解析エラー: ' + summarizeError(err.message));
    clearSession(userId);
    recordBotReply(sheet, rowNumber, AI_ERROR_MESSAGE);
    replyLine(event.replyToken, AI_ERROR_MESSAGE);
    return;
  }

  updateAnalysisToRow(sheet, rowNumber, analysis);
  const missingFields = getMissingFields(analysis);

  if (missingFields.length > 0) {
    sheet.getRange(rowNumber, 12).setValue('AI解析中。不足項目: ' + missingFields.join(','));
    const question = buildMissingQuestion(missingFields, analysis);
    saveSession(userId, {
      status: 'collecting',
      rowNumber: rowNumber,
      missingFields: missingFields
    });
    recordBotReply(sheet, rowNumber, question);
    replyLine(event.replyToken, question);
    return;
  }

  clearSession(userId);
  sheet.getRange(rowNumber, 12).setValue('AI解析完了。必要項目は充足。');
  recordBotReply(sheet, rowNumber, COMPLETE_MESSAGE);
  replyLine(event.replyToken, COMPLETE_MESSAGE);
}

function handleFollowUp(event, userId, session, text) {
  const sheet = getAlertSheet();
  appendConversationLog(sheet, session.rowNumber, 'user', text);

  const current = readRowAsAnalysis(sheet, session.rowNumber);
  analyzeAndReply(event, userId, sheet, session.rowNumber, current.initialComment, text, current);
}

function appendInitialRow(sheet, initialComment) {
  const nextNo = Math.max(1, sheet.getLastRow());
  const row = sheet.getLastRow() + 1;
  sheet.getRange(row, 1, 1, 12).setValues([[
    nextNo,
    initialComment,
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    ''
  ]]);
  return row;
}

function updateAnalysisToRow(sheet, rowNumber, analysis) {
  sheet.getRange(rowNumber, 3, 1, 7).setValues([[
    analysis.when || '',
    analysis.where || '',
    analysis.who || '',
    analysis.toWhom || '',
    analysis.what || '',
    analysis.how || '',
    analysis.urgency || ''
  ]]);
  if (analysis.notes) {
    sheet.getRange(rowNumber, 12).setValue(analysis.notes);
  }
}

function appendConversationLog(sheet, rowNumber, speaker, text) {
  const cell = sheet.getRange(rowNumber, 11);
  const current = cell.getValue();
  const timestamp = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy/MM/dd HH:mm:ss');
  const line = '[' + timestamp + '] ' + speaker + ': ' + text;
  cell.setValue(current ? current + '\n' + line : line);
}

function recordBotReply(sheet, rowNumber, text) {
  sheet.getRange(rowNumber, 10).setValue(text);
  appendConversationLog(sheet, rowNumber, 'bot', text);
}

function readRowAsAnalysis(sheet, rowNumber) {
  const values = sheet.getRange(rowNumber, 1, 1, 12).getValues()[0];
  return {
    initialComment: values[1] || '',
    when: values[2] || '',
    where: values[3] || '',
    who: values[4] || '',
    toWhom: values[5] || '',
    what: values[6] || '',
    how: values[7] || '',
    urgency: values[8] || '',
    notes: values[11] || ''
  };
}

function analyzeComment(initialComment, followUpText, current) {
  const provider = getAiProvider();
  const schema = buildAnalysisSchema();
  const inputText = buildAnalysisPrompt(initialComment, followUpText, current);

  if (provider === 'anthropic') {
    return analyzeCommentWithAnthropic(inputText, schema);
  }
  if (provider === 'openai') {
    return analyzeCommentWithOpenAi(inputText, schema);
  }
  throw new Error('Unsupported AI_PROVIDER: ' + provider);
}

function getAiProvider() {
  const configured = getOptionalProperty('AI_PROVIDER').toLowerCase();
  if (configured) return configured;
  if (getOptionalProperty('ANTHROPIC_API_KEY')) return 'anthropic';
  return 'openai';
}

function buildAnalysisSchema() {
  return {
    type: 'object',
    additionalProperties: false,
    required: ['when', 'where', 'who', 'toWhom', 'what', 'how', 'urgency', 'notes'],
    properties: {
      when: { type: 'string', description: 'いつ。日時、日付、時期、期限。分からない場合は空文字。' },
      where: { type: 'string', description: 'どこで。場所、施設、部屋、状況の発生箇所。分からない場合は空文字。' },
      who: { type: 'string', description: 'だれが。行為者、報告者、発信者、起点になった人。分からない場合は空文字。' },
      toWhom: { type: 'string', description: 'だれに。対象者、被害者、依頼先、影響を受けた人。分からない場合は空文字。' },
      what: { type: 'string', description: 'なにを。起きたこと、依頼内容、問題、行為の内容。分からない場合は空文字。' },
      how: { type: 'string', description: 'どのように。状態、方法、経過、程度。分からない場合は空文字。' },
      urgency: { type: 'string', enum: ['高', '中', '低', ''], description: '緊急度。判断できない場合は空文字。' },
      notes: { type: 'string', description: '判断根拠や補足。なければ空文字。' }
    }
  };
}

function buildAnalysisPrompt(initialComment, followUpText, current) {
  return [
    'あなたは看護・介護関連の連絡内容を記録用に整理するアシスタントです。',
    '初回コメントと追加回答から、Kアラートの項目を抽出してください。',
    '推測しすぎず、不明な項目は空文字にしてください。',
    '既存値にある情報は、追加回答で否定されない限り保持してください。',
    '',
    '既存値:',
    JSON.stringify(current || {}, null, 2),
    '',
    '初回コメント:',
    initialComment,
    '',
    '追加回答:',
    followUpText || ''
  ].join('\n');
}

function analyzeCommentWithOpenAi(inputText, schema) {
  const apiKey = getRequiredProperty('OPENAI_API_KEY');
  const model = getRequiredProperty('OPENAI_MODEL');
  const response = UrlFetchApp.fetch('https://api.openai.com/v1/responses', {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer ' + apiKey
    },
    payload: JSON.stringify({
      model: model,
      input: inputText,
      text: {
        format: {
          type: 'json_schema',
          name: 'k_alert_analysis',
          strict: true,
          schema: schema
        }
      }
    }),
    muteHttpExceptions: true
  });

  const status = response.getResponseCode();
  const body = response.getContentText();
  if (status < 200 || status >= 300) {
    throw new Error('OpenAI API error: ' + status + ' ' + body);
  }

  return parseOpenAiStructuredOutput(JSON.parse(body));
}

function analyzeCommentWithAnthropic(inputText, schema) {
  const apiKey = getRequiredProperty('ANTHROPIC_API_KEY');
  const model = getOptionalProperty('ANTHROPIC_MODEL') || 'claude-haiku-4-5';
  const response = UrlFetchApp.fetch('https://api.anthropic.com/v1/messages', {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01'
    },
    payload: JSON.stringify({
      model: model,
      max_tokens: 700,
      messages: [
        {
          role: 'user',
          content: inputText
        }
      ],
      output_config: {
        format: {
          type: 'json_schema',
          schema: schema
        }
      }
    }),
    muteHttpExceptions: true
  });

  const status = response.getResponseCode();
  const body = response.getContentText();
  if (status < 200 || status >= 300) {
    throw new Error('Anthropic API error: ' + status + ' ' + body);
  }

  return parseAnthropicStructuredOutput(JSON.parse(body));
}

function parseOpenAiStructuredOutput(response) {
  if (response.output_parsed) {
    return response.output_parsed;
  }
  if (response.output_text) {
    return JSON.parse(response.output_text);
  }
  const output = response.output || [];
  for (let i = 0; i < output.length; i++) {
    const content = output[i].content || [];
    for (let j = 0; j < content.length; j++) {
      if (content[j].parsed) return content[j].parsed;
      if (content[j].text) return JSON.parse(content[j].text);
    }
  }
  throw new Error('OpenAI structured output was not found.');
}

function parseAnthropicStructuredOutput(response) {
  const content = response.content || [];
  for (let i = 0; i < content.length; i++) {
    if (content[i].type === 'text' && content[i].text) {
      return JSON.parse(content[i].text);
    }
  }
  throw new Error('Anthropic structured output was not found.');
}

function getMissingFields(analysis) {
  return REQUIRED_FIELDS.filter(function(field) {
    return !analysis[field] || analysis[field].toString().trim() === '';
  });
}

function buildMissingQuestion(missingFields) {
  const labels = {
    when: 'いつ',
    where: 'どこで',
    who: 'だれが',
    toWhom: 'だれに',
    what: '何が起きたか',
    how: 'どのような状況か'
  };
  const missingLabels = missingFields.map(function(field) {
    return labels[field];
  });
  return '確認です。' + missingLabels.join('、') + 'を教えてください。';
}

function replyLine(replyToken, text) {
  replyLineMessages(replyToken, [{ type: 'text', text: text }]);
}

function replyReportLinkCard(replyToken) {
  const reportFormUrl = getOptionalProperty('K_ALERT_LIFF_URL');
  if (!reportFormUrl) {
    replyLine(replyToken, REPORT_LINK_URL_MISSING_MESSAGE);
    return;
  }
  replyLineMessages(replyToken, [buildReportLinkFlexMessage(reportFormUrl)]);
}

function replyLineMessages(replyToken, messages) {
  const token = getRequiredProperty('LINE_CHANNEL_ACCESS_TOKEN');
  const response = UrlFetchApp.fetch('https://api.line.me/v2/bot/message/reply', {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer ' + token
    },
    payload: JSON.stringify({
      replyToken: replyToken,
      messages: messages
    }),
    muteHttpExceptions: true
  });
  console.log('LINE reply:', response.getResponseCode(), response.getContentText());
}

function buildReportLinkFlexMessage(reportFormUrl) {
  return {
    type: 'flex',
    altText: REPORT_LINK_TITLE,
    contents: {
      type: 'bubble',
      size: 'kilo',
      body: {
        type: 'box',
        layout: 'vertical',
        paddingAll: '0px',
        contents: [
          {
            type: 'box',
            layout: 'vertical',
            backgroundColor: '#142d52',
            paddingTop: '7px',
            paddingBottom: '7px',
            paddingStart: '12px',
            paddingEnd: '12px',
            contents: [
              {
                type: 'text',
                text: REPORT_LINK_TITLE,
                color: '#ffd84a',
                weight: 'bold',
                size: 'sm'
              }
            ]
          },
          {
            type: 'box',
            layout: 'vertical',
            paddingAll: '12px',
            spacing: '8px',
            contents: [
              {
                type: 'text',
                text: REPORT_LINK_BODY,
                color: '#4b5563',
                size: 'xs',
                wrap: true
              },
              {
                type: 'button',
                style: 'primary',
                height: 'sm',
                color: '#5ecf5f',
                action: {
                  type: 'uri',
                  label: REPORT_LINK_BUTTON,
                  uri: reportFormUrl
                }
              }
            ]
          }
        ]
      }
    }
  };
}

function getAlertSheet() {
  const ss = SpreadsheetApp.openById(getRequiredProperty('SPREADSHEET_ID'));
  const sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  ensureHeader(sheet);
  return sheet;
}

function ensureHeader(sheet) {
  const headers = [
    'No',
    '初回コメント内容',
    'いつ',
    'どこで',
    'だれが',
    'だれに',
    'なにを',
    'どのように',
    '緊急度',
    '対応コメント',
    'やり取り全文記録',
    '備考'
  ];
  const current = sheet.getRange(1, 1, 1, headers.length).getValues()[0];
  if (current.join('') === '') {
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    sheet.setFrozenRows(1);
  }
}

function setupSpreadsheetFormatting() {
  const ss = SpreadsheetApp.openById(getRequiredProperty('SPREADSHEET_ID'));
  const alertSheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  ensureHeader(alertSheet);
  formatAlertSheet(alertSheet);

  const settingsSheet = ss.getSheetByName('設定') || ss.insertSheet('設定');
  ensureSettingsSheet(settingsSheet);
  formatSettingsSheet(settingsSheet);

  return jsonOutput({
    ok: true,
    message: 'Spreadsheet formatting completed.'
  });
}

function formatAlertSheet(sheet) {
  const maxRows = Math.max(sheet.getMaxRows(), 100);
  const headerRange = sheet.getRange(1, 1, 1, 12);
  const bodyRange = sheet.getRange(2, 1, maxRows - 1, 12);
  const tableRange = sheet.getRange(1, 1, maxRows, 12);

  headerRange
    .setBackground('#0F766E')
    .setFontColor('#FFFFFF')
    .setFontWeight('bold')
    .setHorizontalAlignment('center')
    .setVerticalAlignment('middle')
    .setWrap(true);

  bodyRange
    .setBackground('#FFFFFF')
    .setFontColor('#111827')
    .setVerticalAlignment('top')
    .setWrap(true);

  tableRange.setBorder(true, true, true, true, true, true, '#CBD5E1', SpreadsheetApp.BorderStyle.SOLID);

  sheet.setFrozenRows(1);
  sheet.setRowHeight(1, 34);
  sheet.setColumnWidth(1, 56);
  sheet.setColumnWidth(2, 260);
  sheet.setColumnWidth(3, 120);
  sheet.setColumnWidth(4, 150);
  sheet.setColumnWidth(5, 150);
  sheet.setColumnWidth(6, 150);
  sheet.setColumnWidth(7, 220);
  sheet.setColumnWidth(8, 240);
  sheet.setColumnWidth(9, 90);
  sheet.setColumnWidth(10, 260);
  sheet.setColumnWidth(11, 360);
  sheet.setColumnWidth(12, 220);

  sheet.getRange('A:A').setHorizontalAlignment('center');
  sheet.getRange('I:I').setHorizontalAlignment('center');
  sheet.getRange(2, 1, maxRows - 1, 1).setBackground('#F8FAFC');
  sheet.getRange(2, 9, maxRows - 1, 1).setBackground('#FEF3C7');
  sheet.getRange(2, 11, maxRows - 1, 1).setBackground('#F8FAFC');
}

function ensureSettingsSheet(sheet) {
  const values = sheet.getRange(1, 1, 4, 3).getValues();
  if (values[0].join('') !== '') return;

  sheet.getRange(1, 1, 4, 3).setValues([
    ['キー', '値', '備考'],
    ['trigger_word', 'Kアラート', '公式LINEで開始する文言'],
    ['urgency_options', '高,中,低', '緊急度候補'],
    ['required_fields', 'いつ,どこで,だれが,だれに,なにを,どのように', '完了判定に使う項目']
  ]);
}

function formatSettingsSheet(sheet) {
  const maxRows = Math.max(sheet.getMaxRows(), 30);
  const headerRange = sheet.getRange(1, 1, 1, 3);
  const tableRange = sheet.getRange(1, 1, maxRows, 3);

  headerRange
    .setBackground('#1D4ED8')
    .setFontColor('#FFFFFF')
    .setFontWeight('bold')
    .setHorizontalAlignment('center');

  sheet.getRange(2, 1, maxRows - 1, 3)
    .setBackground('#FFFFFF')
    .setFontColor('#111827')
    .setVerticalAlignment('top')
    .setWrap(true);

  tableRange.setBorder(true, true, true, true, true, true, '#CBD5E1', SpreadsheetApp.BorderStyle.SOLID);

  sheet.setFrozenRows(1);
  sheet.setRowHeight(1, 32);
  sheet.setColumnWidth(1, 180);
  sheet.setColumnWidth(2, 260);
  sheet.setColumnWidth(3, 320);
  sheet.getRange('A:A').setBackground('#F8FAFC');
}

function setupAnthropicProperties() {
  PropertiesService.getScriptProperties().setProperties({
    AI_PROVIDER: 'anthropic',
    ANTHROPIC_MODEL: 'claude-haiku-4-5'
  }, false);

  return jsonOutput({
    ok: true,
    message: 'Anthropic properties were set. Add ANTHROPIC_API_KEY manually.'
  });
}

function getStartPayload(text) {
  const normalized = text.trim();
  for (let i = 0; i < START_TRIGGER_TEXTS.length; i++) {
    const trigger = START_TRIGGER_TEXTS[i];
    if (normalized === trigger) {
      return { isStart: true, content: '' };
    }
    if (
      normalized.indexOf(trigger + ' ') === 0 ||
      normalized.indexOf(trigger + '　') === 0 ||
      normalized.indexOf(trigger + ':') === 0 ||
      normalized.indexOf(trigger + '：') === 0
    ) {
      return {
        isStart: true,
        content: normalized.substring(trigger.length).replace(/^[\s　:：]+/, '').trim()
      };
    }
  }
  return { isStart: false, content: '' };
}

function isDevelopmentTrigger(text) {
  const normalized = text.trim();
  return DEVELOPMENT_TRIGGER_TEXTS.indexOf(normalized) !== -1;
}

function isReportLinkTrigger(text) {
  const normalized = text.trim();
  return REPORT_LINK_TRIGGER_TEXTS.indexOf(normalized) !== -1;
}

function getSession(userId) {
  const raw = CacheService.getScriptCache().get('session:' + userId);
  return raw ? JSON.parse(raw) : null;
}

function saveSession(userId, session) {
  CacheService.getScriptCache().put('session:' + userId, JSON.stringify(session), 21600);
}

function clearSession(userId) {
  CacheService.getScriptCache().remove('session:' + userId);
}

function parseJsonBody(e) {
  if (!e || !e.postData || !e.postData.contents) {
    throw new Error('Request body is empty.');
  }
  return JSON.parse(e.postData.contents);
}

function getRequiredProperty(key) {
  const value = PropertiesService.getScriptProperties().getProperty(key);
  if (!value) {
    throw new Error('Script property is missing: ' + key);
  }
  return value;
}

function getOptionalProperty(key) {
  return PropertiesService.getScriptProperties().getProperty(key) || '';
}

function summarizeError(message) {
  if (message.indexOf('insufficient_quota') !== -1 || message.indexOf('exceeded your current quota') !== -1) {
    return 'OpenAI APIの利用枠不足';
  }
  if (message.length > 240) {
    return message.substring(0, 240) + '...';
  }
  return message;
}

function jsonOutput(value) {
  return ContentService
    .createTextOutput(JSON.stringify(value))
    .setMimeType(ContentService.MimeType.JSON);
}
