"use strict";
function assert(v,reason){ if(!v) throw new Error(reason); }
function validate(a,c,p,f){
 assert(a.schema==="fv-media-silver-bridge-258-six-v1","schema");
 assert(a.frozen_cms_fixture.blob_sha==="6df3251e5a67a971d87a516a1ba4a0cc32f51f96","fixture_pin");
 assert(a.preceding_register.blob_sha==="7093fc6f58f085074c0832bf141510b42496dc8e","prior_pin");
 assert(a.reported_42_guest_verified===false&&a.reported_76_percent_wire_savings_measured===false,"fake_site_claim");
 assert(a.status_semantics.guest_browser_http===null&&a.status_semantics.origin_http===null,"fake_status");
 assert(a.rows.length===6&&p.rows.length===288&&c.rows.length===288,"count_source");
 assert(p.counts.researched_unique===228&&p.counts.unresearched===60&&p.counts.total_evidence_records===233,"bad_prior");
 assert(c.counts.researched_unique===234&&c.counts.unresearched===54&&c.counts.total_evidence_records===239&&c.counts.total_external===288,"count_coverage");
 assert(c.counts.oversized_wp_originals_gt_1500000===15&&c.counts.oversized_stored_original_bytes===47096779,"original_bytes_not_visitor_bytes");
 assert(c.counts.reported_42_broken_browser_confirmed===false&&c.counts.wire_reduction_76_percent_measured===false,"unsupported_performance");
 assert(c.prior_228_register.blob_sha==="7093fc6f58f085074c0832bf141510b42496dc8e","prior_register_pin");
 const original=f.images.filter(x=>x.post_id===258),keys=new Set(),mapped=new Map();
 assert(original.length===6,"fixture_six");
 for(const x of a.rows){
  assert(!keys.has(x.slot)&&original.some(z=>z.key===x.slot),"duplicate_or_unknown_slot");
  keys.add(x.slot);mapped.set(x.slot,x);const y=original.find(z=>z.key===x.slot);
  assert(x.published_src===y.source_url&&x.published_alt===y.alt&&x.post_url===y.post_url&&x.source_host===y.source_host,"frozen_source_mismatch");
  assert(["TOOL_INACCESSIBLE_NOT_ORIGIN_STATUS","IMAGE_DISPLAYED_BY_RETRIEVER_NOT_GUEST_HTTP"].includes(x.web_retriever),"invalid_retriever_class");
  for(const k of ["origin_http_status","guest_http_status","guest_current_src","guest_decoded_px","guest_wire_bytes","guest_broken"])assert(x[k]===null,"invented_visitor_result:"+k);
  for(const k of ["exact_binary_match","rights_cleared","download_authorized","cache_authorized","wordpress_media_upload_authorized","post_rewrite_authorized"])assert(x[k]===false,"unauthorized_release:"+k);
  assert(x.license_review.startsWith("HOLD")&&x.catalog_url.startsWith("https://"),"license_or_catalog");
  if(x.catalog_px===null) assert(x.conditional_960px===null,"invented_geometry");
  else { const [w,h]=x.catalog_px,tw=Math.min(960,w);
   assert(Number.isInteger(w)&&Number.isInteger(h)&&w>0&&h>0&&Array.isArray(x.conditional_960px)&&x.conditional_960px[0]===tw&&x.conditional_960px[1]===Math.round(tw*h/w),"incorrect_geometry"); }
 }
 assert(keys.size===6,"missing_slot");
 let touched=0;
 for(let i=0;i<p.rows.length;i++){const old=p.rows[i],now=c.rows[i];
  assert(old.slot===now.slot&&old.stored_url===now.stored_url,"original_source_changed");
  if(!keys.has(now.slot))assert(JSON.stringify(old)===JSON.stringify(now),"unrelated_row_modified");
  else {touched++; const arow=mapped.get(now.slot);assert(old.evidence.length===0&&old.candidate_sources.length===0,"overwrote_evidence");
   assert(now.evidence.length===1&&now.evidence[0].path==="qa/media-recovery/silver_bridge_258_six_ntsb_fhwa_dpla_20261110.json"&&now.evidence[0].blob_sha==="9836935f4db3aaa9a7f73e68576f1d4db92b8c38","evidence_sha");
   assert(now.candidate_sources.length===1&&now.candidate_sources[0].catalog_url===arow.catalog_url&&now.candidate_sources[0].item_rights_cleared===false&&now.candidate_sources[0].exact_image_match_verified===false,"unsafe_candidate");
   for(const k of ["guest_http_status","guest_current_src","guest_decoded_px","guest_wire_bytes","guest_broken"])assert(now[k]===null,"fake_register_visitor");
   for(const k of ["rights_cleared","download_authorized","cache_authorized","wordpress_media_upload_authorized","post_rewrite_authorized"])assert(now[k]===false,"unsafe_register_release");
  }
 }
 assert(touched===6&&c.rows.filter(x=>x.evidence.length===0).length===54,"derived_counts");
 assert(c.batch_sources.some(x=>x.file==="qa/media-recovery/silver_bridge_258_six_ntsb_fhwa_dpla_20261110.json"&&x.blob_sha==="9836935f4db3aaa9a7f73e68576f1d4db92b8c38"&&x.source_records===6),"missing_batch_blob");
 return {verified:6,researched:234,pending:54,untouched:282,guest_broken_confirmed:0};
}
if(typeof module!=="undefined"&&module.exports){const fs=require("node:fs"),path=require("node:path");const root=path.resolve(__dirname,"../..");function load(p){return JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));}
module.exports={validate,load};if(require.main===module){try{console.log(JSON.stringify(validate(load("qa/media-recovery/silver_bridge_258_six_ntsb_fhwa_dpla_20261110.json"),load("qa/media-recovery/coverage_234_exact_pr1703_20261110.json"),load("qa/media-recovery/coverage_228_exact_pr1703_20261110.json"),load("qa/media-recovery/parts/04.json"))));}catch(e){console.error(e.message);process.exitCode=1;}}}
