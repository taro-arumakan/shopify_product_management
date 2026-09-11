/**
 * ASHEIS shop-staff styling submissions — the Google Form side.
 *
 * Text shown to staff (form titles, help texts) and text sent to the office
 * (mail subjects and bodies) stays Japanese; everything else here is English.
 * Full setup instructions live in README.md next to this file.
 *
 *   1. Create a new project at script.google.com, paste this file in, save.
 *   2. Run setup() and grant the scopes. It creates the form and the
 *      spreadsheet (which also holds the staff master).
 *   3. Open the form-edit URL from the log and add the two file-upload
 *      questions by hand, with the exact titles in TITLES — Apps Script and
 *      the Forms API cannot create that question type.
 *   4. Script properties (Project settings → Script properties):
 *        GH_PAT        : PAT for repository_dispatch. Until it is set the
 *                        dispatch is skipped and the failure mail says so.
 *        GH_REPO       : defaults to taro-arumakan/shopify_product_management
 *        NOTIFY_EMAILS : required. Comma-separated recipients of the failure
 *                        mail. No default — this repository is public.
 *        MAIL_FROM     : optional but wanted. A 「Send mail as」 alias verified
 *                        on this account, used as the From address. See
 *                        notify_ for why it is not cosmetic.
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
  stylingPhotos: 'スタイリング写真',
  tagPhotos: '下げ札写真',
  pageRegister: '新規スタッフ登録',
  pagePost: '投稿内容',
};

// Former title -> current title, used by syncFormTexts() to rename a
// question on a form that already exists. Empty it once every form is synced.
const FORMER_TITLES = {
  'SKU手入力(バーコードを撮影できない場合のみ)': TITLES.manualCodes,
};

const FORM_DESCRIPTION =
  '店舗スタッフ用のスタイリング投稿フォームです。\n' +
  'スタイリング写真(1枚以上、1枚目がカバー画像になります)と、着用商品ごとの下げ札(値札)写真をアップロードしてください。';

// setup() and syncFormTexts() read the same definitions, so the wording is
// only ever edited here.
const HELP_TEXTS = {};
HELP_TEXTS[TITLES.regName] = '例: 佐藤 咲';
HELP_TEXTS[TITLES.regDisplayName] = '記事タイトル・URLに使用します。例: Saki';
HELP_TEXTS[TITLES.regHeight] = '例: 165cm';
HELP_TEXTS[TITLES.regInstagram] = 'アカウント名のみ。例: asheis_saki(任意)';
HELP_TEXTS[TITLES.regShop] = '例: 本店';
HELP_TEXTS[TITLES.stylingPhotos] = '1枚目がカバー画像になります(枚数の下限なし)';
HELP_TEXTS[TITLES.tagPhotos] = 'バーコードと商品名の入った下げ札画像';
HELP_TEXTS[TITLES.caption] = 'コーディネートの説明など(任意)';
HELP_TEXTS[TITLES.manualCodes] =
  '下げ札のバーコードを撮影できない場合のみ、バーコード下の13桁の数字を1行に1つ入力';

const MASTER_SHEET_NAME = 'スタッフマスタ';
const MASTER_HEADERS = ['氏名', '表示名', '身長', 'Instagram', '所属店舗', '登録日'];

const DEFAULTS = {
  GH_REPO: 'taro-arumakan/shopify_product_management',
};

function prop_(key) {
  return PropertiesService.getScriptProperties().getProperty(key) || DEFAULTS[key] || '';
}

function setup() {
  const props = PropertiesService.getScriptProperties();
  if (props.getProperty('FORM_ID')) {
    throw new Error(
      'Already set up. To build a new form and spreadsheet, clear the FORM_ID ' +
        'and SPREADSHEET_ID script properties first — note that doing so leaves ' +
        'the existing responses and staff master behind.'
    );
  }

  const ss = SpreadsheetApp.create('ASHEIS スタッフスタイリング投稿管理 (prototype)');
  const master = ss.getActiveSheet().setName(MASTER_SHEET_NAME);
  master.appendRow(MASTER_HEADERS);
  master.appendRow(['サンプル 花子', 'Hanako', '165cm', 'hanako_asheis', '本店', new Date()]);
  master.setFrozenRows(1);

  const form = FormApp.create('ASHEIS スタッフスタイリング投稿 (prototype)');
  form.setDescription(FORM_DESCRIPTION);
  try {
    form.setEmailCollectionType(FormApp.EmailCollectionType.VERIFIED);
  } catch (err) {
    form.setCollectEmail(true);
  }

  form.addListItem().setTitle(TITLES.staffSelect).setRequired(true);

  form.addPageBreakItem().setTitle(TITLES.pageRegister);
  form.addTextItem().setTitle(TITLES.regName).setHelpText(HELP_TEXTS[TITLES.regName]).setRequired(true);
  form
    .addTextItem()
    .setTitle(TITLES.regDisplayName)
    .setHelpText(HELP_TEXTS[TITLES.regDisplayName])
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
    .setHelpText(HELP_TEXTS[TITLES.regHeight])
    .setRequired(true)
    .setValidation(
      FormApp.createTextValidation()
        .requireTextMatchesPattern('[0-9]{2,3}(cm)?')
        .setHelpText('例: 165cm')
        .build()
    );
  form.addTextItem().setTitle(TITLES.regInstagram).setHelpText(HELP_TEXTS[TITLES.regInstagram]);
  form.addTextItem().setTitle(TITLES.regShop).setHelpText(HELP_TEXTS[TITLES.regShop]).setRequired(true);

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
  form.addParagraphTextItem().setTitle(TITLES.caption).setHelpText(HELP_TEXTS[TITLES.caption]);
  form
    .addParagraphTextItem()
    .setTitle(TITLES.manualCodes)
    .setHelpText(HELP_TEXTS[TITLES.manualCodes]);

  refreshStaffChoices_(form, master);
  applyConfirmation_(form);

  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  ScriptApp.newTrigger('onFormSubmitHandler').forForm(form).onFormSubmit().create();

  props.setProperties({ FORM_ID: form.getId(), SPREADSHEET_ID: ss.getId() });

  Logger.log('form edit URL: %s', form.getEditUrl());
  Logger.log('form response URL: %s', form.getPublishedUrl());
  Logger.log('spreadsheet: %s', ss.getUrl());
  Logger.log(
    'TODO: on the "%s" page of the form editor, add two file-upload questions ' +
      'titled "%s" and "%s" (images only, max 10 files each)',
    TITLES.pagePost,
    TITLES.stylingPhotos,
    TITLES.tagPhotos
  );
}

/**
 * Push the wording defined in this file onto the form that already exists.
 *
 * setup() only writes the wording when it creates the form, so pasting this
 * file in again changes nothing a respondent sees. Run this once after
 * editing any text. It never adds or removes questions: Apps Script cannot
 * create a file-upload question, but it can retitle and re-describe one.
 */
