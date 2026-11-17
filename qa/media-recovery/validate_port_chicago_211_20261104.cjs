"use strict";
// Source-only release guard for the six Port Chicago images. No networking, file writes,
// scraping, WordPress mutation, or inference of image HTTP status.
const EXPECTED=["POCH 2.078","POCH 2.115","POCH 2-113","POCH 2-056","U.S. Navy / National Archives","POCH 2-055"];
const VIEWER_OUTCOMES=new Set(["nps_link_internal_retriever_error","nps_image_variant_displayed","nps_original_unparameterized_image_displayed"]);
function validate(d, frozen){
  const errors=[];
  const bad=(message)=>errors.push(message);
  if(!d||typeof d!=="object")return ["audit object missing"];
  if(d.post?.id!==211||d.post?.status!=="publish")bad("post identity or status changed");
  if(d.frozen_source?.path!=="qa/media-recovery/parts/06.json"||d.frozen_source?.git_blob_sha!=="0f3dfe398a76838049cebba7cb773d5c5a0c8c69")bad("pinned frozen source changed");
  const base=d.baseline||{};
  if(base.published_posts!==61||base.image_slots!==355||base.external_origin_slots!==288||base.original_wp_files_gt_1_5_mib!==13||base.reported_broken_images_unverified!==42||base.reported_76_percent_image_weight_reduction_unmeasured!==true||base.production_repairs!==0)bad("baseline or performance-claim gate changed");
  const live=d.read_only_live_wp||{};
  if(live.images_in_html!==6||live.exact_source_matches!==6||live.exact_alt_matches!==6||live.images_with_width_and_height!==5||live.images_missing_width_or_height!==1)bad("live WP readback invariant mismatch");
  const st=d.status_method||{};
  if(st.origin_http_statuses_measured!==0||st.guest_chrome_used!==false||st.visitor_facing_failures_confirmed!==0||st.actual_cdp_encoded_bytes_measured!==0)bad("unproven browser/HTTP/CDP claim");
  if(!Array.isArray(d.rows)||d.rows.length!==6){bad("six image records required");return errors;}
  const frozenRows=frozen&&Array.isArray(frozen.images)?frozen.images.filter(x=>x.post_id===211).sort((a,b)=>a.slot-b.slot):null;
  if(frozenRows&&frozenRows.length!==6)bad("frozen census lacks six rows");
  const seen=new Set();
  d.rows.forEach((r,i)=>{
    if(!r||typeof r!=="object"){bad("missing row "+i);return;}
    if(r.key!==`211:${i}`||r.post_id!==211||r.slot!==i||seen.has(r.key))bad("row identity "+i);
    seen.add(r.key);
    if(typeof r.source_url!=="string"||!r.source_url.startsWith("https://www.nps.gov/")||r.original_host!=="www.nps.gov")bad("unapproved image host "+i);
    if(frozenRows&&(!frozenRows[i]||r.source_url!==frozenRows[i].source_url||r.original_alt!==frozenRows[i].alt||r.html_declared_width_px!==frozenRows[i].width_px||r.html_declared_height_px!==frozenRows[i].height_px))bad("source/ALT/HTML geometry changed "+i);
    if(r.live_wordpress_exact_src!==true||r.live_wordpress_exact_alt!==true)bad("unverified live source "+i);
    const cat=r.archival||{};
    if(cat.catalog_collection_ref!==EXPECTED[i]||typeof cat.catalog_url!=="string"||!cat.catalog_url.startsWith("https://www.nps.gov/poch/")||cat.catalog_primary_source_nps!==true||cat.rights_review_required!==true||cat.item_public_domain_proven!==false)bad("catalog or rights unsupported "+i);
    const v=r.independent_viewer||{};
    if(!VIEWER_OUTCOMES.has(v.observation)||typeof v.observed_url!=="string"||!v.observed_url.startsWith("https://www.nps.gov/")||v.exact_published_query_tested!==false)bad("retriever method unsupported "+i);
    for(const f of ["origin_http_status","browser_http_status","browser_decode_success","browser_natural_width_px","browser_natural_height_px","cdp_encoded_data_bytes"]){if(v[f]!==null)bad("fabricated visitor value "+i+"."+f);}
    const der=r.derivative||{};
    if(der.max_width_px!==960||der.no_upscale!==true||der.source_intrinsic_dimensions_verified!==false||der.wordpress_derivative_not_created!==true)bad("image sizing or processing promise "+i);
    const dims=der.html_geometry_only_960_dimensions;
    const known=r.html_declared_width_px!=null&&r.html_declared_height_px!=null;
    if(known){
      if(!Array.isArray(dims)||dims.length!==2||dims[0]!==960||dims[1]!==Math.round(960*r.html_declared_height_px/r.html_declared_width_px))bad("HTML-only aspect candidate mismatch "+i);
    }else if(dims!==null)bad("invented dimensions "+i);
    const release=r.release||{};
    for(const f of ["wp_upload_authorized","cache_authorized","post_rewrite_authorized","automatic_swap_authorized"]){if(release[f]!==false)bad("unauthorized release "+i+"."+f);}
  });
  return errors;
}
module.exports={validate,EXPECTED};
if(require.main===module){
  const fs=require("node:fs"),path=require("node:path");
  const dir=__dirname;
  const d=JSON.parse(fs.readFileSync(path.join(dir,"port_chicago_211_nps_primary_20261104.json"),"utf8"));
  const f=JSON.parse(fs.readFileSync(path.join(dir,"parts","06.json"),"utf8"));
  const errs=validate(d,f);
  if(errs.length){console.error(errs.join("\n"));process.exitCode=1;}else console.log("PASS: six Port Chicago sources, rights, and HTTP abstention");
}
