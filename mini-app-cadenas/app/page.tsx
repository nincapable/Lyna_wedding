'use client';

import { FormEvent, useEffect, useRef, useState } from 'react';

// Remplace simplement ces valeurs pour modifier les codes acceptés.
const VALID_CODES = {
  lock1: ['3816', '7482', '1904', '2631', '5279'],
  lock2: ['2543', '9062', '4418', '1357', '6820'],
};

type Stage = 1 | 2 | 3;

export default function Home() {
  const [stage, setStage] = useState<Stage>(1);
  const [code, setCode] = useState('');
  const [message, setMessage] = useState('');
  const [attempts, setAttempts] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const stored = Number(localStorage.getItem('bague-stage')) as Stage;
    if (stored === 2 || stored === 3) setStage(stored);
  }, []);

  useEffect(() => { inputRef.current?.focus(); }, [stage]);

  function submit(event: FormEvent) {
    event.preventDefault();
    if (code.length !== 4) {
      setMessage('Le sceau attend exactement quatre chiffres.');
      return;
    }
    const accepted = stage === 1 ? VALID_CODES.lock1.includes(code) : VALID_CODES.lock2.includes(code);
    setAttempts((value) => value + 1);
    if (!accepted) {
      setMessage('Combinaison refusée. La boucle tient encore — réessayez.');
      setCode('');
      return;
    }
    const nextStage = (stage + 1) as Stage;
    localStorage.setItem('bague-stage', String(nextStage));
    setStage(nextStage);
    setCode('');
    setMessage('');
    setAttempts(0);
  }

  function resetGame() {
    localStorage.removeItem('bague-stage');
    setStage(1);
    setCode('');
    setMessage('La boucle a été réinitialisée.');
    setAttempts(0);
  }

  if (stage === 3) {
    return <main className="app-shell"><section className="success-card" aria-live="polite">
      <div className="card-name"><span>Restauration du continuum</span><span className="mana-row"><i className="mana sun">✦</i><i className="mana arcane">◈</i></span></div>
      <div className="sigil complete" aria-hidden="true">✦</div>
      <p className="eyebrow">Convergence restaurée</p>
      <h1>L’étape suivante est déverrouillée</h1>
      <p>Les deux sceaux ont reconnu vos combinaisons. Le passage temporel est désormais stable.</p>
      <div className="success-code">PASSAGE OUVERT</div>
      <button className="reset-button" onClick={resetGame}>Recommencer la partie</button>
    </section></main>;
  }

  return <main className="app-shell"><section className="lock-card">
    <div className="card-name"><span>{stage === 1 ? 'Sceau de la mémoire' : 'Sceau de la convergence'}</span><span className="mana-row" aria-hidden="true"><i className="mana void">◇</i><i className={`mana ${stage === 1 ? 'arcane' : 'ember'}`}>{stage === 1 ? '◈' : '✹'}</i></span></div>
    <header><p className="eyebrow">Artefact temporel légendaire</p><div className="progress" aria-label={`Étape ${stage} sur 2`}><span className="active">I</span><i /><span className={stage === 2 ? 'active' : ''}>II</span></div></header>
    <div className="art-frame"><div className={`sigil ${stage === 2 ? 'second' : ''}`} aria-hidden="true"><span>{stage === 1 ? 'I' : 'II'}</span></div><div className="time-rings" /></div>
    <div className="copy"><p className="step-label">Cadenas {stage}</p><h1>{stage === 1 ? 'Le sceau de la mémoire' : 'Le sceau de la convergence'}</h1><p>Saisissez la combinaison à quatre chiffres révélée par votre enquête.</p></div>
    <form onSubmit={submit}>
      <label htmlFor="code">Combinaison</label>
      <input ref={inputRef} id="code" value={code} onChange={(event) => { setCode(event.target.value.replace(/\D/g, '').slice(0, 4)); setMessage(''); }} inputMode="numeric" pattern="[0-9]*" autoComplete="off" placeholder="0000" aria-describedby="feedback" />
      <button type="submit" disabled={code.length !== 4}>Tenter la combinaison</button>
    </form>
    <p id="feedback" className={`feedback ${message ? 'visible' : ''}`} aria-live="polite">{message || 'Vous pouvez faire autant d’essais que nécessaire.'}</p>
    {attempts > 0 && <p className="attempts">Essais sur ce cadenas : {attempts}</p>}
    <footer className="card-footer"><span>« Le temps cède à ceux qui comprennent son langage. »</span><b>Ⅰ / Ⅱ</b></footer>
  </section></main>;
}
