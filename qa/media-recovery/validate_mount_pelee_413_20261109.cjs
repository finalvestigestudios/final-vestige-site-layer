"use strict";
const fs = require("node:fs");
const expected="92a904c8da1ace1f972b2f00adf1a4847dde2b99";
const validate=function validate(a,c){
const ok=(z,why)=>{if(!z)throw Error(why)};
ok(a.schema==="fv-loc-pelee-four-v1"&&a.source_census_blob_sha===expected,"schema/census sha");
ok(a.post_id===413 && a.rows.length===4 && a.summary.rows===4 && a.summary.new_individual_slots===4,"cohort");
ok(a.summary.loc_catalog_matches===3 && a.summary.loc_catalog_unknown===1 && a.summary.web_tool_rendered===1 && a.summary.web_tool_inaccessible===3 && a.summary.guest_broken_confirmed===0,"summary");
ok(a.performance.alleged_42_browser_verified===false&&a.performance.proposed_76pct_transfer_saving_measured===false&&a.performance.guest_transferred_bytes===null,"performance");
ok(a.performance.originals_above_1500000_bytes===15 && a.performance.stored_bytes===47096779,"stored media");
const old=new Map(c.rows.map(r=>[r.slot,r]));const seen=new Set();
for(const r of a.rows){
const v=old.get(r.slot);ok(v&&v.post_id===413&&!v.researched,"frozen slot");
ok(!seen.has(r.slot),"duplicate");seen.add(r.slot);
ok(r.exact_original_url===v.stored_url&&r.origin_host===v.origin_host&&r.post_url===v.post_url,"source URL changed");
ok(r.web_observation.source==="WEB_VIEWER_NOT_GUEST_BROWSER"&&r.web_observation.result===(r.slot==="413:4"?"WEB_IMAGE_RENDERED":"WEB_INACCESSIBLE"),"retrieval class");
for(const k of ["guest_http","guest_natural_width","guest_natural_height","guest_wire_bytes","guest_broken"])ok(r.web_observation[k]===null,"invented browser "+k);
for(const k of ["third_party_download","third_party_cache","wordpress_upload","post_rewrite","homepage_change"])ok(r.release[k]===false,"unauthorized release "+k);
const p=r.loc_candidate;ok(p.authority==="LIBRARY_OF_CONGRESS"&&p.binary_crop_match===false&&p.republication_rights_cleared===false&&p.visual_approved===false,"rights/identity hold");
ok(p.native_px===null&&p.conditional_960_px===null&&p.visual_constraint.includes("both eyes"),"geometry/legibility");
if(r.slot==="413:3")ok(!p.record_confirmed&&p.catalog_url===null&&p.item_rights_note==="ITEM_NOT_VERIFIED","catalog unverified");
else {
const ids={"413:1":["1s41590","98504788","BEFORE_ERUPTION"],"413:4":["1s41424","2006688499","AFTER_ERUPTION"],"413:5":["1s41568","2004680426","AFTER_ERUPTION"]};
const k=ids[r.slot];ok(k&&p.record_confirmed===true&&p.accession.includes(k[0])&&p.catalog_url==="https://www.loc.gov/item/"+k[1]+"/"&&p.scene_era===k[2],"accession/date");
ok(p.item_rights_note==="No known restrictions on publication","rights advisory");
}
}
ok(seen.size===4,"full coverage");return {pass:true,slots:seen.size,loc_matches:3,guest_broken_claims:0};
};
module.exports={validate};
if(require.main===module){try{const a=JSON.parse(fs.readFileSync(process.argv[2]||"qa/media-recovery/mount_pelee_413_four_loc_20261109.json","utf8")); const c=JSON.parse(fs.readFileSync(process.argv[3]||"qa/media-recovery/offsite_upstream_288_20261109.json","utf8")); console.log(JSON.stringify(validate(a,c)));}catch(e){console.error("FAIL",e.message);process.exitCode=1;}}
