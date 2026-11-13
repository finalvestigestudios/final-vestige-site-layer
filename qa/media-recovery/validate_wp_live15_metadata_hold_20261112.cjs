"use strict";
function verify(a){
 const errs=[],bad=x=>errs.push(x),rows=a?.records||[];
 if(a?.schema!=="fv-media-live15-metadata-candidate-release-hold-v1")bad("schema");
 if(rows.length!==15||new Set(rows.map(r=>r.media_id)).size!==15)bad("15 unique");
 if(rows.some(r=>!Number.isInteger(r.original_stored_bytes)||r.original_stored_bytes<=1500000))bad("oversize");
 if(rows.reduce((s,r)=>s+r.original_stored_bytes,0)!==47096779)bad("stored total");
 const inlines=rows.filter(r=>r.image_inline_match),missing=rows.filter(r=>r.wordpress_subsize_count===0);
 if(inlines.length!==11||inlines.reduce((s,r)=>s+r.original_stored_bytes,0)!==38480915)bad("inline stored");
 if(missing.length!==5||missing.reduce((s,r)=>s+r.original_stored_bytes,0)!==13267538||missing.some(r=>r.image_inline_match?.html_author_width_px!==1024||r.candidate_existing_wp_virtual_variant!==null))bad("five PNG");
 if(rows.filter(r=>r.image_inline_match?.source_kind==="jetpack_fit_proxy").length!==3)bad("jetpack");
 const posts=[...new Set(inlines.map(r=>r.image_inline_match.post_id))].sort((a,b)=>a-b);
 if(JSON.stringify(posts)!==JSON.stringify([34,35,36,37,38,269,299,621]))bad("posts");
 for(const r of rows){
  const [w,h]=r.conditional_max_960_no_upscale_px||[];
  if(!r.origin_url.startsWith("https://finalvestige.com/wp-content/uploads/"))bad("url");
  if(!(Number.isInteger(w)&&Number.isInteger(h)&&w<=960&&w>=1&&h>=1&&w<=r.native_dimensions_px[0]&&h<=r.native_dimensions_px[1]))bad("960");
  if(r.rights_verified_for_transform!==false||r.origin_http_status!==null||r.guest_http_status!==null||r.guest_transfer_bytes!==null||r.decision!=="HOLD_NOT_RELEASE_AUTHORIZED")bad("no release");
  const c=r.candidate_existing_wp_virtual_variant;
  if(c&&(c.listed_virtual!==true||c.actual_http_status!==null||c.actual_decoding!==null||c.width_px>960||c.width_px>r.native_dimensions_px[0]||!c.url.startsWith("https://finalvestige.com/wp-content/uploads/")))bad("virtual candidate");
  const i=r.image_inline_match;
  if(i&&(i.guest_http_status!==null||i.guest_current_src!==null||i.guest_wire_bytes!==null||!["wordpress_original_direct","jetpack_fit_proxy"].includes(i.source_kind)))bad("guest");
 }
 if(a?.metrics?.visitor_transfer_saving_percent!==null||a?.metrics?.actual_broken_guest_count!==null||a?.metrics?.wordpress_writes!==0)bad("unmeasured");
 if(a?.policy?.wordpress_write!==false||a?.policy?.rights_cleared!==false||a?.policy?.image_binary_download!==false)bad("policy");
 return {valid:errs.length===0,errors:[...new Set(errs)]};
}
module.exports={verify};
