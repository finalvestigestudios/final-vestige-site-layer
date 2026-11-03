/**
 * FINAL VESTIGE — R103 offline attribution contract.
 * No live collection. No network, no DOM, cookies, storage, raw referrers,
 * UTM strings, IP addresses, email addresses or purchaser identities.
 * This is deliberately not a web tracking script. Synthetic QA only.
 */
export const LIVE_COLLECTION_ENABLED = false;
export const CATEGORIES = Object.freeze({
  source: Object.freeze(["organic","tiktok","youtube","direct","other"]),
  topic: Object.freeze(["zen12","memory"]),
  variant: Object.freeze(["text","film_concept"]),
  action: Object.freeze(["guide_open","focus_link","offer_control_disabled"])
});
const KEYS = Object.freeze(["source","topic","variant","action"]);
export const MIN_REPORTING_CELL = 20;
function isPlainObject(obj) {
  if (!obj || typeof obj !== "object" || Array.isArray(obj)) return false;
  const proto = Object.getPrototypeOf(obj);
  return proto === Object.prototype || proto === null;
}
export function validateSyntheticEvent(obj) {
  if (!isPlainObject(obj)) throw new TypeError("Event must be a plain object");
  const keys = Object.keys(obj).sort();
  if (keys.length !== KEYS.length || keys.some((x,i)=>x!==[...KEYS].sort()[i])) {
    throw new TypeError("Unexpected or identifying event fields are forbidden");
  }
  const clean = {};
  for (const k of KEYS) {
    const v = obj[k];
    if (typeof v !== "string" || !CATEGORIES[k].includes(v)) {
      throw new TypeError("Noncategorical or unapproved event value: " + k);
    }
    clean[k] = v;
  }
  return Object.freeze(clean);
}
export function aggregateSyntheticOnly(records) {
  if (!Array.isArray(records) || records.length > 100000) throw new TypeError("Bounded records array required");
  const counts = new Map();
  for (const record of records) {
    const e = validateSyntheticEvent(record);
    const group = KEYS.map(k => e[k]).join("|");
    counts.set(group,(counts.get(group)||0)+1);
  }
  return Object.freeze([...counts.entries()]
    .filter(([,count])=>count >= MIN_REPORTING_CELL)
    .map(([key,count])=>Object.freeze({group:key,count}))
    .sort((a,b)=>a.group.localeCompare(b.group)));
}
export function recordLiveEvent() {
  throw new Error("HARD HOLD: live analytics, outbound attribution and visitor tracking are disabled");
}
export function inferAffiliateSalesFromClicks() {
  throw new Error("Affiliate sales cannot be inferred from clicks; seller reporting not authorized");
}
