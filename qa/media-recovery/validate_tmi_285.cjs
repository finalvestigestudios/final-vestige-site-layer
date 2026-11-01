'use strict';
// Node-only offline validation. No HTTP calls, no WordPress writes.
const EXPECTED = [{"key":"285:0","url":"https://live.staticflickr.com/7278/7447166686_5d24dff6db_b.jpg","alt":"Operators and technical staff inside the Three Mile Island Unit 2 control room during the 1979 accident."},{"key":"285:1","url":"https://i0.wp.com/www.squawkpoint.com/wp-content/uploads/2019/02/Three-Mile-Island-Control-Centre.jpg?ssl=1","alt":"Wide view of the densely instrumented Three Mile Island Unit 2 control room."},{"key":"285:2","url":"https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg","alt":"Three Mile Island control panel showing dense rows of gauges, lights and switches."},{"key":"285:3","url":"https://i.insider.com/5d5eb5f754c75f23dc72ed4c?auto=webp&format=jpeg&width=800","alt":"Technical personnel gathered inside the Three Mile Island control room during the 1979 accident response."},{"key":"285:4","url":"https://images.pixels.com/images-medium-large-5/three-mile-island-damaged-reactor-core-nuclear-regulatory-commissionscience-photo-library.jpg","alt":"Reconstruction of the severely damaged Three Mile Island Unit 2 reactor core after the partial meltdown."},{"key":"285:5","url":"https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg","alt":"Aerial view of the Three Mile Island nuclear generating station on the Susquehanna River."}];
function requireCondition(ok, msg){if(!ok) throw new Error(msg);}
function validateTmi285(d){
  requireCondition(d && d.schema_version===1 && d.post_id===285,'schema/post mismatch');
  requireCondition(d.source_count===6 && d.offsite_source_count===6 && Array.isArray(d.rows) && d.rows.length===6,'six-row census required');
  requireCondition(d.source_inventory_verified_current_cms===true,'CMS readback assertion missing');
  requireCondition(d.claimed_broken_42_verified===false && d.claimed_76pct_weight_reduction_measured===false,'unmeasured claim');
  requireCondition(d.claimed_sitewide_broken_count===null && d.measured_before_image_bytes===null && d.measured_after_image_bytes===null,'fabricated measured result');
  requireCondition(d.production_images_repaired===0,'unauthorized claimed repair');
  const seen=new Set();
  for(let i=0;i<6;i++){
    const r=d.rows[i], e=EXPECTED[i];
    requireCondition(r?.key===e.key && r.slot===i && r.post_id===285 && !seen.has(r.key),'slot/identity mismatch');
    seen.add(r.key);
    requireCondition(r.original_source_url===e.url && r.original_alt===e.alt,'published source/ALT mutated');
    requireCondition(r.source_html_width_px===null && r.source_html_height_px===null,'unverified stored geometry');
    const v=r.viewer, b=r.browser, c=r.candidate;
    requireCondition(v?.method==='web.run.open independent retriever 2026-11-01; not a guest browser','retriever method mismatch');
    requireCondition(v.result===['RETRIEVER_403_FORBIDDEN','IMAGE_RENDERED','REDIRECT_DESTINATION_INACCESSIBLE','IMAGE_RENDERED','IMAGE_RENDERED','RETRIEVER_404_NOT_FOUND'][i],'retriever observation mutated');
    requireCondition(v.retriever_error_code===[403,null,500,null,null,404][i],'retriever code mutated');
    requireCondition(v.origin_http_status===null && v.final_image_http_status===null && v.encoded_transfer_bytes===null && v.decoded_natural_width_px===null,'retriever result mislabeled as origin/browser HTTP');
    requireCondition(b?.logged_out_verified===false && b.current_src===null && b.status===null && b.content_type===null && b.natural_width_px===null && b.natural_height_px===null && b.encoded_transfer_bytes===null && b.failed_visible_screenshot===null,'unsupported guest browser proof');
    requireCondition(c?.rights_review==='HOLD' && c.wordpress_upload_authorized===false && c.wordpress_post_edit_authorized===false && c.visual_QA_complete===false && c.binary_identity_verified===false && c.master_sha256===null,'rights/visual/identity safety gate violated');
    requireCondition(c.no_upscale===true && c.preserve_aspect_ratio===true && c.candidate_width_cap_px===960,'no-upscale geometry policy');
    requireCondition(/^https:\/\//.test(c.record) && c.record.length>35 && typeof c.rights_note==='string' && c.rights_note.length>24 && typeof c.credit==='string','missing archival source/rights');
    requireCondition(['same-archive-ID','unmatched-original','same-subject-alternative','same-work-candidate','publisher-credit-candidate'].includes(c.kind),'candidate relationship unclassified');
    requireCondition(c.kind!=='unmatched-original' || c.conditional_max_dimensions===null,'unmatched photo got invented dimensions');
    const w=c.source_width_px, h=c.source_height_px, t=c.conditional_max_dimensions;
    if(w===null || h===null){requireCondition(w===null && h===null && t===null,'unknown dimensions must stay unknown');}
    else{
      const width=Math.min(w,960), height=Math.round(h*width/w);
      requireCondition(Number.isInteger(w)&&w>0&&Number.isInteger(h)&&h>0,'invalid original geometry');
      requireCondition(t?.width_px===width && t?.height_px===height,'incorrect 960px preserving-aspect calculation');
    }
  }
  return {ok:true,validated_slots:seen.size,retriever_not_browser:true,wp_writes_authorized:0};
}
module.exports={validateTmi285,EXPECTED};
if(require.main===module){
  const fs=require('node:fs'); const path=require('node:path');
  const file=process.argv[2]||path.join(__dirname,'tmi_285_nrc_recovery_20261101.json');
  const result=validateTmi285(JSON.parse(fs.readFileSync(file,'utf8')));
  process.stdout.write(JSON.stringify(result)+'\n');
}
