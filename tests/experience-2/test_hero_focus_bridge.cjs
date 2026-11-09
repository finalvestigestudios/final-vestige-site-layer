'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {build,OLD_ACTIONS,NEW_ACTIONS,REQUIRE}=require('./patch_hero_focus_bridge.cjs');
function doc(){return [
'<div class="fv-margin-strip">',...Array.from({length:72},(_,i)=>`<span class="fv-margin-strip__item" style="--i:${i}">Source item ${i+1}</span>`),'</div>',
'<nav class="fv-hf__chapter-nav" aria-label="Explore the chapters">',...Array.from({length:7},(_,i)=>`<a href="#fv-hf-${i}">Chapter ${i}</a>`),'</nav>',
'<section><p>The Victory Point note: an 1847 message</p>',OLD_ACTIONS,'</section>',
'<p>NASA · Apollo 204 Review Board</p>',
'<!-- wp:jetpack/subscriptions {"className":"is-style-split"} /-->',
'<a href="/focus/">Existing Focus link</a>',
'<img src="focus_complete_cover.webp" alt="">'
].join('\n')}
function payload(){return {data:{id:6,status:'publish',modified:REQUIRE.modified,content:doc()}}}
test('one source-guarded change only, native block, 72 records, 7 links',()=>{const a=payload(),r=build(a);const [before,after]=[a.data.content,r.candidate];assert.equal(after.replace(NEW_ACTIONS,OLD_ACTIONS),before);assert.equal(r.receipt.unrelated_editor_bytes_identical,true);assert.equal(r.receipt.native_jetpack_block_preserved,true);assert.equal(r.receipt.margin_records_preserved,72);assert.equal(r.receipt.affiliate_links_added,0);assert.equal(r.receipt.confirmed_leads,0)});
const cases={
  wrong_site:a=>{a.data.id=7},wrong_status:a=>{a.data.status='draft'},editor_drift:a=>{a.data.modified='2026-11-08T00:00:00'},missing_content:a=>{delete a.data.content},
  missing_hero:a=>{a.data.content=a.data.content.replace(OLD_ACTIONS,'')},duplicated_hero:a=>{a.data.content+=OLD_ACTIONS},
  lost_margin:a=>{a.data.content=a.data.content.replace(/<span class="fv-margin-strip__item"[^>]*>[^<]*<\/span>/,'')},extra_margin:a=>{a.data.content+='<span class="fv-margin-strip__item">Injected</span>'},
  lost_nav:a=>{a.data.content=a.data.content.replace('fv-hf__chapter-nav','missing-nav')},lost_chapter:a=>{a.data.content=a.data.content.replace('<a href="#fv-hf-1">Chapter 1</a>','')},
  removed_jetpack:a=>{a.data.content=a.data.content.replace('<!-- wp:jetpack/subscriptions','<!-- wp:paragraph')},double_jetpack:a=>{a.data.content+='<!-- wp:jetpack/subscriptions {} /-->'},
  removed_focus:a=>{a.data.content=a.data.content.replace('<a href="/focus/">Existing Focus link</a>','')},
  missing_source:a=>{a.data.content=a.data.content.replace('NASA · Apollo 204 Review Board','fake claim')},
  missing_asset:a=>{a.data.content=a.data.content.replace('focus_complete_cover.webp','not-image.webp')},
  preexisting_candidate:a=>{a.data.content=a.data.content.replace(OLD_ACTIONS,NEW_ACTIONS)},
};
for(const [name,mutate] of Object.entries(cases))test('rejects '+name,()=>{const a=payload();mutate(a);assert.throws(()=>build(a),/REVIEW_FAIL_CLOSED/)});
