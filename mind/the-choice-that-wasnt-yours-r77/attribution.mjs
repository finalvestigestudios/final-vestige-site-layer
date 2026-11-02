/**
 * Privacy-by-default, DISABLED attribution design for an unpublished pilot.
 * No DOM, cookies, storage, network, referrers, IP addresses or identifiers.
 * Helpers process only an explicitly supplied array of synthetic test rows.
 * Not a production collector. Future activation requires a new reviewed change.
 */
export const ACTIVATION_ENABLED = false;
export const MIN_REPORTING_GROUP = 20;
const SCHEMA = Object.freeze({
  synthetic: [true],
  topic: ['choice-blindness','zen12'],
  channel: ['organic','tiktok','internal','direct'],
  variant: ['text','film'],
  action: ['guide_view','outbound_intent']
});
const KEYS = Object.freeze(Object.keys(SCHEMA));
export function validateSynthetic(row) {
  if (!row || typeof row !== 'object' || Array.isArray(row)) return false;
  if (Object.getPrototypeOf(row) !== Object.prototype) return false;
  if (Object.keys(row).length !== KEYS.length) return false;
  return KEYS.every(k => Object.prototype.hasOwnProperty.call(row,k) && SCHEMA[k].includes(row[k]));
}
export function summarizeSynthetic(rows) {
  if (!Array.isArray(rows)) throw new TypeError('Synthetic rows must be an array');
  const bucket = new Map();
  for (const row of rows) {
    if (!validateSynthetic(row)) throw new TypeError('Unapproved field/value or non-synthetic event');
    const key = [row.topic,row.channel,row.variant,row.action].join('|');
    bucket.set(key,(bucket.get(key) || 0)+1);
  }
  return [...bucket.entries()].filter(([,n])=>n>=MIN_REPORTING_GROUP).map(([key,count])=>({group:key,count})).sort((a,b)=>a.group.localeCompare(b.group));
}
export function collectOutboundEvent() {
  // FAIL CLOSED. Never call fetch/sendBeacon or write a cookie.
  return {enabled: ACTIVATION_ENABLED, recorded: false, reason:'Affiliate acceptance, consent and source approval unverified'};
}
