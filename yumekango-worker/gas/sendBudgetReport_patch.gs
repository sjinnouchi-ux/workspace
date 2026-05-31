// =====================================================
// 家計消化状況 差し替え用
// 既存コードでは、下記3関数を追加・差し替えしてください。
// - sendBudgetReport: 既存関数を丸ごと置換
// - readBudgetRows_: 新規追加
// - readMonthlySpendingByCategory_: 新規追加
//
// makeBudgetRow(), replyLine(), replyLineRaw(), SPREADSHEET_ID,
// SUMMARY_SHEET_NAME は既存コードのものをそのまま使います。
// =====================================================
function sendBudgetReport(replyToken) {
  try {
    const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    const summarySheet = ss.getSheetByName(SUMMARY_SHEET_NAME);
    const kakeiboSheet = ss.getSheetByName('家計簿');
    if (!summarySheet) { replyLine(replyToken, '集計シートが見つかりません。'); return; }
    if (!kakeiboSheet) { replyLine(replyToken, '家計簿シートが見つかりません。'); return; }

    const now = new Date();
    const month = now.getMonth() + 1;
    const monthLabel = month + '月';
    const today = now.getDate();
    const daysInMonth = new Date(now.getFullYear(), month, 0).getDate();

    const budgetRows = readBudgetRows_(summarySheet);
    if (budgetRows.length === 0) {
      replyLine(replyToken, '❌ 集計シートに表示対象の項目が見つかりません。');
      return;
    }

    const spendingByCategory = readMonthlySpendingByCategory_(kakeiboSheet, monthLabel);
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
  if (headerIdx === -1) return [];

  const rows = [];
  for (let i = headerIdx + 1; i < data.length; i++) {
    const name = data[i][0];
    if (!name) break;
    const nameText = name.toString();
    if (nameText.startsWith('経費')) continue;
    rows.push({
      name: nameText,
      budget: Number(data[i][1]) || 0,
      isFixed: data[i][3].toString().trim() === '-'
    });
  }
  return rows;
}

function readMonthlySpendingByCategory_(kakeiboSheet, monthLabel) {
  const lastRow = kakeiboSheet.getLastRow();
  if (lastRow < 4) return {};

  const values = kakeiboSheet.getRange(4, 2, lastRow - 3, 4).getValues();
  const spending = {};
  for (let i = 0; i < values.length; i++) {
    const rowMonth = values[i][0];
    const category = values[i][1];
    const amount = Number(values[i][3]) || 0;
    if (!rowMonth || !category) continue;
    if (rowMonth.toString().trim() !== monthLabel) continue;
    const key = category.toString();
    spending[key] = (spending[key] || 0) + amount;
  }
  return spending;
}
