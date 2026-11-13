'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {reportHtmlImageGeometry,P0}=require('./audit_html_image_geometry_20261112.cjs');
const clone=x=>JSON.parse(JSON.stringify(x));
const row=(slot,ext=true,w=null,h=null)=>({slot,post_id:Number(slot.split(':')[0]),
 source_url:'https://archive.gov/image-'+slot.replace(':','-')+'.jpg',
 post_url:'https://finalvestige.com/article-'+slot.split(':')[0]+'/',alt:'Historic image',source_equal:true,alt_equal:true,
 offsite_historical_registry:ext,html_width_px:w,html_height_px:h,html_srcset_present:false});
const base=()=>({schema:'fv-media-complete-historical-61-355-live-src-alt-20261112-v1',rows:[row('285:2'),row('285:5'),row('287:5'),row('418:1'),row('418:2'),row('407:1'),row('268:0'),row('299:1',false,960,640)]});
const run=(data,options={testOnlyAllowUnpinned:true})=>reportHtmlImageGeometry(Buffer.from(JSON.stringify(data)),options);
test('eight-image control source audit distinguishes missing dimensions and measured CLS',()=>{
 const a=run(base());assert.equal(a.status,'VERIFIED_SOURCE_ONLY_LAYOUT_GEOMETRY_EXPOSURE');
 assert.equal(a.counts.inline_image_slots,8);assert.equal(a.counts.missing_both_html_dimensions,7);
 assert.equal(a.counts.offsite_missing_both_dimensions,7);assert.equal(a.counts.first_party_missing_both_dimensions,0);
 assert.equal(a.counts.p0_source_slots_without_both_html_dimensions,6);
 assert.deepEqual(a.p0_qa_sequence.map(r=>r.slot),P0);
 assert.equal(a.measured_cls,null);assert.equal(a.guest_broken_images_confirmed,null);assert.equal(a.production_change_allowed,false);
});
test('partial width only is HOLD',()=>{const a=base();a.rows[0].html_width_px=960;assert.equal(run(a).reason,'PARTIAL_OR_INVALID_STORED_HTML_GEOMETRY')});
test('zero height is HOLD',()=>{const a=base();a.rows[0].html_width_px=960;a.rows[0].html_height_px=0;assert.equal(run(a).reason,'PARTIAL_OR_INVALID_STORED_HTML_GEOMETRY')});
test('negative width is HOLD',()=>{const a=base();a.rows[0].html_width_px=-1;a.rows[0].html_height_px=960;assert.equal(run(a).reason,'PARTIAL_OR_INVALID_STORED_HTML_GEOMETRY')});
test('duplicate slot is HOLD',()=>{const a=base();a.rows.push(clone(a.rows[0]));assert.equal(run(a).reason,'INVALID_FROZEN_IMAGE_ROW_OR_IDENTITY')});
test('post identity contradiction is HOLD',()=>{const a=base();a.rows[0].post_id=999;assert.equal(run(a).reason,'INVALID_FROZEN_IMAGE_ROW_OR_IDENTITY')});
test('post URL mismatch is HOLD',()=>{const a=base();a.rows[1].post_url='https://finalvestige.com/other/';assert.equal(run(a).reason,'POST_URL_CONFLICT')});
test('invalid source/caption custody is HOLD',()=>{const a=base();a.rows[0].alt_equal=false;assert.equal(run(a).reason,'INVALID_FROZEN_IMAGE_ROW_OR_IDENTITY')});
test('parsed audit object not accepted as raw Git bytes',()=>{assert.equal(reportHtmlImageGeometry(base()).reason,'RAW_FROZEN_AUDIT_BUFFER_REQUIRED')});
test('unapproved source bytes blocked by Git SHA pin',()=>{assert.equal(run(base(),{testOnlyAllowUnpinned:false}).reason,'FROZEN_AUDIT_GIT_BLOB_MISMATCH')});
test('no cached/WordPress edit permission is emitted',()=>{const a=run(base());assert.equal(a.wordpress_post_rewrite_allowed,false);assert.equal(a.third_party_download_or_mirror_allowed,false);assert.equal(a.output_width_constraint.includes('960px'),true)});
test('missing image DOM dimensions never independently declare an actual browser outage',()=>{const a=run(base());assert.equal(a.guest_broken_images_confirmed,null);assert.equal(a.measured_image_wire_reduction_percent,null);assert.ok(a.inference_limit.includes('not proof'))});
test('all requested P0 refs are strictly existing slots in source audit',()=>{const a=base();a.rows=a.rows.filter(r=>r.slot!=='285:2');const v=run(a);assert.equal(v.counts.p0_source_slots_without_both_html_dimensions,5);assert.equal(v.p0_qa_sequence.length,5)});