function syncFormTexts() {
  const form = FormApp.openById(prop_('FORM_ID'));
  form.setDescription(FORM_DESCRIPTION);
  applyConfirmation_(form);

  form.getItems().forEach(function (item) {
    const renamed = FORMER_TITLES[item.getTitle()];
    if (renamed) {
      Logger.log('renaming "%s" -> "%s"', item.getTitle(), renamed);
      item.setTitle(renamed);
    }
    const help = HELP_TEXTS[item.getTitle()];
    if (help !== undefined && item.getHelpText() !== help) {
      Logger.log('help text updated: %s', item.getTitle());
      item.setHelpText(help);
    }
  });

  // A question we expected is missing, which needs fixing by hand — say so
  // rather than passing silently.
  const titles = form.getItems().map(function (i) {
    return i.getTitle();
  });
  Object.keys(HELP_TEXTS).forEach(function (title) {
    if (titles.indexOf(title) === -1) {
      Logger.log('!! not found on the form, check by hand: %s', title);
    }
  });
  Logger.log('done: %s', form.getEditUrl());
}

/**
 * Send the respondent back through a fresh page load.
 *
 * The staff dropdown is a snapshot baked into the page the respondent already
 * has open; a registration is written to it by the onFormSubmit trigger, which
 * only starts once that respondent is already looking at the confirmation
 * screen. Nothing here can reach into that open page, so the built-in
 * 「別の回答を送信」 link is turned off and the form URL is offered instead —
 * a plain navigation, which fetches the choices again.
 */
function applyConfirmation_(form) {
  form.setShowLinkToRespondAgain(false);
  form.setConfirmationMessage(
    '投稿ありがとうございました。\n' +
      '内容を確認のうえ、記事を作成します。\n\n' +
      '続けて投稿する場合はこちらから:\n' +
      form.getPublishedUrl() +
      '\n(新規登録された方は、このリンクから開き直すとスタッフ名の一覧に反映されます)'
  );
}

