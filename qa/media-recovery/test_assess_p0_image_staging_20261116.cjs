'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {evaluate,ratio960,P0}=require('./assess_p0_image_staging_20261116.cjs');
const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'p0_image_staging_custody_20261116.json'),'utf8'));
const clone=x=>structuredClone(x);
const candidate=manifest.slots.find(x=>x.key==='407:1');
function full(){
 const qa={schema:'fv-siteqa-p0-cold-projection-v1',collector_owner:'site-qa-pr-154',slots:[{
 key:'407:1',post_url:candidate.post_url,wp_modified:candidate.wp_modified,
 authored_url:candidate.authored_url,rendered_url:candidate.rendered_url,
 capture_origin:'logged-out-cold-chromium',synthetic:false,current_src:candidate.rendered_url,
 final_url:candidate.rendered_url,redirect_chain:[candidate.rendered_url],image_request_count:1,
 transferred_bytes:471,http_status:404,content_type:'text/html',
 failed_decode:true,natural_width:0,visibly_broken:true,decode_error:'yes',
 screenshot_ref:'siteqa-154-screen-407-1.png',visual_review_ref:'siteqa-154-report-407-1'}]};
 const approvals={schema:'fv-media-repair-approvals-v1',slots:[{
 key:'407:1', current_wp_modified:candidate.wp_modified,
 candidate_asset_url:candidate.candidate.asset_url,rights_item_record:candidate.candidate.catalog_url,
 rights_basis:'official-public-domain-item',rights_reviewer_approved:true,
 attribution_approved:true,exact_visual_frame_verified:true,cropped_comparison_reviewed:true,
 editorial_signoff:true,rehosting_authorized:true,repair_scope:'single-article-image',
 block_rewrite_requested:false,asset_sha256:'a'.repeat(64),native_width:1200,native_height:800,
 evidence_source:'reviewed-original-binary',credit_text:'USGS / J. R. Stacy'}]};
 return {qa,approvals};
}
const one=r=>r.results.find(x=>x.key==='407:1');
test('baseline six actual-source URLs all HOLD; guest HTTP still unknown',()=>{
 const r=evaluate(manifest);assert.equal(r.ok,true);assert.equal(r.results.length,6);
 assert.deepEqual(r.results.map(x=>x.key),P0);assert.ok(r.results.every(x=>x.decision==='HOLD'));
 assert.equal(r.visitor_broken_confirmed,null);assert.equal(r.staging_review_candidates,0);
 assert.equal(r.wordpress_writes,0);assert.equal(r.media_downloads,0);assert.equal(r.measured_savings_percent,null);
});
test('no licensed exact binaries yet for four P0 slots',()=>{
 const r=evaluate(manifest);for(const k of ['285:2','285:5','287:5','418:2'])
 assert.ok(r.results.find(x=>x.key===k).reasons.includes('NO_IDENTIFIED_REPLACEMENT_BINARY'));
});
test('refuse to treat a catalog HTML page as an image binary',()=>{
 const m=clone(manifest);m.slots[0].candidate={catalog_url:'https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg',
 asset_url:'https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg'};
 const r=evaluate(m);assert.ok(r.results[0].reasons.includes('NO_IDENTIFIED_REPLACEMENT_BINARY'));
});
test('no-upscale geometry 960 by 640',()=>assert.deepEqual(ratio960(1200,800),{width:960,height:640,no_upscale:true}));
test('no-upscale geometry 819 by 614',()=>assert.deepEqual(ratio960(819,614),{width:819,height:614,no_upscale:true}));
test('no-upscale geometry 600 by 463',()=>assert.deepEqual(ratio960(600,463),{width:600,height:463,no_upscale:true}));
test('unknown geometry rejected',()=>assert.equal(ratio960(null,800),null));
test('synthetic complete fields yield STAGING_REVIEW_ONLY, never authorized write',()=>{
 const {qa,approvals}=full();const r=evaluate(manifest,qa,approvals);
 assert.equal(one(r).decision,'STAGING_REVIEW_ONLY');assert.equal(one(r).wordpress_action,'NONE');
 assert.deepEqual(one(r).review_geometry,{width:960,height:640,no_upscale:true});
 assert.equal(r.wordpress_writes,0);assert.equal(r.staging_review_candidates,1);
 assert.equal(r.visitor_broken_confirmed,null);
});
const malformed=[
 ['reorder slots',x=>x.slots.reverse()],
 ['repeat key',x=>x.slots[1].key=x.slots[0].key],
 ['invent HTTP response',x=>x.slots[0].guest_http_status=404],
 ['invent decode state',x=>x.slots[0].guest_decoded=true],
 ['change authored URL',x=>x.slots[0].authored_url='ftp://site/image.jpg'],
 ['malformed rendered URL',x=>x.slots[0].rendered_url='data:example'],
 ['fake WordPress cached',x=>x.slots[0].cached_to_wordpress=true],
 ['increase 960 cap',x=>x.slots[0].max_width=1920],
 ['premature rights approval',x=>x.slots[0].rights_release_status='CLEARED'],
 ['erase post revision',x=>x.slots[0].wp_modified='unknown'],
];
for(const [label,mutate] of malformed)test('manifest rejects '+label,()=>{
 const m=clone(manifest);mutate(m);assert.equal(evaluate(m).error,'INVALID_PINNED_SOURCE_MANIFEST');
});
const edits=[
 ['wrong collector',d=>d.qa.collector_owner='another-team'],
 ['unauthenticated browser',d=>d.qa.slots[0].capture_origin='headless-web-retriever'],
 ['synthetic capture',d=>d.qa.slots[0].synthetic=true],
 ['wrong post URL',d=>d.qa.slots[0].post_url='https://finalvestige.com/different'],
 ['stale revision',d=>d.qa.slots[0].wp_modified='2020-01-01'],
 ['wrong image currentSrc',d=>d.qa.slots[0].current_src='https://example.com/hijack.jpg'],
 ['bad redirect evidence',d=>d.qa.slots[0].redirect_chain=['https://example.com/unknown']],
 ['missing screenshot',d=>d.qa.slots[0].screenshot_ref=''],
 ['missing visual review',d=>d.qa.slots[0].visual_review_ref=''],
 ['missing cold wire byte count',d=>d.qa.slots[0].transferred_bytes=null],
 ['no numeric HTTP',d=>d.qa.slots[0].http_status=null],
 ['decoded image healthy',d=>{d.qa.slots[0].natural_width=900;d.qa.slots[0].failed_decode=false;}],
 ['visible image healthy',d=>d.qa.slots[0].visibly_broken=false],
 ['200 valid image not decode-error',d=>{d.qa.slots[0].http_status=200;d.qa.slots[0].content_type='image/jpeg';d.qa.slots[0].decode_error='no';}],
 ['rights reviewer absent',d=>d.approvals.slots[0].rights_reviewer_approved=false],
 ['no rights record',d=>d.approvals.slots[0].rights_item_record='https://example.com/unknown'],
 ['unsupported rights basis',d=>d.approvals.slots[0].rights_basis='internet-photo'],
 ['wrong source file',d=>d.approvals.slots[0].candidate_asset_url='https://example.com/other.jpg'],
 ['no exact frame',d=>d.approvals.slots[0].exact_visual_frame_verified=false],
 ['no crop match',d=>d.approvals.slots[0].cropped_comparison_reviewed=false],
 ['missing credit',d=>d.approvals.slots[0].credit_text=''],
 ['no permission to rehost',d=>d.approvals.slots[0].rehosting_authorized=false],
 ['homepage design scope',d=>d.approvals.slots[0].repair_scope='homepage'],
 ['proposed block rewrite',d=>d.approvals.slots[0].block_rewrite_requested=true],
 ['unverified source binary',d=>d.approvals.slots[0].evidence_source='catalog-preview'],
 ['unverified master SHA',d=>d.approvals.slots[0].asset_sha256='fake'],
 ['missing master size',d=>d.approvals.slots[0].native_width=null],
 ['stale approval',d=>d.approvals.slots[0].current_wp_modified='2026-09-01'],
];
for(const [label,mutate] of edits)test('evidence gate HOLD on '+label,()=>{
 const d=full();mutate(d);assert.equal(one(evaluate(manifest,d.qa,d.approvals)).decision,'HOLD');
});
test('duplicate QA key rejected globally',()=>{
 const d=full();d.qa.slots.push(clone(d.qa.slots[0]));
 assert.equal(evaluate(manifest,d.qa,d.approvals).error,'DUPLICATE_OR_UNKNOWN_SLOT_EVIDENCE');
});
test('foreign QA key rejected globally',()=>{
 const d=full();d.qa.slots[0].key='777:1';
 assert.equal(evaluate(manifest,d.qa,d.approvals).error,'DUPLICATE_OR_UNKNOWN_SLOT_EVIDENCE');
});
test('missing approval never proceeds despite real failure fields',()=>{
 const d=full();assert.equal(one(evaluate(manifest,d.qa,null)).decision,'HOLD');
});
