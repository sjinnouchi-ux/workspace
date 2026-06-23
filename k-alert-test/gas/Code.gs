const SHEET_NAME = 'アラート';
const TRIGGER_WORD = 'Kアラート';
const START_TRIGGER_TEXTS = ['相談する'];
const CONSULT_START_POSTBACK = 'action=consult';
const CONSULT_END_POSTBACK = 'action=end_consult';
const INVESTIGATOR_CONSULT_POSTBACK = 'action=investigator_consult';
const CONSULT_END_LABEL = '相談を終了する';
const DECISION_REPORT = 'report';
const DECISION_CONSULT = 'consult';
const DECISION_CANCEL = 'cancel';
const REPORT_LINK_TRIGGER_TEXTS = ['通報する'];
const DEVELOPMENT_TRIGGER_TEXTS = ['大人の保健室'];
const REQUIRED_FIELDS = ['when', 'where', 'who', 'toWhom', 'what', 'how'];
const FIELD_LABELS = {
  when: 'いつの事ですか？',
  where: 'どこで起きましたか？',
  who: 'だれが起こした人ですか？',
  toWhom: 'だれに対してのことですか？',
  whatHow: 'なにをどのようにしていましたか'
};
const INTRO_MESSAGE = [
  'こんにちは。Kアラートです🛡️',
  '',
  'このLINEのチャット内容は、匿名相談として取り扱います。',
  '安心して、話せる範囲で大丈夫です。',
  '',
  '必要に応じて、皆さまに危害が及ばないよう担当者より対応します。',
  '',
  '今回はどのような事象がありましたか？'
].join('\n');
const CONSULT_END_MESSAGE = '相談を終了しました。必要なときは、また「相談する」から開始してください。';
const COMPLETE_MESSAGE = '報告ありがとうございます。';
const AI_ERROR_MESSAGE = '記録しました。確認後に対応します。';
const DEVELOPMENT_MESSAGE = '開発中です。';
const REPORT_LINK_TITLE = '通報する';
const REPORT_LINK_BODY = '生命・身体・財産に対して急を要する場合は110番・119番してください';
const REPORT_LINK_BUTTON = '報告画面を開く';
const REPORT_LINK_URL_MISSING_MESSAGE = '報告画面URLが未設定です。管理者へ確認してください。';
const INVESTIGATOR_REQUEST_DISPLAY_TEXT = '調査官への依頼\n※調査官が改めてチャットしますので、連絡をお待ちください';
const INVESTIGATOR_REQUEST_LOG_MESSAGE = '調査官への依頼を受け付けました。調査官からの連絡待ち。';
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
    const userId = event.source && event.source.userId ? event.source.userId : 'unknown';

    if (event.type === 'postback') {
      return handlePostbackEvent(event, userId);
    }

    if (!event.message || event.message.type !== 'text') {
      return jsonOutput({ handled: false, reason: 'not_text' });
    }

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
    report.when,
    report.where,
    report.who,
    report.toWhom,
    report.whatHow,
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

function handlePostbackEvent(event, userId) {
  const data = event.postback && event.postback.data ? event.postback.data : '';

  if (data === CONSULT_START_POSTBACK) {
    startReportSession(event, userId);
    return jsonOutput({ handled: true, mode: 'consult_start_postback' });
  }

  if (data === CONSULT_END_POSTBACK) {
    clearSession(userId);
    replyLine(event.replyToken, CONSULT_END_MESSAGE);
    return jsonOutput({ handled: true, mode: 'consult_end' });
  }

  if (data === INVESTIGATOR_CONSULT_POSTBACK) {
    const session = getSession(userId);
    if (session && session.rowNumber) {
      const sheet = getAlertSheet();
      recordBotReply(sheet, session.rowNumber, INVESTIGATOR_REQUEST_LOG_MESSAGE);
      sheet.getRange(session.rowNumber, 11).setValue('報告せず調査官チャット相談を希望');
    }
    clearSession(userId);
    return jsonOutput({ handled: true, mode: 'investigator_consult' });
  }

  return jsonOutput({ handled: false, reason: 'unknown_postback' });
}

