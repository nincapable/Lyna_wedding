import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import ts from 'typescript';
import { createRequire } from 'node:module';
const resolveModule = createRequire(import.meta.url);

test('final accusation checks the dossier culprit and report remains gated by both locks', async () => {
  let stage = 1;
  let exists = true;
  const dependencies = {
    '@/lib/suspects': load('lib/suspects.ts', {}),
    '@/lib/supabase': { databaseConfigured: () => true, db: async () => Response.json(exists ? [{ stage }] : []) },
  };
  const accuse = load('app/api/games/[code]/accuse/route.ts', dependencies);
  const report = load('app/api/games/[code]/report/route.ts', dependencies);
  const context = { params: Promise.resolve({ code: 'ABC123' }) };
  const guess = id => accuse.POST(new Request('http://localhost', { method: 'POST', body: JSON.stringify({ suspectId: id }) }), context);
  for (stage of [1, 2]) {
    assert.equal((await guess('kern')).status, 403);
    assert.equal((await report.GET(new Request('http://localhost'), context)).status, 403);
  }
  stage = 3;
  for (const suspect of dependencies['@/lib/suspects'].SUSPECTS) {
    const response = await guess(suspect.id);
    assert.equal(response.status, 200);
    assert.equal((await response.json()).correct, suspect.id === 'kern');
  }
  assert.equal((await guess('unknown')).status, 400);
  const pdf = await report.GET(new Request('http://localhost'), context);
  assert.equal(pdf.status, 200);
  assert.equal(pdf.headers.get('content-disposition'), 'inline; filename="rapport-enquete.pdf"');
  const bytes = Buffer.from(await pdf.arrayBuffer());
  assert.equal(bytes.subarray(0, 5).toString(), '%PDF-');
  assert.equal(bytes.length, fs.statSync('resolution-documents/rapport-enquete.pdf').size);
  stage = 1;
  assert.equal((await report.GET(new Request('http://localhost'), context)).status, 403);
  exists = false;
  assert.equal((await guess('kern')).status, 404);
});

