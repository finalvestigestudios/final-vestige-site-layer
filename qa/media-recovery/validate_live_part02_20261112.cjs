"use strict";
function validate(a){
 const e=[],bad=s=>e.push(s);
 if(a.schema!=="fv-cms-live-part02-source-geometry-v1"||a.method!=="AUTHENTICATED_WP_EDIT_SOURCE_NOT_GUEST_BROWSER")bad("SCHEMA");
 if(a.evidence?.worklist_blob!=="48e1ebf07207e948ba5802e714eb39659d2e1c1d"||a.evidence?.source_register_blob!=="4965a862f7de7de46c1f4a1e26f3ca70a8c38805")bad("FROZEN");
 if(a.historical?.published_posts_oct30!==61||a.historical?.images_oct30!==355||a.historical?.external_oct30!==288||a.historical?.reported_broken_guest_unconfirmed!==42||a.historical?.claimed_76pct_wire_reduction_measured!==false)bad("HISTORY");
 if(a.historical?.oversized_originals_decimal_mb!==15||a.historical?.oversized_original_stored_bytes!==47096779)bad("STORAGE");
 if(a.policy?.siteqa_sole_browser_collector!==true||a.policy?.homepage_visual_design_out_of_scope!==true||a.policy?.browser_evidence!==false||a.policy?.wordpress_production_writes!==false||a.policy?.third_party_downloads!==false||a.policy?.asset_caching!==false||a.policy?.licensing_auto_clearance!==false)bad("POLICY");
 if(!Array.isArray(a.posts)||a.posts.length!==8||!Array.isArray(a.records)||a.records.length!==59)bad("SIZE");
 const ids=[413,407,370,367,330,299,292,291],ps=new Set((a.posts||[]).map(p=>p.post_id));
 if(ids.some(id=>!ps.has(id))||ps.size!==8)bad("POST_SET");
 for(const p of a.posts||[])if(p.status!=="publish"||p.live_images!==p.frozen_images)bad("POST_DRIFT");
 let keys=new Set();
 for(const r of a.records||[]){
  if(keys.has(r.slot)||r.slot!==r.post_id+":"+Number(r.slot.split(":")[1]))bad("SLOT");keys.add(r.slot);
  if(!ps.has(r.post_id)||typeof r.live_src!=="string"||!r.live_src.startsWith("https://")||typeof r.frozen_src!=="string"||!r.frozen_src.startsWith("https://"))bad("URL");
  if(r.source_equal!==(r.live_src===r.frozen_src))bad("SOURCE");
  if(r.source_http_status!==null||r.guest_http_status!==null||r.guest_natural_px!==null||r.guest_wire_bytes!==null||r.guest_failure_confirmed!==null)bad("FABRICATED_BROWSER");
  if(r.rights_cleared!==false||r.download_authorized!==false||r.cache_authorized!==false||r.wp_media_write_authorized!==false||r.post_rewrite_authorized!==false)bad("LICENSE_OR_WRITE");
  if((r.html_width!==null&&(!Number.isInteger(r.html_width)||r.html_width<=0))||(r.html_height!==null&&(!Number.isInteger(r.html_height)||r.html_height<=0)))bad("DIMENSION");
  if(!Array.isArray(r.source_candidate_catalogs))bad("CANDIDATES");
  for(const c of r.source_candidate_catalogs||[]){
   if(c.item_rights_cleared!==false||c.exact_binary_match_verified!==false)bad("CANDIDATE_RIGHTS");
   if(c.conditional_960px!==null&&(!Array.isArray(c.conditional_960px)||c.conditional_960px.length!==2||!c.conditional_960px.every(n=>Number.isInteger(n)&&n>0)||c.conditional_960px[0]>960))bad("960");
  }
 }
 const rs=a.records||[],n=f=>rs.filter(f).length,c=a.counts||{};
 if(c.posts!==8||c.images!==59||c.frozen_images!==59||c.src_equal!==n(r=>r.source_equal)||c.src_drift!==n(r=>!r.source_equal)||c.missing_width_height!==n(r=>r.html_width===null&&r.html_height===null)||c.has_both_width_height!==n(r=>r.html_width!==null&&r.html_height!==null)||c.partial_width_height!==n(r=>(r.html_width===null)!==(r.html_height===null))||c.alt_changed!==n(r=>r.baseline_alt!==r.live_alt)||c.candidate_slots!==n(r=>r.source_candidate_catalogs.length>0)||c.srcset!==n(r=>r.srcset_present))bad("COUNTS");
 return {ok:e.length===0,errors:e};
}
module.exports={validate};
if(require.main===module){const fs=require("node:fs");const r=validate(JSON.parse(fs.readFileSync(process.argv[2],"utf8")));if(!r.ok){console.error(r.errors.join(","));process.exit(1)}console.log("PASS");}
