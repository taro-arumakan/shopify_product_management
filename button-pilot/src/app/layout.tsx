import type { Metadata } from "next";
import Link from "next/link";
import Script from "next/script";
import { EB_Garamond } from "next/font/google";
import { auth } from "@/lib/auth";
import { Logo } from "@/components/Logo";
import "./globals.css";

const SNIPCART_VERSION = "3.7.3";

// Serif close to the logo's "BUTTON WORKS" — used for headings/brand labels.
const display = EB_Garamond({
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Hammond Button Works — Trade Button Supply",
    template: "%s · Hammond Button Works",
  },
  description:
    "Heritage workwear buttons for apparel makers — tack, jumper-coat, overall, and engraved work buttons. Made in Japan. Wholesale trade pricing and custom production.",
};

export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const session = await auth();
  const account = session?.user;
  const snipcartKey = process.env.NEXT_PUBLIC_SNIPCART_KEY;

  return (
    <html lang="en" className={display.variable}>
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
        <header className="border-b border-line bg-surface/85 backdrop-blur sticky top-0 z-10">
          <nav className="mx-auto max-w-6xl px-4 h-16 flex items-center justify-between">
            <Link href="/" aria-label="Hammond Button Works — home">
              <Logo variant="compact" className="h-7 w-auto text-foreground" />
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
                  <span className="rounded bg-stone-200/60 px-2 py-0.5 text-xs uppercase tracking-wide">
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
                  className="rounded-md bg-foreground px-3 py-1.5 text-background hover:bg-accent"
                >
                  Trade login
                </Link>
              )}
            </div>
          </nav>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="border-t border-line mt-16">
          <div className="mx-auto max-w-6xl px-4 py-10 text-sm text-stone-500 flex flex-col sm:flex-row items-start justify-between gap-6">
            <div className="flex items-center gap-4">
              <Logo variant="stamp" className="h-14 w-14 text-foreground shrink-0" />
              <div>
                <p className="font-serif text-base text-foreground">Hammond Button Works</p>
                <p className="mt-1">© Hammond Button Works — B2B trade supply (pilot).</p>
              </div>
            </div>
            <span className="max-w-xs sm:text-right">
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
