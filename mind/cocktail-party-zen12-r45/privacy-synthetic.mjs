/**
 * R45 attribution design — NO LIVE COLLECTION / NO NETWORK / NO STORAGE.
 * Requires explicit founder and legal approval plus staging privacy review
 * before any separate implementation can measure real visitors.
 * This module is intentionally safe to import in offline tests.
 */
export const LIVE_COLLECTION_ENABLED = false;
export const MIN_GROUP = 20;
const allowed = Object.freeze({
  variant: Object.freeze(["A","B"]),
  source: Object.freeze(["organic","tiktok","direct","other"]),
  topic: Object.freeze(["attention","history","practice","audio"]),
  event: Object.freeze(["guide_view","qualified_outbound"])
});
const keys = Object.freeze(Object.keys(allowed));
export function validateSyntheticObservation(row) {
  if (!row || typeof row!=="object" || Array.isArray(row)) throw new TypeError("object required");
  const provided = Object.keys(row);
  if (provided.length!==keys.length || provided.some(k=>!keys.includes(k))) throw new Error("unknown field or missing field: no PII");
  const safe={};
  for(const key of keys){
    if(typeof row[key]!=="string" || !allowed[key].includes(row[key])) throw new Error("value outside categorical allowlist");
    safe[key]=row[key];
  }
  return Object.freeze(safe);
}
export function aggregateSyntheticObservations(rows) {
  if(!Array.isArray(rows)) throw new TypeError("array required");
  const cells=new Map();
  for(const raw of rows){
    const row=validateSyntheticObservation(raw);
    const key=keys.map(k=>row[k]).join("|");
    cells.set(key,(cells.get(key)||0)+1);
  }
  return Array.from(cells,([key,n])=>({key,count:n}))
    .filter(x=>x.count>=MIN_GROUP)
    .sort((a,b)=>a.key.localeCompare(b.key));
}
export function recordRealVisitorEvent() {
  throw new Error("HARD_HOLD: no live affiliate attribution, events, cookies, storage or network");
}
