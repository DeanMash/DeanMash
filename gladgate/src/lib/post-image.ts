import sharp from "sharp";
import type { Business, CustomerPulse, SocialPost } from "./types";

function escapeXml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function wrapLines(text: string, maxChars: number, maxLines: number): string[] {
  const words = text.replace(/\s+/g, " ").trim().split(" ");
  const lines: string[] = [];
  let current = "";
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (next.length <= maxChars) {
      current = next;
    } else {
      if (current) lines.push(current);
      current = word;
      if (lines.length >= maxLines - 1) break;
    }
  }
  if (current && lines.length < maxLines) lines.push(current);
  return lines.slice(0, maxLines);
}

export async function renderSocialPostJpeg(input: {
  business: Business;
  post: SocialPost;
  pulse?: CustomerPulse;
}): Promise<Buffer> {
  const { business, post, pulse } = input;
  const isReview = post.kind === "review";
  const rating = pulse?.rating ?? 5;
  const stars = "★".repeat(rating) + "☆".repeat(5 - rating);
  const headline = isReview
    ? `${rating}/5 from ${pulse?.customerName ?? "a happy customer"}`
    : "Now on GladGate";
  const bodyLines = wrapLines(
    post.readyCaption.replace(/\n+/g, " "),
    42,
    5,
  );

  const bodyTspans = bodyLines
    .map(
      (line, i) =>
        `<tspan x="80" dy="${i === 0 ? 0 : 38}">${escapeXml(line)}</tspan>`,
    )
    .join("");

  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="1080" height="1080" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1f4d38"/>
      <stop offset="55%" style="stop-color:#152019"/>
      <stop offset="100%" style="stop-color:#0f1712"/>
    </linearGradient>
  </defs>
  <rect width="1080" height="1080" fill="url(#bg)"/>
  <rect x="56" y="56" width="968" height="968" rx="36" fill="rgba(245,247,242,0.08)" stroke="rgba(232,155,12,0.45)" stroke-width="3"/>
  <text x="80" y="130" fill="#e89b0c" font-family="Arial,sans-serif" font-size="28" font-weight="700">GladGate · Mashtech</text>
  <text x="80" y="210" fill="#f5f7f2" font-family="Arial,sans-serif" font-size="52" font-weight="700">${escapeXml(business.name)}</text>
  <text x="80" y="270" fill="#c8d5cb" font-family="Arial,sans-serif" font-size="28">${escapeXml(business.city)} · ${escapeXml(business.vertical.replace("_", " "))}</text>
  <text x="80" y="340" fill="#f5f7f2" font-family="Arial,sans-serif" font-size="36" font-weight="700">${escapeXml(headline)}</text>
  <text x="80" y="395" fill="#e89b0c" font-family="Arial,sans-serif" font-size="34">${escapeXml(stars)}</text>
  <text x="80" y="470" fill="#dce6df" font-family="Arial,sans-serif" font-size="26" font-weight="400">${bodyTspans}</text>
  <text x="80" y="930" fill="#e89b0c" font-family="Arial,sans-serif" font-size="30" font-weight="700">Tag ${escapeXml(post.tagHandle)}</text>
  <text x="80" y="980" fill="#9fb0a4" font-family="Arial,sans-serif" font-size="22">Scan QR · leave a review · $3/mo EcoCash</text>
</svg>`;

  return sharp(Buffer.from(svg)).jpeg({ quality: 90, mozjpeg: true }).toBuffer();
}
