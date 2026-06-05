import type { Metadata } from 'next';
import { Providers } from './providers';
import './globals.css';

export const metadata: Metadata = {
  title: 'CourtVision AI - NBA Analytics & Predictions',
  description: 'Professional NBA basketball analytics and game predictions powered by AI',
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-dark-bg text-dark-text">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
