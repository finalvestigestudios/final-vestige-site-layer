/**
 * R60 privacy-limited, OFF-BY-DEFAULT attribution design.
 * This module deliberately has no DOM, browser storage, network, or personal identifiers.
 * Do NOT wire this to visitors/WordPress absent separate lawful privacy and release approval.
 */
export const ATTRIBUTION_ENABLED = false;
export const ALLOWED_EVENTS = Object.freeze(["guide_open", "offer_intent", "focus_visit"]);
export const ALLOWED_TOPICS = Object.freeze(["coue", "zen12", "attention", "hypnosis"]);
export const ALLOWED_VARIANTS = Object.freeze(["A", "B"]);
const PERMITTED = Object.freeze(["event", "topic", "variant"]);
const VALID_ID = /^[A-Za-z][A-Za-z0-9_]{0,30}$/;

export function classify(value) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) return null;
  const keys = Object.keys(value);
  if (keys.length !== 3 || keys.some(k => !PERMITTED.includes(k))) return null;
  if (keys.some(k => typeof value[k] !== "string" || !VALID_ID.test(value[k]))) return null;
  if (!ALLOWED_EVENTS.includes(value.event) || !ALLOWED_TOPICS.includes(value.topic) || !ALLOWED_VARIANTS.includes(value.variant)) return null;
  return Object.freeze({ event: value.event, topic: value.topic, variant: value.variant });
}
export function record(candidate) {
  // Fail closed independently of the input, including inputs that would otherwise classify.
  void candidate;
  return Object.freeze({ recorded: false, reason: "release_hold" });
}
export function summarizeSynthetic(rows, minCell = 20) {
  if (!Array.isArray(rows) || !Number.isInteger(minCell) || minCell < 20 || minCell > 10000) throw new TypeError("unsafe synthetic reporting request");
  const counts = new Map();
  for (const row of rows) {
    const item = classify(row);
    if (!item) throw new TypeError("invalid synthetic event or identifying field");
    const key = item.topic + "/" + item.variant + "/" + item.event;
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  return Object.freeze([...counts].filter(([,count]) => count >= minCell).map(([key,count]) => Object.freeze({ group: key, count })));
}
