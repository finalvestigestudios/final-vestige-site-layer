"use strict";
function fail(x){throw Error("TETON291_HOLD "+x)}
const keys=["291:0","291:1","291:2","291:3","291:4","291:5"];
function host(url){
 if(typeof url!=="string"||!/^https:\/\/[^/?#]+/.test(url))fail("invalid HTTPS URL");
 const h=url.split("/")[2];
 if(h.includes("@")||h.includes(":")||url.includes("#"))fail("unsafe URL");
 return h.toLowerCase()
}
function assess(doc){
 if(!doc||doc.schema!=="fv-teton291-v1"||doc.wp_post_id!==291||doc.wp_modified!=="2026-11-02T21:36:09")fail("revision drift");
 if(doc.post_url!=="https://finalvestige.com/2026/08/19/one-bulldozer-never-came-back-teton-dam/")fail("post drift");
 const c=doc.counts,b=doc.baselines;
 if(!c||[c.images,c.unique_urls,c.jetpack,c.direct,c.reader_displayed_slots,c.reader_inaccessible_slots,c.viewport_guest_verified].join()!=="6,5,5,1,5,1,0")fail("count drift");
 if(!b||[b.historical_posts,b.historical_images,b.siteqa_origin_count,b.media_origin_count,b.reported_broken,b.oversized_count,b.oversized_stored_bytes].join()!=="61,355,286,288,42,20,64385752"||b.confirmed_broken!==null||b.claimed_savings_pct!==76||b.measured_savings_pct!==null||b.visitor_wire_bytes!==null)fail("unproven metric");
 if(!Array.isArray(doc.rows)||doc.rows.length!==6)fail("six rows");
 const m=new Map();
 for(const row of doc.rows){
  if(!keys.includes(row.slot)||m.has(row.slot))fail("slot identity");
  m.set(row.slot,row);
  const origin=host(row.authored_url),view=host(row.view_src);
  if(!row.alt||!row.caption||!["BREACH","FLOOD","CLEANUP","REMAINS"].includes(row.phase))fail("caption/phase");
  if(row.delivery==="DIRECT_EXTERNAL"){
   if(row.slot!=="291:3"||row.authored_url!==row.view_src||view!=="brightspotcdn.byui.edu")fail("direct origin");
  }else if(row.delivery==="JETPACK_EXTERNAL_ORIGIN"){
   if(row.slot==="291:3"||view!=="i0.wp.com"||origin==="finalvestige.com")fail("proxy provenance");
  }else fail("delivery unknown");
  if(!["IMAGE_RENDERED","TOOL_INACCESSIBLE"].includes(row.reader))fail("reader invented");
  for(const k of ["guest_http","guest_current_src","guest_decode","guest_transfer_bytes","reader_http","view_width","view_height","binary_sha256"])if(row[k]!==null)fail("unverified "+k);
  for(const k of ["view_srcset","view_sizes","rights_cleared","wp_cached","wp_write_authorized"])if(row[k]!==false)fail("premature "+k);
 }
 if(m.size!==6||new Set(doc.rows.map(r=>r.view_src)).size!==5)fail("source count");
 const early=m.get("291:2"),late=m.get("291:5");
 if(early.view_src!==late.view_src||early.authored_url!==late.authored_url||host(early.authored_url)!=="cloudfront-us-east-1.images.arcpublishing.com")fail("duplicated source");
 if(early.phase!=="BREACH"||late.phase!=="CLEANUP"||!early.alt.includes("Growing breach")||!late.alt.includes("cleanup"))fail("caption conflict");
 if(m.get("291:0").view_src!==m.get("291:0").authored_url||!m.get("291:0").view_src.includes("text-message.blogs.archives.gov"))fail("proxy upstream");
 if(m.get("291:3").reader!=="TOOL_INACCESSIBLE"||doc.rows.filter(r=>r.reader==="IMAGE_RENDERED").length!==5)fail("reader source results");
 const e=doc.editorial_issue;
 if(!e||e.slots?.join()!=="291:2,291:5"||e.same_image!==true||e.different_time_phases!==true||e.observed_scene!=="DOWNTOWN_REXBURG_STREET_CLEANUP_NOT_DAM"||e.status!=="CONFIRMED_SOURCE_VISUAL_MISMATCH_NOT_BROKEN_HTTP"||e.auto_fix_allowed!==false)fail("editorial evidence");
 const candidates=doc.primary_candidates;
 if(!Array.isArray(candidates)||candidates.length!==2||candidates.map(x=>x.naid).sort().join()!=="28894684,28894685")fail("archive candidates");
 for(const x of candidates){
  let dims=x.naid===28894684?"2558,1728,960,649":"2798,1966,960,675";
  if([...x.original_catalog_px,...x.max_no_upscale_px].join()!==dims||x.max_no_upscale_px[0]>960||x.max_no_upscale_px[0]>x.original_catalog_px[0])fail("geometry");
  if(x.record!=="https://catalog.archives.gov/id/"+x.naid||host(x.catalog)!=="commons.wikimedia.org")fail("catalog");
  if(x.rights!=="US_NO_COPYRIGHT_DECLARATION_ITEM_REVIEW_HOLD"||x.exact_visual_match!==false||x.binary_verified!==false||x.rights_approved!==false||x.wp_upload_authorized!==false)fail("rights/crop gate");
 }
 if(doc.read_only!==true||doc.wordpress_writes!==0||doc.homepage_changes!==0||doc.rehosted_images!==0||doc.paid_calls!==0||doc.merges!==0||doc.deployments!==0)fail("production boundary");
 return {result:"EDITORIAL_REVIEW_HOLD",post:291,slots:6,unique_originals:5,visual_mismatch:["291:2","291:5"],browser_broken_verified:null,rights_approved:0,wordpress_writes:0}
}
module.exports={assess};
