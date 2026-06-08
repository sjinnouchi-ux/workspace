// =====================================================
// 設定値
// =====================================================
// Script Properties に以下を設定してください。
// - LINE_CHANNEL_ACCESS_TOKEN
// - SPREADSHEET_ID
// - EXPENSE_SS_ID
const SUMMARY_SHEET_NAME = '集計';
const LIFF_ID = '2010069897-X9JY7R2h';
const INFO_SHEET_NAME = '公式LINE_2';
const MEMO_SHEET_NAME = '公式LINE_3';
const MEMO_STEP = 'wait_text';

function getRequiredProperty_(key) {
  const value = PropertiesService.getScriptProperties().getProperty(key);
  if (!value) throw new Error('Script Property が未設定です: ' + key);
  return value;
}

function getSpreadsheetId_() {
  return getRequiredProperty_('SPREADSHEET_ID');
}

function getExpenseSpreadsheetId_() {
  return getRequiredProperty_('EXPENSE_SS_ID');
}

function getChannelAccessToken_() {
  return getRequiredProperty_('LINE_CHANNEL_ACCESS_TOKEN');
}

function getTokyoNow_() {
  return new Date();
}

function getCurrentMonthLabel_() {
  return (getTokyoNow_().getMonth() + 1) + '月';
}

// =====================================================
// doGet: LIFF フォーム画面を配信
// =====================================================
function doGet(e) {
  if (e.parameter && e.parameter.action === 'getCategories') {
    return ContentService.createTextOutput(JSON.stringify(getCategories_()))
      .setMimeType(ContentService.MimeType.JSON);
  }

  const gasUrl = ScriptApp.getService().getUrl();
  const html = buildFormHtml(getCategories_(), gasUrl);
  return HtmlService.createHtmlOutput(html)
    .setTitle('家計簿入力')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
}

function getCategories_() {
  const sheet = SpreadsheetApp.openById(getSpreadsheetId_()).getSheetByName('家計簿');
  const values = sheet.getRange('G4:H' + sheet.getLastRow()).getValues();
  const categories = [];
  for (let i = 0; i < values.length; i++) {
    if (!values[i][0]) break;
    const name = values[i][0].toString();
    categories.push({
      name,
      needsPayment: categoryNeedsPayment_(name, values[i][1])
    });
  }
  return categories;
}

function categoryNeedsPayment_(categoryName, sheetFlag) {
  const name = String(categoryName || '');
  return sheetFlag === true || name === '交通費（経費計上）';
}

// =====================================================
// doPost: LINE Webhook と LIFF 送信の両方を処理
// =====================================================
function doPost(e) {
  let parsed;
  try {
    parsed = JSON.parse(e.postData.contents);
  } catch (err) {
    return ContentService.createTextOutput('{}');
  }

  if (parsed.source === 'liff') {
    const { month, category, content, amount, paymentMethod } = parsed;
    saveToKakeiboSheet(month, category, content, amount);
    if (paymentMethod === 'キャッシュ') {
      saveToExpenseSheet(month, amount, content);
    }
    return ContentService.createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  const event = parsed.events && parsed.events[0];
  if (!event) return ContentService.createTextOutput('OK');

  const replyToken = event.replyToken;
  const userId = event.source.userId;
  const cache = CacheService.getUserCache();

  if (!event.message || event.message.type !== 'text') {
    return ContentService.createTextOutput('OK');
  }

  const userMessage = event.message.text.trim();
  const step = cache.get(userId + '_step');

  if (userMessage === '保管と入力') {
    startLineMemoInput_(replyToken, userId, cache);
    return ContentService.createTextOutput('OK');
  }

  if (step === MEMO_STEP) {
    finishLineMemoInput_(replyToken, userMessage, userId, cache);
    return ContentService.createTextOutput('OK');
  }

  if (userMessage === '情報参照') {
    sendLineInfoOptions_(replyToken);
    return ContentService.createTextOutput('OK');
  }

  if (userMessage === '家計簿入力開始') {
    const liffUrl = 'https://liff.line.me/' + LIFF_ID;
    replyLineRaw(replyToken, {
      type: 'flex',
      altText: '家計簿の入力画面を開く',
      contents: {
        type: 'bubble',
        size: 'kilo',
        body: {
          type: 'box',
          layout: 'vertical',
          spacing: 'sm',
          contents: [
            { type: 'text', text: '📒 家計簿入力', weight: 'bold', size: 'lg', color: '#333333' },
            { type: 'text', text: '項目・金額を一画面でまとめて入力できます', size: 'xs', color: '#888888', wrap: true, margin: 'sm' }
          ]
        },
        footer: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'button',
              style: 'primary',
              color: '#00B900',
              height: 'sm',
              action: { type: 'uri', label: '入力画面を開く ✏️', uri: liffUrl }
            }
          ]
        }
      }
    });
    return ContentService.createTextOutput('OK');
  }

  if (userMessage === '家計消化状況') {
    sendBudgetReport(replyToken);
    return ContentService.createTextOutput('OK');
  }

  if (step) {
    handleKakeiboStep(replyToken, userMessage, userId, cache, step);
    return ContentService.createTextOutput('OK');
  }

  if (replyLineInfoIfMatched_(replyToken, userMessage)) {
    return ContentService.createTextOutput('OK');
  }

  return ContentService.createTextOutput('OK');
}

