'use strict';
/** Pure, offline, fail-closed Site QA -> Media Recovery staging gate.
 * No network, WordPress, binaries, uploads, post rewrites, or CI interaction.
 * qa is a manually normalized projection of existing Site QA #154 CDP evidence,
 * not a replacement for its collector. Evidence is NEVER self-authenticating.
 */
const HTTPS = /^https:\/\/[^\s?#/]+(?:\/[^\s#]*)?$/i;
const HEX = /^[a-f0-9]{64}$/;
const P0 = ['285:5', '285:2', '287:5', '418:1', '418:2', '407:1'];
const unique = a => new Set(a).size === a.length;
const validUrl = s => typeof s === 'string' && HTTPS.test(s) && !/[@\\]/.test(s);
const integer = v => Number.isSafeInteger(v) && v > 0;
const ratio960 = (w, h) => {
  if (!integer(w) || !integer(h)) return null;
  const width = Math.min(960, w);
  return { width, height: Math.max(1, Math.round(h * width / w)), no_upscale: true };
};
const hold = (key, reasons, geometry=null) => ({key, decision:'HOLD', reasons:[...new Set(reasons)], review_geometry: geometry, wordpress_action:'NONE'});
function evaluate(manifest, qa=null, approvals=null) {
  if (!manifest || manifest.schema !== 'fv-media-p0-staging-custody-v1' ||
      !Array.isArray(manifest.slots) || manifest.slots.length !== P0.length ||
      !unique(manifest.slots.map(x => x.key)) ||
      manifest.slots.some((x,i)=>x.key!==P0[i] || !validUrl(x.post_url) ||
        !validUrl(x.authored_url) || !validUrl(x.rendered_url) ||
        !Number.isFinite(Date.parse(x.wp_modified||'')) ||
        x.guest_http_status!==null || x.guest_decoded!==null ||
        x.guest_current_src!==null || x.cached_to_wordpress!==false ||
        x.max_width!==960 || x.rights_release_status!=='HOLD')) {
    return {ok:false,error:'INVALID_PINNED_SOURCE_MANIFEST',results:[]};
  }
  const qaRows = Array.isArray(qa?.slots) ? qa.slots : [];
  const appRows = Array.isArray(approvals?.slots) ? approvals.slots : [];
  if (qaRows.some(x=>!P0.includes(x.key)) || !unique(qaRows.map(x=>x.key)) ||
      appRows.some(x=>!P0.includes(x.key)) || !unique(appRows.map(x=>x.key)))
    return {ok:false,error:'DUPLICATE_OR_UNKNOWN_SLOT_EVIDENCE',results:[]};
  const guest = new Map(qaRows.map(x=>[x.key,x]));
  const signoffs = new Map(appRows.map(x=>[x.key,x]));
  const results = manifest.slots.map(s=>{
    const reasons = [], q=guest.get(s.key), a=signoffs.get(s.key);
    if (!q) reasons.push('MISSING_SITE_QA_COLD_GUEST_CAPTURE');
    else {
      if (qa.schema!=='fv-siteqa-p0-cold-projection-v1' ||
          qa.collector_owner!=='site-qa-pr-154' || q.capture_origin!=='logged-out-cold-chromium' ||
          q.synthetic!==false || q.post_url!==s.post_url || q.wp_modified!==s.wp_modified ||
          q.authored_url!==s.authored_url || q.rendered_url!==s.rendered_url ||
          !validUrl(q.current_src) || q.current_src!==s.rendered_url || !validUrl(q.final_url) ||
          !Array.isArray(q.redirect_chain) || !q.redirect_chain.length ||
          q.redirect_chain[0]!==q.current_src || q.redirect_chain[q.redirect_chain.length-1]!==q.final_url ||
          q.redirect_chain.some(u=>!validUrl(u)) ||
          !integer(q.image_request_count) || !Number.isSafeInteger(q.transferred_bytes) ||
          q.transferred_bytes<0 || !q.screenshot_ref ||
          typeof q.screenshot_ref !== 'string' || !q.visual_review_ref ||
          typeof q.visual_review_ref!=='string') reasons.push('GUEST_CAPTURE_INCOMPLETE_OR_STALE');
      if (!Number.isSafeInteger(q.http_status) || q.http_status<100 || q.http_status>599 ||
          !['image/jpeg','image/png','image/webp','image/avif','text/html','application/octet-stream'].includes(q.content_type))
        reasons.push('HTTP_MIME_NOT_GROUNDED');
      if (q.failed_decode!==true || q.natural_width!==0 || q.visibly_broken!==true ||
          (q.http_status>=200 && q.http_status<300 && q.content_type.startsWith('image/') && q.decode_error!=='yes'))
        reasons.push('VISITOR_FAILURE_NOT_PROVEN');
    }
    if (!s.candidate || !validUrl(s.candidate.catalog_url) || !validUrl(s.candidate.asset_url))
      reasons.push('NO_IDENTIFIED_REPLACEMENT_BINARY');
    if (!a) reasons.push('MISSING_ITEM_RIGHTS_AND_EDITORIAL_SIGNOFF');
    else {
      if (approvals.schema!=='fv-media-repair-approvals-v1' || a.key!==s.key ||
          a.current_wp_modified!==s.wp_modified || a.candidate_asset_url!==s.candidate?.asset_url ||
          a.rights_item_record!==s.candidate?.catalog_url || !validUrl(a.rights_item_record) ||
          !['official-public-domain-item','item-specific-written-license'].includes(a.rights_basis) ||
          a.rights_reviewer_approved!==true || a.attribution_approved!==true ||
          a.exact_visual_frame_verified!==true || a.cropped_comparison_reviewed!==true ||
          a.editorial_signoff!==true || a.rehosting_authorized!==true ||
          a.repair_scope==='homepage' || a.block_rewrite_requested===true ||
          typeof a.asset_sha256!=='string' || !HEX.test(a.asset_sha256) ||
          !integer(a.native_width) || !integer(a.native_height) ||
          a.evidence_source!=='reviewed-original-binary' || typeof a.credit_text!=='string' || a.credit_text.trim().length<4)
        reasons.push('REPLACEMENT_IDENTITY_RIGHTS_OR_SCOPE_NOT_CLEARED');
    }
    const geometry = a && integer(a.native_width) && integer(a.native_height)
      ? ratio960(a.native_width,a.native_height) : null;
    if (reasons.length) return hold(s.key,reasons,geometry);
    return {
      key:s.key, decision:'STAGING_REVIEW_ONLY', wordpress_action:'NONE',
      post_url:s.post_url, wp_revision_pin:s.wp_modified,
      existing_authored_url:s.authored_url, existing_rendered_url:s.rendered_url,
      candidate_asset_url:s.candidate.asset_url,
      approved_credit:a.credit_text, verified_asset_sha256:a.asset_sha256,
      review_geometry:geometry,
      requirements_before_any_write:['Human editor confirms exact image/caption fidelity','Stage WordPress Media in isolated review environment','Preserve existing post block markup and rollback reference','Independent 360px and 1440px guest screenshot/decode/CLS review','Explicit separate production authorization']
    };
  });
  return {ok:true,schema:'fv-media-p0-staging-results-v1',visitor_broken_confirmed:null,staging_review_candidates:results.filter(r=>r.decision==='STAGING_REVIEW_ONLY').length,
    wordpress_writes:0,media_downloads:0,measured_savings_percent:null,results};
}
module.exports={evaluate,ratio960,P0};
if (require.main===module){
  const fs=require('node:fs');
  const [m,q,a]=process.argv.slice(2);
  if (!m) {console.error('Usage: node assess_p0_image_staging_20261116.cjs manifest.json [siteqa-projection.json] [approval.json]');process.exitCode=2;}
  else {const read=p=>p?JSON.parse(fs.readFileSync(p,'utf8')):null;
    const result=evaluate(read(m),read(q),read(a));console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1;}
}
