/**
 * FV Mind R51: privacy-hard-OFF, synthetic-only attribution design.
 * No browser listeners, network APIs, cookies, localStorage, IP, timestamps, URLs,
 * identifiers, referrer strings, forms or subscriber events.
 * This module is NOT imported into WordPress candidate pages.
 */
export const ATTRIBUTION_ENABLED = false;
const EVENTS = Object.freeze(['mind_view','investigation_view','guide_view','film_start','focus_link','offer_intent']);
const CHANNELS = Object.freeze(['organic','tiktok','internal','direct','other']);
const VARIANTS = Object.freeze(['A','B','none']);
const TOPICS = Object.freeze(['attentional_blink','suggestion','zen12','focus','other']);
const ALLOWED = Object.freeze(['event','channel','variant','topic']);
export const REPORT_MIN_COUNT = 20;
export function validateSyntheticEvent(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) return {ok:false,reason:'not-an-object'};
  const keys=Object.keys(input);
  if (keys.length!==ALLOWED.length || keys.some(k=>!ALLOWED.includes(k))) return {ok:false,reason:'unexpected-or-missing-fields'};
  if(!EVENTS.includes(input.event) || !CHANNELS.includes(input.channel) ||
     !VARIANTS.includes(input.variant) || !TOPICS.includes(input.topic)) return {ok:false,reason:'unknown-enum'};
  return {ok:true, event:Object.freeze({...input})};
}
export function recordLiveEvent(_unused) {
  // Intentionally does not parse, validate, retain or transmit any input.
  return Object.freeze({recorded:false, reason:'OFF: no visitor telemetry or affiliate activation'});
}
export function aggregateSyntheticRows(rows) {
  if (!Array.isArray(rows)) throw new TypeError('synthetic rows only');
  const count=new Map();
  for(const row of rows){
    const v=validateSyntheticEvent(row);
    if(!v.ok) throw new TypeError('invalid synthetic event: '+v.reason);
    const key=[row.event,row.channel,row.variant,row.topic].join('|');
    count.set(key,(count.get(key)||0)+1);
  }
  // No small-cell enumeration: return only groups with >=20 synthetic rows.
  return Object.freeze([...count.entries()]
    .filter(([,n])=>n>=REPORT_MIN_COUNT)
    .map(([key,count])=>({cell:key,count}))
    .sort((a,b)=>a.cell.localeCompare(b.cell)));
}
