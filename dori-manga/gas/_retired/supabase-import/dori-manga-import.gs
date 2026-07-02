// ============================================================
// どり看護師漫画 — Supabase DB 自動インポート GAS
// ============================================================
// 【スプレッドシート「画像格納」シートのセル構成】
//   B2 : 画像ファイルの Google Drive 共有URL
//   B4 : panel_number(コマ番号)
//   B5 : OK フォルダURL
//   B6 : NG フォルダURL
//   B7 : CLOSE フォルダURL
//   B8 : OK / NG / CLOSE(ドロップダウン)
//   B9 : ChatGPT が出力した DB登録用 JSON
//
// 【初回設定】
//   拡張機能 → Apps Script →「プロジェクトの設定」
//   →「スクリプトプロパティ」に以下を追加:
//     SUPABASE_URL          : https://vdntqwtywxyjxelycavx.supabase.co
//     SUPABASE_SERVICE_ROLE_KEY : (Supabase > Settings > API > service_role key)
// ============================================================

const SHEET_NAME = '画像格納';

// ------------------------------------------------------------
// カスタムメニュー(スプレッドシートを開いたとき自動追加)
// ------------------------------------------------------------
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🩺 どり漫画DB')
    .addItem('▶ DBにインポート実行', 'importToDatabase')
    .addSeparator()
    .addItem('🔁 Supabase更新を今すぐ実行', 'runSupabaseKeepaliveFromMenu')
    .addItem('⏱️ 3日ごとのSupabase更新を設定', 'installSupabaseKeepaliveTrigger')
    .addItem('🛑 Supabase定期更新を停止', 'deleteSupabaseKeepaliveTriggers')
    .addSeparator()
    .addItem('⚙️ 初期設定の確認', 'showSetupInstructions')
    .addToUi();
}

