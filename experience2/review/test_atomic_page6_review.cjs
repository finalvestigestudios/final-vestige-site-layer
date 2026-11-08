'use strict';
/* Run: node --test experience2/review/test_atomic_page6_review.cjs
   Synthetic source only; integration requires authenticated public-page exports. */
const test=require('node:test');
const assert=require('node:assert/strict');
const {assemble,REPLACEMENTS,CHAPTERS,PIN}=require('./atomic_page6_review.cjs');
const safe={hashFn:()=>PIN};
function home(){return {
  id:6,status:'publish',modified:'2026-11-05T12:07:24',
  content:'<span class="fv-margin-strip__item"></span>'.repeat(72)+
    REPLACEMENTS.map(x=>x[1]).join('\n')+
    CHAPTERS.map(x=>'<a href="#fv-hf-'+x+'">link</a><div id="fv-hf-'+x+'"></div>').join('')+
    '<!-- wp:jetpack/subscriptions -->'+'<img src="test">'.repeat(4)+
    'href="/focus/"'.repeat(4)+
    's67-19766.webp Franklinexpeditionnote.jpg nypl-5003296-original.jpg'
};}
function focus(){return {id:1579,status:'publish',modified:'2026-11-05T17:44:02',
  content:'our email of new investigations and archive finds, sent when we publish them. fvf-gift-v2'};}
test('composes five reviews atomically, preserves historical record and native Jetpack',()=>{
  const {proposed_content,receipt}=assemble(home(),focus(),safe);
  assert.equal(receipt.review_only,true);
  assert.equal(receipt.production_write,false);
  assert.equal(receipt.release,'HOLD');
  assert.equal(receipt.operations.length,5);
  assert.equal(receipt.before.focus,4);
  assert.equal(receipt.after.focus,5);
  assert.equal(receipt.after.margins,72);
  assert.equal(receipt.after.images,4);
  assert.equal(receipt.after.jetpack,1);
  for(const [,oldText,newText] of REPLACEMENTS)
    assert.ok(proposed_content.includes(newText),'proposed text missing '+oldText.slice(0,30));
});
const cases=[
 ['source hash mismatch',(h,f)=>({h,f,options:{hashFn:()=> 'unexpected'}})],
 ['wrong homepage identity',(h,f)=>({h:{...h,id:999},f})],
 ['wrong Focus identity',(h,f)=>({h,f:{...f,id:999}})],
 ['unpublished homepage',(h,f)=>({h:{...h,status:'draft'},f})],
 ['changed home timestamp',(h,f)=>({h:{...h,modified:'changed'},f})],
 ['changed Focus timestamp',(h,f)=>({h,f:{...f,modified:'changed'}})],
 ['Focus cadence removed',(h,f)=>({h,f:{...f,content:'fvf-gift-v2'}})],
 ['Focus gift-state changed',(h,f)=>({h,f:{...f,content:'our email of new investigations and archive finds, sent when we publish them.'}})],
 ['missing Margin item',(h,f)=>({h:{...h,content:h.content.replace('class="fv-margin-strip__item"','class="other"')},f})],
 ['missing chapter target',(h,f)=>({h:{...h,content:h.content.replace('id="fv-hf-observer"','id="missing"')},f})],
 ['duplicate hero',(h,f)=>({h:{...h,content:h.content+REPLACEMENTS[0][1]},f})],
 ['already-applied hero',(h,f)=>({h:{...h,content:h.content.replace(REPLACEMENTS[0][1],REPLACEMENTS[0][2])},f})],
 ['missing Jetpack block',(h,f)=>({h:{...h,content:h.content.replace('<!-- wp:jetpack/subscriptions -->','')},f})],
 ['missing NYPL map',(h,f)=>({h:{...h,content:h.content.replace('nypl-5003296-original.jpg','')},f})],
 ['lost Focus destination',(h,f)=>({h:{...h,content:h.content.replace('href="/focus/"','href="/blog/"')},f})],
 ['drift in disclosure anchor',(h,f)=>({h:{...h,content:h.content.replace(REPLACEMENTS[2][1],'different-disclosure')},f})]
];
for(const [name,mutate] of cases){
  test('fail closed: '+name,()=>{
    const change=mutate(home(),focus());
    assert.throws(()=>assemble(change.h,change.f,change.options||safe),/HOLD:/);
  });
}

// Unlike the synthetic preservation tests above, these exercise the native
// crypto path rather than overriding hashFn with a test-only return value.
test('native SHA-256 gate rejects synthetic source without a pinned digest',()=>{
  assert.throws(()=>assemble(home(),focus()),/HOLD: exact homepage SHA mismatch/);
});
test('native SHA-256 implementation matches known UTF-8 vector',()=>{
  const crypto=require('node:crypto');
  assert.equal(crypto.createHash('sha256').update('abc','utf8').digest('hex'),
    'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
});
