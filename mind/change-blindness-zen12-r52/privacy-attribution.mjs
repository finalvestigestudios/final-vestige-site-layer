// R52 first-party, offline-only experiment specification. NO browser runtime and NO event sender.
export const ATTRIBUTION_ENABLED = false;
const EVENT = new Set(['guide_view', 'optional_video_play', 'source_follow', 'focus_follow', 'future_merchant_outbound']);
const TOPIC = new Set(['change_blindness', 'zen12_guide']);
const VARIANT = new Set(['text', 'video']);
const CHANNEL = new Set(['direct', 'organic_search', 'social', 'internal', 'unknown']);
const KEYS = new Set(['event', 'topic', 'variant', 'channel']);
const SAFE = Object.freeze({ minimumGroup: 20, enabled: false });

export function validateSyntheticEvent(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input) || Object.getPrototypeOf(input)!==Object.prototype) {
    throw new TypeError('expected a plain categorical event object');
  }
  const keys = Object.keys(input);
  if(keys.length!==4 || keys.some(k=>!KEYS.has(k))) throw new Error('unapproved or identifying field');
  if(!EVENT.has(input.event) || !TOPIC.has(input.topic) || !VARIANT.has(input.variant) || !CHANNEL.has(input.channel)){
    throw new Error('unapproved categorical value');
  }
  return Object.freeze({event:input.event, topic:input.topic, variant:input.variant, channel:input.channel});
}
// Deliberately impossible to activate by sending data; cannot access fetch, beacons, cookies or storage.
export function recordLiveEvent(_input) { return Object.freeze({recorded:false, reason:'commercial permissions and release QA incomplete'}); }
export function aggregateSyntheticEvents(items, minimum=SAFE.minimumGroup) {
  if(!Array.isArray(items) || !Number.isInteger(minimum) || minimum<20) throw new TypeError('invalid synthetic cohort');
  const bins = new Map();
  for(const item of items){
    const v=validateSyntheticEvent(item);
    const key=[v.event,v.topic,v.variant,v.channel].join('|');
    bins.set(key,(bins.get(key)||0)+1);
  }
  return [...bins].filter(([,count])=>count>=minimum).sort((a,b)=>a[0].localeCompare(b[0])).map(([key,count])=>({group:key,count}));
}
export const privacyDesign = SAFE;
