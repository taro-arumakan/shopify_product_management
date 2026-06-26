"use client";

import { useEffect, useState } from "react";
import { ButtonSwatch } from "./ButtonSwatch";
import type { HoleType, Material } from "@/lib/schema";

/**
 * Logged-in ordering panel. Prices are fetched from the gated /api/price
 * endpoint (server-authoritative, tier-aware) on every variant/quantity change,
 * so the client never holds the full price ladder — only the single quote it
 * asked for. The add-to-cart button is wired with the resolved unit price.
 */

type VariantView = {
  variantSku: string;
  sizeLigne: number;
  sizeMm: number;
  finish: string;
  colorHex: string;
  inStockSample: boolean;
};

type Props = {
  productName: string;
  slug: string;
  unit: string;
  moq: number;
  material: Material;
  holeType: HoleType;
  variants: VariantView[];
  productUrl: string;
  snipcartEnabled: boolean;
};

type Quote = {
  unitPrice: number;
  currency: string;
  appliedMinQty: number;
  lineTotal: number;
  unit: string;
};

function money(n: number, currency: string) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(n);
}

export function TradeOrderPanel({
  productName,
  slug,
  unit,
  moq,
  material,
  holeType,
  variants,
  productUrl,
  snipcartEnabled,
}: Props) {
  const [sku, setSku] = useState(variants[0].variantSku);
  const [qty, setQty] = useState(moq);
  const [quote, setQuote] = useState<Quote | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selected = variants.find((v) => v.variantSku === sku)!;

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    fetch("/api/price", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ slug, variantSku: sku, qty: Math.max(moq, qty) }),
    })
      .then(async (r) => {
        if (!r.ok) throw new Error((await r.json()).error ?? "Pricing error");
        return r.json();
      })
      .then((data: Quote) => active && setQuote(data))
      .catch((e) => active && setError(e.message))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [slug, sku, qty, moq]);

  return (
    <div className="rounded-xl border border-stone-200 bg-white p-6">
      <h2 className="text-lg font-semibold">Trade order</h2>

      {/* Variant (size × finish) selector */}
      <fieldset className="mt-4">
        <legend className="text-sm font-medium text-stone-700">Size &amp; finish</legend>
        <div className="mt-2 flex flex-wrap gap-2">
          {variants.map((v) => {
            const isSel = v.variantSku === sku;
            return (
              <button
                key={v.variantSku}
                type="button"
                onClick={() => setSku(v.variantSku)}
                className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm transition ${
                  isSel
                    ? "border-accent ring-1 ring-accent"
                    : "border-stone-200 hover:border-stone-300"
                }`}
              >
                <ButtonSwatch
                  colorHex={v.colorHex}
                  holeType={holeType}
                  material={material}
                  size={28}
                />
                <span>
                  {v.sizeLigne}L · {v.finish}
                </span>
              </button>
            );
          })}
        </div>
      </fieldset>

      {/* Quantity */}
      <div className="mt-5">
        <label htmlFor="qty" className="text-sm font-medium text-stone-700">
          Quantity ({unit}) · MOQ {moq}
        </label>
        <div className="mt-2 flex items-center gap-2">
          <button
            type="button"
            onClick={() => setQty((q) => Math.max(moq, q - 1))}
            className="h-9 w-9 rounded-md border border-stone-300 text-lg leading-none"
            aria-label="Decrease quantity"
          >
            −
          </button>
          <input
            id="qty"
            type="number"
            min={moq}
            value={qty}
            onChange={(e) => setQty(Math.max(moq, Number(e.target.value) || moq))}
            className="h-9 w-24 rounded-md border border-stone-300 px-2 text-center"
          />
          <button
            type="button"
            onClick={() => setQty((q) => q + 1)}
            className="h-9 w-9 rounded-md border border-stone-300 text-lg leading-none"
            aria-label="Increase quantity"
          >
            +
          </button>
        </div>
      </div>

      {/* Price */}
      <div className="mt-5 rounded-lg bg-stone-50 p-4">
        {error ? (
          <p className="text-sm text-red-600">{error}</p>
        ) : loading || !quote ? (
          <p className="text-sm text-stone-400">Calculating trade price…</p>
        ) : (
          <>
            <div className="flex items-baseline justify-between">
              <span className="text-sm text-stone-600">Unit price</span>
              <span className="text-xl font-semibold">
                {money(quote.unitPrice, quote.currency)}
                <span className="text-sm font-normal text-stone-400"> / {unit}</span>
              </span>
            </div>
            <div className="mt-1 flex items-baseline justify-between">
              <span className="text-sm text-stone-600">Line total ({qty} {unit})</span>
              <span className="font-medium">{money(quote.lineTotal, quote.currency)}</span>
            </div>
            <p className="mt-2 text-xs text-stone-400">
              Volume price applied at {quote.appliedMinQty}+ {unit}.
            </p>
          </>
        )}
      </div>

      {/* Add to cart (Snipcart) */}
      {snipcartEnabled && quote ? (
        <button
          type="button"
          className="snipcart-add-item mt-5 w-full rounded-md bg-accent px-4 py-2.5 font-medium text-white hover:opacity-90 disabled:opacity-50"
          disabled={loading}
          data-item-id={selected.variantSku}
          data-item-name={`${productName} — ${selected.sizeLigne}L ${selected.finish}`}
          data-item-price={quote.unitPrice.toFixed(2)}
          data-item-url={productUrl}
          data-item-quantity={String(qty)}
          data-item-min-quantity={String(moq)}
          data-item-custom1-name="Unit"
          data-item-custom1-value={unit}
        >
          Add to cart
        </button>
      ) : (
        <button
          type="button"
          disabled
          className="mt-5 w-full rounded-md bg-stone-200 px-4 py-2.5 font-medium text-stone-500"
          title="Set NEXT_PUBLIC_SNIPCART_KEY to enable checkout"
        >
          {snipcartEnabled ? "Add to cart" : "Cart not configured (test mode)"}
        </button>
      )}

      <a
        href={`/quote?sku=${encodeURIComponent(sku)}&qty=${qty}`}
        className="mt-3 block text-center text-sm text-stone-600 underline"
      >
        Prefer a custom quote? Request one →
      </a>
    </div>
  );
}
