# Meta reporting access setup (per brand)

How to grant the reporting pipeline read access to a brand's Meta assets — Ad
Account, Instagram account, and Facebook Page — via a **System User** and the
`metrics_reporting` Meta Developer App. Do this once when onboarding a brand into
the monthly extraction / dashboard jobs.

Source: [CEC-287](https://sniarti.atlassian.net/browse/CEC-287).

> Note: `pages_read_engagement` etc. are **token scopes** (chosen at token
> generation), not the same thing as the Page's *task* assignment. You need both:
> the asset assigned to the System User **and** the token carrying the scope.

## 1. Share the app with the target brand's Business

The `metrics_reporting` app is owned by the **Blossom JP** portfolio. Rather than
adding the app from the target brand's Business Suite, share it from the app
owner's side:

1. **Meta Business Settings** for the portfolio that owns the app (Blossom JP).
2. **Accounts → Apps** → select **metrics reporting**.
3. Click **Share Assets** (or **Assign Partners**).
4. Enter the **Business ID** of the target brand (e.g. "Apricot Studios Japan").
5. Assign **Full Control**.

## 2. Create a System User on the target brand and assign assets

In the **target brand's** Meta Business Suite → **Users → System users**:

1. **Add** → name it `metrics_reporting`, role **Admin**.
2. **Assign Assets → Apps** → choose `metrics reporting` → **Full Control** → save.
3. **Assign Assets → Ad Accounts** → the brand's ad account → **View performance** (or Manage).
4. **Assign Assets → Instagram Accounts** → the brand's IG account → **Insights**.
5. **Assign Assets → Facebook Pages** → the brand's Page → **Manage** → toggle **Insights**
   (or **Content**, which may enable Insights).
   - Some accounts grey this out with "managed in connected Instagram account" —
     that has been fine for the brands done so far.

## 3. Generate the token with the right scopes

**System users → metrics_reporting → Generate New Token** → select the app →
check these scopes:

| Purpose | Scopes |
|---|---|
| Instagram + Ads | `ads_read`, `instagram_basic`, `instagram_manage_insights` |
| Facebook Page insights | `pages_read_engagement`, `read_insights` |

(`pages_read_engagement` unlocks the Page-access-token step the dashboard does
first; `read_insights` unlocks the Page insight metrics. Missing
`pages_read_engagement` is what produces the `(#100) … requires the
'pages_read_engagement' permission` error.)

Copy the token string — this is the brand's `META_TOKEN`.

## 4. Wire it into the pipeline

The pipeline reads per-brand creds by **env prefix** (e.g. `kumej`,
`apricot-studios`, `rohseoul`). Set all of these:

| Variable | Value |
|---|---|
| `<prefix>-ACCESS_TOKEN` | Shopify Admin API token |
| `<prefix>-GSPREAD_ID` | brand's Google Sheet id |
| `<prefix>-META_TOKEN` | System User token from step 3 |
| `<prefix>-META_AD_ACCOUNT_ID` | Meta ad account id |
| `<prefix>-IG_USER_ID` | Instagram user id |
| `<prefix>-FB_PAGE_ID` | Facebook Page id |

Put them in:
- **`.env`** for local runs, and
- **GitHub Actions secrets** for the scheduled jobs, named `<PREFIX>_<VAR>`
  (uppercase, dashes → underscores — e.g. `kumej-META_TOKEN` → `KUMEJ_META_TOKEN`),
  then reference them in each workflow's `.env` block.

Also register the brand in code: the GA property map
(`helpers/ga_reporting_interface.py`), and the brand lists in
`extract_monthly_reports.py` and `brands/scripts/update_dashboard.py`. Missing
Meta/IG creds are skipped gracefully (Shopify + GA still run), so a brand can be
onboarded incrementally.
