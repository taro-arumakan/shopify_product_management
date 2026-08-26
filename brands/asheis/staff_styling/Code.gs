/**
 * ASHEIS 店舗スタッフ スタイリング投稿 — Google フォーム側プロトタイプ
 *
 * セットアップ手順は同ディレクトリの README.md を参照。
 * 概要:
 *   1. script.google.com で新規プロジェクトを作成し、このファイルを貼り付けて保存
 *   2. setup() を実行して認可 → フォームとスプレッドシート(スタッフマスタ含む)が生成される
 *   3. ログに出力されるフォーム編集URLを開き、「投稿内容」ページに
 *      ファイルアップロード質問を2つ手動で追加する(タイトルは TITLES と完全一致させること)
 *      ※Apps Script / Forms API ではファイルアップロード質問を作成できないため手動
 *   4. スクリプト プロパティ(プロジェクトの設定 → スクリプト プロパティ):
 *        GH_PAT        : repository_dispatch 用 PAT。未設定の間は dispatch をスキップ
 *        GH_REPO       : 省略時 taro-arumakan/shopify_product_management
 *        NOTIFY_EMAILS : 省略時 yusuke@catal.co.jp,taro@sniarti.fi
 */

const TITLES = {
  staffSelect: 'スタッフ名',
  newStaffChoice: '※リストにない(新規登録)',
  regName: '氏名',
  regDisplayName: '表示名(ローマ字)',
  regHeight: '身長',
  regInstagram: 'Instagram',
  regShop: '所属店舗',
  caption: 'キャプション(任意)',
  manualCodes: 'JANコード手入力(バーコードを撮影できない場合のみ)',
  // The question was called SKU手入力 before the tags turned out to carry no
  // 品番 at all. Both titles are accepted so renaming the live form and
  // re-pasting this file can happen in either order without losing answers.
  manualCodesLegacy: 'SKU手入力(バーコードを撮影できない場合のみ)',
  stylingPhotos: 'スタイリング写真',
  tagPhotos: '下げ札写真',
  pageRegister: '新規スタッフ登録',
  pagePost: '投稿内容',
};

const MASTER_SHEET_NAME = 'スタッフマスタ';
const MASTER_HEADERS = ['氏名', '表示名', '身長', 'Instagram', '所属店舗', '登録日'];

const DEFAULTS = {
  GH_REPO: 'taro-arumakan/shopify_product_management',
  NOTIFY_EMAILS: 'yusuke@catal.co.jp,taro@sniarti.fi',
};

function prop_(key) {
  return PropertiesService.getScriptProperties().getProperty(key) || DEFAULTS[key] || '';
}

function setup() {
  const props = PropertiesService.getScriptProperties();
  if (props.getProperty('FORM_ID')) {
    throw new Error(
      'setup 済みです。作り直す場合はスクリプト プロパティの FORM_ID / SPREADSHEET_ID を削除してから再実行してください。'
    );
  }

  const ss = SpreadsheetApp.create('ASHEIS スタッフスタイリング投稿管理 (prototype)');
  const master = ss.getActiveSheet().setName(MASTER_SHEET_NAME);
  master.appendRow(MASTER_HEADERS);
  master.appendRow(['サンプル 花子', 'Hanako', '165cm', 'hanako_asheis', '本店', new Date()]);
  master.setFrozenRows(1);

  const form = FormApp.create('ASHEIS スタッフスタイリング投稿 (prototype)');
  form.setDescription(
    '店舗スタッフ用のスタイリング投稿フォームです。\n' +
      'スタイリング写真(1枚以上、1枚目がカバー画像になります)と、着用商品ごとの下げ札(値札)写真をアップロードしてください。'
  );
  try {
    form.setEmailCollectionType(FormApp.EmailCollectionType.VERIFIED);
  } catch (err) {
    form.setCollectEmail(true);
  }

  form.addListItem().setTitle(TITLES.staffSelect).setRequired(true);

  form.addPageBreakItem().setTitle(TITLES.pageRegister);
  form.addTextItem().setTitle(TITLES.regName).setHelpText('例: 佐藤 咲').setRequired(true);
  form
    .addTextItem()
    .setTitle(TITLES.regDisplayName)
    .setHelpText('記事タイトル・URLに使用します。例: Saki')
    .setRequired(true)
    .setValidation(
      FormApp.createTextValidation()
        .requireTextMatchesPattern('[A-Za-z][A-Za-z0-9_]*')
        .setHelpText('半角ローマ字で入力してください')
        .build()
    );
  form
    .addTextItem()
    .setTitle(TITLES.regHeight)
    .setHelpText('例: 165cm')
    .setRequired(true)
    .setValidation(
      FormApp.createTextValidation()
        .requireTextMatchesPattern('[0-9]{2,3}(cm)?')
        .setHelpText('例: 165cm')
        .build()
    );
  form.addTextItem().setTitle(TITLES.regInstagram).setHelpText('アカウント名のみ。例: asheis_saki(任意)');
  form.addTextItem().setTitle(TITLES.regShop).setHelpText('例: 本店').setRequired(true);

  form.addPageBreakItem().setTitle(TITLES.pagePost);
  form
    .addSectionHeaderItem()
    .setTitle('写真アップロード(セットアップ後に手動追加)')
    .setHelpText(
      'このページに「' +
        TITLES.stylingPhotos +
        '」「' +
        TITLES.tagPhotos +
        '」のファイルアップロード質問を追加してください(README 参照)。追加後この案内は削除して構いません。'
    );
  form.addParagraphTextItem().setTitle(TITLES.caption).setHelpText('コーディネートの説明など(任意)');
  form
    .addParagraphTextItem()
    .setTitle(TITLES.manualCodes)
    .setHelpText('下げ札のバーコードを撮影できない場合のみ、バーコード下の13桁の数字を1行に1つ入力');

  refreshStaffChoices_(form, master);

  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  ScriptApp.newTrigger('onFormSubmitHandler').forForm(form).onFormSubmit().create();

  props.setProperties({ FORM_ID: form.getId(), SPREADSHEET_ID: ss.getId() });

  Logger.log('フォーム編集URL: %s', form.getEditUrl());
  Logger.log('フォーム回答URL: %s', form.getPublishedUrl());
  Logger.log('スプレッドシート: %s', ss.getUrl());
  Logger.log(
    'TODO: フォーム編集画面の「%s」ページにファイルアップロード質問を2つ追加してください: 「%s」「%s」(いずれも画像のみ・最大10ファイル)',
    TITLES.pagePost,
    TITLES.stylingPhotos,
    TITLES.tagPhotos
  );
}

