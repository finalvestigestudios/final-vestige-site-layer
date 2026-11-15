'use strict';
/** Offline fail-closed archival follow-up validator. No requests or mutations. */
const PINS=Object.freeze({
 "285:2":"https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg",
 "418:2":"https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg",
 "287:5":"https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg"
});
const CATALOG=Object.freeze({
 "285:2":"https://commons.wikimedia.org/wiki/File:TMI-2_control_panel.png",
 "418:2":"https://www.history.uscg.mil/Research/THE-LONG-BLUE-LINE/Article/2866442/the-long-blue-line-standing-a-deadly-watch-75-years-agofinal-hours-of-scotch-ca/",
 "287:5":"https://www.floridamemory.com/items/show/131305"
});
function validate(a) {
 const e=[], bad=(x)=>e.push(x);
 if(!a||a.schema!=='fv-media-p0-three-primary-followup-v1')return {ok:false,errors:['SCHEMA']};
 if(a.frozen_historical_cohort?.published_posts!==61||a.frozen_historical_cohort?.external_images!==288||a.frozen_historical_cohort?.inline_images!==355)bad('HISTORICAL_COHORT');
 if(a.frozen_historical_cohort?.reported_broken_unverified!==42||a.frozen_historical_cohort?.guest_confirmed_broken!==0)bad('BROKEN_CLAIM');
 if(a.expanded_performance_cohort?.published_posts!==66||a.expanded_performance_cohort?.inline_images!==361||a.expanded_performance_cohort?.oversized_originals_gt_1500000_decimal_bytes!==15||a.expanded_performance_cohort?.oversized_stored_bytes!==47096779)bad('PERFORMANCE_COHORT');
 if(a.expanded_performance_cohort?.measured_wire_saving_percent!==null||a.expanded_performance_cohort?.previously_proposed_percent!==76)bad('UNMEASURED_WIRE_CLAIM');
 if(!Array.isArray(a.rows)||a.rows.length!==3)return {ok:false,errors:e.concat('ROW_COUNT')};
 if(new Set(a.rows.map(r=>r.slot)).size!==3)bad('DUPLICATE_SLOT');
 for(const r of a.rows) {
  if(!Object.hasOwn(PINS,r.slot)||r.published_original_src!==PINS[r.slot]||r.post_id!==Number(r.slot.split(':')[0])){bad('SOURCE_SLOT:'+r.slot);continue;}
  if(r.origin_http_status!==null||r.guest_http_status!==null||r.guest_encoded_bytes!==null||r.selected_current_src!==null)bad('FAKE_BROWSER_STATUS:'+r.slot);
  if(!r.prior_retriever_only||!['NOT_FOUND','FORBIDDEN','REDIRECT_TARGET_INACCESSIBLE'].includes(r.prior_retriever_only.outcome))bad('RETRIEVER_CONFLATION:'+r.slot);
  if(!Array.isArray(r.candidates)||r.candidates.length!==1){bad('CANDIDATE_COUNT:'+r.slot);continue;}
  const c=r.candidates[0];
  if(c.catalog_url!==CATALOG[r.slot]||c.rights_evidence_url!==CATALOG[r.slot])bad('CATALOG_IDENTITY:'+r.slot);
  if(c.identical_to_published_src_proven!==false||c.commercial_reuse_cleared!==false||c.word_press_cache_approved!==false)bad('UNAUTHORIZED_CLEARANCE:'+r.slot);
  if(!c.scene||!c.source_authority||!c.rights_evidence||!c.creator_credit)bad('PROVENANCE_MISSING:'+r.slot);
  const dims=c.native_pixels_catalog,out=c.conditional_960_px_full_frame;
  if(dims===null){if(out!==null)bad('UNVERIFIED_DIMENSIONS:'+r.slot);}
  else if(!Array.isArray(dims)||dims.length!==2||!dims.every(x=>Number.isSafeInteger(x)&&x>0)||!Array.isArray(out)||out.length!==2||out[0]!==Math.min(960,dims[0])||out[1]!==Math.round(dims[1]*out[0]/dims[0]))bad('CROP_UPSCALE:'+r.slot);
  if(r.slot==='285:2'&&(dims?.[0]!==604||dims?.[1]!==590||c.retouched_derivative!==true||c.historical_date!=='1979-10'))bad('TMI_PANEL_SCENE_VERSION');
  if(r.slot==='287:5'&&(c.catalog_id!=='K893521'||c.creator_credit!=='Robert M. Overton'||c.historical_date!=='1989'||dims!==null))bad('SKYWAY_DATE_CREATOR');
  if(r.slot==='418:2'&&(c.historical_date!=='1946-04'||dims!==null||!r.issue.includes('bluff')||!r.issue.includes('aerial')))bad('SCOTCH_CAP_SCENE_PARITY');
 }
 const x=a.release||{};
 if(x.guest_browser_confirmed_failures_in_this_batch!==0||x.download_binaries!==0||x.wordpress_production_writes!==0||x.theme_or_homepage_edits!==0||x.cached_assets!==0||x.published_block_rewrites!==0||x.spend_usd!==0||x.staging_authorized!==false||x.production_authorized!==false)bad('RELEASE_BOUNDARY');
 if(a.workflow?.guest_qa_owner!=='Site QA PR #154'||JSON.stringify(a.workflow?.priority_order)!==JSON.stringify(['285:5','285:2','287:5','418:1','418:2','407:1']))bad('QA_HANDOFF');
 return {ok:e.length===0,errors:e};
}
module.exports={validate,PINS,CATALOG};
