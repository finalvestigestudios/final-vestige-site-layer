'use strict';
// Offline fail-closed validator; does not retrieve URLs or write to production.
const fs=require('node:fs');
const validateAudit=function validateAudit(x){
 const fail=m=>{throw new Error("HOLD: "+m)};
 if(!x || x.schema!=="fv-media-uscg-item-rights-and-name-conflict-v1") fail("schema");
 const w=x.wordpress,p=x.official_photo,n=x.official_name_conflict,b=x.baseline,g=x.release_gates,d=x.deployment;
 if(!w||w.post_id!==418||w.slot_index_zero_based!==1||w.post_status!=="publish"||w.modified!=="2026-08-28T03:11:08") fail("WordPress identity");
 if(!w.edit_src?.startsWith("https://media.defense.gov/")||!w.edit_src?.endsWith("/210330-G-DE713-0002.JPG")) fail("authored image URL");
 if(w.view_src!=="https://i0.wp.com/media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG?ssl=1") fail("view URL");
 if(w.alt!=="Chief Boatswain’s Mate Anthony L. Petit, officer in charge of Scotch Cap Lighthouse when the 1946 tsunami killed its five-man crew.") fail("authored alt");
 for(const k of ["guest_http_status","guest_current_src","guest_natural_width","guest_natural_height","guest_wire_bytes","guest_broken"]) if(w[k]!==null)fail("unverified guest browser assertion "+k);
 if(!p||p.agency!=="U.S. Coast Guard"||p.catalog_url!=="https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/"||p.photo_identifier!=="210330-G-DE713-0002.JPG"||!w.edit_src.endsWith("/"+p.photo_identifier)) fail("official item custody");
 if(p.public_domain_statement_present!==true||p.cleared_for_release_statement_present!==true||p.reuse_credit_required!=="U.S. Coast Guard"||p.photo_by!=="U.S. Coast Guard") fail("item rights evidence");
 if(p.dod_restrictions_url!=="https://www.dma.mil/Services/Visual-Information/References/Limitations/"||p.item_rights_status!=="official_item_public_domain_cleared_for_release_with_conditions") fail("restricted-use provenance");
 if(p.catalog_display_name!=="Anthony Pettit"||p.exact_pixel_identity_verified!==false||p.storage_cache_or_upload_approved!==false||p.wordpress_replacement_approved!==false)fail("unverified identity or unsafe release");
 if(p.item_native_width_px!==null||p.item_native_height_px!==null||p.review_derivative_width_px!==null||p.review_derivative_height_px!==null||p.permitted_review_max_width_px!==960||p.do_not_upscale!==true)fail("invented dimensions");
 if(!n||n.gallery_spelling!=="Pettit"||n.facility_history_spelling!=="Petit"||n.gallery_url!==p.catalog_url||!n.facility_history_url?.startsWith("https://www.history.uscg.mil/")||n.editorial_status!=="HOLD_CONFLICTING_PRIMARY_SOURCES_NO_AUTOCORRECTION"||n.long_blue_line_same_page_has_both_spellings!==true)fail("disputed name provenance");
 if(!Array.isArray(x.related_slots)||x.related_slots.length!==2||x.related_slots[0].slot!=="418:2"||x.related_slots[1].slot!=="418:5"||x.related_slots.some(r=>r.guest_http_status!==null||r.release!=="HOLD"))fail("adjacent P0 hold");
 if(!b||b.frozen_posts!==61||b.frozen_image_tags!==355||b.current_posts!==66||b.current_image_tags!==361||b.reported_broken_external!==42||b.guest_confirmed_broken!==null||b.claimed_weight_reduction_percent!==76||b.measured_wire_reduction_percent!==null||b.oversize_originals!==20||b.oversize_stored_bytes!==64385752)fail("baseline and unmeasured claims");
 if(!g||Object.values(g).length!==6||Object.values(g).some(v=>v!==false))fail("release gating");
 if(!d||d.new_binaries_downloaded!==0||d.wp_production_writes!==0||d.published_blocks_changed!==0||d.homepage_design_changed!==0||d.subscriptions_spent_usd!==0||d.pr_merge!==false||d.deploy!==false)fail("production safety");
 return {status:"PASS_OFFLINE_RIGHTS_CUSTODY_ONLY",slot:"418:1",image_identifier:p.photo_identifier,cleared_official_item_rights:true,approved_to_publish:false,guest_status:"NOT_MEASURED"};
};
if(require.main===module){try{const x=JSON.parse(fs.readFileSync(process.argv[2]||'','utf8'));console.log(JSON.stringify(validateAudit(x),null,2));}catch(e){console.error(e.message);process.exitCode=2;}}
module.exports={validateAudit};
