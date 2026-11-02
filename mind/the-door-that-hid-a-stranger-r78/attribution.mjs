/**
 * FV Mind R78: SYNTHETIC ONLY, DISABLED, zero-PII attribution design.
 * Never import into production pages; no DOM, cookies, localStorage,
 * network, URL search params, referer/referrer, fingerprint or user IDs.
 * All real collection and partner reporting require separately approved
 * engineering and privacy reviews. No sales or conversions can be inferred.
 */
export const ACTIVATION_ENABLED = false;
export const MIN_REPORTING_GROUP = 20;
export const VALID = Object.freeze({
  synthetic: Object.freeze([true]),
  topic: Object.freeze(['change-blindness','zen12']),
  channel: Object.freeze(['organic','tiktok','internal','direct']),
  variant: Object.freeze(['text','film']),
  action: Object.freeze(['guide_view','outbound_intent'])
});
const FIELDS = Object.freeze(Object.keys(VALID));
export function validateSynthetic(row) {
  if (!row || typeof row !== 'object' || Array.isArray(row)) return false;
  if (Object.getPrototypeOf(row) !== Object.prototype) return false;
  const keys=Object.keys(row);
  if (keys.length!==FIELDS.length) return false;
  return FIELDS.every(key=>Object.prototype.hasOwnProperty.call(row,key)&&VALID[key].includes(row[key]));
}
export function summarizeSynthetic(rows) {
  if (!Array.isArray(rows)) throw new TypeError('Expected array of synthetic events');
  const groups=new Map();
  for(const row of rows){
    if(!validateSynthetic(row)) throw new TypeError('Invalid synthetic record or unapproved field');
    const key=[row.topic,row.channel,row.variant,row.action].join('|');
    groups.set(key,(groups.get(key)||0)+1);
  }
  return [...groups].filter(([,count])=>count>=MIN_REPORTING_GROUP)
    .map(([group,count])=>({group,count,kind:'SYNTHETIC_NOT_REAL_USER_DATA'}))
    .sort((a,b)=>a.group.localeCompare(b.group));
}
export function compareSynthetic(rows){
  const agg=summarizeSynthetic(rows);
  const index=new Map(agg.map(x=>[x.group,x.count]));
  const result=[];
  for(const variant of VALID.variant){
    const views=index.get(['zen12','organic',variant,'guide_view'].join('|'));
    const intents=index.get(['zen12','organic',variant,'outbound_intent'].join('|'));
    result.push({variant,views:views??null,intents:intents??null,
      intent_rate:views!==undefined&&intents!==undefined&&views>0?intents/views:null,
      label:'SIMULATION ONLY; NO REAL CONVERSION CLAIM'});
  }
  return result;
}
export function collectOutboundEvent(){
  return Object.freeze({enabled:false,recorded:false,
    reason:'No production collector; affiliate approval and privacy review are missing'});
}
