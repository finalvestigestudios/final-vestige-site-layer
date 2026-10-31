/* Offline, non-deployed aggregation contract. No pixel, network, cookie or user-level storage. */
"use strict";
const PAGE_KEYS=new Set(["meditation-attentional-blink","zen12-guide","total-focus-guide","focus-shot-guide"]);
const EVENTS=new Set(["content_view","source_click","focus_outbound","video_play","affiliate_outbound"]);
const VARIANTS=new Set(["text","optional_film","not_applicable"]);
const ACQUISITION=new Set(["organic_search","social_video","direct","other"]);
const FIELDS=["date_utc","page_key","variant","event_name","acquisition_group"];
function validDate(s){if(typeof s!=="string"||!/^\d{4}-\d{2}-\d{2}$/.test(s))return false;const d=new Date(s+"T00:00:00Z");return Number.isFinite(d.valueOf())&&d.toISOString().slice(0,10)===s;}
function checked(record){
 if(!record||typeof record!=="object"||Array.isArray(record)||Object.getPrototypeOf(record)!==Object.prototype)throw Error("Invalid event object");
 const keys=Object.keys(record);
 if(keys.length!==5||keys.some(k=>!FIELDS.includes(k)))throw Error("Extra or missing event field; raw referrer, identifiers and URLs prohibited");
 if(!validDate(record.date_utc)||!PAGE_KEYS.has(record.page_key)||!VARIANTS.has(record.variant)||!EVENTS.has(record.event_name)||!ACQUISITION.has(record.acquisition_group))throw Error("Invalid aggregate dimension");
 return FIELDS.map(k=>record[k]);
}
function aggregate(events,policy={}){
 // Disabled by default; no production collection is enabled by this module.
 if(policy.recordingEnabled!==true)return {status:"disabled",counters:[]};
 if(policy.gpc===true||policy.dnt==="1")return {status:"privacy_suppressed",counters:[]};
 if(!Array.isArray(events)||events.length>2000)throw Error("Invalid bounded event batch");
 const buckets=new Map();
 for(const record of events){
  const values=checked(record);
  if(record.event_name==="affiliate_outbound"&&policy.affiliateActivationConfirmed!==true)throw Error("Affiliate outbound cannot be measured before explicit authorization");
  // JSON tuple avoids delimiter injection. No visitor identifiers are accepted.
  const key=JSON.stringify(values);buckets.set(key,(buckets.get(key)||0)+1);
 }
 const counters=[...buckets.entries()].map(([key,count])=>{
  const values=JSON.parse(key),r={};
  FIELDS.forEach((field,i)=>{r[field]=values[i]});
  r.count=count;return r;
 }).sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b)));
 return {status:"ok",counters};
}
function selfTest(){
 const baseline={date_utc:"2026-10-30",page_key:"meditation-attentional-blink",variant:"text",event_name:"content_view",acquisition_group:"organic_search"};
 let results=[];
 const chk=(name,cb)=>{let ok=false;try{ok=!!cb()}catch(e){}results.push({name,pass:ok})};
 const deny=(row)=>{try{aggregate([row],{recordingEnabled:true});return false}catch(e){return true}};
 chk("disabled by default",()=>aggregate([baseline]).status==="disabled");
 chk("happy-path aggregate",()=>aggregate([baseline,baseline],{recordingEnabled:true}).counters[0].count===2);
 chk("exactly five allowed dimensions",()=>Object.keys(aggregate([baseline],{recordingEnabled:true}).counters[0]).length===6);
 chk("GPC fail closed",()=>aggregate([baseline],{recordingEnabled:true,gpc:true}).counters.length===0);
 chk("DNT fail closed",()=>aggregate([baseline],{recordingEnabled:true,dnt:"1"}).status==="privacy_suppressed");
 chk("PII email rejected",()=>deny({...baseline,email:"person@example.com"}));
 chk("IP address rejected",()=>deny({...baseline,ip:"192.0.2.1"}));
 chk("full referrer rejected",()=>deny({...baseline,referrer:"https://social.example/path?a=person"}));
 chk("query string rejected",()=>deny({...baseline,url:"https://example.com/?uid=x"}));
 chk("user agent rejected",()=>deny({...baseline,user_agent:"Mozilla"}));
 chk("cross-visit identifier rejected",()=>deny({...baseline,visitor_id:"abc"}));
 chk("campaign token rejected",()=>deny({...baseline,utm_source:"tiktok"}));
 chk("invalid date rejected",()=>deny({...baseline,date_utc:"2026-13-40"}));
 chk("nonfirstparty page rejected",()=>deny({...baseline,page_key:"https://zen12.com/getstarted"}));
 chk("arbitrary event rejected",()=>deny({...baseline,event_name:"sale_confirmed"}));
 chk("affiliate click blocked pre-approval",()=>deny({...baseline,event_name:"affiliate_outbound"}));
 chk("approved affiliate click still only a click",()=>{let q=aggregate([{...baseline,event_name:"affiliate_outbound"}],{recordingEnabled:true,affiliateActivationConfirmed:true});return q.counters[0].event_name==="affiliate_outbound"&&q.counters[0].count===1});
 chk("no seller URL or commission in counter",()=>{let q=aggregate([baseline],{recordingEnabled:true});return !/https?:|email|cookie|visitor|sale|commission/i.test(JSON.stringify(q))});
 chk("bounded batches",()=>{try{aggregate(Array(2001).fill(baseline),{recordingEnabled:true});return false}catch(e){return true}});
 chk("prototype injection rejected",()=>deny(Object.assign(Object.create({__proto__:null}),baseline)));
 return {total:results.length,passed:results.filter(r=>r.pass).length,failures:results.filter(r=>!r.pass).map(r=>r.name),results};
}
if(typeof module!=="undefined")module.exports={aggregate,selfTest,checked};
if(typeof require==="function"&&require.main===module){const r=selfTest();r.results.forEach(t=>console.log((t.pass?"PASS ":"FAIL ")+t.name));console.log("AGGREGATION "+r.passed+"/"+r.total);if(r.failures.length)process.exitCode=1;}
