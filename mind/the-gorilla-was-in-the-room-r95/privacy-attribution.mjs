// R95 SYNTHETIC-ONLY CONTRACT: NO LIVE EVENT HANDLERS, NO NETWORK OR STORAGE.
const allowed = Object.freeze({
 event: ["page_view","guide_view","video_optional_view","offer_intent_disabled","focus_link"],
 source: ["tiktok","organic","internal","other"],
 topic: ["inattentional-blindness","zen12","self-hypnosis","other"],
 variant: ["a","b","na"]
});
export function classifySyntheticEvent(value) {
 if (!value || typeof value !== "object" || Array.isArray(value)) throw Error("invalid record");
 const keys = Object.keys(value).sort();
 if (keys.join(",") !== ["event","source","topic","variant"].sort().join(",")) throw Error("forbidden or missing fields");
 const out = {};
 for (const field of Object.keys(allowed)) {
   if (typeof value[field] !== "string" || !allowed[field].includes(value[field])) throw Error("unknown categorical value");
   out[field] = value[field];
 }
 return Object.freeze(out);
}
export function aggregateSynthetic(records,{minimumCell=20}={}) {
 if (!Number.isInteger(minimumCell) || minimumCell<20) throw Error("small-cell policy cannot weaken");
 const groups = new Map();
 for (const record of records) {
  const x = classifySyntheticEvent(record);
  const id = [x.event,x.source,x.topic,x.variant].join("|");
  groups.set(id,(groups.get(id)||0)+1);
 }
 return Object.freeze([...groups.entries()].filter(([,count])=>count>=minimumCell).map(([key,count])=>Object.freeze({key,count})));
}
// Reporting demonstration only. Cannot claim deduplicated people, purchases, commissions, rates or causal lift.