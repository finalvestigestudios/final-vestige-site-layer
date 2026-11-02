/**
 * Privacy-first outbound attribution design — DISABLED, not imported by HTML.
 * This module NEVER sends events, reads storage, IP, UA, location, full referrer,
 * email, name, fingerprint, cookies or query strings.
 * It accepts only enumerated synthetic categorical counts. Commission/sales
 * cannot be inferred from outbound clicks. Activation requires separate consent
 * and owner/data-governance/partner approval plus production QA.
 */
export const ENABLED = false;
const TOPICS = Object.freeze(["stroop","meditation","suggestion","perception"]);
const VARIANTS = Object.freeze(["text","video"]);
const EVENTS = Object.freeze(["guide_view","focus_navigation","outbound_click"]);
const ORIGINS = Object.freeze(["direct","organic","social","internal","unknown"]);
const KEYS = Object.freeze(["topic","variant","event","origin"]);
const isRecord = v => v !== null && typeof v === "object" && !Array.isArray(v);
export function normalizeEvent(value) {
  if (!isRecord(value)) return null;
  const keys = Object.keys(value);
  if (keys.length !== 4 || keys.some(key => !KEYS.includes(key))) return null;
  if (!TOPICS.includes(value.topic) || !VARIANTS.includes(value.variant)
      || !EVENTS.includes(value.event) || !ORIGINS.includes(value.origin)) return null;
  return Object.freeze({topic:value.topic, variant:value.variant,
                        event:value.event, origin:value.origin});
}
export function summarizeSyntheticEvents(rawEvents, minimumGroupSize = 20) {
  if (!Array.isArray(rawEvents)) throw new TypeError("Events must be a list");
  if (!Number.isInteger(minimumGroupSize) || minimumGroupSize < 20)
      throw new RangeError("Minimum cohort size is 20");
  const counts = new Map();
  for (const item of rawEvents) {
    const normalized = normalizeEvent(item);
    if (!normalized) continue;
    const key = [normalized.topic, normalized.variant,normalized.event,
                 normalized.origin].join("|");
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  return Array.from(counts.entries()).filter(([, n]) => n >= minimumGroupSize)
    .sort(([a],[b]) => a.localeCompare(b))
    .map(([key,count]) => {
      const [topic,variant,event,origin] = key.split("|");
      return Object.freeze({topic,variant,event,origin,count});
    });
}
// Intentionally no collector, network call, browser event listener or storage.
