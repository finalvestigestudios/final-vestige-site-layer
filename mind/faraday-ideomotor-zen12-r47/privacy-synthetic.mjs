// Mind R47: synthetic-only, side-effect-free attribution model. NEVER wire into production without approval.
// No cookies, external network, URL strings, referrer capture, IP addresses or persisted identifiers.
export const COLLECTION_ENABLED = false;
export const MIN_REPORTING_CELL = 20;
const allowed = Object.freeze({
 source: Object.freeze(['tiktok','organic','internal','direct','unknown']),
 topic: Object.freeze(['ideomotor','perception','zen12-guide','focus']),
 variant: Object.freeze(['text','optional-film','not-applicable']),
 action: Object.freeze(['page-view','guide-read','outbound-intent','focus-navigation'])
});
export function validateSyntheticEvent(record) {
 if (record === null || typeof record !== 'object' || Array.isArray(record)) throw new TypeError('not a plain event');
 if (Object.getPrototypeOf(record) !== Object.prototype) throw new TypeError('prototype rejected');
 const keys=Object.keys(record).sort();
 const expected=Object.keys(allowed).sort();
 if (keys.length!==expected.length || keys.some((k,i)=>k!==expected[i])) throw new TypeError('unexpected or missing fields');
 for (const key of expected) if(typeof record[key]!=='string'||!allowed[key].includes(record[key])) throw new TypeError('invalid category: '+key);
 return Object.freeze({source:record.source,topic:record.topic,variant:record.variant,action:record.action});
}
export function summarizeSyntheticOnly(records, minimum=MIN_REPORTING_CELL) {
 if (!Array.isArray(records) || !Number.isSafeInteger(minimum) || minimum<MIN_REPORTING_CELL) throw new TypeError('invalid aggregation');
 const counts=new Map();
 for (const input of records) {
  const x=validateSyntheticEvent(input);
  const key=[x.source,x.topic,x.variant,x.action].join('|');
  counts.set(key,(counts.get(key)||0)+1);
 }
 const visible=[];let withheldCells=0;
 for (const [key,n] of counts) {
  if(n<minimum){withheldCells++;continue}
  const [source,topic,variant,action]=key.split('|');
  visible.push(Object.freeze({source,topic,variant,action,n}));
 }
 return Object.freeze({visible:Object.freeze(visible),withheldCells,minimum,synthetic:true});
}
export function recordRealVisitorEvent() { throw new Error('HARD_OFF: partner authorization, privacy review and founder release are absent'); }
