// Final Vestige Mind R106. SYNTHETIC-only event contract; no browser API, no storage, no network, no real visitor capture.
const FIELDS=['page','variant','source','event'];
const PAGE='zen12-evidence-guide';
const VARIANTS=['A','B'];
const SOURCES=['direct','search','tiktok','internal','other'];
const EVENTS=['guide_view','source_open','focus_intent','offer_intent'];
export function validateSynthetic(row){
  if(!row||typeof row!=='object'||Array.isArray(row))throw Error('invalid row');
  if(Object.keys(row).some(k=>!FIELDS.includes(k)))throw Error('unknown or identifying field');
  if(Object.keys(row).length!==4)throw Error('incomplete');
  if(row.page!==PAGE||!VARIANTS.includes(row.variant)||!SOURCES.includes(row.source)||!EVENTS.includes(row.event))throw Error('unknown categorical value');
  return Object.freeze({...row});
}
export function aggregateSynthetic(rows, minimum=20){
  if(minimum!==20)throw Error('minimum is fixed at twenty');
  const count=new Map();
  for(const value of rows){const r=validateSynthetic(value);const key=[r.page,r.variant,r.source,r.event].join('|');count.set(key,(count.get(key)||0)+1);}
  return Object.freeze([...count.entries()].filter(([,n])=>n>=20).map(([key,n])=>({group:key,count:n})));
}
export function captureLiveEvent(){throw Error('live tracking explicitly disabled pending permission and privacy review');}
export const ACTIVE=false;