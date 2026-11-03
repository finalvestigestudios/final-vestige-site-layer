/** DISABLED synthetic-only attribution prototype. Do not import into production.
 * These events are NOT anonymous, NOT active, and NOT sales evidence.
 * No cookies, user IDs, IPs, referrers, full URLs, emails or network calls.
 */
export const ENABLED=false;
export const TOPICS=Object.freeze(['attention','suggestion','meditation']);
export const VARIANTS=Object.freeze(['text','film']);
export const ACTIONS=Object.freeze(['guide_view','source_click','offer_intent']);
const keys=['topic','variant','action'];
export function validateSyntheticEvent(v){
 if(!v||Array.isArray(v)||typeof v!=='object') throw Error('Invalid event');
 if(Object.keys(v).length!==keys.length || keys.some(k=>!Object.hasOwn(v,k))) throw Error('Unexpected or missing field');
 if(!TOPICS.includes(v.topic)||!VARIANTS.includes(v.variant)||!ACTIONS.includes(v.action)) throw Error('Unknown category');
 return Object.freeze({...v});
}
export function aggregateSynthetic(rows,minCell=20){
 if(!Number.isInteger(minCell)||minCell<20) throw Error('Minimum cell >=20');
 const counts=new Map();
 for(const row of rows){ const e=validateSyntheticEvent(row),k=[e.topic,e.variant,e.action].join('|'); counts.set(k,(counts.get(k)||0)+1); }
 return Object.freeze([...counts].filter(([,count])=>count>=minCell).map(([key,count])=>({key,count})).sort((a,b)=>a.key.localeCompare(b.key)));
}
/** Future measurement ONLY after partner terms/privacy review:
 * consent-free anonymous-looking web events are not assumed anonymous.
 * Avoid session identifiers/PII, exclude merchant buyer-level data,
 * use approved aggregates with suppression, publish source methodology.
 */