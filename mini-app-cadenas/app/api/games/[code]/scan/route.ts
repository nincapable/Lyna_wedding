import { NextRequest, NextResponse } from 'next/server';
import { databaseConfigured, db } from '@/lib/supabase';
import { recognizeDragon } from '@/lib/dragon-recognition.mjs';
import { scanProof } from '@/lib/scan-proof';

export const runtime = 'nodejs';
export const maxDuration = 30;

type GameRow = { code: string; stage: number; attempts: number; accept_any_code: boolean; updated_at: string; gm_token: string };
const publicGame = (game: GameRow) => ({ code: game.code, stage: game.stage, attempts: game.attempts, acceptAnyCode: game.accept_any_code ?? false, updatedAt: game.updated_at });

export async function POST(request: NextRequest, context: { params: Promise<{ code: string }> }) {
  if (!databaseConfigured()) return NextResponse.json({ error: 'Base non configurée.' }, { status: 503 });
  const { code } = await context.params;
  try {
    const lookup = await db(`game_sessions?code=eq.${encodeURIComponent(code.toUpperCase())}&select=*`);
    if (!lookup.ok) throw new Error('DB_ERROR');
    const [game] = await lookup.json() as GameRow[];
    if (!game) return NextResponse.json({ error: 'Partie introuvable.' }, { status: 404 });
    if (game.stage !== 2) return NextResponse.json({ error: game.stage === 1 ? 'Déverrouillez d’abord le cadenas 1.' : 'Le dragon a déjà été validé.' }, { status: 409 });
    const form = await request.formData();
    const photo = form.get('photo');
    if (!(photo instanceof File) || !['image/jpeg', 'image/png', 'image/webp'].includes(photo.type) || photo.size === 0 || photo.size > 3_000_000) {
      return NextResponse.json({ error: 'Choisissez une photo JPEG, PNG ou WebP de moins de 3 Mo.' }, { status: 400 });
    }
    let accepted = game.accept_any_code;
    let reason = 'match';
    if (!accepted) {
      try {
        const result = await recognizeDragon(Buffer.from(await photo.arrayBuffer()));
        accepted = result.accepted; reason = result.reason;
      } catch {
        return NextResponse.json({ error: 'Photo illisible. Reprenez une photo nette au-dessus des cartes.' }, { status: 400 });
      }
    }
    // Only the still-locked second stage may be modified by this scan.
    const response = await db(`game_sessions?code=eq.${encodeURIComponent(game.code)}&stage=eq.2&updated_at=eq.${encodeURIComponent(game.updated_at)}`, {
      method: 'PATCH', body: JSON.stringify({ stage: 2, attempts: game.attempts + 1, updated_at: new Date().toISOString() }),
    });
    if (!response.ok) throw new Error('DB_ERROR');
    const [updated] = await response.json() as GameRow[];
    if (!updated) return NextResponse.json({ error: 'La partie a changé pendant le scan. Réessayez.' }, { status: 409 });
    const message = accepted ? "Les sorts liés à l'engramme sont à présents déchiffrés"
      : reason === 'violet' ? 'Les traits violets ne sont pas assez visibles. Rapprochez-vous et éclairez les cartes.'
      : reason === 'alignment' ? 'Le dragon ne correspond pas. Vérifiez la position des cartes et photographiez-les bien de dessus.'
      : 'Le dragon est incomplet ou désaligné. Vérifiez la tête, les ailes et la queue, puis réessayez.';
    return NextResponse.json({ ...publicGame(updated), accepted, ...(accepted ? { scanToken: scanProof(updated) } : {}), message });
  } catch { return NextResponse.json({ error: 'Impossible de vérifier la photo. Réessayez.' }, { status: 500 }); }
}
