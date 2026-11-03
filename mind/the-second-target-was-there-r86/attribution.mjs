// DISABLED reference model. Unimported in every page and NEVER run against visitors.
// No IP, user-agent, email, full URL, referrer URL, user ID, order ID or timestamp accepted.
export const enabled=false;
const sources=new Set(["organic","tiktok","direct","other"]);
const topics=new Set(["attentional-blink","zen12-guide","mind-hub"]);
const types=new Set(["guide_view","offer_control_view","proposed_outbound"]);
export function sanitizeSyntheticEvent(input){
 if(!input||typeof input!=="object"||Array.isArray(input))throw new TypeError("event object required");
 const ks=Object.keys(input).sort();
 if(JSON.stringify(ks)!==JSON.stringify(["event","source","topic"]))throw new Error("reject extra/missing event field; no PII");
 const {source,topic,event}=input;
 if(!sources.has(source)||!topics.has(topic)||!types.has(event))throw new Error("unapproved category");
 return {source,topic,event};
}
export function aggregateSyntheticEvents(rows){
 if(!Array.isArray(rows))throw new TypeError("rows must be array");
 const sums=new Map();for(const r of rows){const x=sanitizeSyntheticEvent(r);const k=[x.source,x.topic,x.event].join("|");sums.set(k,(sums.get(k)||0)+1)}
 return [...sums].filter(([k,n])=>n>=20).map(([k,n])=>({cell:k,count:n})).sort((a,b)=>a.cell.localeCompare(b.cell));
}
// min-20 suppression is not a guarantee of anonymity; no deployment or event collection is authorized.
