"use strict";
/*
 * R21 anonymous aggregate measurement design PROTOTYPE, entirely OFF.
 * Not imported by either WordPress draft. No network calls, localStorage,
 * session identifiers, cookies, IP, user-agent, referrer string, URLs,
 * or personalized attribution. No data persists from this module.
 *
 * Future operators must separately approve a first-party endpoint,
 * secure storage aggregation/log redaction, bot safeguards, data retention,
 * notice review, affiliate rights, accessibility and performance before
 * setting FEATURE_ENABLED to true in any integrated release.
 */
const FEATURE_ENABLED = false;
const SOURCES = Object.freeze(["direct","organic_search","tiktok","internal","other"]);
const VARIANTS = Object.freeze(["A","B"]);
const EVENTS = Object.freeze(["presentation","offer_outbound"]);
const TOPICS = Object.freeze(["attentional_blink"]);
function emptyAggregate(){
 const out={};
 for(const variant of VARIANTS){out[variant]={};for(const source of SOURCES){out[variant][source]={presentation:0,offer_outbound:0};}}
 return out;
}
function validEvent(e){
 if(!e||typeof e!=="object"||Array.isArray(e))return false;
 if(Object.keys(e).sort().join(",")!=="event,source,topic,variant")return false;
 return EVENTS.includes(e.event)&&SOURCES.includes(e.source)&&TOPICS.includes(e.topic)&&VARIANTS.includes(e.variant);
}
function acceptAggregate(aggregate,e,enabled=FEATURE_ENABLED){
 if(!enabled)return {accepted:false,reason:"measurement disabled",aggregate};
 if(!validEvent(e))return {accepted:false,reason:"invalid minimized schema",aggregate};
 // This pure mock only counts coarse totals. Production needs independent security/privacy review.
 const copy=JSON.parse(JSON.stringify(aggregate));
 if(!copy[e.variant]?.[e.source]||!Number.isSafeInteger(copy[e.variant][e.source][e.event]))return {accepted:false,reason:"invalid aggregate",aggregate};
 copy[e.variant][e.source][e.event]++;
 return {accepted:true,reason:"coarse aggregate only",aggregate:copy};
}
function summarize(aggregate){
 const out={};
 for(const variant of VARIANTS){
  const exposure=SOURCES.reduce((n,s)=>n+aggregate[variant][s].presentation,0);
  const clicks=SOURCES.reduce((n,s)=>n+aggregate[variant][s].offer_outbound,0);
  out[variant]={presentations:exposure,outbound_clicks:clicks,ratio:exposure>0?clicks/exposure:null};
 }
 return out;
}
function tests(){
 const checks=[];
 const test=(name,pass)=>checks.push({name,pass:!!pass});
 const e={event:"presentation",source:"organic_search",topic:"attentional_blink",variant:"A"};
 const starting=emptyAggregate();
 const off=acceptAggregate(starting,e);
 test("feature defaults disabled",FEATURE_ENABLED===false);
 test("no count when disabled",!off.accepted&&JSON.stringify(off.aggregate)===JSON.stringify(starting));
 test("valid minimized schema",validEvent(e));
 test("mock gated test increments only approved aggregate",acceptAggregate(starting,e,true).aggregate.A.organic_search.presentation===1);
 test("input does not modify original aggregate",starting.A.organic_search.presentation===0);
 test("source whitelist",SOURCES.length===5);
 test("event whitelist",EVENTS.length===2);
 test("variant whitelist",VARIANTS.length===2);
 test("extra visitor ID rejected",!validEvent({...e,user_id:"person123"}));
 test("extra timestamp rejected",!validEvent({...e,timestamp:"2026-10-31"}));
 test("extra URL rejected",!validEvent({...e,url:"https://example.com/?email=person"}));
 test("extra referrer rejected",!validEvent({...e,referrer:"https://example.com/?query=secret"}));
 test("extra IP rejected",!validEvent({...e,ip:"127.0.0.1"}));
 test("email value rejected",!validEvent({...e,source:"x@y.test"}));
 test("raw source URL rejected",!validEvent({...e,source:"https://tiktok.com/@xyz?src=123"}));
 test("arbitrary topic rejected",!validEvent({...e,topic:"unique-search-phrase"}));
 test("arbitrary variant rejected",!validEvent({...e,variant:"C"}));
 test("commercial sale event rejected",!validEvent({...e,event:"sale"}));
 test("anonymous outbound allowed only in mock enabled mode",acceptAggregate(starting,{...e,event:"offer_outbound"},true).aggregate.A.organic_search.offer_outbound===1);
 test("zero sample yields null rate",summarize(starting).A.ratio===null);
 const t=acceptAggregate(starting,e,true).aggregate;
 const o=acceptAggregate(t,{...e,event:"offer_outbound"},true).aggregate;
 test("ratio is outbound per presentation, not unique CTR",summarize(o).A.ratio===1);
 test("zero denominator cannot divide",summarize(o).B.ratio===null);
 test("no storage API or fetch in prototype",!/(?:fetch\s*\(|localStorage|sendBeacon\s*\(|document\.cookie)/.test(acceptAggregate.toString()+summarize.toString()));
 return checks;
}
if(typeof module!=="undefined")module.exports={FEATURE_ENABLED,SOURCES,VARIANTS,EVENTS,emptyAggregate,validEvent,acceptAggregate,summarize,tests};
if(typeof require!=="undefined"&&require.main===module){
 const r=tests();console.log(JSON.stringify({pass:r.filter(x=>x.pass).length,total:r.length,failures:r.filter(x=>!x.pass)},null,2));if(r.some(x=>!x.pass))process.exitCode=1;
}
