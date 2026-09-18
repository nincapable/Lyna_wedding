import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import sharp from 'sharp';
import ts from 'typescript';
import { createRequire } from 'node:module';
import { recognizeDragon, purpleMask } from '../lib/dragon-recognition.mjs';

const resolveModule = createRequire(import.meta.url);
const reference = fs.readFileSync('scan-reference/dragon.png');

test('recognizes the reference under JPEG compression, rotation and dimmer light', async () => {
  const examples = [
    reference,
    await sharp(reference).resize(900).jpeg({ quality: 65 }).toBuffer(),
    await sharp(reference).resize(1000).rotate(27, { background: '#fff' }).jpeg().toBuffer(),
    await sharp(reference).resize(1000).rotate(90).jpeg().toBuffer(),
    await sharp(reference).resize(1000).modulate({ brightness: .65, saturation: .8 }).jpeg().toBuffer(),
  ];
  for (let i = 0; i < examples.length; i++) assert.equal((await recognizeDragon(examples[i])).accepted, true, `Example ${i}`);
});

test('ignores card backgrounds, tolerates overlap occlusion and perspective, rejects misplaced or missing parts', async () => {
  const { data, info } = await sharp(reference).resize(900).removeAlpha().raw().toBuffer({ resolveWithObject: true });
  const mask = purpleMask(data, 900, 900, info.channels);
  const base = Buffer.alloc(900 * 900 * 3, 190);
  for (let i = 0; i < mask.length; i++) if (mask[i]) base.set([143, 0, 255], i * 3);
  const encode = raw => sharp(raw, { raw: { width: 900, height: 900, channels: 3 } }).jpeg({ quality: 85 }).toBuffer();
  assert.equal((await recognizeDragon(await encode(base))).accepted, true);
  const occluded = Buffer.from(base);
  for (let y = 0; y < 900; y++) for (let x = 0; x < 900; x++) {
    if ((x > 220 && x < 270 && y > 280 && y < 590) || (x > 480 && x < 535 && y > 310 && y < 580)
      || (x > 300 && x < 350 && y > 580 && y < 700)) occluded.fill(190, (y * 900 + x) * 3, (y * 900 + x) * 3 + 3);
  }
  assert.equal((await recognizeDragon(await encode(occluded))).accepted, true);
  const warped = Buffer.alloc(base.length, 190);
  const h = [1, .1, -45, .04, 1, -10, .00012, -.00008, 1];
  for (let y = 0; y < 900; y++) for (let x = 0; x < 900; x++) {
    const w = h[6] * x + h[7] * y + 1;
    const sx = Math.round((h[0] * x + h[1] * y + h[2]) / w), sy = Math.round((h[3] * x + h[4] * y + h[5]) / w);
    if (sx >= 0 && sy >= 0 && sx < 900 && sy < 900) base.copy(warped, (y * 900 + x) * 3, (sy * 900 + sx) * 3, (sy * 900 + sx) * 3 + 3);
  }
  assert.equal((await recognizeDragon(await encode(warped))).accepted, true);
  const shuffled = Buffer.alloc(base.length, 190), order = [8, 4, 2, 6, 0, 7, 1, 5, 3];
  for (let y = 0; y < 900; y++) for (let x = 0; x < 900; x++) {
    const tile = Math.floor(y / 300) * 3 + Math.floor(x / 300), source = order[tile];
    const sx = source % 3 * 300 + x % 300, sy = Math.floor(source / 3) * 300 + y % 300;
    base.copy(shuffled, (y * 900 + x) * 3, (sy * 900 + sx) * 3, (sy * 900 + sx) * 3 + 3);
  }
  assert.equal((await recognizeDragon(await encode(shuffled))).accepted, false);
  const missingHead = Buffer.from(base);
  for (let y = 190; y < 490; y++) for (let x = 490; x < 710; x++) missingHead.fill(190, (y * 900 + x) * 3, (y * 900 + x) * 3 + 3);
  assert.equal((await recognizeDragon(await encode(missingHead))).accepted, false);
  assert.equal((await recognizeDragon(await encode(Buffer.alloc(base.length, 255)))).accepted, false);
  const doodle = await sharp(Buffer.from('<svg width="900" height="900"><rect width="900" height="900" fill="white"/><path d="M150 150L750 750M150 750L750 150M100 450H800" stroke="#8f00ff" stroke-width="12"/></svg>')).png().toBuffer();
  assert.equal((await recognizeDragon(doodle)).accepted, false);
});

function loadRoute(path, dependencies) {
  const code = ts.transpileModule(fs.readFileSync(path, 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText;
  const exports = {};
  new Function('require', 'exports', code)(name => dependencies[name] ?? resolveModule(name), exports);
  return exports;
}

test('scan route enforces stage, server recognition, kill switch, attempts and concurrent reset', async () => {
  const row = { code: 'ABC123', stage: 1, attempts: 0, accept_any_code: false, updated_at: new Date().toISOString() };
  let recognized = false, recognitionCalls = 0, concurrentChange = false;
  const route = loadRoute('app/api/games/[code]/scan/route.ts', {
    '@/lib/supabase': { databaseConfigured: () => true, db: async (_, init = {}) => {
      if (init.method === 'PATCH') {
        if (concurrentChange) return Response.json([]);
        Object.assign(row, JSON.parse(init.body));
      }
      return Response.json([row]);
    } },
    '@/lib/dragon-recognition.mjs': { recognizeDragon: async () => {
      recognitionCalls++; return { accepted: recognized, reason: recognized ? 'match' : 'incomplete' };
    } },
  });
  const post = (blob = new Blob(['photo'], { type: 'image/jpeg' })) => {
    const form = new FormData(); form.append('photo', blob, 'dragon.jpg');
    return route.POST(new Request('http://localhost/api/games/ABC123/scan', { method: 'POST', body: form }), { params: Promise.resolve({ code: 'ABC123' }) });
  };
  assert.equal((await post()).status, 409);
  row.stage = 2;
  const failed = await (await post()).json();
  assert.equal(failed.accepted, false); assert.equal(row.stage, 2); assert.equal(row.attempts, 1);
  recognized = true;
  const success = await (await post()).json();
  assert.equal(success.accepted, true); assert.equal(success.unlockedStage, 2); assert.equal(row.stage, 3);
  assert.equal((await post()).status, 409);
  row.stage = 2; recognized = false; row.accept_any_code = true;
  const calls = recognitionCalls;
  assert.equal((await (await post()).json()).accepted, true); assert.equal(recognitionCalls, calls);
  row.stage = 2; row.accept_any_code = false;
  assert.equal((await post(new Blob(['text'], { type: 'text/plain' }))).status, 400);
  concurrentChange = true;
  assert.equal((await post()).status, 409); assert.equal(row.stage, 2);
});

test('the second lock cannot be bypassed using its former numeric code', async () => {
  const route = loadRoute('app/api/games/[code]/route.ts', {
    '@/lib/supabase': { databaseConfigured: () => true, db: async () => Response.json([{ code: 'ABC123', stage: 2, attempts: 0, accept_any_code: false }]) },
  });
  const response = await route.PATCH(new Request('http://localhost/api/games/ABC123', { method: 'PATCH', body: JSON.stringify({ action: 'submit', code: '2543' }) }), { params: Promise.resolve({ code: 'ABC123' }) });
  assert.equal(response.status, 400);
});
