"use strict";
/** Deterministic OFFLINE fail-closed reconciliation; performs no network, CMS or file writes. */
function validate(previous,audit,current,auditBlobSha) {
 const errors=[],bad=x=>errors.push(x), oldRows=previous.rows,rows=current.rows,ar=audit.rows;
 if(oldRows.length!==288||rows.length!==288||ar.length!==5)bad("cardinality");
 if(previous.frozen_source.posts!==61||current.frozen_source.inline_images!==355||current.frozen_source.upstream_images!==288)bad("frozen census");
 if(current.counts.researched_unique!==274||current.counts.unresearched!==14||current.counts.total_evidence_records!==279)bad("counts");
 if(rows.filter(x=>x.evidence.length).length!==274||rows.filter(x=>!x.evidence.length).length!==14)bad("computed coverage");
 if(current.counts.guest_browser_confirmed_broken!==0||current.counts.wire_reduction_76_percent_measured!==false||current.counts.reported_42_broken_browser_confirmed!==false)bad("unverified performance claim");
 if(audit.post.live_original_src_exact_frozen!=="5/5"||audit.post.live_alt_count!==5||audit.post.historical_alt_equality_verified!==false||audit.post.read_only_wordpress!==true)bad("CMS evidence");
 if(audit.counts.wordpress_writes||audit.counts.downloads||audit.counts.caching||audit.counts.spend_usd||audit.publication_authorized!==false)bad("unauthorized operation");
 if(JSON.stringify(current.original_six_p0_guest_queue)!==JSON.stringify(previous.original_six_p0_guest_queue))bad("QA P0 changed");
 const expected=["428:1","428:2","428:3","428:4","428:5"];
 if(JSON.stringify(ar.map(x=>x.slot))!==JSON.stringify(expected))bad("audit identity");
 for(let i=0;i<oldRows.length;i++){
   const o=oldRows[i],n=rows[i];
   if(n.slot!==o.slot||n.stored_url!==o.stored_url||n.post_id!==o.post_id)bad("frozen URL/slot changed "+i);
   if(n.post_id!==428 && JSON.stringify(n)!==JSON.stringify(o))bad("unrelated row changed "+n.slot);
   if(n.post_id===428){
     const a=ar.find(x=>x.slot===n.slot);
     if(!a||o.evidence.length!==0||n.evidence.length!==1||n.candidate_sources.length!==1)bad("batch row count "+n.slot);
     if(!a||a.original_url!==o.stored_url||n.evidence[0].blob_sha!==auditBlobSha||n.evidence[0].path!=="qa/media-recovery/pulaski_428_five_ui_loc_rights_live_20261110.json")bad("batch identity/provenance "+n.slot);
   }
   if(n.guest_http_status!==null||n.guest_wire_bytes!==null||n.guest_broken!==null||n.rights_cleared||n.download_authorized||n.cache_authorized||n.wordpress_media_upload_authorized||n.post_rewrite_authorized)bad("unsupported guest/rights flag "+n.slot);
 }
 if(ar.filter(x=>x.web_retriever_observation==="IMAGE_DISPLAYED").length!==4||ar.filter(x=>x.web_retriever_observation==="RETRIEVER_UNAVAILABLE").length!==1)bad("retriever classification");
 if(ar[0].web_retriever_wrapper_code!=="Internal Error"||ar[0].guest_http_status!==null)bad("wrapper was claimed as HTTP");
 if(!ar[4].diagram_label_legibility_hold||!ar[4].suggested_alt.includes("index"))bad("map legibility/ALT");
 for(const a of ar){
  if(!a.live_source_exact_frozen||!a.live_alt||!a.primary_source_url||!a.rights_review||!a.identity_review||!a.resize_plan)bad("incomplete provenance "+a.slot);
  if(a.guest_http_status!==null||a.origin_http_status!==null||a.guest_wire_bytes!==null||a.guest_broken!==null||a.rights_cleared||a.download_authorized||a.cache_authorized||a.wordpress_media_upload_authorized||a.post_rewrite_authorized||a.exact_binary_match_verified)bad("unverified status/grants "+a.slot);
  if(a.candidate_native_px!==null||a.conditional_max960_px!==null)bad("invented native dimensions "+a.slot);
 }
 return {ok:errors.length===0,errors};
}
module.exports={validate};