// ------------------------------------------------------------
// メイン処理:インポート実行
// ------------------------------------------------------------
function importToDatabase() {
  const ss    = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(SHEET_NAME);
  const ui    = SpreadsheetApp.getUi();

  if (!sheet) {
    ui.alert('❌ エラー', `「${SHEET_NAME}」シートが見つかりません。`, ui.ButtonSet.OK);
    return;
  }

  // ── セル読み取り ──────────────────────────────────────────
  const imageUrl       = sheet.getRange('B2').getValue().toString().trim();
  const panelNumber    = sheet.getRange('B4').getValue();
  const okFolderUrl    = sheet.getRange('B5').getValue().toString().trim();
  const ngFolderUrl    = sheet.getRange('B6').getValue().toString().trim();
  const closeFolderUrl = sheet.getRange('B7').getValue().toString().trim();
  const resultStatus   = sheet.getRange('B8').getValue().toString().trim();
  const jsonText       = sheet.getRange('B9').getValue().toString().trim();

  // ── スクリプトプロパティ チェック(最優先)──────────────
  const props          = PropertiesService.getScriptProperties();
  const supabaseUrl    = props.getProperty('SUPABASE_URL');
  const serviceRoleKey = props.getProperty('SUPABASE_SERVICE_ROLE_KEY');
  if (!supabaseUrl || !serviceRoleKey) {
    ui.alert('⚙️ 初期設定が未完了',
      'スクリプトプロパティが設定されていません。\n\n' +
      '【設定手順】\n' +
      '拡張機能 → Apps Script\n' +
      '→ 左メニュー「プロジェクトの設定」\n' +
      '→「スクリプトプロパティを追加」\n\n' +
      '追加するプロパティ:\n' +
      '1 SUPABASE_URL\n' +
      '   https://vdntqwtywxyjxelycavx.supabase.co\n\n' +
      '2 SUPABASE_SERVICE_ROLE_KEY\n' +
      '   Supabase > Settings > API\n' +
      '   > service_role (secret) の値',
      ui.ButtonSet.OK);
    return;
  }

  // ── 基本入力チェック ─────────────────────────────────────
  if (!imageUrl) {
    ui.alert('⚠️ 入力不足', 'B2に画像URLが入力されていません。', ui.ButtonSet.OK);
    return;
  }
  if (!['OK', 'NG', 'CLOSE'].includes(resultStatus)) {
    ui.alert('⚠️ 入力エラー', `B8の値「${resultStatus}」は無効です。OK / NG / CLOSE のいずれかを選択してください。`, ui.ButtonSet.OK);
    return;
  }
  if (!jsonText) {
    ui.alert('⚠️ 入力不足', 'B9にJSONが入力されていません。', ui.ButtonSet.OK);
    return;
  }

  // ── JSON パース ──────────────────────────────────────────
  let data;
  try {
    data = JSON.parse(jsonText);
  } catch (e) {
    ui.alert('⚠️ JSON形式エラー',
      'B9のJSONを解析できませんでした。\n\n' +
      '【エラー内容】\n' + e.message + '\n\n' +
      '【よくある原因】\n' +
      '・ダブルクォートが正しく閉じていない\n' +
      '・末尾や途中に余分なカンマがある\n' +
      '・波括弧 { } や角括弧 [ ] のバランスが崩れている',
      ui.ButtonSet.OK);
    return;
  }

  // ── JSON 必須フィールドチェック ──────────────────────────
  const REQUIRED = [
    'attempt_number',
    'result_status',
    'final_generation_prompt',
    'evaluation_summary',
    'evaluation_json'
  ];
  const missing = REQUIRED.filter(f => data[f] === undefined || data[f] === null || data[f] === '');
  if (missing.length > 0) {
    ui.alert('⚠️ JSONフィールド不足',
      '以下の必須フィールドがJSONに不足しています:\n\n' +
      missing.map(f => '  ・' + f).join('\n') + '\n\n' +
      '【必須フィールド一覧】\n' +
      REQUIRED.map(f => '  ' + f).join('\n'),
      ui.ButtonSet.OK);
    return;
  }

  // evaluation_json の型チェック
  if (typeof data.evaluation_json !== 'object' || Array.isArray(data.evaluation_json)) {
    ui.alert('⚠️ JSONフィールドエラー',
      'evaluation_json フィールドがオブジェクト形式ではありません。\n\n' +
      '正しい形式の例:\n' +
      '"evaluation_json": {\n' +
      '  "result": "NG",\n' +
      '  "image_features": [...],\n' +
      '  ...\n' +
      '}',
      ui.ButtonSet.OK);
    return;
  }

  // B8 と JSON の result_status 不一致チェック
  if (data.result_status !== resultStatus) {
    const resp = ui.alert('⚠️ 判定不一致',
      `B8 の判定:${resultStatus}\n` +
      `JSON の result_status:${data.result_status}\n\n` +
      `値が一致しません。B8の値(${resultStatus})で続行しますか?`,
      ui.ButtonSet.YES_NO);
    if (resp !== ui.Button.YES) return;
    data.result_status = resultStatus;
  }

  // ── 確認ダイアログ ────────────────────────────────────────
  const confirmMsg = buildConfirmMessage(data, resultStatus, panelNumber);
  const confirm = ui.alert('✅ インポート内容の確認', confirmMsg, ui.ButtonSet.YES_NO);
  if (confirm !== ui.Button.YES) {
    ui.alert('キャンセル', '操作をキャンセルしました。', ui.ButtonSet.OK);
    return;
  }

  // ── 実行フェーズ ──────────────────────────────────────────
  try {

    // STEP 1: ファイル取得(フォルダURL・ファイルURL 両対応)
    let file, fileId, fileName;
    const srcFolderId  = extractFolderId(imageUrl);
    const directFileId = extractFileId(imageUrl);

    if (srcFolderId) {
      const srcFolder = DriveApp.getFolderById(srcFolderId);
      const files = srcFolder.getFiles();
      if (!files.hasNext()) {
        throw new Error(
          'B2のフォルダにファイルが見つかりません。\n\n' +
          'Driveフォルダに画像が1枚入っているか確認してください。\n' +
          'フォルダURL: ' + imageUrl
        );
      }
      file     = files.next();
      fileId   = file.getId();
      fileName = file.getName();
    } else if (directFileId) {
      fileId   = directFileId;
      file     = DriveApp.getFileById(fileId);
      fileName = file.getName();
    } else {
      throw new Error(
        'B2のURLからGoogle DriveのファイルまたはフォルダIDを取得できませんでした。\n\n' +
        '【対応URLの形式】\n' +
        '・フォルダ: https://drive.google.com/drive/folders/フォルダID\n' +
        '・ファイル: https://drive.google.com/file/d/ファイルID/view\n\n' +
        '現在のURL: ' + imageUrl
      );
    }

    // STEP 2: 移動先フォルダ確認(移動はDB書き込み後)
    const destFolderUrl = resultStatus === 'OK'    ? okFolderUrl
                        : resultStatus === 'NG'    ? ngFolderUrl
                        : resultStatus === 'CLOSE' ? closeFolderUrl
                        : null;
    if (!destFolderUrl) {
      throw new Error(`${resultStatus} フォルダのURLが設定されていません。B5〜B7を確認してください。`);
    }
    const destFolderId = extractFolderId(destFolderUrl);
    if (!destFolderId) {
      throw new Error(`フォルダURLからIDを取得できませんでした。\nURL: ${destFolderUrl}`);
    }

    // STEP 3: panel_id を Supabase から取得(なければ自動作成)
    const pNum    = data.panel_number || panelNumber;
    const panelId = getPanelId(pNum, data.episode_title);

    // STEP 4: generation_attempts に INSERT
    const row = {
      panel_id:                panelId,
      attempt_number:          data.attempt_number,
      image_url:               imageUrl,
      drive_file_id:           fileId,
      file_name:               data.file_name || fileName,
      folder_status:           resultStatus,
      result_status:           resultStatus,
      final_generation_prompt: data.final_generation_prompt,
      evaluation_summary:      data.evaluation_summary,
      evaluation_json:         data.evaluation_json
    };
    const inserted   = insertToSupabase('generation_attempts', row);
    const insertedId = inserted && inserted[0] ? inserted[0].id : null;

    // STEP 5: prompt_lessons に INSERT(あれば)
    let lessonCount = 0;
    if (Array.isArray(data.prompt_lesson_candidates) && data.prompt_lesson_candidates.length > 0) {
      data.prompt_lesson_candidates.forEach(lesson => {
        const lessonText = normalizeLessonText(lesson);

        if (lessonText && lessonText.trim()) {
          insertToSupabase('prompt_lessons', {
            source_attempt_id: insertedId || null,
            lesson_text:       lessonText.trim(),
            is_active:         true
          });
          lessonCount++;
        }
      });
    }

    // STEP 6: DB書き込み完了後に Google Drive ファイル移動
    const destFolder = DriveApp.getFolderById(destFolderId);
    file.moveTo(destFolder);

    // STEP 7: 完了通知
    ui.alert('🎉 インポート完了!',
      '処理が正常に完了しました。\n\n' +
      `🗄️ generation_attempts に1件登録\n` +
      (lessonCount > 0 ? `📝 prompt_lessons に ${lessonCount}件 登録\n` : '') +
      `📁 画像を ${resultStatus} フォルダへ移動\n\n` +
      '⚠️ B9のJSONはクリアしました(二重登録防止)',
      ui.ButtonSet.OK);

    // B9 をクリア(二重登録防止)
    sheet.getRange('B9').clearContent();

  } catch (e) {
    ui.alert('❌ 処理エラー',
      '処理中にエラーが発生しました。操作は中断されました。\n\n' +
      e.message,
      ui.ButtonSet.OK);
  }
}

