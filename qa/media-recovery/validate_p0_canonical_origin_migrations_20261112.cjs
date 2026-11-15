'use strict';
/* Offline only. The six frozen URLs and exact absence of genuine browser evidence are deliberate. */
function validateP0CanonicalBridge(a){
 const slots=["285:5","285:2","287:5","418:1","418:2","407:1"];
 if(!a||a.schema!=="fv-media-recovery-six-p0-canonical-source-paths-20261112-v1"||
 !Array.isArray(a.records)||a.records.length!==6||
 a.historical_scope?.posts!==61||a.historical_scope?.inline_images!==355||
 a.historical_scope?.historically_reported_broken!==42||
 a.historical_scope?.reported_broken_guest_confirmed!==false||
 a.historical_scope?.claimed_76_percent_network_reduction_measured!==false||
 a.historical_scope?.oversized_wordpress_originals!==15||
 a.historical_scope?.oversized_original_storage_bytes!==47096779||
 a.policy?.guest_browser_owner_pr!==154||a.policy?.media_recovery_pr!==1703||
 JSON.stringify(a.policy?.p0_queue)!==JSON.stringify(slots)||
 a.policy?.caching_authorized!==false||
 a.policy?.wordpress_production_writes!==false||
 a.policy?.homepage_design_changes!==false||
 a.policy?.subscription_spend_usd!==0||
 a.policy?.width_max_px!==960||a.policy?.upscaling!==false)return false;
 const original=[
 "https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg",
 "https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg",
 "https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg",
 "https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG",
 "https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg",
 "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg"];
 for(let i=0;i<6;i++){
 const r=a.records[i];
 if(!r||r.slot!==slots[i]||r.published_original_url!==original[i]||
 r.actual_origin_http_status!==null||r.actual_guest_http_status!==null||
 r.guest_decoded_image!==null||r.network_transferred_bytes!==null||
 r.retriever_observation?.method!=="THIRD_PARTY_WEB_RETRIEVER_ONLY"||
 !Number.isInteger(r.retriever_observation?.wrapper_code)||
 r.retriever_observation?.access_date!=="2026-11-12"||
 typeof r.candidate_url!=="string"||!r.candidate_url.startsWith("https://")||
 typeof r.license_observation!=="string"||!r.license_observation||
 r.rights_rehost_approved!==false||r.exact_photo_verified!==false||
 r.candidate_asset_downloaded!==false||r.scene_change_approved!==false||
 r.production_media_id!==null||r.conditional_max_width_px>960||
 r.status!=="HOLD_PENDING_GUEST_BROWSER_RIGHTS_AND_SAME_SCENE")return false;
 }
 if(a.records[2].kind!=="publisher_media_host_migration"||
 a.records[2].additional_primary_catalog!=="https://www.floridamemory.com/items/show/32082"||
 a.records[3].official_v_ir_in!=="210330-G-DE713-0002.JPG"||
 a.records[3].catalog_declares_public_domain!==true||
 a.records[5].kind!=="official_catalog_original_path_differs"||
 a.records[5].canonical_catalog_url!=="https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959"||
 a.records[5].catalog_declares_public_domain!==true||
 a.records[5].verified_native_dimensions_px!==null)return false;
 return true;
}
module.exports={validateP0CanonicalBridge};