/** スタッフマスタを編集した後に手動で実行するとプルダウンへ反映される。 */
function refreshStaffChoices() {
  const form = FormApp.openById(prop_('FORM_ID'));
  const master = SpreadsheetApp.openById(prop_('SPREADSHEET_ID')).getSheetByName(MASTER_SHEET_NAME);
  refreshStaffChoices_(form, master);
}

function refreshStaffChoices_(form, masterSheet) {
  const staffItem = form
    .getItems(FormApp.ItemType.LIST)
    .map(function (i) {
      return i.asListItem();
    })
    .find(function (i) {
      return i.getTitle() === TITLES.staffSelect;
    });
  const pages = form.getItems(FormApp.ItemType.PAGE_BREAK).map(function (i) {
    return i.asPageBreakItem();
  });
  const pageRegister = pages.find(function (p) {
    return p.getTitle() === TITLES.pageRegister;
  });
  const pagePost = pages.find(function (p) {
    return p.getTitle() === TITLES.pagePost;
  });

  const names = masterSheet
    .getDataRange()
    .getValues()
    .slice(1)
    .map(function (r) {
      return String(r[0]).trim();
    })
    .filter(String);
  const choices = names.map(function (n) {
    return staffItem.createChoice(n, pagePost);
  });
  choices.push(staffItem.createChoice(TITLES.newStaffChoice, pageRegister));
  staffItem.setChoices(choices);
}

