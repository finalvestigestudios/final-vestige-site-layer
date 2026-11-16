'use strict';
// Offline read-only evidence validation. No network, WordPress, or image file access.
const assess=function assess(d) {
  const errors=[];
  const check=(ok,why)=>{if(!ok)errors.push(why)};
  const exact=(a,b)=>a===b;
  const isNull=x=>x===null;
  check(d.schema==="fv-media-government-figure-route-v1","schema");
  check(d.provenance?.site_qa_pr===154 && d.provenance?.isolated_pr===2747 && d.provenance?.source_blob_sha==="93ed6631518dc0c06253719b61d1cf50b623f6f0","provenance");
  check(d.image?.slot==="285:2" && d.image?.post_id===285,"slot");
  check(d.image?.authored_src==="https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg","original");
  check(d.image?.wp_proxy_src==="https://i0.wp.com/blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg?ssl=1","proxy");
  check(d.image?.publisher_figure_number===4 && d.image?.publisher_figure_link===d.image?.authored_src && d.image?.publisher_caption_source==="Nuclear Regulatory Commission","publisher_fig4");
  check(d.image?.official_government_report?.printed_page===97 && d.image.official_government_report.pdf_screenshot_available===false,"government_source");
  const a=d.observations;
  check(Array.isArray(a)&&a.length===3,"observations");
  if(Array.isArray(a)&&a.length===3){
    check(a[0].url===d.image.authored_src && a[0].outcome==="redirected_to_new_host_then_reader_inaccessible" && a[0].retriever_reported_code===500 && a[0].redirected_to==="https://blog.ucs.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg","redirect_custody");
    check(a[1].url===a[0].redirected_to && a[1].outcome==="reader_inaccessible","newhost");
    check(a[2].url===d.candidate?.direct_binary_url && a[2].outcome==="image_visibly_rendered_in_reader","candidate_reader");
    check(a.every(v=>isNull(v.actual_origin_http_status)&&isNull(v.guest_browser_status)&&isNull(v.decoded_native_dimensions_px)&&isNull(v.transferred_bytes)),"unknown_http_not_fake");
  }
  const c=d.candidate||{};
  check(c.catalog_url==="https://commons.wikimedia.org/wiki/File:TMI-2_control_panel.png" && c.direct_binary_url==="https://upload.wikimedia.org/wikipedia/commons/e/ea/TMI-2_control_panel.png" && !c.direct_binary_url.includes("/wiki/"),"direct_png_not_catalog_html");
  check(c.advertised_catalog_width_px===604 && c.advertised_catalog_height_px===590 && c.max_allowed_width_px===960,"catalog_geometry");
  check(c.planned_review_width_px===604 && c.planned_review_height_px===590 && c.planned_review_width_px<=Math.min(c.advertised_catalog_width_px,960),"no_upscale_geometry");
  check(c.visual_integrity==="RELATED_SCENE_DIFFERENT_CAPTION_CROP" && c.binary_sha256===null && c.decoded_master_dimensions_px===null,"identity_not_overclaimed");
  check(c.item_rights_status==="HOLD_INDIVIDUAL_REVIEW" && c.wp_caching_authorized===false && c.wp_upload_authorized===false && c.staging_approval===false,"rights_release_hold");
  const g=d.actual_guest_browser||{};
  check(["currentSrc","http_status","mime_type","natural_width","natural_height","image_decoded","visual_screenshot","transfer_bytes"].every(k=>isNull(g[k])),"guest_missing_not_fabricated");
  const r=d.release||{};
  check(r.decision==="HOLD_NOT_AN_IDENTICAL_REPLACEMENT" && r.allowed_max_width===960 && r.no_upscaling===true,"release_hold");
  check(["production_wordpress_write","external_binary_download","media_rehost","homepage_visual_change","published_block_rewrite","paid_service"].every(k=>r[k]===false),"no_prod_or_licensing_side_effect");
  const p=d.program_context||{};
  check(p.historical_published_posts===61 && p.historical_inline_images===355 && p.current_oversized_original_count_gt_1_5_decimal_mb===20 && p.current_oversized_original_storage_bytes===64385752,"census_stored_not_wire");
  check(p.reported_broken_42_guest_confirmed===false && p.claimed_76_percent_visitor_transfer_savings_measured===false,"no_unsupported_claim");
  return {decision:errors.length?"INVALID":"HOLD",errors,slot:"285:2"};
};
module.exports={assess};
if(require.main===module){const fs=require('node:fs');const path=require('node:path');const file=process.argv[2]||path.join(__dirname,'tmi_2852_commission_figure_20261116.json');const result=assess(JSON.parse(fs.readFileSync(file,'utf8')));process.stdout.write(JSON.stringify(result)+'\n');if(result.decision!=='HOLD')process.exitCode=1;}
