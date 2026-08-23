import type { Metadata } from "next";
import { Figtree, Syne } from "next/font/google";
import "./globals.css";

const syne = Syne({
  variable: "--font-syne",
  subsets: ["latin"],
  weight: ["600", "700", "800"],
});

const figtree = Figtree({
  variable: "--font-figtree",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "GladGate by Mashtech — $3 EcoCash review QR for small shops",
  description:
    "Register your shop, get a review link and QR code. Automatic customer follow-ups. Mashtech posts happy reviews tagging your page. $3/month on EcoCash.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${syne.variable} ${figtree.variable}`}>
      <body>{children}</body>
    </html>
  );
}
