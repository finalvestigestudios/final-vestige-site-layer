'use strict';
// Pure, dependency-free custody and fail-closed check; never fetches media or writes to WordPress.
const assert=require('node:assert/strict');
const ORIGIN='https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg';
const SIBLING='https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg';
const JETPACK='https://i0.wp.com/d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg?ssl=1';
const LINKED='https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0';
const ALIAS='https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959';
function hold(ok,msg){if(!ok)throw Error('HOLD: '+msg);}
function validate(x){
 hold(x?.schema==='fv-media-official-catalog-alias-differential-v1','schema');
 hold(x.observed_date_local==='2026-11-16','date');
 const w=x.wordpress,cat=x.official_catalogs,obs=x.observations,g=x.gates,i=x.integrity,d=x.derivative,b=x.unchanged_baselines;
 hold(w && w.post_id===407 && w.image_index_zero_based===1 && w.slot==='407:1','slot');
 hold(w.modified==='2026-10-29T18:30:30','WP revision');
 hold(w.published_url==='https://finalvestige.com/2026/08/20/the-lake-wasnt-there-yesterday-hebgen/','post URL');
 hold(w.authored_image_url===ORIGIN && w.rendered_rest_view_url===JETPACK && w.authored_catalog_hyperlink===LINKED,'WordPress URL custody');
 hold(w.alt==='Fresh fault scarp near Hebgen Lake produced by the August 1959 earthquake.','original ALT');
 for(const key of ['guest_current_src','guest_http_status','guest_mime','guest_natural_width','guest_natural_height','guest_transfer_bytes','guest_decoded','guest_broken_proven'])hold(w[key]===null,'unverified guest '+key);
 hold(Array.isArray(cat)&&cat.length===2,'two catalogs');
 hold(cat[0].catalog===LINKED && cat[0].catalog_original_link_url===ORIGIN && cat[0].relationship==='on-post linked catalog','linked USGS Original');
 hold(cat[1].catalog===ALIAS && cat[1].catalog_original_link_url===SIBLING && cat[1].relationship==='official sibling catalog, not linked by post','USGS sibling Original');
 hold(cat[0].catalog_title==='Hebgen Lake fault scarp in 1959' && cat[1].catalog_title===cat[0].catalog_title,'source titles');
 hold(cat.every(c=>c.photographer==='J. R. Stacy' && c.rights_label==='Public Domain.' && c.origin_http_status===null),'photographer/rights/status');
 hold(cat[0].retriever_observation==='original binary rejected as unsupported content-type binary/octet-stream' && cat[1].retriever_observation==='image rendered by public reader','reader outcomes');
 hold(Array.isArray(obs)&&obs.length===3,'route count');
 for(const [idx,url,route,method,result] of [
   [0,ORIGIN,'authored_original_same_as_linked_catalog','public-web-catalog-click','unsupported_binary_octet_stream'],
   [1,SIBLING,'official_sibling_original','public-web-catalog-click','image_rendered'],
   [2,JETPACK,'wordpress_jetpack_view','public-web-document-reader','tool_inaccessible']]){
  const r=obs[idx];hold(r.url===url&&r.route===route&&r.method===method&&r.reader_result===result,'route '+idx);
  hold(r.numeric_origin_status===null&&r.guest_browser_status===null,'no fabricated HTTP status '+idx);
 }
 hold(i.same_filename===true && i.same_photographer_and_subject===true && i.official_item_rights_statement_verified===true,'verified source metadata');
 for(const key of ['same_pixel_hash_proven','same_crop_and_frame_visually_approved','copyright_rehost_approved','source_attribute_correction_approved','image_downloaded'])hold(i[key]===false,'unsafe integrity claim '+key);
 hold(d.max_width_px===960 && d.no_upscale===true && d.verified_native_dimensions===false && d.output_width_px===null && d.output_height_px===null,'unknown native geometry');
 hold(d.formula_after_native_dimensions==='w=min(960,native_w);h=round(native_h*w/native_w)','geometry formula');
 hold(d.wordpress_media_staging_approved===false && d.cache_mirroring_approved===false,'no media rehost');
 for(const key of ['visitor_failure_confirmed','per_image_rights_and_credit_review_done','pixel_or_frame_match_confirmed','responsive_or_lcp_acceptance_done','live_website_changed'])hold(g[key]===false,'false completion '+key);
 hold(g.word_press_write_count===0,'no WP mutation');
 hold(b.frozen_posts===61&&b.frozen_images===355&&b.latest_posts===66&&b.latest_images===361,'historical/current cohort');
 hold(b.reported_broken===42&&b.browser_confirmed_broken===null,'42 are unconfirmed');
 hold(b.claimed_weight_savings_percent===76&&b.visitor_bytes_savings_percent===null,'76% is unmeasured');
 hold(b.over_1_5_mb_originals===20&&b.original_storage_bytes===64385752,'stored originals not transfers');
 hold(x.next_gate.startsWith('Existing Site QA #154 cold guest Chromium collector:'),'Site QA ownership');
 return {status:'HOLD_GUEST_PIXEL_RIGHTS',post_slot:w.slot,official_catalog_count:2,delivery_route_count:3,originals_differ:true,visitor_http_status:null,wordpress_writes:0};
}
module.exports={validate};
