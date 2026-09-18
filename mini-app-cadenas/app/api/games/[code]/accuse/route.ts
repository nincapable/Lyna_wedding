import { NextRequest, NextResponse } from 'next/server';
import { SUSPECTS } from '@/lib/suspects';
import { databaseConfigured, db } from '@/lib/supabase';

export async function POST(request: NextRequest, context: { params: Promise<{ code: string }> }) {
  if (!databaseConfigured()) return NextResponse.json({ error: 'Base non configurée.' }, { status: 503 });
  try {
    const { code } = await context.params;
    const { suspectId } = await request.json();
    if (!SUSPECTS.some(suspect => suspect.id === suspectId)) return NextResponse.json({ error: 'Sélectionnez un suspect.' }, { status: 400 });
    const response = await db(`game_sessions?code=eq.${encodeURIComponent(code.toUpperCase())}&select=stage`);
    if (!response.ok) throw new Error('DB_ERROR');
    const [game] = await response.json() as { stage: number }[];
    if (!game) return NextResponse.json({ error: 'Partie introuvable.' }, { status: 404 });
    if (game.stage !== 3) return NextResponse.json({ error: 'Ouvrez les deux cadenas avant de désigner un coupable.' }, { status: 403 });
    return NextResponse.json({ suspectId, correct: suspectId === 'kern' }, { headers: { 'Cache-Control': 'private, no-store' } });
  } catch { return NextResponse.json({ error: 'Conclusion inaccessible. Réessayez.' }, { status: 500 }); }
}