// =====================================================
// リッチメニュー補助機能
// =====================================================
function startLineMemoInput_(replyToken, userId, cache) {
  cache.put(userId + '_step', MEMO_STEP);
  replyLine(replyToken, 'メモしたい内容を入力してください。公式LINE_3に記録します。');
}

function finishLineMemoInput_(replyToken, text, userId, cache) {
  try {
    saveLineMemoToSheet_(text);
    replyLine(replyToken, '✅ 公式LINE_3に記録しました。');
  } catch (err) {
    replyLine(replyToken, '❌ 記録に失敗しました: ' + err.message);
  } finally {
    cache.remove(userId + '_step');
  }
}

function sendLineInfoOptions_(replyToken) {
  const sheet = getOptionalSheet_(INFO_SHEET_NAME);
  if (!sheet) {
    replyLine(replyToken, INFO_SHEET_NAME + ' シートが見つかりません。');
    return;
  }

  const lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    replyLine(replyToken, '参照できる項目がありません。');
    return;
  }

  const values = sheet.getRange(2, 1, lastRow - 1, 1).getValues();
  const options = [];
  for (let i = 0; i < values.length; i++) {
    if (values[i][0] === '' || values[i][0] === null) break;
    options.push(values[i][0].toString());
  }

  if (options.length > 0) {
    sendQuickReply(replyToken, '項目を選択してください', options);
  } else {
    replyLine(replyToken, '参照できる項目がありません。');
  }
}

function replyLineInfoIfMatched_(replyToken, userMessage) {
  const sheet = getOptionalSheet_(INFO_SHEET_NAME);
  if (!sheet || sheet.getLastRow() < 2) return false;

  const infoData = sheet.getRange(2, 1, sheet.getLastRow() - 1, 2).getValues();
  const message = normalizeText_(userMessage);
  const matchRow = infoData.find(row => normalizeText_(row[0]) === message);
  if (!matchRow) return false;

  const answer = matchRow[1] ? matchRow[1].toString() : '';
  replyLine(replyToken, answer || '表示できる内容が未入力です。');
  return true;
}

function saveLineMemoToSheet_(text) {
  const sheet = getOptionalSheet_(MEMO_SHEET_NAME);
  if (!sheet) throw new Error(MEMO_SHEET_NAME + ' シートが見つかりません。');

  const date = Utilities.formatDate(getTokyoNow_(), 'JST', 'yyyy/MM/dd HH:mm');
  const data = sheet.getRange('A2:A').getValues();
  let targetRow = 2;
  for (let i = 0; i < data.length; i++) {
    if (data[i][0] === '' || data[i][0] === null) { targetRow = i + 2; break; }
    if (i === data.length - 1) targetRow = data.length + 2;
  }
  sheet.getRange(targetRow, 1, 1, 2).setValues([[date, text]]);
}

