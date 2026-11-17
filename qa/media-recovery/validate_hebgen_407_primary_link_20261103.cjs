"use strict";
/** Read-only exact original-link comparison. No HTTP, binary download or WordPress operations. */
const PIN="48e1ebf07207e948ba5802e714eb39659d2e1c1d";
const ROOT="https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/";
function validateHebgenPrimary(a,part){
 const errors=[];const check=(c,m)=>{if(!c)errors.push(m)};
 const src=part?.images?.filter(x=>x.post_id===407)||[];
 check(a?.schema_version===1&&a?.post_id===407,"schema");
 check(a?.frozen_census?.git_blob_sha===PIN,"pinned source");
 check(src.length===8&&a?.rows?.length===8,"eight sources");
 check(a?.findings?.exact_usgs_archive_original_link_matches===7&&a?.findings?.published_source_path_discrepancies===1&&a?.findings?.production_changes===0,"summary");
 check(a?.observation_limits?.live_wordpress_read_this_run===false&&a?.observation_limits?.guest_http_status_for_all===null&&a?.observation_limits?.actual_browser_transfer_bytes===null,"invented observation");
 check(a?.observation_limits?.claimed_42_broken_images_verified===false&&a?.observation_limits?.claimed_76_percent_savings_measured===false,"unsupported sitewide claim");
 let exact=0,drift=0;
 (a?.rows||[]).forEach((r,i)=>{
 const x=src[i],q=r.archive,g=r.geometry,rights=r.rights,rel=r.release_gate;
 if(!x){check(false,"extra slot");return}
 check(r.key===x.key&&r.key==="407:"+i&&r.source_url===x.source_url&&r.source_alt===x.alt&&r.source_host===x.source_host,"source tampering "+i);
 check(q?.authority==="U.S. Geological Survey"&&/^https:\/\/www\.usgs\.gov\/media\/images\/[a-z0-9-]+$/.test(q.catalog_url||""),"catalog "+i);
 check(q?.usgs_catalog_original_url?.startsWith(ROOT)&&q?.usgs_catalog_original_url?.split("/").at(-1)===r.source_url?.split("/").at(-1),"unexpected archive candidate "+i);
 const matches=q?.usgs_catalog_original_url===r.source_url;
 check(q?.published_url_equals_usgs_catalog_original_url===matches,"archive identity "+i);
 if(i===1){
  drift++;
  check(!matches&&r.source_url===ROOT+"img7535.jpg"&&q?.usgs_catalog_original_url===ROOT+"thumbnails/image/img7535.jpg","407:1 path drift");
  check(q?.relationship==="PUBLISHED_PATH_DIFFERS_POTENTIAL_REPAIR_CANDIDATE"&&r.independent_source_observation==="RETRIEVER_REJECTED_ORIGINAL_AS_OCTET_STREAM","407:1 transport");
 }else{
  exact++;
  check(matches&&q?.relationship==="URL_EXACT_MATCH_BINARY_NOT_HASHED"&&r.independent_source_observation==="USGS_ARCHIVE_ORIGINAL_VISIBLE_IN_INDEPENDENT_VIEWER","exact rendered link "+i);
 }
 check(rights?.catalog_label==="Public Domain"&&rights?.specific_rights_and_attribution_check==="HOLD"&&rights?.local_cache_approved===false&&rights?.wordpress_edit_approved===false&&rights?.master_binary_sha256===null,"rights bypass "+i);
 check(rel?.production_authorized===false&&rel?.needs_guest_chrome_currentSrc_http_mime_decode===true&&rel?.needs_same_scene_crop_verification===true&&rel?.needs_per_item_rights_and_credit_review===true&&rel?.needs_staging_and_rollback_plan===true,"release bypass "+i);
 check(r.numeric_origin_http_status===null&&r.guest_http_status===null&&r.guest_natural_width===null&&r.guest_current_src===null&&r.transferred_bytes===null,"fabricated status "+i);
 check(g?.stored_html_width===x.width_px&&g?.stored_html_height===x.height_px&&g?.original_binary_dimensions_verified===false&&g?.no_upscale===true,"intrinsic geometry "+i);
 const w=Number.isInteger(x.width_px)?Math.min(960,x.width_px):null;
 const h=w?Math.round(w*x.height_px/x.width_px):null;
 check(g?.conditional_max_width_960===w&&g?.conditional_aspect_preserving_height===h,"960px computation "+i);
 });
 check(exact===7&&drift===1,"count");
 return {ok:errors.length===0,errors,exact,drift};
}
module.exports={validateHebgenPrimary};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
 const raw=fs.readFileSync(path.join(__dirname,"parts/02.json"));
 const sha=crypto.createHash("sha1").update(Buffer.concat([Buffer.from("blob "+raw.length+"\0"),raw])).digest("hex");
 if(sha!==PIN)throw Error("Git blob mismatch "+sha);
 const a=JSON.parse(fs.readFileSync(path.join(__dirname,"hebgen_407_primary_path_audit_20261103.json"),"utf8"));
 const outcome=validateHebgenPrimary(a,JSON.parse(raw.toString("utf8")));
 console.log(JSON.stringify(outcome));
 if(!outcome.ok)process.exitCode=1;
}