/** Run by hand after editing the staff master to refresh the dropdown. */
function refreshStaffChoices() {
  const form = FormApp.openById(prop_('FORM_ID'));
  const master = SpreadsheetApp.openById(prop_('SPREADSHEET_ID')).getSheetByName(MASTER_SHEET_NAME);
  refreshStaffChoices_(form, master);
}

/** Master rows that carry a name, each with its 1-based sheet row number. */
function masterRows_(masterSheet) {
  return masterSheet
    .getDataRange()
    .getValues()
    .map(function (values, i) {
      return { row: i + 1, values: values };
    })
    .slice(1)
    .filter(function (r) {
      return String(r.values[0]).trim();
    });
}

/**
 * The master row for a name, or null.
 *
 * Compared with every space removed: the master is hand-editable, and Forms
 * rewrites a full-width space in a choice value as a plain one, so the two
 * spellings of one name have to meet somewhere.
 */
function masterRowFor_(masterSheet, name) {
  const wanted = nameKey_(name);
  return (
    masterRows_(masterSheet).find(function (r) {
      return nameKey_(r.values[0]) === wanted;
    }) || null
  );
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
        files[item.getTitle()] = ir.getResponse(); // array of Drive file ids
      } else {
        answers[item.getTitle()] = ir.getResponse();
      }
    });

    const ss = SpreadsheetApp.openById(prop_('SPREADSHEET_ID'));
    const master = ss.getSheetByName(MASTER_SHEET_NAME);

    let staff;
    if (answers[TITLES.staffSelect] === TITLES.newStaffChoice) {
      staff = {
        name: normalizeSpaces_(answers[TITLES.regName]),
        display_name: normalizeSpaces_(answers[TITLES.regDisplayName]),
        height: normalizeHeight_(answers[TITLES.regHeight]),
        instagram: normalizeSpaces_(answers[TITLES.regInstagram]),
        shop: normalizeSpaces_(answers[TITLES.regShop]),
        is_new: true,
      };
      // Registering is also what a staff member does when the dropdown they
      // are looking at predates their own registration, so the same name can
      // arrive twice. Overwrite that row instead of appending a second one:
      // two rows with one name would put the name in the dropdown twice and
      // make which record wins depend on sheet order.
      const existing = masterRowFor_(master, staff.name);
      if (existing) {
        master
          .getRange(existing.row, 1, 1, 5)
          .setValues([[staff.name, staff.display_name, staff.height, staff.instagram, staff.shop]]);
        staff.is_new = false;
        Logger.log('re-registration of %s: updated master row %s', staff.name, existing.row);
      } else {
        master.appendRow([staff.name, staff.display_name, staff.height, staff.instagram, staff.shop, new Date()]);
      }
      refreshStaffChoices_(FormApp.openById(prop_('FORM_ID')), master);
    } else {
      const found = masterRowFor_(master, answers[TITLES.staffSelect]);
      if (!found) {
        // The dropdown is a snapshot written into the form; the master is read
        // live on every submission. Editing or removing a master row leaves the
        // old name selectable, and this is where that turns up — the staff
        // member picks a name that no longer exists. Rebuild the choices so the
        // stale one disappears, and say what the master actually holds, because
        // the mismatch is usually invisible at a glance.
        try {
          refreshStaffChoices_(FormApp.openById(prop_('FORM_ID')), master);
        } catch (refreshErr) {
          Logger.log('could not refresh the choices: %s', refreshErr);
        }
        throw new Error(
          'スタッフマスタに該当がありません: 「' +
            answers[TITLES.staffSelect] +
            '」 現在のスタッフマスタ: ' +
            masterRows_(master)
              .map(function (r) {
                return '「' + String(r.values[0]).trim() + '」';
              })
              .join(' ') +
            ' (フォームの選択肢を更新しました。再投稿をご依頼ください)'
        );
      }
      const row = found.values;
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
      // Left empty when email collection is off.
    }

    const submission = {
      response_id: fr.getId(),
      submitted_at: fr.getTimestamp().toISOString(),
      respondent_email: respondentEmail,
      staff: staff,
      caption: String(answers[TITLES.caption] || ''),
      manual_jan_codes: String(answers[TITLES.manualCodes] || '')
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
        'コード手入力: ' + (submission.manual_jan_codes.join(', ') || 'なし'),
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

/**
 * Collapse any run of whitespace, full-width included, to one plain space.
 *
 * Forms does this to a choice value on its own: a name registered as
 * 「和泉　紀亜」 with a full-width space is stored on the form as 「和泉 紀亜」
 * with a half-width one, and that is what comes back in the response. Writing
 * the master in the same shape keeps the master, the choice and the answer
 * identical instead of leaving the master the odd one out.
 */
function normalizeSpaces_(value) {
  return String(value == null ? '' : value)
    .replace(/[\s\u3000]+/g, ' ')
    .trim();
}

/**
 * Key a staff name for comparison, ignoring whitespace entirely.
 *
 * normalizeSpaces_ keeps new registrations consistent, but rows written before
 * it, or edited by hand since, can still differ by a space. Names do not
 * collide on spacing alone, so matching on the spaceless form costs nothing
 * and spares a staff member a submission that fails for an invisible reason.
 */
function nameKey_(value) {
  return String(value == null ? '' : value).replace(/[\s\u3000]+/g, '');
}

function normalizeHeight_(v) {
  const s = String(v || '').trim();
  if (!s) return '';
  return /cm$/i.test(s) ? s : s + 'cm';
}


/**
 * Send the repository_dispatch and return {ok, detail}.
 *
 * A failure is reported rather than thrown: the photos and the answers are
 * already saved, so the submission is not lost — only its processing is. The
 * detail is Japanese because it is quoted into the failure mail.
 */
function dispatchToGitHub_(submission) {
  const pat = prop_('GH_PAT');
  if (!pat) {
    Logger.log('GH_PAT is not set; skipping repository_dispatch');
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
      // client_payload allows only 10 top-level keys, so everything goes
      // under a single `submission` key.
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
    return { ok: true, detail: 'dispatched' };
  } catch (err) {
    Logger.log('repository_dispatch error: %s', err);
    return { ok: false, detail: String(err) };
  }
}

/** One mail addressed to every recipient, so each can see who else was told. */
/**
 * Mail the office, as the MAIL_FROM alias rather than as this account.
 *
 * That is not cosmetic. Gmail does not deliver a message to the inbox of the
 * account that sent it — a group that account belongs to included — so a
 * notification addressed only to the admin group never reaches whoever owns
 * the script, who is usually the person watching it most closely. The copy is
 * dropped rather than filed, so no filter brings it back.
 *
 * Setting From to a verified 「Send mail as」 alias is enough: the Action's
 * mail already does exactly this over SMTP, from this same account, to this
 * same group, and it arrives. Only the From header differs.
 *
 * MailApp has no from option, so this goes through GmailApp — which is why the
 * script asks for the wider Gmail scope and needs re-authorising after a paste.
 * An alias that is not verified on the account would be ignored silently and
 * the mail would go out as the account again, which is the failure we are
 * trying to avoid, so check it and say so rather than sending it blind.
 */
function notify_(subject, body) {
  const to = prop_('NOTIFY_EMAILS')
    .split(',')
    .map(function (s) {
      return s.trim();
    })
    .filter(String)
    .join(',');
  if (!to) {
    // Nothing to fall back on: the addresses are a script property precisely
    // so they stay out of a public repository. Say so loudly in the log.
    Logger.log('NOTIFY_EMAILS script property is not set; cannot send: %s', subject);
    return;
  }

  const from = prop_('MAIL_FROM');
  if (!from) {
    Logger.log('MAIL_FROM is not set; sending as this account, which will not reach its own inbox');
    MailApp.sendEmail(to, subject, body);
    return;
  }

  const aliases = GmailApp.getAliases();
  if (aliases.indexOf(from) === -1) {
    Logger.log(
      'MAIL_FROM %s is not a verified alias on this account, so it would be ignored; ' +
        'sending as the account instead. Verified aliases: %s',
      from,
      aliases.join(', ') || '(none)'
    );
    MailApp.sendEmail(to, subject, body);
    return;
  }

  GmailApp.sendEmail(to, subject, body, { from: from });
}

/** Run by hand to see what MAIL_FROM may be set to. */
function showMailAliases() {
  Logger.log('verified 「Send mail as」 aliases: %s', GmailApp.getAliases().join(', ') || '(none)');
}
