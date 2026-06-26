import Link from "next/link";
import type { Product, Tier } from "@/lib/schema";
import { ButtonSwatch } from "./ButtonSwatch";
import { resolvePrice, formatPrice } from "@/lib/pricing";

/**
 * Flat, gridline-separated catalog cell (FreshService-style). The parent grid
 * draws its top + left edge; each cell draws its right + bottom edge, so the
 * cards tile into one continuous grid with no gaps.
 *
 * Price shows only when a `tier` is passed (logged-in trade account); guests
 * see a neutral "Trade pricing" tag — no numbers ever enter the guest payload.
 */
export function ProductCard({
  product,
  tier,
}: {
  product: Product;
  tier: Tier | null;
}) {
  const hero = product.variants[0];
  const priced = tier ? resolvePrice(hero, tier, product.moq) : null;
  const minLigne = Math.min(...product.variants.map((v) => v.sizeLigne));

  return (
    <Link
      href={`/catalog/${product.slug}`}
      className="group flex flex-col border-r border-b border-line bg-surface transition-colors hover:bg-background"
    >
      <div className="flex aspect-square items-center justify-center overflow-hidden p-6">
        <ButtonSwatch
          colorHex={hero.colorHex}
          holeType={product.holeType}
          material={product.material}
          size={150}
          label={product.name}
          className="transition-transform duration-300 ease-out group-hover:scale-105"
        />
      </div>
      <div className="border-t border-line px-4 py-3">
        <h3 className="font-serif text-lg leading-tight text-foreground">
          {product.name}
        </h3>
        <p className="mt-1 text-xs uppercase tracking-wide text-stone-500">
          {product.material} · {product.holeType} · from {minLigne}L
        </p>
        <div className="mt-2 text-sm">
          {priced ? (
            <span className="font-medium text-foreground">
              from {formatPrice(priced.unitPrice, priced.currency)}
              <span className="text-stone-400"> / {product.unit}</span>
            </span>
          ) : (
            <span className="text-xs text-stone-500">
              {tier ? " " : "Trade pricing — sign in"}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
