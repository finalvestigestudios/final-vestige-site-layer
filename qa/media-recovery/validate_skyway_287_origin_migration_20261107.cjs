"use strict";
const EXPECTED=[
  "https://arc-anglerfish-washpost-prod-washpost.s3.amazonaws.com/public/IIYZWAFLJUQD3YGEYEKMG5PVXY.jpg",
  "https://cloudfront-us-east-1.images.arcpublishing.com/tbt/555OWMWIJMI6TGNIIBWI6S7HAY.jpg",
  "https://skywaydisaster.com/images/timeline2.jpg",
  "https://img.connatix.com/ecf95169-f8cd-4cd5-8698-9bc54211f8e9/1_th.jpg",
  "https://www.flmd.uscourts.gov/sites/flmd/files/images/figure-9-sunshine-skyway-bridge-3.jpg",
  "https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg"
];
function validate(d){
 const errors=[];
 const fail=(msg)=>errors.push(msg);
 if(!d||typeof d!=="object")return {valid:false,errors:["manifest must be object"]};
 if(d.schema_version!=="fv.media.skyway_p0.origin_migration.v1")fail("schema_version");
 if(d.scope?.post_id!==287||!String(d.scope?.permalink||"").startsWith("https://finalvestige.com/"))fail("post identity");
 if(d.retrieval_methodology?.method!=="web.open isolated URL renderer"||d.retrieval_methodology?.origin_http_headers_verified!==false||d.retrieval_methodology?.chrome_logged_out_verified!==false)fail("unsupported transport assurance");
 const c=d.controls||{};
 for(const field of ["production_changes","downloaded_any_media","created_derivatives","wp_upload_authorized","copyright_clearance_granted","guest_browser_tested","reported_broken_42_confirmed","claimed_transfer_reduction_76_percent_measured"]){
  if(c[field]!==false)fail("safety "+field);
 }
 if(!Array.isArray(d.images)||d.images.length!==6)fail("exact six image entries");
 else d.images.forEach((im,i)=>{
  if(im.slot!==i||im.stored_src!==EXPECTED[i]||!/^https:\/\//.test(im.stored_src))fail("source identity "+i);
  if(!im.stored_alt||typeof im.stored_alt!=="string")fail("missing ALT "+i);
  const o=im.retrieval_observation||{};
  if(o.outcome!==(i===5?"fetch_failed_reported_404":"viewer_rendered_image"))fail("viewer classification "+i);
  if(o.viewer_reported_http_status!==(i===5?404:null))fail("viewer reported status "+i);
  if(typeof o.source_ref!=="string"||!/^turn\d+view\d+$/.test(o.source_ref))fail("viewer evidence "+i);
  for(const k of ["guest_browser_http_status","guest_browser_current_src","guest_browser_natural_width","guest_browser_decoded","guest_browser_transfer_bytes","guest_browser_screenshot"]){
   if(o[k]!==null)fail("unverified guest status "+i+" "+k);
  }
  const r=im.restoration||{};
  if(r.max_width_px!==960||r.rights_status!=="HOLD"||r.rehosting_permitted!==false||r.auto_replacement_permitted!==false||r.no_upscale!==true||r.wp_media_id!==null)fail("image rights and no-upscale "+i);
  if(r.source_native_dimensions!==null||r.preview_dimensions!==null)fail("fabricated derivative geometry "+i);
 });
 if(!Array.isArray(d.candidates)||d.candidates.length!==3)fail("candidate count");
 else {
  const publisher=d.candidates[0], archive=d.candidates[1], county=d.candidates[2];
  if(publisher.for_slot!==5||publisher.candidate_url!=="https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg"||publisher.identity_status.indexOf("NOT_verified")<0)fail("publisher relocation evidence");
  if(archive.for_slot!==3||archive.record_id!=="RC09236"||archive.kind!=="different_archival_composition")fail("Florida Memory archive identity hold");
  if(county.for_slot!==5||county.record_id!=="p16681coll1/29937"||county.kind!=="different_archival_composition")fail("county archive identity hold");
  d.candidates.forEach((x,i)=>{
    if(x.reuse_approved!==false||x.publication_approved!==false||x.max_width_px!==960||x.native_dimensions!==null||x.conditional_preview_dimensions!==null)fail("unapproved candidate "+i);
    if(!/^https:\/\//.test(x.catalog_url)||!x.rights)fail("rights provenance "+i);
  });
 }
 if(!Array.isArray(d.priority_findings)||d.priority_findings.length!==3)fail("findings");
 if(!Array.isArray(d.next_steps)||d.next_steps.length<3)fail("staging plan");
 return {valid:errors.length===0,errors};
}
module.exports={validate};
