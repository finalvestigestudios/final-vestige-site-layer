'use strict';
/** Offline immutable snapshot guard: status unknown != image broken. No I/O. */
const names=['New_London_School_explosion.jpg','New_London_School_before_explosion.webp','INP_Photos_of_New_London_School_explosion.jpg','INP_Photos_of_New_London_School_explosion_(1).jpg','INP_Photos_of_New_London_School_explosion_(2).jpg','New_London_School_Explosion_Memorial_-_46699056584.jpg'];
const dimensions=[[760,609],[960,685],[2861,2244],[2457,1950],[2457,1862],[3840,2160]];
function validate(d){
 const errors=[],yes=(v,m)=>{if(!v)errors.push(m)};
 yes(d?.schema==='fv-new-london-217-20261114-v1'&&d?.post_id===217&&d?.post_url==='https://finalvestige.com/2026/08/18/the-gas-had-no-smell/','post');
 yes(d?.frozen_source?.blob==='0f3dfe398a76838049cebba7cb773d5c5a0c8c69'&&d?.frozen_source?.pr===183,'frozen source');
 yes(d?.reference_61_355?.posts===61&&d?.reference_61_355?.stored_image_tags===355,'61/355');
 yes(d?.reference_61_355?.report_of_42_broken==='not_browser_confirmed'&&d?.reference_61_355?.report_of_76_percent==='unmeasured_wire_bytes','claims');
 yes(d?.reference_61_355?.oversize_originals_above_1500000_bytes===16&&d?.reference_61_355?.oversize_originals_stored_bytes===49107665,'oversize');
 yes(d?.browser_verified_broken_count===null&&d?.visitor_weight_reduction_percent===null,'invented results');
 yes(d?.production_wordpress_write===false&&d?.downloaded_media_binaries===false&&d?.homepage_changed===false,'safe scope');
 yes(Array.isArray(d?.images)&&d.images.length===6,'six images');
 for(let i=0;i<6;i++){
  const x=d?.images?.[i];if(!x){yes(false,'missing '+i);continue}
  const nm=names[i],[w,h]=dimensions[i],maxw=Math.min(w,960),maxh=Math.round(maxw*h/w);
  yes(x.key==='217:'+i,'key '+i);
  yes(x.original_file===nm&&x.source_url==='https://commons.wikimedia.org/wiki/Special:Redirect/file/'+nm+'?width=1280','exact src '+i);
  yes(x.catalog_url==='https://commons.wikimedia.org/wiki/File:'+nm&&x.catalog_observation==='html_metadata_seen_no_binary_or_origin_status','catalog '+i);
  yes(x.requested_width_px===1280&&x.original_width_px===w&&x.original_height_px===h,'native '+i);
  yes(x.conditional_max_width_px===maxw&&x.conditional_max_height_px===maxh&&maxw<=w&&maxh<=h,'no upscale '+i);
  yes(x.stored_width===null&&x.stored_height===null,'stored geometry '+i);
  yes(typeof x.alt==='string'&&x.alt.length>20&&typeof x.caption_html==='string'&&x.caption_html.length>20,'caption '+i);
  yes(x.commons_reported_rights===(i===5?'CC_BY_SA_2_0':'PD_US_NOT_RENEWED_ASSERTED')&&x.license_url===(i===5?'https://creativecommons.org/licenses/by-sa/2.0/':null),'license '+i);
  yes(x.caption_has_license_link===false,'actual caption link '+i);
  yes(x.extracted_from_original===([3,4].includes(i)?names[2]:null),'crop provenance '+i);
  yes((x.metadata_date_discrepancy!==null)===(i===0),'date note '+i);
  yes(x.legal_review==='HOLD'&&x.exact_original_binary_hash===null&&x.exact_visual_crop_verified===false,'rights/visual '+i);
  yes(x.source_reader_original_http_status===null&&x.guest_browser_http_status===null&&x.browser_current_src===null&&x.guest_network_transfer_bytes===null,'HTTP/wire unverified '+i);
  yes(x.rights_clear_to_cache===false&&x.rights_clear_to_rehost===false&&x.production_wordpress_write_authorized===false,'no release '+i);
 }
 return {ok:!errors.length,errors,summary:{slots:6,smaller_native_than_requested:2,INP_derived_crops:2,modern_CC_image:1,actual_visitor_failures:null,actual_wire_bytes:null}};
}
module.exports={validate};
if(require.main===module){const a=require('./new_london_217_catalog_rights_20261114.json');const r=validate(a);console.log(JSON.stringify(r,null,2));if(!r.ok)process.exitCode=1}
