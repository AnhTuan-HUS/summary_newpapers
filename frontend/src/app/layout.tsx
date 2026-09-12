import type { Metadata } from "next";

import { Geist, Geist_Mono } from "next/font/google";

import Header from "@/components/Header";

import Footer from "@/components/Footer";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "TECH VIỆT — Tạp chí công nghệ Việt Nam",
  description:
    "Tin tức bán dẫn, vi mạch, trí tuệ nhân tạo, startup, xe điện và hạ tầng số.",
};

export default function RootLayout({
  children,
}: LayoutProps<"/">) {
  return (
    <html
      lang="vi"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (() => {
                try {
                  const theme = localStorage.getItem("theme");

                  if (theme === "dark") {
                    document.documentElement.classList.add("dark");
                  } else {
                    document.documentElement.classList.remove("dark");
                  }
                } catch {}
              })();
            `,
          }}
        />
      </head>

      <body className="flex min-h-full flex-col bg-[#F9FAFB] text-[#111827] transition-colors dark:bg-[#0B0F19] dark:text-gray-100">
        <Header />

        <main className="flex-1">
          {children}
        </main>

        <Footer />
      </body>
    </html>
  );
}