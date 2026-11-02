/* OFF by default, standalone synthetic model: no browser instrumentation, no network, no cookies. */
export const ACTIVE=false;
const allowedVariants=new Set(['text','video']);
const allowedTopics=new Set(['attention','suggestion','meditation']);
export function acceptSynthetic(record){
 if(ACTIVE) throw new Error('Visitor collection requires separate release');
 if(!record||Object.keys(record).some(k=>!['variant','topic','event'].includes(k))) return false;
 return allowedVariants.has(record.variant)&&allowedTopics.has(record.topic)&&record.event==='outbound-intent';
}
export function aggregateSynthetic(records){
 const safe=records.filter(acceptSynthetic);
 const counts=new Map();
 for(const r of safe){const k=r.variant+':'+r.topic;counts.set(k,(counts.get(k)||0)+1);}
 return [...counts].filter(([,n])=>n>=20).map(([key,count])=>({key,count}));
}
