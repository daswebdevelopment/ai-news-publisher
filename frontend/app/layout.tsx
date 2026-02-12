import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI News Publisher",
  description: "Minimal Next.js frontend for published AI news events"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main className="container">{children}</main>
      </body>
    </html>
  );
}
