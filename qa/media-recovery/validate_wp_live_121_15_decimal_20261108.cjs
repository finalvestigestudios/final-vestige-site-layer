'use strict';
// Offline, read-only validation of a frozen WordPress media inventory.
// Stored original bytes are NEVER measured browser transfer or demonstrated savings.
function validate(a) {
  const e=[], fail=(message)=>e.push(message);
  if(!a||typeof a!=='object')return ['audit_not_object'];
  if(a.schema!=='fv-live-wp-121-media-decimal-oversize-v1')fail('schema');
  if(a.capture_date_local!=='2026-11-08'||!String(a.capture_context).includes('read-only'))fail('evidence_provenance');
  if(a.frozen_20261030_posts!==61||a.frozen_20261030_inline_images!==355||a.current_published_post_count_readonly!==66)fail('cohort_versions');
  const m=a.live_media_inventory||{},rows=a.rows;
  if(!Array.isArray(rows))return [...e,'rows_missing'];
  if(m.media_type!=='image'||JSON.stringify(m.pages_checked)!=='[1,2]'||
     JSON.stringify(m.returned_rows_by_page)!=='[100,21]'||m.image_media_items!==121||
     m.all_stored_original_bytes!==70554906)fail('live_inventory_custody');
  if(m.threshold_decimal_bytes_exclusive!==1500000||m.threshold_binary_bytes_exclusive!==1572864)fail('threshold_units');
  if(rows.length!==15||m.over_decimal_count!==15)fail('decimal_count');
  if(m.over_decimal_stored_original_bytes!==47096779)fail('decimal_total');
  if(m.over_binary_count!==14||m.over_binary_stored_original_bytes!==45553777)fail('binary_total');
  if(m.actual_browser_transfer_bytes!==null||m.reported_76_pct_visitor_savings_verified!==false)fail('browser_transfer_claim');
  const ids=new Set(),urls=new Set(),oldIds=[388,1258,1257,39,43,389,40,41,42,382,482,405,293];
  let decBytes=0,binCount=0,binBytes=0;
  for(const r of rows){
    if(!Number.isSafeInteger(r.media_id)||ids.has(r.media_id))fail('duplicate_or_bad_media_id');
    ids.add(r.media_id);
    if(typeof r.original_url!=='string'||!r.original_url.startsWith('https://finalvestige.com/wp-content/uploads/')||urls.has(r.original_url))fail('duplicate_or_external_source_url');
    urls.add(r.original_url);
    const b=r.original_stored_bytes, dims=r.wp_metadata_native_px,deriv=r.conditional_derivative_px;
    if(!Number.isSafeInteger(b)||b<=1500000)fail('nonoversize_in_decimal_rows');
    else {decBytes+=b;if(b>1572864){binBytes+=b;binCount++;}}
    if(!Array.isArray(dims)||dims.length!==2||!dims.every(x=>Number.isSafeInteger(x)&&x>0))fail('bad_original_dimensions');
    if(!Array.isArray(deriv)||deriv.length!==2||!deriv.every(x=>Number.isSafeInteger(x)&&x>0))fail('bad_derivative_dimensions');
    if(Array.isArray(dims)&&Array.isArray(deriv)&&dims.every(x=>Number.isSafeInteger(x)&&x>0) && deriv.every(x=>Number.isSafeInteger(x)&&x>0)){
      const expectedWidth=Math.min(dims[0],960), expectedHeight=Math.round(dims[1]*expectedWidth/dims[0]);
      if(deriv[0]!==expectedWidth||deriv[1]!==expectedHeight||deriv[0]>dims[0]||deriv[1]>dims[1])fail('geometry_or_upscale');
    }
    if(!Number.isSafeInteger(r.wp_metadata_subsize_count)||r.wp_metadata_subsize_count<0)fail('subsize_metadata');
    for(const key of ['source_status_origin_http','guest_browser_http','guest_decoded_px','guest_current_src','guest_wire_bytes','binary_content_hash_sha256'])
      if(r[key]!==null)fail('fabricated_network_or_binary_proof:'+key);
    for(const key of ['wp_upload_authorized','post_rewrite_authorized'])
      if(r[key]!==false)fail('prohibited_write:'+key);
    if(r.bytes_are_storage_not_transfer!==true||r.derivative_only_after_rights_and_visual_approval!==true||
       typeof r.rights_status!=='string'||!r.rights_status.includes('REVIEW')&&!r.rights_status.includes('UNVERIFIED')&&!r.rights_status.includes('REQUIRED'))fail('release_rights_hold');
    if(r.wp_attachment_post_id!==null && !Number.isSafeInteger(r.wp_attachment_post_id))fail('attachment_id');
  }
  if(decBytes!==47096779||binBytes!==45553777||binCount!==14)fail('recomputed_weight_totals');
  const previous=a.prior_verified_13_MiB_20261104||{}, newItems=a.newly_reconciled||{};
  if(JSON.stringify(previous.media_ids)!==JSON.stringify(oldIds)||previous.stored_original_bytes!==43522829||
     oldIds.some(id=>!ids.has(id)))fail('old_13_crosswalk');
  const added=[...ids].filter(id=>!oldIds.includes(id)).sort((x,y)=>x-y);
  if(JSON.stringify(added)!=='[1714,2148]'||!Array.isArray(newItems.additional_vs_13_id_list)||
     JSON.stringify([...newItems.additional_vs_13_id_list].sort((x,y)=>x-y))!=='[1714,2148]'||
     newItems.decimal_only_id!==1714||newItems.additional_stored_bytes!==3573950)fail('new_two_reconciliation');
  const one=rows.find(r=>r.media_id===1714),two=rows.find(r=>r.media_id===2148);
  if(!one||one.original_stored_bytes!==1543002||JSON.stringify(one.wp_metadata_native_px)!=='[1280,1280]'||
     one.mime!=='image/png'||JSON.stringify(one.conditional_derivative_px)!=='[960,960]')fail('halifax_media_custody');
  if(!two||two.original_stored_bytes!==2030948||JSON.stringify(two.wp_metadata_native_px)!=='[1821,1190]'||
     two.mime!=='image/jpeg'||JSON.stringify(two.conditional_derivative_px)!=='[960,627]')fail('noaa_media_custody');
  const custody=a.target_source_custody||{}, hal=custody['1714']||{}, noaa=custody['2148']||{};
  if(hal.post_id!==269||hal.raw_gutenberg_img_src_confirmed!==one?.original_url||
     !hal.post_url?.includes('/the-watch-lost-its-hands-halifax-explosion/')||
     hal.map_text_legibility_review!==true||hal.rights_status!=='AUTHOR_OR_LICENSE_UNVERIFIED')fail('halifax_published_source');
  if(noaa.media_added!=='2026-11-07T11:37:04'||noaa.commons_record_bytes!==2030948||
     JSON.stringify(noaa.commons_record_px)!=='[1821,1190]'||
     !noaa.commons_catalog_url?.startsWith('https://commons.wikimedia.org/wiki/File:1927_')||
     !noaa.noaa_catalog_url?.includes('wea00739jpg')||noaa.byte_identity_sha1_verified_locally!==false||
     noaa.matched_wp_original_bytes_and_dimensions!==true||noaa.usage_in_66_live_posts!=='NOT_ESTABLISHED'||
     noaa.rights_status!=='REVIEW_REQUIRED')fail('noaa_provenance_hold');
  const release=a.release||{};
  if(release.visitor_confirmed_broken_total!==null||release.reported_42_browser_broken_verified!==false||
     release.reported_76_transfer_reduction_measured!==false||
     JSON.stringify(release.unchanged_priority_p0_slots)!=='["285:5","285:2","287:5","418:1","418:2","407:1"]')fail('p0_and_performance_claims');
  for(const k of ['source_failures_certified','assets_downloaded','assets_rehosted','wordpress_production_writes','homepage_changes','spend_usd'])
    if(release[k]!==0)fail('unsafe_operation:'+k);
  if(release.all_proposed_derivatives_hold!==true)fail('derivative_release_hold');
  return [...new Set(e)];
}
module.exports={validate};
if(typeof require!=='undefined' && require.main===module){
  const fs=require('node:fs');
  const file=process.argv[2]||'qa/media-recovery/wp_live_121_15_decimal_threshold_20261108.json';
  const errors=validate(JSON.parse(fs.readFileSync(file,'utf8')));
  if(errors.length){console.error('HOLD '+errors.join(', '));process.exitCode=1;}
  else console.log('PASS: exact 121-image metadata, 15 decimal MB rows, 14 binary MiB rows; no browser/rights/write claims');
}
