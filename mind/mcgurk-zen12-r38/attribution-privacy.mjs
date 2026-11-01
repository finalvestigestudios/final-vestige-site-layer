/**
 * R38 synthetic attribution contract, not live analytics. NO network, cookies,
 * browser state, identifiers, automatic clicks or WordPress integration.
 * ENABLED is deliberately fixed false; changing it alone does not create a collector.
 */
export const ENABLED = false;
export const ALLOWED_SOURCES = Object.freeze(["tiktok","search","internal","direct","unknown"]);
export const ALLOWED_TOPICS = Object.freeze(["mcgurk","attention","historical-suggestion","focus","other"]);
export const ALLOWED_VARIANTS = Object.freeze(["text","film","none"]);
export const ALLOWED_EVENTS = Object.freeze(["guide_view","read_source","free_fieldbook","outbound_intent"]);
export const ALLOWED_DESTINATIONS = Object.freeze(["internal_guide","existing_focus","source_study","merchant_zen12"]);
const EXACT = Object.freeze(["source","topic","variant","event","destination"]);
const PERMITTED = Object.freeze({
  source:ALLOWED_SOURCES, topic:ALLOWED_TOPICS, variant:ALLOWED_VARIANTS,
  event:ALLOWED_EVENTS, destination:ALLOWED_DESTINATIONS
});
/** Pure validation: rejects *all* extra fields incl referrer, IP, user IDs, URL,
 *  user-agent, session, query strings, timestamps, email, free-text campaign IDs.
 */
export function sanitizeCandidate(candidate){
 if (!candidate || typeof candidate !== "object" || Array.isArray(candidate)) return null;
 if (Object.keys(candidate).length!==EXACT.length) return null;
 const safe=Object.create(null);
 for(const k of EXACT){
   if(!Object.prototype.hasOwnProperty.call(candidate,k))return null;
   const v=candidate[k];
   if(typeof v!=="string" || !PERMITTED[k].includes(v))return null;
   safe[k]=v;
 }
 if(safe.event==="outbound_intent" && safe.destination!=="merchant_zen12")return null;
 if(safe.event!=="outbound_intent" && safe.destination==="merchant_zen12")return null;
 return Object.freeze(safe);
}
/** Synthetic cohort aggregator only; not a privacy guarantee across repeated queries.
 *  No time dimension or user identifier. No published subgroup smaller than 10.
 */
export function aggregateSynthetic(candidates, minGroup=10){
 if (!Array.isArray(candidates)||minGroup<10||!Number.isInteger(minGroup))throw Error("invalid synthetic input");
 const counts=new Map();
 for(const item of candidates){
   const safe=sanitizeCandidate(item);
   if(!safe)continue;
   const key=[safe.topic,safe.variant,safe.event].join("|");
   counts.set(key,(counts.get(key)||0)+1);
 }
 return [...counts].filter(([k,n])=>n>=minGroup).sort(([a],[b])=>a.localeCompare(b))
 .map(([key,count])=>{const [topic,variant,event]=key.split("|");return Object.freeze({topic,variant,event,count});});
}
export function collectLive(_candidate){
 // HARD OFF. Do not add a network request, storage or global listener here.
 return Object.freeze({enabled:ENABLED,emitted:false,reason:"release-gate-hard-off"});
}
export function selfTest(){
 const base={source:"search",topic:"mcgurk",variant:"text",event:"guide_view",destination:"internal_guide"};
 const exact=sanitizeCandidate(base);
 const poison=["email","ip","phone","referrer","url","path","user_id","click_id","utm_campaign","session","timestamp","ua","pixel_id","gclid","fbclid","cookie"];
 let cases=0;
 if(!exact||exact.topic!=="mcgurk")throw Error("valid categorical event rejected");cases++;
 for(const x of poison){if(sanitizeCandidate({...base,[x]:"secret"})!==null)throw Error("PII field passed "+x);cases++;}
 for(const x of ["http://test","john@example.com","xyz","A".repeat(100)]){
   if(sanitizeCandidate({...base,source:x})!==null)throw Error("arbitrary source passed");cases++;
 }
 for(const x of ["merchant_zen12","other_merchant","https://zen12.com",""]){
   if(sanitizeCandidate({...base,destination:x})!==null)throw Error("unexpected destination passed");cases++;
 }
 if(sanitizeCandidate({...base,event:"outbound_intent",destination:"merchant_zen12"})===null)throw Error("outbound categorical event rejected");cases++;
 if(sanitizeCandidate({...base,event:"outbound_intent"})!==null)throw Error("wrong destination accepted");cases++;
 if(aggregateSynthetic(Array(9).fill(base)).length!==0)throw Error("small-cell leak");cases++;
 if(aggregateSynthetic(Array(10).fill(base)).length!==1)throw Error("ten threshold fail");cases++;
 if(collectLive(base).emitted||ENABLED!==false)throw Error("live instrumentation enabled");cases++;
 return Object.freeze({pass:cases,enabled:ENABLED});
}
