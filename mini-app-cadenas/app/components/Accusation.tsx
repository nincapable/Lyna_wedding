'use client';
import { useState } from 'react';
import Image from 'next/image';
import { SUSPECTS } from '@/lib/suspects';
import PdfViewer from '@/app/components/PdfViewer';

export default function Accusation({ gameCode }: { gameCode: string }) {
  const [selected, setSelected] = useState('');
  const [result, setResult] = useState<{ correct: boolean; suspectId: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [report, setReport] = useState(false);
  const suspect = SUSPECTS.find(suspect => suspect.id === selected);
  async function confirm() {
    if (!suspect || busy || result) return;
    setBusy(true); setError('');
    try {
      const response = await fetch(`/api/games/${gameCode}/accuse`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ suspectId: selected }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error ?? 'Confirmation impossible.');
      setResult(data);
    } catch (error) { setError(error instanceof Error ? error.message : 'Confirmation impossible.'); }
    finally { setBusy(false); }
  }
  if (report && result) return <div className="panel documents"><section className="document-reader">
    <button className="reader-back" onClick={() => setReport(false)}>← Retour à la conclusion</button>
    <h1>Rapport d’enquête</h1><PdfViewer src={`/api/games/${gameCode}/report`} title="Rapport d’enquête — résolution" />
  </section></div>;
  return <div className="panel accusation-panel">
    {result ? <section className="investigation-result" aria-live="polite">
      <Image src="/images/anneau.svg" alt={result.correct ? 'Félicitations : l’anneau est retrouvé' : 'L’anneau a été replacé à 21 h 16'} width={400} height={280} className="result-ring" />
      <p className="eyebrow">{result.correct ? 'Enquête résolue' : 'Une autre histoire se révèle'}</p>
      <h1>{result.correct ? 'Félicitations !' : 'Le mystère demeure'}</h1>
      {result.correct ? <p>Vous avez démasqué {SUSPECTS.find(suspect => suspect.id === result.suspectId)?.name}. L’anneau a été retrouvé : découvrez toute la vérité dans le rapport d’enquête.</p> : <p>Le suspect désigné n’est pas le coupable. L’anneau a été replacé à 21 h 16 : visiblement, le voleur n’était pas mal intentionné. Une équipe indépendante du futur a produit ce rapport pour éclaircir les événements.</p>}
      <button className="primary" onClick={() => setReport(true)}>Consulter le rapport d’enquête</button>
      {!result.correct && <button className="primary" onClick={() => { setResult(null); setSelected(''); setError(''); setReport(false); }}>Réessayer — choisir un autre suspect</button>}
    </section> : <>
      <p className="eyebrow">Dernière déduction</p><h1>Désignez le coupable</h1>
      <p>Sélectionnez un suspect, puis confirmez votre accusation pour découvrir la conclusion de l’enquête.</p>
      <fieldset className="suspect-list" disabled={busy}><legend>Les suspects</legend>
        {SUSPECTS.map(suspect => <label key={suspect.id} className={`suspect-card ${selected === suspect.id ? 'selected' : ''}`}>
          <input type="radio" name="suspect" value={suspect.id} checked={selected === suspect.id} onChange={() => setSelected(suspect.id)} />
          <span><strong>{suspect.name}</strong><small>{suspect.description}</small></span>
        </label>)}
      </fieldset>
      <button className="primary" disabled={!suspect || busy} onClick={confirm}>{busy ? 'Vérification…' : suspect ? `Désigner ${suspect.name} coupable` : 'Confirmer l’accusation'}</button>
      {error && <p className="feedback visible" role="alert">{error}</p>}
    </>}
  </div>;
}
