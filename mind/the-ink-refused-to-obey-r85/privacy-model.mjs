/**
 * Mind R85 privacy model — NOT imported by a site, not a running collector.
 * Use only with hand-written synthetic counts for design review. It is intentionally
 * NOT an analytics service, does not transmit data, and stores no visitor information.
 */
export const MINIMUM_COHORT = 20;
export const TOPICS = Object.freeze(['stroop','attention','suggestion','zen12-guide']);
export const VARIANTS = Object.freeze(['text','film']);
export const SOURCES = Object.freeze(['search','tiktok','internal','direct','other']);
export const ACTIONS = Object.freeze(['guide_open','offer_intent','focus_open']);
const KEYS=['topic','variant','source','action','count'];
function exactObject(x) {
  if(!x || typeof x!=='object' || Array.isArray(x)) return false;
  return Object.keys(x).length === KEYS.length && KEYS.every(k=>Object.hasOwn(x,k));
}
export function acceptSyntheticCounter(x) {
  if(!exactObject(x)) return false; // excludes IP, user_id, email, click URL, UTM strings, device id, cookies
  if(!TOPICS.includes(x.topic)||!VARIANTS.includes(x.variant)||!SOURCES.includes(x.source)||!ACTIONS.includes(x.action))return false;
  return Number.isSafeInteger(x.count) && x.count>=0 && x.count<=1000000;
}
export function summarizeSyntheticRows(rows) {
  if (!Array.isArray(rows)) throw new TypeError('Array required');
  const totals=new Map();
  for(const row of rows){
    if(!acceptSyntheticCounter(row))throw new TypeError('Unknown or identifying field rejected');
    const key=[row.topic,row.variant,row.source,row.action].join('|');
    totals.set(key,(totals.get(key)||0)+row.count);
  }
  return [...totals].filter(([,n])=>n>=MINIMUM_COHORT).sort(([a],[b])=>a.localeCompare(b)).map(([key,count])=>({topic:key.split('|')[0],variant:key.split('|')[1],source:key.split('|')[2],action:key.split('|')[3],count}));
}
// This module has no network imports, persistence, global hooks, request endpoints or tracking IDs.
