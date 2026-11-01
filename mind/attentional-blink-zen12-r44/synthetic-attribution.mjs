/* Synthetic-only evaluation primitive. No DOM use, listener, network, storage or live wiring. */
const allowed=Object.freeze({variant:new Set(["text","film"]),topic:new Set(["attentional-blink"]),event:new Set(["guide_view","outbound_intent"]),channel:new Set(["organic","tiktok","direct","unknown"])});
export function sanitizeSyntheticRecord(input){
 if(!input||typeof input!=="object"||Array.isArray(input))return null;
 const keys=Object.keys(input);
 if(keys.length!==4||keys.some(k=>!Object.prototype.hasOwnProperty.call(allowed,k)))return null;
 for(const key of keys)if(typeof input[key]!=="string"||!allowed[key].has(input[key]))return null;
 return Object.freeze({variant:input.variant,topic:input.topic,event:input.event,channel:input.channel});
}
export function summarizeSyntheticGroups(records,minimum=20){
 if(!Array.isArray(records)||!Number.isInteger(minimum)||minimum<20)return [];
 const counts=new Map();
 for(const input of records){const safe=sanitizeSyntheticRecord(input);if(!safe)continue;const key=[safe.variant,safe.topic,safe.event,safe.channel].join("|");counts.set(key,(counts.get(key)||0)+1)}
 return [...counts.entries()].filter(([,n])=>n>=minimum).map(([key,count])=>Object.freeze({key,count}));
}
