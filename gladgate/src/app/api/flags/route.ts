import { NextResponse } from "next/server";
import { updateFlagStatus } from "@/lib/store";
import type { FlaggedReview } from "@/lib/types";

export async function PATCH(request: Request) {
  const body = (await request.json()) as {
    flagId?: string;
    status?: FlaggedReview["status"];
  };

  if (!body.flagId || !body.status) {
    return NextResponse.json(
      { error: "flagId and status are required" },
      { status: 400 },
    );
  }

  if (!["open", "recovering", "resolved"].includes(body.status)) {
    return NextResponse.json({ error: "Invalid status" }, { status: 400 });
  }

  try {
    const flag = updateFlagStatus(body.flagId, body.status);
    return NextResponse.json({ flag });
  } catch {
    return NextResponse.json({ error: "Flag not found" }, { status: 404 });
  }
}
