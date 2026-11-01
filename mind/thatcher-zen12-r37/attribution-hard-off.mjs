// This module is not imported by any production page. No side effects, no network.
export const ENABLED = false;
const VARIANTS=new Set(["text","film"]);
const SOURCES=new Set(["organic","tiktok","direct","internal","other"]);
const TOPICS=new Set(["zen12","thatcher"]);
const ACTIONS=new Set(["guide","source","transcript","offer-intent"]);
export function aggregateSynthetic(events, minimum=10){
 if(ENABLED) throw Error("Production activation prohibited");
 if(!Array.isArray(events)) throw TypeError("Synthetic events must be an array");
 if(!Number.isInteger(minimum) || minimum < 10) throw RangeError("Minimum is ten");
 const groups=new Map();
 for(const event of events){
  if(event===null || typeof event!=="object" || Array.isArray(event)) throw TypeError("Bad synthetic event");
  const keys=Object.keys(event).sort();
  if(keys.join(",")!=="action,source,topic,variant") throw Error("Extra or missing fields are prohibited");
  if(!VARIANTS.has(event.variant)||!SOURCES.has(event.source)||!TOPICS.has(event.topic)||!ACTIONS.has(event.action)) throw Error("Unexpected category");
  const key=[event.variant,event.source,event.topic,event.action].join("|");
  groups.set(key,(groups.get(key)||0)+1);
 }
 return [...groups].filter(([,n])=>n>=minimum).map(([key,count])=>({group:key,count}));
}
