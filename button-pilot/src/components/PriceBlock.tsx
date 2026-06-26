import Link from "next/link";
import type { Product, Tier } from "@/lib/schema";
import { TradeOrderPanel } from "./TradeOrderPanel";

/**
 * Server component that decides what a viewer may see:
 *  - Guest  → a "sign in for trade pricing" CTA. No prices reach the payload.
 *  - Trade  → the interactive ordering panel (prices fetched server-side).
 */
export function PriceBlock({
  product,
  tier,
  productUrl,
}: {
  product: Product;
  tier: Tier | null;
  productUrl: string;
}) {
  if (!tier) {
    return (
      <div className="rounded-xl border border-dashed border-stone-300 bg-stone-50 p-6">
        <h2 className="text-lg font-semibold">Trade pricing</h2>
        <p className="mt-2 text-sm text-stone-600">
          Wholesale pricing and ordering are available to approved trade accounts.
          Sign in to see tiered pricing for this style, or request access.
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link
            href="/login"
            className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:opacity-90"
          >
            Trade login
          </Link>
          <Link
            href={`/quote?sku=${encodeURIComponent(product.variants[0].variantSku)}`}
            className="rounded-md border border-stone-300 px-4 py-2 text-sm font-medium hover:border-accent"
          >
            Request trade access
          </Link>
        </div>
        <p className="mt-4 text-xs text-stone-500">
          MOQ {product.moq} {product.unit} · lead time ~{product.leadTimeDays} days.
        </p>
      </div>
    );
  }

  const snipcartEnabled = Boolean(process.env.NEXT_PUBLIC_SNIPCART_KEY);

  return (
    <TradeOrderPanel
      productName={product.name}
      slug={product.slug}
      unit={product.unit}
      moq={product.moq}
      material={product.material}
      holeType={product.holeType}
      productUrl={productUrl}
      snipcartEnabled={snipcartEnabled}
      variants={product.variants.map((v) => ({
        variantSku: v.variantSku,
        sizeLigne: v.sizeLigne,
        sizeMm: v.sizeMm,
        finish: v.finish,
        colorHex: v.colorHex,
        inStockSample: v.inStockSample,
      }))}
    />
  );
}
