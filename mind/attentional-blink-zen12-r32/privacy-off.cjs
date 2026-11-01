/* R32 synthetic-only analytics design. NEVER INSTALL ON LIVE SITE.
   No DOM hooks, no remote calls, no storage or cookies. Fail closed. */
'use strict';
const ENABLED=false;
const K=10;
const fields=['topic','arm','event','source'];
const allow={
 topic:['attentional_blink','zen12_guide','focus'],
 arm:['A','B','NA'],
 event:['guide_view','film_open','offer_intent','focus_nav'],
 source:['organic','tiktok','internal','other']
};
function valid(row){
 if(row===null||typeof row!=='object'||Array.isArray(row))return false;
 const keys=Object.keys(row);
 if(keys.length!==fields.length)return false;
 for(const f of fields){
  if(!Object.prototype.hasOwnProperty.call(row,f))return false;
  if(typeof row[f]!=='string'||!allow[f].includes(row[f]))return false;
 }
 return true;
}
function summarizeSynthetic(rows){
 if(!Array.isArray(rows)||rows.length>100000)throw Error('synthetic rows only; max 100000');
 const counts=Object.create(null);
 for(const row of rows){
  if(!valid(row))throw Error('unsupported attribute or value');
  const key=fields.map(f=>row[f]).join('|');
  counts[key]=(counts[key]||0)+1;
 }
 return Object.keys(counts).sort().filter(k=>counts[k]>=K).map(k=>{
   const values=k.split('|'); const group={};
   fields.forEach((f,i)=>group[f]=values[i]);
   group.count=counts[k];return group;
 });
}
function send(){throw Error('no runtime instrumentation or collection is authorized');}
function selfTest(){
 const sample={topic:'zen12_guide',arm:'B',event:'film_open',source:'tiktok'};
 const check=[];
 function expect(label,ok){check.push({label,pass:Boolean(ok)});if(!ok)throw Error('failed '+label);}
 expect('analytics off',ENABLED===false);
 expect('valid synthetic schema',valid(sample));
 for(const f of fields){
  const o={...sample};delete o[f];expect('missing '+f+' rejected',!valid(o));
  const o2={...sample,[f]:'not-allowed'};expect('unknown '+f+' rejected',!valid(o2));
 }
 for(const forbidden of ['ip','email','user_id','url','referer','referrer','timestamp','query','utm_source','session','cookie']){
   expect('forbidden '+forbidden+' rejected',!valid({...sample,[forbidden]:'x'}));
 }
 expect('null rejected',!valid(null));expect('array rejected',!valid([]));
 expect('small groups suppressed',summarizeSynthetic(Array(9).fill(sample)).length===0);
 const visible=summarizeSynthetic(Array(10).fill(sample));
 expect('10 reported',visible.length===1&&visible[0].count===10);
 expect('only aggregate keys',Object.keys(visible[0]).sort().join(',')==='arm,count,event,source,topic');
 const split=[...Array(10).fill(sample),...Array(8).fill({...sample,arm:'A'})];
 expect('small second arm suppressed',summarizeSynthetic(split).length===1);
 let bad=false;try{summarizeSynthetic([{...sample,ip:'10.0.0.1'}]);}catch{bad=true;}expect('PII record fails closed',bad);
 bad=false;try{send(sample);}catch{bad=true;}expect('send throws',bad);
 return {passed:check.length,checks:check};
}
module.exports={ENABLED,K,fields,valid,summarizeSynthetic,send,selfTest};
if(require.main===module){const r=selfTest();process.stdout.write(r.passed+' synthetic privacy checks passed; telemetry OFF\n');}