function getOptionalSheet_(sheetName) {
  return SpreadsheetApp.openById(getSpreadsheetId_()).getSheetByName(sheetName);
}

function normalizeText_(value) {
  return String(value || '').trim();
}

// =====================================================
// LIFF フォーム HTML 生成
// =====================================================
function buildFormHtml(categories, gasUrl) {
  const catJson = JSON.stringify(categories);
  const currentMonth = getTokyoNow_().getMonth() + 1;

  return `<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<script charset="utf-8" src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Hiragino Sans', 'Yu Gothic UI', sans-serif; background: #f0f2f5; min-height: 100vh; }
.header { background: #00B900; color: white; padding: 14px 16px; font-size: 17px; font-weight: bold; text-align: center; letter-spacing: 0.5px; position: sticky; top: 0; z-index: 10; }
.form-wrap { padding: 14px 14px 100px; max-width: 520px; margin: 0 auto; }
.card { background: white; border-radius: 14px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.09); }
.label { font-size: 11px; color: #999; font-weight: bold; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 10px; }
.month-nav { display: flex; align-items: center; justify-content: space-between; }
.month-arrow { width: 40px; height: 40px; border: none; background: #f0f2f5; border-radius: 50%; font-size: 20px; color: #00B900; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.month-arrow:active { background: #e0f5e0; }
.month-display { font-size: 26px; font-weight: bold; color: #222; }
select { width: 100%; padding: 13px 12px; font-size: 16px; border: 1.5px solid #e8e8e8; border-radius: 10px; background: #fafafa; appearance: none; -webkit-appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%23999' stroke-width='1.5' fill='none'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 14px center; }
select:focus { border-color: #00B900; outline: none; background-color: #fff; }
input[type=text], input[type=number] { width: 100%; padding: 13px 12px; font-size: 16px; border: 1.5px solid #e8e8e8; border-radius: 10px; background: #fafafa; }
input:focus { border-color: #00B900; outline: none; background: #fff; }
.payment-row { display: flex; gap: 10px; }
.pay-btn { flex: 1; padding: 13px 8px; border: 2px solid #e8e8e8; border-radius: 10px; background: #fafafa; font-size: 15px; cursor: pointer; text-align: center; transition: all 0.15s; color: #555; }
.pay-btn.active { border-color: #00B900; background: #e8f5e9; color: #00B900; font-weight: bold; }
.pay-btn:active { opacity: 0.7; }
.footer-bar { position: fixed; bottom: 0; left: 0; right: 0; padding: 12px 16px; padding-bottom: calc(12px + env(safe-area-inset-bottom)); background: white; border-top: 1px solid #eee; }
.submit-btn { width: 100%; padding: 15px; background: #00B900; color: white; border: none; border-radius: 12px; font-size: 17px; font-weight: bold; cursor: pointer; letter-spacing: 0.5px; }
.submit-btn:disabled { background: #bbb; }
.submit-btn:active { background: #009900; }
#successView { display: none; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh; padding: 40px 20px; }
.success-icon { font-size: 72px; margin-bottom: 20px; }
.success-text { font-size: 22px; font-weight: bold; color: #222; margin-bottom: 8px; }
.success-sub { font-size: 14px; color: #888; }
</style>
</head>
<body>
<div class="header">📒 家計簿入力</div>
<div class="form-wrap" id="mainForm">
  <div class="card">
    <div class="label">月</div>
    <div class="month-nav">
      <button class="month-arrow" onclick="changeMonth(-1)">‹</button>
      <div class="month-display" id="monthDisplay">${currentMonth}月</div>
      <button class="month-arrow" onclick="changeMonth(1)">›</button>
    </div>
  </div>
  <div class="card">
    <div class="label">項目</div>
    <select id="category" onchange="onCategoryChange()">
      <option value="">選択してください</option>
      ${categories.map(c => `<option value="${c.name}" data-needs-payment="${c.needsPayment}">${c.name}</option>`).join('\n      ')}
    </select>
  </div>
  <div class="card" id="paymentCard" style="display:none">
    <div class="label">支払方法</div>
    <div class="payment-row">
      <div class="pay-btn" id="btn-cash" onclick="selectPayment('キャッシュ')">💴 現金</div>
      <div class="pay-btn" id="btn-card" onclick="selectPayment('カード')">💳 カード</div>
    </div>
  </div>
  <div class="card">
    <div class="label">内容</div>
    <input type="text" id="content" placeholder="例：外食、スーパーなど" autocomplete="off">
  </div>
  <div class="card">
    <div class="label">金額（円）</div>
    <input type="number" id="amount" placeholder="0" inputmode="numeric" pattern="[0-9]*">
  </div>
</div>
<div id="successView">
  <div class="success-icon">✅</div>
  <div class="success-text">登録しました！</div>
  <div class="success-sub">画面が閉じます</div>
</div>
<div class="footer-bar" id="footerBar">
  <button class="submit-btn" id="submitBtn" onclick="submitForm()">登録する</button>
</div>
<script>
const CATEGORIES = ${catJson};
const GAS_URL = '${gasUrl}';
let currentMonth = ${currentMonth};
let selectedPayment = '';
liff.init({ liffId: '${LIFF_ID}' }).catch(err => console.warn('LIFF init error:', err));
function changeMonth(delta) {
  currentMonth = Math.min(12, Math.max(1, currentMonth + delta));
  document.getElementById('monthDisplay').textContent = currentMonth + '月';
}
function onCategoryChange() {
  const sel = document.getElementById('category');
  const opt = sel.options[sel.selectedIndex];
  const needsPayment = opt && opt.dataset.needsPayment === 'true';
  document.getElementById('paymentCard').style.display = needsPayment ? 'block' : 'none';
  selectedPayment = '';
  document.getElementById('btn-cash').classList.remove('active');
  document.getElementById('btn-card').classList.remove('active');
}
function selectPayment(type) {
  selectedPayment = type;
  document.getElementById('btn-cash').classList.toggle('active', type === 'キャッシュ');
  document.getElementById('btn-card').classList.toggle('active', type === 'カード');
}
async function submitForm() {
  const category = document.getElementById('category').value;
  const content = document.getElementById('content').value.trim();
  const amount = document.getElementById('amount').value;
  const needsPayment = document.getElementById('paymentCard').style.display !== 'none';
  if (!category) { alert('項目を選択してください'); return; }
  if (!content) { alert('内容を入力してください'); return; }
  if (amount === '' || isNaN(Number(amount)) || Number(amount) < 0) { alert('金額を入力してください'); return; }
  if (needsPayment && !selectedPayment) { alert('支払方法を選択してください'); return; }
  const btn = document.getElementById('submitBtn');
  btn.disabled = true;
  btn.textContent = '送信中...';
  try {
    await fetch(GAS_URL, {
      method: 'POST',
      mode: 'no-cors',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source: 'liff', month: currentMonth + '月', category, content, amount: Number(amount), paymentMethod: selectedPayment })
    });
  } catch (err) {
    alert('通信エラーが発生しました。再度お試しください。');
    btn.disabled = false;
    btn.textContent = '登録する';
    return;
  }
  const lines = ['✅ 家計簿登録完了', '月：' + currentMonth + '月', '項目：' + category, '内容：' + content, '金額：' + Number(amount).toLocaleString() + '円'];
  if (selectedPayment) lines.push('支払：' + selectedPayment);
  if (liff.isInClient()) {
    try { await liff.sendMessages([{ type: 'text', text: lines.join('\\n') }]); } catch (e) { console.warn('sendMessages error:', e); }
  }
  document.getElementById('mainForm').style.display = 'none';
  document.getElementById('footerBar').style.display = 'none';
  document.getElementById('successView').style.display = 'flex';
  setTimeout(() => { if (liff.isInClient()) liff.closeWindow(); }, 1800);
}
</script>
</body>
</html>`;
}