function normalizeLiffReportPayload(payload) {
  const report = payload.report || {};
  const normalized = {
    companyName: normalizeField(report.companyName),
    reporterName: normalizeField(report.reporterName),
    when: normalizeField(report.when),
    where: normalizeField(report.where),
    who: normalizeField(report.who),
    toWhom: normalizeField(report.toWhom),
    whatHow: normalizeField(report.whatHow || joinWhatHow(report.what, report.how)),
    freeText: normalizeField(report.freeText),
    consultationRequest: normalizeField(report.consultationRequest)
  };

  const requiredFields = ['companyName', 'when', 'where', 'who', 'toWhom', 'whatHow', 'consultationRequest'];
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

function joinWhatHow(what, how) {
  return [normalizeField(what), normalizeField(how)].filter(function(value) {
    return value;
  }).join(' / ');
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
    FIELD_LABELS.when,
    FIELD_LABELS.where,
    FIELD_LABELS.who,
    FIELD_LABELS.toWhom,
    FIELD_LABELS.whatHow,
    'その他（自由記載）',
    '相談受付希望'
  ];
  const currentWidth = Math.max(sheet.getLastColumn(), headers.length);
  const current = sheet.getRange(1, 1, 1, currentWidth).getValues()[0];
  const hasOldLiffHeader = current[3] === '入力１' &&
    current[4] === '入力２' &&
    current[5] === '入力３' &&
    current[6] === 'その他（自由記載）' &&
    current[7] === '相談受付希望';
  const hasSplitWhatHowHeader = current[3] === 'When（いつ）' &&
    current[4] === 'Where（どこで）' &&
    current[5] === 'Who（だれが）' &&
    current[6] === 'Whom（だれに）' &&
    current[7] === 'What（なにを）' &&
    current[8] === 'How（どのように）';
  if (hasOldLiffHeader) {
    sheet.insertColumnsAfter(6, 3);
  } else if (hasSplitWhatHowHeader) {
    mergeColumns(sheet, 8, 9);
    sheet.deleteColumn(9);
  }
  if (current.join('') === '') {
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    sheet.setFrozenRows(1);
  } else {
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  }
}

