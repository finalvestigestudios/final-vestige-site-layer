'use strict';
/* FV Mind R29 — DISABLED, local synthetic privacy model. DO NOT WIRE INTO WORDPRESS.
   No browser listener, network call, cookies, localStorage, fingerprint, IP/referrer/URL. */
const ENABLED = false;
const FIELDS = ['event','variant','source','topic','week'];
const EVENT = ['page_view','outbound_click','focus_interest'];
const VARIANT = ['text','film'];
const SOURCE = ['search','tiktok','direct','other'];
const TOPIC = ['zen12','gorilla','mind'];
function normalizeSynthetic(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) return null;
  const keys=Object.keys(input);
  if (keys.length !== FIELDS.length || keys.some(k=>!FIELDS.includes(k))) return null;
  if (!EVENT.includes(input.event) || !VARIANT.includes(input.variant) ||
      !SOURCE.includes(input.source) || !TOPIC.includes(input.topic)) return null;
  if (typeof input.week!=='string' || !/^20\d{2}-W(0[1-9]|[1-4]\d|5[0-3])$/.test(input.week)) return null;
  return {event:input.event,variant:input.variant,source:input.source,topic:input.topic,week:input.week};
}
function collect() { return null; } // fail-closed even if called with valid synthetic payload
function aggregateSynthetic(events) {
  if (!Array.isArray(events)) return [];
  const bins=new Map();
  for(const e of events) {
    const x=normalizeSynthetic(e);if (!x) continue;
    const k=FIELDS.map(f=>x[f]).join('|');bins.set(k,(bins.get(k)||0)+1);
  }
  return [...bins.entries()].filter(([,count])=>count>=10).map(([key,count])=>({key,count})).sort((a,b)=>a.key.localeCompare(b.key));
}
function selfTest(){
 let count=0;const ok=(b,m)=>{count++;if(!b)throw Error('Privacy test '+count+': '+m)};
 const sample={event:'page_view',variant:'text',source:'search',topic:'zen12',week:'2026-W44'};
 ok(ENABLED===false,'flag stays off');ok(collect(sample)===null,'no collection');ok(normalizeSynthetic(sample)!==null,'valid synthetic input');ok(normalizeSynthetic({...sample,ip:'1.2.3.4'})===null,'reject IP');ok(normalizeSynthetic({...sample,referrer:'https://example.com?q=name'})===null,'reject referrer');ok(normalizeSynthetic({...sample,email:'test@example.com'})===null,'reject email');ok(normalizeSynthetic({...sample,utm:'raw'})===null,'reject raw UTM');ok(normalizeSynthetic({...sample,identifier:'id'})===null,'reject identifier');ok(normalizeSynthetic({...sample,userAgent:'ua'})===null,'reject UA');ok(normalizeSynthetic({...sample,url:'/mind/?token=x'})===null,'reject path');ok(normalizeSynthetic({...sample,cookie:'x'})===null,'reject cookie');ok(normalizeSynthetic({...sample,session:'uuid'})===null,'reject session');ok(normalizeSynthetic({...sample,device:'mobile'})===null,'reject device');ok(normalizeSynthetic({...sample,fullTimestamp:'2026-10-31T00:00:01Z'})===null,'reject exact time');ok(normalizeSynthetic({...sample,event:'purchase'})===null,'reject purchases');ok(normalizeSynthetic({...sample,variant:'b'})===null,'reject variant');ok(normalizeSynthetic({...sample,source:'reddit.com/u/name'})===null,'reject unknown source');ok(normalizeSynthetic({...sample,topic:'anxiety'})===null,'reject health categories');ok(normalizeSynthetic({...sample,week:'2026-10-31'})===null,'reject day precision');ok(normalizeSynthetic({...sample,week:'2026-W00'})===null,'reject week zero');ok(normalizeSynthetic({...sample,week:'2026-W54'})===null,'reject week >53');ok(normalizeSynthetic([])===null,'reject array');ok(normalizeSynthetic(null)===null,'reject null');ok(normalizeSynthetic('x')===null,'reject string');ok(normalizeSynthetic({})===null,'reject empty');ok(aggregateSynthetic(Array(9).fill(sample)).length===0,'small cell suppressed');ok(aggregateSynthetic(Array(10).fill(sample)).length===1,'threshold cell shown');ok(aggregateSynthetic(Array(11).fill(sample))[0].count===11,'count');ok(aggregateSynthetic([sample,...Array(9).fill(null)]).length===0,'drop invalid');ok(aggregateSynthetic(Array(10).fill({...sample,source:'tiktok'}))[0].key.includes('tiktok'),'coarse source');ok(aggregateSynthetic(Array(12).fill({...sample,variant:'film'}))[0].key.includes('film'),'variant');ok(aggregateSynthetic(null).length===0,'not-array');ok(aggregateSynthetic([{}]).length===0,'invalid only');ok(JSON.stringify(aggregateSynthetic(Array(10).fill(sample))).indexOf('email')===-1,'outputs no PII');return count;
}
if (typeof module !== 'undefined') module.exports={ENABLED,FIELDS,normalizeSynthetic,collect,aggregateSynthetic,selfTest};
if (typeof require !== 'undefined' && typeof module !== 'undefined' && require.main===module){console.log('FV Mind privacy OFF self-tests: '+selfTest()+' passed; enabled='+ENABLED)}