function load(path, dependencies) {
  dependencies = { '@/lib/scan-proof': loadProof(), ...dependencies };
  const code = ts.transpileModule(fs.readFileSync(path, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  const exports = {};
  new Function('require', 'exports', code)(name => dependencies[name] ?? resolveModule(name), exports);
  return exports;
}

function loadProof() {
  const code = ts.transpileModule(fs.readFileSync('lib/scan-proof.ts', 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText;
  const exports = {};
  new Function('require', 'exports', code)(resolveModule, exports);
  return exports;
}

test('suspect selection requires confirmation and both endings open the report inside the app', async () => {
  const originalFetch = global.fetch;
  const suspects = load('lib/suspects.ts', {});
  function nodes(node) {
    if (!node || typeof node !== 'object') return [];
    return [node, ...[node.props?.children].flat(Infinity).flatMap(nodes)];
  }
  try {
    for (const correct of [true, false]) {
      const states = ['', null, false, '', false];
      let index = 0;
      let requests = 0;
      const component = load('app/components/Accusation.tsx', {
        '@/lib/suspects': suspects,
        react: { useState: value => { const i = index++; return [states[i] ?? value, next => { states[i] = next; }]; } },
      }).default;
      const render = () => { index = 0; return component({ gameCode: 'ABC123' }); };
      let tree = render();
      assert.equal(nodes(tree).find(node => node.type === 'button').props.disabled, true);
      const choice = correct ? 'kern' : 'saran';
      nodes(tree).find(node => node.type === 'input' && node.props.value === choice).props.onChange();
      global.fetch = async (url, init) => {
        requests++;
        assert.equal(url, '/api/games/ABC123/accuse');
        assert.equal(JSON.parse(init.body).suspectId, choice);
        return Response.json({ correct, suspectId: choice });
      };
      tree = render();
      assert.equal(requests, 0);
      await nodes(tree).find(node => node.type === 'button').props.onClick();
      assert.equal(requests, 1);
      tree = render();
      assert.ok(nodes(tree).some(node => node.props?.src === '/images/anneau.svg'));
      const text = nodes(tree).filter(node => node.type === 'p').map(node => JSON.stringify(node.props.children)).join(' ');
      if (!correct) {
        assert.ok(text.includes('21 h 16'));
        assert.ok(text.includes('équipe indépendante du futur'));
      } else assert.equal(nodes(tree).find(node => node.type === 'h1').props.children, 'Félicitations !');
      nodes(tree).find(node => node.type === 'button').props.onClick();
      tree = render();
      assert.equal(nodes(tree).find(node => node.type === 'iframe').props.src, '/api/games/ABC123/report#view=FitH');
    }
  } finally { global.fetch = originalFetch; }
});

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
    method: 'PATCH', body: JSON.stringify({ action: 'submit', code, ...(row.stage === 2 ? { scanToken: loadProof().scanProof(row) } : {}) }),
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
  const home = load('app/page.tsx', { react, '@/lib/enquete': load('lib/enquete.ts', {}), '@/app/components/Accusation': { default: () => null }, '@/app/components/DragonScanner': { default: () => null } });
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

test('a recognized photo authorizes code entry without opening the second lock', async () => {
  const initial = { code: 'ABC123', stage: 2, attempts: 0, acceptAnyCode: false, updatedAt: '2026-09-18T10:00:00Z' };
  const states = [initial, '', '', '', 'cadenas', '', false, null];
  let index = 0;
  const callbacks = [];
  const react = {
    useState: value => {
      const i = index++;
      if (!(i in states)) states[i] = value;
      return [states[i], next => { states[i] = next; }];
    },
    useRef: value => ({ current: value }),
    useCallback: fn => { callbacks.push(fn); return fn; },
    useEffect: () => {},
  };
  const Scanner = () => null;
  const home = load('app/page.tsx', { react, '@/lib/enquete': load('lib/enquete.ts', {}), '@/app/components/Accusation': { default: () => null }, '@/app/components/DragonScanner': { default: Scanner } });
  const tree = home.default();
  function nodes(node) {
    if (!node || typeof node !== 'object') return [];
    return [node, ...[node.props?.children].flat(Infinity).flatMap(nodes)];
  }
  assert.equal(nodes(tree).some(node => node.props?.id === 'lock-code'), false);
  assert.equal(nodes(tree).some(node => node.type === 'form'), false);
  states[0] = { ...initial, acceptAnyCode: true }; index = 0;
  assert.equal(nodes(home.default()).some(node => node.props?.id === 'lock-code'), false);
  states[0] = { ...initial, bypassDragon: true }; index = 0;
  assert.equal(nodes(home.default()).find(node => node.props?.id === 'lock-code').props.disabled, false);
  states[0] = initial;
  callbacks[0](initial);
  function findScanner(node) {
    if (!node || typeof node !== 'object') return null;
    if (node.type === Scanner) return node;
    for (const child of [node.props?.children].flat(Infinity)) {
      const result = findScanner(child);
      if (result) return result;
    }
    return null;
  }
  const originalFetch = global.fetch;
  global.fetch = async (url, init) => {
    assert.equal(url, '/api/games/ABC123/scan');
    assert.equal(init.method, 'POST');
    assert.ok(init.body instanceof FormData);
    return Response.json({ ...initial, stage: 2, attempts: 1, updatedAt: '2026-09-18T10:00:01Z', accepted: true, scanToken: 'validated-proof' });
  };
  try {
    const form = new FormData(); form.append('photo', new Blob(['photo'], { type: 'image/jpeg' }), 'dragon.jpg');
    await findScanner(tree).props.onScan(form);
    assert.equal(states[0].stage, 2);
    assert.equal(states[7], null);
    assert.equal(states[9], 'validated-proof');
    assert.equal(states[4], 'cadenas');
    assert.equal(states[6], false);
    states[3] = '2543'; index = 0;
    const afterScan = home.default();
    const codeForm = nodes(afterScan).find(node => node.type === 'form');
    assert.ok(codeForm);
    assert.equal(nodes(codeForm).find(node => node.props?.id === 'lock-code').props.disabled, false);
    assert.equal(nodes(codeForm).find(node => node.type === 'label').props.children, 'Combinaison');
    global.fetch = async (url, init) => {
      assert.equal(url, '/api/games/ABC123');
      assert.equal(JSON.parse(init.body).scanToken, 'validated-proof');
      return Response.json({ ...initial, stage: 3, updatedAt: '2026-09-18T10:00:02Z', accepted: true, unlockedStage: 2 });
    };
    codeForm.props.onSubmit({ preventDefault() {} });
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(states[0].stage, 3);
    assert.equal(states[7], 2);
  } finally { global.fetch = originalFetch; }
});
