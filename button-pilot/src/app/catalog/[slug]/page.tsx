import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { auth } from "@/lib/auth";
import { baseUrl } from "@/lib/url";
import { getAllProducts, getProductBySlug } from "@/lib/products";
import { ButtonSwatch } from "@/components/ButtonSwatch";
import { PriceBlock } from "@/components/PriceBlock";

export function generateStaticParams() {
  return getAllProducts().map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const product = getProductBySlug(slug);
  if (!product) return {};
  return {
    title: product.seo.title ?? product.name,
    description: product.seo.description ?? product.shortDescription,
  };
}

function Spec({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-stone-100 py-2 text-sm">
      <dt className="text-stone-500">{label}</dt>
      <dd className="font-medium text-right">{value}</dd>
    </div>
  );
}

export default async function ProductPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const product = getProductBySlug(slug);
  if (!product) notFound();

  const session = await auth();
  const tier = session?.user.tier ?? null;
  const productUrl = `${await baseUrl()}/catalog/${product.slug}`;

  const sizes = [...new Set(product.variants.map((v) => v.sizeLigne))].sort(
    (a, b) => a - b,
  );

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <nav className="text-sm text-stone-500">
        <Link href="/catalog" className="hover:text-accent">
          Catalog
        </Link>{" "}
        / <span className="text-stone-700">{product.name}</span>
      </nav>

      <div className="mt-6 grid gap-10 lg:grid-cols-2">
        {/* Gallery + specs */}
        <div>
          <div className="flex items-center justify-center rounded-2xl bg-stone-50 py-12">
            <ButtonSwatch
              colorHex={product.variants[0].colorHex}
              holeType={product.holeType}
              material={product.material}
              size={240}
              label={product.name}
            />
          </div>
          <div className="mt-4 flex flex-wrap gap-3">
            {product.variants.map((v) => (
              <div
                key={v.variantSku}
                className="flex flex-col items-center rounded-lg border border-stone-200 p-2"
                title={`${v.sizeLigne}L · ${v.finish}`}
              >
                <ButtonSwatch
                  colorHex={v.colorHex}
                  holeType={product.holeType}
                  material={product.material}
                  size={48}
                />
                <span className="mt-1 text-[11px] text-stone-500">
                  {v.sizeLigne}L
                </span>
              </div>
            ))}
          </div>

          <h2 className="mt-8 text-lg font-semibold">Specifications</h2>
          <dl className="mt-2">
            <Spec label="Material" value={cap(product.material)} />
            <Spec label="Attachment" value={product.holeType} />
            <Spec
              label="Sizes"
              value={sizes.map((s) => `${s}L`).join(", ")}
            />
            <Spec
              label="Applications"
              value={product.application.map(cap).join(", ") || "—"}
            />
            <Spec label="MOQ" value={`${product.moq} ${product.unit}`} />
            <Spec label="Lead time" value={`~${product.leadTimeDays} days`} />
            {product.countryOfOrigin && (
              <Spec label="Origin" value={product.countryOfOrigin} />
            )}
            {product.certifications.length > 0 && (
              <Spec label="Certifications" value={product.certifications.join(", ")} />
            )}
          </dl>
          {product.careNotes && (
            <p className="mt-4 text-sm text-stone-500">
              <span className="font-medium text-stone-700">Care:</span>{" "}
              {product.careNotes}
            </p>
          )}
        </div>

        {/* Title, copy, pricing/order */}
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">{product.name}</h1>
          <p className="mt-1 text-sm uppercase tracking-wide text-stone-400">
            {product.sku}
          </p>
          <p className="mt-4 text-stone-600">{product.shortDescription}</p>
          <p className="mt-3 text-sm leading-relaxed text-stone-600">
            {product.longDescription}
          </p>

          <div className="mt-8">
            <PriceBlock product={product} tier={tier} productUrl={productUrl} />
          </div>

          <p className="mt-4 text-xs text-stone-400">
            Visuals are representative mockups; physical samples available on request.
          </p>
        </div>
      </div>
    </div>
  );
}

function cap(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}
