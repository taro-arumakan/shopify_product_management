import type { Metadata } from "next";
import Link from "next/link";
import { auth } from "@/lib/auth";
import { getAllProducts } from "@/lib/products";
import { ProductCard } from "@/components/ProductCard";

export const metadata: Metadata = {
  title: "Catalog",
  description:
    "Garment button catalog — corozo, urea resin, mother-of-pearl, and metal buttons for apparel makers.",
};

export default async function CatalogPage() {
  const session = await auth();
  const tier = session?.user.tier ?? null;
  const products = getAllProducts();

  return (
    <div className="mx-auto max-w-6xl px-4 py-12">
      <h1 className="text-3xl font-semibold tracking-tight">Button catalog</h1>
      <p className="mt-2 max-w-2xl text-stone-600">
        Our pilot range of garment buttons. {tier
          ? "Showing your trade pricing."
          : "Sign in for wholesale pricing and ordering."}
      </p>

      {!tier && (
        <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          You're browsing as a guest — prices are hidden.{" "}
          <Link href="/login" className="font-medium underline">
            Trade login
          </Link>{" "}
          to see pricing.
        </div>
      )}

      <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {products.map((p) => (
          <ProductCard key={p.slug} product={p} tier={tier} />
        ))}
      </div>
    </div>
  );
}
