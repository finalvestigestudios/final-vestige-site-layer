// Inert, first-party-only SYNTHETIC cohort planning. No browser APIs, cookies, IP, referrer, URLs, merchant pixels or requests.
export const ACTIVE=false;
export const MIN_GROUP_SIZE=20;
const KEYS=["source","topic","variant","clicked"];
const ALLOWED={source:["organic","tiktok","direct","internal"],topic:["binaural-beats","zen12-guide"],variant:["text","film"]};
export function validateSyntheticInput(row){
 if(!row||typeof row!=="object"||Array.isArray(row))throw Error("Invalid synthetic record");
 if(Object.keys(row).some(k=>!KEYS.includes(k))||Object.keys(row).length!==4)throw Error("Unexpected field / identifying data");
 for(const k of ["source","topic","variant"])if(!ALLOWED[k].includes(row[k]))throw Error("Unexpected cohort value");
 if(typeof row.clicked!=="boolean")throw Error("Invalid synthetic event");
 return Object.freeze({...row});
}
export function collectOutboundEvent(){throw Error("LIVE_COLLECTION_DISABLED: merchant links and instrumentation not activated");}
export function summarizeSynthetic(records){
 if(!Array.isArray(records))throw Error("Records must be synthetic array");
 const m=new Map();
 for(const r of records){const x=validateSyntheticInput(r),k=[x.source,x.topic,x.variant].join("|");const z=m.get(k)||{source:x.source,topic:x.topic,variant:x.variant,n:0,clicks:0};z.n++;z.clicks+=Number(x.clicked);m.set(k,z)}
 return [...m.values()].filter(x=>x.n>=MIN_GROUP_SIZE).sort((a,b)=>(a.source+a.topic+a.variant).localeCompare(b.source+b.topic+b.variant)).map(x=>({...x,rate:x.clicks/x.n}));
}
