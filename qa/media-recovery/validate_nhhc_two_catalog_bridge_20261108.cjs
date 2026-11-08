'use strict';
const fs = require('node:fs');
const path = require('node:path');
const auditFile = path.join(__dirname, 'nhhc_two_catalog_bridge_20261108.json');
const upstreamFile = path.join(__dirname, 'navy_8_live_pueblo_honda_retriever_20261108.json');
const expectedSlots = ['280:4', '288:2'];
const expectedIds = { '280:4': ['NH 68705','NH 68703','NH 68706'], '288:2': ['UG 21-01.02'] };
const allowedRelations = new Set(['SAME_SHIP_DIFFERENT_PHOTO_UNTIL_VISUAL_MATCH','CATALOG_PATH_MATCH_BINARY_UNVERIFIED']);
function inspect(audit, upstream) {
  const errors=[];
  const requireThat=(condition,msg)=>{if(!condition)errors.push(msg);};
  requireThat(audit?.schema==='fv-nhhc-two-unresolved-catalog-bridge-v1','schema');
  requireThat(Array.isArray(audit?.rows)&&audit.rows.length===2,'two_rows');
  requireThat(audit?.baseline?.historical_posts===61 && audit?.baseline?.historical_src_refs===355,'frozen_census');
  requireThat(audit?.baseline?.reported_broken_42_browser_verified===false && audit?.baseline?.reported_wire_reduction_76_measured===false,'unverified_historic_claims');
  requireThat(audit?.baseline?.large_wp_originals_gt_1500000_bytes===15 && audit?.baseline?.large_wp_original_stored_bytes===47096779,'stored_weight_only');
  requireThat(audit?.policy?.max_width===960 && audit.policy.upscale_permitted===false && audit.policy.image_rehosting_authorized===false && audit.policy.production_changes===0 && audit.policy.additional_spend_usd===0,'no_release_or_spend');
  const slots=(audit?.rows||[]).map(r=>r.slot);
  requireThat(JSON.stringify(slots)===JSON.stringify(expectedSlots),'exact_slot_order');
  for(const row of audit?.rows||[]) {
    const slot=row.slot;
    const prior=(upstream?.rows||[]).find(x=>x.slot===slot);
    requireThat(Boolean(prior),'upstream_row:'+slot);
    requireThat(prior?.published_source_url===row.published_src,'immutable_published_src:'+slot);
    requireThat(prior?.published_alt_snapshot===row.original_alt,'immutable_alt:'+slot);
    requireThat(prior?.post_id===row.post_id,'immutable_post_id:'+slot);
    requireThat(prior?.web_retriever?.result===row.original_retriever_result,'retriever_category:'+slot);
    requireThat(row.guest_browser_http===null && row.guest_current_src===null && row.guest_natural_dimensions===null && row.guest_transfer_bytes===null && row.guest_broken===null,'no_invented_guest_result:'+slot);
    requireThat(row.original_exact_photo_identity_proven===false,'no_exact_photo_claim:'+slot);
    requireThat(row.source_context?.url?.startsWith('https://www.history.navy.mil/'),'official_source_context:'+slot);
    const actualIds=(row.catalog_candidates||[]).map(c=>c.catalog_id);
    requireThat(JSON.stringify(actualIds)===JSON.stringify(expectedIds[slot]),'exact_catalog_candidate_ids:'+slot);
    for(const c of row.catalog_candidates||[]) {
      requireThat(c.url.startsWith('https://www.history.navy.mil/') && !c.url.includes('?'), 'official_url:'+slot);
      requireThat(allowedRelations.has(c.relationship),'explicit_nonidentical_photo_status:'+slot);
      requireThat(c.copyright_catalog_field==='Naval History and Heritage Command','archive_copyright_field_not_pd:'+slot);
      const d=c.master_tiff_dimensions_px;
      const x=c.conditional_max_960_px;
      requireThat(Array.isArray(d)&&d.length===2&&d.every(n=>Number.isSafeInteger(n)&&n>0),'master_dimensions:'+slot);
      requireThat(Array.isArray(x)&&x.length===2&&x.every(n=>Number.isSafeInteger(n)&&n>0),'conditional_dimensions:'+slot);
      if(Array.isArray(d)&&d.length===2&&d.every(n=>Number.isSafeInteger(n)&&n>0)&&Array.isArray(x)&&x.length===2) {
        const w=Math.min(960,d[0]);
        requireThat(x[0]===w && x[1]===Math.round(d[1]*w/d[0]),'proportional_no_upscale:'+slot);
      }
      requireThat(Number.isSafeInteger(c.catalog_medium_jpeg_kb)&&c.catalog_medium_jpeg_kb>0,'catalog_size_not_wire:'+slot);
    }
    const release=row.release||{};
    for(const flag of ['native_served_jpeg_dimensions_verified','same_exact_image_verified','item_reuse_cleared','editor_approved','download','cache','wordpress_media_write','wordpress_post_write']) requireThat(release[flag]===false,'must_hold_'+flag+':'+slot);
    requireThat(release.image_binary_sha256===null,'no_download_hash:'+slot);
  }
  return errors;
}
if(require.main===module) {
  const audit=JSON.parse(fs.readFileSync(auditFile,'utf8'));
  const upstream=JSON.parse(fs.readFileSync(upstreamFile,'utf8'));
  const errors=inspect(audit,upstream);
  console.log(JSON.stringify({status:errors.length?'HOLD_INVALID':'HOLD_VALID',rows:audit.rows.length,candidates:audit.rows.reduce((n,r)=>n+r.catalog_candidates.length,0),errors},null,2));
  process.exitCode=errors.length?1:0;
}
module.exports={inspect};
