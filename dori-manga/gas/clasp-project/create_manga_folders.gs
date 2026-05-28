/**
 * どり漫画管理シート - フォルダ一括作成 & URL挿入
 *
 * 【実行方法】
 *   1. Google スプレッドシートを開く
 *   2. 拡張機能 → Apps Script
 *   3. このコードを貼り付け
 *   4. 「run」関数を選択して ▶ 実行
 *   5. 初回のみ Drive / Sheets の権限許可が必要
 *
 * 【処理内容】
 *   どり漫画管理シートで B列にタイトルがあり R列が空白の行に対して
 *   指定の親フォルダ内に同名フォルダを作成し、URL を R列に挿入する
 *
 * 【対象スプレッドシート】
 *   https://docs.google.com/spreadsheets/d/1TYbBLOi6tjeOuEyXbNO8vh0tGq_Z2R9oSELv8OebHcw/edit
 *
 * 【親フォルダ】
 *   https://drive.google.com/drive/folders/1ORTTI5--9o9lmdUbLciKJ6FwbulKofo8
 */

function run() {
  const SPREADSHEET_ID  = '1TYbBLOi6tjeOuEyXbNO8vh0tGq_Z2R9oSELv8OebHcw';
  const SHEET_NAME      = 'どり漫画管理';
  const PARENT_FOLDER_ID = '1ORTTI5--9o9lmdUbLciKJ6FwbulKofo8';

  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = ss.getSheetByName(SHEET_NAME);

  if (!sheet) {
    Logger.log('エラー: シートが見つかりません → ' + SHEET_NAME);
    return;
  }

  const lastRow = sheet.getLastRow();
  Logger.log('最終行: ' + lastRow);

  // B列（タイトル）と R列（画像格納フォルダ）を一括取得（2行目〜最終行）
  const colB = sheet.getRange(2, 2,  lastRow - 1, 1).getValues();  // B列
  const colR = sheet.getRange(2, 18, lastRow - 1, 1).getValues();  // R列

  const parentFolder = DriveApp.getFolderById(PARENT_FOLDER_ID);

  let createdCount = 0;
  let skippedCount = 0;
  let errorCount   = 0;

  for (let i = 0; i < colB.length; i++) {
    const title     = String(colB[i][0]).trim();
    const folderUrl = String(colR[i][0]).trim();
    const rowNum    = i + 2;

    // B列にタイトルあり & R列が空白 → フォルダ作成
    if (title && !folderUrl) {
      try {
        const newFolder    = parentFolder.createFolder(title);
        const newFolderUrl = 'https://drive.google.com/drive/folders/'
                             + newFolder.getId()
                             + '?usp=drive_link';

        sheet.getRange(rowNum, 18).setValue(newFolderUrl);

        Logger.log('[作成] 行' + rowNum + ': ' + title + ' → ' + newFolderUrl);
        createdCount++;

        // 10件ごとに書き込みをフラッシュ（途中保存）
        if (createdCount % 10 === 0) {
          SpreadsheetApp.flush();
          Utilities.sleep(300);   // API レート制限対策（0.3秒）
        }

      } catch (e) {
        Logger.log('[エラー] 行' + rowNum + ': ' + title + ' → ' + e.message);
        errorCount++;
      }

    } else if (title && folderUrl) {
      // 既にURLあり → スキップ
      Logger.log('[スキップ] 行' + rowNum + ': ' + title);
      skippedCount++;
    }
  }

  // 最終フラッシュ
  SpreadsheetApp.flush();

  Logger.log('');
  Logger.log('===== 完了 =====');
  Logger.log('作成済み : ' + createdCount + ' 件');
  Logger.log('スキップ : ' + skippedCount + ' 件（既存URLあり）');
  Logger.log('エラー   : ' + errorCount   + ' 件');
}
