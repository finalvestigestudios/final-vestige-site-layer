'use strict';
// Source-only, fail-closed guard. No network calls, CMS writes, or dependency installation.
function validate(d) {
  const errors=[];
  const bad=(condition,why)=>{if(condition)errors.push(why)};
  bad(!d||d.schema!=='fv.media.recovery.tmi_fig4.v1','schema');
  if(!d||!d.source_snapshot||!Array.isArray(d.investigated_slots)||!Array.isArray(d.candidates)||!d.release)return ['missing fields'];
  bad(d.source_snapshot.post_id!==285||d.source_snapshot.status!=='publish','post identity');
  bad(d.source_snapshot.modified!=='2026-11-02T21:39:59','source version');
  bad(d.source_snapshot.source_git_blob!=='49183f66f880f7c4dfd363acca906876877f2e5e','frozen evidence blob');
  const b=d.sitewide_baseline||{};
  bad(b.posts!==61||b.source_image_slots!==355||b.third_party_origin_slots!==288||b.wp_originals_above_1_5_mib!==13,'baseline');
  bad(b.reported_broken_42_visitor_confirmed!==false||b.claimed_76_percent_wire_saving_verified!==false,'unverified performance/failure claim');
  const srcs={'285:2':'https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg','285:5':'https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg'};
  bad(d.investigated_slots.length!==2||new Set(d.investigated_slots.map(x=>x.key)).size!==2,'slots count');
  for(const row of d.investigated_slots){
    bad(row.published_src!==srcs[row.key],'exact published source '+row.key);
    bad(!row.published_alt||!row.published_caption,'published editorial content '+row.key);
    bad(!row.retriever||row.retriever.numeric_origin_http_status!==null,'retriever not origin HTTP '+row.key);
    bad(!row.image_search||row.image_search.numeric_origin_http_status!==null,'image search not origin HTTP '+row.key);
    const g=row.guest_browser||{};
    for(const field of ['http_status','current_src','natural_width','decoded','encoded_transfer_bytes','screenshot','broken'])bad(g[field]!==null,'invented guest evidence '+row.key+':'+field);
    if(row.key==='285:2'){
      bad(row.retriever.result!=='redirect_wrapper_error_500','redirect wrapper is NOT origin 500');
      bad(row.retriever.final_declared_url!=='https://blog.ucs.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg','declared target');
      bad(row.image_search.result!=='same_exact_published_src_image_displayed','independent image display');
      bad(!/maintenance tags/.test(row.editorial_issue),'historical detail');
    }
    if(row.key==='285:5')bad(row.retriever.result!=='retriever_404_not_found','404 retrieval label');
  }
  bad(d.candidates.length!==2,'catalog count');
  for(const c of d.candidates){
    bad(!srcs[c.for_key]||!c.catalog_url||!c.source_record,'catalog provenance');
    bad(!Number.isInteger(c.intrinsic_width)||!Number.isInteger(c.intrinsic_height)||c.intrinsic_width<1||c.intrinsic_height<1,'original pixel geometry');
    bad(!Number.isInteger(c.proposed_width)||!Number.isInteger(c.proposed_height)||c.proposed_width>960||c.proposed_width>c.intrinsic_width||c.proposed_height>c.intrinsic_height||c.proposed_width<1||c.proposed_height<1,'960px/no-upscale');
    bad(Math.abs(c.proposed_width/c.proposed_height-c.intrinsic_width/c.intrinsic_height)>0.002,'aspect ratio');
    bad(c.pixel_crop_sha_match!==false||c.rights_item_verified_for_rehosting!==false||c.editorial_approved!==false||c.wp_upload_authorized!==false,'unauthorized identity/rights/cms release');
    bad(!c.creator_credit||!c.license_signal,'license/attribution');
    if(c.for_key==='285:2')bad(c.intrinsic_width!==604||c.intrinsic_height!==590||c.candidate_type!=='same_historical_plate_retouched_derivative_not_binary_match','retouch/catalog mismatch');
    if(c.for_key==='285:5')bad(c.intrinsic_width!==819||c.intrinsic_height!==614||c.candidate_type!=='publisher_linked_same_scene_uncropped_original_not_binary_match','publisher crop/catalog mismatch');
  }
  const alt=d.optional_nonidentical_backup||{};
  bad(alt.catalog_url!=='https://wwwn.cdc.gov/phil/Details.aspx?pid=1194'||!alt.subject.includes('not the publisher')||alt.editorial_approved!==false||alt.source_binary_identity_verified!==false,'CDC backup must remain nonidentical');
  bad(alt.conditional_derivative_width!==960||alt.conditional_derivative_height!==614||alt.commons_width!==2843||alt.commons_height!==1817,'CDC Commons geometry');
  const r=d.release;
  for(const key of ['requires_logged_out_browser_decode','requires_before_after_same_scene_crops','requires_item_specific_rights_signoff','requires_editorial_alt_caption_review','requires_wordpress_media_staging','requires_actual_cold_wire_transfer_measurement','all_caching_and_publication_on_hold'])bad(r[key]!==true,'release gate '+key);
  bad(r.production_changes_made!==false||r.repairs_confirmed!==0,'no production modifications');
  return errors;
}
module.exports={validate};
if(require.main===module){const fs=require('node:fs');const path=require('node:path');const file=process.argv[2]||path.join(__dirname,'tmi_285_fig4_upstream_20261103.json');const errors=validate(JSON.parse(fs.readFileSync(file,'utf8')));if(errors.length){console.error(errors.join('\n'));process.exitCode=1;}else console.log('PASS: TMI 285 primary-source and no-production gates');}
