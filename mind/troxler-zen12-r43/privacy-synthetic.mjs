// SYNTHETIC / UNPUBLISHED ONLY. No network, DOM, cookies, storage or real visitor processing.
export const ENABLED=false;
const allowed=Object.freeze({variant:["A","B"],source:["organic","tiktok","internal","unknown"],topic:["troxler","zen12","suggestion","other"],event:["guide-view","source-open","offer-intent"]});
export function normalizeSynthetic(e){if(!e||typeof e!=="object"||Array.isArray(e))return null;const keys=Object.keys(e).sort(),want=Object.keys(allowed).sort();if(keys.length!==want.length||keys.some((x,i)=>x!==want[i]))return null;for(const k of want)if(typeof e[k]!=="string"||!allowed[k].includes(e[k]))return null;return Object.freeze({...e});}
export function aggregateSynthetic(events){if(!Array.isArray(events))return [];const counts=new Map();for(const raw of events){const e=normalizeSynthetic(raw);if(!e)continue;const key=JSON.stringify(e);counts.set(key,(counts.get(key)||0)+1);}return [...counts].filter(([,n])=>n>=20).map(([key,count])=>({bucket:JSON.parse(key),count}));}
export function recordLive(){return false;}
