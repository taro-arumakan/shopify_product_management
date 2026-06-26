import { NextRequest, NextResponse } from "next/server";
import { SESSION_COOKIE, verifyToken } from "@/lib/session";

/**
 * Server-side gate. Runs on the Edge before any gated route renders.
 *
 * Catalog and product pages are intentionally PUBLIC (SEO), but they never
 * contain prices for guests — pricing is resolved server-side per tier and the
 * price-bearing API is gated here. Guests calling it get 401; there is no
 * client payload to "unlock". A reserved /account area is gated for future use.
 */
export async function middleware(req: NextRequest) {
  const token = req.cookies.get(SESSION_COOKIE)?.value;
  const session = await verifyToken(token, "session");

  if (session) return NextResponse.next();

  const { pathname, search } = req.nextUrl;

  if (pathname.startsWith("/api/")) {
    return NextResponse.json(
      { error: "Trade login required." },
      { status: 401 },
    );
  }

  const loginUrl = new URL("/login", req.url);
  loginUrl.searchParams.set("next", pathname + search);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  // Gate the price resolution API and the reserved account area. Catalog,
  // product, marketing, /login, /quote, and /api/auth/* stay public.
  matcher: ["/api/price/:path*", "/account/:path*"],
};
