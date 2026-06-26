import Link from "next/link";
import type { Metadata } from "next";
import { requestMagicLink } from "./actions";

export const metadata: Metadata = { title: "Trade login" };

const MESSAGES: Record<string, { tone: "info" | "warn" | "error"; text: string }> = {
  sent: {
    tone: "info",
    text: "Check your inbox — we've emailed you a sign-in link (valid for 15 minutes). In local dev with no email key set, the link is printed in the server console.",
  },
  notfound: {
    tone: "warn",
    text: "That email isn't on our approved trade list yet. Request a quote and we'll set you up with an account.",
  },
  invalid: {
    tone: "error",
    text: "That sign-in link is invalid or has expired. Please request a new one.",
  },
  error: { tone: "error", text: "Please enter a valid email address." },
};

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ status?: string }>;
}) {
  const { status } = await searchParams;
  const message = status ? MESSAGES[status] : undefined;

  return (
    <div className="mx-auto max-w-md px-4 py-16">
      <h1 className="text-2xl font-semibold tracking-tight">Trade login</h1>
      <p className="mt-2 text-stone-600">
        Approved trade accounts sign in with a one-time email link to see wholesale
        pricing and place orders.
      </p>

      {message && (
        <div
          className={`mt-6 rounded-md border px-4 py-3 text-sm ${
            message.tone === "info"
              ? "border-green-200 bg-green-50 text-green-800"
              : message.tone === "warn"
                ? "border-amber-200 bg-amber-50 text-amber-800"
                : "border-red-200 bg-red-50 text-red-800"
          }`}
        >
          {message.text}
          {status === "notfound" && (
            <>
              {" "}
              <Link href="/quote" className="font-medium underline">
                Request a quote →
              </Link>
            </>
          )}
        </div>
      )}

      <form action={requestMagicLink} className="mt-8 space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-stone-700">
            Work email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            autoComplete="email"
            placeholder="you@yourbrand.com"
            className="mt-1 w-full rounded-md border border-stone-300 px-3 py-2 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
          />
        </div>
        <button
          type="submit"
          className="w-full rounded-md bg-accent px-4 py-2.5 font-medium text-white hover:opacity-90"
        >
          Email me a sign-in link
        </button>
      </form>

      <p className="mt-6 text-xs text-stone-500">
        Not a trade customer yet?{" "}
        <Link href="/quote" className="underline">
          Request trade access
        </Link>
        .
      </p>
    </div>
  );
}
