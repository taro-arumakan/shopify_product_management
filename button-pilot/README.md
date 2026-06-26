# Atelier Buttons — B2B Trade Pilot

A from-scratch pilot storefront for a **B2B garment-button** business. Showcases 4
products and validates three B2B fundamentals before a full build:

1. **Login-gated catalog** — only approved trade accounts see prices / can order.
2. **Wholesale tiered pricing** — per-account tiers with quantity breaks, resolved
   **server-side** so guests never receive price data.
3. **Quote / inquiry requests** — bulk/custom requests via a simple form → email
   (+ optional Google Sheet).

Built with **Next.js 15 (App Router) + React 19 + Tailwind v4**. No database. Cart/checkout
is offloaded to **Snipcart** (swappable behind `src/lib/cart.ts`).

> Product visuals are consistent **SVG mockups** (`src/components/ButtonSwatch.tsx`).
> See `content/image-prompts.md` to generate photoreal heroes later.

---

## Quick start

```bash
cd button-pilot
npm install
cp .env.local.example .env.local      # then set AUTH_SECRET (openssl rand -base64 32)
npm run dev                            # http://localhost:3000
```

No email/cart keys are needed for local dev:
- Magic-link emails are **printed to the server console** (no Resend key).
- Add-to-cart is disabled until `NEXT_PUBLIC_SNIPCART_KEY` is set; everything else works.

### Try the gated pricing
1. Visit `/catalog` as a guest — products show, **no prices**.
2. Go to `/login`, enter a seeded demo account (see `src/lib/allowlist.ts`):
   - `buyer@example-standard.com` (standard tier)
   - `buyer@example-volume.com` (volume tier)
   - `buyer@example-partner.com` (partner tier)
3. Copy the magic link from the **server console**, open it → you're signed in and prices appear.
4. Compare a product's price across the three accounts to see the tiers; raise the quantity
   past a break (e.g. 25 or 100) to see the unit price drop.

---

## How it works

| Concern | Where | Notes |
|---|---|---|
| Product data | `content/products/*.json` | Validated by Zod at build — bad data fails `next build`. |
| Schema (source of truth) | `src/lib/schema.ts` | Product → variant model; tiers + quantity breaks. |
| Price resolution | `src/lib/pricing.ts` (`server-only`) | Returns `null` for guests; never runs client-side. |
| Gated price API | `src/app/api/price/route.ts` | 401 for guests (via `middleware.ts`); powers the live pricer. |
| Auth | `src/lib/{session,auth,allowlist}.ts` | Signed (HMAC) magic-link + session cookie. No DB. |
| Gate | `src/middleware.ts` | Catalog/product pages are public (SEO); price API + `/account` gated. |
| Cart | `src/lib/cart.ts`, `TradeOrderPanel.tsx` | Snipcart adapter; swap for Stripe/Medusa later. |
| Quote | `src/app/api/quote/route.ts` | Honeypot + rate limit → Resend email + optional Sheet. |

**Why prices can't leak:** the catalog HTML is public for SEO, but prices are computed in
Server Components / a gated API keyed to the signed-in tier. A guest's HTML and network
payloads contain no price numbers — there is no client-side gate to bypass.

---

## Configuration

All env vars are documented in `.env.local.example`. Summary:

- `AUTH_SECRET` *(required)* — signs tokens.
- `RESEND_API_KEY`, `EMAIL_FROM`, `QUOTE_INBOX` — real email (else console fallback).
- `TRADE_ALLOWLIST` — add approved accounts without code changes: `email|tier|Company`.
- `NEXT_PUBLIC_SNIPCART_KEY`, `NEXT_PUBLIC_CART_PROVIDER` — enable the cart.
- `QUOTE_SHEET_WEBHOOK_URL` — append quotes to a Google Sheet (see below).
- `NEXT_PUBLIC_SITE_URL` — absolute URL for email links in production.

### Adding / editing products
Add a JSON file under `content/products/` matching `src/lib/schema.ts`. `npm run build`
validates it. Sizes are in **ligne** (`sizeLigne`) with `sizeMm` (1 ligne ≈ 0.635 mm);
prices are per-tier arrays of `{ minQty, unitPrice }` sorted ascending.

### Adding photoreal images
Generate with the prompts in `content/image-prompts.md`, save to
`public/images/products/<variantSku>.jpg`, then render them via `next/image` in
`ButtonSwatch`/product page (and add the host to `next.config.ts` if remote).

### Quote → Google Sheet (optional)
Create a Google Apps Script web app that does `SpreadsheetApp...appendRow([...])` from the
POSTed JSON, deploy it as "Anyone", and put its URL in `QUOTE_SHEET_WEBHOOK_URL`.

### Snipcart B2B note
Snipcart validates cart prices by crawling the product URL. With per-account pricing the
crawled (guest) page has no price, so for production you'll either enable Snipcart's
server-side price validation webhook or graduate the cart to Stripe/Medusa (see roadmap).
Test mode is fine for the pilot.

---

## Deploy (Vercel)
1. Push this folder to its **own GitHub repo** (see below).
2. Import into Vercel; set the env vars from `.env.local.example`.
3. Set `NEXT_PUBLIC_SITE_URL` to the deployed URL so email links resolve.

## Moving to a dedicated repo
This project currently lives inside the `shopify_product_management` repo under
`button-pilot/` (the working session could only push there). To split it out:

```bash
# from the shopify_product_management checkout, on the feature branch:
git subtree split --prefix=button-pilot -b button-pilot-only
# create an empty GitHub repo, then:
git push <new-repo-url> button-pilot-only:main
```
Or simply copy the `button-pilot/` directory into a fresh repo — it's fully self-contained.

---

## Roadmap (post-pilot)
- **Phase 2:** live checkout, tax/shipping, order emails.
- **Phase 3:** move products to a headless CMS (reuse the Zod schema); full catalog + filters.
- **Phase 4:** self-serve trade-account application + admin approve/reject + customers DB.
- **Phase 5:** graduate cart to Medusa (B2B price lists); add a B2C surface with retail pricing.

## Scripts
- `npm run dev` — local dev server
- `npm run build` — production build (validates all product JSON)
- `npm run typecheck` — TypeScript check
- `npm run lint` — Next lint
