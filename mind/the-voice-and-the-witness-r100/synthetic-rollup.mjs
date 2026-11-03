/* Synthetic-only, no DOM hooks, no browser invocation, no network, no persistence.
   Do NOT deploy/event-collect before partner acceptance, link approval, privacy review.
   Aggregate rollups only: no users, sessions, times, referrers, raw URLs, IDs or querystrings.
*/
const allowedSources=new Set(["tiktok","organic_search","internal_archive","direct_unknown"]);
const allowedVariants=new Set(["text","optional_video"]);
const allowedActions=new Set(["guide_view","offer_interest"]);
function categoryEvent(obj){
 if(!obj||typeof obj!=="object"||Array.isArray(obj))throw new Error("invalid event");
 const keys=Object.keys(obj).sort();
 if(keys.join(",")!=="action,source,variant")throw new Error("refused unknown or identifying field");
 for(const [k,choices] of [["action",allowedActions],["source",allowedSources],["variant",allowedVariants]]){
  if(typeof obj[k]!=="string"||!choices.has(obj[k]))throw new Error("invalid category "+k);
 }
 return obj;
}
function safeRollup(events, minGroup=20) {
 if(!Array.isArray(events)||!Number.isSafeInteger(minGroup)||minGroup<20)throw new Error("invalid rollup");
 const counts=new Map();
 for(const ev of events){const {action,source,variant}=categoryEvent(ev);const key=[source,variant,action].join("|");counts.set(key,(counts.get(key)||0)+1)}
 return [...counts].filter(([k,n])=>n>=minGroup).sort(([a],[b])=>a.localeCompare(b)).map(([key,count])=>{const [source,variant,action]=key.split("|");return {source,variant,action,count}})
}
export {categoryEvent,safeRollup};
// Usage: ONLY synthetic unit tests. Event activation and a minimal privacy notice require separate approval.
