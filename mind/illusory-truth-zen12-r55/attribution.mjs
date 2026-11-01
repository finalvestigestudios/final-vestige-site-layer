/** R55: Pure synthetic prototype. NO collection, network, cookies, persistence or browser instrumentation. */
export const ATTRIBUTION_ENABLED = false;
const ALLOWED = Object.freeze({
 topic: new Set(['illusory-truth','zen12-guide']),
 channel: new Set(['organic','tiktok','direct','internal']),
 variant: new Set(['A','B']),
 action: new Set(['guide_view','source_read','focus_intent','outbound_intent'])
});
export function measurementEnabled(){ return false; }
export function validateSyntheticEvent(value){
 if(value===null || typeof value!=='object' || Array.isArray(value))return null;
 if(Object.getPrototypeOf(value)!==Object.prototype)return null;
 const keys=Object.keys(value);
 if(keys.length!==4 || keys.some(k=>!Object.prototype.hasOwnProperty.call(ALLOWED,k)))return null;
 const sanitized={};
 for(const key of Object.keys(ALLOWED)){
   if(typeof value[key]!=='string'||!ALLOWED[key].has(value[key]))return null;
   sanitized[key]=value[key];
 }
 return sanitized;
}
export function aggregateSyntheticRows(rows){
 if(!Array.isArray(rows)||rows.length>100000)return [];
 const counts=new Map();
 for(const row of rows){
  const safe=validateSyntheticEvent(row);
  if(!safe)continue;
  const k=[safe.topic,safe.channel,safe.variant,safe.action].join('|');
  counts.set(k,(counts.get(k)||0)+1);
 }
 return [...counts.entries()].filter(([,count])=>count>=20).sort((a,b)=>a[0].localeCompare(b[0])).map(([group,count])=>({group,count}));
}
// Explicitly no event listeners, cookies, querystring, referrers, unique user IDs,
// phone/email/IP capture, cross-domain tracking or purchase reporting.