// ------------------------------------------------------------
// prompt_lesson_candidates の型ブレを吸収して文字列化する
// ------------------------------------------------------------
function normalizeLessonText(lesson) {
  if (lesson === undefined || lesson === null) return '';

  if (typeof lesson === 'string') {
    return lesson;
  }

  if (typeof lesson === 'number' || typeof lesson === 'boolean') {
    return String(lesson);
  }

  if (typeof lesson === 'object') {
    if (lesson.lesson_text) return String(lesson.lesson_text);
    if (lesson.text) return String(lesson.text);
    if (lesson.rule) return String(lesson.rule);
    if (lesson.content) return String(lesson.content);
    return JSON.stringify(lesson);
  }

  return String(lesson);
}

// ------------------------------------------------------------
// 確認メッセージを組み立てる
// ------------------------------------------------------------
function buildConfirmMessage(data, resultStatus, panelNumber) {
  const ej         = data.evaluation_json || {};
  const goodPoints = (ej.good_points     || []).join('、') || 'なし';
  const ngReason   = ej.ng_reason        || 'なし';
  const nextHint   = ej.next_prompt_hint || 'なし';
  const lessons    = data.prompt_lesson_candidates || [];

  const lines = [
    '以下の内容でインポートします。よろしいですか?',
    '',
    '━━━━━━━━━━━━━━━━━━━━',
    `📋 エピソード   : ${data.episode_title || '未指定'}`,
    `🔢 コマ番号     : ${data.panel_number  || panelNumber}`,
    `🔄 試行回数     : ${data.attempt_number} 回目`,
    `🏷️  判定         : ${resultStatus}`,
    `📝 評価まとめ   : ${data.evaluation_summary}`,
    '',
    `✅ 良かった点   : ${goodPoints}`,
    `❌ NGの理由     : ${ngReason}`,
    `💡 次回ヒント   : ${nextHint.length > 60 ? nextHint.substring(0, 60) + '...' : nextHint}`,
  ];

  // ── final_generation_prompt を箇条書きで表示 ──────────────
  const prompt = (data.final_generation_prompt || '').trim();
  if (prompt) {
    lines.push('');
    lines.push('🖊️ 使用プロンプト:');
    prompt.split(',').forEach(part => {
      const p = part.trim();
      if (p) lines.push('  ・' + p);
    });
  }

  if (lessons.length > 0) {
    lines.push('');
    lines.push(`📚 改善ルール(${lessons.length}件):`);
    lessons.forEach(l => {
      const lessonText = normalizeLessonText(l);
      if (lessonText) {
        lines.push('  ・' + (lessonText.length > 50 ? lessonText.substring(0, 50) + '...' : lessonText));
      }
    });
  }

  lines.push('━━━━━━━━━━━━━━━━━━━━');
  return lines.join('\n');
}

