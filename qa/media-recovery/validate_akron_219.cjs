'use strict';
// Independent offline source/rights evidence gate; no network, file, or WP writes.
const IDs=["80-G-1009363","NH 43900","NH 98039","80-G-463185","NH 97977",null];
const WH=[[2650,2190],[5516,4241],[5482,4160],[740,581],[740,586],[590,765]];
const CATALOGS=["https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/aircraft-us/aircraft-usn-a/uss-akron-zrs-4/80-g-1009363.html","https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-43000/NH-43900.html","https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-98000/NH-98039.html","https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-460000/80-G-463185.html","https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97977.html","https://commons.wikimedia.org/wiki/File:Akron_kitchen.jpg"];
function validate(a, inventory) {
 const errors=[]; const bad=(m)=>errors.push(m);
 const src=(Array.isArray(inventory)?inventory:inventory&&inventory.images)||[];
 const refs=src.filter(x=>x.post_id===219).sort((x,y)=>x.slot-y.slot);
 if(refs.length!==6)bad('frozen_inventory_count');
 if(a?.schema_version!==1||a?.article?.id!==219||a?.article?.source_part!=='qa/media-recovery/parts/05.json'||a?.article?.source_blob_sha!=='9b16b828342a9ac338f3e65610fd3d8d508355e9')bad('frozen_context');
 if(a?.article?.current_wp_matches_frozen_src_and_alt!==6||a?.article?.modified!=='2026-10-29T15:54:20')bad('current_wp_readback');
 const s=a?.sitewide||{};
 if(s.published_posts!==61||s.stored_image_refs!==355||s.external_stored_refs!==288||s.large_wp_originals_over_1_5_mib!==13||s.claimed_42_broken_verified!==false||s.claimed_76_percent_transfer_reduction_measured!==false||s.actual_guest_broken_count!==null||s.actual_transfer_reduction_percent!==null||s.production_replacements!==0)bad('sitewide_no_invented_claim');
 const q=a?.probe_method||{}; if(q.guest_browser_run!==false||q.origin_http_checks_performed!==false)bad('browser_proof_missing');
 const t=a?.safety||{};if(t.wordpress_production_writes!==false||t.asset_downloads!==false||t.unlicensed_caching!==false||t.homepage_design_changes!==false||t.site_qa_code_changes!==false||t.subscription_spend_usd!==0)bad('side_effects');
 if(!Array.isArray(a?.images)||a.images.length!==6){bad('image_count');return errors;}
 for(let i=0;i<6;i++){
  const x=a.images[i],r=refs[i]; if(!r||x?.key!==r.key||x.post_id!==219||x.slot!==i||x.published_source_url!==r.source_url||x.published_alt!==r.alt||x.stored_source_kind!==r.source_kind)bad('source_identity_'+i);
  if(x.source_query_requested_width_px!==1280||x.authority?.catalog_number!==IDs[i]||x.authority?.catalog_url!==CATALOGS[i]||x.authority?.exact_binary_sha256!==null||x.authority?.same_photo_pixels_verified!==false||!x.authority?.commons_file_url?.startsWith('https://commons.wikimedia.org/wiki/File:'))bad('catalog_identity_'+i);
  const y=x.geometry||{},w=Math.min(960,WH[i][0]),h=Math.round(w*WH[i][1]/WH[i][0]);
  if(y.catalog_commons_original_width_px!==WH[i][0]||y.catalog_commons_original_height_px!==WH[i][1]||y.proposed_max_width_px!==w||y.proposed_height_px!==h||y.no_upscale!==true||y.requested_width_exceeds_original!==(WH[i][0]<1280)||y.visitor_encoded_bytes!==null)bad('safe_geometry_'+i);
  const rights=x.rights||{}; if(rights.commons_pd_statement_observed!==true||rights.individual_reuse_review_complete!==false||rights.independent_creator_rights_cleared!==false||rights.local_cache_authorized!==false||rights.wordpress_upload_authorized!==false)bad('rights_hold_'+i);
  const v=x.guest||{};for(const k of ['rendered_current_src','identity_proven','network_http_status','origin_http_status','content_type','natural_width_px','natural_height_px','transfer_bytes','visibly_broken'])if(v[k]!==null)bad('guest_unverified_'+i+'_'+k);
  const z=x.release||{};if(z.asset_downloaded!==false||z.wp_media_uploaded!==false||z.wp_post_edited!==false||z.live_media_repaired!==false)bad('no_production_change_'+i);
 }
 if(a.images[2].authority.creator_caution!=='official U.S. Army Air Corps, not proven U.S. Navy employee')bad('army_rights_mismatch');
 if(!a.images[5].authority.creator_caution.startsWith('unknown;'))bad('unknown_photographer');
 return errors;
}
module.exports={validate};
