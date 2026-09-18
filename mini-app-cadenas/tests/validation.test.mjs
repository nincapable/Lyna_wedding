import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import ts from 'typescript';
import { createRequire } from 'node:module';
const resolveModule = createRequire(import.meta.url);

function load(path, dependencies) {
  const code = ts.transpileModule(fs.readFileSync(path, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  const exports = {};
  new Function('require', 'exports', code)(name => dependencies[name] ?? resolveModule(name), exports);
  return exports;
}

test('investigation batches contain all expected PDFs without the solution report', () => {
  const { ENQUETE_BATCHES: batches } = load('lib/enquete.ts', {});
  assert.equal(batches[0].stage, 2);
  assert.equal(batches[1].stage, 3);
  assert.deepEqual(batches[0].documents.map(doc => doc.id), [
    'registre-biometrique', 'ancres', 'lettre-lyna', 'emargement',
    'notice-historique', 'lettre-milo', 'post-it', 'journal-intime',
  ]);
  const documents = batches.flatMap(batch => batch.documents);
  assert.equal(new Set(documents.map(doc => doc.id)).size, documents.length);
  assert.deepEqual(documents.map(doc => doc.file).sort(), fs.readdirSync('enquete-documents').sort());
  for (const doc of documents) {
    assert.ok(!doc.file.includes('Rapport_enquete'));
    const fd = fs.openSync(`enquete-documents/${doc.file}`, 'r');
    const header = Buffer.alloc(5);
    try { fs.readSync(fd, header, 0, 5, 0); } finally { fs.closeSync(fd); }
    assert.equal(header.toString(), '%PDF-');
  }
});

test('PDF access follows both locks and reset, even through direct URLs', async () => {
  let stage = 1;
  let exists = true;
  const route = load('app/api/games/[code]/documents/[id]/route.ts', {
    '@/lib/enquete': load('lib/enquete.ts', {}),
    '@/lib/supabase': { databaseConfigured: () => true, db: async () => Response.json(exists ? [{ stage }] : []) },
  });
  const get = async id => {
    const response = await route.GET(new Request('http://localhost'), { params: Promise.resolve({ code: 'ABC123', id }) });
    if (response.status === 200) {
      const reader = response.body.getReader();
      let bytes = 0;
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        bytes += value.byteLength;
      }
      const { ENQUETE_BATCHES: batches } = load('lib/enquete.ts', {});
      const doc = batches.flatMap(batch => batch.documents).find(doc => doc.id === id);
      assert.equal(bytes, fs.statSync(`enquete-documents/${doc.file}`).size);
    }
    return response;
  };
  assert.equal((await get('notice-historique')).status, 403);
  assert.equal((await get('carnet')).status, 403);
  stage = 2;
  const first = await get('notice-historique');
  assert.equal(first.status, 200);
  assert.equal(first.headers.get('content-type'), 'application/pdf');
  assert.equal(first.headers.get('cache-control'), 'private, no-store');
  assert.equal((await get('carnet')).status, 403);
  stage = 3;
  assert.equal((await get('notice-historique')).status, 200);
  assert.equal((await get('carnet')).status, 200);
  assert.equal((await get('photographies')).status, 200);
  stage = 1;
  assert.equal((await get('notice-historique')).status, 403);
  assert.equal((await get('carnet')).status, 403);
  assert.equal((await get('rapport-enquete')).status, 404);
  assert.equal((await get('../../supabase.sql')).status, 404);
  exists = false;
  assert.equal((await get('notice-historique')).status, 404);
});

test('kill switch submissions explicitly confirm the unlocked stage', async () => {
  const row = { code: 'ABC123', stage: 1, attempts: 0, accept_any_code: true, gm_token: 'secret', updated_at: new Date().toISOString() };
  const route = load('app/api/games/[code]/route.ts', {
    '@/lib/supabase': {
      databaseConfigured: () => true,
      db: async (_, init = {}) => {
        if (init.method === 'PATCH') Object.assign(row, JSON.parse(init.body));
        return Response.json([row]);
      },
    },
  });
  const submit = async code => (await route.PATCH(new Request('http://localhost/api/games/ABC123', {
    method: 'PATCH', body: JSON.stringify({ action: 'submit', code }),
  }), { params: Promise.resolve({ code: 'ABC123' }) })).json();
  for (const stage of [1, 2]) {
    const result = await submit('0000');
    assert.equal(result.accepted, true);
    assert.equal(result.unlockedStage, stage);
    assert.equal(result.stage, stage + 1);
  }
  assert.equal((await submit('0000')).accepted, false);
  row.stage = 1;
  row.accept_any_code = false;
  assert.equal((await submit('0000')).accepted, false);
});

test('submitting device shows success and ignores a poll started before submission', async () => {
  const initial = { code: 'ABC123', stage: 1, attempts: 0, acceptAnyCode: true, updatedAt: '2026-09-18T10:00:00Z' };
  const states = [initial, '', '', '0000', 'cadenas', '', false, null];
  const refs = [];
  const callbacks = [];
  let index = 0;
  const react = {
    useState: value => {
      const i = index++;
      if (!(i in states)) states[i] = value;
      return [states[i], next => { states[i] = next; }];
    },
    useRef: value => { const ref = { current: value }; refs.push(ref); return ref; },
    useCallback: fn => { callbacks.push(fn); return fn; },
    useEffect: () => {},
  };
  const home = load('app/page.tsx', { react, '@/lib/enquete': load('lib/enquete.ts', {}) });
  const tree = home.default();
  const [applyGame, loadGame] = callbacks;
  applyGame(initial);
  const originalFetch = global.fetch;
  let finishPoll, finishSubmit;
  global.fetch = (_, init) => new Promise(resolve => {
    if (init?.method === 'PATCH') finishSubmit = resolve;
    else finishPoll = resolve;
  });
  const find = node => {
    if (!node || typeof node !== 'object') return null;
    if (node.type === 'form') return node;
    for (const child of [node.props?.children].flat(Infinity)) {
      const result = find(child);
      if (result) return result;
    }
    return null;
  };
  try {
    const polling = loadGame(initial.code, true);
    find(tree).props.onSubmit({ preventDefault() {} });
    assert.equal(refs[1].current, true);
    finishSubmit(Response.json({ ...initial, stage: 2, updatedAt: '2026-09-18T10:00:01Z', accepted: true, unlockedStage: 1 }));
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(states[7], 1);
    assert.equal(states[4], 'cadenas');
    assert.equal(states[0].stage, 2);
    assert.equal(refs[1].current, false);
    finishPoll(Response.json(initial));
    await polling;
    assert.equal(states[7], 1);
    assert.equal(states[0].stage, 2);
  } finally {
    global.fetch = originalFetch;
  }
});