// ------------------------------------------------------------
// Supabase REST API — テーブルに1行 INSERT
// ------------------------------------------------------------
function insertToSupabase(tableName, row) {
  const props          = PropertiesService.getScriptProperties();
  const supabaseUrl    = props.getProperty('SUPABASE_URL');
  const serviceRoleKey = props.getProperty('SUPABASE_SERVICE_ROLE_KEY');

  if (!supabaseUrl || !serviceRoleKey) {
    throw new Error(
      'スクリプトプロパティが未設定です。\n\n' +
      '拡張機能 → Apps Script →「プロジェクトの設定」\n' +
      '→「スクリプトプロパティ」に以下を追加してください:\n\n' +
      '  SUPABASE_URL\n  SUPABASE_SERVICE_ROLE_KEY'
    );
  }

  const options = {
    method:      'post',
    contentType: 'application/json',
    headers: {
      'apikey':        serviceRoleKey,
      'Authorization': 'Bearer ' + serviceRoleKey,
      'Prefer':        'return=representation'
    },
    payload:            JSON.stringify(row),
    muteHttpExceptions: true
  };

  const resp       = UrlFetchApp.fetch(`${supabaseUrl}/rest/v1/${tableName}`, options);
  const statusCode = resp.getResponseCode();
  const body       = resp.getContentText();

  if (statusCode < 200 || statusCode >= 300) {
    throw new Error(`Supabase エラー (HTTP ${statusCode})\n\n${tableName} への INSERT に失敗しました。\n\n${body}`);
  }

  return JSON.parse(body);
}

// ------------------------------------------------------------
// Supabase休眠防止:3日に1回、既存マスタ行へ軽いUPDATEを送る
// ------------------------------------------------------------
const KEEPALIVE_TRIGGER_FUNCTION = 'runSupabaseKeepalive';

