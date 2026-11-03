"use strict";
function validate(a, frozen) {
  const e=[];
  const fail=(condition,msg)=>{if(!condition)e.push(msg)};
  const orig=frozen.images.filter(x=>x.post_id===220).sort((x,y)=>x.slot-y.slot);
  const p=frozen.posts.find(x=>x.id===220);
  const expected=[["NH 97545",4918,6136],["NH 97552",740,574],["NH 97310",578,737],["NH 97567",740,532],[null,1700,1349],["NH 97570",739,574],["NH 97557",740,576]];
  fail(a.source.blob_sha==="9b16b828342a9ac338f3e65610fd3d8d508355e9","pinned frozen blob sha");
  fail(a.schema==="fv-media-recovery-thresher-220-v1","schema");
  fail(a.source.post_id===220 && a.source.post_url===p?.url,"post identity");
  fail(a.source.snapshot==="qa/media-recovery/parts/05.json" && a.source.not_live_wp_read===true,"frozen source provenance");
  fail(a.images.length===7 && orig.length===7,"seven slots");
  fail(a.conclusion.confirmed_guest_breaks===0 && a.conclusion.confirmed_browser_transfers===0 && a.conclusion.production_repairs===0,"unverified metrics");
  fail(a.conclusion.sitewide_42_verified===false && a.conclusion.sitewide_76_percent_measured===false,"sitewide false claims");
  const unique=new Set();
  for(let i=0;i<7;i++){
    const r=a.images[i],s=orig[i];
    if(!r||!s){e.push("missing source row "+i);continue}
    fail(r.key===s.key && r.slot===i && r.exact_source_url===s.source_url && r.original_alt===s.alt,"source identity "+i);
    fail(!unique.has(r.key),"duplicate "+i);unique.add(r.key);
    const o=r.retrieval,c=r.catalog,u=r.rights,x=r.proposed;
    fail(o.observed==="web_tool_internal_error_no_response" && o.origin_http_status===null && o.guest_browser_http_status===null && o.guest_browser_decoded===null && o.guest_image_wire_bytes===null && o.guest_current_src===null,"unverified transport "+i);
    fail(c.navy_catalog_id===expected[i][0] && c.original_width_px===expected[i][1] && c.original_height_px===expected[i][2],"fixed cited catalog ID and dimensions "+i);
    fail(c.observation==="catalog_html_accessible" && c.url.startsWith("https://commons.wikimedia.org/wiki/File:") && c.navy_primary_url.startsWith("https://www.history.navy.mil/"),"archival URLs "+i);
    fail(Number.isInteger(c.original_width_px)&&Number.isInteger(c.original_height_px)&&c.original_width_px>0&&c.original_height_px>0,"catalog dimensions "+i);
    const width=Math.min(960,c.original_width_px);
    fail(x.width_px===width && x.height_px===Math.round(c.original_height_px*width/c.original_width_px) && x.width_px<=960,"resize no upscale "+i);
    fail(u.item_specific_signoff===false && u.copy_allowed===false && u.credits_reviewed===false && x.wordpress_cache_and_rehost==="HOLD" && x.swap_published_src==="HOLD" && x.visual_identity_approval===false,"rights/production HOLD "+i);
    fail((i===4)===(c.navy_catalog_id===null),"nonidentical primary image "+i);
    fail((i===4?c.association==="related_Navy_photo_not_same_image":c.association==="same_catalog_image_by_Commons_source_record"),"source identity kind "+i);
  }
  return e;
}
module.exports={validate};
