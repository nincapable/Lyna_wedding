'use client';

import { useEffect, useRef, useState } from 'react';
import type { PDFDocumentProxy, PDFDocumentLoadingTask, RenderTask } from 'pdfjs-dist';

export default function PdfViewer({ src, title }: { src: string; title: string }) {
  const container = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const [pdf, setPdf] = useState<PDFDocumentProxy | null>(null);
  const [page, setPage] = useState(1);
  const [zoom, setZoom] = useState(1);
  const [width, setWidth] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [retry, setRetry] = useState(0);
  const [text, setText] = useState('');

  useEffect(() => {
    const element = container.current;
    if (!element) return;
    const observer = new ResizeObserver(() => setWidth(Math.max(1, element.clientWidth - 24)));
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    let cancelled = false;
    let task: PDFDocumentLoadingTask | undefined;
    async function load() {
      try {
        const engine = await import('pdfjs-dist/legacy/build/pdf.mjs');
        if (cancelled) return;
        setLoading(true); setError(''); setPdf(null); setPage(1); setText('');
        const assets = `/pdfjs/${engine.version}/`;
        engine.GlobalWorkerOptions.workerSrc = `${assets}pdf.worker.min.mjs`;
        task = engine.getDocument({ url: src, cMapUrl: `${assets}cmaps/`, cMapPacked: true,
          standardFontDataUrl: `${assets}standard_fonts/`, wasmUrl: `${assets}wasm/`,
        });
        const document = await task.promise;
        if (!cancelled) setPdf(document);
      } catch {
        if (!cancelled) { setError('Ce document n’a pas pu être chargé. Réessayez.'); setLoading(false); }
      }
    }
    void load();
    return () => { cancelled = true; if (task) void task.destroy().catch(() => {}); };
  }, [src, retry]);

  useEffect(() => {
    if (!pdf || !width || !canvas.current) return;
    let cancelled = false;
    let task: RenderTask | undefined;
    const element = canvas.current;
    async function render() {
      try {
        const currentPage = await pdf!.getPage(page);
        if (cancelled) return;
        setLoading(true); setError('');
        const base = currentPage.getViewport({ scale: 1 });
        const viewport = currentPage.getViewport({ scale: width / base.width * zoom });
        // Keep high-DPI pages sharp without allocating huge canvases on phones.
        const pixelRatio = Math.min(window.devicePixelRatio || 1, 2, Math.sqrt(4_000_000 / (viewport.width * viewport.height)));
        element.width = Math.max(1, Math.floor(viewport.width * pixelRatio));
        element.height = Math.max(1, Math.floor(viewport.height * pixelRatio));
        element.style.width = `${viewport.width}px`;
        element.style.height = `${viewport.height}px`;
        const context = element.getContext('2d');
        if (!context) throw new Error('CANVAS_UNAVAILABLE');
        task = currentPage.render({ canvas: element, canvasContext: context, viewport,
          transform: [pixelRatio, 0, 0, pixelRatio, 0, 0], background: '#ffffff',
        });
        await task.promise;
        if (cancelled) return;
        setLoading(false);
        const content = await currentPage.getTextContent();
        if (!cancelled) setText(content.items.map(item => 'str' in item ? item.str : '').join(' '));
      } catch {
        if (!cancelled) { setLoading(false); setError('Cette page n’a pas pu être affichée. Réessayez.'); }
      }
    }
    void render();
    return () => { cancelled = true; task?.cancel(); };
  }, [pdf, page, zoom, width]);

  return <section className="pdf-viewer" aria-label={title}>
    <div className="pdf-toolbar" aria-label="Commandes du document">
      <div className="pdf-page-controls">
        <button type="button" disabled={!pdf || loading || page === 1} onClick={() => { setLoading(true); setPage(page - 1); }}>← Précédente</button>
        <span aria-live="polite">{pdf ? `Page ${page} / ${pdf.numPages}` : 'Chargement…'}</span>
        <button type="button" disabled={!pdf || loading || page === pdf.numPages} onClick={() => { setLoading(true); setPage(page + 1); }}>Suivante →</button>
      </div>
      <div className="pdf-zoom-controls">
        <button type="button" aria-label="Réduire le zoom" disabled={!pdf || loading || zoom <= .75} onClick={() => setZoom(Math.max(.75, zoom - .25))}>−</button>
        <span>{Math.round(zoom * 100)} %</span>
        <button type="button" aria-label="Agrandir le document" disabled={!pdf || loading || zoom >= 3} onClick={() => setZoom(Math.min(3, zoom + .25))}>+</button>
        <button type="button" disabled={!pdf || loading || zoom === 1} onClick={() => setZoom(1)}>Ajuster</button>
      </div>
    </div>
    {loading && !error && <p className="pdf-status" role="status">Affichage du document…</p>}
    {error && <div className="pdf-status" role="alert"><p>{error}</p><button type="button" className="reader-back" onClick={() => setRetry(retry + 1)}>Réessayer</button></div>}
    <div className="pdf-pages" ref={container} aria-busy={loading}>
      <canvas ref={canvas} role="img" aria-label={`${title} — page ${page}`} hidden={!pdf || Boolean(error)} />
    </div>
    <p className="pdf-accessible-text">{text}</p>
  </section>;
}