function installSupabaseKeepaliveTrigger() {
  deleteSupabaseKeepaliveTriggers(false);

  ScriptApp.newTrigger(KEEPALIVE_TRIGGER_FUNCTION)
    .timeBased()
    .everyDays(3)
    .atHour(9)
    .create();

  SpreadsheetApp.getUi().alert(
    '⏱️ 設定完了',
    'Supabase休眠防止のため、3日に1回の更新トリガーを設定しました。\n\n' +
    '実行内容: prompt_templates または characters の既存1行へ is_active の軽いUPDATEを送信します。',
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}

function deleteSupabaseKeepaliveTriggers(showAlert) {
  const triggers = ScriptApp.getProjectTriggers();
  let deleted = 0;

  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === KEEPALIVE_TRIGGER_FUNCTION) {
      ScriptApp.deleteTrigger(trigger);
      deleted++;
    }
  });

  if (showAlert !== false) {
    SpreadsheetApp.getUi().alert(
      '🛑 停止完了',
      `Supabase定期更新トリガーを ${deleted} 件削除しました。`,
      SpreadsheetApp.getUi().ButtonSet.OK
    );
  }
}

function runSupabaseKeepaliveFromMenu() {
  try {
    const touched = touchSupabaseKeepalive_();
    SpreadsheetApp.getUi().alert(
      '✅ Supabase更新完了',
      `${touched.table} の既存行に軽いUPDATEを送信しました。\n\n対象ID: ${touched.id}`,
      SpreadsheetApp.getUi().ButtonSet.OK
    );
  } catch (e) {
    SpreadsheetApp.getUi().alert(
      '❌ Supabase更新エラー',
      'Supabase更新中にエラーが発生しました。\n\n' + e.message,
      SpreadsheetApp.getUi().ButtonSet.OK
    );
  }
}

function runSupabaseKeepalive() {
  const touched = touchSupabaseKeepalive_();
  Logger.log(`Supabase keepalive updated ${touched.table}: ${touched.id}`);
}

function touchSupabaseKeepalive_() {
  const targets = [
    { table: 'prompt_templates', select: 'id,is_active' },
    { table: 'characters', select: 'id,is_active' }
  ];

  for (const target of targets) {
    const rows = requestSupabase_(
      'get',
      `${target.table}?select=${encodeURIComponent(target.select)}&order=created_at.asc.nullslast&limit=1`
    );

    if (Array.isArray(rows) && rows.length > 0) {
      const row = rows[0];
      const activeValue = row.is_active !== false;

      requestSupabase_(
        'patch',
        `${target.table}?id=eq.${encodeURIComponent(row.id)}`,
        { is_active: activeValue },
        'return=minimal'
      );

      return { table: target.table, id: row.id };
    }
  }

  throw new Error('keepalive対象の既存行が見つかりません。prompt_templates または characters に1件以上登録してください。');
}

function requestSupabase_(method, path, payload, prefer) {
  const props          = PropertiesService.getScriptProperties();
  const supabaseUrl    = props.getProperty('SUPABASE_URL');
  const serviceRoleKey = props.getProperty('SUPABASE_SERVICE_ROLE_KEY');

  if (!supabaseUrl || !serviceRoleKey) {
    throw new Error(
      'スクリプトプロパティが未設定です。\n\n' +
      'SUPABASE_URL と SUPABASE_SERVICE_ROLE_KEY を設定してください。'
    );
  }

  const headers = {
    'apikey':        serviceRoleKey,
    'Authorization': 'Bearer ' + serviceRoleKey
  };
  if (prefer) headers['Prefer'] = prefer;

  const options = {
    method:             method,
    headers:            headers,
    muteHttpExceptions: true
  };
  if (payload !== undefined) {
    options.contentType = 'application/json';
    options.payload = JSON.stringify(payload);
  }

  const base = supabaseUrl.replace(/\/$/, '');
  const resp = UrlFetchApp.fetch(`${base}/rest/v1/${path}`, options);
  const statusCode = resp.getResponseCode();
  const body = resp.getContentText();

  if (statusCode < 200 || statusCode >= 300) {
    throw new Error(`Supabase エラー (HTTP ${statusCode})\n\n${body}`);
  }

  return body ? JSON.parse(body) : null;
}

