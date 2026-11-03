/**
 * Mind R90 — PRIVACY-SAFE MEASUREMENT SPECIMEN
 * OFF BY DEFAULT. No visitor collection, no network requests, no browser storage.
 * Can only be introduced after written partner, privacy, editorial and release review.
 * Raw referrers, URL parameters, identifiers and merchant tokens are not accepted.
 */
export const ATTRIBUTION_ENABLED = false;
export const MIN_AGGREGATE_GROUP = 20;
const EVENT_TYPES = new Set(["investigation_read", "guide_view", "focus_resource_interest", "offer_interest_disabled"]);
const TOPICS = new Set(["rubber-hand", "zen12", "mind-hub"]);
const SOURCES = new Set(["organic", "tiktok", "direct", "internal", "other"]);
const EXPECTED_KEYS = ["event", "topic", "source"];
export function validateSyntheticEvent(input) {
  if (!input || typeof input !== "object" || Array.isArray(input) || Object.getPrototypeOf(input) !== Object.prototype) {
    throw new TypeError("Expected a plain categorical event object");
  }
  const keys=Object.keys(input);
  if (keys.length !== 3 || keys.some(k => !EXPECTED_KEYS.includes(k))) {
    throw new Error("Only event/topic/source are permitted; no PII, URL, referrer or tracking payload");
  }
  if (!EVENT_TYPES.has(input.event) || !TOPICS.has(input.topic) || !SOURCES.has(input.source)) {
    throw new Error("Unrecognized categorical value");
  }
  return Object.freeze({event:input.event,topic:input.topic,source:input.source});
}
export function summarizeSyntheticEvents(events) {
  if (!Array.isArray(events)) throw new TypeError("Synthetic events must be an array");
  const groups = new Map();
  for (const raw of events) {
    const r=validateSyntheticEvent(raw);
    const key=[r.event,r.topic,r.source].join("::");
    groups.set(key,(groups.get(key)||0)+1);
  }
  return [...groups].filter(([,count])=>count>=MIN_AGGREGATE_GROUP).map(([key,count])=>{
    const [event,topic,source]=key.split("::");
    return Object.freeze({event,topic,source,count});
  });
}
/** Intentionally NO emit/track function; source may be used only in synthetic test harnesses. */
