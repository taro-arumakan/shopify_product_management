import { NextRequest, NextResponse } from "next/server";
import { endSession } from "@/lib/auth";

export async function POST(req: NextRequest): Promise<NextResponse> {
  await endSession();
  return NextResponse.redirect(new URL("/", req.url), { status: 303 });
}
