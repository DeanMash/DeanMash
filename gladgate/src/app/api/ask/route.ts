import { NextResponse } from "next/server";
import { sendAskBatch } from "@/lib/store";
import type { Channel } from "@/lib/types";

export async function POST(request: Request) {
  const body = (await request.json().catch(() => ({}))) as {
    count?: number;
    channel?: Channel;
  };

  const count = Math.min(Math.max(body.count ?? 3, 1), 6);
  const channel = body.channel === "sms" ? "sms" : "whatsapp";
  const result = sendAskBatch(count, channel);

  return NextResponse.json(result);
}
