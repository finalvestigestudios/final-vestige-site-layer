// R98 deterministic synthetic-only categories. NOT an analytics client; no network, storage, cookies or browser access.
export const CATEGORIES = Object.freeze(["organic","tiktok","direct","internal"]);
export const EVENTS = Object.freeze(["guide_view","offer_review_intent","free_resource_visit"]);
export const MIN_REPORT_GROUP = 20;
export function validateSynthetic(event) {
  if(!event || typeof event !== "object" || Array.isArray(event)) throw Error("synthetic object required");
  const keys = Object.keys(event);
  if(keys.length !== 3 || keys.some(k => !["synthetic","category","event"].includes(k))) throw Error("unknown or identifying field");
  if(event.synthetic !== true || !CATEGORIES.includes(event.category) || !EVENTS.includes(event.event)) throw Error("unapproved categorical value");
  return Object.freeze({category:event.category,event:event.event});
}
export function aggregateSyntheticOnly(events) {
 if(!Array.isArray(events)) throw Error("array only");
 const counts=Object.create(null);
 for(const raw of events){const e=validateSynthetic(raw);const k=e.category+"|"+e.event;counts[k]=(counts[k]||0)+1;}
 return Object.freeze(Object.fromEntries(Object.entries(counts).filter(([,n])=>n>=MIN_REPORT_GROUP).sort()));
}