// =====================================================
// 家計消化状況
// 集計シートのC/D列の月固定数式には依存せず、家計簿シートから当月実績を直接集計する。
// =====================================================
function sendBudgetReport(replyToken) {
  try {
    const ss = SpreadsheetApp.openById(getSpreadsheetId_());
    const summarySheet = ss.getSheetByName(SUMMARY_SHEET_NAME);
    const kakeiboSheet = ss.getSheetByName('家計簿');
    if (!summarySheet) { replyLine(replyToken, '集計シートが見つかりません。'); return; }
    if (!kakeiboSheet) { replyLine(replyToken, '家計簿シートが見つかりません。'); return; }

    const now = getTokyoNow_();
    const month = now.getMonth() + 1;
    const monthLabel = month + '月';
    const today = now.getDate();
    const daysInMonth = new Date(now.getFullYear(), month, 0).getDate();

    const budgetRows = readBudgetRows_(summarySheet);
    if (budgetRows.length === 0) {
      replyLine(replyToken, '❌ 集計シートに表示対象の項目が見つかりません。');
      return;
    }

    const spendingByCategory = readMonthlySpendingByCategory_(kakeiboSheet, now);
    const rows = budgetRows.map(row => {
      const spent = spendingByCategory[row.name] || 0;
      const remaining = row.budget - spent;
      const pctVal = row.isFixed ? '-' : (row.budget > 0 ? spent / row.budget : 0);
      return { name: row.name, budget: row.budget, diff: remaining, pctVal: pctVal };
    });

    const flexMsg = {
      type: 'flex',
      altText: monthLabel + 'の家計消化状況',
      contents: {
        type: 'bubble',
        body: {
          type: 'box',
          layout: 'vertical',
          paddingAll: 'md',
          contents: [
            { type: 'text', text: monthLabel + 'の家計　' + today + '/' + daysInMonth + '日時点', weight: 'bold', size: 'sm' },
            { type: 'separator', margin: 'sm' },
            ...rows.map(r => makeBudgetRow(r.name, r.budget, r.diff, r.pctVal)),
            { type: 'text', text: today + '/' + daysInMonth + '日経過', size: 'xxs', color: '#AAAAAA', margin: 'md', align: 'end' }
          ]
        }
      }
    };

    replyLineRaw(replyToken, flexMsg);
  } catch (err) {
    replyLine(replyToken, '❌ エラー: ' + err.message);
  }
}

