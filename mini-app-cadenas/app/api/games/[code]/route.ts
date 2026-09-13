import { NextRequest, NextResponse } from 'next/server';
import { databaseConfigured, db } from '@/lib/supabase';

const LOCKS = [
  (process.env.LOCK_1_CODES ?? '3816,7482,1904,2631,5279').split(','),
  (process.env.LOCK_2_CODES ?? '2543,9062,4418,1357,6820').split(','),
];
type Row = { code: string; stage: 1 | 2 | 3; attempts: number; updated_at: string; gm_token: string };
const publicGame = (row: Row) => ({ code: row.code, stage: row.stage, attempts: row.attempts, updatedAt: row.updated_at });

async function findGame(code: string): Promise<Row | null> {
  const response = await db(`game_sessions?code=eq.${encodeURIComponent(code)}&select=*`);
  if (!response.ok) throw new Error('DB_ERROR');
  const rows = await response.json() as Row[];
  return rows[0] ?? null;
}

export async function GET(_: NextRequest, context: { params: Promise<{ code: string }> }) {
  if (!databaseConfigured()) return NextResponse.json({ error: 'Base non configurée.' }, { status: 503 });
  const { code } = await context.params;
  try {
    const game = await findGame(code.toUpperCase());
    return game ? NextResponse.json(publicGame(game)) : NextResponse.json({ error: 'Partie introuvable.' }, { status: 404 });
  } catch { return NextResponse.json({ error: 'Base inaccessible.' }, { status: 500 }); }
}

export async function PATCH(request: NextRequest, context: { params: Promise<{ code: string }> }) {
  if (!databaseConfigured()) return NextResponse.json({ error: 'Base non configurée.' }, { status: 503 });
  const { code } = await context.params;
  try {
    const body = await request.json() as { action?: string; code?: string; gmToken?: string };
    const game = await findGame(code.toUpperCase());
    if (!game) return NextResponse.json({ error: 'Partie introuvable.' }, { status: 404 });
    let stage = game.stage;
    let attempts = game.attempts;
    let message = '';
    if (body.action === 'submit') {
      if (stage === 3) return NextResponse.json(publicGame(game));
      attempts++;
      if (!body.code || !LOCKS[stage - 1].includes(body.code)) {
        const failed = await update(game.code, { attempts });
        return NextResponse.json({ ...publicGame(failed), message: 'Combinaison refusée. La boucle tient encore.' });
      }
      stage = (stage + 1) as 2 | 3;
      message = stage === 3 ? 'Le continuum est restauré.' : 'Sceau déverrouillé sur tous les appareils.';
    } else {
      if (!body.gmToken || body.gmToken !== game.gm_token) return NextResponse.json({ error: 'Commande MJ non autorisée.' }, { status: 403 });
      if (body.action === 'advance') { stage = Math.min(3, stage + 1) as 1 | 2 | 3; message = 'Étape débloquée par le MJ.'; }
      else if (body.action === 'reset') { stage = 1; attempts = 0; message = 'La partie a été réinitialisée.'; }
      else return NextResponse.json({ error: 'Action inconnue.' }, { status: 400 });
    }
    const updated = await update(game.code, { stage, attempts });
    return NextResponse.json({ ...publicGame(updated), message });
  } catch { return NextResponse.json({ error: 'Impossible de modifier la partie.' }, { status: 500 }); }
}

async function update(code: string, values: { stage?: number; attempts?: number }): Promise<Row> {
  const response = await db(`game_sessions?code=eq.${encodeURIComponent(code)}`, { method: 'PATCH', body: JSON.stringify({ ...values, updated_at: new Date().toISOString() }) });
  if (!response.ok) throw new Error('DB_ERROR');
  const [row] = await response.json() as Row[];
  return row;
}
