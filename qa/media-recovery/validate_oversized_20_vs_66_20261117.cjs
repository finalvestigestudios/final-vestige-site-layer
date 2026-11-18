'use strict';
// Offline only: crosswalk current WordPress original sizes to authenticated VIEW img src.
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {readCensus,verify}=require('./validate_live_66_view_20261117.cjs');
function readOversize(dir=__dirname){
  return {
    media:JSON.parse(fs.readFileSync(path.join(dir,'live_media_over_1_5mib_20261117_1624pt.json'),'utf8')),
    crosswalk:JSON.parse(fs.readFileSync(path.join(dir,'live_20_oversized_to_66_post_inline_crosswalk_20261117.json'),'utf8')),
    census:readCensus(dir)
  };
}
function verifyOversize(media,crosswalk,census){
  verify(census.slices,census.rollup);
  assert.equal(media.schema,'fv-current-oversized-media-v2');
  assert.equal(crosswalk.schema,'fv-oversized-current-66-inline-crosswalk-v1');
  assert.equal(media.production_writes,0);assert.equal(crosswalk.production_writes,0);
  assert.equal(media.summary.image_media_items,132);
  assert.equal(media.summary.decimal_threshold_bytes,1500000);
  assert.equal(media.summary.binary_threshold_bytes,1572864);
  assert.equal(media.items.length,20);assert.equal(crosswalk.items.length,20);
  assert.equal(media.summary.decimal_over_1_5MB_count,20);
  assert.equal(media.summary.decimal_over_1_5MB_stored_bytes,64385752);
  assert.equal(media.summary.binary_over_1_5MiB_count,19);
  assert.equal(media.summary.binary_over_1_5MiB_stored_bytes,62842750);
  const extras=media.items.filter(m=>m.original_bytes>1500000&&m.original_bytes<=1572864);
  assert.deepEqual(extras.map(m=>[m.id,m.original_bytes]),[[1714,1543002]]);
  const images=census.slices.flatMap(p=>p.images);
  let found=0,foundBytes=0,missingBytes=0,foundSlots=0,withVariants=0;
  for(const item of media.items){
    assert.ok(item.original_bytes>1500000);
    assert.equal(item.above_binary_1_5MiB,item.original_bytes>1572864);
    assert.equal(item.guest_delivered_bytes,null);assert.equal(item.production_action,'none');
    assert.equal(item.source_rights,'not_audited');
    assert.ok(item.recommended_no_upscale_max960.width<=960&&item.recommended_no_upscale_max960.width<=item.width);
    assert.ok(item.recommended_no_upscale_max960.height<=item.height);
    for(const option of item.existing_responsive_variants_at_or_under960)assert.ok(option.width<=960);
    if(item.existing_responsive_variants_at_or_under960.length)withVariants++;
    const row=crosswalk.items.find(r=>r.id===item.id);
    assert.ok(row,'missing media ID '+item.id);
    assert.equal(row.filename,item.wp_original_file);
    assert.equal(row.original_bytes,item.original_bytes);
    assert.equal(row.visitor_network_bytes,null);
    assert.equal(row.rights_for_reprocessing,'HOLD');
    const expected=images.filter(im=>(im.source_origin_url||'').split('?')[0]===item.source_url.split('?')[0]).map(im=>im.post_id+':'+im.slot).sort();
    const actual=row.inline_exact_origin_slots.map(im=>im.slot_id).sort();
    assert.deepEqual(actual,expected,'incorrect exact-src crosswalk '+item.id);
    if(actual.length){found++;foundBytes+=item.original_bytes;foundSlots+=actual.length;}else missingBytes+=item.original_bytes;
    for(const x of row.inline_exact_origin_slots){
      const im=images.find(y=>y.post_id+':'+y.slot===x.slot_id);
      assert.ok(im);assert.equal(x.view_img_src,im.authored_view_src);
      assert.equal(x.has_srcset,im.has_srcset);assert.equal(x.has_sizes,im.has_sizes);
    }
  }
  assert.equal(found,11);assert.equal(foundSlots,11);assert.equal(foundBytes,38480915);
  assert.equal(missingBytes,25904837);
  assert.equal(withVariants,15);
  assert.equal(crosswalk.summary.inline_exact_originals,found);
  assert.equal(crosswalk.summary.inline_exact_image_slots,foundSlots);
  assert.equal(crosswalk.summary.not_observed_exact_inline,20-found);
  assert.equal(crosswalk.summary.inline_exact_stored_original_bytes,foundBytes);
  assert.equal(crosswalk.summary.not_observed_exact_inline_stored_original_bytes,missingBytes);
  assert.equal(crosswalk.summary.visitor_wire_bytes,null);
  return {oversized:20,inline_exact:found,not_inline_exact:20-found,stored_bytes:64385752};
}
if(require.main===module)process.stdout.write(JSON.stringify(verifyOversize(...Object.values(readOversize())))+'\n');
module.exports={readOversize,verifyOversize};
