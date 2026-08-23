import { NextResponse } from "next/server";
import { findTrial, TRIAL_OFFERS } from "@/lib/trials";

export async function GET() {
  return NextResponse.json({
    trials: TRIAL_OFFERS,
    launchNote:
      "Share these codes and links before EcoCash billing goes live. After trial, shops pay $3 / month on EcoCash.",
  });
}

export async function POST(request: Request) {
  const body = (await request.json()) as { code?: string };
  if (!body.code) {
    return NextResponse.json({ error: "code required" }, { status: 400 });
  }
  const trial = findTrial(body.code);
  if (!trial) {
    return NextResponse.json({ error: "Invalid trial code" }, { status: 404 });
  }
  return NextResponse.json({ trial });
}
