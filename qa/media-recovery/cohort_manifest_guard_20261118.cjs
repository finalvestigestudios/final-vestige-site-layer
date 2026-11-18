"use strict";
const {createHash}=require("node:crypto");
const manifest=require("./cohort_61_66_manifest_20261118.json");
const MANIFEST_SHA256=createHash("sha256").update(JSON.stringify(manifest)).digest("hex");
const rowsFor=(cohort)=>cohort==="historic-61"?manifest.rows.filter(r=>r.in_historic_61===true):cohort==="current-66"?manifest.rows.slice():[];
function validateManifest(m=manifest){
 const problems=[];
 if(!m||m.schema!=="fv-fixed-image-cohorts-v1"||!Array.isArray(m.rows))return ["schema"];
 const ids=new Set(),urls=new Set();
 for(const r of m.rows){
  if(!Number.isSafeInteger(r.post_id)||r.post_id<1||ids.has(r.post_id))problems.push("duplicate_post_id");
  ids.add(r.post_id);
  if(typeof r.url!=="string"||!/^https:\/\/finalvestige\.com\//.test(r.url)||urls.has(r.url))problems.push("invalid_post_url");
  urls.add(r.url);
  if(!Number.isSafeInteger(r.img_slots)||r.img_slots<0||r.img_slots>100)problems.push("invalid_image_count");
  if(r.in_historic_61===true&&r.img_slots!==r.historic_source_img_count)problems.push("historic_image_count_drift");
  if(r.in_historic_61===false&&r.historic_source_img_count!==null)problems.push("new_post_historic_count");
 }
 const old=m.rows.filter(r=>r.in_historic_61===true),newRows=m.rows.filter(r=>r.in_historic_61===false);
 if(m.rows.length!==66||old.length!==61||newRows.length!==5)problems.push("post_totals");
 if(m.rows.reduce((a,r)=>a+r.img_slots,0)!==361||old.reduce((a,r)=>a+r.img_slots,0)!==355)problems.push("image_totals");
 if(newRows.map(r=>r.post_id).sort((a,b)=>a-b).join(",")!=="1917,1920,1922,1924,1926"||newRows.reduce((a,r)=>a+r.img_slots,0)!==6)problems.push("delta");
 if(m.historical_61?.git_blob!=="76aa63ffaa299a6e6878edc1b66e637fa6f058ab"||!Array.isArray(m.current_66?.git_blobs)||m.current_66.git_blobs.length!==9||m.current_66.git_blobs.some(x=>!/^[a-f0-9]{40}$/.test(x.sha||"")))problems.push("source_pinning");
 return [...new Set(problems)];
}
function verifyCapture(c,cohort){
 const expectedRows=rowsFor(cohort);
 if(!expectedRows.length)return ["unknown_cohort"];
 if(!c||!Array.isArray(c.pages))return ["pages_missing"];
 const issues=[],expected=new Map(expectedRows.map(r=>[String(r.post_id),r])),seen=new Set();
 if(c.pages.length!==expectedRows.length)issues.push("page_count");
 for(const p of c.pages){
  const id=String(p?.post_id??"");
  if(seen.has(id)){issues.push("duplicate_post");continue;}
  seen.add(id);
  const rec=expected.get(id);
  if(!rec){issues.push("unexpected_post");continue;}
  if(p.url!==rec.url)issues.push("post_url_drift");
  if(!Array.isArray(p.images)||p.images.length!==rec.img_slots){issues.push("inline_slot_count");continue;}
  const slots=new Set(p.images.map(x=>x?.asset_id));
  if(slots.size!==rec.img_slots)issues.push("duplicate_inline_slot");
  for(let i=0;i<rec.img_slots;i++)if(!slots.has(id+":"+i))issues.push("slot_identity");
 }
 if([...expected.keys()].some(id=>!seen.has(id)))issues.push("missing_posts");
 return [...new Set(issues)];
}
const integrity=validateManifest();
if(integrity.length)throw new Error("Corrupt pinned cohort manifest: "+integrity.join(","));
module.exports={MANIFEST_SHA256,rowsFor,validateManifest,verifyCapture};
