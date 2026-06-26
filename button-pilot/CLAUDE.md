# Hammond Button Works — Project Guide (for Claude Code)

A from-scratch **B2B pilot storefront** for **Hammond Button Works** — a maker of
**heritage workwear buttons** (tack / jeans, rigid-eye jumper-coat, doughnut overall,
engraved work buttons; "made in Japan" identity). The pilot showcases 4 products and
validates three B2B fundamentals before a full build.

## Lineage (read this first)
- Originally built generically as "Atelier Buttons", then **rebranded to Hammond Button
  Works** and re-themed to heritage workwear buttons.
- This folder was **copied out of** the `button-pilot/` directory of the
  `shopify_product_management` repo (branch `claude/button-business-website-4cyd47`) and is
  meant to become **its own standalone repo**. It has no git history of its own yet — run
  `git init` (or it may inherit the parent's; detach if so).
- It is **self-contained** — no dependency on the parent Python repo.

## Stack
Next.js 15 (App Router) · React 19 · TypeScript · Tailwind CSS v4 · Zod. **No database.**
Auth is a self-rolled signed-token magic link (Web Crypto HMAC). Cart is **Snipcart**
(test mode), behind a swappable abstraction. Email via **Resend** (console fallback in dev).
Deploy target: **Vercel**.

## Run / build / verify
```bash
npm install
cp .env.local.example .env.local       # set AUTH_SECRET: openssl rand -base64 32
npm run dev                            # http://localhost:3000
npm run build                          # validates all product JSON via Zod (fails on bad data)
npm run typecheck
```
Demo trade accounts (see `src/lib/allowlist.ts`), magic link prints to the **server console**
when no Resend key is set:
- `buyer@example-standard.com` (standard tier)
- `buyer@example-volume.com` (volume tier)
- `buyer@example-partner.com` (partner tier)

## Critical invariants — DO NOT BREAK
1. **Guests must never receive price data.** Prices resolve **server-side** in
   `src/lib/pricing.ts` (marked `import "server-only"`; returns `null` for guests).
   `ProductCard`/`PriceBlock` only render prices when a `tier` is present; `/api/price`
   returns **401** for guests via `src/middleware.ts`. Guard check: a guest's
   `/catalog` HTML must contain **0** price strings. (A price leak was found and fixed
   once already — keep it fixed.)
2. **Catalog & product pages are public for SEO** — only the *prices* are gated, not the
   pages. Don't move catalog behind auth.
3. **Product JSON is the source of truth and is Zod-validated at build.** Bad data
   (missing SKU, non-ascending price breaks, bad hex) **fails `next build`** on purpose.
4. The **logo wordmark is an approximation** of a custom typeface (`src/components/Logo.tsx`,
   geometric font stack + dot-in-`o` accent). Swap in the real vector/font when the owner
   provides it.

## Architecture & key files
| Concern | File |
|---|---|
| Zod schema (single source of truth; tiers, `tack` holeType) | `src/lib/schema.ts` |
| Product loader + build-time validation | `src/lib/products.ts` |
| Server-only tier/quantity price resolver | `src/lib/pricing.ts` |
| Signed magic-link + session tokens (Web Crypto) | `src/lib/session.ts` |
| `auth()` / session cookie helpers | `src/lib/auth.ts` |
| Approved trade accounts (+ `TRADE_ALLOWLIST` env) | `src/lib/allowlist.ts` |
| Edge gate for `/api/price` + `/account` | `src/middleware.ts` |
| Swappable cart (Snipcart adapter) | `src/lib/cart.ts` |
| Resend wrapper (console fallback) | `src/lib/email.ts` |
| Rate limit / base URL helpers | `src/lib/ratelimit.ts`, `src/lib/url.ts` |
| SVG logo (compact/full/stamp) | `src/components/Logo.tsx` |
| SVG button render (incl. `tack` stud) | `src/components/ButtonSwatch.tsx` |
| Grid cell / price block / order panel / quote form | `src/components/{ProductCard,PriceBlock,TradeOrderPanel,QuoteForm}.tsx` |
| Pages | `src/app/{page,catalog,catalog/[slug],quote,login}` |
| APIs | `src/app/api/{price,quote,auth/verify,auth/logout}/route.ts` + `app/login/actions.ts` |
| 4 products | `content/products/*.json` |
| AI hero prompts | `content/image-prompts.md` |

**Data model:** product = a button *style*; variants = size (ligne) × finish. Tiers:
`tier_standard` / `tier_volume` / `tier_partner`, each with ascending quantity breaks.
`unit` is `gross` (144). `holeType` includes `tack` for rivet-set jeans/work buttons.

## Branding / design system
Heritage-minimal: background cream `#f3efe6`, ink `#1a1714`, brass accent `#8a6d3b`
(`src/app/globals.css`). Serif = **EB Garamond** via `next/font` (`--font-display`),
used for headings (`font-serif`). A **double-line frame** motif (`.frame-double`) mirrors
the logo. Product listing is a **flat, gridline-separated grid** (FreshService-style):
container draws top/left edge, each cell draws right/bottom. Footer carries the circular
**Made-in-Japan stamp**.

## Decisions made this session
- **Domain:** chose **`hammondbutton.works`** (the `.works` TLD reads as the brand name).
  Recommended also grabbing `hammondbuttonworks.com` as a redirect.
- **DNS/host:** keep DNS on **Route 53** (owner already uses it for `sniarti.fi`); deploy on
  **Vercel**; set `NEXT_PUBLIC_SITE_URL=https://hammondbutton.works`. Did **not** recommend
  switching to Cloudflare for one domain (Vercel already provides CDN/SSL/DDoS).
- **Cart:** Snipcart in test mode. NOTE: Snipcart validates cart price by crawling the
  product URL, which has no price for guests — production B2B pricing needs Snipcart's
  server-side price-validation webhook, or graduate to Stripe/Medusa.

## Open items / next steps
- ⚠️ **Trademark check:** an established Japanese brand **"Button Works" (ボタンワークス)**
  exists in the *same* workwear-button niche. Verify "Hammond Button Works" is clear before
  committing the name to packaging/hardware.
- Initialize this as its own git repo and push to a dedicated remote.
- Replace placeholder product specs/prices with the owner's real data.
- Pixel-perfect logo once the original vector/font is supplied.
- Photoreal hero images (prompts ready in `content/image-prompts.md`); save to
  `public/images/products/<variantSku>.jpg` and wire via `next/image`.
- Optional `DEPLOY.md` (Route 53 + Vercel records) — offered, not yet written.

## Env vars (see `.env.local.example`)
`AUTH_SECRET` (required) · `NEXT_PUBLIC_SITE_URL` · `RESEND_API_KEY` / `EMAIL_FROM` /
`QUOTE_INBOX` · `TRADE_ALLOWLIST` (`email|tier|Company`) · `NEXT_PUBLIC_SNIPCART_KEY` /
`NEXT_PUBLIC_CART_PROVIDER` · `QUOTE_SHEET_WEBHOOK_URL`.

## Post-pilot roadmap
Phase 2 live checkout + tax/shipping/order emails · Phase 3 headless CMS (reuse the Zod
schema) + full catalog/filters · Phase 4 self-serve trade-account application + admin
approval + customers DB · Phase 5 graduate cart to Medusa (B2B price lists) + B2C surface.
