'use strict';
// Source-only; read-only; does not infer HTTP statuses, rights, or transfer savings.
const assert=require('node:assert/strict');
const sum=a=>a.reduce((n,r)=>n+r.original_bytes,0);
function expectedFor(originals,parts){
 assert.equal(parts.length,8);
 const posts=parts.flatMap(p=>p.posts),images=parts.flatMap(p=>p.images);
 assert.equal(posts.length,61);assert.equal(images.length,355);assert.equal(originals.length,13);
 assert.equal(new Set(images.map(x=>x.key)).size,355);
 assert.equal(new Set(originals.map(x=>x.media_id)).size,13);
 assert.equal(new Set(originals.map(x=>x.url)).size,13);
 const byKey=new Map(images.map(x=>[x.key,x]));
 const referenced=originals.filter(x=>x.referenced_inline_positions.length);
 const unreferenced=originals.filter(x=>!x.referenced_inline_positions.length);
 const noVariant=referenced.filter(x=>x.existing_wp_1024_variant===null);
 const withVariant=referenced.filter(x=>x.existing_wp_1024_variant!==null);
 const rows=originals.map(o=>{
  assert.ok(/^https:\/\/finalvestige\.com\/wp-content\/uploads\//i.test(o.url));
  assert.ok(Number.isSafeInteger(o.original_bytes)&&o.original_bytes>1572864);
  assert.ok(Number.isSafeInteger(o.original_width_px)&&o.original_width_px>0);
  assert.ok(Number.isSafeInteger(o.original_height_px)&&o.original_height_px>0);
  assert.ok(o.existing_wp_1024_variant===null||/^https:\/\//.test(o.existing_wp_1024_variant));
  assert.equal(o.approved_for_recompression,false);
  assert.equal(o.browser_transfer_bytes,null);
  assert.equal(new Set(o.referenced_inline_positions).size,o.referenced_inline_positions.length);
  const linked=o.referenced_inline_positions.map(key=>{
   const p=byKey.get(key);
   assert.ok(p&&p.source_url===o.url&&p.source_kind==='first_party');
   return{image_key:key,post_id:p.post_id,post_title:p.post_title,post_url:p.post_url,
     stored_source_url:p.source_url,stored_html_width_px:p.width_px,
     stored_html_height_px:p.height_px,stored_alt:p.alt};
  });
  const width=Math.min(960,o.original_width_px);
  return{media_id:o.media_id,original_url:o.url,original_bytes:o.original_bytes,
    original_width_px:o.original_width_px,original_height_px:o.original_height_px,
    inline_references:linked,recorded_1024_variant_url:o.existing_wp_1024_variant,
    exposure_class:!linked.length?'NOT_REFERENCED_INLINE_IN_FROZEN_61_POSTS':
      o.existing_wp_1024_variant?'INLINE_WITH_RECORDED_RESPONSIVE_PROXY':'INLINE_NO_RECORDED_RESPONSIVE_PROXY',
    conditional_960px_derivative:{width_px:width,height_px:Math.round(width*o.original_height_px/o.original_width_px),
      no_upscale:true,generate_only_after_rights_and_browser_review:true},
    guest_http_status:null,guest_current_src:null,guest_encoded_transfer_bytes:null,
    guest_visual_decode_confirmed:null,actual_weight_savings_bytes:null,
    rights_cleared_for_new_derivative:false,production_wp_write_authorized:false};
 });
 const summary={snapshot_published_posts:posts.length,snapshot_image_slots:images.length,
  oversized_originals_count:originals.length,oversized_original_bytes:sum(originals),
  oversized_originals_with_inline_reference:referenced.length,
  inline_referenced_original_bytes:sum(referenced),
  oversized_originals_not_referenced_inline:unreferenced.length,
  not_referenced_inline_original_bytes:sum(unreferenced),
  inline_without_recorded_1024_variant:noVariant.length,
  inline_without_recorded_1024_variant_original_bytes:sum(noVariant),
  inline_with_recorded_1024_variant:withVariant.length,
  inline_with_recorded_1024_variant_original_bytes:sum(withVariant),
  reported_42_broken_images_verified:false,claimed_76_percent_wire_reduction_measured:false,
  production_media_changes:0};
 return{rows,summary};
}
function validate(doc,originals,parts){
 assert.equal(doc.schema_version,1);
 assert.equal(doc.generated_utc_date,'2026-11-02');
 assert.equal(doc.kind,'frozen_CMS_source_and_Media_Library_inventory_not_a_live_browser_audit');
 assert.deepEqual(Object.keys(doc).sort(),['schema_version','generated_utc_date','kind',
  'frozen_input_blobs','summary','interpretation','rows'].sort());
 const expected=expectedFor(originals,parts);
 assert.deepEqual(doc.rows,expected.rows);
 assert.deepEqual(doc.summary,expected.summary);
 assert.equal(doc.summary.oversized_original_bytes,43522829);
 assert.equal(doc.summary.inline_referenced_original_bytes,23619602);
 assert.equal(doc.summary.inline_without_recorded_1024_variant_original_bytes,13267538);
 assert.equal(doc.summary.oversized_originals_with_inline_reference,7);
 assert.equal(doc.summary.oversized_originals_not_referenced_inline,6);
 assert.equal(doc.summary.inline_without_recorded_1024_variant,5);
 assert.match(doc.interpretation.method,/visitor-network image transfer bytes/);
 assert.match(doc.interpretation.rights,/not by themselves establish licensing/);
 assert.ok(/^[0-9a-f]{40}$/.test(doc.frozen_input_blobs.oversized_media_blob_sha));
 assert.ok(doc.frozen_input_blobs.parts_blob_shas.length===8&&
  doc.frozen_input_blobs.parts_blob_shas.every(x=>/^[0-9a-f]{40}$/.test(x)));
 return expected.summary;
}
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
 const read=p=>fs.readFileSync(path.join(__dirname,p),'utf8');
 const hash=s=>crypto.createHash('sha1').update('blob '+Buffer.byteLength(s)+'\0').update(s).digest('hex');
 const doc=JSON.parse(read('oversized_inline_exposure_20261102.json'));
 const raw=read('oversize_originals_20261030.json');
 assert.equal(hash(raw),doc.frozen_input_blobs.oversized_media_blob_sha);
 const parts=Array.from({length:8},(_,i)=>{
  const source=read('parts/0'+(i+1)+'.json');
  assert.equal(hash(source),doc.frozen_input_blobs.parts_blob_shas[i]);
  return JSON.parse(source);
 });
 process.stdout.write(JSON.stringify({validated:true,...validate(doc,JSON.parse(raw),parts)},null,2)+'\n');
}
module.exports={expectedFor,validate};
