'use strict';
/**
 * FV Mind R109 — SYNTHETIC, IN-MEMORY review harness, NOT a browser collector.
 * Deployment is deliberately impossible through this module: recordLive throws.
 * No cookies, networking, storage, logs or affiliate conversion attribution.
 * Coarse daily event totals are NOT people, purchasers, revenue, or A/B uplift.
 */
const SCHEMA = Object.freeze({
  day: /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/,
  channel: ['tiktok', 'organic', 'internal', 'direct', 'unknown'],
  variant: ['A', 'B'],
  topic: ['attention', 'perception', 'suggestion', 'practice', 'product'],
  event: ['page_view', 'source_read', 'offer_intent']
});
const EXACT_KEYS = Object.freeze(['channel', 'day', 'event', 'topic', 'variant']);
const MIN_CELL = 20;
function validDay(value) {
  if (typeof value !== 'string' || !SCHEMA.day.test(value)) return false;
  const [y,m,d] = value.split('-').map(Number);
  const at = new Date(Date.UTC(y,m-1,d));
  return at.getUTCFullYear() === y && at.getUTCMonth() === m-1 && at.getUTCDate() === d;
}
function sanitizeSynthetic(record) {
  if (!record || typeof record !== 'object' || Array.isArray(record)) throw Error('invalid synthetic record');
  const keys = Object.keys(record).sort();
  if (keys.length !== EXACT_KEYS.length || keys.some((k,i) => k !== EXACT_KEYS[i])) {
    throw Error('strict schema: extra/missing/identity fields prohibited');
  }
  if (!validDay(record.day)) throw Error('invalid day');
  for (const k of ['channel','variant','topic','event']) {
    if (typeof record[k] !== 'string' || !SCHEMA[k].includes(record[k])) throw Error('invalid categorical dimension');
  }
  return Object.freeze({ day: record.day, channel:record.channel, variant:record.variant, topic:record.topic, event:record.event });
}
function aggregateSynthetic(records) {
  if (!Array.isArray(records) || records.length > 100000) throw Error('expected bounded array');
  const buckets = new Map();
  for (const raw of records) {
    const r = sanitizeSynthetic(raw);
    const key = [r.day,r.channel,r.variant,r.topic,r.event].join('|');
    buckets.set(key,(buckets.get(key) || 0) + 1);
  }
  return Array.from(buckets,([key,events]) => {
    const [day,channel,variant,topic,event] = key.split('|');
    return {day,channel,variant,topic,event,events};
  }).filter(row=>row.events >= MIN_CELL).sort((a,b)=>[a.day,a.channel,a.variant,a.topic,a.event].join('|').localeCompare([b.day,b.channel,b.variant,b.topic,b.event].join('|')));
}
function recordLive(){throw Error('LIVE ATTRIBUTION DISABLED: partner permissions and user privacy review required');}
function recordPurchase(){throw Error('PURCHASER DATA PROHIBITED');}
module.exports = Object.freeze({MIN_CELL,validDay,sanitizeSynthetic,aggregateSynthetic,recordLive,recordPurchase});
