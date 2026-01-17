import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import { Analytics } from "@vercel/analytics/react";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
  display: "swap",
});

// Enhanced viewport for mobile responsiveness
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  viewportFit: "cover",
  themeColor: "#CE2029",
};

// Comprehensive SEO metadata
export const metadata: Metadata = {
  title: "Firefighter Exam Prep | Free Practice Tests & Study Guide | Captain's Academy",
  description:
    "Pass your firefighter written exam with AI-powered practice tests, flashcards, and expert tutoring. Built by firefighters, using real fire service manuals. Free online preparation for entry-level and promotional exams.",
  keywords: [
    "firefighter written exam",
    "firefighter practice test",
    "firefighter study guide",
    "fireteam test prep",
    "firefighter aptitude test",
    "fire department exam",
    "nfpa exam questions",
    "firefighter civil service exam",
    "firefighter certification",
    "fire academy prep",
  ],
  authors: [{ name: "Captain's Academy" }],
  creator: "Captain's Academy",
  publisher: "Captain's Academy",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://captains-academy.vercel.app",
    siteName: "Captain's Academy",
    title: "Firefighter Exam Prep | Free Practice Tests & Study Guide",
    description:
      "Pass your firefighter written exam with AI-powered practice tests and flashcards. Built by firefighters using real fire service manuals.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Captain's Academy - Firefighter Exam Prep",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Firefighter Exam Prep | Captain's Academy",
    description:
      "AI-powered firefighter exam preparation with practice tests, flashcards, and expert tutoring.",
    images: ["/og-image.png"],
  },
  alternates: {
    canonical: "https://captains-academy.vercel.app",
  },
  category: "Education",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        {/* Preconnect to external resources for faster loading */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} antialiased bg-background text-foreground`}
      >
        {children}
        <Analytics />
      </body>
    </html>
  );
}

