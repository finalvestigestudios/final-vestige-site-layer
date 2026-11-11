"use strict";
const EXPECT={
 "285:5": {
  src:"https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg",
  id:"MTg5ODU1MTM1NjYzNDAwNjM2", commons:"https://upload.wikimedia.org/wikipedia/commons/0/09/Three_mile_island_062010.jpg"},
 "407:1": {
  src:"https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg",
  catalog:"https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0"}
};
function validatePrimaryVisualLineage(a){
 const errors=[];
 const fail=(msg)=>errors.push(msg);
 if(!a || typeof a!=="object") return {ok:false,errors:["missing audit"]};
 if(a.schema!=="fv-primary-visual-lineage-285-407-20261111-v1")fail("schema changed");
 if(!Array.isArray(a.items)||a.items.length!==2) return {ok:false,errors:["expected exactly two P0 items"]};
 if(a.history?.historical_posts!==61||a.history?.historical_inline_images!==355||a.history?.external_image_slots!==288)fail("historical baseline drift");
 if(a.history?.previously_reported_broken!==42||a.history?.guest_confirmed_broken!==0)fail("unsupported broken-image count");
 if(a.history?.measured_transfer_reduction_percent!==null||a.history?.proposed_transfer_reduction_percent!==76)fail("fabricated 76 percent measurement");
 if(a.history?.wp_originals_over_1500000_bytes!==15||a.history?.wp_original_stored_bytes!==47096779)fail("oversize storage baseline drift");
 if(a.immutable_source?.p0_bridge_blob!=="d1a9c7a499510ec37bcdba5858d45165752587e0")fail("source snapshot unpinned");
 const slots=new Set(a.items.map(x=>x.slot));
 if(slots.size!==2||!slots.has("285:5")||!slots.has("407:1"))fail("source slot roster changed");
 for(const item of a.items){
  const exp=EXPECT[item.slot];if(!exp){fail("unexpected slot");continue;}
  if(item.exact_published_src!==exp.src)fail(item.slot+" original URL changed");
  if(item.guest_http_status!==null||item.origin_http_status!==null||item.guest_current_src!==null||item.guest_wire_bytes!==null)fail(item.slot+" guest/origin evidence invented");
  if(item.upload_authorized!==false||item.caching_authorized!==false||item.post_rewrite_authorized!==false||item.replacement_visual_parity_approved!==false)fail(item.slot+" publication permission claimed");
  if(item.geometry?.automatic_crop_allowed!==false||item.geometry?.upscale_allowed!==false)fail(item.slot+" auto crop/upscale allowed");
  if(item.attribution?.publication_approval!==false)fail(item.slot+" editorial approval invented");
  if(item.slot==="285:5"){
   const e=item.evidence||{},g=item.geometry||{};
   if(e.publisher_media_identifier!==exp.id||!e.publisher_rendered_image_url?.includes("/.image/"+exp.id+"/")||!exp.src.includes(exp.id))fail("285:5 publisher asset ID lineage not established");
   if(e.publisher_links_public_domain_original!==exp.commons||e.catalog_url!=="https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg")fail("285:5 Commons license chain changed");
   if(e.strict_pixel_identity_proven!==false||e.original_published_retriever_method!=="EXTERNAL_WEB_RETRIEVER_NOT_GUEST")fail("285:5 retriever mistaken for binary/CDP");
   if(item.attribution.photographed_year!==2010||item.attribution.not_a_1979_accident_photo!==true||item.attribution.license_catalog!=="PUBLIC_DOMAIN_CREATOR_DEDICATION_PD_SELF")fail("285:5 TMI chronology/rights changed");
   if(JSON.stringify(g.catalog_original_native_px)!=="[819,614]"||JSON.stringify(g.conditional_no_upscale_px)!=="[819,614]"||g.full_frame_vs_published_crop_differs!==true||!g.published_transform?.includes("16:9"))fail("285:5 aspect/no-upscale/crop gate changed");
   if(item.decision!=="P0_SAME_SCENE_RIGHTS_LEAD_EDITOR_CROP_AND_BROWSER_HOLD")fail("285:5 release gate changed");
  }else{
   const e=item.evidence||{},g=item.geometry||{};
   if(e.primary_catalog_url!==exp.catalog||e.primary_catalog_original_link_url!==exp.src||e.original_link_exact_match_to_published_src!==true)fail("407:1 must exactly equal USGS official Original href");
   if(!e.alternate_primary_catalog_original_link_url?.includes("/thumbnails/image/img7535.jpg")||e.alternate_link_same_basename_not_binary_proof!==true)fail("407:1 alternate official path distinction lost");
   if(e.published_original_retriever_method!=="EXTERNAL_WEB_RETRIEVER_NOT_GUEST"||e.published_original_retriever_result!=="UNSUPPORTED_CONTENT_TYPE_BINARY_OCTET_STREAM"||e.image_binary_identity_sha256!==null)fail("407:1 unsupported binary treated as guest HTTP/hash");
   if(item.attribution.photographed_year!==1959||item.attribution.license_catalog!=="USGS_SOURCES_USAGE_PUBLIC_DOMAIN")fail("407:1 primary source provenance changed");
   if(g.published_original_native_px!==null||g.conditional_no_upscale_px!==null||g.alternate_rendered_copy_not_native_dimensions!==true)fail("407:1 thumbnail pixels invented as original");
   if(item.decision!=="P0_EXACT_USGS_SOURCE_URL_BROWSER_FIRST_NO_REHOST")fail("407:1 release gate changed");
  }
 }
 if(a.release?.actual_guest_failures_confirmed!==0||a.release?.wordpress_production_writes!==0||a.release?.source_candidate_assets_downloaded!==0||a.release?.merged_or_deployed!==false||a.release?.spend_usd!==0||a.release?.new_browser_collectors!==0)fail("production boundary changed");
 return {ok:errors.length===0,errors};
}
module.exports={validatePrimaryVisualLineage};
