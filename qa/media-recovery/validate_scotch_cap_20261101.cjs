"use strict";
function validate(d){
 const errors=[],add=(x)=>errors.push(x);
 const expected={
 "418:0":{src:"https://www.history.uscg.mil/Portals/6/2_%20new%20and%20old%20lighthouses%2019849609_web1_1_-Scotch-Cap-lighthouse-1200x984.jpg",candidate:"https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/2_-new-and-old-lighthouses-19849609-e1728394749751-600x480.jpg",dims:[600,480],outcome:"NO_ORIGIN_STATUS"},
 "418:1":{src:"https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG",candidate:"https://media.defense.gov/2021/Mar/30/2002905913/-1/-1/0/210330-G-DE713-0002.JPG",dims:null,outcome:"RETRIEVER_403"},
 "418:2":{src:"https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg",candidate:"https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/5_-Scotch_Cap_debris2_1946-600x463.jpg",dims:[600,463],outcome:"RETRIEVER_403"}
 };
 if(d.schema_version!==1||d.date!=="2026-11-01")add("schema/date");
 const c=d.counts||{};
 if(c.posts!==61||c.inline_source_references!==355||c.external_references!==288||c.wp_originals_over_1_5MiB!==13||c.alleged_broken_unverified!==42||c.claimed_savings_unmeasured_percent!==76||c.confirmed_production_repairs!==0)add("frozen baseline");
 if(!Array.isArray(d.rows)||d.rows.length!==3){add("rows");return {ok:false,errors};}
 const seen=new Set();
 for(const r of d.rows){
  const e=expected[r.key];
  if(!e||seen.has(r.key)){add("unknown/duplicate key");continue;}
  seen.add(r.key);
  if(r.published_src!==e.src||r.candidate_url!==e.candidate)add("photo identity "+r.key);
  if(r.post_url!=="https://finalvestige.com/2026/08/20/the-lighthouse-was-gone-at-dawn-1946-tsunami/"||!r.alt?.length)add("post/alt "+r.key);
  if(r.retriever!==e.outcome||r.retriever_code!==(e.outcome==="RETRIEVER_403"?403:null)||r.preview!=="DISPLAYED"||r.preview_source!=="WEB_IMAGE_RETRIEVER_NOT_VISITOR_BROWSER")add("retriever provenance "+r.key);
  if(!r.guest_browser||Object.values(r.guest_browser).some(v=>v!==null))add("invented visitor evidence "+r.key);
  if(r.rights!=="HOLD"||r.image_master_sha256!==null||r.identity_binary_verified!==false||r.wp_media_upload_authorized!==false||r.wp_post_edit_authorized!==false||r.cache_authorized!==false)add("unsafe publication "+r.key);
  if(r.max_width_px!==960||r.no_upscale!==true)add("geometry gate "+r.key);
  if(JSON.stringify(r.preview_dimensions_px)!==JSON.stringify(e.dims)||JSON.stringify(r.target_dimensions_px)!==JSON.stringify(e.dims))add("derivative dimensions "+r.key);
  if(!r.candidate_kind?.includes(r.key==="418:1"?"VIRIN":r.key==="418:2"?"debris2":"scene"))add("historical scene rationale "+r.key);
 }
 if(seen.size!==3)add("missing key");
 if(!Array.isArray(d.excluded_wrong_photos)||d.excluded_wrong_photos.length!==2||!d.excluded_wrong_photos.some(r=>r.url.includes("debris1_1946"))||!d.excluded_wrong_photos.some(r=>r.url.includes("debris3_1946")))add("lookalike exclusions");
 if(!d.publication_gate||d.publication_gate.approved!==false||d.publication_gate.wordpress_writes!==false||d.publication_gate.downloaded_photos!==false||d.publication_gate.claimed_wire_bytes_saved!==null||d.publication_gate.caching!=="HOLD")add("final publication gate");
 return {ok:errors.length===0,errors};
}
module.exports={validate};
if(require.main===module){const fs=require("node:fs"),path=require("node:path");const data=JSON.parse(fs.readFileSync(path.join(__dirname,"scotch_cap_museum_sourcecrosswalk_20261101.json"),"utf8"));const v=validate(data);if(!v.ok){console.error(v.errors);process.exitCode=1;}else console.log("scotch cap source ledger PASS");}
