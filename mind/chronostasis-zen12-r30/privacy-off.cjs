"use strict";
// A PROPOSAL ONLY. There is no production handler, endpoint, storage or network.
const ENABLED=false;
const ALLOWED={
  variant:new Set(["A","B"]),
  event:new Set(["guide_view","source_open","practice_open","approved_cta_click"]),
  topic:new Set(["zen12","chronostasis"])
};
const THRESHOLD=10;
function normalize(event){
  if(!ENABLED)return null;
  if(!event || Object.prototype.toString.call(event)!=="[object Object]")return null;
  const keys=Object.keys(event).sort();
  if(keys.length!==3||keys.join("|")!=="event|topic|variant")return null;
  for(const k of keys){if(typeof event[k]!=="string" || !ALLOWED[k].has(event[k]))return null;}
  return {variant:event.variant,event:event.event,topic:event.topic};
}
function aggregateSyntheticOnly(rows,k=THRESHOLD){
  // This only accepts manually supplied synthetic normalized categories; NEVER raw HTTP data.
  if(k<10)throw Error("minimum k=10 required");
  const map=new Map();
  for(const row of rows){
    if(row===null || Object.keys(row).sort().join("|")!=="event|topic|variant")continue;
    if(!ALLOWED.variant.has(row.variant)||!ALLOWED.event.has(row.event)||!ALLOWED.topic.has(row.topic))continue;
    const key=[row.variant,row.event,row.topic].join("/");
    map.set(key,(map.get(key)||0)+1);
  }
  return [...map].filter(([_,n])=>n>=k).map(([category,count])=>({category,count})).sort((a,b)=>a.category.localeCompare(b.category));
}
function selfTest(){
  let n=0;
  function ok(cond,why){n++;if(!cond)throw Error("privacy assertion "+n+" "+why);}
  ok(ENABLED===false,"must be off");
  ok(THRESHOLD>=10,"no small cells");
  const good={variant:"A",event:"guide_view",topic:"zen12"};
  ok(normalize(good)===null,"production off");
  const badKeys=["email","ip","referrer","url","userAgent","fingerprint","cookie","localStorage","session","orderId","utm_source","query","clickId","timestamp","purchase","price","location","userId","name"];
  for(const key of badKeys)ok(normalize({...good,[key]:"example"})===null,"reject "+key);
  ok(normalize({variant:"A",event:"guide_view"})===null,"reject incomplete");
  ok(normalize(null)===null,"reject null");
  ok(normalize("foo")===null,"reject scalar");
  ok(normalize({variant:"A",event:"guide_view",topic:"zen12",extra:"x"})===null,"reject extra");
  ok(aggregateSyntheticOnly(Array(9).fill(good)).length===0,"9 suppressed");
  const ten=aggregateSyntheticOnly(Array(10).fill(good));
  ok(ten.length===1&&ten[0].count===10,"10 visible");
  ok(aggregateSyntheticOnly(Array(11).fill(good),11)[0].count===11,"threshold can tighten");
  try{aggregateSyntheticOnly(Array(15).fill(good),9);throw Error("bad threshold accepted");}catch(e){ok(/minimum/.test(e.message),"below 10 rejected");}
  const mixed=aggregateSyntheticOnly([...Array(12).fill(good),...Array(2).fill({variant:"B",event:"source_open",topic:"chronostasis"})]);
  ok(mixed.length===1 && mixed[0].category==="A/guide_view/zen12","suppress small group");
  ok(!JSON.stringify(mixed).includes("referrer"),"no raw referrer");
  ok(!/fetch\(|XMLHttpRequest|sendBeacon|document\.cookie|localStorage|sessionStorage/.test(String(normalize)+String(aggregateSyntheticOnly)),"no browser collection");
  return {passed:n,enabled:ENABLED,threshold:THRESHOLD};
}
module.exports={ENABLED,ALLOWED,THRESHOLD,normalize,aggregateSyntheticOnly,selfTest};
if(typeof require!=="undefined"&&require.main===module){console.log(JSON.stringify(selfTest()));}
