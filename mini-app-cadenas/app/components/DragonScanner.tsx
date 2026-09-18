'use client';

import { ChangeEvent, useEffect, useRef, useState } from 'react';
import Image from 'next/image';

export default function DragonScanner({ disabled, onScan }: { disabled: boolean; onScan: (form: FormData) => Promise<void> }) {
  const camera = useRef<HTMLInputElement>(null);
  const gallery = useRef<HTMLInputElement>(null);
  const [photo, setPhoto] = useState<{ blob: Blob; preview: string; width: number; height: number } | null>(null);
  const [preparing, setPreparing] = useState(false);
  const [error, setError] = useState('');
  const locked = disabled || preparing;

  useEffect(() => () => { if (photo) URL.revokeObjectURL(photo.preview); }, [photo]);

  async function choosePhoto(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;
    setPreparing(true); setError(''); setPhoto(null);
    const original = URL.createObjectURL(file);
    try {
      const image = document.createElement('img');
      image.src = original;
      await image.decode();
      const ratio = Math.min(1, 1400 / Math.max(image.naturalWidth, image.naturalHeight));
      const canvas = document.createElement('canvas');
      canvas.width = Math.max(1, Math.round(image.naturalWidth * ratio));
      canvas.height = Math.max(1, Math.round(image.naturalHeight * ratio));
      const ctx = canvas.getContext('2d');
      if (!ctx) throw new Error('CANVAS_UNAVAILABLE');
      ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
      const blob = await new Promise<Blob>((resolve, reject) => canvas.toBlob(result => result ? resolve(result) : reject(new Error('IMAGE_UNAVAILABLE')), 'image/jpeg', .9));
      setPhoto({ blob, preview: URL.createObjectURL(blob), width: canvas.width, height: canvas.height });
    } catch {
      setError('Cette photo ne peut pas être ouverte. Essayez une photo JPEG ou PNG.');
    } finally { URL.revokeObjectURL(original); setPreparing(false); }
  }

  return <section className="dragon-scanner" aria-label="Scanner le dragon violet" aria-busy={locked}>
    <div className="scan-buttons">
      <button type="button" onClick={() => camera.current?.click()} disabled={locked}>Photographier le dragon</button>
      <button type="button" onClick={() => gallery.current?.click()} disabled={locked}>Choisir une photo</button>
    </div>
    <input ref={camera} type="file" accept="image/*" capture="environment" onChange={choosePhoto} hidden disabled={locked} />
    <input ref={gallery} type="file" accept="image/*" onChange={choosePhoto} hidden disabled={locked} />
    {preparing && <p role="status">Préparation de la photo…</p>}
    {photo && <div className="scan-preview">
      <Image src={photo.preview} alt="Photo du dragon à vérifier" width={photo.width} height={photo.height} unoptimized />
      <button type="button" className="scan-validate" disabled={locked} onClick={() => {
        const form = new FormData(); form.append('photo', photo.blob, 'dragon.jpg'); void onScan(form);
      }}>{disabled ? 'Analyse du dragon…' : 'Vérifier le dragon'}</button>
    </div>}
    {error && <p className="scan-error" role="alert">{error}</p>}
  </section>;
}
