'use strict';
const assert=require('node:assert/strict');
function check(m) {
assert.equal(m.schema,'fv-prinsendam292-v1');assert.equal(m.post_id,292);
assert.equal(m.rows.length,6);
assert.deepEqual(m.counts,{authored:6,jetpack:5,direct:1,view_geometry:1,reader_displayed:5,reader_error:1,guest_browser_verified:0});
assert.deepEqual(m.historical,{posts:61,inline_images:355,external_origins:286,broken_reported:42,broken_verified:null,claimed_wire_saving_percent:76,wire_saving_measured_percent:null,oversized_originals:20,oversized_stored_bytes:64385752,oversized_visitor_bytes:null});
for(const x of Object.values(m.safety))assert.equal(x,0);
assert.match(m.dedupe_warning,/NOT be automatically/);
for(let i=0;i<6;i++){
const r=m.rows[i];assert.equal(r.slot,'292:'+i);
assert.ok(r.authored_url.startsWith('https://')&&r.view_src.startsWith('https://'));
assert.equal(r.alt_edit,r.alt_view);assert.ok(r.alt_view.length>30);
assert.equal(r.view_srcset,false);assert.equal(r.view_sizes,false);
assert.equal(r.view_jetpack,i!==2);
assert.equal(r.visitor_http_status,null);assert.equal(r.visitor_current_src,null);
assert.equal(r.visitor_decode,null);assert.equal(r.visitor_mime,null);assert.equal(r.visitor_transfer_bytes,null);
assert.equal(r.max_width_px,960);assert.equal(r.pixel_match_confirmed,false);
assert.equal(r.rights_to_copy_approved,false);assert.equal(r.wordpress_media_write_approved,false);
assert.ok(r.rights_summary.length>25);assert.ok(r.visual_match_status.length>8);
if(i===0){assert.equal(r.view_width,900);assert.equal(r.view_height,675);}
else {assert.equal(r.view_width,null);assert.equal(r.view_height,null);}
if(i===1)assert.ok(r.authored_url.includes('itok=wjXwUo3w'));
if(i===2)assert.equal(r.authored_url,r.view_src);
if(i===5)assert.equal(r.source_reader_result,'RETRIEVER_403_NOT_VISITOR_HTTP');
else assert.ok(r.source_reader_result.startsWith('IMAGE_DISPLAYED'));
if(r.candidate_native_catalog_px){
 const [w,h]=r.candidate_native_catalog_px,[tw,th]=r.conditional_review_px;
 assert.equal(tw,Math.min(960,w));assert.equal(th,Math.round(h*tw/w));
 assert.ok(tw<=w&&th<=h);
} else assert.equal(r.conditional_review_px,null);
}
assert.equal(m.rows[0].candidate_native_catalog_px[0],2870);
assert.equal(m.rows[3].candidate_native_catalog_px[0],2820);
assert.notEqual(m.rows[0].view_width/m.rows[0].view_height,2870/1930);
return true;
}
module.exports={check};
if(require.main===module){
const fs=require('node:fs');
const m=JSON.parse(fs.readFileSync(process.argv[2]||'qa/media-recovery/prinsendam292_guest_source_custody_20261116_2031pt.json','utf8'));
check(m);console.log('PASS Prinsendam 292 provenance guard');
}