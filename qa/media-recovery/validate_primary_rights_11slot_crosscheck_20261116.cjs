'use strict';
/* Offline source/rights preflight. Never fetches third-party images or writes WordPress. */
const KEYS=['287:0','287:5','288:0','288:4','432:0','432:1','432:2','432:3','432:4','432:5','432:6'];
const validUrl=s=>typeof s==='string'&&s.startsWith('https://')&&!/[\s\\@]/.test(s);
function inspect(a) {
 const errors=[];
 const fail=s=>errors.push(s);
 if(!a||a.schema!=='fv-media-primary-rights-crosscheck-v1'||a.date!=='2026-11-16')return {ok:false,errors:['SCHEMA']};
 if(!Array.isArray(a.rows)||a.rows.length!==11)return {ok:false,errors:['ROW_COUNT']};
 if(JSON.stringify(a.rows.map(r=>r.key))!==JSON.stringify(KEYS))fail('KEY_DRIFT');
 if(JSON.stringify(a.scope?.posts)!=='[287,288,432]'||a.scope?.slots!==11||a.scope?.raw_image_slots!==19||a.scope?.florida_image_slots!==7||a.scope?.navy_image_slots!==2||a.scope?.skyway_related_slots!==2)fail('COHORT_DRIFT');
 if(a.release!=='HOLD'||a.reported_42_broken_confirmed!==false||a.claimed_76_percent_measured!==false||a.oversized_original_stored_bytes!==64385752||a.no_wordpress_writes!==true||a.no_media_downloads!==true||a.site_qa_owner!=='PR #154 cold logged-out Chromium collector only')fail('CLAIM_ESCALATION');
 if(a.rights_records?.florida_faq!=='https://floridamemory.com/share/order-info/faq.php'||!a.rights_records?.florida_policy?.includes('Public Domain Mark 1.0')||!a.rights_records?.florida_policy?.includes('257.35(6)')||!a.rights_records?.navy_photo_policy?.includes('history.navy.mil')||!a.rights_records?.skyway_caveat?.includes('not to publisher-hosted'))fail('RIGHTS_POLICY_DRIFT');
 const counts={};
 for(const r of a.rows) {
  if(!r||!Number.isSafeInteger(r.post_id)||!Number.isSafeInteger(r.slot)||r.key!==r.post_id+':'+r.slot){fail('BAD_KEY');continue;}
  counts[r.post_id]=(counts[r.post_id]||0)+1;
  if(!validUrl(r.post_url)||!validUrl(r.edit_url)||!validUrl(r.view_url)||typeof r.wp_modified!=='string'||r.wp_modified.length<19||r.alt_matches_edit!==true||!r.alt||!r.view_url.startsWith('https://i0.wp.com/'))fail('INVALID_SOURCE_FIDELITY');
  if(r.post_id===432&&(!r.edit_url.includes('floridamemory.com/')||r.source_class!=='florida-memory'||r.rights_policy!=='florida-memory-PDM-1.0-source-claim'))fail('FLORIDA_SCOPE');
  if(r.post_id===287&&(r.source_class!=='publisher-hosted-skyway'||r.rights_policy!=='current-publisher-image-rights-unknown; different-scene Florida candidate PDM source-claimed only'))fail('PUBLISHER_SCOPE');
  if(r.post_id===288&&(r.source_class!=='navy-or-ibiblio'||r.rights_policy!=='NHHC-photo-archive-most-public-domain-not-item-cleared'))fail('NAVY_SCOPE');
  if(r.rights_approval!=='HOLD'||r.visitor_failure_verified!==false||r.master_binary_dimensions_verified!==false||r.wordpress_caching_authorized!==false||r.upload_authorized!==false||r.published_post_rewrite_authorized!==false||r.guest_http_status!==null||r.guest_current_src!==null||r.guest_natural_width!==null||r.guest_transferred_bytes!==null||r.guest_decoded!==null)fail('UNAUTHORIZED_STATUS');
  const high=r.catalog_high_dimensions_px, g=r.conditional_960_px_from_catalog;
  if(high!==null){if(!Array.isArray(high)||high.length!==2||high.some(n=>!Number.isSafeInteger(n)||n<960)||!Array.isArray(g)||g[0]!==960||g[1]!==Math.round(high[1]*960/high[0]))fail('BAD_PREVIEW_GEOMETRY');}
  else if(g!==null)fail('INVENTED_GEOMETRY');
  if(r.authority_record_url!==null&&!validUrl(r.authority_record_url))fail('CATALOG_URL_INVALID');
 }
 if(counts[287]!==2||counts[288]!==2||counts[432]!==7)fail('POST_COUNTS');
 const by=Object.fromEntries(a.rows.map(r=>[r.key,r]));
 if(!by['288:0']?.authority_record_url?.includes('NH-69586.html')||!by['288:4']?.authority_record_url?.includes('NH-84822.html')||!by['432:3']?.authority_record_url?.endsWith('/141398')||!by['432:6']?.authority_record_url?.endsWith('/340182')||!by['287:0']?.authority_match?.startsWith('related different')||!by['287:5']?.authority_match?.startsWith('related different'))fail('ACCESSIONS');
 if(!by['288:4']?.caption_note?.includes('rescue operations')||!by['432:3']?.caption_note?.includes('disaster-response')||!by['432:6']?.caption_note?.includes('2001'))fail('CAPTION_CAVEATS');
 return {ok:errors.length===0,errors:[...new Set(errors)],rows_checked:a.rows.length,guest_http_verified:false,wordpress_writes:0,authorized_replacements:0,release:'HOLD'};
}
module.exports={inspect,KEYS};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const p=process.argv[2]||path.join(__dirname,'primary_rights_11slot_crosscheck_20261116.json');
 const r=inspect(JSON.parse(fs.readFileSync(p,'utf8')));
 process.stdout.write(JSON.stringify(r,null,2)+'\n');if(!r.ok)process.exitCode=1;
}
