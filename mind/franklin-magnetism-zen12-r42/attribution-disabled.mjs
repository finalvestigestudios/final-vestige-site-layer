export const ENABLED = false;
const allowed = Object.freeze({ arm: ["A","B"], source: ["organic","tiktok","internal","unknown"], topic: ["mesmer","zen12","suggestion","other"], event: ["view","source-open","offer-intent"] });
export function normalizeSynthetic(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) return null;
  const keys=Object.keys(input).sort(), expected=Object.keys(allowed).sort();
  if (keys.length!==expected.length || keys.some((x,i)=>x!==expected[i])) return null;
  for (const key of expected) if (typeof input[key]!=="string" || !allowed[key].includes(input[key])) return null;
  return Object.freeze({...input});
}
export function reportSynthetic(events) {
  if (!Array.isArray(events)) return [];
  const counts=new Map();
  for (const x of events) { const v=normalizeSynthetic(x); if (!v) continue; const k=JSON.stringify(v); counts.set(k,(counts.get(k)||0)+1); }
  return [...counts].filter(([_,n])=>n>=10).map(([k,n])=>({bucket:JSON.parse(k),count:n}));
}
export function recordLive() { return false; } // HARD OFF; does not call DOM, storage, fetch, network or telemetry.
export function selfTest() {
 const valid={arm:"A",source:"organic",topic:"zen12",event:"view"};
 const cases=[
  normalizeSynthetic(valid)!==null,
  normalizeSynthetic({...valid,email:"x@y.com"})===null,
  normalizeSynthetic({...valid,ip:"127.0.0.1"})===null,
  normalizeSynthetic({...valid,referrer:"https://example.com"})===null,
  normalizeSynthetic({...valid,utm:"secret"})===null,
  normalizeSynthetic({...valid,source:"arbitrary"})===null,
  normalizeSynthetic({...valid,arm:"C"})===null,
  normalizeSynthetic({...valid,event:"purchase"})===null,
  normalizeSynthetic(null)===null,
  normalizeSynthetic([])===null,
  reportSynthetic(Array(9).fill(valid)).length===0,
  reportSynthetic(Array(10).fill(valid))[0]?.count===10,
  recordLive(valid)===false,
  ENABLED===false
 ];
 return {passed:cases.filter(Boolean).length,total:cases.length};
}
