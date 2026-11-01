'use strict';
/* FV Mind R34 — NO COLLECTION. Pure, offline synthetic attribution model.
 * This file is intentionally non-wired. It does NOT read URL, headers,
 * document, navigator, cookies, storage or network, and never sends data.
 */
const ENABLED = false;
const K_MIN = 10;
const KEYS = Object.freeze(['source', 'variant', 'event']);
const SOURCES = Object.freeze(['organic', 'tiktok', 'internal', 'direct', 'other']);
const VARIANTS = Object.freeze(['A', 'B']);
const EVENTS = Object.freeze(['guide_view', 'completed_guide', 'approved_outbound_intent']);
function cleanSynthetic(candidate) {
  if (!candidate || typeof candidate !== 'object' || Array.isArray(candidate)) return null;
  const keys = Object.keys(candidate);
  if (keys.length !== KEYS.length || keys.some(k => !KEYS.includes(k))) return null;
  if (!SOURCES.includes(candidate.source) || !VARIANTS.includes(candidate.variant) ||
      !EVENTS.includes(candidate.event)) return null;
  return {source:candidate.source, variant:candidate.variant, event:candidate.event};
}
function collect(/* event */) { return {accepted:false,reason:'HARD_DISABLED_PENDING_APPROVAL'}; }
function syntheticAggregate(fixtures) {
  if (!Array.isArray(fixtures) || fixtures.length>100000) throw new TypeError('synthetic fixtures only, <=100000');
  const counts = Object.create(null);
  for (const item of fixtures) {
    const v=cleanSynthetic(item);
    if(!v) throw new TypeError('invalid fixture; no identifiers or unknown fields');
    const key=[v.source,v.variant,v.event].join('|');
    counts[key]=(counts[key]||0)+1;
  }
  return Object.fromEntries(Object.entries(counts).filter(([,n])=>n>=K_MIN).sort());
}
function selfTest() {
  let passed=0; function ok(c,msg){if(!c)throw new Error(msg);passed++;}
  ok(ENABLED===false,'disabled');
  ok(collect({source:'organic',variant:'A',event:'guide_view'}).accepted===false,'collect refuses');
  ok(cleanSynthetic(null)===null,'null');
  ok(cleanSynthetic('text')===null,'string');
  ok(cleanSynthetic([])===null,'array');
  ok(cleanSynthetic({})===null,'empty');
  ok(cleanSynthetic({source:'organic',variant:'A',event:'guide_view'}).source==='organic','good');
  for(const f of ['email','userId','ip','referrer','url','cookie','session','fingerprint','utm','timestamp','purchase','name','phone']){
    ok(cleanSynthetic({source:'organic',variant:'A',event:'guide_view',[f]:'x'})===null,'reject extra '+f);
  }
  for(const f of ['organic','tiktok','internal','direct','other'])ok(cleanSynthetic({source:f,variant:'B',event:'guide_view'})!==null,'source '+f);
  for(const f of ['A','B'])ok(cleanSynthetic({source:'organic',variant:f,event:'guide_view'})!==null,'variant '+f);
  for(const f of ['guide_view','completed_guide','approved_outbound_intent'])ok(cleanSynthetic({source:'organic',variant:'A',event:f})!==null,'event '+f);
  for(const f of ['bad','https://social.example/x?id=1','127.0.0.1',''])ok(cleanSynthetic({source:f,variant:'A',event:'guide_view'})===null,'invalid source '+f);
  const example={source:'organic',variant:'A',event:'guide_view'};
  for(const n of [0,1,5,9])ok(Object.keys(syntheticAggregate(Array(n).fill(example))).length===0,'suppress '+n);
  for(const n of [10,11,12])ok(syntheticAggregate(Array(n).fill(example))['organic|A|guide_view']===n,'include '+n);
  ok(Object.keys(syntheticAggregate([...Array(10).fill(example),...Array(9).fill({source:'tiktok',variant:'B',event:'guide_view'})])).length===1,'separate cells');
  let rejected=false;try{syntheticAggregate([{source:'organic',variant:'A',event:'guide_view',email:'test@example.org'}]);}catch(e){rejected=true;}ok(rejected,'PII fails closed');
  return {passed,enabled:ENABLED,k:K_MIN};
}
if(typeof module!=='undefined')module.exports={ENABLED,K_MIN,cleanSynthetic,collect,syntheticAggregate,selfTest};
if(typeof require!=='undefined' && typeof module!=='undefined' && require.main===module) console.log(JSON.stringify(selfTest()));
