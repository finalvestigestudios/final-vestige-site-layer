// Prototype only. NEVER add to WP or run on real visitors without privacy/legal review.
export const ENABLED = false;
const TOPICS = new Set(["historical-suggestion","meditation-format","perception"]);
const VARIANTS = new Set(["A-text","B-film"]);
const CHANNELS = new Set(["direct","search","organic-social","internal"]);
const EVENTS = new Set(["offer-intent","guide-read","focus-intent"]);
export function validateSyntheticEvent(x) {
 if(ENABLED || !x || typeof x!=="object" || Array.isArray(x)) return null;
 const keys=Object.keys(x);
 if(keys.length!==4 || keys.some(k=>!["topic","variant","channel","event"].includes(k))) return null;
 if(!TOPICS.has(x.topic)||!VARIANTS.has(x.variant)||!CHANNELS.has(x.channel)||!EVENTS.has(x.event)) return null;
 return Object.freeze({...x});
}
export function aggregateSynthetic(events, minCohort=20){
 if(ENABLED) throw Error("Live attribution not authorized");
 if(!Number.isInteger(minCohort)||minCohort<20) throw Error("Minimum cohort 20");
 const counts=new Map();
 for(const item of events){const x=validateSyntheticEvent(item);if(!x)continue;
   const key=[x.topic,x.variant,x.channel,x.event].join("|");
   counts.set(key,(counts.get(key)||0)+1);
 }
 return [...counts.entries()].filter(([,v])=>v>=minCohort).map(([category,count])=>({category,count}));
}
