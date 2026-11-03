/** FV Mind R88: synthetic fixture-only attribution proposal. NOT IMPORTED by WordPress.
 * No cookies, browser APIs, network, localStorage, IPs, raw referrers or outbound URLs.
 * Nothing is active while ENABLED=false. Partner conversion != outbound click.
 */
export const ENABLED = false;
export const MIN_GROUP = 20;
const VALID = Object.freeze({
  provenance: new Set(['synthetic_test']),
  event: new Set(['guide_view','guide_source_click','focus_internal_click','offer_control_seen','synthetic_outbound_click']),
  source: new Set(['organic_search','tiktok','internal','direct','unknown']),
  topic: new Set(['autosuggestion','zen12','total_focus','attention']),
  variant: new Set(['A','B','NA'])
});
const FIELDS = Object.freeze(Object.keys(VALID));
export function validateSynthetic(row) {
  if (!row || typeof row !== 'object' || Array.isArray(row) || Object.getPrototypeOf(row)!==Object.prototype)
    throw new TypeError('plain object required');
  if (Object.keys(row).length !== FIELDS.length || !FIELDS.every(k=>Object.hasOwn(row,k)))
    throw new TypeError('unexpected, missing or identifying field');
  for(const k of FIELDS) if(typeof row[k]!=='string'||!VALID[k].has(row[k]))
    throw new TypeError('invalid controlled value for '+k);
  return {event:row.event,source:row.source,topic:row.topic,variant:row.variant};
}
export function aggregateSynthetic(rows) {
  if (!Array.isArray(rows)) throw new TypeError('array required');
  const groups = new Map();
  for(const row of rows) {
    const v=validateSynthetic(row);
    const key=[v.event,v.source,v.topic,v.variant].join('|');
    groups.set(key,(groups.get(key)||0)+1);
  }
  return [...groups].filter(([,count])=>count>=MIN_GROUP).map(([key,count])=>{
    const [event,source,topic,variant]=key.split('|');
    return {event,source,topic,variant,count};
  }).sort((a,b)=>b.count-a.count);
}
export function productionTrack() {
  throw new Error('NOT ACTIVE: affiliate permission/privacy/release gates closed');
}
