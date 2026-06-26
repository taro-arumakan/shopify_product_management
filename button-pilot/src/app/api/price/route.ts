import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { currentTier } from "@/lib/auth";
import { getProductBySlug, getVariantBySku } from "@/lib/products";
import { resolvePrice } from "@/lib/pricing";

/**
 * Gated price resolution for interactive quantity changes.
 *
 * Middleware already 401s guests before this runs, but we re-check the tier
 * here too (defense in depth) — pricing is NEVER computed without an
 * authenticated tier. The response carries only this account's own price.
 */
const Body = z.object({
  slug: z.string(),
  variantSku: z.string(),
  qty: z.number().int().positive(),
});

export async function POST(req: NextRequest): Promise<NextResponse> {
  const tier = await currentTier();
  if (!tier) {
    return NextResponse.json({ error: "Trade login required." }, { status: 401 });
  }

  const parsed = Body.safeParse(await req.json().catch(() => null));
  if (!parsed.success) {
    return NextResponse.json({ error: "Bad request." }, { status: 400 });
  }

  const { slug, variantSku, qty } = parsed.data;
  const product = getProductBySlug(slug);
  const variant = product && getVariantBySku(product, variantSku);
  if (!product || !variant) {
    return NextResponse.json({ error: "Not found." }, { status: 404 });
  }

  const price = resolvePrice(variant, tier, qty);
  if (!price) {
    return NextResponse.json({ error: "Trade login required." }, { status: 401 });
  }

  return NextResponse.json({
    unitPrice: price.unitPrice,
    currency: price.currency,
    appliedMinQty: price.appliedMinQty,
    lineTotal: Number((price.unitPrice * qty).toFixed(2)),
    unit: product.unit,
  });
}
