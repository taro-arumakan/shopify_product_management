import Link from "next/link";
import { auth } from "@/lib/auth";
import { getAllProducts } from "@/lib/products";
import { ProductCard } from "@/components/ProductCard";
import { Logo } from "@/components/Logo";

export default async function HomePage() {
  const session = await auth();
  const tier = session?.user.tier ?? null;
  const products = getAllProducts();

  return (
    <div>
      {/* Hero */}
      <section className="border-b border-line bg-surface">
        <div className="mx-auto grid max-w-6xl items-center gap-10 px-4 py-20 md:grid-cols-[1.3fr_1fr]">
          <div>
            <p className="font-serif text-sm uppercase tracking-[0.2em] text-accent">
              Heritage workwear buttons · Made in Japan
            </p>
            <h1 className="mt-4 max-w-2xl font-serif text-4xl leading-tight tracking-tight sm:text-5xl">
              Buttons built for hard wear, supplied for the trade.
            </h1>
            <p className="mt-4 max-w-xl text-lg text-stone-600">
              Tack, jumper-coat, overall, and engraved work buttons for apparel makers.
              Wholesale tiered pricing, low minimums, and custom face stamping.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/catalog"
                className="rounded-md bg-foreground px-5 py-3 font-medium text-background hover:bg-accent"
              >
                Browse the catalog
              </Link>
              <Link
                href="/quote"
                className="rounded-md border border-foreground/30 px-5 py-3 font-medium hover:border-accent hover:text-accent"
              >
                Request a quote
              </Link>
            </div>
          </div>
          <div className="hidden justify-center md:flex">
            <Logo variant="full" className="w-full max-w-xs text-foreground" />
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
              d: "Custom face stamping, logo tooling, and certified, nickel-safe finishes.",
            },
          ].map((b) => (
            <div key={b.t}>
              <h3 className="font-serif text-xl">{b.t}</h3>
              <p className="mt-1 text-sm text-stone-600">{b.d}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Featured products */}
      <section className="mx-auto max-w-6xl px-4 pb-20">
        <div className="flex items-end justify-between">
          <h2 className="font-serif text-3xl tracking-tight">The pilot range</h2>
          <Link href="/catalog" className="text-sm text-accent hover:underline">
            View all →
          </Link>
        </div>
        <div className="mt-6 grid grid-cols-2 border-t border-l border-line lg:grid-cols-4">
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
