// Pure, synthetic-only proof-of-concept. Not imported from site markup.
// DOES NOT attach listeners, send requests, set cookies or store any events.
const TOPIC = new Set(["troxler","attention","suggestion","zen12"]);
const SOURCE = new Set(["organic","tiktok","direct","internal","unknown"]);
const VARIANT = new Set(["a","b","none"]);
const KIND = new Set(["guide_view","cta_intent","outbound_verified"]);
const FIELDS = ["kind","topic","source","variant"];
export function validateSynthetic(event) {
  if (!event || typeof event !== "object" || Array.isArray(event)) throw new Error("not a plain event");
  const keys = Object.keys(event).sort();
  if (keys.length !== FIELDS.length || keys.join("|") !== [...FIELDS].sort().join("|")) throw new Error("unexpected keys / PII / URL");
  if (!KIND.has(event.kind) || !TOPIC.has(event.topic) || !SOURCE.has(event.source) || !VARIANT.has(event.variant)) throw new Error("invalid categorical value");
  if (event.kind === "outbound_verified") throw new Error("live outbound disabled until partner approval");
  return Object.freeze({kind:event.kind,topic:event.topic,source:event.source,variant:event.variant});
}
export function groupedSynthetic(events, min=20) {
  if (min < 20 || !Number.isInteger(min)) throw new Error("minimum suppression threshold is 20");
  const grouped=new Map();
  for (const e of events) {
    const safe=validateSynthetic(e),key=[safe.kind,safe.topic,safe.source,safe.variant].join("|");
    grouped.set(key,(grouped.get(key)||0)+1);
  }
  return [...grouped.entries()].filter(([,n])=>n>=min).map(([key,count])=>({category:key,count}));
}
// No click == no sale: no inferred conversion, identifier, referral or commission.