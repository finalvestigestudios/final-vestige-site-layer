/**
 * Final Vestige R102: OFFLINE/SYNTHETIC-ONLY attribution demonstration.
 * No telemetry, browser globals, cookies, client IP, referrers, URLs or network access.
 * It is impossible to enable live logging from this module.
 */
export const ACTIVATION = Object.freeze({
  enabled:false,mode:"SYNTHETIC_ONLY",merchantLinkActive:false,
  personalDataCollection:false,networkRequests:false,minPublicCell:20
});
const KEY_SET=Object.freeze(["action","channel","count","topic"]);
const CHANNELS=new Set(["organic","tiktok","youtube","internal","direct","other"]);
const TOPICS=new Set(["mcgurk","zen12","focus_fieldbook","mind_archive"]);
const ACTIONS=new Set(["guide_view","resource_view","offer_intent_disabled"]);
function validate(x){
  if(x===null||typeof x!=="object"||Array.isArray(x)||Object.getPrototypeOf(x)!==Object.prototype)throw new TypeError("only synthetic plain data");
  const keys=Reflect.ownKeys(x);
  if(keys.length!==KEY_SET.length||keys.some(k=>typeof k!=="string"||!KEY_SET.includes(k))||KEY_SET.some(k=>!Object.hasOwn(x,k)))throw new TypeError("identifying or unexpected field rejected");
  for(const k of keys){const descriptor=Object.getOwnPropertyDescriptor(x,k);if(!Object.hasOwn(descriptor,"value"))throw new TypeError("getters rejected");}
  if(!CHANNELS.has(x.channel)||!TOPICS.has(x.topic)||!ACTIONS.has(x.action))throw new TypeError("invalid allowlisted category");
  if(!Number.isSafeInteger(x.count)||x.count<0||x.count>10000)throw new RangeError("bad synthetic count");
}
export function aggregateSynthetic(rows){
  if(!Array.isArray(rows)||rows.length>1000)throw new TypeError("at most 1000 preaggregated synthetic rows");
  const groups=new Map();
  for(const row of rows){
    validate(row);const k=JSON.stringify([row.topic,row.channel,row.action]);
    const n=(groups.get(k)||0)+row.count;
    if(!Number.isSafeInteger(n))throw new RangeError("overflow");
    groups.set(k,n);
  }
  const visible=[];
  for(const [key,count] of groups){
    if(count<ACTIVATION.minPublicCell)continue;
    const [topic,channel,action]=JSON.parse(key);
    visible.push(Object.freeze({topic,channel,action,synthetic_count:count}));
  }
  visible.sort((a,b)=>a.topic.localeCompare(b.topic)||a.channel.localeCompare(b.channel)||a.action.localeCompare(b.action));
  return Object.freeze({mode:"SYNTHETIC_ONLY",enabled:false,minPublicCell:20,groups:Object.freeze(visible)});
}
export function recordLiveEvent(){throw new Error("CLOSED: no real-world tracking approved");}
export function trackPurchase(){throw new Error("CLOSED: no transaction/purchaser data collection approved");}
