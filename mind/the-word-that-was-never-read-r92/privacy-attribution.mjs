/**
 * Final Vestige Studios — R92 privacy-safe attribution CONTRACT, not live tracker.
 * No browser listeners, fetch, pixels, cookies, storage, persistent identifiers,
 * raw URLs, user agents, geolocation, IP, timestamps or affiliate endpoints.
 * This file imports nothing and attaches nothing to window. It is for local
 * synthetic testing until the founder and partner approve measurement.
 */
export const ACTIVATION = Object.freeze({
  collect_live: false,
  emit_merchant_click: false,
  ingest_partner_purchase_records: false,
  supported_channels: Object.freeze([]),
  minimum_public_cell: 20
});
const own = (o,k) => Object.prototype.hasOwnProperty.call(o,k);
const topics = new Set(["perception","suggestion","practice","zen12-guide"]);
const sources = new Set(["organic-search","tiktok","internal","other"]);
const variants = new Set(["A","B"]);
const events = new Set(["guide_view","qualified_guide_read","disabled_offer_interest"]);
const keys = new Set(["synthetic","event","topic","source_bucket","variant"]);
export function verifySynthetic(event) {
  if (!event || Object.getPrototypeOf(event) !== Object.prototype) throw new TypeError("Plain object required");
  const present=Object.keys(event);
  if (present.length!==keys.size || present.some(k=>!keys.has(k))) throw new TypeError("Unexpected field or missing field (PII rejected)");
  if (event.synthetic !== true) throw new Error("Only synthetic events are accepted");
  if (!topics.has(event.topic) || !sources.has(event.source_bucket) || !variants.has(event.variant) || !events.has(event.event)) throw new TypeError("Categorical allowlist failed");
  return Object.freeze({...event});
}
export function aggregateSynthetic(rows, minimum=ACTIVATION.minimum_public_cell) {
  if(!Number.isInteger(minimum)||minimum<20) throw new RangeError("Minimum cell size must be >=20");
  if(!Array.isArray(rows) || rows.length>100000) throw new TypeError("Synthetic array required");
  const counts=new Map();
  for(const raw of rows) {
    const item=verifySynthetic(raw);
    const key=[item.event,item.topic,item.source_bucket,item.variant].join("|");
    counts.set(key,(counts.get(key)||0)+1);
  }
  return [...counts.entries()].filter(([k,n])=>n>=minimum)
    .map(([key,count])=>Object.freeze({dimensions:key.split("|"),count}))
    .sort((a,b)=>a.dimensions.join("|").localeCompare(b.dimensions.join("|")));
}
export function activateMerchantLink() { throw new Error("HARD HOLD: partner and release approval absent"); }
export function collectLiveEvent() { throw new Error("HARD HOLD: live tracking disabled"); }
export function inferSalesFromClicks() { throw new Error("Invalid inference: purchases require approved aggregate partner reporting"); }
