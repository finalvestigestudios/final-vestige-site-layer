'use strict';
// Offline, deterministic and fail closed; never fetches images or writes WordPress.
const assess = function assess(d){
 const errors=[];const ck=(b,n)=>{if(!b)errors.push(n)};
 ck(d?.schema==="fv-media-two-proxy-reader-v1"&&d?.observation_method==="PUBLIC_IMAGE_READER_NOT_COLD_BROWSER","method");
 ck(d?.date==="2026-11-16"&&d?.qa_pr===154&&d?.parent_pr===2747,"custody");
 ck(d?.historical?.posts===61&&d?.historical?.images===355&&d?.historical?.qa_offsite===286&&d?.historical?.media_offsite===288,"census");
 ck(d?.claimed_42_browser_broken===false&&d?.measured_76_percent_savings===false&&d?.browser_failure_confirmed===false,"claims");
 ck(d?.large_stored?.count===20&&d?.large_stored?.bytes===64385752&&d?.large_stored?.visitor_transfer_bytes===null,"storage");
 ck(d?.rights_policy==="https://www.archives.gov/research/still-pictures/permissions","rights_policy");
 ck(d?.license_cleared===false&&d?.production_write===false&&d?.homepage_change===false&&d?.paid_action===false&&d?.automatic_replace===false,"production_hold");
 const want=[
 ["285:1","https://i0.wp.com/www.squawkpoint.com/wp-content/uploads/2019/02/Three-Mile-Island-Control-Centre.jpg?ssl=1","https://www.flickr.com/photos/nrcgov/7447591424","RELATED_NOT_EXACT"],
 ["291:0","https://i0.wp.com/text-message.blogs.archives.gov/wp-content/uploads/sites/5/2016/05/teton_failing_fourth-scaled.jpg?ssl=1","https://text-message.blogs.archives.gov/2016/05/31/the-unforgettable-calamity-40th-anniversary-of-the-teton-dam-failure/","CURATORIAL_NOT_EXACT_ACCESSION"]];
 ck(Array.isArray(d?.rows)&&d.rows.length===2,"row_count");
 for(let i=0;i<2;i++){const r=d?.rows?.[i];if(!r){errors.push("missing_"+i);continue}
  ck(r.slot===want[i][0]&&r.url===want[i][1],"url_"+i);
  ck(r.reader_rendered===true&&typeof r.scene==="string"&&r.scene.length>15,"rendered_"+i);
  for(const k of ["reader_http","origin_http","guest_http","guest_current_src","guest_decode","guest_transfer_bytes","binary_sha256","native_dimensions"])ck(r[k]===null,"null_"+k+"_"+i);
  ck(r.rights==="HOLD"&&r.reference_rights==="UNVERIFIED"&&r.max_width===960&&r.wp_cached===false,"release_"+i);
  ck(r.official_reference===want[i][2]&&r.relation===want[i][3],"source_"+i);
 }
 return {ok:errors.length===0,errors,decision:"HOLD_BROWSER_AND_ITEM_RIGHTS"};
};
module.exports = {assess};
if(require.main===module){const fs=require('node:fs');const r=assess(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));console.log(JSON.stringify(r,null,2));if(!r.ok)process.exitCode=2;}
