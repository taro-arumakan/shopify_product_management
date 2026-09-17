# ASHEIS Staff Styling — submission pipeline

Shop staff submit styling photos + price-tag photos through a Google Form.
An Apps Script trigger forwards each submission to GitHub via
`repository_dispatch`, and [staff_styling_to_blogpost.py](../staff_styling_to_blogpost.py)
turns it into an article in the Styling blog.

```
Google Form (staff, photos, tags)
  └─ Drive (photos) + Sheet (answers, スタッフマスタ)
       └─ Apps Script onFormSubmit
            ├─ appends new staff to スタッフマスタ, refreshes the dropdown
            └─ repository_dispatch: staff-styling-submission
                 └─ GitHub Action: staff_styling_article.yml
                      └─ staff_styling_to_blogpost.py
                           decode 13-digit JAN → variant_by_barcode
                           HEIC→JPEG, upload, article + metafields
                           outcome email to NOTIFYEES_STAFF_STYLING
```

**The article is published straight away once it has at least one identified
product and one photo** (`PUBLISH_MIN_PRODUCTS` / `PUBLISH_MIN_PHOTOS`).
Anything wrong past that point — a second tag that would not read, a photo that
failed to import — still gets a 公開・要確認 email, but no longer holds the post
back.

Below the threshold the article is still created, hidden: the email says
非公開・要確認, names what is missing and links both the article in the Shopify
admin and the tag photos in Drive, so the operator can identify the items,
complete the article and publish it. Only an unexpected error leaves no
article, and that is emailed too.

Subjects after 【スタイリング投稿】: 公開 / 公開・要確認 / 非公開・要確認 /
作成済み (a re-run, skipped) / エラー.

Each article carries the form response id in `custom.styling_submission_id`, so
re-running the Action for a submission that already produced an article skips
it rather than publishing the same post twice.

**One mail per submission.** The Action reports every submission it receives, so
the Apps Script side stays quiet on the happy path and mails only when the
Action will never run — the dispatch failed, or `GH_PAT` is unset — naming the
submitter so someone can be asked to re-submit. Both sides address the whole
recipient list in a single mail rather than one mail each, so a recipient can
see who else was told.

The residual gap is a dispatch that GitHub accepts but that never starts a run
(a renamed event type, or the workflow missing from the default branch): the
Apps Script sees a 204 and stays quiet. Worth knowing when changing either
side's event name.

## Prototype setup (Google side, personal account)

