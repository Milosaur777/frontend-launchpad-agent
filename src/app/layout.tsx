import type { Metadata } from "next";
import { Cinzel, Cormorant_Garamond, UnifrakturMaguntia } from "next/font/google";
import "./globals.css";

const cinzel = Cinzel({
  variable: "--font-cinzel",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const cormorant = Cormorant_Garamond({
  variable: "--font-cormorant",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

const blackletter = UnifrakturMaguntia({
  variable: "--font-blackletter",
  subsets: ["latin"],
  weight: "400",
});

export const metadata: Metadata = {
  title: "Milo's Arcanum | Dark Fantasy Art Gallery",
  description: "A curated gallery of dark fantasy, gothic medieval, and occult-inspired artwork. Explore the storm-crowned castle, the illuminated scriptorium, and the void beyond.",

};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${cinzel.variable} ${cormorant.variable} ${blackletter.variable} dark antialiased`}
    >
      <body className="min-h-full flex flex-col bg-storm-void text-foreground overflow-x-hidden">
        {children}
      </body>
    </html>
  );
}
