// SYNTHETIC-ONLY attribution research model: NOT imported on any page, NOT deployed.
// Not a user tracker. No I/O, no browser APIs, no network calls, no cookies.
// Future live collection requires separate founder privacy approval, legal review and QA.
export const ACTIVE = false;
const eventNames=new Set(["guide_open","offer_section_view","outbound_click_future"]);
const topics=new Set(["thatcher","zen12","mesmerism","change_blindness","other"]);
const surfaces=new Set(["organic","tiktok","site_internal","direct","other"]);
const versions=new Set(["A","B"]);
const exactKeys=["event","topic","surface","variant","count"];
export function validateSynthetic(row){
  if(row===null||typeof row!=="object"||Array.isArray(row)) throw Error("invalid synthetic record");
  const got=Object.keys(row).sort(),want=[...exactKeys].sort();
  if(got.length!==want.length||got.some((x,i)=>x!==want[i])) throw Error("unexpected keys including possible identifier");
  if(!eventNames.has(row.event)||!topics.has(row.topic)||!surfaces.has(row.surface)||!versions.has(row.variant))throw Error("non-allowlisted category");
  if(!Number.isSafeInteger(row.count)||row.count<1||row.count>100000)throw Error("invalid aggregate count");
  return Object.freeze({...row});
}
export function summarizeSyntheticOnly(rows,minCell=20){
  if(ACTIVE)throw Error("prototype must remain disabled");
  if(!Array.isArray(rows)||minCell<20||!Number.isSafeInteger(minCell))throw Error("invalid synthetic input");
  const groups=new Map();
  for(const raw of rows){
    const r=validateSynthetic(raw);
    const key=[r.event,r.topic,r.surface,r.variant].join("|");
    groups.set(key,(groups.get(key)||0)+r.count);
  }
  // Suppression on aggregates is only a display practice, NOT a privacy guarantee.
  return [...groups.entries()].filter(([,n])=>n>=minCell).sort((a,b)=>a[0].localeCompare(b[0])).map(([key,n])=>({cell:key,total:n}));
}
// This module has no collection, listener, outbound link, storage or reporting integration.
