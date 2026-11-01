/**
 * R41 OFFLINE / SYNTHETIC ONLY. No DOM, cookies, storage, network, URL/referrer,
 * session IDs, visitor IDs or any client-side import. DO NOT DEPLOY.
 */
export const ENABLED = false;
export const SCHEMA = Object.freeze({
  topic: Object.freeze(["mind_wandering", "zen12_guide"]),
  variant: Object.freeze(["text_only", "poster_transcript"]),
  channel: Object.freeze(["direct", "search", "tiktok", "internal", "unknown"]),
  action: Object.freeze(["guide_view", "cta_eligibility_review", "outbound_review"]),
});
const FIELDS = Object.freeze(Object.keys(SCHEMA));
export function validateSynthetic(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) return null;
  const keys = Object.keys(input);
  if (keys.length !== FIELDS.length || keys.some(k => !FIELDS.includes(k))) return null;
  for (const key of FIELDS) if (typeof input[key] !== "string" || !SCHEMA[key].includes(input[key])) return null;
  return Object.freeze(Object.fromEntries(FIELDS.map(k => [k, input[k]])));
}
export function collect() { return false; }
export function outbound() { return false; }
export function summarizeSynthetic(events, minimumGroup = 10) {
  if (!Array.isArray(events) || !Number.isInteger(minimumGroup) || minimumGroup < 10) return Object.freeze([]);
  const counts = new Map();
  for (const raw of events) {
    const event = validateSynthetic(raw);
    if (!event) continue;
    const key = FIELDS.map(f => event[f]).join("|");
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }
  return Object.freeze([...counts.entries()].filter(([,n]) => n >= minimumGroup).map(([key,n]) =>
    Object.freeze({category: key, count: n})
  ));
}
export const REVIEW_ONLY = Object.freeze({
  enabled: ENABLED, mode: "synthetic-no-network-no-storage",
  acceptsPII: false, productionData: false, outcomeReporting: false,
  referralURLCollection: false, published: false
});