function mergeColumns(sheet, leftColumn, rightColumn) {
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return;
  const values = sheet.getRange(2, leftColumn, lastRow - 1, 2).getValues();
  const merged = values.map(function(row) {
    return [joinWhatHow(row[0], row[1])];
  });
  sheet.getRange(2, leftColumn, merged.length, 1).setValues(merged);
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
  replyLineWithConsultEnd(event.replyToken, INTRO_MESSAGE);
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

function analyzeAndReply(event, userId, sheet, rowNumber, initialComment, followUpText, current, session) {
  let analysis;
  try {
    analysis = analyzeComment(initialComment, followUpText, current);
  } catch (err) {
    console.error(err);
    sheet.getRange(rowNumber, 11).setValue('AI解析エラー: ' + summarizeError(err.message));
    clearSession(userId);
    recordBotReply(sheet, rowNumber, AI_ERROR_MESSAGE);
    replyLine(event.replyToken, AI_ERROR_MESSAGE);
    return;
  }

  updateAnalysisToRow(sheet, rowNumber, analysis);
  const missingFields = getMissingFields(analysis);
  const turnCount = session && session.turnCount ? Number(session.turnCount) + 1 : 1;

  if (turnCount < 2) {
    const empathyReply = buildEmpathyReply(turnCount);
    saveSession(userId, {
      status: 'collecting',
      rowNumber: rowNumber,
      missingFields: missingFields,
      turnCount: turnCount
    });
    sheet.getRange(rowNumber, 11).setValue('AI解析中。相談内容を聞き取り中。');
    recordBotReply(sheet, rowNumber, empathyReply);
    replyLineWithConsultEnd(event.replyToken, empathyReply);
    return;
  }

  if (missingFields.length > 0) {
    sheet.getRange(rowNumber, 11).setValue('AI解析中。不足項目: ' + missingFields.join(','));

    const decisionText = buildReportDecisionText();
    saveSession(userId, {
      status: 'awaiting_decision',
      rowNumber: rowNumber,
      missingFields: missingFields,
      turnCount: turnCount
    });
    recordBotReply(sheet, rowNumber, decisionText);
    replyLineWithConsultEnd(event.replyToken, decisionText);
    return;
  }

  sheet.getRange(rowNumber, 11).setValue('AI解析完了。報告または調査官相談の選択待ち。');
  const decisionText = buildReportDecisionText();
  saveSession(userId, {
    status: 'awaiting_decision',
    rowNumber: rowNumber,
    turnCount: turnCount
  });
  recordBotReply(sheet, rowNumber, decisionText);
  replyLineWithConsultEnd(event.replyToken, decisionText);
}

function handleFollowUp(event, userId, session, text) {
  const sheet = getAlertSheet();
  appendConversationLog(sheet, session.rowNumber, 'user', text);

  if (session.status === 'awaiting_decision') {
    handleDecisionReply(event, userId, sheet, session, text);
    return;
  }

  const current = readRowAsAnalysis(sheet, session.rowNumber);
  analyzeAndReply(event, userId, sheet, session.rowNumber, current.initialComment, text, current, session);
}

function appendInitialRow(sheet, initialComment) {
  const nextNo = Math.max(1, sheet.getLastRow());
  const row = sheet.getLastRow() + 1;
  sheet.getRange(row, 1, 1, 11).setValues([[
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
    ''
  ]]);
  return row;
}

function updateAnalysisToRow(sheet, rowNumber, analysis) {
  sheet.getRange(rowNumber, 3, 1, 6).setValues([[
    analysis.when || '',
    analysis.where || '',
    analysis.who || '',
    analysis.toWhom || '',
    joinWhatHow(analysis.what, analysis.how),
    analysis.urgency || ''
  ]]);
  if (analysis.notes) {
    sheet.getRange(rowNumber, 11).setValue(analysis.notes);
  }
}

function appendConversationLog(sheet, rowNumber, speaker, text) {
  const cell = sheet.getRange(rowNumber, 10);
  const current = cell.getValue();
  const timestamp = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy/MM/dd HH:mm:ss');
  const line = '[' + timestamp + '] ' + speaker + ': ' + text;
  cell.setValue(current ? current + '\n' + line : line);
}

function recordBotReply(sheet, rowNumber, text) {
  sheet.getRange(rowNumber, 9).setValue(text);
  appendConversationLog(sheet, rowNumber, 'bot', text);
}

function readRowAsAnalysis(sheet, rowNumber) {
  const values = sheet.getRange(rowNumber, 1, 1, 11).getValues()[0];
  return {
    initialComment: values[1] || '',
    when: values[2] || '',
    where: values[3] || '',
    who: values[4] || '',
    toWhom: values[5] || '',
    what: values[6] || '',
    how: '',
    urgency: values[7] || '',
    notes: values[10] || ''
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
      when: { type: 'string', description: 'いつの事ですか？ 日時、日付、時期、期限。分からない場合は空文字。' },
      where: { type: 'string', description: 'どこで起きましたか？ 場所、施設、部屋、状況の発生箇所。分からない場合は空文字。' },
      who: { type: 'string', description: 'だれが起こした人ですか？ 行為者、報告者、発信者、起点になった人。分からない場合は空文字。' },
      toWhom: { type: 'string', description: 'だれに対してのことですか？ 対象者、被害者、依頼先、影響を受けた人。分からない場合は空文字。' },
      what: { type: 'string', description: 'なにをしていましたか？ 起きたこと、依頼内容、問題、行為の内容。分からない場合は空文字。' },
      how: { type: 'string', description: 'どのようにしていましたか？ 状態、方法、経過、程度。分からない場合は空文字。' },
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

function buildEmpathyReply(turnCount) {
  if (turnCount <= 1) {
    return '話してくださってありがとうございます。\n\nつらい状況だったと思います。続けて、覚えている範囲で教えてください。';
  }
  return 'ここまで教えてくださりありがとうございます。\n\n無理のない範囲で大丈夫です。もう少しだけ状況を確認させてください。';
}

function classifyDecision(text) {
  const normalized = normalizeField(text);
  const compact = normalized.replace(/[\s\u3000]/g, '');
  if (!compact) return { decision: '', notes: 'empty' };

  if (
    /相談/.test(compact) &&
    (/報告しない|通報しない|会社に報告しない|会社には報告しない|報告せず|通報せず/.test(compact) || !/報告|通報/.test(compact))
  ) {
    return { decision: DECISION_CONSULT, notes: 'rule_consult' };
  }

  if (/報告|通報|会社/.test(compact) && !/報告しない|通報しない|やめ|キャンセル|不要|終了/.test(compact)) {
    return { decision: DECISION_REPORT, notes: 'rule_report' };
  }

  if (/やめ|止め|キャンセル|終了|不要|大丈夫|結構|しない|やはり/.test(compact)) {
    return { decision: DECISION_CANCEL, notes: 'rule_cancel' };
  }

  try {
    return classifyDecisionWithAi(normalized);
  } catch (err) {
    console.error(err);
    return { decision: '', notes: 'classification_error: ' + summarizeError(err.message) };
  }
}

function classifyDecisionWithAi(text) {
  const schema = {
    type: 'object',
    additionalProperties: false,
    required: ['decision', 'notes'],
    properties: {
      decision: {
        type: 'string',
        enum: [DECISION_REPORT, DECISION_CONSULT, DECISION_CANCEL, ''],
        description: '匿名で会社に報告するなら report。報告せずに担当調査官へ相談するなら consult。やはりやめた・終了・不要なら cancel。判断できない場合は空文字。'
      },
      notes: { type: 'string', description: '判断理由。なければ空文字。' }
    }
  };
  const prompt = [
    'ユーザーの返答を次の3分類のどれかに分類してください。',
    '- report: 匿名で会社に報告する',
    '- consult: 報告せずに相談する',
    '- cancel: やはりやめた',
    '判断できない場合は decision を空文字にしてください。',
    '',
    '返答:',
    text
  ].join('\n');

  const provider = getAiProvider();
  if (provider === 'anthropic') return analyzeCommentWithAnthropic(prompt, schema);
  if (provider === 'openai') return analyzeCommentWithOpenAi(prompt, schema);
  throw new Error('Unsupported AI_PROVIDER: ' + provider);
}

function handleDecisionReply(event, userId, sheet, session, text) {
  const result = classifyDecision(text);
  const decision = result.decision || '';
  const reportFormUrl = getOptionalProperty('K_ALERT_LIFF_URL');

  if (!decision) {
    const retryText = 'すみません。どれに近いか、短く教えてください。\n\n「匿名で会社に報告する」\n「報告せずに相談する」\n「やはりやめた」';
    recordBotReply(sheet, session.rowNumber, retryText);
    replyLineWithConsultEnd(event.replyToken, retryText);
    return;
  }

  if (decision === DECISION_REPORT && !reportFormUrl) {
    recordBotReply(sheet, session.rowNumber, REPORT_LINK_URL_MISSING_MESSAGE);
    replyLineWithConsultEnd(event.replyToken, REPORT_LINK_URL_MISSING_MESSAGE);
    return;
  }

  sheet.getRange(session.rowNumber, 11).setValue('相談方針: ' + decision + ' / ' + (result.notes || ''));

  if (decision === DECISION_CANCEL) {
    clearSession(userId);
  }

  recordBotReply(sheet, session.rowNumber, getDecisionButtonTitle(decision));
  replyLineMessages(event.replyToken, [buildDecisionActionFlexMessage(decision, reportFormUrl)]);
}

function buildReportDecisionText() {
  return [
    '今回のご相談を、匿名で会社に報告しますか？',
    '',
    '報告しない場合でも、担当の調査官にチャットで相談できます。'
  ].join('\n');
}

function replyLine(replyToken, text) {
  replyLineMessages(replyToken, [{ type: 'text', text: text }]);
}

function replyLineWithConsultEnd(replyToken, text) {
  replyLineMessages(replyToken, [buildConsultTextMessage(text)]);
}

function buildConsultTextMessage(text) {
  return {
    type: 'text',
    text: text,
    quickReply: {
      items: [
        {
          type: 'action',
          action: {
            type: 'postback',
            label: CONSULT_END_LABEL,
            data: CONSULT_END_POSTBACK,
            displayText: CONSULT_END_LABEL,
            inputOption: 'closeRichMenu'
          }
        }
      ]
    }
  };
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

function getDecisionButtonTitle(decision) {
  if (decision === DECISION_REPORT) return '匿名で会社に報告する';
  if (decision === DECISION_CONSULT) return '報告せずに相談する';
  if (decision === DECISION_CANCEL) return 'やはりやめた';
  return '相談内容の確認';
}

function buildDecisionActionFlexMessage(decision, reportFormUrl) {
  const title = getDecisionButtonTitle(decision);
  const action = getDecisionButtonAction(decision, reportFormUrl);
  return {
    type: 'flex',
    altText: title,
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
            paddingTop: '8px',
            paddingBottom: '8px',
            paddingStart: '12px',
            paddingEnd: '12px',
            contents: [
              {
                type: 'text',
                text: title,
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
            spacing: '9px',
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
                action: action
              }
            ]
          }
        ]
      }
    }
  };
}

