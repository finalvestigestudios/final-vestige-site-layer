// Prototype ONLY. Zero network, storage, cookies, device IDs or runtime activation.
export const ATTRIBUTION_ENABLED=false;
const allowed={variant:new Set(["text","film"]),origin:new Set(["organic","tiktok","direct","other"]),event:new Set(["page_view","internal_focus_click","prospective_offer_view","approved_outbound_click"])};
export function validateEvent(e){if(!e||typeof e!=="object"||Array.isArray(e))throw Error("invalid event");const k=Object.keys(e);if(k.length!==3||k.some(v=>!Object.hasOwn(allowed,v)))throw Error("unexpected field/PII");for(const [a,v]of Object.entries(e)){if(typeof v!=="string"||!allowed[a].has(v))throw Error("invalid category")}return Object.freeze({...e})}
export function syntheticAggregate(events,minimum=20){if(!Number.isInteger(minimum)||minimum<20)throw Error("minimum threshold");const counts=new Map();for(const event of events){const v=validateEvent(event);const k=[v.variant,v.origin,v.event].join("|");counts.set(k,(counts.get(k)||0)+1)}return Object.freeze(Object.fromEntries([...counts].filter(([k,n])=>n>=minimum)))}
export function record(){return {accepted:false,reason:"ATTRIBUTION_DISABLED"};}
