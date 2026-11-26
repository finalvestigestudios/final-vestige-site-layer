"use strict";
// Read-only, fail-closed quality gate. No requests, writes, downloads or HTML mutations.
const pinned=[
  {
    "key": "418:0",
    "authored_url": "https://www.history.uscg.mil/Portals/6/2_%20new%20and%20old%20lighthouses%2019849609_web1_1_-Scotch-Cap-lighthouse-1200x984.jpg",
    "jetpack_view_url": "https://i0.wp.com/www.history.uscg.mil/Portals/6/2_%20new%20and%20old%20lighthouses%2019849609_web1_1_-Scotch-Cap-lighthouse-1200x984.jpg?resize=1200%2C984&ssl=1",
    "catalog_url": "https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/",
    "asset_url": "https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/2_-new-and-old-lighthouses-19849609-e1728394749751-600x480.jpg"
  },
  {
    "key": "418:1",
    "authored_url": "https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG",
    "jetpack_view_url": "https://i0.wp.com/media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG?ssl=1",
    "catalog_url": "https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/",
    "asset_url": "https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG"
  },
  {
    "key": "418:2",
    "authored_url": "https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg",
    "jetpack_view_url": "https://i0.wp.com/www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg?ssl=1",
    "catalog_url": "https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/",
    "asset_url": "https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/5_-Scotch_Cap_debris2_1946-600x463.jpg"
  },
  {
    "key": "418:3",
    "authored_url": "https://www.history.uscg.mil/Portals/6/6_%20Scotch%20Cap%20remains.jpg",
    "jetpack_view_url": "https://i0.wp.com/www.history.uscg.mil/Portals/6/6_%20Scotch%20Cap%20remains.jpg?ssl=1",
    "catalog_url": "https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/",
    "asset_url": "https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/6_-Scotch-Cap-remains-e1728394850930-600x474.jpg"
  },
  {
    "key": "418:4",
    "authored_url": "https://www.hawaiimagazine.com/wp-content/uploads/2020/12/Tsunami1946NOAA2.jpg",
    "jetpack_view_url": "https://i0.wp.com/www.hawaiimagazine.com/wp-content/uploads/2020/12/Tsunami1946NOAA2.jpg?ssl=1",
    "catalog_url": "https://www.noaa.gov/noaa-collections/photo-library/pl23theb2705jpg",
    "asset_url": null
  },
  {
    "key": "418:5",
    "authored_url": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/styles/full_width/public/media/images/19460401_UNKNOWN_37-012_copy.jpg?itok=ASMRCahz",
    "jetpack_view_url": "https://i0.wp.com/d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/styles/full_width/public/media/images/19460401_UNKNOWN_37-012_copy.jpg?ssl=1",
    "catalog_url": "https://www.usgs.gov/media/images/damage-hilo-tsunami-struck-april-fools-day-1946",
    "asset_url": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/images/19460401_UNKNOWN_37-012_copy.jpg"
  }
];
function assess(d){
 const e=[];const ok=(x,k)=>{if(!x)e.push(k)};
 ok(d&&d.schema==="fv-scotchcap-six-source-custody-v1","schema");
 ok(d&&d.post_id===418&&d.post_modified==="2026-08-28T03:11:08","post_pin");
 ok(d&&d.image_count===6&&d.images_without_explicit_view_geometry===5&&d.images_with_explicit_view_geometry===1&&d.images_with_srcset===0&&d.images_with_sizes===0,"view_geometry_census");
 const h=d&&d.historical_census||{};
 ok(h.posts===61&&h.inline_images===355&&h.reported_broken===42&&h.guest_confirmed_broken===null&&h.claimed_wire_reduction_percent===76&&h.measured_wire_reduction_percent===null&&h.oversized_wp_original_count===20&&h.oversized_stored_bytes===64385752&&h.visitor_bytes_for_oversized===null,"historical_not_wire");
 const s=d&&d.scope||{};
 ok(["production_wordpress_writes","third_party_downloads","media_rehosts","homepage_design_changes","post_block_rewrites","subscription_spend"].every(k=>s[k]===0),"no_prod_scope");
 const rr=d&&d.rows||[];
 ok(Array.isArray(rr)&&rr.length===6,"six_rows");
 if(Array.isArray(rr))rr.forEach((r,i)=>{
 const p=pinned[i]; if(!p)return;
 ok(r.key===p.key&&r.authored_url===p.authored_url&&r.jetpack_view_url===p.jetpack_view_url&&r.catalog_url===p.catalog_url&&r.asset_url===p.asset_url,"pinned_urls_"+i);
 ok(r.alt_edit&&r.alt_edit===r.alt_view,"alt_integrity_"+i);
 ok(r.jetpack_view_url.startsWith("https://i0.wp.com/")&&r.jetpack_view_url.includes("ssl=1"),"jetpack_source_"+i);
 ok(r.guest_current_src===null&&r.guest_http_status===null&&r.guest_mime_type===null&&r.guest_decoding_success===null&&r.guest_transfer_bytes===null&&r.source_http_status===null,"no_fabricated_http_"+i);
 ok(r.exact_frame_verified===false&&r.native_candidate_dimensions_verified===false&&r.measured_candidate_binary_bytes===null&&r.candidate_sha256===null,"binary_fidelity_not_invented_"+i);
 ok(r.item_copy_rehost_approved===false&&r.wordpress_upload_approved===false,"no_stage_"+i);
 ok(r.max_width_px===960&&r.upscaling_allowed===false,"no_upscale_"+i);
 ok(r.published_srcset_present===false&&r.published_sizes_present===false,"responsive_not_invented_"+i);
 const dim=r.conditional_review_dimensions_px,prev=r.preview_advertised_px;
 ok((dim===null&&prev===null)||(Array.isArray(dim)&&Array.isArray(prev)&&dim.length===2&&dim[0]===prev[0]&&dim[1]===prev[1]&&dim[0]>0&&dim[0]<=960&&dim[1]>0),"preview_not_upscaled_"+i);
 ok(typeof r.rights_claim==="string"&&r.rights_claim.length>10&&r.credit.length>3,"rights_credit_"+i);
 });
 if(Array.isArray(rr)){
 const keys=rr.map(r=>r.key);ok(new Set(keys).size===6,"unique_slots");
 const withGeometry=rr.filter(r=>Array.isArray(r.published_dimensions_px));
 ok(withGeometry.length===1&&JSON.stringify(withGeometry[0].published_dimensions_px)===JSON.stringify([1200,984]),"view_width_height_from_wp");
 }
 if(Array.isArray(rr)&&rr.length===6){
 ok(rr[1].catalog_provenance==="USCG_PHOTO_GALLERY_VIRIN_210330-G-DE713-0002"&&rr[1].rights_claim==="USCG_ITEM_CLEARED_FOR_RELEASE_PUBLIC_DOMAIN_WITH_LIMITATIONS"&&rr[1].catalog_listed_size_mb===0.04&&rr[1].spelling_review.includes("Pettit"),"pettit_item_rights_and_spelling");
 ok(rr[4].asset_url===null&&rr[4].rights_claim==="PUBLISHER_HOST_NO_ITEM_COPYRIGHT_CLEARANCE","no_noaa_guess");
 ok(rr[5].rights_claim==="USGS_ITEM_PUBLIC_DOMAIN_CREATOR_UNKNOWN"&&rr[5].asset_url.endsWith("/media/images/19460401_UNKNOWN_37-012_copy.jpg")&&rr[5].visual_fidelity!=="PIXEL_IDENTICAL","usgs_source_not_overclaimed");
 }
 return {decision:e.length?"INVALID":"HOLD",errors:e,slots:Array.isArray(rr)?rr.length:0};
}
module.exports={assess};
if(require.main===module){const fs=require("node:fs");const path=require("node:path");const d=JSON.parse(fs.readFileSync(process.argv[2]||path.join(__dirname,"scotchcap_418_six_source_custody_20261116_1930pt.json"),"utf8"));const a=assess(d);process.stdout.write(JSON.stringify(a)+"\n");if(a.decision!=="HOLD")process.exitCode=1;}
