// R89: synthetic-only. NOT imported into WordPress, no network, no cookies, no browser APIs.
export const ENABLED=false;
export const MIN_GROUP=20;
const allowed={event:new Set(['guide_view','guide_source_click','focus_internal_click','offer_control_seen','synthetic_outbound_click']),source:new Set(['organic_search','tiktok','internal','direct_unknown']),topic:new Set(['zen12','mcgurk']),variant:new Set(['A','B'])};
export function validateSynthetic(value){
  if(!value||Object.getPrototypeOf(value)!==Object.prototype)throw Error('plain object required');
  if(value.provenance!=='synthetic_test')throw Error('synthetic only');
  const keys=Object.keys(value);
  if(keys.length!==5||keys.some(k=>!['provenance','event','source','topic','variant'].includes(k)))throw Error('nonallowlisted field');
  const r={};
  for(const key of Object.keys(allowed)){if(typeof value[key]!=='string'||!allowed[key].has(value[key]))throw Error('nonallowlisted value');r[key]=value[key];}
  return r;
}
export function aggregateSynthetic(events){
  if(!Array.isArray(events))throw Error('array required');
  const counts=new Map();
  for(const obj of events){const r=validateSynthetic(obj);const k=JSON.stringify([r.event,r.source,r.topic,r.variant]);counts.set(k,(counts.get(k)||0)+1);}
  return [...counts].filter(([k,n])=>n>=MIN_GROUP).map(([k,count])=>{const [event,source,topic,variant]=JSON.parse(k);return {event,source,topic,variant,count};});
}
export function productionTrack(){throw Error('DISABLED: real visitor collection not authorized');}
