// DISABLED synthetic-only draft design. No hooks, network, cookies, local storage, purchaser data or visitor collection.
export const EVENTS=["guide_view","video_intent","evidence_open","focus_nav_intent","offer_intent"];
export const SOURCES=["search","tiktok","internal","direct","other"];
export const VARIANTS=["text","video"];
export const TOPICS=["doorway","zen12","mind_hub"];
export function isSyntheticRow(row){
  if(!row || typeof row!=="object" || Array.isArray(row) || Object.getPrototypeOf(row)!==Object.prototype)return false;
  const keys=Object.keys(row).sort().join("|");
  return keys==="count|event|source|synthetic|topic|variant" && row.synthetic===true && Number.isSafeInteger(row.count) && row.count>=0
    && EVENTS.includes(row.event) && SOURCES.includes(row.source) && VARIANTS.includes(row.variant) && TOPICS.includes(row.topic);
}
export function summarizeSynthetic(rows,minCell=20){
  if(minCell!==20 || !Array.isArray(rows) || rows.some(r=>!isSyntheticRow(r)))throw Error("Invalid or identifying aggregate");
  const counts=new Map();
  for(const r of rows){const k=JSON.stringify([r.event,r.source,r.topic,r.variant]);counts.set(k,(counts.get(k)||0)+r.count);}
  return [...counts].filter(([,c])=>c>=20).map(([key,count])=>{const [event,source,topic,variant]=JSON.parse(key);return {event,source,topic,variant,count};});
}
// No URL, raw referrer, unique visitor, order ID, phone, email, IP or transaction attribution.
// These synthetic categorical counts cannot establish real conversions or sales.