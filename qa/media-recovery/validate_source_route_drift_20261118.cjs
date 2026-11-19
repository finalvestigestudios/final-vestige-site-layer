"use strict";
/** Offline, fail-closed reconciliation validator. No HTTP or CMS writes. */
function validate(d) {
 const bad=[], err=k=>{if(!bad.includes(k))bad.push(k);};
 const arr=a=>Array.isArray(a)?a:[];
 if(!d||d.schema!=="fv-source-route-drift-20261118-v1")return ["schema"];
 if(d.source_kind!=="PINNED_CMS_SOURCE_NOT_GUEST"||d.historic_csv?.blob!=="76aa63ffaa299a6e6878edc1b66e637fa6f058ab"||arr(d.current_slices).length!==9||d.current_slices.some(x=>!/^[a-f0-9]{40}$/.test(x.blob||"")))err("pinning");
 const r=arr(d.crosswalk), hist=r.filter(x=>x.prior_img!==null), seen=new Set();
 if(r.length!==66||hist.length!==61)err("cohorts");
 for(const x of r){if(!Number.isSafeInteger(x.post_id)||seen.has(x.post_id)||!/^https:\/\/finalvestige\.com\//.test(x.post_url||""))err("post_identity");seen.add(x.post_id);
  for(const field of ["current_img","current_offsite"]){if(!Number.isSafeInteger(x[field])||x[field]<0)err("invalid_count");}
  if(x.current_offsite>x.current_img)err("external_exceeds_total");
  if(x.prior_img!==null&&(x.prior_img!==x.current_img||x.delta_offsite!==x.current_offsite-x.prior_offsite))err("historic_delta");
  if(x.prior_img===null&&(x.prior_offsite!==null||x.delta_offsite!==null))err("new_post_leak");
 }
 const sum=(rows,field)=>rows.reduce((n,x)=>n+(Number.isSafeInteger(x[field])?x[field]:0),0);
 if(sum(hist,"prior_img")!==355||sum(hist,"prior_offsite")!==286||sum(hist,"current_offsite")!==288||sum(r,"current_img")!==361||sum(r,"current_offsite")!==294)err("sum_mismatch");
 if(hist.filter(x=>x.delta_offsite).sort((a,b)=>a.post_id-b.post_id).map(x=>x.post_id+":"+x.delta_offsite).join(",")!=="285:1,291:1")err("unexpected_drift");
 if(r.filter(x=>x.prior_img===null).map(x=>x.post_id).sort((a,b)=>a-b).join(",")!=="1917,1920,1922,1924,1926")err("new_ids");
 const imgs=arr(d.changed_image_sources),keys=new Set();
 if(imgs.length!==12)err("changed_source_coverage");
 for(const x of imgs){if(!/^(285|291):[0-5]$/.test(x.slot||"")||keys.has(x.slot)||!/^https:\/\//.test(x.origin_url||"")||!/^https:\/\//.test(x.published_url||""))err("changed_image_identity");keys.add(x.slot);
 if(x.guest_browser_status!==null||x.http_status!==null)err("invented_http");}
 const dup=arr(d.duplicate_origin_review);
 if(dup.length!==2||dup.map(x=>arr(x.slots).map(s=>s.slot).sort().join(",")).sort().join("|")!=="213:2,213:6|291:2,291:5")err("duplicate_slots");
 for(const x of dup){if(!/^https:\/\//.test(x.source_url||"")||arr(x.slots).length!==2||x.slots.some(s=>s.authored_url!==x.slots[0].authored_url)||x.guest_browser_status!==undefined)err("duplicate_provenance");}
 if(d.visual_finding?.key!=="291:2"||d.visual_finding?.guest_chromium_verified!==false||d.visual_finding?.decision!=="P0_EDITORIAL_VISUAL_REVIEW_NO_AUTO_REPLACEMENT")err("visual_review_status");
 if(d.source_observation?.http_status!==null||d.source_observation?.guest_browser_status!==null||d.guardrails?.production_write_allowed!==false||d.guardrails?.wp_media_upload_allowed!==false||d.guardrails?.max_derivative_width_px!==960||d.guardrails?.no_upscale!==true||d.guardrails?.license_clearance!=="HOLD")err("unsafe_release_claim");
 if(d.claims?.broken_guest_images_42!=="UNVERIFIED"||d.claims?.wire_savings_76_percent!=="UNMEASURED")err("unproven_claim");
 return bad;
}
module.exports={validate};
if(require.main===module){let d=require(process.argv[2]);const failures=validate(d);console.log(JSON.stringify({gate:failures.length?"HOLD":"REVIEW_ONLY",failures},null,2));process.exitCode=failures.length?1:0;}
