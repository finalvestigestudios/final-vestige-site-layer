/** R79 disabled synthetic-only measurement prototype; no browser collection. */
export const ACTIVATION_ENABLED=false;
export const REAL_VISITORS_COLLECTED=0;
const topics=new Set(['gorilla','zen12','puysegur','focus']);
const sources=new Set(['organic','tiktok','internal','direct','other']);
const variants=new Set(['A','B']);
const intents=new Set(['guide_read','offer_intent','focus_navigation']);
export function syntheticOnly(r){
 if(ACTIVATION_ENABLED||!r||typeof r!=='object'||Array.isArray(r))return null;
 if(JSON.stringify(Object.keys(r).sort())!==JSON.stringify(['intent','source','topic','variant']))return null;
 if(typeof r.topic!=='string'||!topics.has(r.topic)||typeof r.source!=='string'||!sources.has(r.source)||typeof r.variant!=='string'||!variants.has(r.variant)||typeof r.intent!=='string'||!intents.has(r.intent))return null;
 return Object.freeze({topic:r.topic,source:r.source,variant:r.variant,intent:r.intent});
}
export function groupedSynthetic(rows){
 if(!Array.isArray(rows))return [];
 const m=new Map();
 for(const raw of rows){const r=syntheticOnly(raw);if(!r)continue;const key=[r.topic,r.source,r.variant,r.intent].join(':');m.set(key,(m.get(key)||0)+1);}
 return [...m].filter(([,n])=>n>=20).map(([group,n])=>Object.freeze({group,count:n}));
}
// No real events, cookies, network, URL strings, referrers, timestamp, UTM, PII, localStorage or fingerprint.
