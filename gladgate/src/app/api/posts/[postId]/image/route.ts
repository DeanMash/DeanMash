import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { isMashtechAuthed, MASHTECH_COOKIE } from "@/lib/auth";
import { renderSocialPostJpeg } from "@/lib/post-image";
import { getPostById } from "@/lib/store";

/** Returns social post as JPEG (1080×1080) for Facebook / WhatsApp. */
export async function GET(
  _request: Request,
  context: { params: Promise<{ postId: string }> },
) {
  const jar = await cookies();
  if (!isMashtechAuthed(jar.get(MASHTECH_COOKIE)?.value)) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { postId } = await context.params;
  const found = getPostById(postId);
  if (!found) {
    return NextResponse.json({ error: "Post not found" }, { status: 404 });
  }

  const jpeg = await renderSocialPostJpeg(found);
  return new NextResponse(new Uint8Array(jpeg), {
    headers: {
      "Content-Type": "image/jpeg",
      "Content-Disposition": `attachment; filename="gladgate-${found.business.slug}-${postId}.jpg"`,
      "Cache-Control": "public, max-age=3600",
    },
  });
}