// ------------------------------------------------------------
// panel_id を Supabase から取得(なければ episode/panel を自動作成)
// ------------------------------------------------------------
function getPanelId(panelNumber, episodeTitle) {
  const props          = PropertiesService.getScriptProperties();
  const supabaseUrl    = props.getProperty('SUPABASE_URL');
  const serviceRoleKey = props.getProperty('SUPABASE_SERVICE_ROLE_KEY');

  const fetchOpts = {
    headers: {
      'apikey':        serviceRoleKey,
      'Authorization': 'Bearer ' + serviceRoleKey
    },
    muteHttpExceptions: true
  };

  // ── 1. episode_id を取得または作成 ───────────────────────
  const title  = episodeTitle || '(未設定)';
  const epUrl  = `${supabaseUrl}/rest/v1/manga_episodes?title=eq.${encodeURIComponent(title)}&select=id&limit=1`;
  const epResp = UrlFetchApp.fetch(epUrl, fetchOpts);
  const eps    = JSON.parse(epResp.getContentText());

  let episodeId;
  if (Array.isArray(eps) && eps.length > 0) {
    episodeId = eps[0].id;
  } else {
    const newEp = insertToSupabase('manga_episodes', { title: title, status: 'draft' });
    if (!Array.isArray(newEp) || !newEp[0]) {
      throw new Error(`manga_episodes への自動登録に失敗しました。\nレスポンス: ${JSON.stringify(newEp)}`);
    }
    episodeId = newEp[0].id;
  }

  // ── 2. panel_id を取得または作成 ─────────────────────────
  const panelUrl  = `${supabaseUrl}/rest/v1/manga_panels?episode_id=eq.${episodeId}&panel_number=eq.${panelNumber}&select=id&limit=1`;
  const panelResp = UrlFetchApp.fetch(panelUrl, fetchOpts);
  const panels    = JSON.parse(panelResp.getContentText());

  if (Array.isArray(panels) && panels.length > 0) {
    return panels[0].id;
  }

  // パネルが存在しないので自動作成(description カラムは含めない)
  const newPanel = insertToSupabase('manga_panels', {
    episode_id:   episodeId,
    panel_number: panelNumber
  });
  if (!Array.isArray(newPanel) || !newPanel[0]) {
    throw new Error(`manga_panels への自動登録に失敗しました。\nレスポンス: ${JSON.stringify(newPanel)}`);
  }
  return newPanel[0].id;
}

// ------------------------------------------------------------
// Google Drive ファイルID抽出
// ------------------------------------------------------------
function extractFileId(url) {
  let m;
  m = url.match(/\/file\/d\/([a-zA-Z0-9_-]{10,})/);
  if (m) return m[1];
  m = url.match(/\/d\/([a-zA-Z0-9_-]{10,})/);
  if (m) return m[1];
  m = url.match(/[?&]id=([a-zA-Z0-9_-]{10,})/);
  if (m) return m[1];
  return null;
}

// ------------------------------------------------------------
// Google Drive フォルダID抽出
// ------------------------------------------------------------
function extractFolderId(url) {
  const m = url.match(/\/folders\/([a-zA-Z0-9_-]{10,})/);
  return m ? m[1] : null;
}

// ------------------------------------------------------------
// 初期設定ガイド表示
// ------------------------------------------------------------
function showSetupInstructions() {
  SpreadsheetApp.getUi().alert('⚙️ 初期設定',
    [
      '【STEP 1】 Apps Script を開く',
      '  拡張機能 → Apps Script',
      '',
      '【STEP 2】 スクリプトプロパティを設定',
      '  左メニュー「プロジェクトの設定」',
      '  →「スクリプトプロパティを追加」',
      '',
      '  1 SUPABASE_URL',
      '    https://vdntqwtywxyjxelycavx.supabase.co',
      '',
      '  2 SUPABASE_SERVICE_ROLE_KEY',
      '    Supabase > Settings > API',
      '    > service_role (secret) の値',
      '',
      '⚠️ service_role key はサーバーサイド専用です。',
      '   このスクリプトプロパティは非公開になります。',
    ].join('\n'),
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}
