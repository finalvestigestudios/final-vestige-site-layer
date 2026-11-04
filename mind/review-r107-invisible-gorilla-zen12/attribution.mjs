/** Offline demonstration only. Not imported, not installed or hooked on any live page. */
export const LIVE_CAPTURE_ENABLED = false;
const ALLOWED={
 event:new Set(["guide_view","guide_read","film_concept_read","focus_path_open","outbound_intent_disabled"]),
 topic:new Set(["zen12","invisible_gorilla","puysegur","focus"]),
 channel:new Set(["search","tiktok","internal","direct","unknown"]),
 variant:new Set(["text","poster_transcript"])
};
export function parseSynthetic(row){
 if(!row||typeof row!=="object"||Array.isArray(row))return null;
 const keys=Object.keys(row),accepted=Object.keys(ALLOWED);
 if(keys.length!==4||keys.some(k=>!accepted.includes(k)))return null;
 if(!accepted.every(k=>ALLOWED[k].has(row[k])))return null;
 return Object.freeze({event:row.event,topic:row.topic,channel:row.channel,variant:row.variant});
}
export function summarizeSynthetic(rows,minCell=20){
 if(!Array.isArray(rows)||!Number.isInteger(minCell)||minCell<20)throw Error("invalid aggregate settings");
 const m=new Map();let rejected=0;
 for(const raw of rows){const r=parseSynthetic(raw);if(!r){rejected++;continue}const key=Object.values(r).join("|");m.set(key,(m.get(key)||0)+1)}
 return {live:false,rejected,groups:Array.from(m).filter(([k,n])=>n>=minCell).map(([key,count])=>({key,count}))};
}
export function captureLive(){return {enabled:false,recorded:false}}
