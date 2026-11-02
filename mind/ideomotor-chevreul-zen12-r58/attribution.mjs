/* R58 concept only: NO visitor tracking, persistence, network, or cookies.
 * Do not enable without partner authorization, founder approval, privacy review and public notice.
 */
export const ATTRIBUTION_ENABLED = false;
const channels = new Set(["organic_search","tiktok","direct","internal","unknown"]);
const topics = new Set(["ideomotor","history_suggestion","meditation","other"]);
const variants = new Set(["A","B"]);
const actions = new Set(["guide_view","proposed_outbound_click"]);
const allowed = new Set(["channel","topic","variant","action"]);
export function sanitizeCategoricalEvent(input) {
  if (!input || Object.getPrototypeOf(input)!==Object.prototype) return null;
  const keys=Object.keys(input);
  if (keys.length !== 4 || keys.some(key=>!allowed.has(key))) return null;
  if (!channels.has(input.channel) || !topics.has(input.topic)
      || !variants.has(input.variant) || !actions.has(input.action)) return null;
  return Object.freeze({channel:input.channel,topic:input.topic,variant:input.variant,action:input.action});
}
export function recordEvent(input) {
  if (!ATTRIBUTION_ENABLED) return Object.freeze({recorded:false,reason:"disabled_by_design"});
  const sanitized=sanitizeCategoricalEvent(input);
  return sanitized ? Object.freeze({recorded:false,reason:"no_approved_collector"})
    : Object.freeze({recorded:false,reason:"invalid"});
}
export function aggregateSyntheticOnly(rows,minimum=20) {
  if (!Array.isArray(rows) || minimum < 20 || !Number.isSafeInteger(minimum)) throw Error("invalid synthetic data");
  const counts=new Map();
  for(const row of rows){
    const e=sanitizeCategoricalEvent(row);
    if(!e) throw Error("invalid event contains unknown or identifying fields");
    const key=[e.channel,e.topic,e.variant,e.action].join("/");
    counts.set(key,(counts.get(key)||0)+1);
  }
  return Object.freeze([...counts.entries()].filter(([,n])=>n>=minimum)
    .sort((a,b)=>a[0].localeCompare(b[0]))
    .map(([key,count])=>Object.freeze({key,count})));
}
// Deliberately no SDK, outbound request, browser hooks, storage, raw referrer,
// client IP, cookie, email, user agent, timestamp, fingerprint or pseudonymous ID.
