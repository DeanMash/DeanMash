import { createHmac, timingSafeEqual } from "node:crypto";

export const MASHTECH_COOKIE = "mashtech_auth";
const SESSION_MS = 7 * 24 * 60 * 60 * 1000;

function secret(): string {
  return (
    process.env.MASHTECH_SESSION_SECRET ||
    process.env.MASHTECH_DASHBOARD_PASSWORD ||
    "mashtech-change-me-before-live"
  );
}

export function mashtechPassword(): string {
  return process.env.MASHTECH_DASHBOARD_PASSWORD || "Mashtech2026!";
}

export function verifyMashtechPassword(input: string): boolean {
  return input === mashtechPassword();
}

export function createMashtechSessionToken(): string {
  const payload = String(Date.now());
  const sig = createHmac("sha256", secret()).update(payload).digest("hex");
  return `${payload}.${sig}`;
}

export function isMashtechAuthed(token: string | undefined | null): boolean {
  if (!token) return false;
  const [payload, sig] = token.split(".");
  if (!payload || !sig) return false;
  const age = Date.now() - Number(payload);
  if (!Number.isFinite(age) || age < 0 || age > SESSION_MS) return false;
  const expected = createHmac("sha256", secret()).update(payload).digest("hex");
  try {
    return timingSafeEqual(Buffer.from(sig), Buffer.from(expected));
  } catch {
    return false;
  }
}

export function mashtechCookieOptions() {
  return {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax" as const,
    path: "/",
    maxAge: SESSION_MS / 1000,
  };
}
