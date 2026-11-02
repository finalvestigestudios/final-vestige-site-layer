/** Mind R69 privacy prototype: no live collection, no network, no URLs/cookies/storage.
 * Only synthetic, anonymous, allowlisted cohort counting, never sales attribution.
 * ACTIVE stays false until separate founder privacy approval and documented tests.
 */
export const ACTIVE = false;
export const MIN_COHORT = 20;
const VARIANTS = Object.freeze(["text", "film"]);
const TOPICS = Object.freeze(["white-bear", "perception", "suggestion", "meditation"]);
const EVENTS = Object.freeze(["guide_view", "research_source_open", "prospective_cta_view"]);
function assertPlainObject(o) {
  if (!o || Object.getPrototypeOf(o)!==Object.prototype) throw new TypeError("Plain synthetic record only");
}
export function validateSynthetic(record) {
  assertPlainObject(record);
  const keys = Object.keys(record);
  if(keys.length !== 3 || keys.some(k => !["variant","topic","event"].includes(k))) throw new TypeError("Unexpected field; PII/URL/referrer not accepted");
  if(!VARIANTS.includes(record.variant)||!TOPICS.includes(record.topic)||!EVENTS.includes(record.event)) throw new TypeError("Unknown enum value");
  return Object.freeze({variant:record.variant, topic:record.topic, event:record.event});
}
export function aggregateSynthetic(rows) {
  if(!Array.isArray(rows) || rows.length>10000) throw new TypeError("Expected <=10000 synthetic records");
  const counts = new Map();
  for(const raw of rows){const r=validateSynthetic(raw);const k=[r.variant,r.topic,r.event].join("|");counts.set(k,(counts.get(k)||0)+1)}
  return Object.freeze([...counts.entries()].filter(([,n])=>n>=MIN_COHORT).map(([k,n])=>Object.freeze({cohort:k,count:n})));
}
export function recordVisitorEvent() {throw new Error("DISABLED: no visitor tracking authorization, collection or networking");}
export function activateAffiliateAttribution() {throw new Error("DISABLED: no partner approval and no earning link");}
