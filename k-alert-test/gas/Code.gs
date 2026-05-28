const SHEET_NAME = 'アラート';
const TRIGGER_WORD = 'Kアラート';
const REQUIRED_FIELDS = ['when', 'where', 'who', 'what', 'how'];

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

    if (!isKAlertStart(text) && !session) {
      return jsonOutput({ handled: false, reason: 'not_k_alert' });
    }

    if (session) {
      handleFollowUp(event, userId, session, text);
      return jsonOutput({ handled: true, mode: 'follow_up' });
    }

    handleInitialComment(event, userId, text);
    return jsonOutput({ handled: true, mode: 'initial' });
  } catch (err) {
    console.error(err);
    return jsonOutput({ handled: true, error: err.message });
  }
}

function handleInitialComment(event, userId, text) {
  const initialComment = stripTriggerWord(text);
  const sheet = getAlertSheet();
  const rowNumber = appendInitialRow(sheet, initialComment);
  const analysis = analyzeComment(initialComment, '');
  updateAnalysisToRow(sheet, rowNumber, analysis);

  const missingFields = getMissingFields(analysis);
  appendConversationLog(sheet, rowNumber, 'user', initialComment);

  if (missingFields.length > 0) {
    const question = buildMissingQuestion(missingFields, analysis);
    appendConversationLog(sheet, rowNumber, 'bot', question);
    saveSession(userId, {
      rowNumber: rowNumber,
      missingFields: missingFields
    });
    replyLine(event.replyToken, question);
    return;
  }

  clearSession(userId);
  replyLine(event.replyToken, buildCompleteMessage(analysis));
}

function handleFollowUp(event, userId, session, text) {
  const sheet = getAlertSheet();
  appendConversationLog(sheet, session.rowNumber, 'user', text);

  const current = readRowAsAnalysis(sheet, session.rowNumber);
  const analysis = analyzeComment(current.initialComment, text, current);
  updateAnalysisToRow(sheet, session.rowNumber, analysis);

  const missingFields = getMissingFields(analysis);
  if (missingFields.length > 0) {
    const question = buildMissingQuestion(missingFields, analysis);
    appendConversationLog(sheet, session.rowNumber, 'bot', question);
    saveSession(userId, {
      rowNumber: session.rowNumber,
      missingFields: missingFields
    });
    replyLine(event.replyToken, question);
    return;
  }

  clearSession(userId);
  const completeMessage = buildCompleteMessage(analysis);
  appendConversationLog(sheet, session.rowNumber, 'bot', completeMessage);
  replyLine(event.replyToken, completeMessage);
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
    analysis.what || '',
    analysis.how || '',
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

function readRowAsAnalysis(sheet, rowNumber) {
  const values = sheet.getRange(rowNumber, 1, 1, 11).getValues()[0];
  return {
    initialComment: values[1] || '',
    when: values[2] || '',
    where: values[3] || '',
    who: values[4] || '',
    what: values[5] || '',
    how: values[6] || '',
    urgency: values[7] || '',
    notes: values[10] || ''
  };
}

function analyzeComment(initialComment, followUpText, current) {
  const apiKey = getRequiredProperty('OPENAI_API_KEY');
  const model = getRequiredProperty('OPENAI_MODEL');
  const schema = {
    type: 'object',
    additionalProperties: false,
    required: ['when', 'where', 'who', 'what', 'how', 'urgency', 'notes'],
    properties: {
      when: { type: 'string', description: 'いつ。日時、日付、時期、期限。分からない場合は空文字。' },
      where: { type: 'string', description: 'どこで。場所、施設、部屋、状況の発生箇所。分からない場合は空文字。' },
      who: { type: 'string', description: 'だれが。対象者、関係者、投稿者。分からない場合は空文字。' },
      what: { type: 'string', description: 'なにを。起きたこと、依頼内容、問題。分からない場合は空文字。' },
      how: { type: 'string', description: 'どのように。状態、方法、経過、程度。分からない場合は空文字。' },
      urgency: { type: 'string', enum: ['高', '中', '低', ''], description: '緊急度。判断できない場合は空文字。' },
      notes: { type: 'string', description: '判断根拠や補足。なければ空文字。' }
    }
  };

  const inputText = [
    'あなたは看護・介護関連の連絡内容を記録用に整理するアシスタントです。',
    '初回コメントと追加回答から、Kアラートの項目を抽出してください。',
    '推測しすぎず、不明な項目は空文字にしてください。',
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

function getMissingFields(analysis) {
  return REQUIRED_FIELDS.filter(function(field) {
    return !analysis[field] || analysis[field].toString().trim() === '';
  });
}

function buildMissingQuestion(missingFields) {
  const labels = {
    when: 'いつの出来事ですか？',
    where: 'どこで起きましたか？',
    who: 'だれに関する内容ですか？',
    what: 'なにが起きましたか？',
    how: 'どのような状況でしたか？'
  };
  const lines = ['記録しました。確認のため、次の点だけ教えてください。', ''];
  missingFields.forEach(function(field, index) {
    lines.push(index + 1 + '. ' + labels[field]);
  });
  return lines.join('\n');
}

function buildCompleteMessage(analysis) {
  return [
    'Kアラートを記録しました。',
    'いつ: ' + analysis.when,
    'どこで: ' + analysis.where,
    'だれが: ' + analysis.who,
    'なにを: ' + analysis.what,
    'どのように: ' + analysis.how,
    '緊急度: ' + (analysis.urgency || '未判定')
  ].join('\n');
}

function replyLine(replyToken, text) {
  const token = getRequiredProperty('LINE_CHANNEL_ACCESS_TOKEN');
  const response = UrlFetchApp.fetch('https://api.line.me/v2/bot/message/reply', {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer ' + token
    },
    payload: JSON.stringify({
      replyToken: replyToken,
      messages: [{ type: 'text', text: text }]
    }),
    muteHttpExceptions: true
  });
  console.log('LINE reply:', response.getResponseCode(), response.getContentText());
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

function isKAlertStart(text) {
  return text === TRIGGER_WORD || text.indexOf(TRIGGER_WORD + ' ') === 0 || text.indexOf(TRIGGER_WORD + '　') === 0 || text.indexOf(TRIGGER_WORD + ':') === 0 || text.indexOf(TRIGGER_WORD + '：') === 0;
}

function stripTriggerWord(text) {
  return text.replace(/^Kアラート[\s　:：]*/, '').trim() || text;
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

function jsonOutput(value) {
  return ContentService
    .createTextOutput(JSON.stringify(value))
    .setMimeType(ContentService.MimeType.JSON);
}

