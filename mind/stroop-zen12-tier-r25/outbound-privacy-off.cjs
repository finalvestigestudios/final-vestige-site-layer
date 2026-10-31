'use strict';
// NO AUTOMATIC NETWORKING. This file demonstrates a disabled, privacy-limited reporting model.
// No cookie, session id, raw referrer, email, IP, fingerprint, querystring, or unique client token.
const ENABLED=false;
const allowedSources=new Set(['tiktok','organic','direct','internal','other']);
const allowedTopics=new Set(['stroop','zen12','puys','focus','other']);
const allowedActions=new Set(['guide_view','cta_view','outbound_intent']);
const allowedVariants=new Set(['text','video']);
function validate(obj){
 if(ENABLED)return false; // activation requires a separate implementation and approval.
 if(!obj||typeof obj!=='object'||Array.isArray(obj))return false;
 const keys=Object.keys(obj).sort().join(',');
 if(keys!=='action,source,topic,variant,week')return false;
 if(!allowedSources.has(obj.source)||!allowedTopics.has(obj.topic)||!allowedActions.has(obj.action)||!allowedVariants.has(obj.variant))return false;
 return /^20[2-9][0-9]-W(0[1-9]|[1-4][0-9]|5[0-3])$/.test(obj.week);
}
function summarize(rows){
 const totals=new Map();
 for(const row of rows){if(!validate(row))return {status:'INVALID_ROW',groups:[]};
 const k=[row.week,row.source,row.topic,row.variant,row.action].join('|');
 totals.set(k,(totals.get(k)||0)+1);}
 return {status:'OFFLINE_ONLY',groups:[...totals].filter(([_,n])=>n>=10).map(([key,count])=>({key,count}))};
}
function selftest(){
 let pass=0;const ok=(x,m)=>{if(!x)throw Error(m);pass++};
 const good={week:'2026-W44',source:'organic',topic:'zen12',variant:'text',action:'guide_view'};
 ok(validate(good),'valid coarse row');
 for(const forbidden of ['email','ip','referrer','cookie','session','click_id','utm_source','href','url','timestamp','device','language','userAgent','query','subscriber','order'])ok(!validate({...good,[forbidden]:'secret'}),'reject '+forbidden);
 ok(!validate({...good,source:'linkedin'}),'source enumeration');
 ok(!validate({...good,topic:'medical'}),'topic enumeration');
 ok(!validate({...good,variant:'experiment3'}),'variant enumeration');
 ok(!validate({...good,action:'purchase'}),'sales inference');
 ok(!validate({...good,week:'2026-10-31T11:00:00'}),'no exact time');
 ok(!validate({...good,week:'2026-W88'}),'no invalid week');
 ok(!validate(null),'null invalid');
 ok(!validate([]),'array invalid');
 ok(summarize(Array(9).fill(good)).groups.length===0,'suppress nine');
 ok(summarize(Array(10).fill(good)).groups.length===1,'allow 10 aggregated offline');
 ok(summarize([good,{...good,email:'x'}]).status==='INVALID_ROW','fail closed on invalid row');
 ok(ENABLED===false,'feature flag off');
 return pass;
}
if(require.main===module&&process.argv.includes('--selftest'))console.log('PASS',selftest());
module.exports={ENABLED,validate,summarize,selftest};
