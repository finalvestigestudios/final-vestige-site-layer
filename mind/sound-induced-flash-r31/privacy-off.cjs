"use strict";
/** Research-only synthetic adapter. Nothing in this module connects to web APIs, a database,
 * browser storage, analytics, or WordPress. No visitor events are sent. DEFAULT OFF.
 * Release would require separate scope, privacy review, and founder authorization. */
const ENABLED = false;
const K_MIN = 10;
const allowed = Object.freeze({
  variant: new Set(["A","B"]),
  topic: new Set(["zen12","sound_flash"]),
  event: new Set(["guide_view","source_open","free_practice_open","authorized_outbound_click"]),
  channel: new Set(["direct","organic_search","tiktok","internal","unknown"])
});
function ownPlainObject(value) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) return false;
  const proto = Object.getPrototypeOf(value);
  return proto === Object.prototype || proto === null;
}
function strictCategory(input) {
  // Deliberately no production ingestion or storage: this is a validator for future privacy design.
  if (!ENABLED) return null;
  if (!ownPlainObject(input)) return null;
  const names = Object.keys(input).sort();
  if (names.length !== 4 || names.join("|") !== "channel|event|topic|variant") return null;
  for (const key of names) if (typeof input[key] !== "string" || !allowed[key].has(input[key])) return null;
  return { variant:input.variant, topic:input.topic, event:input.event, channel:input.channel };
}
function syntheticAggregate(records, threshold=K_MIN) {
  if (!Number.isInteger(threshold) || threshold < K_MIN) throw Error("k-anonymity threshold cannot be reduced below ten");
  if (!Array.isArray(records)) throw TypeError("expected synthetic array");
  const counts = new Map();
  for (const row of records) {
    if (!ownPlainObject(row)) continue;
    const keys = Object.keys(row).sort();
    if (keys.length !== 4 || keys.join("|") !== "channel|event|topic|variant") continue;
    if (!keys.every(key => typeof row[key] === "string" && allowed[key].has(row[key]))) continue;
    const id=[row.variant,row.topic,row.event,row.channel].join("/");
    counts.set(id,(counts.get(id)||0)+1);
  }
  return [...counts].filter(([,count])=>count>=threshold).map(([category,count])=>({category,count})).sort((a,b)=>a.category.localeCompare(b.category));
}
function selfTest() {
 let checked=0;
 const ok=(condition,msg)=>{checked++;if(!condition)throw Error("privacy check "+checked+" failed: "+msg);};
 ok(ENABLED===false,"disabled"); ok(K_MIN===10,"minimum threshold");
 const clean={variant:"A",topic:"zen12",event:"guide_view",channel:"organic_search"};
 ok(strictCategory(clean)===null,"nothing ingested while off");
 for(const bad of [
  {...clean,ip:"127.0.0.1"}, {...clean,email:"a@example.org"}, {...clean,referrer:"https://example.com/person"},
  {...clean,session_id:"secret"}, {...clean,utm_campaign:"test"}, {...clean,userAgent:"name"},
  {...clean,channel:"q=private"}, {...clean,topic:"user-123"}, {...clean,event:"purchase"},
  {...clean,variant:"C"}, {...clean,channel:null}, {...clean,variant:undefined},
  null, [], "string", 14
 ])ok(strictCategory(bad)===null,"reject bad input");
 const ten=Array.from({length:10},()=>({...clean}));
 ok(syntheticAggregate(ten).length===1,"10 aggregate");ok(syntheticAggregate(ten.slice(0,9)).length===0,"9 suppressed");
 ok(syntheticAggregate(ten,11).length===0,"11 suppressed");
 for(const val of [9,0,-1,1.5,NaN]){let threw=false;try{syntheticAggregate(ten,val)}catch{threw=true}ok(threw,"reject bad k");}
 ok(syntheticAggregate([...ten,{...clean,email:"hidden"}]).length===1,"PII ignored");
 ok(syntheticAggregate([{...clean,channel:"direct"},...ten]).every(x=>x.category==="A/zen12/guide_view/organic_search"),"small alternate cell suppressed");
 ok(syntheticAggregate(ten).every(x=>!Object.keys(x).some(k=>/ip|email|referrer|session/i.test(k))),"aggregate outputs categories only");
 return {assertions:checked,enabled:ENABLED};
}
if (typeof module!=="undefined") module.exports={ENABLED,K_MIN,strictCategory,syntheticAggregate,selfTest};
if (typeof require!=="undefined" && typeof module!=="undefined" && require.main===module)console.log(JSON.stringify(selfTest()));
