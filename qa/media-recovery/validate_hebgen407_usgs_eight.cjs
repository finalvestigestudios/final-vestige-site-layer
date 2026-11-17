'use strict';
// Offline ONLY: read-only, reject unsupported browser/rights/performance claims.
const names=['vhp_img317.jpg','img7535.jpg','EarthquakeLake1.jpg','EarthquakeLake3.jpg','img7536.jpg','img7538.jpg','img7537.jpg','Quake%20lake%20and%20slide%2020230627.jpg'];
const slugs=['earthquake-damage-1959-hebgen-lake-event-yellowstone-plateau','hebgen-lake-fault-scarp-1959','view-madison-slide-august-21-1959-rapidly-filling-earthquake-lake','dragline-working-lower-outlet-channel-earthquake-lake-october-18-1959','rockslide-damage-golden-gate-area-near-mammoth-hot-springs','sapphire-pool-upper-geyser-basin-erupting-after-1959-hebg','seismic-geyser-eruption-1970','earthquake-lake-and-madison-slide'];
const exactGeometry={2:[1024,719],3:[1024,730],7:[1024,771]};
const canonical1='https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg';
function check(c,m){if(!c)throw Error(m);}
function validate(d){
 check(d && d.schema==='fv-usgs-hebgen-eight-primary-custody-v1','schema');
 check(d.wp_site==='https://finalvestige.com'&&d.wp_post_id===407&&d.wp_status==='publish','post');
 check(d.wp_post_url==='https://finalvestige.com/2026/08/20/the-lake-wasnt-there-yesterday-hebgen/'&&d.wp_modified==='2026-10-29T18:30:30','revision');
 check(d.guest_browser_captures===0&&d.direct_media_probe_numerical_http_status==='NOT_MEASURED','no-browser-capture');
 check(d.history&&d.history.posts===61&&d.history.inline_images===355&&d.history.reported_broken_third_party_images===42&&d.history.guest_verified_broken_images===null,'census-vs-claim');
 check(d.history.claimed_weight_reduction_percent===76&&d.history.measured_wire_reduction_percent===null&&d.history.oversized_original_count===20&&d.history.oversized_stored_bytes===64385752,'weight-no-measure');
 check(d.wordpress_changes===0&&d.downloads===0&&d.licensed_asset_mirrors===0,'no-writes');
 check(Array.isArray(d.rows)&&d.rows.length===8,'eight-rows');
 d.rows.forEach((r,i)=>{
  check(r && r.key==='407:'+i && r.slot===i,'slot');
  check(typeof r.authored_source_url==='string'&&r.authored_source_url.startsWith('https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/')&&r.authored_source_url.endsWith('/'+names[i]),'authored-source');
  check(typeof r.published_jetpack_url==='string'&&r.published_jetpack_url.startsWith('https://i0.wp.com/d9-wret.s3.us-west-2.amazonaws.com')&&r.published_jetpack_url.includes(names[i])&&r.published_jetpack_url.includes('ssl=1'),'view-src');
  check(typeof r.alt_text==='string'&&r.alt_text.length>25,'alt');
  check(r.usgs_item_url==='https://www.usgs.gov/media/images/'+slugs[i],'primary-record');
  check(r.usgs_catalog_rights_statement==='Public Domain.'&&r.rights_review==='ITEM_REVIEW_BEFORE_REHOST'&&typeof r.usgs_catalog_credit==='string'&&r.usgs_catalog_credit.length>8,'rights-custody');
  check(r.usgs_original_link_url===(i===1?canonical1:r.authored_source_url),'canonical-source');
  check(r.canonical_path_relationship===(i===1?'CANONICAL_PATH_DIFFERS':'SAME_AUTHORED'),'canonical-difference');
  check(r.original_retriever_observation===(i===1?'TOOL_UNSUPPORTED_OCTET_STREAM_400':i===3?'DIRECT_TOOL_INACCESSIBLE_THEN_OFFICIAL_LINK_DISPLAYED':'DISPLAYED_DIRECT'),'retriever-evidence');
  check(r.official_original_retriever_observation==='IMAGE_DISPLAYED'&&r.tool_observation_is_browser_http===false,'reader-not-browser');
  check(r.browser_current_src===null&&r.browser_http_status===null&&r.browser_mime_type===null&&r.browser_decode_success===null&&r.browser_wire_bytes===null,'unknown-browser');
  check(r.same_frame_hash_verified===false&&r.rehosting_approved===false&&r.wordpress_write_approved===false&&r.broken_for_visitors_confirmed===false,'release-hold');
  const g=exactGeometry[i]||null;
  check(r.published_width_height_explicit===!!g&&r.published_srcset_present===false&&r.published_sizes_present===false,'markup');
  if(g){
   check(Array.isArray(r.authored_dimensions_px)&&r.authored_dimensions_px[0]===g[0]&&r.authored_dimensions_px[1]===g[1],'markup-ratio');
   check(Array.isArray(r.conditional_960px_ratio_from_markup)&&r.conditional_960px_ratio_from_markup[0]===960&&r.conditional_960px_ratio_from_markup[1]===Math.round(960*g[1]/g[0]),'960-ratio');
  }else check(r.authored_dimensions_px===null&&r.conditional_960px_ratio_from_markup===null,'geometry-unknown');
  check(r.native_pixel_dimensions_verified===false,'no-invented-native');
 });
 return {validated_slots:8,canonical_rewrite_candidate_slots:['407:1'],browser_verified_failures:0,wordpress_changes:0,rights_release:'HOLD'};
}
module.exports={validate};
