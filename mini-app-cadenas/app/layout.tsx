import type { Metadata } from 'next';
import './globals.css';
import './card-theme.css';

export const metadata: Metadata = {
  title: 'La Bague hors du Temps — Partie synchronisée',
  description: 'Application multijoueur de l’escape game temporel.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="fr"><body>{children}</body></html>;
}