function getDecisionButtonAction(decision, reportFormUrl) {
  if (decision === DECISION_REPORT) {
    return {
      type: 'uri',
      label: '通報フォームを開く',
      uri: reportFormUrl || 'https://line.me/'
    };
  }
  if (decision === DECISION_CONSULT) {
    return {
      type: 'postback',
      label: '調査官に依頼する',
      data: INVESTIGATOR_CONSULT_POSTBACK,
      displayText: INVESTIGATOR_REQUEST_DISPLAY_TEXT
    };
  }
  return {
    type: 'postback',
    label: '相談を終了する',
    data: CONSULT_END_POSTBACK,
    displayText: 'やはりやめた'
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
    FIELD_LABELS.when,
    FIELD_LABELS.where,
    FIELD_LABELS.who,
    FIELD_LABELS.toWhom,
    FIELD_LABELS.whatHow,
    '緊急度',
    '対応コメント',
    'やり取り全文記録',
    '備考'
  ];
  const currentWidth = Math.max(sheet.getLastColumn(), headers.length);
  const current = sheet.getRange(1, 1, 1, currentWidth).getValues()[0];
  const hasSplitWhatHowHeader = current[2] === 'When（いつ）' &&
    current[3] === 'Where（どこで）' &&
    current[4] === 'Who（だれが）' &&
    current[5] === 'Whom（だれに）' &&
    current[6] === 'What（なにを）' &&
    current[7] === 'How（どのように）';
  if (hasSplitWhatHowHeader) {
    mergeColumns(sheet, 7, 8);
    sheet.deleteColumn(8);
  }
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.setFrozenRows(1);
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
  const headerRange = sheet.getRange(1, 1, 1, 11);
  const bodyRange = sheet.getRange(2, 1, maxRows - 1, 11);
  const tableRange = sheet.getRange(1, 1, maxRows, 11);

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
  sheet.setColumnWidth(7, 300);
  sheet.setColumnWidth(8, 90);
  sheet.setColumnWidth(9, 260);
  sheet.setColumnWidth(10, 360);
  sheet.setColumnWidth(11, 220);

  sheet.getRange('A:A').setHorizontalAlignment('center');
  sheet.getRange('H:H').setHorizontalAlignment('center');
  sheet.getRange(2, 1, maxRows - 1, 1).setBackground('#F8FAFC');
  sheet.getRange(2, 8, maxRows - 1, 1).setBackground('#FEF3C7');
  sheet.getRange(2, 10, maxRows - 1, 1).setBackground('#F8FAFC');
}

function ensureSettingsSheet(sheet) {
  const values = sheet.getRange(1, 1, 4, 3).getValues();
  if (values[0].join('') !== '') return;

  sheet.getRange(1, 1, 4, 3).setValues([
    ['キー', '値', '備考'],
    ['trigger_word', 'Kアラート', '公式LINEで開始する文言'],
    ['urgency_options', '高,中,低', '緊急度候補'],
    ['required_fields', 'いつの事ですか？,どこで起きましたか？,だれが起こした人ですか？,だれに対してのことですか？,なにをどのようにしていましたか', '完了判定に使う項目']
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
