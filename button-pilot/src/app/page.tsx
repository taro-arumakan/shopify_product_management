import Link from "next/link";
import { auth } from "@/lib/auth";
import { getAllProducts } from "@/lib/products";
import { ProductCard } from "@/components/ProductCard";

export default async function HomePage() {
  const session = await auth();
  const tier = session?.user.tier ?? null;
  const products = getAllProducts();

  return (
    <div>
      {/* Hero */}
      <section className="border-b border-stone-200 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-20">
          <p className="text-sm font-medium uppercase tracking-wider text-accent">
            B2B button supply
          </p>
          <h1 className="mt-3 max-w-2xl text-4xl font-semibold tracking-tight sm:text-5xl">
            Garment buttons, supplied for the trade.
          </h1>
          <p className="mt-4 max-w-xl text-lg text-stone-600">
            Corozo, urea, mother-of-pearl, and metal buttons for apparel makers.
            Wholesale tiered pricing, low minimums, and color-matched production runs.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/catalog"
              className="rounded-md bg-accent px-5 py-3 font-medium text-white hover:opacity-90"
            >
              Browse the catalog
            </Link>
            <Link
              href="/quote"
              className="rounded-md border border-stone-300 px-5 py-3 font-medium hover:border-accent"
            >
              Request a quote
            </Link>
          </div>
        </div>
      </section>

      {/* Value props */}
      <section className="mx-auto max-w-6xl px-4 py-14">
        <div className="grid gap-8 sm:grid-cols-3">
          {[
            {
              t: "Trade pricing",
              d: "Tiered wholesale pricing with volume breaks. Sign in to see your rates.",
            },
            {
              t: "Low minimums",
              d: "Start from small gross quantities for sampling, scale to production lots.",
            },
            {
              t: "Made to spec",
              d: "Color-matching, custom engraving, and certified materials (OEKO-TEX, REACH).",
            },
          ].map((b) => (
            <div key={b.t}>
              <h3 className="font-semibold">{b.t}</h3>
              <p className="mt-1 text-sm text-stone-600">{b.d}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Featured products */}
      <section className="mx-auto max-w-6xl px-4 pb-20">
        <div className="flex items-end justify-between">
          <h2 className="text-2xl font-semibold tracking-tight">Pilot collection</h2>
          <Link href="/catalog" className="text-sm text-accent hover:underline">
            View all →
          </Link>
        </div>
        <div className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {products.map((p) => (
            <ProductCard key={p.slug} product={p} tier={tier} />
          ))}
        </div>
        {!tier && (
          <p className="mt-6 text-sm text-stone-500">
            Prices are visible to approved trade accounts.{" "}
            <Link href="/login" className="underline">
              Trade login
            </Link>{" "}
            or{" "}
            <Link href="/quote" className="underline">
              request access
            </Link>
            .
          </p>
        )}
      </section>
    </div>
  );
}
