/**
 * Final Vestige R65 PROTOTYPE ONLY. This module is not referenced by live CMS.
 * No listener, cookie, fetch, beacon, storage, referrer reading or event binding.
 * It creates no user identifiers and never records visitor data.
 * Any production analytics requires separate privacy review, permitted channels,
 * written affiliate attribution terms, purpose disclosure and founder approval.
 */
export const ACTIVE = false;
export const MIN_GROUP = 20;
const sources = Object.freeze(new Set(['organic','tiktok','internal','direct','unknown']));
const topics = Object.freeze(new Set(['thatcher','attentional-blink','change-blindness','hypnosis-history','zen12-guide','focus']));
const actions = Object.freeze(new Set(['guide_view','video_opt_in','focus_navigation','offer_intent']));
const variants = Object.freeze(new Set(['text','video','not_applicable']));
const keys = Object.freeze(['source','topic','action','variant']);

const exactObject = v => v !== null && Object.getPrototypeOf(v) === Object.prototype &&
  Object.keys(v).length === keys.length &&
  keys.every(k => Object.hasOwn(v,k)) &&
  Object.keys(v).every(k => keys.includes(k));

export function validateSyntheticRecord(record) {
  if (!exactObject(record)) return false;
  return typeof record.source === 'string' && sources.has(record.source)
    && typeof record.topic === 'string' && topics.has(record.topic)
    && typeof record.action === 'string' && actions.has(record.action)
    && typeof record.variant === 'string' && variants.has(record.variant);
}

/**
 * Aggregate PREEXISTING, SYNTHETIC COUNTS. It does not derive any real visitor
 * event, connect to a provider or equate clicks with conversions.
 * Suppress the entire group if n<20; do not emit low-count cells.
 */
export function aggregateSynthetic(rows) {
  if (!Array.isArray(rows) || rows.length > 100000 || rows.some(r=>!validateSyntheticRecord(r))) {
    throw new TypeError('Only bounded, exact-schema synthetic events are accepted.');
  }
  const counts = new Map();
  for(const row of rows) {
    const k = keys.map(field=>row[field]).join('|');
    counts.set(k,(counts.get(k)||0)+1);
  }
  return [...counts.entries()].filter(([,n])=>n>=MIN_GROUP).map(([key,count])=>{
    const [source,topic,action,variant] = key.split('|');
    return {source,topic,action,variant,count};
  }).sort((a,b)=>b.count-a.count);
}

/** Sentinel makes accidental activation fail rather than secretly collect data. */
export function emitOutboundEvent() {
  throw new Error('Not activated: affiliate approvals and privacy release pending.');
}
