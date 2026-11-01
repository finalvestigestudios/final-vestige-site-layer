/** Draft-only categorical attribution primitives; NO live collection, no network, no storage. */
export const ATTRIBUTION_ENABLED = false;
const EXACT_KEYS = ["topic","channel","variant","action"];
const SETS = {
 topic:new Set(["thatcher","zen12","puysegur","focus"]),
 channel:new Set(["organic","tiktok","internal","unknown"]),
 variant:new Set(["A","B"]),
 action:new Set(["guide","focus_page","merchant_hold"])
};
export function validateSynthetic(input) {
 if(!input || typeof input!=="object" || Array.isArray(input)) return null;
 const keys=Object.keys(input);
 if(keys.length!==EXACT_KEYS.length || keys.some(k=>!EXACT_KEYS.includes(k))) return null;
 const out=Object.create(null);
 for(const k of EXACT_KEYS){ if(typeof input[k]!=="string" || !SETS[k].has(input[k]))return null;out[k]=input[k]; }
 return out;
}
export function summarizeSynthetic(rows, threshold=20){
 if(!Array.isArray(rows) || !Number.isInteger(threshold) || threshold<20) return [];
 const buckets=new Map();
 for(const r of rows){const v=validateSynthetic(r);if(!v)continue;
 const key=EXACT_KEYS.map(k=>v[k]).join("|");
 buckets.set(key,(buckets.get(key)||0)+1);
 }
 return [...buckets].filter(([,count])=>count>=threshold).map(([key,count])=>({bucket:key,count}));
}
export function browserAttribution(){ return ATTRIBUTION_ENABLED ? null : {enabled:false,reason:"NO_APPROVED_LINK_OR_MEASUREMENT_CONSENT"}; }
/* Never call this module from consumer pages until privacy, permissions and approvals are documented. */
