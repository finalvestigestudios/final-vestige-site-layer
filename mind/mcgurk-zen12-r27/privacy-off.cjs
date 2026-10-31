'use strict';
/*
 * OFF-BY-DEFAULT aggregate-only attribution research fixture.
 * No live endpoint, cookie, local storage, request handler or merchant URL.
 * Synthetic inputs ONLY; no user/session identifiers, raw referrer or timestamps.
 */
const ENABLED = false;
const allowed = Object.freeze({
  event: new Set(['guide_view', 'video_intent', 'offer_gate_view']),
  source: new Set(['organic', 'tiktok', 'internal', 'direct', 'other']),
  topic: new Set(['perception', 'suggestion', 'focus', 'other']),
  variant: new Set(['text', 'video']),
  product: new Set(['zen12']),
});
function normalizeSynthetic(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) throw new Error('invalid shape');
  const keys = Object.keys(input);
  if (keys.length !== Object.keys(allowed).length ||
      keys.some(k => !(k in allowed))) throw new Error('unknown or missing field');
  const out = {};
  for (const [k, options] of Object.entries(allowed)) {
    if (typeof input[k] !== 'string' || !options.has(input[k])) throw new Error('non-categorical value');
    out[k] = input[k];
  }
  return Object.freeze(out);
}
function aggregateSynthetic(rows, threshold=10) {
  if (!Array.isArray(rows) || !Number.isInteger(threshold) || threshold < 10) throw new Error('invalid aggregation');
  const counts = new Map();
  for (const raw of rows) {
    const item=normalizeSynthetic(raw);
    const key=[item.event,item.source,item.topic,item.variant,item.product].join('|');
    counts.set(key,(counts.get(key)||0)+1);
  }
  return Array.from(counts.entries()).filter(([,n])=>n>=threshold)
    .map(([key,count])=>Object.freeze({event:key.split('|')[0], source:key.split('|')[1],topic:key.split('|')[2],variant:key.split('|')[3],product:key.split('|')[4],count}))
    .sort((a,b)=>b.count-a.count||a.source.localeCompare(b.source));
}
function makeFixture(overrides={}) {
  return Object.assign({event:'offer_gate_view',source:'organic',topic:'focus',variant:'text',product:'zen12'},overrides);
}
function selfTest() {
  let passed=0; const check=(c,m)=>{if(!c)throw new Error('privacy test: '+m);passed++;};
  const reject=(v)=>{try{normalizeSynthetic(v);return false}catch{return true}};
  check(ENABLED===false,'disabled');
  check(reject({}), 'empty object rejected');
  check(reject(null),'null rejected');
  check(reject([]),'arrays rejected');
  check(reject(makeFixture({ip:'127.0.0.1'})),'IP rejected');
  check(reject(makeFixture({email:'a@b.c'})),'email rejected');
  check(reject(makeFixture({user_id:'123'})),'user id rejected');
  check(reject(makeFixture({session_id:'x'})),'session id rejected');
  check(reject(makeFixture({utm_campaign:'x'})),'raw campaign rejected');
  check(reject(makeFixture({referrer:'https://example.com/?q=x'})),'raw referrer rejected');
  check(reject(makeFixture({timestamp:'2026-10-31'})),'time rejected');
  check(reject(makeFixture({cookie:'x'})),'cookies rejected');
  check(reject(makeFixture({amount:100})),'amount rejected');
  check(reject(makeFixture({source:'https://tiktok.com/'})),'full URLs rejected');
  check(reject(makeFixture({source:'other?x=1'})),'query strings rejected');
  check(reject(makeFixture({product:'hypnosis_live'})),'unreviewed product rejected');
  check(reject(makeFixture({event:'purchase'})),'purchase attribution rejected');
  check(reject(makeFixture({variant:'A'})),'non-canonical variant rejected');
  check(reject(makeFixture({topic:'123'})),'topic rejected');
  check(reject(makeFixture({source:42})),'numeric source rejected');
  check(reject(makeFixture({product:null})),'null category rejected');
  check(Object.isFrozen(normalizeSynthetic(makeFixture())),'normalized record immutable');
  check(aggregateSynthetic(Array.from({length:9},()=>makeFixture())).length===0,'small cells suppressed');
  check(aggregateSynthetic(Array.from({length:10},()=>makeFixture())).length===1,'threshold 10');
  check(aggregateSynthetic(Array.from({length:10},()=>makeFixture()))[0].count===10,'count correct');
  check(aggregateSynthetic([...Array.from({length:10},()=>makeFixture()),makeFixture({source:'direct'})]).length===1,'rare cells dropped');
  check(aggregateSynthetic([]).length===0,'empty aggregate');
  let bad=false;try{aggregateSynthetic([makeFixture()],9)}catch{bad=true}check(bad,'threshold cannot drop below 10');
  bad=false;try{aggregateSynthetic([makeFixture(),makeFixture({email:'bad'})])}catch{bad=true}check(bad,'invalid row rejects entire batch');
  check(!('referrer' in aggregateSynthetic(Array.from({length:10},()=>makeFixture()))[0]),'no raw referrer output');
  check(!('id' in aggregateSynthetic(Array.from({length:10},()=>makeFixture()))[0]),'no visitor id output');
  return passed;
}
if (typeof require!=='undefined' && require.main===module && process.argv.includes('--selftest')) {
  console.log('Privacy OFF selftest: '+selfTest()+' passed.');
}
module.exports={ENABLED,normalizeSynthetic,aggregateSynthetic,makeFixture,selfTest};
