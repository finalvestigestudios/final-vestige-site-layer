"use strict";
const fs=require("node:fs");
const path=require("node:path");
const EXPECTED=[
  ["278:0","https://media.defense.gov/2007/Jan/25/2000519451/-1/-1/0/070125-F-0000Z-099.JPG","The B-24D Lady Be Good lying largely intact in the Libyan Desert after its discovery."],
  ["278:1","https://media.defense.gov/2006/May/30/2000572755/2000/2000/0/050606-F-1234P-012.JPG","The nine members of the Lady Be Good crew posed in front of a B-24 before the 1943 mission."],
  ["278:2","https://upload.wikimedia.org/wikipedia/commons/4/49/0000050606-F-1234P-014.jpg","The preserved wreck of Lady Be Good in the Libyan Desert."],
  ["278:3","https://qmmuseum.army.mil/assets/img/aotm/2012/09_M1910_canteen_1.jpg","The Model 1910 canteen recovered from the Lady Be Good crew's desert trail."],
  ["278:4","https://www.ladybegood.net/diaries/full/Toner_Diary2%20.jpg","A page from Robert Toner's diary recovered with members of the Lady Be Good crew."],
  ["278:5","https://unwritten-record.blogs.archives.gov/wp-content/uploads/sites/6/2017/06/111-c-17240-scaled.jpg","U.S. military investigators examining the Lady Be Good wreck in the Libyan Desert."],
  ["278:6","https://media.defense.gov/2006/Jun/02/2000554420/-1/-1/0/060530-F-1234S-041.JPG","Search and recovery personnel working around Lady Be Good in the Libyan Desert."],
];
function check(a){
 const problems=[];
 if(a?.schema!=="fv-media-lady-be-good-recovery-v1"||a?.post_id!==278)problems.push("schema/post");
 if(a?.rows?.length!==7)problems.push("seven slots");
 if(a?.prior_independent_research?.git_blob_sha!=="cf69fc6666037488012cf9fd48bb204764904e00")problems.push("missed prior PR183 research");
 if(a?.rows?.find(r=>r.slot==="278:6")?.catalog?.url!=="https://www.nationalmuseum.af.mil/Upcoming/Photos/igphoto/2000554420/")problems.push("USAF verified record regression");
 if(a?.measurements?.guest_measurement_performed!==false||a?.measurements?.original_reported_broken_42_verified!==false||a?.measurements?.transfer_reduction_76pct_measured!==false)problems.push("fabricated measurement");
 if(a?.source_inventory?.posts!==61||a?.source_inventory?.images!==355||a?.source_inventory?.offsite!==288)problems.push("frozen cohort");
 const seen=new Set();
 for(const [slot,url,alt] of EXPECTED){
 const r=(a.rows||[]).find(x=>x.slot===slot);
 if(!r){problems.push("missing "+slot);continue;}
 if(seen.has(r.slot))problems.push("duplicate slot");seen.add(r.slot);
 if(r.post_id!==278||r.stored_url!==url||r.original_alt!==alt)problems.push("source identity "+slot);
 if(!r.original_source_fixture||r.original_source_fixture.blob_sha!=="6df3251e5a67a971d87a516a1ba4a0cc32f51f96")problems.push("unfrozen source "+slot);
 if(r.retrieval?.method!=="INDEPENDENT_WEB_VIEWER_NOT_ORIGIN_OR_VISITOR_HTTP"||!["WRAPPER_403","WRAPPER_502","IMAGE_DISPLAYED"].includes(r.retrieval.result))problems.push("retrieval type "+slot);
 const v=r.visitor||{};
 if(["http_status","natural_width","natural_height","wire_bytes","confirmed_broken","cache_state"].some(k=>v[k]!==null))problems.push("invented guest result "+slot);
 if(!r.hold||Object.values(r.hold).some(v=>v!==false))problems.push("unauthorized release "+slot);
 if(r.catalog?.rights==="CLEARED"||r.catalog?.source_match==="VERIFIED_BINARY")problems.push("unsupported rights/binary "+slot);
 const px=r.catalog?.native_px, resized=r.catalog?.conditional_960_px;
 if((px===null)!==(resized===null))problems.push("invented dims "+slot);
 if(px!==null){
  if(!Array.isArray(px)||!Array.isArray(resized)||px.length!==2||resized.length!==2||px.some(n=>!Number.isInteger(n)||n<1)||resized.some(n=>!Number.isInteger(n)||n<1))problems.push("malformed dimensions "+slot);
  else if(resized[0]>960||resized[0]>px[0]||resized[1]>px[1]||Math.abs(resized[1]-(px[1]*resized[0]/px[0]))>0.51)problems.push("invalid 960px "+slot);
 }
 }
 if((a.rows||[]).some(r=>!EXPECTED.some(([s])=>s===r.slot)))problems.push("unexpected row");
 if(a.rows?.find(r=>r.slot==="278:3")?.catalog?.scene_note?.includes("NOT corroborated")!==true)problems.push("canteen false specificity hold");
 if(a.rows?.find(r=>r.slot==="278:5")?.catalog?.scene_note?.includes("POSSIBLE ALT ERROR")!==true)problems.push("NARA alt review hold");
 return problems;
}
if(require.main===module){
 const target=path.join(__dirname,"lady_be_good_278_seven_20261109.json");
 const problems=check(JSON.parse(fs.readFileSync(target,"utf8")));
 console.log(problems.length?"FAIL "+problems.join(" | "):"PASS seven source-locked rights-held Lady Be Good image positions");
 process.exitCode=problems.length?1:0;
}
module.exports={check};
