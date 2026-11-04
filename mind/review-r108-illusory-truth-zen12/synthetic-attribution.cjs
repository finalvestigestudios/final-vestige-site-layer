"use strict";
/**
 * Final Vestige Mind & Perception — OFFLINE ONLY instrumentation design.
 * NOT connected to WordPress, Jetpack, pixel, analytics network, localStorage,
 * cookies, beacons, CRM, or any visitor event in production.
 * Synthetic tuples never claim unique viewers, sales, or merchant conversion.
 */
const ALLOWED = Object.freeze({
  event_type: new Set(["guide_view", "focus_route", "offer_intent", "outbound_click"]),
  topic: new Set(["attention", "suggestion", "meditation", "zen12"]),
  variant: new Set(["A", "B"]),
  source_bucket: new Set(["organic", "tiktok", "internal", "direct", "other"]),
  day: null,
  synthetic: new Set([true])
});
const FIELDS = Object.keys(ALLOWED);
const MIN_GROUP = 20;

function validateSynthetic(row) {
  if (!row || Array.isArray(row) || typeof row !== "object" ||
      (Object.getPrototypeOf(row) !== Object.prototype && Object.getPrototypeOf(row) !== null))
    throw new Error("expected plain synthetic event");
  const keys = Object.keys(row);
  if (keys.length !== FIELDS.length || !keys.every(k => FIELDS.includes(k)))
    throw new Error("unknown or missing keys: refuse any personally identifying fields");
  for (const [key, allowed] of Object.entries(ALLOWED)) {
    if (key === "day") {
      if (typeof row.day !== "string" || !/^20\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/.test(row.day))
        throw new Error("calendar-day only, never a timestamp");
      continue;
    }
    if (!allowed.has(row[key])) throw new Error("invalid synthetic categorical value");
  }
  return { event_type:row.event_type, topic:row.topic, variant:row.variant,
    source_bucket:row.source_bucket, day:row.day, synthetic:true };
}
function reportSyntheticOnly(rows) {
  if (!Array.isArray(rows)) throw new Error("expected array");
  const groups = new Map();
  for (const event of rows) {
    const v = validateSynthetic(event);
    const key = JSON.stringify([v.day,v.topic,v.variant,v.source_bucket,v.event_type]);
    groups.set(key,(groups.get(key)||0)+1);
  }
  const result = [];
  for (const [key,n] of groups.entries()) if(n>=MIN_GROUP) {
    const [day,topic,variant,source_bucket,event_type] = JSON.parse(key);
    result.push({day,topic,variant,source_bucket,event_type,events:n,
      caveat:"Synthetic counts only; not visitors, sales, or incremental lift"});
  }
  return result;
}
function recordLiveEvent() { throw new Error("LIVE COLLECTION DISABLED: require founder/privacy/QA release"); }
module.exports = {ALLOWED,MIN_GROUP,validateSynthetic,reportSyntheticOnly,recordLiveEvent};
