import { open } from 'node:fs/promises';
import { join } from 'node:path';
import { Readable } from 'node:stream';
import { NextRequest, NextResponse } from 'next/server';
import { databaseConfigured, db } from '@/lib/supabase';

export const runtime = 'nodejs';
export async function GET(_: NextRequest, context: { params: Promise<{ code: string }> }) {
  if (!databaseConfigured()) return NextResponse.json({ error: 'Base non configurée.' }, { status: 503 });
  try {
    const { code } = await context.params;
    const response = await db(`game_sessions?code=eq.${encodeURIComponent(code.toUpperCase())}&select=stage`);
    if (!response.ok) throw new Error('DB_ERROR');
    const [game] = await response.json() as { stage: number }[];
    if (!game) return NextResponse.json({ error: 'Partie introuvable.' }, { status: 404 });
    if (game.stage !== 3) return NextResponse.json({ error: 'Ouvrez les deux cadenas pour accéder au rapport.' }, { status: 403 });
    const file = await open(join(process.cwd(), 'resolution-documents', 'rapport-enquete.pdf'), 'r');
    return new NextResponse(Readable.toWeb(file.createReadStream()) as ReadableStream<Uint8Array>, { headers: {
      'Content-Type': 'application/pdf', 'Content-Disposition': 'inline; filename="rapport-enquete.pdf"',
      'Cache-Control': 'private, no-store', 'X-Content-Type-Options': 'nosniff',
    } });
  } catch { return NextResponse.json({ error: 'Rapport inaccessible. Réessayez.' }, { status: 500 }); }
}
