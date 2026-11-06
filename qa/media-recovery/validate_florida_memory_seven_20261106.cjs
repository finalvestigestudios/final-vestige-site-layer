'use strict';
// Offline audit verification, no network calls or WordPress writes.
const expected=[
  [
    "PR04493",
    "prints/pr04493.jpg",
    "4144"
  ],
  [
    "RC17068",
    "reference/rc17068.jpg",
    "38362"
  ],
  [
    "RC10673",
    "reference/rc10673.jpg",
    "33289"
  ],
  [
    "N031889",
    "general/n031889.jpg",
    "141398"
  ],
  [
    "RC04344",
    "reference/rc04344.jpg",
    "27848"
  ],
  [
    "RC07668",
    "reference/rc07668.jpg",
    "30741"
  ],
  [
    "MSF-PB11548-001",
    "msf/MSF-PB11548-001.jpg",
    "340182"
  ]
];
function verify(a){
  const must=(ok,label)=>{if(!ok)throw Error(label)};
  must(a.schema==="fv-media-florida-memory-seven-v1","schema");
  must(a.date==="2026-11-06"&&a.post.id===432&&a.post.stored_images===7&&a.post.stored_images_without_width_height===7,"post_source");
  must(a.audit_context.legacy_posts===61&&a.audit_context.legacy_images===355&&a.audit_context.latest_posts===66&&a.audit_context.latest_refs===361,"baseline");
  must(a.audit_context.asserted_broken_count===42&&!a.audit_context.asserted_broken_browser_confirmed,"no_fabricated_breaks");
  must(a.audit_context.asserted_weight_reduction_percent===76&&!a.audit_context.actual_weight_reduction_measured,"no_fabricated_savings");
  must(a.audit_context.worklist_found===false,"worklist_missing");
  must(a.release.browser_verified===false&&a.release.native_pixels_verified===false&&a.release.item_rights_fully_cleared===false,"release_guard");
  must(a.release.production_wordpress_writes===0&&a.release.third_party_downloads===0&&a.release.third_party_caches===0&&a.release.production_fixed===0,"production_guard");
  must(Array.isArray(a.rows)&&a.rows.length===7,"row_count");
  for(let i=0;i<7;i++){
    const r=a.rows[i], [id,path,cat]=expected[i];
    must(r.key===`432:${i}`&&r.post_id===432,"key");
    must(r.image_src===`https://www.floridamemory.com/fpc/${path}`&&r.retrieval.attempted_url===r.image_src,"src");
    must(r.catalog_id===id&&r.catalog_url===`https://www.floridamemory.com/items/show/${cat}`&&r.catalog_path_match===true,"catalog");
    must(r.visual_binary_match_unverified===true,"binary_hold");
    must(r.retrieval.wrapper_error===500&&r.retrieval.redirect_to===`https://floridamemory.com/fpc/${path}`,"wrapper");
    for(const k of ["origin_http","browser_http","visitor_broken","natural_width","natural_height","wire_bytes"])must(r.retrieval[k]===null,"retrieval_unknown");
    must(r.rights.policy==="PDM_1_0_SITE_WIDE"&&r.rights.credit==="State Archives of Florida / Florida Memory"&&r.rights.credit_required===true&&r.rights.statute==="Fla. Stat. 257.35(6)"&&r.rights.item_review==="HOLD","rights");
    must(r.preview.max_width===960&&r.preview.no_upscale===true,"geometry_max");
    for(const k of ["native_width","native_height","proposed_width","proposed_height"])must(r.preview[k]===null,"geometry_unknown");
    must(r.media_downloaded===false&&r.third_party_cached===false&&r.wordpress_written===false&&r.release_approved===false,"row_release");
  }
  must(a.rows[1].editorial_review_note.includes("Avenue A"),"detail_Avenue_A");
  must(a.rows[6].catalog_date==="2001"&&a.rows[6].editorial_review_note.includes("2001"),"2001_photo");
  return true;
}
module.exports={verify};
if(require.main===module){const fs=require('node:fs');const path=require('node:path');verify(JSON.parse(fs.readFileSync(path.join(__dirname,'florida_memory_seven_20261106.json'),'utf8')));console.log('7-row Florida Memory evidence gate PASS')}
