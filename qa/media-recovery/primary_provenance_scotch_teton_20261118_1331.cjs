"use strict";
/** Read-only, fail-closed provenance and chronology gate for verified slots. No HTTP/CMS access. */
const validate=function validate(d){
 const bad=[],err=s=>{if(!bad.includes(s))bad.push(s)};
 if(!d||d.schema!=="fv-primary-provenance-scotch-teton-v1")return ["schema"];
 if(d.source_method!=="read_only_wordpress_view_plus_public_retriever_and_official_catalog"||d.source_snapshot?.historical_worklist_blob!=="9cdf7af84175883775aaebf55ffa5ca77b33e423"||d.source_snapshot?.prior_66post_audit_blob!=="03d19a553e8ccb233ee9bc15b87df32aea1f4d0c"||d.source_snapshot?.posts_current!==66||d.source_snapshot?.posts_historical!==61)err("source_integrity");
 const req={"418:1":"https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG","418:2":"https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg","291:2":"https://cloudfront-us-east-1.images.arcpublishing.com/deseretnews/PLWPL72QKJB7BBFJWTXJWVK6QQ.JPG","291:5":"https://cloudfront-us-east-1.images.arcpublishing.com/deseretnews/PLWPL72QKJB7BBFJWTXJWVK6QQ.JPG"};
 if(!Array.isArray(d.slots)||d.slots.length!==4)return ["slot_count"];
 const keys=new Set();
 for(const s of d.slots){
  if(!req[s.key]||keys.has(s.key)||s.original!==req[s.key]||s.authored!=="https://i0.wp.com/"+s.original.slice(8)+"?ssl=1")err("slot_identity");keys.add(s.key);
  if(s.origin_observation?.final_guest_status!==null||s.origin_observation?.decoded_guest!==null||s.origin_observation?.guest_bytes!==null)err("unverified_guest_claim");
  const should403=s.key.startsWith("418:");
  if(s.origin_observation?.status!==(should403?403:null)||s.origin_observation?.method!==(should403?"public_web_retriever_not_chromium":"public_web_image_retriever_visual_only"))err("origin_observation_integrity");
  if(typeof s.alt!=="string"||s.alt.length<20||typeof s.caption!=="string"||s.caption.length<20)err("caption_missing");
 }
 if(keys.size!==4)err("slot_identity");
 const a=d.slots.find(s=>s.key==="291:2"),b=d.slots.find(s=>s.key==="291:5");
 if(a?.original!==b?.original||a?.visual_integrity!=="CONFIRMED_ORIGIN_VISUAL_MISMATCH_STREET_CLEANUP_NOT_BREACH"||b?.visual_integrity!=="ORIGIN_VISUAL_CONSISTENT_WITH_CLEANUP_NOT_FINAL_PROVENANCE")err("teton_visual_integrity");
 const p=d.slots.find(s=>s.key==="418:1");
 if(!p?.candidate_refs?.includes("USCG_VIRIN_210330_G_DE713_0002")||p?.visual_integrity!=="SAME_VIRIN_OFFICIAL_PORTRAIT_IDENTITY_CATALOGED_RASTER_UNVERIFIED")err("uscg_portrait_identity");
 if(!Array.isArray(d.candidates)||d.candidates.length!==4)err("candidate_count");
 const c=Array.isArray(d.candidates)?d.candidates:[];
 if(new Set(c.map(x=>x.id)).size!==4)err("candidate_count");
 const nara=c.find(x=>x.id==="NARA_NAID_28894685");
 if(!nara||nara.for_slot!=="291:2"||nara.official_id!=="28894685"||nara.catalog_original_width!==2798||nara.catalog_original_height!==1966||nara.derivative_width!==960||nara.derivative_height!==675||nara.no_upscale!==true||nara.rights_status!=="US_NO_COPYRIGHT_STATEMENT_REVIEW_HOLD"||nara.approved!==false||nara.exact_binary_verified!==false)err("nara_pinned_derivative_rights");
 for(const x of c){if(x.approved!==false||x.exact_binary_verified!==false||!/^(HOLD|ITEM_POLICY_IDENTIFIED_FINAL_REUSE_REVIEW_HOLD|US_NO_COPYRIGHT_STATEMENT_REVIEW_HOLD)$/.test(x.rights_status||"")||!/^https:\/\//.test(x.source||""))err("candidate_rights_or_provenance");
  if(x.derivative_width!==null&&(!Number.isInteger(x.derivative_width)||x.derivative_width>960||x.derivative_width<=0))err("derivative_width");
  if(x.derivative_width!==null&&x.native_width!==undefined&&x.native_width!==null&&x.derivative_width>x.native_width)err("upscale");
 }
 const uscg=c.find(x=>x.id==="USCG_VIRIN_210330_G_DE713_0002");
 if(!uscg||uscg.for_slot!=="418:1"||uscg.official_id!=="210330-G-DE713-0002.JPG"||uscg.native_width!==null||uscg.catalog_display_mb!==0.04)err("uscg_archive_identity");
 const date=d.chronology_guard;
 if(date?.event_date!=="1946-04-01"||date?.noaa_pages_currently_say!=="1964"||date?.override_to!=="1946"||date?.status!=="DO_NOT_INHERIT_INCORRECT_ARCHIVE_CAPTION"||!Array.isArray(date?.invalid_date_in_noaa_pages)||date.invalid_date_in_noaa_pages.length!==2)err("noaa_chronology");
 const g=d.protections;
 if(g?.max_width_px!==960||g?.no_upscale!==true||g?.rights_cleared!==false||g?.wp_upload_allowed!==false||g?.wordpress_production_write!==false||g?.rehost_allowed!==false||g?.editorial_approval!==false||g?.browser_failure_claim!==false||g?.actual_wire_savings_claim!==false)err("unsafe_approval");
 if(d.acceptance?.guest_cdp_trace_sha256!==null||d.acceptance?.guest_screenshots!==null||d.acceptance?.full_61_or_66_post_wire_parity!==null||d.acceptance?.visitor_broken_42_claim!=="UNVERIFIED"||d.acceptance?.visitor_76_percent_reduction!=="UNMEASURED")err("invented_sitewide_evidence");
 return bad;
};
module.exports={validate};
if(require.main===module){const fs=require("node:fs");const d=JSON.parse(fs.readFileSync(process.argv[2]||__dirname+"/primary_provenance_scotch_teton_20261118_1331.json","utf8"));const errors=validate(d);console.log(JSON.stringify({gate:errors.length?"HOLD":"EDITORIAL_REVIEW_ONLY",errors},null,2));if(errors.length)process.exitCode=1;}
