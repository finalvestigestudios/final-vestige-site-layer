'use strict';
/** Iroquois 283 visual-integrity recovery. Offline rights/HTTP fail closed; no source rewriting. */
const snapshot=require('./parts/03.json');
const identity=["283:0","283:1","283:2","283:3","283:4","283:5","283:6"],observations=["displayed_web_image_viewer","displayed_web_image_viewer","displayed_web_image_viewer","inaccessible_no_origin_http_code","displayed_web_image_viewer","displayed_web_image_viewer","displayed_web_image_viewer"];
const catalogIds=[null,"DN-0001578","ICHi-36010","DN-0001586",null,null,"ICHi-36009"];
function validate(x) {
 const errors=[],e=s=>errors.push(s);
 if(!x||typeof x!=='object'||Array.isArray(x))return ['invalid_data'];
 if(x.schema!=='fv.media-recovery.iroquois283.v1'||x.post_id!==283||
 x.source_inventory_blob_sha!=='49183f66f880f7c4dfd363acca906876877f2e5e'||x.external_source_count!==7||
 x.image_viewer_displayed_count!==6||x.image_viewer_inaccessible_count!==1)e('wrong_inventory_or_observation_totals');
 if(x.confirmed_browser_broken_count!==null||x.claimed_42_broken_verified!==false||
 x.claimed_76_percent_savings_measured!==false||x.production_image_repairs!==0||
 x.all_caching_hold!==true||x.editorial_correction_proposed_not_published!==true)e('unsupported_release');
 if(!Array.isArray(x.records)||x.records.length!==7)return [...new Set([...errors,'incorrect_number_of_rows'])];
 const originals=snapshot.images.filter(s=>s.post_id===283).sort((a,b)=>a.slot-b.slot),seen=new Set();
 for(let i=0;i<7;i++){
  const o=originals[i],r=x.records[i],v=r?.independent_viewer_observation,f=r?.visual_editorial_finding,
   c=r?.candidate,rights=r?.rights,opt=r?.optimization,st=r?.staging;
  if(!r||!o||r.key!==identity[i]||seen.has(r.key)||
   r.published_url!==o.source_url||r.published_alt!==o.alt||
   r.post_url!==o.post_url||r.source_snapshot_blob!=='49183f66f880f7c4dfd363acca906876877f2e5e')e('source_modified_'+i);
  if(r)seen.add(r.key);
  if(!v||v.method!=='web.open image viewer'||v.result!==observations[i]||
   v.status_code_reported_by_retriever!==null||v.origin_http_status!==null||
   v.logged_out_browser_status!==null||v.chrome_current_src!==null||
   v.decoded_width_px!==null||v.decoded_height_px!==null||v.transferred_bytes!==null)e('fabricated_network_'+i);
  if(!f||f.editorial_change_authorized!==false||
    f.visual_verified_in_independent_viewer!==(i!==3)||
    f.finding!==(i===0?'published_alt_describes_photo_but_source_is_mixed_illustrated_diagram':i===6?'caption_emphasizes_crowd_but_original_catalog_identifies_exterior_theatre_facade':'no_proven_factual_alt_mismatch')||
    (i===0&&!f.suggested_alt_subject_to_editor_review?.includes('Illustrated comparison')))e('caption_truth_gate_'+i);
  if(!c||c.catalog_id!==catalogIds[i]||!c.source_page?.startsWith('https://')||
    !c.match_type||c.relation.includes('exact_image_substitution_approved'))e('catalog_provenance_'+i);
  if(i===5&&c.relation!=='alternate_historical_after_fire_panorama_not_exact')e('LOC_not_same_scene_'+i);
  if(i===6&&c.creator_credit!=='Charles R. Clark (cataloged by Chicago History Museum)')e('CHM_credit_'+i);
  if(!rights||rights.copyright_clearance!=='HOLD'||rights.download_authorized!==false||
    rights.wordpress_upload_authorized!==false||rights.existing_publisher_display_not_republication_license!==true)e('rights_hold_'+i);
  if(!opt||opt.maximum_width_px!==960||opt.allow_upscale!==false||
    opt.current_original_dimensions_verified!==false||opt.candidate_archive_master_dimensions_verified!==false||
    opt.target_height_px!==null||opt.source_image_sha256!==null)e('made_up_dimensions_'+i);
  if(!st||Object.values(st).length!==6||Object.values(st).some(v=>v!==false))e('premature_publish_'+i);
 }
 return [...new Set(errors)];
}
module.exports={validate};
if(require.main===module){let e=validate(require('./iroquois_283_media_visual_integrity_20261102.json'));if(e.length){console.error(e);process.exitCode=1}else console.log('IROQUOIS283_PASS: 7 exact source URLs, one serious ALT finding; all rights HOLD');}
