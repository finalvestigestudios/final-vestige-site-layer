/** R40 first-party attribution prototype, deliberately HARD OFF.
 * No browser, WordPress, network, cookies, storage, sessions, raw referrers or identifiers.
 * Only synthetic categorical values can be aggregated in selfTest.
 */
export const ENABLED = false;
export const CHANNELS = Object.freeze(["direct","organic","tiktok","internal","other"]);
export const TOPICS = Object.freeze(["gorilla","zen12","mind-hub"]);
export const VARIANTS = Object.freeze(["text","video"]);
export const ACTIONS = Object.freeze(["view","outbound_intent"]);
export function validateSyntheticEvent(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) return false;
  if (Object.keys(input).sort().join(",") !== "action,channel,topic,variant") return false;
  return ACTIONS.includes(input.action) && CHANNELS.includes(input.channel) && TOPICS.includes(input.topic) && VARIANTS.includes(input.variant);
}
export function recordEvent(_input) { return null; } // permanently off, regardless of input
export function aggregateSynthetic(events,minCount=10){
  if (!Array.isArray(events) || !Number.isInteger(minCount) || minCount<10) throw Error("Invalid synthetic inputs");
  if (!events.every(validateSyntheticEvent)) throw Error("Invalid event schema");
  const counts=new Map();
  for(const e of events){const k=[e.action,e.channel,e.topic,e.variant].join(":");counts.set(k,(counts.get(k)||0)+1);}
  return [...counts].filter(([,n])=>n>=minCount).map(([key,count])=>({key,count}));
}
export function selfTest(){
  let passed=0; const check=(ok,msg)=>{if(!ok)throw Error("Privacy test "+msg);passed++;};
  check(ENABLED===false,"disabled");
  check(recordEvent({action:"view",channel:"tiktok",topic:"zen12",variant:"video"})===null,"no record");
  const valid={action:"view",channel:"organic",topic:"mind-hub",variant:"text"};
  check(validateSyntheticEvent(valid),"valid shape");
  for(const key of ["email","ip","visitor_id","session","url","referrer","utm_source","path","cookie","userAgent","timestamp","name"]){
    check(!validateSyntheticEvent({...valid,[key]:"sensitive"}),"reject "+key);
  }
  for(const bad of ["x",null,[],{},{...valid,channel:"https://x.example"},{...valid,topic:"personal"},{...valid,variant:"private"},{...valid,action:"purchase"}]){
    check(!validateSyntheticEvent(bad),"bad event");
  }
  check(aggregateSynthetic(Array(9).fill(valid)).length===0,"small cell");
  check(aggregateSynthetic(Array(10).fill(valid)).length===1,"threshold");
  return passed;
}
