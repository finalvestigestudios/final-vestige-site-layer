/** R68 privacy-first attribution prototype. Deliberately inert until separately authorized.
 * Synthetic aggregate design only. No cookies, localStorage, IP, referrer URLs or network requests.
 * Not connected to WordPress/Jetpack/merchant. Deny actual collection even when called explicitly.
 */
export const ACTIVE = false;
const TOPICS = Object.freeze(new Set(["attention","memory","suggestion","meditation","perception"]));
const CHANNELS = Object.freeze(new Set(["organic","tiktok","direct","internal","unknown"]));
const EVENTS = Object.freeze(new Set(["guide_view","exercise_view","offer_intent","focus_route","outbound_attempt"]));
export function validateSyntheticEvent(e) {
  if(!e || typeof e !== "object" || Array.isArray(e)) throw new Error("Invalid synthetic event");
  const keys=Object.keys(e).sort();
  if(keys.join("|") !== "channel|event|topic|variant") throw new Error("Unexpected attribute / possible PII");
  if(!TOPICS.has(e.topic)||!CHANNELS.has(e.channel)||!EVENTS.has(e.event)||!["a","b"].includes(e.variant)) throw new Error("Not allowlisted");
  return Object.freeze({topic:e.topic,channel:e.channel,event:e.event,variant:e.variant});
}
export function collectRealEvent() { throw new Error("HARD_HOLD: no real visitor measurement authorized"); }
export function synthesizeAggregate(events) {
  if(!Array.isArray(events)) throw new Error("Expected synthetic array");
  const groups=new Map();
  for(const evt of events){
    const x=validateSyntheticEvent(evt); const key=[x.topic,x.channel,x.event,x.variant].join("|");
    groups.set(key,(groups.get(key)||0)+1);
  }
  return [...groups].filter(([,n])=>n>=20).map(([key,count])=>Object.freeze({cohort:key,count}));
}
export const hypotheticalComparison = Object.freeze({
  hypothesis:"Adding an original optional 40-second captioned educational video may improve informed CTA intent versus text-only; direction unknown.",
  randomization:"NOT IMPLEMENTED",
  assignment:"none",
  exposure:"none",
  clicks:"none",
  purchases:"unobservable",
  primary_metric:"not defined for collection until approved",
  required_before_test:["publisher permission","founder approval","WCAG QA","privacy review","same substantive guide","original media hosted with captions"],
});
