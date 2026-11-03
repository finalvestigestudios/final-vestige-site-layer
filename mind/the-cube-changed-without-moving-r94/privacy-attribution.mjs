// Pure, disabled, synthetic-only proposed measurement contract. NOT imported in WP.
export const APPROVED_SOURCES = Object.freeze(["organic","tiktok","direct","internal","other"]);
export const APPROVED_VARIANTS = Object.freeze(["A","B"]);
export const APPROVED_TOPICS = Object.freeze(["necker","zen12","mind"]);
export const MIN_REPORT_CELL = 20;
const KEYS = Object.freeze(["event","source","variant","topic"]);
export function validateAggregateEvent(x) {
  if (!x || Array.isArray(x) || typeof x !== "object") throw Error("invalid event");
  const actual=Object.keys(x).sort();
  if (actual.join("|")!==[...KEYS].sort().join("|")) throw Error("unknown or missing fields");
  if(x.event!=="outbound_intent") throw Error("event not authorized");
  if(!APPROVED_SOURCES.includes(x.source)||!APPROVED_VARIANTS.includes(x.variant)||!APPROVED_TOPICS.includes(x.topic)) throw Error("not in allowlist");
  return {event:x.event,source:x.source,variant:x.variant,topic:x.topic};
}
export function syntheticAggregate(rows){
  if(!Array.isArray(rows))throw Error("rows required");
  const buckets=new Map();
  for(const item of rows){
    const r=validateAggregateEvent(item);const key=[r.event,r.source,r.variant,r.topic].join("|");
    buckets.set(key,(buckets.get(key)||0)+1);
  }
  return [...buckets.entries()].filter(([,n])=>n>=MIN_REPORT_CELL).map(([key,count])=>({category:key,count}));
}
// No IP, timestamp, browser fingerprint, persistent ID, URL, referrer string, cookie,
// customer identifier, pixel, fetch, keepalive, storage, listener or partner reporting.
// No WP deployment. This cannot yield unique-user counts or conversion rates.