function readBudgetRows_(summarySheet) {
  const data = summarySheet.getRange('A1:D35').getValues();
  const headerIdx = data.findIndex(r => r[0].toString().trim() === '項目');
  if (headerIdx === -1) {
    return [];
  }

  const rows = [];
  for (let i = headerIdx + 1; i < data.length; i++) {
    const name = data[i][0];
    if (!name) break;
    const nameText = normalizeCategoryName_(name);
    if (nameText.startsWith('経費')) continue;
    rows.push({
      name: nameText,
      budget: Number(data[i][1]) || 0,
      isFixed: data[i][3].toString().trim() === '-'
    });
  }
  return rows;
}

function readMonthlySpendingByCategory_(kakeiboSheet, targetDate) {
  const lastRow = kakeiboSheet.getLastRow();
  if (lastRow < 4) return {};

  const targetYear = targetDate.getFullYear();
  const targetMonth = targetDate.getMonth() + 1;
  const values = kakeiboSheet.getRange(4, 2, lastRow - 3, 4).getValues();
  const spending = {};
  for (let i = 0; i < values.length; i++) {
    const rowMonth = values[i][0];
    const category = values[i][1];
    const amount = Number(values[i][3]) || 0;
    if (!rowMonth || !category) continue;
    if (!isSameMonthValue_(rowMonth, targetYear, targetMonth)) continue;
    const key = normalizeCategoryName_(category);
    spending[key] = (spending[key] || 0) + amount;
  }
  return spending;
}

