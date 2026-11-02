// R79: pure synthetic policy simulator. Never loaded on a published page.
export const ACTIVATION_ENABLED = false;
export const MIN_REPORTING_GROUP = 20;
const allow = Object.freeze({synthetic:[true], topic:['zen12','inattentional-blindness'],channel:['organic','tiktok','direct','focus'],variant:['text','film'],action:['guide_view','outbound_intent']});
export function validateSynthetic(obj){
 if(!obj || Object.getPrototypeOf(obj)!==Object.prototype) return false;
 const keys=Object.keys(obj);
 return keys.length===5&&Object.keys(allow).every(key=>Object.hasOwn(obj,key)&&allow[key].includes(obj[key]))&&keys.every(key=>Object.hasOwn(allow,key));
}
export function summarizeSynthetic(events){
 if(!Array.isArray(events) || !events.every(validateSynthetic)) throw new TypeError('Synthetic predefined values only');
 const m=new Map();
 for(const e of events){const k=[e.topic,e.channel,e.variant,e.action].join('|');m.set(k,(m.get(k)||0)+1)}
 return [...m.entries()].filter(([,n])=>n>=MIN_REPORTING_GROUP).map(([group,count])=>({group,count,synthetic:true}));
}
export function compareSynthetic(events){
 if(!Array.isArray(events)||!events.every(validateSynthetic))throw new TypeError('Synthetic fixtures only');
 return ['text','film'].map(variant=>{
  const views=events.filter(e=>e.variant===variant&&e.action==='guide_view').length;
  const intents=events.filter(e=>e.variant===variant&&e.action==='outbound_intent').length;
  return {variant,views:views>=MIN_REPORTING_GROUP?views:null,intents:intents>=MIN_REPORTING_GROUP?intents:null,intent_rate:views>=MIN_REPORTING_GROUP&&intents>=MIN_REPORTING_GROUP?intents/views:null,synthetic:true};
 });
}
export function collectOutboundEvent(){return Object.freeze({enabled:false,recorded:false,reason:'No merchant authorization, no visitor instrumentation'});}
