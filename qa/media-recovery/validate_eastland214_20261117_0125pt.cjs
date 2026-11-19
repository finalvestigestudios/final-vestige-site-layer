'use strict';
const sha="0f3dfe398a76838049cebba7cb773d5c5a0c8c69";
function check(d){
 function bad(s){throw new Error(s)}
 if(!d||d.type!=="image-qa-custody"||d.post_id!==214||d.source_snapshot_sha!==sha||d.site_baseline?.posts!==61||d.site_baseline?.refs!==355||!Array.isArray(d.slots)||d.slots.length!==6)bad("census");
 if(d.proven_42_broken!==false||d.measured_76_percent_savings!==false||d.original_storage_equals_visitor_bytes!==false||d.wp_production_authorized!==false||d.media_cache_authorized!==false||d.homepage_scope!==false||d.decision!=="HOLD")bad("release");
 for(let i=0;i<6;i++){
  const s=d.slots[i];if(!s||s.key!==`214:${i}`||!s.original_url?.startsWith("https://")||!s.alt||!s.catalog?.url?.startsWith("https://")||!s.catalog.id||!s.catalog.rights_note)bad("source");
  if(["guest_current_src","guest_http_status","guest_mime","guest_decoded","guest_transfer_bytes","guest_screenshot","source_sha256"].some(k=>s[k]!==null)||s.rights_approved!==false||s.frame_verified!==false)bad("invented proof");
  const n=s.catalog.native_px,r=s.catalog.review_px;
  if(n===null){if(r!==null)bad("invented size")}else{
   if(!Array.isArray(n)||n.length!==2||!n.every(x=>Number.isInteger(x)&&x>0)||!r)bad("native size");
   const width=Math.min(960,n[0]);if(r.width!==width||r.height!==Math.round(n[1]*width/n[0]))bad("upscale/distortion");
  }
 }
 if(!d.slots[0].catalog.id.includes("19622")||!d.slots[4].catalog.id.includes("19623")||!d.slots[5].catalog.id.includes("281841"))bad("archival drift");
 return {decision:"HOLD",count:6};
}
module.exports={check};
