import { createHmac, timingSafeEqual } from 'node:crypto';

type Session = { code: string; gm_token: string; updated_at: string };
export function scanProof(game: Session) {
  return createHmac('sha256', game.gm_token).update(`${game.code}:${game.updated_at}:dragon`).digest('hex');
}
export function verifiedScan(game: Session, proof: unknown) {
  if (typeof proof !== 'string' || !/^[a-f0-9]{64}$/.test(proof)) return false;
  return timingSafeEqual(Buffer.from(scanProof(game), 'hex'), Buffer.from(proof, 'hex'));
}
