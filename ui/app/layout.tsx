import type { Metadata } from "next";
import { Montserrat, Poiret_One } from "next/font/google";
import { ThemeProvider } from "next-themes";
import "./globals.css";

const defaultUrl = process.env.VERCEL_URL
  ? `https://${process.env.VERCEL_URL}`
  : "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(defaultUrl),
  title: "LeafLine - AI-Powered Plant Identification & Diagnostics",
  description:
    "Identify your plants and diagnose issues with AI-powered assistance. Get expert care recommendations for your plants.",
};

// Body/paragraph font
const montserrat = Montserrat({
  variable: "--font-montserrat",
  display: "swap",
  subsets: ["latin"],
});

// Title/heading font
const poiretOne = Poiret_One({
  variable: "--font-poiret",
  display: "swap",
  subsets: ["latin"],
  weight: "400", // Poiret One only has one weight
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${montserrat.variable} ${poiretOne.variable} antialiased`}
        suppressHydrationWarning
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
