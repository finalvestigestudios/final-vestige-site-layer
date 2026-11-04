'use strict';
/** Source/rights fail-closed guard for the 2026-11-04 TMI 285 recovery audit.
 * Offline only. No HTTP, WordPress writes, binary downloads, or browser claims.
 */
const EXPECTED_BLOB = '49183f66f880f7c4dfd363acca906876877f2e5e';
const REQUIRE_NULL = ['guest_browser_http_status','guest_browser_current_src','guest_browser_natural_width','guest_browser_decode_ok','cold_cdp_transfer_bytes','confirmed_broken_for_visitors'];
function unproxy(s) {
  let raw = s.replaceAll('&#038;','&').replaceAll('&amp;','&');
  raw = raw.replace(/^https:\/\/i[012]\.wp\.com\//,'https://');
  raw = raw.replace(/([?&])ssl=1$/, '');
  try { return decodeURIComponent(raw); } catch { return raw; }
}
function validate(a,part) {
  const errors=[];
  const err = (msg)=>errors.push(msg);
  if(a.schema!=='fv.media-recovery.tmi-285.v1'||a.post_id!==285||!a.cms_read_only||a.posts_images_count!==6)err('metadata');
  if(a.frozen_inventory_blob_sha!==EXPECTED_BLOB||!a.frozen_inventory_20261030)err('inventory pin');
  if(a.live_source_and_alt_match_count!==6||a.live_missing_html_dimension_pairs!==6)err('cms metrics');
  if(!Array.isArray(part.images)||!Array.isArray(a.source_checks)||a.source_checks.length!==6) {err('cohort');return errors;}
  const original=part.images.filter(x=>x.post_id===285);
  if(original.length!==6||new Set(original.map(x=>x.key)).size!==6)err('original cohort');
  for(let i=0;i<6;i++){
    const row=a.source_checks[i], ref=original[i];
    if(!row||!ref) {err('missing '+i); continue;}
    if(row.slot_key!==ref.key||row.source_url_frozen!==ref.source_url||row.alt_live!==ref.alt||!row.source_identity_matches_frozen)err('source/alt '+i);
    const normalized=unproxy(row.published_html_src||'');
    if(normalized!==decodeURIComponent(ref.source_url)&&row.published_html_src!==ref.source_url)err('live src '+i);
    if(row.has_width_height_pair!==false)err('dimension evidence '+i);
    if(REQUIRE_NULL.some(k=>row[k]!==null))err('invented browser evidence '+i);
    if(row.rights_to_rehost_approved!==false||row.production_change_approved!==false)err('unauthorized image '+i);
    const o=row.web_retriever;
    if(!o||!['tool_error','tool_error_redirect','rendered_image'].includes(o.result)||typeof o.method!=='string'||typeof o.detail!=='string'||typeof o.ref!=='string')err('tool provenance '+i);
    if(o&&(o.result==='rendered_image'?o.retriever_error_code!==null:![403,404,500].includes(o.retriever_error_code)))err('tool status semantics '+i);
  }
  if(!Array.isArray(a.candidates)||a.candidates.length!==4)err('candidate cohort');
  else for(let i=0;i<a.candidates.length;i++){
    const c=a.candidates[i], row=a.source_checks.find(x=>x.slot_key===c.for_slot);
    if(!row||!Number.isInteger(c.source_width)||!Number.isInteger(c.source_height)||!Number.isInteger(c.max_recommended_width)||!Number.isInteger(c.max_recommended_height))err('candidate geometry '+i);
    else if(c.max_recommended_width>960||c.max_recommended_width>c.source_width||c.max_recommended_height>c.source_height||c.max_recommended_width<=0||c.max_recommended_height<=0||Math.abs(c.max_recommended_width/c.max_recommended_height-c.source_width/c.source_height)>0.004)err('upscale/ratio '+i);
    if(!c.catalog_url?.startsWith('https://commons.wikimedia.org/wiki/File:')||!c.rights_review||!c.reported_rights||!c.description||c.approved!==false||c.historical_relation==='exact_same_photo_verified')err('rights/provenance '+i);
  }
  const p=a.candidate_rules;
  if(!p||p.max_width!==960||p.never_upscale!==true||p.preserve_subject_or_explicitly_relabel!==true||p.one_to_one_image_copy_forbidden_without_item_rights_review!==true||p.wordpress_uploads_approved!==false||p.wordpress_edits_approved!==false||p.cdn_cache_approved!==false||p.subscription_spend_approved!==false)err('release gate');
  if(a.site_baseline?.posts!==61||a.site_baseline?.stored_image_slots!==355||a.site_baseline?.external_source_slots!==288||a.site_baseline?.oversized_wordpress_originals!==13||a.site_baseline?.visitor_broken_verified!==0||a.site_baseline?.cold_cdp_reduction_measured!==false)err('claims');
  return errors;
}
module.exports={validate,unproxy};
if(require.main===module){
  const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
  const dir=__dirname;
  const raw=fs.readFileSync(path.join(dir,'parts','03.json'));
  const blob=crypto.createHash('sha1').update('blob '+raw.length+'\0').update(raw).digest('hex');
  if(blob!==EXPECTED_BLOB) {console.error('FAIL: source Git blob hash drift '+blob);process.exit(1);}
  const audit=JSON.parse(fs.readFileSync(path.join(dir,'tmi_285_p0_live_wp_source_custody_20261104.json'),'utf8'));
  const errors=validate(audit,JSON.parse(raw.toString('utf8')));
  if(errors.length){console.error('FAIL:',errors.join('; '));process.exit(1);}
  console.log('PASS: six TMI images/rights/retriever statuses reconciled, browser claims null');
}
