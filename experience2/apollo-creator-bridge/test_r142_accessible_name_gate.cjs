'use strict';
/** Apollo R142: native Node adversarial accessible-name and raw-text regressions. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {auditStrictReaderContinuity}=require('./r141_dom_custody_gate.cjs');
const {ATLAS,ARTICLE,BOARD}=require('./r140_reader_continuity_gate.cjs');
const open='<a href="'+ARTICLE+'">';
const CTA=open+'Read the full investigation</a>';
function snapshot(markup){
 return {
  atlas:{id:2017,slug:'apollo-1-evidence-atlas',status:'publish',link:ATLAS,content:'<main>'+markup+'<p>'+('Apollo provenance '.repeat(25))+'</p><a href="'+BOARD+'">NASA board</a></main>'},
  article:{id:434,slug:'the-hatch-opened-inward-apollo-1',status:'publish',link:ARTICLE,title:'The Hatch Opened Inward',content:'<main><p>'+('Primary-source context '.repeat(25))+'</p><a href="'+BOARD+'">NASA board</a></main>'}
 };
}
function check(markup){
 const {atlas,article}=snapshot(markup);
 const r=auditStrictReaderContinuity(atlas,article);
 assert.equal(r.release,'STAGING_HOLD');
 assert.equal(r.approved_to_publish,false);
 assert.equal(r.browser,'NOT_TESTED');
 return r;
}
for(const [name,markup] of [
 ['hidden descendant text',open+'<span aria-hidden="true">Read the full investigation</span></a>'],
 ['hidden HTML descendant text',open+'<span hidden>Read the full investigation</span></a>'],
 ['inert descendant text',open+'<span inert>Read the full investigation</span></a>'],
 ['CSS-hidden descendant',open+'<span style="display:none">Read the full investigation</span></a>'],
 ['ARIA aria-label on descendant',open+'<span aria-label="Buy now">Read the full investigation</span></a>'],
 ['ARIA aria-labelledby on descendant',open+'<span aria-labelledby="b">Read the full investigation</span></a>'],
 ['image alt modifies accessible name',open+'<img src="fake.png" alt="Buy now">Read the full investigation</a>'],
 ['image without alt ambiguous',open+'<img src="fake.png">Read the full investigation</a>'],
 ['SVG changes accessible name',open+'<svg role="img" aria-label="Buy"></svg>Read the full investigation</a>'],
 ['nested role alters semantics',open+'<span role="button">Read the full investigation</span></a>'],
 ['anchor role button','<a role="button" href="'+ARTICLE+'">Read the full investigation</a>'],
 ['anchor aria-labelledby','<a aria-labelledby="different" href="'+ARTICLE+'">Read the full investigation</a>'],
 ['textarea fake anchor','<textarea>'+CTA+'</textarea>'],
 ['title fake anchor','<title>'+CTA+'</title>'],
 ['xmp fake anchor','<xmp>'+CTA+'</xmp>'],
 ['select fake anchor','<select><option>'+CTA+'</option></select>'],
 ['closed details link','<details><summary>Information</summary>'+CTA+'</details>'],
 ['unterminated anchor','<section>'+open+'Read the full investigation</section>'],
 ['unterminated HTML comment',CTA+'<!-- open forever'],
 ['stray closing anchor','</a>'+CTA]
]){
 test('R142 rejects '+name,()=>{
   const r=check(markup);
   assert.equal(r.source_gate,'REVIEW_REQUIRED',name);
   assert.equal(r.next_action,null);
 });
}
for(const [name,markup] of [
 ['simple anchor',CTA],
 ['benign span',open+'<span>Read the full investigation</span></a>'],
 ['open details','<details open><summary>More</summary>'+CTA+'</details>'],
 ['aria-label equals visible text','<a aria-label="Read the full investigation" href="'+ARTICLE+'">Read the full investigation</a>']
]){
 test('R142 preserves '+name+' as SOURCE ONLY',()=>{
   const r=check(markup);
   assert.equal(r.source_gate,'SOURCE_LINK_CONTINUITY_ONLY',name);
   assert.equal(r.next_action,ARTICLE);
 });
}
test('R142 conservatively reviews benign hidden ornaments until legacy parser updated',()=>{
 const r=check(open+'<span aria-hidden="true">ornament</span><span>Read the full investigation</span></a>');
 assert.equal(r.source_gate,'REVIEW_REQUIRED');
});
test('R142 determinism: no private fields, sale or license fabrication',()=>{
 const {atlas,article}=snapshot(CTA);
 atlas.customer_email='private@example.com';article.order_id='synthetic-123';
 const a=auditStrictReaderContinuity(atlas,article);
 assert.deepEqual(a,auditStrictReaderContinuity(atlas,article));
 assert.ok(!JSON.stringify(a).includes('private@example.com'));
 assert.ok(!JSON.stringify(a).includes('synthetic-123'));
 assert.equal(a.media_rights,'REVIEW_REQUIRED');
 assert.equal(a.commercial_offer,'NOT_VERIFIED');
 assert.equal(a.attributed_revenue,'NOT_OBSERVED');
});
test('R142 browser-only acceptance remains explicitly unresolved',()=>{
 const r=check(CTA);
 assert.equal(r.axe,'NOT_TESTED');
 assert.equal(r.lcp_cls,'NOT_MEASURED');
});
