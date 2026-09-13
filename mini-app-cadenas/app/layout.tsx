import type { Metadata } from 'next';
import './globals.css';
import './card-theme.css';

export const metadata: Metadata = {
  title: 'La Bague hors du Temps — Cadenas',
  description: 'Mini-application de validation des codes de l’escape game.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
