'use strict';
// Offline safety validator for five previously unresolved Navy-image source slots.
function validateBatch(d){
 const errors=[];
 const err=(s)=>errors.push(s);
 if(d?.schema!=="fv-navy-five-gap-closure-v1")err("schema");
 if(d?.baseline?.ledger_blob_sha!=="fda8819e86771cfd03a55a9ff252618127b0e420")err("baseline pinned blob");
 if(d?.baseline?.original_site_posts!==66||d?.baseline?.original_site_inline_images!==361)err("site cohort");
 if(d?.baseline?.visitor_verified_broken_count!==null||d?.baseline?.measured_savings_percent!==null)err("unsupported live claims");
 if(d?.policy?.max_preview_width!==960||d?.policy?.no_upscale!==true||d?.policy?.publication_allowed!==false||d?.policy?.wordpress_writes_allowed!==false||d?.policy?.downloads_allowed!==false||d?.policy?.third_party_cache_allowed!==false)err("safety policy");
 const fixed=["274:1","274:2","280:1","280:4","288:2"];
 if(!Array.isArray(d?.records)||d.records.length!==5)err("row count");
 const rmap=new Map((d?.records||[]).map(r=>[r.slot,r]));
 if(rmap.size!==5||fixed.some(k=>!rmap.has(k)))err("row identity");
 const expectedOriginals={
 "274:1":"1485804525424.jpg","274:2":"1701176168705.jpg","280:1":"1514467381634.jpg","280:4":"image.img.jpg","288:2":"1564510769845.jpg"
 };
 for(const k of fixed){
 const r=rmap.get(k);if(!r)continue;
 if(r.post_id!==Number(k.split(":")[0])||!r.original_src?.startsWith("https://www.history.navy.mil/")||!r.original_src.endsWith(expectedOriginals[k]))err(k+" original URL");
 if(!r.post_url?.startsWith("https://finalvestige.com/")||typeof r.original_alt!=="string"||!r.original_alt.length)err(k+" article mapping");
 if(r.evidence?.published_origin_http_status!==null||r.evidence?.catalog_http_status!==null||r.evidence?.guest_http_status!==null||r.evidence?.guest_natural_pixels!==null||r.evidence?.guest_current_src!==null||r.evidence?.guest_cold_wire_bytes!==null||r.evidence?.visitor_broken!==null||r.evidence?.exact_binary_match!==false)err(k+" fabricated HTTP/image evidence");
 if(r.rights?.clearance!=="HOLD_ITEM_LEVEL"||r.rights?.can_cache!==false||r.rights?.can_rehost!==false)err(k+" rights gate");
 if(Object.values(r.actions||{}).some(v=>v!==false)||Object.keys(r.actions||{}).length!==5)err(k+" operations gate");
 if(k==="280:4"){if(r.primary_candidate!==null||r.alternatives?.length!==2||r.alternatives.some(a=>a.review!=="SUBJECT_ONLY_NOT_MATCHED"||a.preview_candidate!==null||a.date!=="1969-05-12"))err(k+" image cannot be assigned");continue}
 const c=r.primary_candidate;
 if(!c?.catalog_id||!c.catalog_url?.startsWith("https://www.history.navy.mil/")||c.identity_review.includes("BINARY_VERIFIED"))err(k+" catalog");
 const master=c?.high_master_pixels, p=c?.preview_candidate;
 if(k==="280:1"){if(master!==null||p!==null)err(k+" unknown geometry must remain unknown")}
 else if(!Array.isArray(master)||master.length!==2||master.some(n=>!Number.isInteger(n)||n<1000)||!p||p.width>960||p.width>master[0]||p.height!==Math.round(master[1]*p.width/master[0])||p.delivered_crop_confirmed!==false||p.output_generated!==false)err(k+" unsafe geometry");
 }
 if(d?.results?.official_item_candidates!==4||d?.results?.exact_binary_verified!==0||d?.results?.unmatched_originals!==1)err("rollup");
 return {ok:errors.length===0,errors};
}
module.exports={validateBatch};
if (require.main===module){const fs=require('node:fs');const path=require('node:path');const data=JSON.parse(fs.readFileSync(path.join(__dirname,'navy_five_gap_closure_20261106.json'),'utf8'));const output=validateBatch(data);console.log(JSON.stringify(output));if(!output.ok)process.exitCode=1;}
