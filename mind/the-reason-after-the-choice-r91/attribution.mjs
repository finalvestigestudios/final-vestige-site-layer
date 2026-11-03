/**
 * Privacy-preserving Mind guide attribution model — NOT WIRED TO LIVE WEBSITE.
 * Zero network, cookies, storage, unique IDs, IPs, full referrers or query strings.
 * Only approved categorical aggregate *synthetic* events for offline QA.
 * Before any activation obtain consent/legal/partner review, review suppression
 * against inference risks, and verify first-party logging configuration.
 */
export const ATTRIBUTION_ENABLED = false;
export const MIN_REPORTING_GROUP = 20;
const TOPICS = Object.freeze(["choice-blindness","change-blindness","attentional-blink","hypnosis-history","self-hypnosis"]);
const SURFACES = Object.freeze(["organic","tiktok","direct","internal","other"]);
const ACTIONS = Object.freeze(["guide_view","offer_cta"]);
const VARIANTS = Object.freeze(["text","film"]);
const EXPECTED_KEYS = Object.freeze(["topic","surface","action","variant"]);

function own(o,key){ return Object.prototype.hasOwnProperty.call(o,key); }
export function validateSyntheticEvent(e){
  if (!e || typeof e !== "object" || Array.isArray(e)) throw new Error("Synthetic event must be a plain record");
  if (Object.getPrototypeOf(e) !== Object.prototype && Object.getPrototypeOf(e) !== null) throw new Error("Unexpected prototype");
  const keys=Object.keys(e).sort();
  if(keys.length!==EXPECTED_KEYS.length || keys.join("|")!==[...EXPECTED_KEYS].sort().join("|")) throw new Error("Unexpected field: reject IDs, referrers, URLs, UTM, metadata and PII");
  if(!EXPECTED_KEYS.every(k=>own(e,k) && typeof e[k]==="string")) throw new Error("Invalid categorical value");
  if(!TOPICS.includes(e.topic)||!SURFACES.includes(e.surface)||!ACTIONS.includes(e.action)||!VARIANTS.includes(e.variant)) throw new Error("Not in categorical allowlist");
  return {topic:e.topic,surface:e.surface,action:e.action,variant:e.variant};
}
export function summarizeSyntheticEvents(events){
  if(!Array.isArray(events)||events.length>100000)throw new Error("Invalid event batch");
  const groups=new Map();
  for(const event of events){const e=validateSyntheticEvent(event),key=[e.topic,e.surface,e.action,e.variant].join("|");groups.set(key,(groups.get(key)||0)+1);}
  return [...groups.entries()].filter(([,n])=>n>=MIN_REPORTING_GROUP).sort((a,b)=>a[0].localeCompare(b[0])).map(([key,count])=>{const [topic,surface,action,variant]=key.split("|");return {topic,surface,action,variant,count};});
}
export function proposedMeasurementPlan(){
  return Object.freeze({enabled:ATTRIBUTION_ENABLED,first_party_only:true,topics:TOPICS,surfaces:SURFACES,actions:ACTIONS,variants:VARIANTS,raw_identifiers:false,raw_referrers:false,visitor_level_attribution:false,minimum_reporting_group:MIN_REPORTING_GROUP,conversions_not_inferred_from_clicks:true});
}
