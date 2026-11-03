// Offline synthetic categorical aggregation ONLY. No browser hooks, storage, network or cookies.
// NOT for deployment. Do not expand this to raw click IDs, URLs, referrers or buyer events.
export const ALLOWED={
  topic:new Set(["zen12","total-focus"]),
  variant:new Set(["text","optional-film"]),
  event:new Set(["guide_view","offer_interest_disabled","focus_link_interest"])
};
export function safeRecord(row){
  if(!row||typeof row!=="object"||Array.isArray(row))throw Error("invalid-row");
  const keys=Object.keys(row).sort();
  if(keys.join(",")!=="event,topic,variant")throw Error("unexpected-fields");
  for(const k of keys)if(typeof row[k]!=="string"||!ALLOWED[k].has(row[k]))throw Error("invalid-category");
  return [row.topic,row.variant,row.event].join("|");
}
export function syntheticAggregate(rows,minGroup=20){
  if(!Array.isArray(rows)||rows.length>5000||minGroup!==20)throw Error("invalid-input");
  const tally=Object.create(null);
  for(const row of rows){const k=safeRecord(row);tally[k]=(tally[k]||0)+1;}
  return Object.entries(tally).filter(([,n])=>n>=20).map(([category,n])=>({category,count:n}));
}
