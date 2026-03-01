/*
  Data Ingestion Worker
  - Fetches CORS-enabled sources
  - Transforms text chunks
  - Returns records ready for vectorization + IndexedDB insertion
*/

self.onmessage = async (event) => {
  const { type, payload } = event.data || {};

  if (type !== 'INGEST_SOURCES') return;

  const sources = payload?.sources || [];
  const docs = [];
  const errors = [];

  for (const source of sources) {
    try {
      const res = await fetch(source.url, { mode: 'cors' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const text = await res.text();
      const chunks = chunkText(text, 480);
      for (const [i, chunk] of chunks.entries()) {
        docs.push({
          id: `${source.id || source.url}-${i}`,
          source: source.url,
          text: chunk,
          metadata: source.metadata || {},
          ts: Date.now(),
        });
      }
    } catch (err) {
      errors.push({ source: source.url, error: String(err) });
    }
  }

  self.postMessage({
    type: 'INGEST_RESULT',
    payload: {
      docs,
      errors,
      count: docs.length,
      failed: errors.length,
    },
  });
};

function chunkText(input, size) {
  const clean = input.replace(/\s+/g, ' ').trim();
  if (!clean) return [];

  const out = [];
  for (let i = 0; i < clean.length; i += size) {
    out.push(clean.slice(i, i + size));
  }
  return out;
}
