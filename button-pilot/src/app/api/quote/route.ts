import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { sendEmail, escapeHtml } from "@/lib/email";
import { rateLimit } from "@/lib/ratelimit";

/**
 * Quote / trade-access request handler.
 *  1. Honeypot + rate limit (anti-spam).
 *  2. Email the owner (QUOTE_INBOX) with the details, reply-to the requester.
 *  3. Auto-acknowledge the requester.
 *  4. Optionally append a row to a Google Sheet via QUOTE_SHEET_WEBHOOK_URL
 *     (a Google Apps Script web app — see README).
 *
 * No database required.
 */
const QuoteSchema = z.object({
  company: z.string().min(1).max(200),
  name: z.string().min(1).max(200),
  email: z.string().email().max(200),
  phone: z.string().max(80).optional().or(z.literal("")),
  sku: z.string().max(80).optional().or(z.literal("")),
  qty: z.string().max(40).optional().or(z.literal("")),
  message: z.string().min(1).max(4000),
  website: z.string().max(0).optional(), // honeypot: must be empty
});

export async function POST(req: NextRequest): Promise<NextResponse> {
  const ip =
    req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "unknown";
  const limit = rateLimit(`quote:${ip}`, 5, 10 * 60 * 1000); // 5 per 10 min
  if (!limit.ok) {
    return NextResponse.json(
      { error: "Too many requests. Please try again shortly." },
      { status: 429 },
    );
  }

  const parsed = QuoteSchema.safeParse(await req.json().catch(() => null));
  if (!parsed.success) {
    // Honeypot filled or invalid input — fail quietly to bots.
    return NextResponse.json({ error: "Invalid submission." }, { status: 400 });
  }

  const q = parsed.data;
  const inbox = process.env.QUOTE_INBOX ?? process.env.EMAIL_FROM ?? "owner@example.com";

  const rows: [string, string][] = [
    ["Company", q.company],
    ["Name", q.name],
    ["Email", q.email],
    ["Phone", q.phone || "—"],
    ["SKU", q.sku || "—"],
    ["Quantity", q.qty || "—"],
    ["Message", q.message],
  ];
  const html = `
    <div style="font-family:system-ui,sans-serif">
      <h2>New quote request</h2>
      <table style="border-collapse:collapse">
        ${rows
          .map(
            ([k, v]) =>
              `<tr><td style="padding:4px 12px 4px 0;color:#78716c;vertical-align:top">${k}</td><td style="padding:4px 0">${escapeHtml(v)}</td></tr>`,
          )
          .join("")}
      </table>
    </div>`;

  // 2. Notify the owner.
  await sendEmail({
    to: inbox,
    subject: `Quote request — ${q.company}`,
    html,
    replyTo: q.email,
  });

  // 3. Acknowledge the requester (best-effort).
  await sendEmail({
    to: q.email,
    subject: "We received your request — Hammond Button Works",
    html: `<div style="font-family:system-ui,sans-serif"><p>Hi ${escapeHtml(q.name)},</p>
      <p>Thanks for reaching out to Hammond Button Works. We've received your request and will
      reply with pricing and next steps, usually within one business day.</p>
      <p>— Hammond Button Works</p></div>`,
  }).catch(() => {});

  // 4. Optional: append to a Google Sheet.
  const sheetWebhook = process.env.QUOTE_SHEET_WEBHOOK_URL;
  if (sheetWebhook) {
    await fetch(sheetWebhook, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...q, receivedAt: new Date().toISOString() }),
    }).catch((e) => console.error("Sheet append failed:", e));
  }

  return NextResponse.json({ ok: true });
}
