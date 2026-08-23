import QRCode from "qrcode";

export async function qrDataUrl(text: string, size = 280): Promise<string> {
  return QRCode.toDataURL(text, {
    width: size,
    margin: 2,
    color: {
      dark: "#152019",
      light: "#f5f7f2",
    },
    errorCorrectionLevel: "M",
  });
}

export function absoluteUrl(path: string, origin?: string): string {
  const base =
    origin?.replace(/\/$/, "") ||
    process.env.NEXT_PUBLIC_APP_URL?.replace(/\/$/, "") ||
    "http://localhost:3000";
  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}
