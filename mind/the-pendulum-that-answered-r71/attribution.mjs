/** Final Vestige R71: privacy-first ANALYTICS PROPOSAL. Not included in WordPress candidates; executes nothing on import. */
export const ENABLED = false;
export const ALLOWED = Object.freeze({
  page: ['zen12-guide', 'ideomotor-investigation'],
  variant: ['A','B'],
  channel: ['direct','organic','tiktok','internal','unknown'],
  event: ['view','cta-intent','source-open','focus-nav'],
});
export function normalizeSyntheticEvent(input) {
  if (!ENABLED) return null;
  if (!input || typeof input !== 'object' || Array.isArray(input)) return null;
  const keys=Object.keys(input);
  if (keys.length !== 4 || keys.some(k => !Object.hasOwn(ALLOWED,k))) return null;
  if (keys.some(k => typeof input[k] !== 'string' || !ALLOWED[k].includes(input[k]))) return null;
  return Object.freeze({page:input.page,variant:input.variant,channel:input.channel,event:input.event});
}
export function previewAggregatesForOfflineReview(events, minimum=20) {
  if(!Array.isArray(events)||minimum<20) return [];
  const counts=new Map();
  for(const item of events){
    if(!item || typeof item!=='object' || Object.keys(item).length!==4) continue;
    const keys=Object.keys(ALLOWED);
    if(keys.some(k=>!Object.hasOwn(item,k)||typeof item[k]!=='string'||!ALLOWED[k].includes(item[k]))) continue;
    const key=keys.map(k=>item[k]).join('|');
    counts.set(key,(counts.get(key)||0)+1);
  }
  return Array.from(counts.entries()).filter(([,count])=>count>=minimum).map(([key,count])=>({dimensions:key.split('|'),count}));
}
/* Never accept referrer URL, IP, email, timestamps, query strings, free text, device ID, cookies, user agent,
   link identifier or URL parameters; no network calls, browser storage, external scripts, or telemetry are implemented.
   Event rates and purchases cannot be inferred from local synthetic testing. */