function onFormSubmitHandler(e) {
  try {
    const fr = e.response;
    const answers = {};
    const files = {};
    fr.getItemResponses().forEach(function (ir) {
      const item = ir.getItem();
      if (item.getType() === FormApp.ItemType.FILE_UPLOAD) {
        files[item.getTitle()] = ir.getResponse(); // Drive ファイルIDの配列
      } else {
        answers[item.getTitle()] = ir.getResponse();
      }
    });

    const ss = SpreadsheetApp.openById(prop_('SPREADSHEET_ID'));
    const master = ss.getSheetByName(MASTER_SHEET_NAME);

    let staff;
    if (answers[TITLES.staffSelect] === TITLES.newStaffChoice) {
      staff = {
        name: String(answers[TITLES.regName] || '').trim(),
        display_name: String(answers[TITLES.regDisplayName] || '').trim(),
        height: normalizeHeight_(answers[TITLES.regHeight]),
        instagram: String(answers[TITLES.regInstagram] || '').trim(),
        shop: String(answers[TITLES.regShop] || '').trim(),
        is_new: true,
      };
      master.appendRow([staff.name, staff.display_name, staff.height, staff.instagram, staff.shop, new Date()]);
      refreshStaffChoices_(FormApp.openById(prop_('FORM_ID')), master);
    } else {
      const row = master
        .getDataRange()
        .getValues()
        .slice(1)
        .find(function (r) {
          return String(r[0]).trim() === answers[TITLES.staffSelect];
        });
      if (!row) throw new Error('スタッフマスタに該当がありません: ' + answers[TITLES.staffSelect]);
      staff = {
        name: String(row[0]).trim(),
        display_name: String(row[1]).trim(),
        height: normalizeHeight_(row[2]),
        instagram: String(row[3]).trim(),
        shop: String(row[4]).trim(),
        is_new: false,
      };
    }

    let respondentEmail = '';
    try {
      respondentEmail = fr.getRespondentEmail() || '';
    } catch (err) {
      // メール収集が無効な場合は空のまま
    }

    const submission = {
      response_id: fr.getId(),
      submitted_at: fr.getTimestamp().toISOString(),
      respondent_email: respondentEmail,
      staff: staff,
      caption: String(answers[TITLES.caption] || ''),
      manual_skus: String(answers[TITLES.manualCodes] || answers[TITLES.manualCodesLegacy] || '')
        .split('\n')
        .map(function (s) {
          return s.trim();
        })
        .filter(String),
      styling_photo_ids: files[TITLES.stylingPhotos] || [],
      tag_photo_ids: files[TITLES.tagPhotos] || [],
      spreadsheet_id: prop_('SPREADSHEET_ID'),
    };

    const dispatch = dispatchToGitHub_(submission);
    if (dispatch.ok) {
      // The Action reports on every submission it receives, and its mail says
      // everything a receipt would plus the article link. This side speaks up
      // only when the Action will never run.
      Logger.log('dispatched; the outcome mail is left to the Action');
      return;
    }

    notify_(
      '【スタイリング投稿】連携失敗: ' + staff.name,
      [
        '記事作成処理を起動できませんでした。写真と回答は保存されています。',
        '',
        '理由: ' + dispatch.detail,
        '',
        'スタッフ: ' +
          staff.name +
          ' (' +
          staff.display_name +
          ' / ' +
          staff.shop +
          ')' +
          (staff.is_new ? ' ※新規登録' : ''),
        '投稿者: ' + (respondentEmail || '(メール収集が無効)'),
        'スタイリング写真: ' + submission.styling_photo_ids.length + '枚',
        '下げ札写真: ' + submission.tag_photo_ids.length + '枚',
        'コード手入力: ' + (submission.manual_skus.join(', ') || 'なし'),
        '',
        '回答スプレッドシート: ' + ss.getUrl(),
        '',
        'GitHub Actions 側の設定を確認してください。復旧後は投稿者に再投稿を依頼してください。',
      ].join('\n')
    );
  } catch (err) {
    notify_(
      '【スタイリング投稿】フォーム側エラー',
      ['フォーム送信の処理中にエラーが発生しました。', '', String((err && err.stack) || err)].join('\n')
    );
    throw err;
  }
}

function normalizeHeight_(v) {
  const s = String(v || '').trim();
  if (!s) return '';
  return /cm$/i.test(s) ? s : s + 'cm';
}


/**
 * #TODO [CEC-471] comments in English
 * repository_dispatch を送信し、{ok, detail} を返す。
 * 送信失敗は例外にせずメールで可視化する — 写真・回答自体は保存済みのため。
 */
function dispatchToGitHub_(submission) {
  const pat = prop_('GH_PAT');
  if (!pat) {
    Logger.log('GH_PAT が未設定のため repository_dispatch をスキップしました');
    return { ok: false, detail: 'GH_PAT が未設定のため連携をスキップしました' };
  }
  try {
    const res = UrlFetchApp.fetch('https://api.github.com/repos/' + prop_('GH_REPO') + '/dispatches', {
      method: 'post',
      contentType: 'application/json',
      muteHttpExceptions: true,
      headers: {
        Authorization: 'Bearer ' + pat,
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
      },
      // client_payload はトップレベル10キー制限があるため submission 1キーに集約する
      payload: JSON.stringify({
        event_type: 'staff-styling-submission',
        client_payload: { submission: submission },
      }),
    });
    const code = res.getResponseCode();
    if (code >= 300) {
      Logger.log('repository_dispatch failed: %s %s', code, res.getContentText());
      return { ok: false, detail: 'HTTP ' + code + ' — ' + res.getContentText().slice(0, 200) };
    }
    return { ok: true, detail: '起動しました' };
  } catch (err) {
    Logger.log('repository_dispatch error: %s', err);
    return { ok: false, detail: String(err) };
  }
}

/** One mail addressed to every recipient, so each can see who else was told. */
function notify_(subject, body) {
  const to = prop_('NOTIFY_EMAILS')
    .split(',')
    .map(function (s) {
      return s.trim();
    })
    .filter(String)
    .join(',');
  if (!to) return;
  MailApp.sendEmail(to, subject, body);
}
