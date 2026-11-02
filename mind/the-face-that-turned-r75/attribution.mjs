// UNPUBLISHED, never emit visitor data; deterministic synthetic QA only.
export const ENABLED=false;
const allowed={variant:new Set(["text","film"]),topic:new Set(["thatcher","zen12"]),channel:new Set(["direct","search","tiktok","other"]),event:new Set(["guide_open","source_open","offer_intent"])};
export function validateSynthetic(row){if(row===null||typeof row!=="object"||Array.isArray(row)||Object.keys(row).length!==4)return null;for(const k of Object.keys(allowed)){if(!allowed[k].has(row[k]))return null;}return Object.freeze({variant:row.variant,topic:row.topic,channel:row.channel,event:row.event});}
export function syntheticReport(rows){if(!Array.isArray(rows))throw new TypeError("rows expected");const by=new Map();for(const row of rows){const x=validateSynthetic(row);if(!x)continue;const id=[x.variant,x.topic,x.channel,x.event].join("|");by.set(id,(by.get(id)||0)+1);}return [...by].filter(([k,n])=>n>=20).map(([cohort,count])=>({cohort,count})).sort((a,b)=>a.cohort.localeCompare(b.cohort));}
export function sendEvent(){return Object.freeze({enabled:false,dispatched:false});}
