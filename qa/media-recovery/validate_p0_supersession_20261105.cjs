"use strict";
const EXPECTED={"285:5":"https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg","285:2":"https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg","287:5":"https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg","418:1":"https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG","418:2":"https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg","407:1":"https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg"};
const WRAPPERS={"285:5":404,"285:2":500,"287:5":404,"418:1":403,"418:2":403,"407:1":400};
function check(d){
const e=[]; const bad=(s)=>e.push(s);
if(d?.schema!=="fv-p0-candidate-supersession-v1")bad("schema");
if(!Array.isArray(d?.rows)||d.rows.length!==6)return {ok:false,errors:["six rows required",...e]};
if(new Set(d.rows.map(x=>x.k)).size!==6)bad("duplicate slot");
for(const x of d.rows){
if(!(x.k in EXPECTED)){bad("unexpected slot");continue;}
if(x.src!==EXPECTED[x.k])bad(x.k+" source drift");
if(x.wrapper!==WRAPPERS[x.k])bad(x.k+" tool status drift");
for(const f of ["guest_http","guest_current_src","guest_natural_pixels","guest_wire_bytes","visitor_broken"])if(x[f]!==null)bad(x.k+" invented browser "+f);
for(const f of ["rights_rehost","binary_identity_verified","cache_allowed","wp_upload","wp_post_edit","automated_rewrite"])if(x[f]!==false)bad(x.k+" unauthorized "+f);
for(const f of ["catalog","candidate"])if(typeof x[f]!=="string"||!x[f].startsWith("https://"))bad(x.k+" invalid "+f);
if(!x.credit||!x.detail||!x.relationship)bad(x.k+" provenance missing");
const p=x.preview;
if(p===null){if(x.max_safe_width_if_preview_known!==null)bad(x.k+" unknown pixels output cap invented");}
else if(!Array.isArray(p)||p.length!==2||p.some(n=>!Number.isInteger(n)||n<=0)||x.max_safe_width_if_preview_known!==Math.min(960,p[0]))bad(x.k+" invalid preview geometry");
}
const q=Object.fromEntries(d.rows.map(x=>[x.k,x]));
if(q["285:2"]?.candidate!=="https://commons.wikimedia.org/wiki/File:TMI-2_control_panel.png"||!q["285:2"]?.reject?.includes("Nuclear_Regulatory_Commission_inspector")||q["285:2"]?.max_safe_width_if_preview_known!==604)bad("NARA inspector stale candidate");
if(q["285:5"]?.relationship!=="RELATED_THREE_MILE_ISLAND_NOT_IDENTICAL_PUBLICITY_PHOTO")bad("285:5 false same-photo");
if(q["287:5"]?.relationship!=="MATCHES_OLD_NEW_BRIDGES_ALT_BUT_DIFFERENT_PHOTO"||!q["287:5"]?.publisher_relocated?.startsWith("https://media.stpetecatalyst.com/"))bad("Skyway chronology/host conflation");
if(q["418:1"]?.relationship!=="EXACT_VIRIN_MATCH_BINARY_PIXELS_UNVERIFIED"||!q["418:1"]?.src?.endsWith("210330-G-DE713-0002.JPG"))bad("Coast Guard VIRIN");
if(q["418:2"]?.preview?.join("x")!=="600x463"||!q["418:2"]?.detail?.includes("1946"))bad("Scotch Cap date/geometry");
if(q["407:1"]?.relationship!=="OFFICIAL_USGS_ORIGINAL_LINK_EQUALS_PUBLISHED_SRC")bad("USGS exact original");
if(d.release?.max_width!==960||d.release?.no_upscale!==true||d.release?.pr_site_qa!==154||d.release?.pr_media!==183||d.release?.production_changes!==0)bad("release gate");
if(d.baseline?.alleged_broken_browser_confirmed!==false||d.baseline?.weight_savings_measured!==false||d.baseline?.oversized_original_storage_bytes!==43522829)bad("claims");
return {ok:!e.length,errors:e};
}
module.exports={check};
if(require.main===module){const fs=require("node:fs");const p=process.argv[2];if(!p){console.error("Pass manifest path");process.exit(2)}const r=check(JSON.parse(fs.readFileSync(p,"utf8")));console.log(JSON.stringify(r));if(!r.ok)process.exit(1)}
