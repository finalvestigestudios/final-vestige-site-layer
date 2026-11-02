// R61: Synthetic-only, off-by-default model. Never include in production page without separate review.
export const ATTRIBUTION_ENABLED = false;
const TOPICS = new Set(['braid','zen12-guide','focus']);
const VARIANTS = new Set(['A','B']);
const CHANNELS = new Set(['organic','tiktok','direct','other']);
export function validateSynthetic(row){
 if(!row||Object.getPrototypeOf(row)!==Object.prototype)return false;
 const keys=Object.keys(row).sort();
 if(keys.join(',')!=='channel,topic,variant')return false;
 return TOPICS.has(row.topic)&&VARIANTS.has(row.variant)&&CHANNELS.has(row.channel);
}
export function record(){return false;}
export function summarizeSynthetic(rows, min=20){
 if(!Array.isArray(rows)||!Number.isInteger(min)||min<20)return [];
 if(rows.some(x=>!validateSynthetic(x)))return [];
 const grouped=new Map();
 for(const x of rows){const key=[x.topic,x.variant,x.channel].join('|');grouped.set(key,(grouped.get(key)||0)+1)}
 return [...grouped.entries()].filter(([,n])=>n>=min).map(([k,n])=>({group:k,count:n})).sort((a,b)=>a.group.localeCompare(b.group));
}
