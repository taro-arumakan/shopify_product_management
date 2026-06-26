import { NextRequest, NextResponse } from "next/server";
import { verifyToken } from "@/lib/session";
import { startSession } from "@/lib/auth";
import { lookupAccount } from "@/lib/allowlist";

/**
 * Magic-link landing route. Validates the signed, short-lived token, then
 * re-checks the allowlist (so revoked accounts can't reuse an old link) before
 * issuing a session cookie.
 */
export async function GET(req: NextRequest): Promise<NextResponse> {
  const token = req.nextUrl.searchParams.get("token");
  const payload = await verifyToken(token, "magic");

  if (!payload) {
    return NextResponse.redirect(new URL("/login?status=invalid", req.url));
  }

  // Re-validate against the current allowlist at the moment of sign-in.
  const account = lookupAccount(payload.sub);
  if (!account) {
    return NextResponse.redirect(new URL("/login?status=notfound", req.url));
  }

  await startSession(account);
  return NextResponse.redirect(new URL("/catalog", req.url));
}
