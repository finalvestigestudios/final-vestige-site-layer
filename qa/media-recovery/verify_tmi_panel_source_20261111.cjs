'use strict';
function dimensionsAtMost(original, cap) {
 if(!Array.isArray(original)||original.length!==2||!original.every(n=>Number.isInteger(n)&&n>0)||!Number.isInteger(cap)||cap<1) return null;
 const w=Math.min(original[0],cap);
 return [w,Math.round(w*original[1]/original[0])];
}
function validate(r){
 const problems=[];const chk=(condition,code)=>{if(condition)problems.push(code)};
 chk(!r||r.schema!=='fv-tmi-panel-p0-lineage-v1','schema');
 if(!r)return {ok:false,problems};
 chk(!r.post||r.post.slot!=='285:2'||r.post.id!==285||r.post.published_src!=='https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg'||r.post.status!=='publish','published-original');
 chk(!r.observations||r.observations.web_retriever.method!=='WEB_OPEN_WRAPPER_NOT_GUEST_OR_ORIGIN'||r.observations.real_origin_http_status!==null||r.observations.confirmed_guest_broken!==false||r.observations.guest_cdp.http_status!==null||r.observations.guest_cdp.completed_cold_image_response!==null||r.observations.guest_cdp.encoded_transfer_bytes!==null,'unverified-http');
 chk(!r.provenance||r.provenance.ucs_figure!=='4'||r.provenance.printed_page!==97||r.provenance.pdf_zero_index_page!==27||r.provenance.strict_binary_identity_verified!==false||r.provenance.federal_report_scan_url!=='https://www.tmia.com/sites/tmia.com/files/media/Presidents-Commission.pdf','1979-primary-document');
 const c=r.candidates;
 chk(!Array.isArray(c)||c.length!==3||c.some(x=>x.cache_authorized!==false||x.pixel_identity_verified!==false),'candidate-hold');
 if(Array.isArray(c)&&c.length===3){
 chk(c[1].kind!=='PRIMARY_1979_FEDERAL_COMMISSION_REPORT'||c[1].printed_page!==97||c[1].pdf_zero_index_page!==27,'report-candidate');
 chk(c[2].kind!=='COMMONS_RETOUCHED_DERIVATIVE'||c[2].url!=='https://commons.wikimedia.org/wiki/File:TMI-2_control_panel.png'||c[2].retouched_revision!==true||JSON.stringify(c[2].native_px)!=='[604,590]'||JSON.stringify(c[2].conditional_960px)!=='[604,590]','commons-original');
 }
 chk(!r.size||r.size.ceiling_width_px!==960||r.size.no_upscale!==true||r.size.no_crop!==true||JSON.stringify(r.size.conditional_output_px)!==JSON.stringify(dimensionsAtMost([604,590],960))||r.size.retina_2x_max_css_width_px!==302,'no-upscale');
 chk(!r.editorial||r.editorial.distinct_failure_mechanisms!==true||r.editorial.editor_approved!==false||r.editorial.apply_to_wordpress!==false||!/emergency.feedwater/i.test(r.editorial.proposed_caption||'')||!/relief valve/i.test(r.editorial.proposed_caption||''),'image-subject-integrity');
 const d=r.decision;chk(!d||d.result!=='HOLD_REVIEW_ONLY'||['allow_binary_download','allow_cache','allow_wordpress_media','allow_wordpress_post_edit','allow_homepage_edit','allow_deploy','allow_merge'].some(k=>d[k]!==false)||d.subscription_spend_usd!==0,'no-production-authority');
 chk(!r.sitewide||r.sitewide.historical_posts!==61||r.sitewide.external_positions!==288||r.sitewide.reported_broken_guest_unconfirmed!==42||r.sitewide.measured_transfer_reduction_pct!==null||r.sitewide.proposed_reduction_pct!==76,'no-false-performance-claims');
 return {ok:problems.length===0,problems};
}
function reviewStage(r,e={}){
 const v=validate(r);if(!v.ok)return {decision:'INVALID_SOURCE',problems:v.problems};
 const missing=[];
 if(e.completed_cold_image_request!==true||e.http_status!==200||e.cache!=='EXPLICIT_UNCACHED'||!Number.isInteger(e.natural_width)||e.natural_width<=0||!Number.isInteger(e.natural_height)||e.natural_height<=0)missing.push('guest');
 if(e.visual_same_photo_review!==true)missing.push('visual');
 if(e.item_rights_clearance!==true)missing.push('rights');
 if(e.editor_approval!==true)missing.push('editor');
 return {decision:'HOLD_NO_PRODUCTION_WRITES',missing,ready_for_separate_staging_review:missing.length===0};
}
module.exports={dimensionsAtMost,validate,reviewStage};
