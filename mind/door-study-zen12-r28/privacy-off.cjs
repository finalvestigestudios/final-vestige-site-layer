'use strict';
/* Unconnected synthetic first-party attribution data model. DO NOT ENABLE without new founder approval. No network, storage, cookies or browser hooks. */
const ENABLED=false,K=10;
const events=new Set(['guide_view','film_intent','offer_intent','source_open','focus_open']);
const channels=new Set(['short','search','direct','other']);
const variants=new Set(['text','optional_film']);
function validate(v){
 if(v===null||typeof v!=='object'||Array.isArray(v))throw Error('bad input');
 const keys=Object.keys(v);
 if(keys.length!==3||keys.some(x=>!['event','channel','variant'].includes(x)))throw Error('unexpected field');
 if(!events.has(v.event)||!channels.has(v.channel)||!variants.has(v.variant))throw Error('bad category');
 return Object.freeze({event:v.event,channel:v.channel,variant:v.variant});
}
function aggregate(samples){
 const m=new Map();
 for(const s of samples){const v=validate(s),key=[v.event,v.channel,v.variant].join('|');m.set(key,(m.get(key)||0)+1)}
 return [...m].filter(([,count])=>count>=K).map(([key,count])=>({key,count})).sort((a,b)=>a.key.localeCompare(b.key));
}
function record(){throw Error('Live measurement disabled; no tracking endpoint exists')}
function selfTest(){
 const assert=require('assert');let passed=0;const ok=(v)=>{assert.ok(v);passed++};const rej=(v)=>{assert.throws(v);passed++};
 ok(ENABLED===false);ok(K===10);ok(events.size===5);ok(channels.size===4);ok(variants.size===2);
 const good={event:'guide_view',channel:'search',variant:'text'};ok(validate(good).event==='guide_view');
 for(const key of ['email','ip','referrer','url','session','userAgent','utm','click_id','gclid','fbclid','device_id','cookie','timestamp','client_id'])rej(()=>validate({...good,[key]:'identifier'}));
 for(const event of ['purchase','sale','revenue','checkout','conversion','signup','user','visit'])rej(()=>validate({...good,event}));
 for(const channel of ['https://example.org','google.com','social:personal',''])rej(()=>validate({...good,channel}));
 for(const variant of ['B','film-experiment', '', 'control-user'])rej(()=>validate({...good,variant}));
 rej(()=>validate(null));rej(()=>validate([]));rej(()=>validate({}));rej(()=>record(good));
 ok(aggregate(Array(9).fill(good)).length===0);ok(aggregate(Array(10).fill(good))[0].count===10);ok(aggregate([]).length===0);
 return passed;
}
if(typeof require==='function'&&require.main===module&&process.argv.includes('--selftest'))console.log('R28 privacy OFF: '+selfTest()+' synthetic assertions passed, no live collection');
module.exports={ENABLED,K,validate,aggregate,record,selfTest};
