'use strict';
/**
 * Read-only, fail-closed audit verifier for Scotch Cap image custody.
 * No network, WordPress, image copying, or actual HTTP claims.
 * Run: node qa/media-recovery/test_scotch_cap_418_20261104.cjs
 */
const VALID_PROBES = new Set([
  'unavailable_to_independent_web_retriever',
  'web_retriever_403_wrapper_not_origin_status',
  'image_visibly_displayed_in_independent_web_retriever'
]);
const EXACT_SOURCE_BLOB='948bc1b65b42799aa40cfdb810ddf6ffd80886b6';
function validate(audit, frozen) {
  const errors=[];
  const bad=(msg)=>errors.push(msg);
  if (!audit || !frozen || !Array.isArray(audit.rows) || !Array.isArray(frozen.images)) return {ok:false,errors:['missing rows or frozen images']};
  if (audit.schema_version!=='1.0'||audit.post?.id!==418||audit.post?.status!=='publish') bad('post/schema');
  if (audit.frozen_source?.git_blob_sha!==EXACT_SOURCE_BLOB) bad('frozen source blob');
  if (audit.verification?.six_src_matches!==true||audit.verification?.six_alt_matches!==true||audit.verification?.img_tags!==6||audit.verification?.img_tags_with_width_and_height!==0) bad('CMS match/dimension evidence');
  if (audit.http_evidence?.guest_browser_used!==false||audit.http_evidence?.origin_get_statuses_measured!==0||audit.http_evidence?.actual_bytes_measured!==0) bad('unmeasured HTTP/bytes');
  if (audit.baseline?.posts!==61||audit.baseline?.inline_images!==355||audit.baseline?.external_original_refs!==288||audit.baseline?.oversized_wp_originals_1_5MiB!==13||audit.baseline?.reported_broken_unconfirmed!==42||audit.baseline?.reported_reduction_unmeasured_percent!==76) bad('frozen scope');
  const expected=frozen.images.filter(x=>x.post_id===418).sort((a,b)=>a.slot-b.slot);
  if(expected.length!==6||audit.rows.length!==6) bad('six-slot cohort');
  const seen=new Set(), origins=new Set();
  for(let i=0;i<audit.rows.length;i++) {
    const r=audit.rows[i], o=expected[i];
    if(!r||!o) {bad('slot '+i+' absent');continue;}
    if(r.key!=='418:'+i||r.slot!==i||r.key!==o.key||r.source_url!==o.source_url||r.alt!==o.alt||r.source_host!==o.source_host||r.source_kind!==o.source_kind) bad('original identity '+i);
    if(seen.has(r.key)||origins.has(r.source_url)) bad('duplicate '+i);
    seen.add(r.key); origins.add(r.source_url);
    if(!/^https:\/\//.test(r.source_url)||!r.archival||!/^https:\/\//.test(r.archival.catalog||'')||!/^https:\/\//.test(r.archival.rendition||'')) bad('archival path '+i);
    if(!VALID_PROBES.has(r.probe?.kind)) bad('probe category '+i);
    for(const field of ['origin_http_status','browser_http_status','browser_mime','decoded_natural_width','decoded_natural_height','cdp_encoded_data_bytes']) {
      if(r.probe?.[field]!==null) bad('fabricated visitor evidence '+i+':'+field);
    }
    if(r.derivative?.hard_max_width_px!==960||r.derivative?.no_upscale!==true||r.derivative?.requires_intrinsic_master_probe!==true||r.derivative?.preverified_960_derivative_dimensions!==null) bad('derivative gate '+i);
    const preview=r.archival.rendition_dims;
    if(preview!==null && (!Array.isArray(preview)||preview.length!==2||preview.some(x=>!Number.isInteger(x)||x<=0)||preview[0]>960)) bad('preview size '+i);
    if(r.derivative?.known_candidate_preview_dimensions===undefined||JSON.stringify(r.derivative.known_candidate_preview_dimensions)!==JSON.stringify(preview)) bad('preview provenance '+i);
    if(r.rights_gate?.rehost_authorized!==false||r.rights_gate?.wp_upload_authorized!==false||r.rights_gate?.requires_item_level_review!==true) bad('rights gate '+i);
  }
  if(audit.production_changes?.wp_writes!==0||audit.production_changes?.downloaded_or_rehosted_images!==0||audit.production_changes?.homepage_design_edits!==0||audit.production_changes?.cost_usd!==0) bad('production boundary');
  return {ok:errors.length===0,errors,source_blob_sha:EXACT_SOURCE_BLOB,slots_checked:Math.min(audit.rows.length,expected.length)};
}
module.exports={validate};
