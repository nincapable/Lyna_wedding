import { open } from 'node:fs/promises';
import { join } from 'node:path';
import { Readable } from 'node:stream';
import { NextRequest, NextResponse } from 'next/server';
import { ENQUETE_BATCHES } from '@/lib/enquete';
import { databaseConfigured, db } from '@/lib/supabase';

export const runtime = 'nodejs';

export async function GET(_: NextRequest, context: { params: Promise<{ code: string; id: string }> }) {
  if (!databaseConfigured()) return NextResponse.json({ error: 'Base non configurée.' }, { status: 503 });
  const { code, id } = await context.params;
  const batch = ENQUETE_BATCHES.find(batch => batch.documents.some(doc => doc.id === id));
  const document = batch?.documents.find(doc => doc.id === id);
  if (!batch || !document) return NextResponse.json({ error: 'Document introuvable.' }, { status: 404 });
  try {
    const response = await db(`game_sessions?code=eq.${encodeURIComponent(code.toUpperCase())}&select=stage`);
    if (!response.ok) throw new Error('DB_ERROR');
    const [game] = await response.json() as { stage: number }[];
    if (!game) return NextResponse.json({ error: 'Partie introuvable.' }, { status: 404 });
    if (game.stage < batch.stage) return NextResponse.json({ error: `Déverrouillez le cadenas ${batch.number} pour accéder à ce batch.` }, { status: 403 });
    const file = await open(join(process.cwd(), 'enquete-documents', document.file), 'r');
    const stream = Readable.toWeb(file.createReadStream()) as ReadableStream<Uint8Array>;
    return new NextResponse(stream, { headers: {
      'Content-Type': 'application/pdf',
      'Content-Disposition': `inline; filename="${document.file}"`,
      'Cache-Control': 'private, no-store',
      'X-Content-Type-Options': 'nosniff',
    } });
  } catch { return NextResponse.json({ error: 'Document inaccessible. Réessayez.' }, { status: 500 }); }
}