function isSameMonthValue_(value, targetYear, targetMonth) {
  if (value instanceof Date) {
    return value.getFullYear() === targetYear && (value.getMonth() + 1) === targetMonth;
  }

  if (typeof value === 'number') {
    return value === targetMonth;
  }

  const text = toHalfWidthNumber_(String(value || '').trim());
  if (!text) return false;

  const yearMonth = text.match(/(20\d{2})\D+(\d{1,2})/);
  if (yearMonth) {
    return Number(yearMonth[1]) === targetYear && Number(yearMonth[2]) === targetMonth;
  }

  const monthOnly = text.match(/^(\d{1,2})\s*月?$/);
  if (monthOnly) {
    return Number(monthOnly[1]) === targetMonth;
  }

  return text === targetMonth + '月';
}

function normalizeCategoryName_(value) {
  return String(value || '').trim();
}

function toHalfWidthNumber_(text) {
  return text.replace(/[０-９]/g, ch => String.fromCharCode(ch.charCodeAt(0) - 0xFEE0));
}

function makeBudgetRow(name, budget, remaining, pctVal) {
  let pct = 0;
  const isFixed = (typeof pctVal === 'string' && pctVal.toString().trim() === '-');
  if (!isFixed) {
    if (typeof pctVal === 'number') { pct = Math.round(pctVal * 100); }
    else if (typeof pctVal === 'string') { const m = pctVal.match(/\d+/); pct = m ? parseInt(m[0]) : 0; }
  }
  pct = Math.min(pct, 100);

  const isOver = remaining < 0;
  const color = (isOver || pct >= 100) ? '#E53935' : pct >= 60 ? '#FF9800' : '#43A047';
  const fmt = n => Math.round(Math.abs(n)).toString().replace(/\B(?=(\d{3})+\b)/g, ',');
  const budgetText = (budget && budget !== 0) ? '（予算 ' + fmt(budget) + '円）' : '';
  const remainText = isFixed ? '固定費（毎月）' + budgetText
    : isOver ? '超過 ' + fmt(remaining) + '円' + budgetText
    : '残 ' + fmt(remaining) + '円' + budgetText;

  const barContents = (pct > 0)
    ? [{ type: 'box', layout: 'horizontal', backgroundColor: color, width: pct + '%', height: '8px', contents: [{ type: 'filler' }] }, { type: 'filler' }]
    : [{ type: 'filler' }];

  return {
    type: 'box',
    layout: 'vertical',
    margin: 'sm',
    contents: [
      {
        type: 'box',
        layout: 'horizontal',
        contents: [
          { type: 'text', text: name, size: 'xs', color: '#333333', flex: 4 },
          { type: 'text', text: isFixed ? '固定' : pct + '%', size: 'xs', color: '#888888', align: 'end', flex: 1 }
        ]
      },
      { type: 'box', layout: 'horizontal', backgroundColor: '#E0E0E0', height: '8px', cornerRadius: '4px', margin: 'xs', contents: barContents },
      { type: 'text', text: remainText, size: 'xs', color: color, margin: 'xs' }
    ]
  };
}

