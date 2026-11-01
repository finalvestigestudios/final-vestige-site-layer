// Only synthetic cohort modelling. NO collection, transport, storage, cookies, analytics or real visitor events.
export const COLLECTION_ENABLED=false;
export const MIN_REPORTING_CELL=20;
const allowed={source:['organic','tiktok','direct','internal'],topic:['coué','zen12-guide','mind-hub'],variant:['text','film'],action:['guide-read','source-read','cta-pending']};
export function validateSyntheticEvent(x){
 if(x===null||Array.isArray(x)||typeof x!=='object'||Object.getPrototypeOf(x)!==Object.prototype)throw Error('STRICT_PLAIN_OBJECT');
 if(Object.keys(x).sort().join('|')!==Object.keys(allowed).sort().join('|'))throw Error('UNKNOWN_OR_MISSING_FIELD');
 for(const k of Object.keys(allowed))if(!allowed[k].includes(x[k]))throw Error('NON_ALLOWLISTED_VALUE');
 return Object.freeze({...x});
}
export function summarizeSyntheticOnly(rows,minCell=MIN_REPORTING_CELL){
 if(!Array.isArray(rows)||minCell<MIN_REPORTING_CELL)throw Error('INVALID_SYNTHETIC_COLLECTION');
 const counts=new Map();for(const x of rows){const v=validateSyntheticEvent(x);const k=JSON.stringify(v);counts.set(k,(counts.get(k)||0)+1)}
 const visible=[];let withheld=0;for(const [k,n] of counts){if(n<minCell){withheld++;continue}visible.push({...JSON.parse(k),n})}
 return {visible,withheld};
}
export function recordRealVisitorEvent(){throw Error('HARD_OFF_NO_LIVE_TRACKING')}
