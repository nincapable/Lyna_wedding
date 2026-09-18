import { randomBytes, randomUUID } from 'crypto';
import { NextResponse } from 'next/server';
import { databaseConfigured, db } from '@/lib/supabase';

export const runtime = 'nodejs';

export async function POST() {
  if (!databaseConfigured()) return NextResponse.json({ error: 'Base non configurée. Consultez SETUP-SYNC.md.' }, { status: 503 });
  for (let attempt = 0; attempt < 5; attempt++) {
    const code = randomBytes(4).toString('hex').slice(0, 6).toUpperCase();
    const gmToken = randomUUID();
    const response = await db('game_sessions', { method: 'POST', body: JSON.stringify({ code, gm_token: gmToken, stage: 1, attempts: 0 }) });
    if (response.ok) {
      const [row] = await response.json();
      return NextResponse.json({ code: row.code, stage: row.stage, attempts: row.attempts, updatedAt: row.updated_at, acceptAnyCode: row.accept_any_code ?? false, bypassDragon: row.bypass_dragon ?? false, gmToken });
    }
    if (response.status !== 409) return NextResponse.json({ error: 'Impossible de créer la partie.' }, { status: 500 });
  }
  return NextResponse.json({ error: 'Impossible de générer un code unique.' }, { status: 500 });
}
