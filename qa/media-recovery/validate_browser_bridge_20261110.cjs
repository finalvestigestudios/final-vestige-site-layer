'use strict';
// Pure offline schema guard. No network, browser, WordPress or file writes.
// This handoff is NOT Site QA's browser collector and does not evaluate live results.
const P0=[
  [
    "285:5",
    "https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg"
  ],
  [
    "285:2",
    "https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg"
  ],
  [
    "287:5",
    "https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg"
  ],
  [
    "418:1",
    "https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG"
  ],
  [
    "418:2",
    "https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg"
  ],
  [
    "407:1",
    "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg"
  ]
];
const MEDIA=[
  [
    388,
    8176362,
    "https://finalvestige.com/wp-content/uploads/2026/08/vasa-modell-2020.jpg"
  ],
  [
    1258,
    5553669,
    "https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg"
  ],
  [
    1257,
    4798395,
    "https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg"
  ],
  [
    39,
    2892087,
    "https://finalvestige.com/wp-content/uploads/2026/08/bceca0bd-a16f-44f7-be08-16376fbf08ca.png"
  ],
  [
    43,
    2836245,
    "https://finalvestige.com/wp-content/uploads/2026/08/01340c2e-1165-4ca0-aa96-87398a83d13a.png"
  ],
  [
    389,
    2822969,
    "https://finalvestige.com/wp-content/uploads/2026/08/vasa-01-2020.jpg"
  ],
  [
    40,
    2552136,
    "https://finalvestige.com/wp-content/uploads/2026/08/377e08da-e121-4f57-9174-1548343402b3.png"
  ],
  [
    41,
    2498247,
    "https://finalvestige.com/wp-content/uploads/2026/08/a44f673d-a8a8-4c83-9f29-7e24dd55156b.png"
  ],
  [
    42,
    2488823,
    "https://finalvestige.com/wp-content/uploads/2026/08/c1237ffd-4a47-4988-8254-e3b021069e72.png"
  ],
  [
    382,
    2318980,
    "https://finalvestige.com/wp-content/uploads/2026/08/vasa-med-gamla-och-nya-stottor_vasa-with-old-and-new-supports.jpg"
  ],
  [
    482,
    2293016,
    "https://finalvestige.com/wp-content/uploads/2026/08/050e21e0-7b54-4f9a-ba0b-7f594657af05.png"
  ],
  [
    405,
    2201573,
    "https://finalvestige.com/wp-content/uploads/2026/08/The20Water20Resilience20Field20Manual.png"
  ],
  [
    293,
    2090327,
    "https://finalvestige.com/wp-content/uploads/2026/08/ne.png"
  ],
  [
    2148,
    2030948,
    "https://finalvestige.com/wp-content/uploads/2026/11/1927-caernarvon-levee-explosion-noaa-archive.jpg"
  ],
  [
    1714,
    1543002,
    "https://finalvestige.com/wp-content/uploads/2026/10/halifax-explosion-map.png"
  ]
];
const P0_EXTRA=[["https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg","PD_SELF",[819,614],"NOT_FOUND",404],["https://blog.ucs.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg","UNKNOWN",null,"REDIRECT_TARGET_INACCESSIBLE",500],["https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg","RIGHTS_UNVERIFIED",null,"NOT_FOUND",404],["https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/","USCG_PUBLIC_DOMAIN_RELEASE_CATALOG",null,"FORBIDDEN",403],["https://www.lighthousefriends.com/Scotch_Cap_debris2_1946.jpg","RIGHTS_UNVERIFIED",null,"FORBIDDEN",403],["https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg","USGS_PUBLIC_DOMAIN_CATALOG",null,"UNSUPPORTED_OCTET_STREAM",400]];
const MEDIA_EXTRA=[[[4256,2832],[960,639],[299],["https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-modell-2020.jpg?fit=1024%2C681&ssl=1"],7,"EDITORIAL_ONLY_MUSEUM_CREDIT_REQUIRED"],[[5667,3831],[960,649],[621],["https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg"],7,"ITEM_LEVEL_REVIEW_REQUIRED"],[[4000,3000],[960,720],[621],["https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg"],7,"ITEM_LEVEL_REVIEW_REQUIRED"],[[1672,941],[960,540],[34],["https://finalvestige.com/wp-content/uploads/2026/08/bceca0bd-a16f-44f7-be08-16376fbf08ca.png"],0,"HISTORICAL_RECONSTRUCTION_CREATOR_LICENSE_UNVERIFIED"],[[1672,941],[960,540],[38],["https://finalvestige.com/wp-content/uploads/2026/08/01340c2e-1165-4ca0-aa96-87398a83d13a.png"],0,"HISTORICAL_RECONSTRUCTION_CREATOR_LICENSE_UNVERIFIED"],[[2147,1417],[960,634],[299],["https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-01-2020.jpg?fit=1024%2C676&ssl=1"],7,"ITEM_LEVEL_REVIEW_REQUIRED"],[[1672,941],[960,540],[35],["https://finalvestige.com/wp-content/uploads/2026/08/377e08da-e121-4f57-9174-1548343402b3.png"],0,"HISTORICAL_RECONSTRUCTION_CREATOR_LICENSE_UNVERIFIED"],[[1672,941],[960,540],[36],["https://finalvestige.com/wp-content/uploads/2026/08/a44f673d-a8a8-4c83-9f29-7e24dd55156b.png"],0,"HISTORICAL_RECONSTRUCTION_CREATOR_LICENSE_UNVERIFIED"],[[1672,941],[960,540],[37],["https://finalvestige.com/wp-content/uploads/2026/08/c1237ffd-4a47-4988-8254-e3b021069e72.png"],0,"HISTORICAL_RECONSTRUCTION_CREATOR_LICENSE_UNVERIFIED"],[[1800,1200],[960,640],[299],["https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-med-gamla-och-nya-stottor_vasa-with-old-and-new-supports.jpg?fit=1024%2C683&ssl=1"],6,"ITEM_LEVEL_REVIEW_REQUIRED"],[[1672,941],[960,540],[],[],6,"ITEM_LEVEL_REVIEW_REQUIRED"],[[1122,1402],[960,1200],[],[],5,"ITEM_LEVEL_REVIEW_REQUIRED"],[[1122,1402],[960,1200],[],[],5,"ITEM_LEVEL_REVIEW_REQUIRED"],[[1821,1190],[960,627],[],[],6,"COMMONS_NOAA_PD_ASSERTION_CROP_REVIEW_REQUIRED"],[[1280,1280],[960,960],[269],["https://finalvestige.com/wp-content/uploads/2026/10/halifax-explosion-map.png"],5,"ORIGINAL_MAP_AUTHOR_RIGHTS_UNVERIFIED"]];
const REF={"ledger":"8526557c7a5138e1ca22a347e3f9839503d48b2c","coverage":"4965a862f7de7de46c1f4a1e26f3ca70a8c38805","worklist":"2acd06a4ca4317646006eb6591face3fe76fedec"};
function validate(d) {
 const errors=[],bad=(x)=>errors.push(x);
 if (!d || d.schema !== 'fv-media-recovery-siteqa-bridge-v1') return {pass:false,errors:['schema']};
 if (d.authority?.site_qa_pr!==154 || d.authority?.media_recovery_pr!==1703) bad('ownership');
 if(d.authority?.source_ledger?.blob_sha!==REF.ledger||d.authority?.full_provenance?.blob_sha!==REF.coverage||d.authority?.worklist?.blob_sha!==REF.worklist||d.authority?.worklist?.pr!==183) bad('source_sha');
 if(JSON.stringify(d.cohorts?.historical)!==JSON.stringify({posts:61,inline_positions:355,external_positions:288,research_completed:288})) bad('frozen_cohort');
 if(d.cohorts?.expanded_live_nov_08?.posts!==66||d.cohorts?.expanded_live_nov_08?.inline_positions!==361||d.cohorts?.expanded_live_nov_08?.media_records!==122) bad('expanded_cohort');
 const r=d.release||{};
 if(r.guest_verified_broken_count!==0||r.claimed_historical_broken!==42||r.claim_42_verified!==false||r.claim_76_percent_measured!==false||r.production_repairs!==0||r.wordpress_writes!==0||r.third_party_downloads!==0||r.rights_preapproved!==false) bad('unproven_release');
 if(!Array.isArray(d.p0_queue)||d.p0_queue.length!==6)bad('p0_length');
 else d.p0_queue.forEach((x,i)=>{
   if(x.slot!==P0[i][0]||x.original_src!==P0[i][1]||x.post_id!==Number(x.slot.split(':')[0]))bad('p0_identity_'+i);
   if(JSON.stringify([x.catalog_candidate_url,x.rights_observation,x.conditional_960px,x.retriever_only?.result,x.retriever_only?.wrapper_code])!==JSON.stringify(P0_EXTRA[i]))bad('p0_evidence_drift_'+i);
   if(x.retriever_only?.method!=='EXTERNAL_WEB_RETRIEVER_NOT_GUEST')bad('retriever_method_'+i);
   if(x.actual_origin_http_status!==null||x.guest_http_status!==null||x.guest_current_src!==null||x.guest_natural_px!==null||x.cold_encoded_image_bytes!==null)bad('invented_guest_'+i);
   if(x.exact_visual_identity_proven!==false||x.reuse_rights_cleared!==false||x.caching_approved!==false||x.wordpress_upload_approved!==false)bad('unapproved_replacement_'+i);
   if(typeof x.catalog_candidate_url!=='string'||!x.catalog_candidate_url.startsWith('https://'))bad('candidate_url_'+i);
   if(x.conditional_960px!==null&&(!Array.isArray(x.conditional_960px)||x.conditional_960px.length!==2||x.conditional_960px.some(y=>!Number.isInteger(y)||y<1)||x.conditional_960px[0]>960))bad('p0_geometry_'+i);
 });
 if(!Array.isArray(d.oversized_media)||d.oversized_media.length!==15)bad('oversize_length');
 else {
  let sum=0,inline=0,count=0;
  d.oversized_media.forEach((x,i)=>{
   const [id,size,url]=MEDIA[i];sum+=x.stored_original_bytes; if(x.inline_post_ids?.length){inline+=x.stored_original_bytes;count++}
   if(JSON.stringify([x.native_px,x.conditional_960px,x.inline_post_ids,x.published_direct_srcs,x.generated_subsizes,x.rights_observation])!==JSON.stringify(MEDIA_EXTRA[i]))bad('media_metadata_drift_'+i);
   if(x.media_id!==id||x.stored_original_bytes!==size||x.original_url!==url||size<=1500000)bad('oversize_identity_'+i);
   if(!Array.isArray(x.inline_post_ids)||!Array.isArray(x.published_direct_srcs)||!Number.isInteger(x.generated_subsizes)||x.generated_subsizes<0)bad('oversize_snapshot_'+i);
   if(x.guest_current_src!==null||x.guest_wire_bytes!==null||x.derivative_authorized!==false)bad('invented_media_measurement_'+i);
   const p=x.native_px,q=x.conditional_960px;
   if(!Array.isArray(p)||p.length!==2||p.some(z=>!Number.isInteger(z)||z<1)||!Array.isArray(q)||q.length!==2||q.some(z=>!Number.isInteger(z)||z<1)||q[0]>Math.min(p[0],960)||q[1]>p[1])bad('upscale_'+i);
  });
  if(sum!==47096779||inline!==38480915||count!==11)bad('oversize_totals');
 }
 const m=d.methodology||{};
 if(m.original_storage_byte_total!==47096779||m.inline_referenced_original_storage_bytes!==38480915||m.decimal_threshold_bytes!==1500000)bad('storage_totals');
 if(m.measured_cold_baseline_image_bytes!==null||m.measured_cold_candidate_image_bytes!==null||m.measured_saving_pct!==null||m.stated_target_pct!==76)bad('invented_transfer_savings');
 return {pass:!errors.length,errors};
}
module.exports={validate};
