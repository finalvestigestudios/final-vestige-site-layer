"use strict";
// Offline custody validator: no network or WordPress writes. Source ledger Git blob 41a2b5cc5c2a14420927312d6e996133e46f7b2f.
const fs=require("node:fs");const path=require("node:path");
const verify=function verify(doc,source){
 const errs=[];const fail=m=>errs.push(m);
 if(doc.schema!=="fv-oversize-cross-surface-noninline-v1")fail("schema");
 if(doc.observed_date_pt!=="2026-11-15")fail("date");
 if(doc.source_20_record_git_blob_sha!=="41a2b5cc5c2a14420927312d6e996133e46f7b2f")fail("source SHA");
 if(doc.published_post_featured_fields_examined!==66||doc.published_page_featured_fields_examined!==92)fail("listed scope");
 if(JSON.stringify(doc.individual_page_bodies_examined)!=="[234,85,2429]")fail("body scope");
 if(doc.total_noninline_originals!==9||doc.total_noninline_original_storage_bytes!==25904837)fail("totals");
 const expected={"2640":["published_post_featured",1917,"publish"],"2636":["published_post_featured",1924,"publish"],"2638":["published_post_featured",1920,"publish"],"2637":["published_post_featured",1926,"publish"],"293":["published_page_inline",234,"publish"],"405":["draft_page_inline",85,"draft"],"2432":["draft_page_inline",2429,"draft"],"482":["unresolved",null,null],"2148":["unresolved",null,null]};
 const counts={published_post_featured:0,published_page_inline:0,draft_page_inline:0,unresolved:0};let sum=0;
 if(!Array.isArray(doc.records)||doc.records.length!==9)return ["invalid record count"];
 const seen=new Set();
 for(const r of doc.records){
  if(seen.has(r.attachment_id))fail("duplicate ID "+r.attachment_id);seen.add(r.attachment_id);
  const e=expected[String(r.attachment_id)],original=source.records.find(x=>x.attachment_id===r.attachment_id);
  if(!e||!original||original.published_inline_uses.length!==0){fail("not a known noninline asset "+r.attachment_id);continue;}
  if(r.usage_class!==e[0])fail("incorrect usage "+r.attachment_id);
  if(r.title!==original.title||r.original_url!==original.media_original_url||r.original_stored_bytes!==original.stored_original_bytes||r.native_width!==original.native_width||r.native_height!==original.native_height)fail("media identity "+r.attachment_id);
  if(r.review_max_width!==original.conditional_review_width||r.review_proportional_height!==original.conditional_review_height||r.review_max_width>960||r.review_max_width>r.native_width||Math.abs(r.review_proportional_height-r.native_height*r.review_max_width/r.native_width)>1)fail("geometry "+r.attachment_id);
  if(r.published_post_body_inline_uses!==0||r.rights_status!=="HOLD_ITEM_SPECIFIC"||r.cache_authorized!==false||r.wp_upload_authorized!==false||r.post_rewrite_authorized!==false||r.guest_http_status!==null||r.guest_current_src!==null||r.guest_transferred_bytes!==null)fail("claims/permissions "+r.attachment_id);
  if(!Array.isArray(r.verified_usage)||r.verified_usage.length!==(e[1]===null?0:1))fail("usage count "+r.attachment_id);
  if(e[1]!==null){const u=r.verified_usage[0];if(!u||u.object_id!==e[1]||u.object_status!==e[2]||u.type!==(e[0]==="published_post_featured"?"post_featured_media":"page_body_image")||!u.object_url?.startsWith("https://finalvestige.com/"))fail("usage custody "+r.attachment_id);if(e[0]==="published_post_featured"&&u.evidence_attachment_id!==r.attachment_id)fail("featured linkage "+r.attachment_id);if(e[0].includes("page_inline")&&!["data-attachment-id","exact_source_filename"].includes(u.match_method))fail("page proof "+r.attachment_id);}
  counts[e[0]]++;sum+=r.original_stored_bytes;
 }
 if(Object.keys(expected).some(id=>!seen.has(Number(id))))fail("missing IDs");
 if(sum!==doc.total_noninline_original_storage_bytes)fail("byte sum");
 for(const [k,v]of Object.entries(counts))if(doc.usage_counts?.[k]!==v)fail("count "+k);
 if(doc.sitewide_visitor_transfer_reduction_percent!==null||doc.reported_42_broken_guest_verified!==false||doc.production_writes!==0)fail("sitewide unsupported claim");
 if(!Array.isArray(doc.known_limitations)||doc.known_limitations.length<4||!doc.known_limitations.some(x=>x.includes("NOT proven unused")))fail("limit disclosure");
 return errs;
};
module.exports={verify};
if(require.main===module){const root=path.resolve(__dirname,"../..");const doc=JSON.parse(fs.readFileSync(path.join(root,"qa/media-recovery/wp66_oversize_noninline_cross_surface_20261115.json"),"utf8"));const source=JSON.parse(fs.readFileSync(path.join(root,"qa/media-recovery/wp66_132media_20oversized_inline_exposure_20261115.json"),"utf8"));const errs=verify(doc,source);if(errs.length){console.error("FAIL:",errs.join("; "));process.exitCode=1}else console.log("PASS: 9 non-inline oversized images, exact usage and rights HOLD");}
