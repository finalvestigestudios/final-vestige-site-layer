/**
 * Final Vestige R49 — privacy-hard-off, SYNTHETIC ONLY.
 * Does not attach to DOM, store cookies/IDs, read referrers, or send network requests.
 * This module is not wired into a live site.
 */
export const ENABLE_REAL_COLLECTION = false;
const options = Object.freeze({
  topic: new Set(['rubber-hand', 'zen12']),
  variant: new Set(['text', 'film']),
  sourceBucket: new Set(['search', 'tiktok', 'internal', 'direct', 'other']),
  action: new Set(['article-view', 'guide-view', 'focus-link', 'authorized-offer-link'])
});
const keys = Object.freeze(['topic','variant','sourceBucket','action']);
export function normalizeSynthetic(raw) {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw) ||
      ![null, Object.prototype].includes(Object.getPrototypeOf(raw))) {
    throw new TypeError('Reject non-plain event');
  }
  const given = Object.keys(raw);
  if (given.length !== keys.length || given.some(k=>!keys.includes(k))) {
    throw new TypeError('Reject missing, extra or identifying fields');
  }
  const out = Object.create(null);
  for (const k of keys) {
    if (typeof raw[k] !== 'string' || !options[k].has(raw[k])) {
      throw new TypeError('Reject unsupported category');
    }
    out[k]=raw[k];
  }
  return Object.freeze(out);
}
export function aggregateSynthetic(records, minCount=20) {
  if (!Array.isArray(records) || minCount!==20) throw new TypeError('Strict synthetic threshold');
  const counts=new Map();
  for (const x of records) {
    const e=normalizeSynthetic(x);
    const k=keys.map(field=>e[field]).join('|');
    counts.set(k,(counts.get(k)||0)+1);
  }
  return [...counts].filter(([,count])=>count>=20).map(([key,count])=>Object.freeze({key,count}));
}
export function collectRealVisitorEvent() {
  throw new Error('HARD OFF: no authorized live visitor collection');
}
