import React from 'react'
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SuitSize.ai - Find Your Perfect Suit Size',
  description: 'AI-powered suit size recommendations. Get your perfect fit instantly with our advanced body type analysis.',
  keywords: 'suit size, suit fitting, menswear, AI sizing, body type analysis',
  openGraph: {
    title: 'SuitSize.ai - Find Your Perfect Suit Size',
    description: 'AI-powered suit size recommendations. Get your perfect fit instantly.',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
} 