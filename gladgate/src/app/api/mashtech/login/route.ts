import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import {
  createMashtechSessionToken,
  isMashtechAuthed,
  mashtechCookieOptions,
  MASHTECH_COOKIE,
  verifyMashtechPassword,
} from "@/lib/auth";

export async function POST(request: Request) {
  const body = (await request.json()) as { password?: string };
  if (!body.password || !verifyMashtechPassword(body.password)) {
    return NextResponse.json({ error: "Invalid password" }, { status: 401 });
  }

  const token = createMashtechSessionToken();
  const res = NextResponse.json({ ok: true, message: "Signed in to Mashtech." });
  res.cookies.set(MASHTECH_COOKIE, token, mashtechCookieOptions());
  return res;
}

export async function DELETE() {
  const res = NextResponse.json({ ok: true });
  res.cookies.set(MASHTECH_COOKIE, "", { ...mashtechCookieOptions(), maxAge: 0 });
  return res;
}

export async function GET() {
  const jar = await cookies();
  return NextResponse.json({
    authed: isMashtechAuthed(jar.get(MASHTECH_COOKIE)?.value),
  });
}
