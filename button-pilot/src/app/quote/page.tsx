import type { Metadata } from "next";
import { QuoteForm } from "@/components/QuoteForm";

export const metadata: Metadata = {
  title: "Request a quote",
  description:
    "Request wholesale pricing, samples, or a custom button production quote for your apparel brand.",
};

export default async function QuotePage({
  searchParams,
}: {
  searchParams: Promise<{ sku?: string; qty?: string }>;
}) {
  const { sku, qty } = await searchParams;

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="font-serif text-4xl tracking-tight">Request a quote</h1>
      <p className="mt-2 text-stone-600">
        Tell us what you're making. We'll reply with trade pricing, sample options, and
        lead times — and set up a trade account if you don't have one yet.
      </p>

      <div className="mt-8 rounded-xl border border-stone-200 bg-white p-6">
        <QuoteForm defaultSku={sku} defaultQty={qty} />
      </div>

      <p className="mt-6 text-sm text-stone-500">
        Prefer email? Reach us directly and we'll route your request to the right person.
      </p>
    </div>
  );
}
