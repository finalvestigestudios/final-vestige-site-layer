#!/usr/bin/env node
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const assert = (condition,message) => {if(!condition)throw new Error(message)};
function validate(m,c){
  assert(m.schema === "fv-coastal-12-source-evidence-v1","wrong schema");
  assert(m.origin_census_blob_sha === "92a904c8da1ace1f972b2f00adf1a4847dde2b99","census SHA mismatch");
  assert(Array.isArray(m.rows) && m.rows.length===12 && m.counts.rows===12,"row count");
  assert(m.counts.previously_researched===2 && m.counts.incrementally_researched===10,"research counts");
  const source = new Map(c.rows.map(r=>[r.slot,r])), seen=new Set(), counts={IMAGE_RENDERED_WEB_TOOL:0,WEB_OPEN_403:0,WEB_OPEN_INACCESSIBLE:0};
  let prior=0;
  for(const row of m.rows) {
    const original=source.get(row.slot);
    assert(original && [292,418].includes(row.post_id),"slot not in frozen census");
    assert(!seen.has(row.slot),"duplicate slot");seen.add(row.slot);
    assert(row.post_id===original.post_id && row.original_url===original.stored_url && row.post_url===original.post_url && row.source_upstream_host===original.origin_host,"source URL/host drift");
    assert(row.prior_researched_in_288===original.researched,"prior-research drift"); prior+=Number(row.prior_researched_in_288);
    const t=row.retrieval_observation;
    assert(t.service==="INDEPENDENT_WEB_OPEN_NOT_ORIGIN_HTTP" && t.date_utc==="2026-11-09" && /^turn[0-9]+view[0-9]+$/.test(t.tool_reference),"invalid retriever provenance");
    assert(Object.hasOwn(counts,t.result),"unsupported retrieval result");counts[t.result]++;
    for(const field of ["visitor_http_status","visitor_decoded_px","visitor_transferred_bytes","visitor_broken"]) assert(t[field]===null,"fabricated visitor measurement");
    for(const field of ["binary_download","cdn_cache","wordpress_upload","post_block_rewrite","homepage_visual_change"]) assert(row.release[field]===false,"unsafe release flag");
    const a=row.candidate;
    assert(a.exact_binary_match_confirmed===false && a.rights_cleared===false,"unapproved rights or identity");
    assert(a.relationship && a.scene_integrity && a.rights_review && a.authority,"missing candidate constraints");
    if(a.archival_native_dimensions_px){
      assert(row.slot==="292:3","unsupported native size claim");
      assert(a.archival_native_dimensions_px[0]===2820 && a.archival_native_dimensions_px[1]===1891,"source catalog dimension drift");
      assert(a.conditional_960_max_rendition_px[0]===960 && a.conditional_960_max_rendition_px[1]===644,"incorrect ratio");
    } else assert(a.conditional_960_max_rendition_px===null,"invented derivative dimensions");
    if(a.filename_rendition_dimensions_hint_px)assert(["292:0","418:0"].includes(row.slot),"undocumented filename geometry");
  }
  assert(prior===2,"prior total");
  assert(counts.IMAGE_RENDERED_WEB_TOOL===7 && counts.WEB_OPEN_403===3 && counts.WEB_OPEN_INACCESSIBLE===2,"retrieval totals");
  assert(m.counts.web_tool_rendered===7&&m.counts.web_tool_http_403===3&&m.counts.web_tool_inaccessible===2&&m.counts.confirmed_guest_failures===0,"summary fabricates evidence");
  return {rows:seen.size,new_slots:seen.size-prior,retrieval:counts};
}
if(require.main===module){
  const root=process.cwd(), file=process.argv[2]||"qa/media-recovery/coastal_scotch_cap_prinsendam_12_20261109.json";
  const censusPath=process.argv[3]||"qa/media-recovery/offsite_upstream_288_20261109.json";
  try {
    const result=validate(JSON.parse(fs.readFileSync(path.resolve(root,file),"utf8")),JSON.parse(fs.readFileSync(path.resolve(root,censusPath),"utf8")));
    console.log("PASS",JSON.stringify(result));
  } catch(e){ console.error("FAIL",e.message); process.exitCode=1; }
}
module.exports={validate};
