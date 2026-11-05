'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {auditStrictReaderContinuity}=require('./r141_dom_custody_gate.cjs');
const {ATLAS,ARTICLE,BOARD}=require('./r140_reader_continuity_gate.cjs');
const CTA='<a href="'+ARTICLE+'">Read the full investigation</a>';
const fixture=()=>({
 atlas:{id:2017,slug:'apollo-1-evidence-atlas',status:'publish',link:ATLAS,content:'<main>'+CTA+'<p>'+('Apollo provenance '.repeat(25))+'</p><a href="'+BOARD+'">NASA board</a></main>'},
 article:{id:434,slug:'the-hatch-opened-inward-apollo-1',status:'publish',link:ARTICLE,title:'The Hatch Opened Inward',content:'<main><p>'+('Primary-source context '.repeat(25))+'</p><a href="'+BOARD+'">Board</a></main>'}
});
function run(markup){const f=fixture();f.atlas.content=f.atlas.content.replace(CTA,markup);return auditStrictReaderContinuity(f.atlas,f.article)}
test('verified static CTA is SOURCE ONLY; no release',()=>{const f=fixture(),r=auditStrictReaderContinuity(f.atlas,f.article);assert.equal(r.source_gate,'SOURCE_LINK_CONTINUITY_ONLY');assert.equal(r.release,'STAGING_HOLD');assert.equal(r.browser,'NOT_TESTED')});
test('nested visible span remains accessible',()=>assert.equal(run('<a href="'+ARTICLE+'"><span>Read the full investigation</span></a>').source_gate,'SOURCE_LINK_CONTINUITY_ONLY'));
const cases=[
 ['hidden parent','<section hidden>'+CTA+'</section>'],
 ['inert parent','<div inert>'+CTA+'</div>'],
 ['aria hidden parent','<div aria-hidden="true">'+CTA+'</div>'],
 ['display none parent','<div style="display:none">'+CTA+'</div>'],
 ['visibility hidden parent','<div style="visibility:hidden">'+CTA+'</div>'],
 ['hidden element','<a hidden href="'+ARTICLE+'">Read the full investigation</a>'],
 ['positive tabindex','<a tabindex="1" href="'+ARTICLE+'">Read the full investigation</a>'],
 ['negative tabindex','<a tabindex="-1" href="'+ARTICLE+'">Read the full investigation</a>'],
 ['new tab','<a target="_blank" href="'+ARTICLE+'">Read the full investigation</a>'],
 ['download','<a download href="'+ARTICLE+'">Read the full investigation</a>'],
 ['ARIA label disguises visible wording','<a aria-label="Read the full investigation" href="'+ARTICLE+'">Buy now</a>'],
 ['comment only','<!-- '+CTA+' -->'],
 ['template only','<template>'+CTA+'</template>'],
 ['script only','<script>const x='+JSON.stringify(CTA)+'</script>'],
 ['noscript only','<noscript>'+CTA+'</noscript>'],
 ['wrong destination','<a href="https://finalvestige.com.evil.example/">Read the full investigation</a>'],
 ['double CTA',CTA+CTA],
 ['nested anchors','<a href="'+ARTICLE+'"><a href="'+ARTICLE+'">Read the full investigation</a></a>']
];
for(const [name,html] of cases)test('rejects '+name,()=>{const r=run(html);assert.equal(r.source_gate,'REVIEW_REQUIRED');assert.equal(r.next_action,null);assert.equal(r.release,'STAGING_HOLD')});
test('buyer email and fabricated clearance are never reported',()=>{const f=fixture();f.atlas.buyer_email='sensitive@example.com';const r=auditStrictReaderContinuity(f.atlas,f.article,{rights:true,paid:true});assert.equal(r.approved_to_publish,false);assert.equal(r.attributed_revenue,'NOT_OBSERVED');assert.ok(!JSON.stringify(r).includes('sensitive@example.com'))});
test('identical sources produce identical hashes and receipts',()=>{const f=fixture();assert.deepEqual(auditStrictReaderContinuity(f.atlas,f.article),auditStrictReaderContinuity(f.atlas,f.article))});
