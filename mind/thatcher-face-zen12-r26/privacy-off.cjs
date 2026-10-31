'use strict';
/**
 * UNPUBLISHED privacy-OFF prototype. No network hooks, storage, visitor event collection,
 * cookies, identifiers, referrer URLs, email capture, or attribution endpoint.
 * This module cannot turn on analytics; a future release would require a separate reviewed implementation.
 */
const ENABLED = false;
const MIN_CELL = 10;
const ALLOWED_VARIANTS = Object.freeze(['A','B']);
const ALLOWED_ACTIONS = Object.freeze(['guide_view','free_exercise_view','proposed_offer_view']);
function canRecordVisitorEvent() { return false; }
function recordVisitorEvent(_event) { return { accepted:false, reason:'COLLECTION_DISABLED' }; }
function aggregateSyntheticOnly(events) {
  if (!Array.isArray(events)) throw Error('events must be an array');
  const counts=Object.create(null);
  for (const e of events) {
    if (e===null || typeof e!=='object' || Array.isArray(e)) throw Error('invalid synthetic record');
    const keys=Object.keys(e).sort();
    if (keys.join(',') !== 'action,variant') throw Error('unexpected field refused; no IP, URL, referrer, timestamp, cookie, agent, user ID, session or email');
    if (!ALLOWED_VARIANTS.includes(e.variant)||!ALLOWED_ACTIONS.includes(e.action)) throw Error('invalid controlled category');
    const k=e.variant+'/'+e.action;
    counts[k]=(counts[k]||0)+1;
  }
  // Entirely synthetic counts; no individuals and no small cells are revealed.
  return Object.fromEntries(Object.entries(counts).filter(([,v])=>v>=MIN_CELL).map(([k,v])=>[k,v]));
}
if (require.main === module && process.argv.includes('--selftest')) {
  const assert=require('node:assert/strict');
  const checks=[];
  function ok(cond,message){assert.ok(cond,message);checks.push(message)}
  ok(ENABLED===false,'collection disabled');ok(!canRecordVisitorEvent(),'cannot accept visitor events');
  ok(recordVisitorEvent({}).accepted===false,'record refuses visitor event');
  for(const field of ['ip','email','referrer','url','userAgent','cookie','timestamp','id','session','visitorId','utm_source']){
    let threw=false;try{aggregateSyntheticOnly([{variant:'A',action:'guide_view',[field]:'x'}])}catch{threw=true}
    ok(threw,'reject extra field '+field);
  }
  for(const variant of ['A','B'])for(const action of ALLOWED_ACTIONS){
    ok(aggregateSyntheticOnly(Array.from({length:9},()=>({variant,action})))[variant+'/'+action]===undefined,'suppress small '+variant+'/'+action);
    ok(aggregateSyntheticOnly(Array.from({length:10},()=>({variant,action})))[variant+'/'+action]===10,'release synthetic ten '+variant+'/'+action);
  }
  let blocked=false;try{aggregateSyntheticOnly([{variant:'C',action:'guide_view'}])}catch{blocked=true}
  ok(blocked,'reject nonprotocol variant');
  console.log('R26 privacy-OFF synthetic selftest PASS '+checks.length+'/'+checks.length);
}
module.exports={ENABLED,MIN_CELL,canRecordVisitorEvent,recordVisitorEvent,aggregateSyntheticOnly};
