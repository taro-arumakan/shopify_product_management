"use server";

import { redirect } from "next/navigation";
import { lookupAccount } from "@/lib/allowlist";
import { createToken } from "@/lib/session";
import { magicLinkEmail, sendEmail } from "@/lib/email";
import { baseUrl } from "@/lib/url";

/**
 * Handle a trade-login request.
 * - On the allowlist  → email a magic link, redirect to a "check your inbox" state.
 * - Not on the list    → redirect to a state that points them at the quote form
 *                        (turns a rejected login into a lead).
 */
export async function requestMagicLink(formData: FormData): Promise<void> {
  const email = String(formData.get("email") ?? "").trim();
  if (!email) redirect("/login?status=error");

  const account = lookupAccount(email);
  if (!account) {
    redirect("/login?status=notfound");
  }

  const token = await createToken("magic", {
    email: account.email,
    tier: account.tier,
    company: account.company,
  });
  const url = `${await baseUrl()}/api/auth/verify?token=${encodeURIComponent(token)}`;

  await sendEmail({
    to: account.email,
    subject: "Your Hammond Button Works sign-in link",
    html: magicLinkEmail(url, account.company),
  });

  redirect("/login?status=sent");
}
