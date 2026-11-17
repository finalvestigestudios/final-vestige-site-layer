'use strict';
// Source-only site-wide audit validation. No HTTP calls, binary fetches or CMS writes.
function family(u){
 if(u.includes('?fit='))return 'jetpack_wp_numeric_fit';
 if(u.includes('?resize='))return 'crop_capable_query_resize';
 if(u.includes('/crop/'))return 'crop_encoded_in_path';
 if(u.includes('?VersionId='))return 's3_object_version_selector';
 if(u.includes('?image=')&&u.includes('rendition='))return 'navy_dynamic_image_id';
 if(u.includes('?width=')&&u.includes('commons.wikimedia.org'))return 'commons_redirect_width';
 if(u.includes('?h=')&&u.includes('itok='))return 'drupal_h_hash_and_itok';
 if(u.includes('?itok='))return 'drupal_style_token';
 return 'other_query_or_dynamic_selector';
}
function validateTransformCensus(audit,parts){
 const errors=[],problem=x=>errors.push(x);
 const batches=Array.isArray(parts)?parts:[];
 const slots=batches.flatMap(x=>Array.isArray(x?.images)?x.images:[]);
 const posts=batches.flatMap(x=>Array.isArray(x?.posts)?x.posts:[]);
 const eligible=slots.filter(x=>typeof x.source_url==='string'&&x.source_url.includes('?'));
 const byKey=new Map(eligible.map(s=>[s.key,s])),rows=audit?.rows||[];
 if(batches.length!==8||posts.length!==61||slots.length!==355||eligible.length!==126||
    new Set(slots.map(x=>x.key)).size!==355)problem('frozen_source_cardinality_drift');
 if(audit?.frozen_inventory?.post_count!==61||audit?.frozen_inventory?.image_slots!==355||
    audit?.frozen_inventory?.query_bearing_slots!==126||
    audit?.frozen_inventory?.external_origin_ref_count!==288)problem('census_summary_invalid');
 if(audit?.schema!=='fv-query-transform-risk-census-v1')problem('schema_invalid');
 if(!Array.isArray(rows)||rows.length!==126)problem('query_row_count_invalid');
 const counts={},seen=new Set();
 for(const row of Array.isArray(rows)?rows:[]){
  const old=byKey.get(row?.image_key);
  if(!old||seen.has(row.image_key)||row.source_url!==old.source_url||
     row.post_id!==old.post_id||row.page_url!==old.post_url||
     row.source_kind!==old.source_kind)problem('source_identity_mismatch');
  if(row?.image_key)seen.add(row.image_key);
  const cat=family(old?.source_url||'');
  if(row.transform_family!==cat)problem('wrong_transform_family');
  counts[cat]=(counts[cat]||0)+1;
  if(row.http_status!==null||row.visitor_broken!==null||
    row.network_final_url!==null||row.decoded_width_px!==null||
    row.downloaded_bytes!==null||row.source_binary_inspected!==false)
     problem('fabricated_browser_or_binary_evidence');
  if(row.rights_clearance!=='HOLD_UNVERIFIED'||row.allowed_to_copy_or_cache!==false||
     row.approved_960px_derivative!==false||row.proposed_max_width_px!==960)
     problem('unauthorized_redistribution_or_dimensions');
 }
 if(seen.size!==eligible.length)problem('missing_or_extra_query_images');
 const expected={commons_redirect_width:92,crop_capable_query_resize:1,crop_encoded_in_path:1,
  drupal_h_hash_and_itok:1,drupal_style_token:3,jetpack_wp_numeric_fit:7,
  navy_dynamic_image_id:6,other_query_or_dynamic_selector:12,s3_object_version_selector:3};
 for(const [k,v]of Object.entries(expected))if(counts[k]!==v||audit?.category_counts?.[k]!==v)
   problem('category_drift:'+k);
 const rot=rows.find(x=>x.image_key==='292:1'),c=audit?.verified_subject_level_candidate;
 if(!rot||rot.transform_family!=='drupal_h_hash_and_itok'||!rot.source_url.includes('h=3e6ca723')||
    !c||c.image_key!=='292:1'||c.same_binary_verified!==false||
    c.wordpress_cache_upload_rewrite_authorized!==false||
    c.archival_photo_rights?.startsWith('HOLD')!==true||
    c.proposed_width_px!==960||c.proposed_height_px!==null)
    problem('rotterdam_rights_or_geometry_invalid');
 if(audit?.performance_claims?.reported_broken_42!=='UNVERIFIED'||
    audit?.performance_claims?.reported_76_percent_byte_savings!=='UNMEASURED'||
    audit?.performance_claims?.production_fixes!==0)
    problem('false_production_or_optimization_claim');
 if(!Array.isArray(audit?.source_part_blobs)||audit.source_part_blobs.length!==8||
    audit.source_part_blobs.some(x=>!/^([0-9a-f]{40})$/.test(x.blob_sha)))
    problem('missing_frozen_blob_pins');
 return {pass:errors.length===0,errors:[...new Set(errors)],counts,source_image_count:slots.length,query_image_count:eligible.length};
}
module.exports={validateTransformCensus};
