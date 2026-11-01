// Final Vestige Mind R42 — OFFLINE ONLY classification experiment.
// DO NOT wire this module to production, DOM listeners, network, WordPress or storage.
// This is not a privacy guarantee and no approval for data collection is implied.
export const ENABLED = false;
const allowed = Object.freeze({
  topic: ['historical_suggestion','perception','meditation'],
  asset: ['zen12_guide','history_archive'],
  variant: ['text','film'],
  slot: ['context','foot'],
  destination: ['seller_unavailable','focus_page']
});
export function classify(record) {
  if (!record || typeof record!=='object' || Array.isArray(record)) return null;
  const keys=Object.keys(record);
  if (keys.length !== Object.keys(allowed).length || !keys.every(key=>Object.hasOwn(allowed,key))) return null;
  const result=Object.create(null);
  for (const key of Object.keys(allowed)){
    if (typeof record[key]!=='string' || !allowed[key].includes(record[key])) return null;
    result[key]=record[key];
  }
  return result;
}
export function syntheticReport(testRecords,threshold=10) {
  if (!Array.isArray(testRecords)||!Number.isSafeInteger(threshold)||threshold<10) return [];
  const counts=new Map();
  for(const item of testRecords){
    const rec=classify(item); if(!rec) continue;
    const bucket=Object.values(rec).join('|');
    counts.set(bucket,(counts.get(bucket)||0)+1);
  }
  return [...counts].filter(([,count])=>count>=threshold).map(([bucket,count])=>({bucket,count}));
}
export function canCollect(){return ENABLED;} // False; no production activation hooks.
