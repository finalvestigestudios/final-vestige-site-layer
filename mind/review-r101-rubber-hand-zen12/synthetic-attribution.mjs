/**
 * FINAL VESTIGE / Mind R101 — privacy-preserving, OFFLINE SYNTHETIC-ONLY counter prototype.
 *
 * ZERO live instrumentation. This module never reads browser/window/location,
 * requests, query strings, cookies, headers, referrers, email, IP or user agents.
 * Future activation requires independent approval, opt-out from identifying
 * merchant reporting, and a new reviewed change. Nothing here sends events.
 */
export const ATTRIBUTION_ACTIVATION = Object.freeze({
  enabled: false,
  mode: "SYNTHETIC_ONLY",
  externalMerchantLinkActive: false,
  purchaserIdentityCollection: false,
  analyticsNetworkRequests: false,
  sampleFloor: 20
});

const ALLOWED_KEYS = ["action", "channel", "count", "topic"];
const CHANNELS = new Set(["organic_search", "tiktok", "youtube", "direct", "internal", "other"]);
const TOPICS = new Set(["rubber_hand", "zen12_guide", "mind_hub", "focus_fieldbook"]);
const ACTIONS = new Set(["guide_view", "offer_intent_disabled", "focus_resource_view"]);
const MAX_ROWS = 1000;
const MAX_COUNT = 10000;

function validate(row) {
  if (row === null || typeof row !== "object" || Array.isArray(row)) throw new TypeError("row must be plain data");
  const keys = Reflect.ownKeys(row);
  if (keys.length !== ALLOWED_KEYS.length ||
      keys.some(k => typeof k !== "string" || !ALLOWED_KEYS.includes(k)) ||
      ALLOWED_KEYS.some(k => !Object.prototype.hasOwnProperty.call(row, k)))
    throw new TypeError("unapproved keys; no raw identifiers, URL or referrer may be stored");
  if (!CHANNELS.has(row.channel) || !TOPICS.has(row.topic) || !ACTIONS.has(row.action))
    throw new TypeError("unapproved categorical value");
  if (!Number.isSafeInteger(row.count) || row.count < 0 || row.count > MAX_COUNT)
    throw new RangeError("invalid synthetic aggregate count");
}

/** Accepts ONLY synthetic, pre-aggregated, strictly whitelisted categorical records.
 * Small cells are omitted. Does not output a grand total or combinations from
 * which a suppressed small count could be derived. This is NOT visitor analytics.
 */
export function aggregateSynthetic(rows) {
  if (!Array.isArray(rows) || rows.length > MAX_ROWS) throw new TypeError("expected <=1000 synthetic aggregate rows");
  const groups = new Map();
  for (const row of rows) {
    validate(row);
    const key = JSON.stringify([row.topic, row.channel, row.action]);
    const before = groups.get(key) || 0;
    const next = before + row.count;
    if (!Number.isSafeInteger(next)) throw new RangeError("synthetic aggregate overflow");
    groups.set(key, next);
  }
  const summary = [];
  for (const [key, count] of groups.entries()) {
    if (count < ATTRIBUTION_ACTIVATION.sampleFloor) continue;
    const [topic, channel, action] = JSON.parse(key);
    summary.push(Object.freeze({topic, channel, action, synthetic_count: count}));
  }
  summary.sort((a,b)=>a.topic.localeCompare(b.topic)||a.channel.localeCompare(b.channel)||a.action.localeCompare(b.action));
  return Object.freeze({mode:"SYNTHETIC_ONLY",enabled:false,sample_floor:20,groups:Object.freeze(summary)});
}

export function recordLiveEvent() {
  throw new Error("CLOSED: live measurement and merchant attribution not approved");
}
