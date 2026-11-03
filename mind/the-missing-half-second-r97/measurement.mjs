/**
 * FV Mind R97: PURE, OFFLINE, SYNTHETIC-ONLY measurement design.
 * No event listener, no network, no cookies, no localStorage and no vendor pixel.
 * Must not be deployed without written privacy/partner authorization and QA.
 * Never accepts/refers to purchaser reports. A click is NOT a purchase.
 */
const CATEGORIES = Object.freeze({
 source: Object.freeze(['organic','tiktok','direct','internal','other']),
 topic: Object.freeze(['attentional-blink','zen12-guide']),
 variant: Object.freeze(['text','film-concept']),
 action: Object.freeze(['guide-view','read-through','outbound-intent'])
});
const KEYS=Object.freeze(['source','topic','variant','action']);
export function normalizeSyntheticEvent(input){
 if(!input || typeof input!=='object' || Array.isArray(input) || Object.getPrototypeOf(input)!==Object.prototype)
   throw new TypeError('Plain object required');
 const own=Object.keys(input);
 if(own.length!==KEYS.length || own.some(k=>!KEYS.includes(k)) || KEYS.some(k=>!Object.hasOwn(input,k))) throw new Error('Unexpected or missing field; no identifiers or URLs permitted');
 const out={};
 for(const k of KEYS){if(typeof input[k]!=='string'||!CATEGORIES[k].includes(input[k])) throw new Error('Unapproved categorical value');out[k]=input[k];}
 return Object.freeze(out);
}
/**
 * Suppresses groups smaller than 20. Reports groups only; never returns
 * a raw event. Only for tests with synthetic inputs. No anonymous user IDs.
 * For future production, require privacy review incl. differencing risks
 * across arbitrary filtered queries; never infer sales from outbound clicks.
 */
export function syntheticAggregate(events,{minimum=20}={}){
 if(!Array.isArray(events)||minimum!==20) throw new Error('Fixed privacy threshold 20');
 const counts=new Map();
 for(const item of events){const e=normalizeSyntheticEvent(item);const key=KEYS.map(k=>e[k]).join('|');counts.set(key,(counts.get(key)||0)+1);}
 const rows=[];
 for(const [key,count] of counts){if(count<20)continue;const [source,topic,variant,action]=key.split('|');rows.push(Object.freeze({source,topic,variant,action,count}));}
 return Object.freeze(rows.sort((a,b)=>a.source.localeCompare(b.source)||a.topic.localeCompare(b.topic)||a.variant.localeCompare(b.variant)||a.action.localeCompare(b.action)));
}
