"use strict";
/** Strict offline schema + source-identity gate. No HTTP requests, no WordPress writes. */
function validateHebgen(a,sourceImages){
 const errors=[];
 const fail=s=>errors.push(s);
 if(!a||a.schema_version!==1||a.post_id!==407) fail("schema or post");
 if(a?.inventory_source?.git_blob_sha!=="48e1ebf07207e948ba5802e714eb39659d2e1c1d") fail("pinned source blob");
 if(a?.inventory_source?.method?.includes("NOT a fresh CMS readback")!==true) fail("fresh CMS overclaim");
 if(!Array.isArray(sourceImages)||sourceImages.length!==8) fail("source census");
 if(!Array.isArray(a?.rows)||a.rows.length!==8) fail("row count");
 const expected=new Map((sourceImages||[]).map(x=>[x.key,x]));
 const seen=new Set();let displayed=0,unsupported=0,inaccessible=0,candidates=0;
 for(const r of a?.rows||[]){
  const x=expected.get(r.key);
  if(!x||seen.has(r.key)||r.slot!==x.slot||r.published_src_from_20261030!==x.source_url||r.published_alt_from_20261030!==x.alt) fail("source identity "+r?.key);
  seen.add(r.key);
  if(!/^https:\/\/d9-wret\.s3\.us-west-2\.amazonaws\.com\//.test(r.published_src_from_20261030||"")) fail("source host "+r.key);
  if(!/^https:\/\/www\.usgs\.gov\/media\/images\//.test(r.official_usgs_catalog_url||"")) fail("authoritative catalog "+r.key);
  if(r.catalog_reports_public_domain!==true||typeof r.creator_and_rights_note!=="string"||!r.creator_and_rights_note) fail("catalog custody "+r.key);
  if(r.copyright_clearance!=="HOLD_ITEM_REVIEW"||r.wp_media_cache_approved!==false||r.wordpress_production_write_approved!==false||r.identical_binary_or_crop_verified!==false) fail("unsafe release "+r.key);
  const b=r.guest_browser||{};
  if(["http_status","final_current_src","natural_width_px","decoded","mime","cdp_encoded_bytes","visibly_broken"].some(k=>b[k]!==null)) fail("invented guest evidence "+r.key);
  const w=r.exact_source_retriever||{};
  if(w.method!=="web.open (independent renderer, NOT guest browser HTTP)"||w.observed_origin_http_status!==null||w.observed_response_mime!==null) fail("invented origin status "+r.key);
  const o=w.observation;
  if(o==="DISPLAYED"){displayed++;if(w.wrapper_error_code!==null)fail("display code "+r.key);}
  else if(o==="RETRIEVER_UNSUPPORTED_BINARY_OCTET_STREAM"){unsupported++;if(r.key!=="407:1"||w.wrapper_error_code!==400)fail("octet wrapper "+r.key);}
  else if(o==="RETRIEVER_INACCESSIBLE_NO_STATUS"){inaccessible++;if(r.key!=="407:3"||w.wrapper_error_code!==null)fail("inaccessible code "+r.key);}
  else fail("fabricated retriever observation "+r.key);
  const d=r.conditional_derivative||{},dims=r.source_intrinsic_dimensions_px||{};
  if(d.max_width_px!==960||d.target_width_px!==null||d.target_height_px!==null||d.no_upscale!==true||dims.width!==null||dims.height!==null) fail("fabricated native geometry "+r.key);
  if(r.official_rendition_candidate_url){
   candidates++;
   if(!["407:1","407:3"].includes(r.key)||!r.official_rendition_candidate_url.startsWith("https://d9-wret.s3.us-west-2.amazonaws.com/")||r.official_rendition_retriever_observation!=="DISPLAYED_FROM_OFFICIAL_USGS_LINK") fail("candidate mislabel "+r.key);
  }else if(r.official_rendition_retriever_observation!==null) fail("candidate with no URL "+r.key);
 }
 for(const key of expected.keys())if(!seen.has(key))fail("missing "+key);
 const s=a?.summary||{};
 if(displayed!==6||unsupported!==1||inaccessible!==1||candidates!==2||s.slots!==8||s.exact_urls_displayed!==6||s.exact_url_octet_stream_retriever_unsupported!==1||s.exact_url_inaccessible_without_origin_status!==1||s.official_usgs_catalog_matches!==8||s.official_usgs_renditions_independently_displayed!==2||s.guest_browser_failures_confirmed!==0||s.observed_actual_origin_http_statuses!==0||s.measured_transfer_bytes!==0||s.production_images_fixed!==0||s.sitewide_42_report_confirmed!==false||s.sitewide_76_percent_measured!==false)fail("unsubstantiated aggregate");
 if(a.release_status!=="HOLD_NEEDS_GUEST_BROWSER_PLUS_RIGHTS_AND_CROP")fail("release gate");
 return {ok:errors.length===0,errors,checked:a?.rows?.length||0};
}
module.exports={validateHebgen};
if(require.main===module){
 const fs=require("node:fs"),p=require("node:path");
 const dir=__dirname;
 const a=JSON.parse(fs.readFileSync(p.join(dir,"hebgen_407_usgs_octet_cross_transport_20261103.json"),"utf8"));
 const source=JSON.parse(fs.readFileSync(p.join(dir,"parts/02.json"),"utf8")).images.filter(x=>x.post_id===407);
 const res=validateHebgen(a,source);
 console.log(JSON.stringify(res));
 if(!res.ok)process.exitCode=1;
}
