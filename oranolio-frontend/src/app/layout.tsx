import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Oranolio - The Digital Shadow Framework',
  description: 'Advanced penetration testing and red team operations platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-900 text-white`}>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-red-900 to-black">
          {children}
        </div>
      </body>
    </html>
  )
}