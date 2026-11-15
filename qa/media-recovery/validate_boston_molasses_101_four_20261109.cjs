"use strict";
const validate=function validateBoston(a,c){
const ok=(v,why)=>{if(!v)throw Error(why)};
ok(a.schema==="fv-boston-molasses-101-four-commons-v1"&&a.source_inventory.blob_sha==="92a904c8da1ace1f972b2f00adf1a4847dde2b99","schema/ledger");
ok(a.post_id===101 && a.summary.rows===4 && a.rows.length===4 && a.summary.web_viewer_images_rendered===4 && a.summary.guest_http_verified===0 && a.summary.source_below_960_count===2,"cohort metrics");
ok(a.primary_archive_context.same_image_match===false&&a.primary_archive_context.rights_for_alternative_verified===false&&a.primary_archive_context.url.startsWith("https://content.boston.gov/"),"alternative claims");
ok(a.performance.historical_broken_42_browser_verified===false&&a.performance.claimed_76pct_wire_reduction_measured===false&&a.performance.guest_wire_bytes===null,"performance");
ok(a.performance.originals_over_1500000_bytes===15&&a.performance.oversize_original_stored_bytes===47096779,"stored media");
const specs={
"101:1":[417,327,"PD_US_HISTORICAL_COMMONS_CLAIM","PRE_1919_01_15","North_End_molasses_tank.jpg"],
"101:2":[874,742,"PD_CREATOR_RELEASE_COMMONS","2005_03_21","Boston_molasses_detail_map.png"],
"101:4":[1127,1435,"PD_US_PRE_1931_COMMONS_CLAIM","1919_01_16","Boston_post-January_16"],
"101:6":[3129,2801,"CC_BY_SA_3_0_UNPORTED","2012_12_13","Molasses_Flood_Historical_Marker.jpg"]};
const old=new Map(c.rows.map(x=>[x.slot,x]));const seen=new Set();
for(const r of a.rows){
const s=specs[r.slot],src=old.get(r.slot);ok(s&&src&&src.post_id===101&&!src.researched,"slot not original/unresearched");
ok(!seen.has(r.slot),"duplicate slot");seen.add(r.slot);
ok(r.post_url===src.post_url&&r.exact_stored_url===src.stored_url&&r.origin_host===src.origin_host&&r.delivery_host===src.delivery_host,"url mismatch");
ok(r.external_viewer.source==="WEB_IMAGE_VIEWER_NOT_GUEST_BROWSER"&&r.external_viewer.observation==="IMAGE_DISPLAYED","source observation");
for(const k of ["http_status","mime","transferred_bytes"])ok(r.external_viewer[k]===null,"fake numeric external status");
for(const k of ["current_src","http_status","decoded_width","decoded_height","wire_bytes","broken"])ok(r.guest_browser[k]===null,"fake visitor status");
for(const k of ["asset_download","cache","wordpress_upload","post_rewrite","homepage_change","license_cleared","visually_approved"])ok(r.release[k]===false,"unsafe release");
const p=r.commons_candidate;ok(p.catalog_url.startsWith("https://commons.wikimedia.org/wiki/File:")&&p.catalog_url.includes(s[4]),"catalog identity");
ok(p.catalog_original_dimensions_px[0]===s[0]&&p.catalog_original_dimensions_px[1]===s[1],"original geometry");
const w=Math.min(960,s[0]),h=Math.round(s[1]*w/s[0]);
ok(p.conditional_no_upscale_960px[0]===w&&p.conditional_no_upscale_960px[1]===h&&w<=s[0]&&w<=960,"960 geometry");
ok(p.claimed_license===s[2]&&p.item_date===s[3]&&p.creator_credit.length>1,"item rights/date");
ok(p.binary_sha256===null&&p.original_binary_exact_match===false&&p.rights_review_complete===false,"binary/rights");
ok(p.historical_scene_note.length>70&&p.visual_legibility_gate.length>24,"historical/legibility");
if(r.slot==="101:6")ok(p.historical_scene_note.includes("share-alike")&&p.creator_credit==="MLHalsey","BY-SA obligations");
if(r.slot==="101:2")ok(p.historical_scene_note.includes("NOT a 1919")&&p.catalog_original_dimensions_px[0]===874,"map is not period original");
if(r.slot==="101:1")ok(p.conditional_no_upscale_960px[0]===417,"no-upscale small");
}
ok(seen.size===4&&Object.keys(specs).every(x=>seen.has(x)),"slot set");
return {pass:true,rows:4,known_catalog_geometry:4,browser_broken_claims:0,production_writes:0};
};
module.exports={validate};
if(require.main===module){const fs=require("node:fs");const path=require("node:path");try{const d=JSON.parse(fs.readFileSync(path.join(__dirname,"boston_molasses_101_four_20261109.json"),"utf8"));const c=JSON.parse(fs.readFileSync(path.join(__dirname,"offsite_upstream_288_20261109.json"),"utf8"));console.log(JSON.stringify(validate(d,c)));}catch(e){console.error("FAIL",e.message);process.exitCode=1;}}
