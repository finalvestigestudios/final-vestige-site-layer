"use strict";
// Offline, adversarial no-publication tests. Also runnable as a dependency-injected
// V8 test when full Node/Chromium is unavailable.
function run(validate, audit, frozen){
  let passed=0;
  function ok(cond,label){if(!cond)throw Error("FAIL "+label);passed++;}
  ok(validate(audit,frozen).length===0,"real ledger accepted");
  ok(audit.rows.length===6,"six official NPS sources");
  ok(audit.rows.every(r=>r.independent_viewer.browser_http_status===null),"no invented visitor status");
  ok(audit.rows.every(r=>r.release.wp_upload_authorized===false),"no WordPress uploads");
  ok(audit.rows.every(r=>r.archival.item_public_domain_proven===false),"rights per item held");
  const mutationCases=[
    ["source src",d=>d.rows[0].source_url="https://www.nps.gov/poch/incorrect.jpg"],
    ["source alt",d=>d.rows[1].original_alt="Some unrelated ship"],
    ["source ID",d=>d.rows[3].key="211:2"],
    ["post id",d=>d.post.id=999],
    ["post status",d=>d.post.status="draft"],
    ["pinned source SHA",d=>d.frozen_source.git_blob_sha="0000000"],
    ["known collection ID",d=>d.rows[2].archival.catalog_collection_ref="POCH 9.999"],
    ["fabricated PD",d=>d.rows[4].archival.item_public_domain_proven=true],
    ["rights approval",d=>d.rows[5].archival.rights_review_required=false],
    ["non NPS candidate catalog",d=>d.rows[0].archival.catalog_url="https://untrusted.test/shot.jpg"],
    ["wrong image host",d=>d.rows[3].original_host="evil.test"],
    ["invented origin 200",d=>d.rows[2].independent_viewer.origin_http_status=200],
    ["invented browser 404",d=>d.rows[2].independent_viewer.browser_http_status=404],
    ["invented decode",d=>d.rows[2].independent_viewer.browser_decode_success=true],
    ["invented natural width",d=>d.rows[2].independent_viewer.browser_natural_width_px=1024],
    ["invented wire bytes",d=>d.rows[2].independent_viewer.cdp_encoded_data_bytes=120000],
    ["fabricated guest chrome",d=>d.status_method.guest_chrome_used=true],
    ["fabricated transfer scan",d=>d.status_method.actual_cdp_encoded_bytes_measured=1],
    ["invented broken count",d=>d.status_method.visitor_facing_failures_confirmed=1],
    ["false 76 percent proof",d=>d.baseline.reported_76_percent_image_weight_reduction_unmeasured=false],
    ["false repairs",d=>d.baseline.production_repairs=1],
    ["wrong percent inventory",d=>d.baseline.external_origin_slots=286],
    ["960 width exceeded",d=>d.rows[0].derivative.max_width_px=1200],
    ["unverified upscale",d=>d.rows[0].derivative.no_upscale=false],
    ["invented intrinsic decode",d=>d.rows[0].derivative.source_intrinsic_dimensions_verified=true],
    ["false html dimensions",d=>d.rows[0].derivative.html_geometry_only_960_dimensions=[960,900]],
    ["invented trial dimensions",d=>d.rows[4].derivative.html_geometry_only_960_dimensions=[960,840]],
    ["unauthorized WordPress upload",d=>d.rows[0].release.wp_upload_authorized=true],
    ["unauthorized caching",d=>d.rows[0].release.cache_authorized=true],
    ["unauthorized post rewrite",d=>d.rows[0].release.post_rewrite_authorized=true],
    ["unauthorized image swap",d=>d.rows[0].release.automatic_swap_authorized=true],
    ["false readback coverage",d=>d.read_only_live_wp.exact_alt_matches=5],
    ["unsupported exact query tested",d=>d.rows[4].independent_viewer.exact_published_query_tested=true],
    ["fabricated renderer success",d=>d.rows[4].independent_viewer.observation="browser_200"]
  ];
  for(const [label,change] of mutationCases){
    const d=JSON.parse(JSON.stringify(audit));change(d);
    ok(validate(d,frozen).length>0,label+" rejected");
  }
  return {passed,mutations:mutationCases.length,kind:"isolated_source_only",visitor_browser_run:false};
}
module.exports={run};
if(require.main===module){
  const fs=require("node:fs"),path=require("node:path");
  const here=__dirname;
  const v=require("./validate_port_chicago_211_20261104.cjs");
  const d=JSON.parse(fs.readFileSync(path.join(here,"port_chicago_211_nps_primary_20261104.json"),"utf8"));
  const f=JSON.parse(fs.readFileSync(path.join(here,"parts","06.json"),"utf8"));
  console.log(JSON.stringify(run(v.validate,d,f)));
}
