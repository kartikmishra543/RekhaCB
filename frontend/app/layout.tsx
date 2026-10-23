import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "RekhaCB | HR Copilot",
  description: "HR policies, people insights and everyday requests in one workspace",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
