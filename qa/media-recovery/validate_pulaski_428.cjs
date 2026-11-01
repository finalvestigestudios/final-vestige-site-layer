'use strict';
// Read-only, fail-closed Pulaski/Big Burn six-image provenance validator.
// Usage: node qa/media-recovery/validate_pulaski_428.cjs
const EXPECTED=[
 ["428:0","pic_2014-09-30_005143b","https://www.lib.uidaho.edu/digital/archivalidaho/items/archivalidaho432.html","https://objects.lib.uidaho.edu/archivalidaho/archivalidaho432.jpg","RETRIEVER_INACCESSIBLE_NO_HTTP_STATUS","PDM_1_0_CATALOG_WITH_OTHER_HOLDING_INSTITUTION"],
 ["428:1","8-B498b","https://www.lib.uidaho.edu/digital/bigburn/items/bigburn23.html","https://objects.lib.uidaho.edu/bigburn/bigburn23.jpg","RETRIEVER_IMAGE_DISPLAYED","PDM_1_0_CATALOG"],
 ["428:2","8-C05b","https://www.lib.uidaho.edu/digital/bigburn/items/bigburn38.html","https://objects.lib.uidaho.edu/bigburn/bigburn38.jpg","RETRIEVER_IMAGE_DISPLAYED","PDM_1_0_CATALOG"],
 ["428:3","8-X90","https://www.lib.uidaho.edu/digital/bigburn/items/bigburn10.html","https://objects.lib.uidaho.edu/bigburn/bigburn10.jpg","RETRIEVER_IMAGE_DISPLAYED","PDM_1_0_CATALOG"],
 ["428:4","8-X545e","https://www.lib.uidaho.edu/digital/bigburn/items/bigburn18.html","https://objects.lib.uidaho.edu/bigburn/bigburn18.jpg","RETRIEVER_IMAGE_DISPLAYED","PDM_1_0_CATALOG"],
 ["428:5","sanborn01687_005","https://www.loc.gov/item/sanborn01687_005/","https://www.loc.gov/resource/g4274wm.g016871905/","RETRIEVER_IMAGE_DISPLAYED","1905_US_WORK_COMPOSITE_PUBLIC_DOMAIN_CANDIDATE_RIGHTS_REVIEW"],
];
function validate(manifest,census){
 const errors=[];
 const fail=(code)=>errors.push(code);
 if(manifest?.schema_version!==1)fail('schema');
 if(manifest?.post?.id!==428||manifest.post.status!=='publish'||manifest.post.live_cms_img_count!==6||manifest.post.matched_frozen_exact_src_alt!==true)fail('post');
 if(manifest?.sitewide?.published_posts!==61||manifest.sitewide.stored_image_refs!==355||manifest.sitewide.offsite_stored_refs!==288||manifest.sitewide.wordpress_originals_exceeding_1_5_mib!==13)fail('census');
 if(manifest?.sitewide?.reported_broken_42_browser_verified!==false||manifest.sitewide.reported_reduction_76_percent_measured!==false||manifest.sitewide.production_images_repaired!==0)fail('unsupported_claim');
 const original=Array.isArray(census?.images)?census.images.filter(x=>x.post_id===428).sort((a,b)=>a.slot-b.slot):[];
 if(original.length!==6||!Array.isArray(manifest?.rows)||manifest.rows.length!==6){fail('row_count');return errors}
 const seen=new Set();
 manifest.rows.forEach((r,i)=>{
  const f=original[i],ex=EXPECTED[i],c=r?.candidate||{},rt=r?.retrieval||{},g=r?.geometry||{},v=r?.guest_browser||{},rights=r?.rights||{},rel=r?.release||{};
  if(r?.key!==ex[0]||r?.post_id!==428||r?.slot!==i||seen.has(r?.key))fail('key_'+i);
  seen.add(r?.key);
  if(r?.published_source_url!==f?.source_url||r?.published_alt!==f?.alt||r?.live_cms_source_and_alt_verified!==true)fail('source_alt_'+i);
  if(c?.catalog_id!==ex[1]||c?.archive_record_url!==ex[2]||c?.candidate_asset_url!==ex[3])fail('archival_id_'+i);
  if((i>=1&&i<=4)&&c.candidate_asset_url!==r.published_source_url)fail('unjustified_substitution_'+i);
  if(c.master_binary_sha256!==null||c.confirmed_same_binary!==false)fail('fabricated_binary_identity_'+i);
  if(rt.method!=='independent_web_image_retriever_NOT_logged_out_Chrome'||rt.result!==ex[4]||rt.origin_http_status!==null||rt.visitor_http_status!==null||rt.content_type!==null||rt.transferred_bytes!==null)fail('fabricated_http_'+i);
  if(rights.archive_rights_signal!==ex[5]||rights.item_level_reuse_review!=='HOLD'||rights.cache_reproduction_permission!=='HOLD'||!rights.credit?.includes(ex[1]))fail('rights_'+i);
  if(g.master_width_px!==null||g.master_height_px!==null||g.proposed_width_px!==null||g.proposed_height_px!==null||g.max_width_px!==960||g.no_upscale!==true||g.aspect_preserved!==true)fail('geometry_'+i);
  for(const key of ['page_current_src','natural_width_px','natural_height_px','network_http_status','final_mime','actual_encoded_transfer_bytes','visibly_broken','screenshot_evidence_url'])if(v[key]!==null)fail('fabricated_browser_'+i+'_'+key);
  if(rel.stage_ready!==false||rel.wordpress_media_upload_authorized!==false||rel.wordpress_post_edit_authorized!==false||rel.production_repaired!==false)fail('release_'+i);
  if(i===0){
   const wp=r?.wordpress_media_proof||{},px=wp.wordpress_original_dimensions_px||{},safe=wp.no_upscale_maximum_for_present_wordpress_media_px||{};
   if(wp.method!=='authenticated_wordpress_media_list_read_only'||wp.media_id!==476||wp.post_id!==428||wp.original_url!==r.published_source_url||wp.mime_type!=='image/jpeg'||px.width!==623||px.height!==900||wp.wordpress_original_storage_bytes!==90157||safe.width!==623||safe.height!==900||wp.actual_guest_transfer_bytes!==null||!wp.recorded_jetpack_full_url?.startsWith('https://i0.wp.com/'))fail('wordpress_media_0');
  }
  if(i===4&&r?.visual_integrity?.review_required!==true)fail('editorial_integrity_'+i);
 });
 return errors;
}
module.exports={validate,EXPECTED};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const dir=__dirname;
 const audit=JSON.parse(fs.readFileSync(path.join(dir,'pulaski_428_idaho_loc_20261101.json'),'utf8'));
 const census=JSON.parse(fs.readFileSync(path.join(dir,'parts','01.json'),'utf8'));
 const failures=validate(audit,census);
 if(failures.length){console.error('PULASKI_428_REVIEW_FAIL',failures);process.exitCode=1;}
 else console.log('PULASKI_428_REVIEW_PASS: 6 exact source slots, rights and browser-status gates closed');
}
