'use strict';
// Offline source/rights gate. Viewer wrapper status is never promoted to visitor HTTP.
const fs = require('node:fs');
const p = require('node:path');
const OLD='https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg';
const NEW='https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg';
const SHA='49183f66f880f7c4dfd363acca906876877f2e5e';
const NULL_BROWSER=['current_src','http_status','response_mime','natural_width_px','natural_height_px','encoded_image_bytes','visually_broken'];
function validate(a, source) {
 const errors=[]; const bad=(x)=>errors.push(x);
 if(a?.schema!=='fv.media_recovery.skyway_p0_migration.v1' || a?.article?.id!==287 || a?.article?.status!=='publish')bad('SCHEMA_OR_POST');
 if(a?.archived_inventory?.git_blob_sha!==SHA || a?.archived_inventory?.file!=='qa/media-recovery/parts/03.json')bad('ARCHIVE_PIN');
 const posts=(source?.posts||[]).filter(x=>x.id===287), imgs=(source?.images||[]).filter(x=>x.post_id===287);
 if(posts.length!==1 || a?.article?.url!==posts[0]?.url || imgs.length!==6 || a?.published_images?.length!==6 || a?.article?.wp_readonly_verified_6_of_6!==true)bad('ARTICLE_SOURCE_COUNT');
 const seen=new Set();
 for(const row of a?.published_images||[]) {
  if(seen.has(row.key))bad('DUPLICATE_KEY');seen.add(row.key);
  const orig=imgs.find(x=>x.key===row.key);
  if(!orig || orig.source_url!==row.published_src || orig.alt!==row.published_alt || orig.width_px!==row.cms_width_px || orig.height_px!==row.cms_height_px)bad('SOURCE_URL_ALT_DIMENSION_DRIFT');
  if(row.source_kind!=='external' || row.conditional_derivative_max_width_px!==960 || row.conditional_derivative_height_px!==null || row.source_intrinsic_width_px!==null || row.source_intrinsic_height_px!==null || row.same_binary_confirmed!==false)bad('UNVERIFIED_GEOMETRY');
  if(!row.visitor_browser || NULL_BROWSER.some(k=>row.visitor_browser[k]!==null))bad('FABRICATED_BROWSER_RESPONSE');
  if(row.wordpress_upload_approved!==false || !row.rights?.includes('NOT authorized'))bad('UNAUTHORIZED_PUBLICATION');
  if(row.viewer_method!=='web.open exact published URL' || row.viewer_evidence_url && row.viewer_evidence_url!==row.published_src)bad('VIEWER_URL');
  const isP0=row.key==='287:5';
  if(isP0 && (row.published_src!==OLD || row.viewer_result!=='RETRIEVER_404' || row.retriever_wrapper_status!==404 || !row.rights.includes('University Press of Florida')))bad('P0_OLD_URL_404');
  if(!isP0 && (row.viewer_result!=='DISPLAYED' || row.retriever_wrapper_status!==null))bad('SOURCE_VIEWER_OTHER_SLOTS');
 }
 const c=a?.migration_candidate;
 if(c?.key!=='287:5'||c?.old_url!==OLD||c?.new_url!==NEW||c?.publisher_article!=='https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/'||c?.publisher_photo_credit!=='University Press of Florida'||c?.new_url_viewer_result!=='DISPLAYED'||c?.same_filename_and_publisher!==true)bad('CANDIDATE_IDENTITY');
 if(c?.binary_identical_verified!==false||c?.rights_permission_verified!==false||c?.wp_rehost_authorized!==false||c?.wp_url_change_authorized!==false||c?.original_width_px!==null||c?.original_height_px!==null||c?.conditional_height_px!==null||c?.maximum_no_upscale_width_px!==960 || c?.decision!=='HOLD_FOR_GUEST_BROWSER_IMAGE_PROOF_AND_PHOTO_LICENSE')bad('RELEASE_OR_SIZE_GATES');
 if(!c?.alt_correction_proposed_not_published?.includes('surviving old steel truss'))bad('VISUAL_CHRONOLOGY');
 if(a?.site_metrics?.posts!==61||a?.site_metrics?.stored_slots!==355||a?.site_metrics?.oversize_wp_originals_over_1_5_mib!==13||a?.site_metrics?.claimed_broken_42_guest_verified!==false||a?.site_metrics?.claimed_76_percent_wire_reduction_measured!==false||a?.site_metrics?.confirmed_visitor_image_failures!==0||a?.site_metrics?.production_images_repaired!==0)bad('INVENTED_SITE_CLAIMS');
 if(a?.authoritative_archival_context_not_exact_replacements?.length!==2 || a.authoritative_archival_context_not_exact_replacements.some(x=>x.same_scene!==false||x.publishing_rights_verified!==false||x.max_no_upscale_width_px!==960))bad('ARCHIVE_DIFFERENT_SCENE');
 if(!a?.controls || Object.values(a.controls).some(x=>x!==true))bad('OPERATIONAL_BOUNDS');
 return {ok:errors.length===0,errors};
}
if(require.main===module){
 try{
  const a=JSON.parse(fs.readFileSync(process.argv[2]||p.join(__dirname,'skyway_287_p0_migration_20261103.json'),'utf8'));
  const s=JSON.parse(fs.readFileSync(process.argv[3]||p.join(__dirname,'parts','03.json'),'utf8'));
  const out=validate(a,s); console.log(JSON.stringify(out));process.exitCode=out.ok?0:1;
 }catch(e){console.error('NOT_VERIFIED',e.message);process.exitCode=1;}
}
module.exports={validate};
