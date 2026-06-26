import type { Metadata } from "next";
import Link from "next/link";
import Script from "next/script";
import { auth } from "@/lib/auth";
import "./globals.css";

const SNIPCART_VERSION = "3.7.3";

export const metadata: Metadata = {
  title: {
    default: "Atelier Buttons — Trade Button Supply",
    template: "%s · Atelier Buttons",
  },
  description:
    "Garment buttons for apparel makers — corozo, urea, shell, and metal. Wholesale trade pricing and custom production.",
};

export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const session = await auth();
  const account = session?.user;
  const snipcartKey = process.env.NEXT_PUBLIC_SNIPCART_KEY;

  return (
    <html lang="en">
      {snipcartKey && (
        <head>
          <link rel="preconnect" href="https://app.snipcart.com" />
          <link
            rel="stylesheet"
            href={`https://cdn.snipcart.com/themes/v${SNIPCART_VERSION}/default/snipcart.css`}
          />
        </head>
      )}
      <body className="min-h-screen flex flex-col">
        <header className="border-b border-stone-200 bg-white/80 backdrop-blur sticky top-0 z-10">
          <nav className="mx-auto max-w-6xl px-4 h-16 flex items-center justify-between">
            <Link href="/" className="font-semibold tracking-tight text-lg">
              Atelier<span className="text-accent">Buttons</span>
            </Link>
            <div className="flex items-center gap-6 text-sm">
              <Link href="/catalog" className="hover:text-accent">
                Catalog
              </Link>
              <Link href="/quote" className="hover:text-accent">
                Request a quote
              </Link>
              {snipcartKey && account && (
                <button className="snipcart-checkout hover:text-accent">
                  Cart (<span className="snipcart-items-count">0</span>)
                </button>
              )}
              {account ? (
                <span className="flex items-center gap-2 text-stone-500">
                  <span className="hidden sm:inline">
                    {account.companyName ?? account.email}
                  </span>
                  <span className="rounded bg-stone-100 px-2 py-0.5 text-xs uppercase tracking-wide">
                    {account.tier?.replace("tier_", "") ?? "trade"}
                  </span>
                  <form action="/api/auth/logout" method="post">
                    <button type="submit" className="text-xs underline hover:text-accent">
                      Sign out
                    </button>
                  </form>
                </span>
              ) : (
                <Link
                  href="/login"
                  className="rounded-md bg-accent px-3 py-1.5 text-white hover:opacity-90"
                >
                  Trade login
                </Link>
              )}
            </div>
          </nav>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="border-t border-stone-200 mt-16">
          <div className="mx-auto max-w-6xl px-4 py-8 text-sm text-stone-500 flex flex-col sm:flex-row justify-between gap-2">
            <span>© Atelier Buttons — B2B trade supply (pilot).</span>
            <span>
              Product visuals are representative mockups; physical samples available on
              request.
            </span>
          </div>
        </footer>

        {snipcartKey && (
          <>
            <div hidden id="snipcart" data-api-key={snipcartKey} data-config-modal-style="side" />
            <Script
              src={`https://cdn.snipcart.com/themes/v${SNIPCART_VERSION}/default/snipcart.js`}
              strategy="afterInteractive"
            />
          </>
        )}
      </body>
    </html>
  );
}
