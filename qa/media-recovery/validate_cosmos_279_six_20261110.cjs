"use strict";
/** Offline fail-closed post-279 recovery validator. Never fetches, uploads, or mutates CMS. */
function validateCosmos(audit, next, prev) {
 const errors=[], check=(yes,code)=>{if(!yes)errors.push(code)};
 if(!audit||!next||!prev||!Array.isArray(audit.rows)||!Array.isArray(next.rows)||!Array.isArray(prev.rows))
   return {ok:false,errors:["REQUIRED_ROWS_MISSING"]};
 const targets=["279:0","279:1","279:2","279:3","279:4","279:5"], targetSet=new Set(targets);
 const oldBy=new Map(prev.rows.map(r=>[r.slot,r]));
 const newBy=new Map(next.rows.map(r=>[r.slot,r]));
 const auditBy=new Map(audit.rows.map(r=>[r.slot,r]));
 check(audit.schema==="fv-cosmos-279-six-original-source-rights-v1","AUDIT_SCHEMA");
 check(audit.post?.source_urls_exact_six_of_six===true&&audit.post?.live_alt_captured_count===6,"LIVE_WP_READBACK");
 check(audit.post?.historical_alt_equality_verified===false,"NO_HISTORICAL_ALT_CLAIM");
 check(prev.rows.length===288&&next.rows.length===288,"EXACT_CENSUS");
 check(oldBy.size===288&&newBy.size===288&&auditBy.size===6,"UNIQUE_KEYS");
 check(targets.every(k=>oldBy.has(k)&&newBy.has(k)&&auditBy.has(k)),"ALL_SIX_PRESENT");
 check(prev.counts?.researched_unique===257&&prev.counts?.unresearched===31,"PREVIOUS_COUNT");
 check(next.counts?.researched_unique===263&&next.counts?.unresearched===25,"NEW_COUNT");
 check(next.counts?.total_evidence_records===268,"EVIDENCE_COUNT");
 check(next.rows.filter(r=>r.evidence?.length).length===263&&next.rows.filter(r=>!r.evidence?.length).length===25,"RECOMPUTED_COVERAGE");
 check(next.rows.reduce((s,r)=>s+(r.evidence?.length||0),0)===268,"RECOMPUTED_EVIDENCE");
 check(next.counts?.guest_browser_confirmed_broken===0&&next.counts?.guest_browser_confirmed_loaded===0&&next.counts?.reported_42_broken_browser_confirmed===false,"NO_FAKE_GUEST");
 check(next.counts?.wire_reduction_76_percent_measured===false&&next.counts?.oversized_stored_original_bytes===47096779,"NO_FAKE_BYTES");
 check(audit.counts?.web_retriever_rendered_exact_original===5&&audit.counts?.web_retriever_unavailable===1,"RETRIEVER_COUNTS");
 check(auditBy.get("279:3")?.source_scene_description.includes("NO aircraft")===true,"NO_AIRCRAFT_IN_COLLAGE");
 check(auditBy.get("279:4")?.source_native_px?.join("x")==="640x958","NATIVE_SCHEMATIC_SIZE");
 check(auditBy.get("279:4")?.conditional_max960_px?.join("x")==="640x958","NO_SCHEMATIC_UPSCALE");
 check(auditBy.get("279:5")?.retriever_observation==="WEB_TOOL_INTERNAL_ERROR","LINKEDIN_UNVERIFIED");
 check(audit.rows.every(r=>r.guest_http_status===null&&r.origin_http_status===null&&r.guest_transfer_bytes===null&&r.guest_broken===null),"NO_INVENTED_HTTP");
 check(audit.rows.every(r=>r.rights_cleared===false&&!r.download_authorized&&!r.cache_authorized&&!r.wordpress_upload_authorized&&!r.post_rewrite_authorized),"NO_UNLICENSED_WRITE");
 check(audit.rows.every(r=>r.sizing_rule.includes("no upscaling")),"NO_UPSCALE_RULE");
 const batch=next.batch_sources?.at(-1);
 check(batch?.file==="qa/media-recovery/cosmos_279_six_live_primary_rights_20261110.json"&&typeof batch?.blob_sha==="string"&&/^[0-9a-f]{40}$/.test(batch.blob_sha),"BATCH_SHA_AND_PATH");
 const changed=[];
 for(const o of prev.rows){
   const n=newBy.get(o.slot);
   if(!n){errors.push("MISSING_"+o.slot);continue}
   if(JSON.stringify(o)!==JSON.stringify(n))changed.push(o.slot);
   if(!targetSet.has(o.slot))check(JSON.stringify(o)===JSON.stringify(n),"OTHER_CHANGED_"+o.slot);
 }
 check(changed.length===6&&changed.every(k=>targetSet.has(k)),"ONLY_SIX_CHANGED");
 for(const key of targets){
   const a=auditBy.get(key),o=oldBy.get(key),n=newBy.get(key);
   if(!a||!o||!n){errors.push("TARGET_MISSING_"+key);continue}
   check(a.original_url===o.stored_url&&n.stored_url===o.stored_url,"EXACT_SRC_"+key);
   check(o.evidence.length===0&&n.evidence.length===1,"ONE_EVIDENCE_"+key);
   check(n.evidence[0]?.blob_sha===batch?.blob_sha&&n.evidence[0]?.path===batch?.file,"EVIDENCE_PIN_"+key);
   check(n.candidate_sources?.length===1&&!n.candidate_sources[0].item_rights_cleared,"RIGHTS_HOLD_"+key);
   check(n.guest_http_status===null&&n.guest_wire_bytes===null&&n.guest_broken===null,"GUEST_UNKNOWN_"+key);
   check(!n.rights_cleared&&!n.cache_authorized&&!n.wordpress_media_upload_authorized&&!n.post_rewrite_authorized,"REHOST_BLOCK_"+key);
 }
 return {ok:errors.length===0,errors,changed,checks:"offline original-identity/rightsholder/browser/sizing gates"};
}
module.exports={validateCosmos};
