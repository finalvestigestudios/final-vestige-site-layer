// R82 PRIVACY / NEVER IMPORT INTO WORDPRESS. NO production event listener.
export const LIVE_COLLECTION_ENABLED = false;
const allowed = Object.freeze({
  topic: ["troxler","zen12","attention","history"],
  source: ["direct","organic","tiktok","internal","unknown"],
  variant: ["A","B","none"],
  action: ["guide_view","cta_intent","focus_route"]
});
const keys = Object.keys(allowed);
export function validateSynthetic(event) {
  if (LIVE_COLLECTION_ENABLED) return {ok:false,reason:"hard_stop_enabled_mismatch"};
  if (!event || typeof event !== "object" || Array.isArray(event)) return {ok:false,reason:"not_object"};
  if (Object.keys(event).length !== keys.length || Object.keys(event).some(k=>!keys.includes(k)))
    return {ok:false,reason:"unknown_or_missing_fields"};
  for(const k of keys) if(typeof event[k]!=="string" || !allowed[k].includes(event[k]))
    return {ok:false,reason:"invalid_"+k};
  return {ok:true,event:{topic:event.topic,source:event.source,variant:event.variant,action:event.action}};
}
export function syntheticAggregate(rows, minimum=20) {
  if (LIVE_COLLECTION_ENABLED || minimum<20) throw new Error("privacy_gate");
  const count = new Map();
  for(const row of rows){
    const v=validateSynthetic(row);
    if(!v.ok) throw new Error(v.reason);
    const k=[v.event.topic,v.event.source,v.event.variant,v.event.action].join("|");
    count.set(k,(count.get(k)||0)+1);
  }
  return [...count.entries()].filter(([,n])=>n>=minimum).map(([key,n])=>({group:key,events:n}));
}
export function outboundClick() { return {ok:false,reason:"NO_APPROVED_PARTNER_LINK"}; }
