'use strict';
const master=[
['PR04493','prints/pr04493.jpg',4144,1928],
['RC17068','reference/rc17068.jpg',38362,1928],
['RC10673','reference/rc10673.jpg',33289,1928],
['N031889','general/n031889.jpg',141398,1928],
['RC04344','reference/rc04344.jpg',27848,1928],
['RC07668','reference/rc07668.jpg',30741,1928],
['MSF-PB11548-001','msf/MSF-PB11548-001.jpg',340182,2001]];
function verify(a){
 const gate=(ok,reason)=>{if(!ok)throw Error(reason)};
 gate(a&&a.schema==='fv-okeechobee432-florida-memory-seven-v1'&&a.post_id===432,'scope');
 gate(a.source_git_sha==='1c8cd5d1fd015705c0937d68471fb54546ed2f67','source custody');
 gate(Array.isArray(a.images)&&a.images.length===7,'seven images');
 gate(a.image_source_retriever_result.includes('not verified origin HTTP 500'),'redirect semantics');
 gate(a.confirmed_guest_broken_count===null&&!a.claimed_42_guest_confirmed&&!a.claimed_76_percent_savings_verified,'no invented performance or failure');
 gate(a.derivative_max_width_px===960&&a.allow_upscale===false&&!a.authorized_binary_download&&!a.authorized_wordpress_upload&&a.production_writes===0,'safe staging only');
 gate(a.oversized_originals_stored_bytes_baseline===64385752,'stored baseline');
 for(let i=0;i<7;i++){
  const x=a.images[i],m=master[i];
  gate(x&&x.slot_id==='432:'+i&&x.archive_id===m[0]&&x.catalog_year===m[3],'accession and chronology');
  gate(x.original_url==='https://www.floridamemory.com/fpc/'+m[1],'exact original URL');
  gate(x.catalog_image_url==='https://floridamemory.com/fpc/'+m[1]&&x.official_catalog_url==='https://floridamemory.com/items/show/'+m[2],'official catalog crosswalk');
  gate(x.published_jetpack_url.startsWith('https://i0.wp.com/www.floridamemory.com/')||x.published_jetpack_url.startsWith('https://i1.wp.com/www.floridamemory.com/')||x.published_jetpack_url.startsWith('https://i2.wp.com/www.floridamemory.com/'),'expected Jetpack source');
  gate(x.official_catalog_identity_matched===true,'identity claim');
  gate(x.original_origin_http_status===null&&x.guest_image_http_status===null&&x.guest_decode===null&&x.guest_wire_bytes===null,'unknown HTTP remains unknown');
  gate(x.published_width_px===null&&x.published_height_px===null&&!x.has_srcset&&!x.has_sizes,'observed HTML metadata');
  gate(x.master_pixel_width===null&&x.master_pixel_height===null&&x.derived_width===null&&x.derived_height===null,'no fabricated pixels');
  gate(x.rights_state==='PDM_PROVIDER_CLAIM_ITEM_REVIEW_PENDING'&&!x.rehosting_allowed&&x.replacement_status==='HOLD','rights and upload hold');
 }
 gate(a.images[3].proposed_alt==='State Board of Health staff at its Pahokee headquarters in 1928.','correct unsupported response assertion');
 gate(a.images[6].catalog_year===2001&&a.images[6].proposed_alt.includes('2001'),'2001 photo chronology');
 return {status:'REVIEW_ONLY',slots:7,confirmed_guest_failures:0,production_writes:0};
}
module.exports={verify};
