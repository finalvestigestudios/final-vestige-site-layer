/** Synthetic, locally invoked measurement protocol ONLY: never import into public WordPress.
 * This file makes ZERO network requests and stores ZERO visitor state.
 * No raw URL, user agent, IP, cookie, name, email, referrer, or affiliate URL fields.
 */
export const ENABLED=false;
const TYPES=new Set(['guide_view','offer_intent','source_click','focus_visit']);
const VARIANTS=new Set(['text','film']);
const ORIGINS=new Set(['tiktok','search','internal','direct','other']);
export function validateSyntheticEvent(event){
 if(!event||typeof event!=='object'||Array.isArray(event))return false;
 const keys=Object.keys(event).sort().join(',');
 if(keys!=='origin,topic,type,variant')return false;
 return TYPES.has(event.type)&&VARIANTS.has(event.variant)&&ORIGINS.has(event.origin)&&event.topic==='zen12-r76';
}
export function aggregateSynthetic(events){
 if(ENABLED)throw Error('Unreviewed instrumentation must remain disabled');
 const counts=new Map();for(const e of events){if(!validateSyntheticEvent(e))throw Error('Invalid or identifying event');const key=[e.type,e.variant,e.origin].join('|');counts.set(key,(counts.get(key)||0)+1)}
 return [...counts].filter(([,n])=>n>=20).map(([k,count])=>({type:k.split('|')[0],variant:k.split('|')[1],origin:k.split('|')[2],count}));
}
