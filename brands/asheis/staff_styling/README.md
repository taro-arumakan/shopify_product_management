# ASHEIS Staff Styling — submission pipeline

Shop staff submit styling photos + price-tag photos through a Google Form.
An Apps Script trigger forwards each submission to GitHub via
`repository_dispatch`, and [staff_styling_to_blogpost.py](../staff_styling_to_blogpost.py)
turns it into a hidden article in the Styling blog for review and publishing.

```
Google Form (staff, photos, tags)
  └─ Drive (photos) + Sheet (answers, スタッフマスタ)
       └─ Apps Script onFormSubmit
            ├─ appends new staff to スタッフマスタ, refreshes the dropdown
            ├─ receipt email to NOTIFY_EMAILS
            └─ repository_dispatch: staff-styling-submission
                 └─ GitHub Action: staff_styling_article.yml
                      └─ staff_styling_to_blogpost.py
                           decode JAN (== SKU) → variant_by_sku
                           HEIC→JPEG, upload, hidden article + metafields
                           outcome email to NOTIFYEES_STAFF_STYLING
```

## Prototype setup (Google side, personal account)

1. Open [script.google.com](https://script.google.com) → New project → paste
   [Code.gs](Code.gs) → save.
2. Run `setup()` once and authorize the scopes. It creates:
   - the form (staff dropdown with 新規登録 branch, caption, manual-SKU fallback)
   - the spreadsheet with the スタッフマスタ tab (seeded with a sample row)
   - the `onFormSubmit` trigger, and stores ids in Script Properties.
3. **Manual step** — Apps Script cannot create file-upload questions. Open the
   form-edit URL printed in the log and add two file-upload questions on the
   「投稿内容」 page, titles exactly as in `TITLES`:
   - 「スタイリング写真」 — images only, max 10 files (min 4 is enforced by
     convention/review, Forms cannot enforce a minimum)
   - 「下げ札写真」 — images only, max 10 files
   Then delete the placeholder section header.
4. Script Properties (プロジェクトの設定 → スクリプト プロパティ), all optional
   at first:
   - `GH_PAT` — fine-grained PAT for `taro-arumakan/shopify_product_management`
     with **Contents: Read and write** (needed by `repository_dispatch`).
     Until set, submissions are stored + emailed but not dispatched.
   - `GH_REPO` — defaults to `taro-arumakan/shopify_product_management`
   - `NOTIFY_EMAILS` — defaults to `yusuke@catal.co.jp,taro@sniarti.fi`
5. Test-submit from a phone. Expect: row in the sheet, photos in Drive
   (「(File responses)」 folders), receipt email, and — once `GH_PAT` is set and
   the workflow is on `main` — a run of the "Staff styling article" action
   whose log prints the parsed payload.

Notes:

- Submitting requires being signed in to any Google account (file upload).
- New-staff registrations are appended to スタッフマスタ automatically; to edit
  the master by hand, fix the rows and run `refreshStaffChoices()`.
- 表示名 (latin) drives the article title/URL numbering (e.g. Saki9 / saki-10)
  and the per-staff article tag.

## Repo side

- Workflow: [.github/workflows/staff_styling_article.yml](../../../.github/workflows/staff_styling_article.yml)
  (`repository_dispatch` only fires for workflows on the default branch).
- Secrets required beyond the existing ones: `ASHEIS_ACCESS_TOKEN`,
  optionally `NOTIFYEES_STAFF_STYLING` (falls back to
  `yusuke@catal.co.jp,taro@sniarti.fi`).
- Before the processing steps land, share the form's Drive
  「(File responses)」 folders with the service account email from
  `GOOGLE_CREDENTIALS_JSON` so the job can download the photos.

## Migration to the catal.co.jp account (after testing)

Re-run the same setup under the production account (namekata@catal.co.jp as
owner, admin@catal.co.jp group as editor): new Apps Script project, `setup()`,
re-add the two file-upload questions, set Script Properties, share the new
File-responses folders with the service account. Keep forms with file-upload
questions in My Drive — they are not supported in Shared Drives. The repo side
needs no change beyond rotating `GH_PAT` if it should stop being tied to a
personal token.
