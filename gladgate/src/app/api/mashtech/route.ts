import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { isMashtechAuthed, MASHTECH_COOKIE } from "@/lib/auth";
import {
  confirmEcoCashPayment,
  getMashtechSnapshot,
  publishAllQueuedPosts,
  publishPostById,
} from "@/lib/store";

async function requireAuth() {
  const jar = await cookies();
  if (!isMashtechAuthed(jar.get(MASHTECH_COOKIE)?.value)) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  return null;
}

export async function GET() {
  const denied = await requireAuth();
  if (denied) return denied;
  return NextResponse.json(getMashtechSnapshot());
}

export async function POST(request: Request) {
  const denied = await requireAuth();
  if (denied) return denied;

  const body = (await request.json()) as {
    action?: "publish_all" | "publish_post" | "confirm_payment";
    postId?: string;
    reference?: string;
  };

  try {
    if (body.action === "publish_all") {
      const result = publishAllQueuedPosts();
      return NextResponse.json({
        ...result,
        message: `Published ${result.posted} Mashtech post(s).`,
        snapshot: getMashtechSnapshot(),
      });
    }

    if (body.action === "publish_post") {
      if (!body.postId) {
        return NextResponse.json({ error: "postId required" }, { status: 400 });
      }
      const post = publishPostById(body.postId);
      return NextResponse.json({
        post,
        message: "Post published.",
        snapshot: getMashtechSnapshot(),
      });
    }

    if (body.action === "confirm_payment") {
      if (!body.reference) {
        return NextResponse.json(
          { error: "reference required" },
          { status: 400 },
        );
      }
      const result = confirmEcoCashPayment({
        reference: body.reference,
        source: "mashtech_ops",
      });
      return NextResponse.json({
        ...result,
        message: result.alreadyConfirmed
          ? "Already confirmed."
          : "Payment confirmed — monthly plan active.",
        snapshot: getMashtechSnapshot(),
      });
    }

    return NextResponse.json({ error: "Unknown action" }, { status: 400 });
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed" },
      { status: 400 },
    );
  }
}
