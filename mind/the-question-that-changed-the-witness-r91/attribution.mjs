/** Mind R91: synthetic-only illustration. OFF. No emitted events, cookies, fingerprints, URLs, personal identifiers or network. */
export const ENABLED=false;
export const MIN_CELL=20;
const events=new Set(["article_view","guide_view","free_resource_interest","offer_interest_disabled"]);
const topics=new Set(["misinformation","zen12","mind"]);
const sources=new Set(["organic","tiktok","direct","internal","other"]);
export function validateSynthetic(input){
 if(!input||typeof input!=="object"||Array.isArray(input)||Object.getPrototypeOf(input)!==Object.prototype)throw Error("Plain categorical object required");
 const keys=Object.keys(input).sort();
 if(keys.join(",")!=="event,source,topic")throw Error("Unknown field, PII, URL, or referrer rejected");
 if(!events.has(input.event)||!topics.has(input.topic)||!sources.has(input.source))throw Error("Unrecognized categorical value");
 return Object.freeze({event:input.event,topic:input.topic,source:input.source});
}
export function syntheticAggregate(rows){
 if(!Array.isArray(rows))throw Error("Array required");
 const counter=new Map();
 for(const raw of rows){const e=validateSynthetic(raw);const key=[e.event,e.topic,e.source].join("|");counter.set(key,(counter.get(key)||0)+1)}
 return [...counter].filter(([,count])=>count>=MIN_CELL).map(([key,count])=>{const[event,topic,source]=key.split("|");return{event,topic,source,count}});
}
// Intentionally no emit, transport, persistence, purchase attribution or browser integration.
