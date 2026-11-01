/** R54: no tracking, storage, network calls or cookies. Pure synthetic validation only. */
export const ATTRIBUTION_ENABLED = false;
const ALLOWED = { topic:new Set(['gorilla','zen12-guide']), channel:new Set(['organic','tiktok','direct','internal']), variant:new Set(['A','B']), action:new Set(['view','guide_read','focus_link','outbound_intent'])};
export function validateSyntheticEvent(value){ if(!value||Array.isArray(value)||typeof value!=='object') return null;const keys=Object.keys(value);if(keys.length!==4||keys.some(k=>!(k in ALLOWED))) return null;const row={};for(const k of Object.keys(ALLOWED)){if(typeof value[k]!=='string'||!ALLOWED[k].has(value[k])) return null;row[k]=value[k]}return row;}
export function reportSyntheticGroups(rows){const grouped=new Map();for(const row of rows){const safe=validateSyntheticEvent(row);if(!safe)continue;const key=Object.values(safe).join('|');grouped.set(key,(grouped.get(key)||0)+1)}return [...grouped.entries()].filter(([,count])=>count>=20).map(([key,count])=>({key,count}));}
export function measurementEnabled(){return false;}
// No browser listeners; no localStorage, cookie, referrer, URL query, IP or timestamps. Only a proposal for future aggregated analytics approval.
