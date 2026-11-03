// R105 SYNTHETIC-ONLY. No collection, storage, cookies, pixels or network transport.
export const LIVE_COLLECTION_ENABLED=false;
const allowed={
  source:new Set(["organic","tiktok","direct","other"]),
  variant:new Set(["text","film"]),
  action:new Set(["guide_view","focus_interest","merchant_interest"])
};
export function acceptSynthetic(row){
  if(row===null||typeof row!=="object"||Array.isArray(row))throw new TypeError("plain record required");
  const keys=Object.keys(row).sort();
  if(keys.join(",")!=="action,source,variant")throw new Error("unexpected field rejected");
  for(const k of keys)if(!allowed[k].has(row[k]))throw new Error("invalid category");
  return Object.freeze({source:row.source,variant:row.variant,action:row.action});
}
export function aggregateSynthetic(rows,k=20){
  if(!Number.isInteger(k)||k<20)throw new Error("minimum cell size 20");
  if(!Array.isArray(rows))throw new TypeError("rows required");
  const counts=new Map();
  for(const row of rows){const r=acceptSynthetic(row);const key=[r.source,r.variant,r.action].join("/");counts.set(key,(counts.get(key)||0)+1);}
  return [...counts].filter(([key,count])=>count>=k).map(([bucket,n])=>({bucket,n})).sort((a,b)=>a.bucket.localeCompare(b.bucket));
}
export function recordLiveEvent(){throw new Error("LIVE COLLECTION DISABLED: partner and privacy review missing");}