// =====================================================
// 家計簿ステップ処理（フォールバック用）
// =====================================================
function handleKakeiboStep(token, msg, userId, cache, step) {
  const ss = SpreadsheetApp.openById(getSpreadsheetId_());
  const sheet = ss.getSheetByName('家計簿');

  switch (step) {
    case 'month':
      cache.put(userId + '_month', msg);
      cache.put(userId + '_step', 'category');
      const gHValues = sheet.getRange('G4:H').getValues();
      const categories = [];
      for (let i = 0; i < gHValues.length; i++) {
        if (gHValues[i][0] === '' || gHValues[i][0] === null) break;
        categories.push(gHValues[i][0].toString());
      }
      sendQuickReply(token, '【2/4】項目を選択：', categories);
      break;

    case 'category':
      cache.put(userId + '_category', msg);
      const list = sheet.getRange('G4:H' + sheet.getLastRow()).getValues();
      const selected = list.find(row => row[0].toString() === msg);
      if (selected && categoryNeedsPayment_(msg, selected[1])) {
        cache.put(userId + '_step', 'payment_method');
        sendQuickReply(token, '支払方法を選んでください。', ['キャッシュ', 'カード']);
      } else {
        cache.put(userId + '_step', 'content');
        replyLine(token, '【3/4】内容を入力：');
      }
      break;

    case 'payment_method':
      cache.put(userId + '_payment_method', msg);
      cache.put(userId + '_step', 'content');
      replyLine(token, '【3/4】内容を入力：');
      break;

    case 'content':
      cache.put(userId + '_content', msg);
      cache.put(userId + '_step', 'amount');
      replyLine(token, '【4/4】金額を入力（数字）：');
      break;

    case 'amount':
      const amount = msg.replace(/[^0-9]/g, '');
      cache.put(userId + '_amount', amount);
      cache.put(userId + '_step', 'confirm');
      const confirmMsg = `【確認】\n月:${cache.get(userId + '_month')}\n項:${cache.get(userId + '_category')}\n内:${cache.get(userId + '_content')}\n金:${amount}円\n登録しますか？`;
      sendQuickReply(token, confirmMsg, ['Yes', 'No']);
      break;

    case 'confirm':
      if (msg === 'Yes') {
        const month = cache.get(userId + '_month');
        const category = cache.get(userId + '_category');
        const content = cache.get(userId + '_content');
        const confirmAmount = cache.get(userId + '_amount');
        const payMethod = cache.get(userId + '_payment_method');
        saveToKakeiboSheet(month, category, content, confirmAmount);
        if (payMethod === 'キャッシュ') saveToExpenseSheet(month, confirmAmount, content);
        replyLine(token, '✅ 登録が完了しました。');
      } else {
        replyLine(token, '❌ キャンセルしました。');
      }
      cache.removeAll([userId + '_step', userId + '_month', userId + '_category', userId + '_content', userId + '_amount', userId + '_payment_method']);
      break;
  }
}

// =====================================================
// スプレッドシート書き込み
// =====================================================
function saveToKakeiboSheet(month, category, content, amount) {
  const sheet = SpreadsheetApp.openById(getSpreadsheetId_()).getSheetByName('家計簿');
  const date = Utilities.formatDate(getTokyoNow_(), 'JST', 'yyyy/MM/dd HH:mm');
  const colAValues = sheet.getRange('A4:A').getValues();
  let row = 4;
  for (let i = 0; i < colAValues.length; i++) {
    if (colAValues[i][0] === '') { row = i + 4; break; }
    if (i === colAValues.length - 1) row = colAValues.length + 4;
  }
  sheet.getRange(row, 1, 1, 5).setValues([[date, month, category, content, Number(amount)]]);
}

function saveToExpenseSheet(month, amount, content) {
  const ss = SpreadsheetApp.openById(getExpenseSpreadsheetId_());
  const sheet = ss.getSheetByName('経費報告');
  const date = Utilities.formatDate(getTokyoNow_(), 'JST', 'yyyy/MM/dd HH:mm');
  const data = sheet.getRange('A2:C').getValues();
  let targetRow = 2;
  for (let i = 0; i < data.length; i++) {
    if (data[i][0] === '' && data[i][1] === '' && data[i][2] === '') { targetRow = i + 2; break; }
    if (i === data.length - 1) targetRow = data.length + 2;
  }
  sheet.getRange(targetRow, 1, 1, 4).setValues([[date, month, Number(amount), content]]);
}

// =====================================================
// LINE 送信ヘルパー
// =====================================================
function sendQuickReply(token, text, options) {
  const items = options.slice(0, 13).map(opt => ({
    type: 'action',
    action: {
      type: 'message',
      label: opt.length > 20 ? opt.slice(0, 17) + '...' : opt,
      text: opt
    }
  }));
  replyLineRaw(token, { type: 'text', text: text, quickReply: { items: items } });
}

function replyLine(token, text) {
  replyLineRaw(token, { type: 'text', text: text });
}

function replyLineRaw(token, messageObject) {
  const res = UrlFetchApp.fetch('https://api.line.me/v2/bot/message/reply', {
    method: 'post',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + getChannelAccessToken_()
    },
    payload: JSON.stringify({ replyToken: token, messages: [messageObject] }),
    muteHttpExceptions: true
  });
  console.log('LINE API status:', res.getResponseCode(), res.getContentText());
}
