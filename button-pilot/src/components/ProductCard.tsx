import Link from "next/link";
import type { Product, Tier } from "@/lib/schema";
import { ButtonSwatch } from "./ButtonSwatch";
import { resolvePrice, formatPrice } from "@/lib/pricing";

/**
 * Catalog/home card. Renders the first variant as an SVG swatch. Price shows
 * only when a tier is passed (logged-in trade account); guests see a neutral
 * "Trade pricing" badge instead — no numbers in the guest payload.
 */
export function ProductCard({
  product,
  tier,
}: {
  product: Product;
  tier: Tier | null;
}) {
  const hero = product.variants[0];
  // For logged-in accounts, show their "from" price at MOQ; for guests, nothing.
  const priced = tier ? resolvePrice(hero, tier, product.moq) : null;

  return (
    <Link
      href={`/catalog/${product.slug}`}
      className="group rounded-xl border border-stone-200 bg-white p-5 transition hover:border-accent hover:shadow-sm"
    >
      <div className="flex items-center justify-center rounded-lg bg-stone-50 py-6">
        <ButtonSwatch
          colorHex={hero.colorHex}
          holeType={product.holeType}
          material={product.material}
          size={120}
          label={product.name}
        />
      </div>
      <div className="mt-4">
        <h3 className="font-medium group-hover:text-accent">{product.name}</h3>
        <p className="mt-1 text-sm text-stone-500 capitalize">
          {product.material} · {product.holeType} · from {Math.min(...product.variants.map((v) => v.sizeLigne))}L
        </p>
        <div className="mt-3 text-sm">
          {priced ? (
            <span className="font-medium">
              from {formatPrice(priced.unitPrice, priced.currency)}
              <span className="text-stone-400"> / {product.unit}</span>
            </span>
          ) : (
            <span className="inline-block rounded bg-stone-100 px-2 py-0.5 text-xs text-stone-500">
              {tier ? "" : "Trade pricing — sign in"}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
