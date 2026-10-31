'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {parseImageURL,validate}=require('./validate_oversize_inline_reconciled.cjs');
const read=f=>JSON.parse(fs.readFileSync(path.join(__dirname,f),'utf8'));
const manifest=read('oversize_inline_reconciled_20261031.json');
const originals=read('oversize_originals_20261030.json');
const census=Array.from({length:8},(_,i)=>read('parts/'+String(i+1).padStart(2,'0')+'.json')).flatMap(x=>x.images);
const copy=x=>structuredClone(x);
const run=fn=>{const m=copy(manifest);if(fn)fn(m);return validate(m,originals,census);};
test('complete 13/355 snapshot reconciles 10 inline media (7 direct, 3 Jetpack)',()=>{
 const out=run();assert.equal(out.ok,true,out.errors.join(','));assert.equal(out.original_storage_bytes,43522829);
 assert.equal(out.matched_inline_media,10);assert.equal(out.exact_inline,7);
 assert.equal(out.jetpack_inline,3);assert.equal(out.not_inline,3);assert.equal(out.unsized_featured_media,5);
});
test('Jetpack same-site URL matches canonical path but remains a different stored URL',()=>{
 const orig=manifest.rows.find(x=>x.media_id===388);
 const a=parseImageURL(orig.original_url),b=parseImageURL(orig.inline_matches[0].stored_url);
 assert.equal(a.path,b.path);assert.equal(a.method,'exact_first_party_path');
 assert.equal(b.method,'verified_same_origin_jetpack_proxy');
});
test('reject external Jetpack source and content-selecting query confusion',()=>{
 assert.equal(parseImageURL('https://i0.wp.com/other.org/wp-content/uploads/x.jpg?fit=960%2C640&ssl=1'),null);
 assert.equal(parseImageURL('https://i0.wp.com/finalvestige.com/wp-content/uploads/a.jpg?image=other&fit=960%2C640&ssl=1'),null);
 assert.equal(parseImageURL('https://i0.wp.com/finalvestige.com/wp-content/uploads/a.jpg?fit=0%2C640&ssl=1'),null);
});
for(const [label,mut,needle] of [
 ['fabricated HTTP 404',m=>m.rows[0].actual_image_http_status=404,'unverified_or_unauthorized'],
 ['fabricated response bytes',m=>m.rows[1].actual_image_transfer_bytes=150000,'unverified_or_unauthorized'],
 ['fake decoded image width',m=>m.rows[2].decoded_browser_width_px=960,'unverified_or_unauthorized'],
 ['claimed 42 browser failures',m=>m.reported_broken_images_42_browser_verified=true,'fabricated_claim'],
 ['claimed 76 percent savings',m=>m.summary.measured_weight_reduction_percent=76,'fabricated_claim'],
 ['unapproved rights assertion',m=>m.rows[0].rights_clearance=true,'unverified_or_unauthorized'],
 ['unapproved WordPress upload',m=>m.rows[0].wordpress_upload_authorized=true,'unverified_or_unauthorized'],
 ['production rewrite claim',m=>m.rows[0].production_post_change_authorized=true,'unverified_or_unauthorized'],
 ['invented SHA256',m=>m.rows[0].original_sha256='a'.repeat(64),'unverified_or_unauthorized'],
 ['oversized derivative',m=>m.rows[3].proposed_width_px=1280,'dimensions'],
 ['wrong derivative height',m=>m.rows[3].proposed_height_px=1,'dimensions'],
 ['wrong Vasa slot',m=>m.rows.find(x=>x.media_id===388).inline_matches[0].image_key='299:0','false_alias'],
 ['swapped Vasa CDN source',m=>m.rows.find(x=>x.media_id===389).inline_matches[0].stored_url='https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-modell-2020.jpg?fit=1024%2C681&ssl=1','false_alias'],
 ['proxy replaced with unrelated origin',m=>m.rows.find(x=>x.media_id===382).inline_matches[0].stored_url='https://i0.wp.com/unrelated.com/wp-content/uploads/2026/08/vasa-med-gamla-och-nya-stottor_vasa-with-old-and-new-supports.jpg?fit=1024%2C683&ssl=1','false_alias'],
 ['missing proxy inline match',m=>m.rows.find(x=>x.media_id===389).inline_matches=[],'missing_inline'],
 ['duplicate historical image key',m=>{const x=m.rows.find(y=>y.media_id===388);x.inline_matches.push(copy(x.inline_matches[0]));},'missing_inline'],
 ['false nonexistent WordPress hero sizes',m=>m.rows.find(x=>x.media_id===39).wordpress_registered_subsizes=true,'subsize_record'],
 ['false non-inline flag',m=>m.rows.find(x=>x.media_id===388).review_priority='P3_no_inline_match_in_61_post_snapshot','vasa_proxy'],
 ['missing featured association',m=>m.rows.find(x=>x.media_id===39).featured_post_verified=null,'featured_hero'],
 ['original storage bytes changed',m=>m.rows.find(x=>x.media_id===40).original_storage_bytes=100,'original_snapshot'],
 ['bad source kind',m=>m.rows.find(x=>x.media_id===389).inline_matches[0].source_kind='external','false_alias'],
 ['unsupported 76% top-level claim',m=>m.reported_76pct_weight_saving_measured=true,'fabricated_claim']
]) test('reject '+label,()=>{const r=run(mut);assert.equal(r.ok,false);assert.ok(r.errors.some(x=>x.includes(needle)),r.errors.join(','));});
