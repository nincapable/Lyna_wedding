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
  const home = load('app/page.tsx', { react });
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
