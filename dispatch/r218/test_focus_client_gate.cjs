'use strict';
const assert = require('node:assert/strict');
const G = require('./focus_client_gate.cjs');
let pass=0;
function test(name,fn){try{fn(); pass++; process.stdout.write('PASS '+name+'\n');}catch(e){process.stderr.write('FAIL '+name+' '+e.message+'\n');process.exitCode=1;}}
for(const bad of ['invalid_email','error','blocked_email','opted_out','blocked'])
  test('bad query '+bad,()=>assert.equal(G.liveGiftVisible({subscribeQuery:bad}),false));
for(const any of ['pending','failed','unconfirmed','anything','confirm_later','success'])
  test('unrecognized query '+any+' exposes gift',()=>assert.equal(G.liveGiftVisible({subscribeQuery:any}),true));
test('no query no class',()=>assert.equal(G.liveGiftVisible({}),false));
test('empty query no class',()=>assert.equal(G.liveGiftVisible({subscribeQuery:''}),false));
test('is-subscriber class exposes gift',()=>assert.equal(G.liveGiftVisible({containerClasses:'x is-subscriber y'}),true));
test('hyphen-bounded class text also triggers',()=>assert.equal(G.liveGiftVisible({containerClasses:'not-is-subscriber-x'}),true));
test('bad query plus is-subscriber class exposes gift',()=>assert.equal(G.liveGiftVisible({subscribeQuery:'error',containerClasses:'is-subscriber'}),true));
test('browser gift display never proves confirmation',()=>assert.equal(G.interpretBrowserState({subscribeQuery:'success'}).confirmedSignup,null));
test('browser gift display never emits confirmed_signup',()=>assert.equal(G.interpretBrowserState({subscribeQuery:'success'}).analyticsInstruction,'DO_NOT_EMIT_CONFIRMED_SIGNUP'));
test('missing provider event rejected',()=>assert.equal(G.classifyProviderRecord(null),'INSUFFICIENT_PROVIDER_EVIDENCE'));
test('browser-only record rejected',()=>assert.equal(G.classifyProviderRecord({subscribeQuery:'success'}),'INSUFFICIENT_PROVIDER_EVIDENCE'));
test('unauthenticated record rejected',()=>assert.equal(G.classifyProviderRecord({provider:'jetpack',record_type:'subscription_confirmation',status:'confirmed',provider_event_id:'test-12345678',anonymous_subject_digest:'a'.repeat(64)}),'INSUFFICIENT_PROVIDER_EVIDENCE'));
const fixture={provider:'jetpack',record_type:'subscription_confirmation',status:'confirmed',provider_event_id:'event-fixture-123',anonymous_subject_digest:'a'.repeat(64),source_verified:true};
test('shape alone cannot prove authority',()=>assert.equal(G.classifyProviderRecord(fixture),'STRUCTURALLY_ELIGIBLE_AWAIT_AUTHENTICATED_PROVENANCE'));
test('duplicate same id counted once structurally',()=>assert.deepEqual(G.dedupeConfirmedEvents([fixture,fixture]),{structurallyEligible:1,duplicates:1,rejected:0,confirmedLeads:null,reason:'Connector authenticity and recipient email eligibility not established.'}));
test('unconfirmed rejected in structural summary',()=>assert.equal(G.dedupeConfirmedEvents([{...fixture,status:'pending'}]).rejected,1));
test('no fabricated total for absent records',()=>assert.equal(G.dedupeConfirmedEvents([]).confirmedLeads,null));
test('zero sending permission',()=>assert.equal(G.releaseStatus().authorizedToSend,false));
test('4:2 restrictions preserved',()=>assert.equal(G.releaseStatus().commercial03And05,'HOLD_MERCHANT'));
console.log(pass+' native Node assertions passed'); if(process.exitCode)process.exit(process.exitCode);
