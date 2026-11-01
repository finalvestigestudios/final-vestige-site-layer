/**
 * Final Vestige Mind R50 / design-only attribution specification.
 * NOT imported into WordPress, no storage/network/cookie/browser runtime.
 * Activation is hard-disabled even if a caller claims merchant approval.
 * Any future enabled implementation requires an independently reviewed PR.
 */
export const ATTRIBUTION_ENABLED = false;
export const MIN_PUBLIC_COHORT = 20;
const KINDS = new Set(["guide_view","film_intent","cta_intent"]);
const TOPICS = new Set(["zen12","mcgurk"]);
const VARIANTS = new Set(["A_TEXT","B_FILM"]);
const SOURCES = new Set(["direct","organic","tiktok","internal","unknown"]);
const FIELDS = ["kind","topic","variant","source"];
const key = e => [e.kind,e.topic,e.variant,e.source].join("|");

export function acceptSyntheticEvent(payload) {
  if (payload === null || typeof payload !== "object" || Array.isArray(payload) || Object.getPrototypeOf(payload) !== Object.prototype) return null;
  const keys = Object.keys(payload);
  if (keys.length !== FIELDS.length || keys.some(k => !FIELDS.includes(k))) return null;
  if (!KINDS.has(payload.kind) || !TOPICS.has(payload.topic) || !VARIANTS.has(payload.variant) || !SOURCES.has(payload.source)) return null;
  return Object.freeze({kind:payload.kind,topic:payload.topic,variant:payload.variant,source:payload.source});
}

/** Aggregates only synthetic, non-identifying example events; does not collect users. */
export function summarizeSynthetic(events) {
  if (!Array.isArray(events) || events.length > 100000) return [];
  const counts = new Map();
  for (const raw of events) {
    const e = acceptSyntheticEvent(raw);
    if (e) counts.set(key(e),(counts.get(key(e))||0)+1);
  }
  return [...counts].filter(([,n]) => n >= MIN_PUBLIC_COHORT)
    .sort(([a],[b]) => a.localeCompare(b))
    .map(([name,count]) => Object.freeze({bucket:name,count}));
}

/** Explicit fail-closed live entry point. No "enable" argument exists. */
export function recordLiveEvent(_event) { return Object.freeze({status:"DISABLED",recorded:false}); }
