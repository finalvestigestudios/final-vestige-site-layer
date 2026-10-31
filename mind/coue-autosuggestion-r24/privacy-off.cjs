'use strict';
// Offline synthetic model ONLY; never imported by pages, no network, storage or cookies.
function valid(r){
 if(!r||typeof r!=='object'||Array.isArray(r))return false;
 const keys=Object.keys(r);if(keys.length!==4||keys.some(k=>!['week','variant','channel','event'].includes(k)))return false;
 return /^20\d\d-W(?:0[1-9]|[1-4]\d|5[0-3])$/.test(r.week)&&['A','B'].includes(r.variant)&&['organic','tiktok','direct','other'].includes(r.channel)&&['guide_view','outbound_intent'].includes(r.event);
}
function aggregate(rows,threshold=10){
 if(!Number.isInteger(threshold)||threshold<10)throw Error('threshold must be at least 10');
 const groups=new Map();
 for(const row of rows){if(!valid(row))throw Error('reject unknown/PII event');const k=[row.week,row.variant,row.channel,row.event].join('|');groups.set(k,(groups.get(k)||0)+1)}
 return [...groups].filter(([,n])=>n>=threshold).sort().map(([group,count])=>({group,count}));
}
function selftest(){
 let count=0;const check=c=>{if(!c)throw Error('privacy check failed: '+count);count++};
 const good={week:'2026-W44',variant:'A',channel:'organic',event:'guide_view'};check(valid(good));
 for(const bad of [null,[],{}, {...good,email:'x'},{...good,ip:'x'},{...good,utm:'x'},{...good,referrer:'x'},{...good,visitor:'x'},{...good,session:'x'},{...good,cookie:'x'},{...good,week:'2026-10-31'},{...good,week:'2026-W92'},{...good,variant:'Z'},{...good,channel:'foo'},{...good,event:'sale'}])check(!valid(bad));
 check(aggregate(Array(9).fill(good)).length===0);check(aggregate(Array(10).fill(good)).length===1);check(aggregate(Array(10).fill(good))[0].count===10);check(aggregate([]).length===0);
 try{aggregate([{...good,email:'x'}]);throw Error('bad')}catch(e){check(e.message==='reject unknown/PII event')}
 try{aggregate([],1);throw Error('bad')}catch(e){check(e.message==='threshold must be at least 10')}
 return count;
}
module.exports={valid,aggregate,selftest};
if(require.main===module&&process.argv.includes('--selftest'))console.log(selftest()+' synthetic privacy tests passed; no collection or network');