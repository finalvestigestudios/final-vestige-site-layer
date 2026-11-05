"use strict";
const fs = require("node:fs");
const path = require("node:path");
const EXPECTED = Object.freeze({
  39:2892087,40:2552136,41:2498247,42:2488823,43:2836245,
  293:2090327,382:2318980,388:8176362,389:2822969,405:2201573,
  482:2293016,1257:4798395,1258:5553669
});
const GROUPS = Object.freeze({
 historical_reconstruction_png5:[5,13267538],malbone_original2:[2,10352064],
 vasa_press3:[3,13318311],remaining_uncategorized3:[3,6584916]
});
function validate(a) {
 const fail=[],push=(ok,msg)=>{if(!ok)fail.push(msg);};
 push(a&&a.schema==="fv-media-oversize13-audit-v1","schema");
 push(a?.threshold_bytes===1572864,"threshold");
 push(a?.media_records_inspected===115,"scan total");
 push(Array.isArray(a?.entries)&&a.entries.length===13,"entry count");
 push(a?.oversized_count===13,"count");
 push(a?.oversized_stored_bytes===43522829,"stored total");
 push(a?.origin_actual_http_checks_performed===0&&a?.guest_browser_checks_performed===0,"browser status was not measured");
 push(a?.production_fixes_made===0,"production repairs not performed");
 push(a?.external_origin_broken_images_claim==="UNVERIFIED_42_REPORTED","broken source allegation cannot become fact");
 push(a?.transferred_weight_reduction_claim==="UNMEASURED_76_PERCENT_REPORTED","wire reduction cannot become fact");
 const seen=new Set(),groups={},e=Array.isArray(a?.entries)?a.entries:[];
 let sum=0;
 for(const x of e){
  push(Number.isInteger(x.media_id)&&!seen.has(x.media_id),"duplicate or malformed id");
  seen.add(x.media_id);sum+=x.original_bytes||0;
  push(x.original_bytes===EXPECTED[x.media_id],"image byte identity "+x.media_id);
  push(typeof x.origin_url==="string"&&x.origin_url.startsWith("https://finalvestige.com/wp-content/uploads/2026/08/"),"origin identity "+x.media_id);
  push(Number.isInteger(x.original_width)&&x.original_width>0&&Number.isInteger(x.original_height)&&x.original_height>0,"master geometry");
  push(x.original_bytes>1572864,"strict cutoff");
  push(x.conditional_max_960?.width===Math.min(x.original_width,960)&&x.conditional_max_960?.height===Math.round(x.original_height*Math.min(x.original_width,960)/x.original_width),"960 no-upscale proportional geometry");
  push(x.conditional_max_960?.upscale===false&&x.conditional_max_960?.publication_candidate===false,"not published");
  push(x.rights_clearance==="HOLD"&&x.asset_binary_sha256===null,"uncleared rights and binary");
  push(x.caching_approved===false&&x.wordpress_upload_approved===false&&x.published_post_edit_approved===false,"no media or CMS writes");
  push(x.exact_current_visitor_src===null&&x.origin_http_status===null&&x.guest_http_status===null&&x.actual_wire_bytes===null&&x.browser_decoding_verified===false,"no invented browser verification");
  push(Array.isArray(x.registered_sizes)&&x.registered_sizes.every(s=>typeof s.virtual==="boolean"&&Number.isInteger(s.width)&&Number.isInteger(s.height)),"sizes not confused with actual delivery");
  groups[x.category]??={count:0,bytes:0};groups[x.category].count++;groups[x.category].bytes+=x.original_bytes;
 }
 push(sum===43522829,"reconstructed storage sum");
 push(seen.size===13&&Object.keys(EXPECTED).every(id=>seen.has(Number(id))),"all 13 exact identities");
 for(const [k,[count,bytes]] of Object.entries(GROUPS)){
  push(groups[k]?.count===count&&groups[k]?.bytes===bytes,"group "+k);
  push(a?.group_totals?.[k]?.count===count&&a?.group_totals?.[k]?.bytes===bytes,"manifest group "+k);
 }
 const by=id=>e.find(x=>x.media_id===id);
 push(by(293)?.usage_evidence?.status==="published_author_bio_jsonld_image"&&by(293)?.usage_evidence?.page_id===234,"published author image");
 push(by(405)?.usage_evidence?.status==="draft_product_page_img_jetpack_819x1024"&&by(405)?.usage_evidence?.page_id===85,"draft cover not live wire");
 push(by(482)?.usage_evidence?.status==="unknown_not_assigned_or_reconciled","opaque PNG not declared orphan");
 const cross=a?.published_post_inline_image_crosscheck;
 push(cross?.published_posts===66&&cross?.stored_inline_img_src_slots===361,"66/361 source census crosscheck");
 push(cross?.exact_filename_matches?.["293_ne_png"]===0&&cross?.exact_filename_matches?.["405_water_cover"]===0&&cross?.exact_filename_matches?.["482_opaque_png"]===0,"none of three in article img tags (not global orphan)");
 push(Array.isArray(cross?.underlying_source_blob_shas)&&cross.underlying_source_blob_shas.join(",")==="05b01ce3876a62233b1bb497cdc4b1e842d487ee,fe4a33b8a0ca0d2c19d8a577d92281af0ce1e9e7,ccda35904b62ed1f2dbda09ab5001c39888b6faa,a4e0ad40652446761fdcc5f879127038255d8838,c3278c73bd6498debb541e9a52dc3df9b4fd3e61,aab2002740fcd59bb0a192d80a86a3b2e1514e26","pinned 6 inventory blobs");
 const checks=a?.read_only_page_checks;
 push(Array.isArray(checks)&&checks.some(x=>x.id===234&&x.status==="publish"&&x.filename_hits.founder_portrait>0)&&checks.some(x=>x.id===85&&x.status==="draft"&&x.filename_hits.water_manual>0),"fresh targeted page evidence");
 return fail;
}
module.exports={validate,EXPECTED};
if(require.main===module){
 const file=process.argv[2]||path.join(__dirname,"oversize13_remaining3_20261105.json");
 const errors=validate(JSON.parse(fs.readFileSync(file,"utf8")));
 if(errors.length){console.error(JSON.stringify({pass:false,errors},null,2));process.exitCode=1}
 else console.log(JSON.stringify({pass:true,records:13,stored_bytes:43522829,rights:"HOLD",browser:"UNVERIFIED"}));
}
