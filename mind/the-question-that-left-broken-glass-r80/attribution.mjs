/**
 * Final Vestige / Mind R80 — UNPUBLISHED instrumentation design.
 * NO browser or WordPress installation. NO real events collected.
 * Synthetic offline QA only. No persistence, cookies, raw URLs, request headers,
 * IP addresses, hashed/clear identifiers, merchant data or external calls.
 */
export const ACTIVATION_ENABLED = false;
export const MIN_REPORTING_CELL = 20;
export const EVENT_TYPES = Object.freeze(["guide_view", "offer_intent"]);
export const VARIANTS = Object.freeze(["a_text", "b_optional_film"]);
export const PLACEMENTS = Object.freeze(["guide_end", "related_article"]);
export const TOPICS = Object.freeze(["total_focus", "zen12"]);
const ALLOWED_KEYS = Object.freeze(["synthetic", "event", "variant", "placement", "topic", "count"]);

function plainRecord(value) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) return false;
  return Object.getPrototypeOf(value) === Object.prototype;
}
const member = (set, value) => typeof value === "string" && set.includes(value);
/** Reject IDs and arbitrary keys rather than silently dropping them. */
export function validateSynthetic(input) {
  if (!plainRecord(input)) throw new TypeError("Expected plain synthetic category record");
  const keys = Object.keys(input);
  if (keys.some(k => !ALLOWED_KEYS.includes(k))) throw new TypeError("Unexpected field; user identifiers disallowed");
  if (input.synthetic !== true) throw new TypeError("Synthetic marker required");
  if (!member(EVENT_TYPES, input.event)) throw new TypeError("Unrecognized event");
  if (!member(VARIANTS, input.variant)) throw new TypeError("Unrecognized variant");
  if (!member(PLACEMENTS, input.placement)) throw new TypeError("Unrecognized placement");
  if (!member(TOPICS, input.topic)) throw new TypeError("Unrecognized topic");
  if (!Number.isSafeInteger(input.count) || input.count < 1 || input.count > 10000) {
    throw new TypeError("Count must be safe integer 1–10000");
  }
  if (keys.length !== ALLOWED_KEYS.length) throw new TypeError("All synthetic fields required");
  return Object.freeze({
    synthetic: true, event: input.event, variant: input.variant,
    placement: input.placement, topic: input.topic, count: input.count
  });
}
/** Never reports synthetic groups below n=20. Counts are not unique users. */
export function aggregateSynthetic(input) {
  if (!Array.isArray(input)) throw new TypeError("Input must be synthetic array");
  if (input.length > 5000) throw new RangeError("Too many synthetic rows");
  const buckets = new Map();
  for (const row of input) {
    const r = validateSynthetic(row);
    const key = [r.topic, r.variant, r.placement, r.event].join("|");
    buckets.set(key, (buckets.get(key) || 0) + r.count);
  }
  const safe = [];
  for (const [key,count] of buckets.entries()) {
    if (count < MIN_REPORTING_CELL) continue;
    const [topic,variant,placement,event] = key.split("|");
    safe.push(Object.freeze({topic,variant,placement,event,count}));
  }
  return Object.freeze({
    label:"SYNTHETIC OFFLINE ONLY — NOT UNIQUE PEOPLE, NOT PURCHASES",
    activation:false,
    min_cell:MIN_REPORTING_CELL,
    cells:Object.freeze(safe.sort((a,b) => a.topic.localeCompare(b.topic) || a.variant.localeCompare(b.variant)))
  });
}
/** Public guard: even accidental calls cannot initiate tracking or redirects. */
export function recordOutboundEvent() {
  return Object.freeze({accepted:false,reason:"DISABLED; no real visitor events or clicks captured"});
}