1. Open [script.google.com](https://script.google.com) → New project → paste
   [Code.gs](Code.gs) → save.
2. Run `setup()` once and authorize the scopes. It creates:
   - the form (staff dropdown with 新規登録 branch, caption, manual-code fallback)
   - the spreadsheet with the スタッフマスタ tab (seeded with a sample row)
   - the `onFormSubmit` trigger, and stores ids in Script Properties.
3. **Manual step** — Apps Script cannot create file-upload questions. Open the
   form-edit URL printed in the log and add two file-upload questions on the
   「投稿内容」 page, titles exactly as in `TITLES`:
   - 「スタイリング写真」 — images only, max 10 files (no minimum; the first
     photo becomes the cover image)
   - 「下げ札写真」 — images only, max 10 files
   Then delete the placeholder section header.
4. Script Properties (プロジェクトの設定 → スクリプト プロパティ), all optional
   at first:
   - `GH_PAT` — fine-grained PAT for `taro-arumakan/shopify_product_management`
     with **Contents: Read and write** (needed by `repository_dispatch`).
     Until set, submissions are stored + emailed but not dispatched.
   - `GH_REPO` — defaults to `taro-arumakan/shopify_product_management`
   - `NOTIFY_EMAILS` — **required**, comma-separated. No default: this repo
     is public, so the addresses live only in the Script Properties.
   - `MAIL_FROM` — optional, but set it. A 「Send mail as」 alias verified on
     the sending account, used as the From address. **Without it the mail
     never reaches the script owner's own inbox**: Gmail does not deliver a
     message to the account that sent it, a group that account belongs to
     included, and it drops the copy rather than filing it, so no filter
     brings it back. Setting From to an alias is enough — the Action's mail
     goes from the same account to the same group and arrives, differing only
     in that header. Run `showMailAliases()` to see what may be used here.
     Since `MailApp` has no `from` option this goes through `GmailApp`, so the
     script asks for the wider Gmail scope and needs re-authorising after the
     paste that introduces it.
5. Test-submit from a phone. Expect: row in the sheet, photos in Drive
   (「(File responses)」 folders), receipt email, and — once `GH_PAT` is set and
   the workflow is on `main` — a run of the "Staff styling article" action
   whose log prints the parsed payload.

Notes:

- Submitting requires being signed in to any Google account (file upload).
- New-staff registrations are appended to スタッフマスタ automatically; to edit
  the master by hand, fix the rows and run `refreshStaffChoices()`.
- **The staff dropdown is a snapshot, and a page already open keeps the old
  one.** The choices are baked into the form page when it loads, and a
  registration reaches them only through the `onFormSubmit` trigger, which
  starts once the respondent is already on the confirmation screen — so
  nothing here can refresh the page they are looking at. Two things make that
  harmless instead of fixing the unfixable: the built-in 「別の回答を送信」
  link is off in favour of the form URL in the confirmation message, so going
  round again is a fresh page load; and 新規登録 is idempotent — registering a
  name the master already holds overwrites that row rather than adding a
  second one. Someone who cannot find themselves in the list can just register
  again, and the master, the dropdown and the article all stay single.
- 表示名 (latin) drives the article title/URL numbering (e.g. Saki9 / saki-10)
  and the per-staff article tag.
- **Editing Code.gs here changes nothing by itself** — the Apps Script project
  is the deployment, so paste the file in again after every change. Pasting
  updates only the script: `setup()` writes the wording when it *creates* the
  form and refuses to run twice, so after changing any text in `TITLES`,
  `FORM_DESCRIPTION` or `HELP_TEXTS`, run **`syncFormTexts()`** once to push it
  to the existing form. It renames questions listed in `FORMER_TITLES`, updates
  help texts, sets the confirmation message, and logs anything it could not
  find. It never adds or removes
  questions — the two file-upload questions stay as they are and never need
  re-adding.
- The price tag prints **no 品番** — brand, product name, colour, size, price
  and the JAN barcode, nothing else. The barcode is the only identifier on it,
  so the manual fallback asks for the 13 digits printed under the barcode
  rather than a SKU — the payload calls it `manual_jan_codes`. Lookup still
  falls back to SKU, so a code typed from anywhere else resolves too.
- **Share the 「(File responses)」 folders with everyone in
  `NOTIFYEES_STAFF_STYLING`**, not only with the service account: a 要確認
  email links the tag photos so the operator can read the codes off them, and
  those links 404 for anyone the folder was never shared with.

## Repo side

- Workflow: [.github/workflows/staff_styling_article.yml](../../../.github/workflows/staff_styling_article.yml)
  (`repository_dispatch` only fires for workflows on the default branch).
- Secrets required beyond the existing ones: `ASHEIS_ACCESS_TOKEN` and
  `NOTIFYEES_STAFF_STYLING` (comma-separated recipients). Neither has a
  default — the job fails up front if the recipient list is unset, rather than
  finishing and telling nobody.
- Before the processing steps land, share the form's Drive
  「(File responses)」 folders with the service account email from
  `GOOGLE_CREDENTIALS_JSON` so the job can download the photos.

## Migration to the catal.co.jp account (after testing)

Re-run the same setup under the production account (the CEO's catal.co.jp
account as owner, the admin group as editor): new Apps Script project, `setup()`,
re-add the two file-upload questions, set Script Properties, share the new
File-responses folders with the service account. Keep forms with file-upload
questions in My Drive — they are not supported in Shared Drives. The repo side
needs no change beyond rotating `GH_PAT` if it should stop being tied to a
personal token.

Set `MAIL_FROM` again on the new project — the alias is per-account, so the
production account needs its own 「Send mail as」 entry for it. Two things also
get better on their own: `noReply: true` becomes available (it is refused for
consumer gmail.com accounts), and the send quota goes from 100 recipients a day
to 1,500.
