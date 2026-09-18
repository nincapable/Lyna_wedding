 'use client';

import { FormEvent, useCallback, useEffect, useRef, useState } from 'react';

type Game = { code: string; stage: 1 | 2 | 3; attempts: number; updatedAt: string; acceptAnyCode: boolean };
type Tab = 'cadenas' | 'enquete' | 'chronologie' | 'mj';
const DOCUMENTS = [
  { title: 'Rapport d’anomalie', stage: 1, body: 'Une oscillation temporelle a été enregistrée près du vestiaire à 22 h 14. Trois signatures distinctes se chevauchent.' },
  { title: 'Journal des appels', stage: 2, body: 'À 22 h 11, un appel de 47 secondes est émis depuis le couloir nord. Le terminal déclaré était pourtant hors service.' },
  { title: 'Dossier d’empreintes', stage: 3, body: 'La trace relevée sur l’écrin correspond à un voyageur portant des gants à ancrage chronal de deuxième génération.' },
];

export default function Home() {
  const [game, setGame] = useState<Game | null>(null);
  const [joinCode, setJoinCode] = useState('');
  const [gmToken, setGmToken] = useState('');
  const [code, setCode] = useState('');
  const [tab, setTab] = useState<Tab>('cadenas');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [unlockedStage, setUnlockedStage] = useState<1 | 2 | null>(null);
  const latestGame = useRef<Game | null>(null);
  const actionPending = useRef(false);
  const syncGeneration = useRef(0);

  const applyGame = useCallback((next: Game) => {
    const previous = latestGame.current;
    if (previous?.code === next.code && Date.parse(next.updatedAt) < Date.parse(previous.updatedAt)) return;
    if (previous?.code === next.code && next.stage > previous.stage && previous.stage < 3) {
      setUnlockedStage(previous.stage as 1 | 2);
      setCode('');
      setTab('cadenas');
    } else if (previous?.code !== next.code || next.stage < previous.stage) {
      setUnlockedStage(null);
    }
    latestGame.current = next;
    setGame(next);
  }, []);

  useEffect(() => {
    if (unlockedStage === null) return;
    const timer = window.setTimeout(() => setUnlockedStage(null), 2200);
    return () => window.clearTimeout(timer);
  }, [unlockedStage]);

  const loadGame = useCallback(async (sessionCode: string, silent = false) => {
    if (actionPending.current) return false;
    const generation = syncGeneration.current;
    try {
      const response = await fetch(`/api/games/${sessionCode}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(response.status === 404 ? 'Partie introuvable.' : 'Synchronisation impossible.');
      const data = await response.json() as Game;
      if (actionPending.current || generation !== syncGeneration.current) return false;
      applyGame(data);
      if (!silent) setMessage('Partie synchronisée.');
      return true;
    } catch (error) {
      if (!silent) setMessage(error instanceof Error ? error.message : 'Erreur inconnue.');
      return false;
    }
  }, [applyGame]);

  useEffect(() => {
    queueMicrotask(() => {
      const savedCode = localStorage.getItem('bague-game-code');
      const savedToken = localStorage.getItem('bague-gm-token') ?? '';
      if (savedCode) { setJoinCode(savedCode); setGmToken(savedToken); void loadGame(savedCode, true); }
    });
  }, [loadGame]);

  const currentGameCode = game?.code;
  useEffect(() => {
    if (!currentGameCode) return;
    const timer = window.setInterval(() => void loadGame(currentGameCode, true), 2000);
    return () => window.clearInterval(timer);
  }, [currentGameCode, loadGame]);

  async function createGame() {
    setBusy(true); setMessage('Création de la ligne temporelle…');
    try {
      const response = await fetch('/api/games', { method: 'POST' });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error ?? 'Création impossible.');
      localStorage.setItem('bague-game-code', data.code);
      localStorage.setItem('bague-gm-token', data.gmToken);
      setGmToken(data.gmToken); applyGame(data); setJoinCode(data.code); setTab('cadenas');
      setMessage('Partie créée. Partagez le code aux deux équipes.');
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Erreur inconnue.'); }
    finally { setBusy(false); }
  }

  async function joinGame(event: FormEvent) {
    event.preventDefault();
    const normalized = joinCode.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 6);
    if (normalized.length !== 6) { setMessage('Le code de partie contient six caractères.'); return; }
    setBusy(true);
    const joined = await loadGame(normalized);
    if (joined) {
      localStorage.setItem('bague-game-code', normalized);
      setGmToken(''); localStorage.removeItem('bague-gm-token');
    }
    setBusy(false);
  }

  async function action(body: Record<string, string | boolean>) {
    if (!game || busy || actionPending.current || unlockedStage !== null) return;
    actionPending.current = true;
    syncGeneration.current++;
    setBusy(true);
    try {
      const response = await fetch(`/api/games/${game.code}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error ?? 'Action refusée.');
      applyGame(data);
      if (body.action === 'submit' && data.accepted === true && (data.unlockedStage === 1 || data.unlockedStage === 2)) {
        setUnlockedStage(data.unlockedStage);
        setTab('cadenas');
      }
      setCode(''); setMessage(data.message ?? 'État synchronisé.');
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Erreur inconnue.'); }
    finally { actionPending.current = false; setBusy(false); }
  }

  function leaveGame() {
    localStorage.removeItem('bague-game-code'); localStorage.removeItem('bague-gm-token');
    latestGame.current = null;
    syncGeneration.current++;
    setGame(null); setGmToken(''); setJoinCode(''); setMessage(''); setUnlockedStage(null);
  }

  if (!game) return <main className="app-shell"><section className="portal-card">
    <p className="eyebrow">Registre des lignes temporelles</p><h1>La Bague hors du Temps</h1>
    <p>Créez une partie sur l’appareil du maître du jeu, puis rejoignez-la sur chaque appareil avec le même code.</p>
    <button className="primary" onClick={createGame} disabled={busy}>Créer une partie</button>
    <div className="divider"><span>ou</span></div>
    <form onSubmit={joinGame} className="join-form"><label htmlFor="game-code">Code de partie</label>
      <input id="game-code" className="session-input" value={joinCode} onChange={e => setJoinCode(e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 6))} placeholder="ABC123" />
      <button disabled={busy || joinCode.length !== 6}>Rejoindre</button></form>
    <p className="feedback visible" aria-live="polite">{message}</p>
  </section></main>;

  return <main className="app-shell"><section className="game-frame">
    <header className="topbar"><div><p className="eyebrow">Ligne temporelle</p><strong>{game.code}</strong></div><div className="sync"><i /> Synchronisée</div></header>
    <nav className="tabs" aria-label="Navigation">
      <button className={tab === 'cadenas' ? 'active' : ''} onClick={() => setTab('cadenas')}>Cadenas</button>
      <button className={tab === 'enquete' ? 'active' : ''} onClick={() => setTab('enquete')}>Enquête</button>
      <button className={tab === 'chronologie' ? 'active' : ''} onClick={() => setTab('chronologie')}>Chronologie</button>
      {gmToken && <button className={tab === 'mj' ? 'active' : ''} onClick={() => setTab('mj')}>MJ</button>}
    </nav>
    {tab === 'cadenas' && <div className="panel">
      {unlockedStage !== null ? <div className="unlock-celebration" role="status" aria-live="polite">
        <div className="unlock-emblem" aria-hidden="true">
          <div className="unlock-wave" />
          <svg className="unlock-icon" viewBox="0 0 100 100" fill="none" stroke="currentColor" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round">
            <path className="unlock-shackle" d="M30 46V29a20 20 0 0 1 40 0v17" />
            <rect x="23" y="46" width="54" height="42" rx="7" />
            <path className="unlock-check" d="m37 67 9 9 18-20" />
          </svg>
        </div>
        <p className="eyebrow">Combinaison validée</p>
        <h1>Sceau {unlockedStage === 1 ? 'I' : 'II'} déverrouillé</h1>
        <p>{unlockedStage === 2 ? 'Le continuum se restaure…' : 'Le prochain sceau se révèle…'}</p>
      </div> : game.stage === 3 ? <div className="victory"><div className="sigil complete">✦</div><p className="eyebrow">Continuum restauré</p><h1>Le passage est ouvert</h1><p>Les deux sceaux ont été déverrouillés sur tous les appareils.</p></div> : <>
        <div className="progress"><span className="active">I</span><i/><span className={game.stage === 2 ? 'active' : ''}>II</span></div>
        <div className={`sigil ${game.stage === 2 ? 'second' : ''}`}><span>{game.stage === 1 ? 'I' : 'II'}</span></div>
        <div className="copy"><p className="step-label">Cadenas {game.stage}</p><h1>{game.stage === 1 ? 'Sceau de la mémoire' : 'Sceau de la convergence'}</h1><p>Saisissez la combinaison à quatre chiffres révélée par l’enquête.</p></div>
        <form onSubmit={e => { e.preventDefault(); void action({ action: 'submit', code }); }}><label htmlFor="lock-code">Combinaison</label>
          <input id="lock-code" value={code} onChange={e => { setCode(e.target.value.replace(/\D/g, '').slice(0, 4)); setMessage(''); }} inputMode="numeric" placeholder="0000" />
          <button disabled={busy || code.length !== 4}>Tenter la combinaison</button></form>
        <p className={`feedback ${message ? 'visible' : ''}`}>{message || 'Essais illimités — la progression est partagée.'}</p><p className="attempts">Essais de la partie : {game.attempts}</p>
      </>}
    </div>}
    {tab === 'enquete' && <div className="panel documents"><p className="eyebrow">Archives récupérées</p><h1>Dossier d’enquête</h1>{DOCUMENTS.map(doc => <article key={doc.title} className={game.stage >= doc.stage ? '' : 'locked'}><span>Lot {doc.stage}</span><h2>{game.stage >= doc.stage ? doc.title : 'Document verrouillé'}</h2><p>{game.stage >= doc.stage ? doc.body : 'Stabilisez le prochain sceau pour récupérer cette archive.'}</p></article>)}</div>}
    {tab === 'chronologie' && <div className="panel timeline"><p className="eyebrow">État partagé</p><h1>Chronologie</h1><ol><li className="done"><b>Connexion établie</b><span>Les voyageurs ont rejoint la même ligne.</span></li><li className={game.stage >= 2 ? 'done' : ''}><b>Sceau de la mémoire</b><span>{game.stage >= 2 ? 'Stabilisé.' : 'En attente de combinaison.'}</span></li><li className={game.stage >= 3 ? 'done' : ''}><b>Sceau de la convergence</b><span>{game.stage >= 3 ? 'Stabilisé.' : 'Verrouillé.'}</span></li></ol></div>}
    {tab === 'mj' && gmToken && <div className="panel gm-panel"><p className="eyebrow">Console du chronomancien</p><h1>Contrôle MJ</h1><p>Ces commandes modifient tous les appareils.</p><div className="kill-switch"><h2>Kill switch des cadenas</h2><p>{game.acceptAnyCode ? 'Activé : toute combinaison de quatre chiffres saisie par les joueurs est valide et passe à l’étape suivante.' : 'Désactivé : seules les bonnes combinaisons ouvrent les cadenas.'}</p><button type="button" role="switch" aria-checked={game.acceptAnyCode} onClick={() => action({ action: 'set-bypass', gmToken, enabled: !game.acceptAnyCode })} disabled={busy}>{game.acceptAnyCode ? 'Désactiver le kill switch' : 'Activer le kill switch'}</button><p>Activer ce réglage ne change pas l’étape : les joueurs doivent saisir une combinaison. Réinitialiser la partie le désactive.</p></div><div className="gm-actions"><button onClick={() => action({ action: 'advance', gmToken })} disabled={busy || game.stage === 3}>Débloquer l’étape suivante</button><button className="danger" onClick={() => action({ action: 'reset', gmToken })} disabled={busy}>Réinitialiser la partie</button></div></div>}
    <footer className="game-footer"><span>Dernière évolution : {new Date(game.updatedAt).toLocaleTimeString('fr-FR')}</span><button onClick={leaveGame}>Quitter</button></footer>
  </section></main>;
}
