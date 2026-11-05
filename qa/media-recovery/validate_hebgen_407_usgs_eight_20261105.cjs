'use strict';
// Source-only offline crosswalk. No HTTP client, media operations, or WordPress write path.
const EXPECTED_CATALOGS=[
  "https://www.usgs.gov/media/images/earthquake-damage-1959-hebgen-lake-event-yellowstone-plateau",
  "https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0",
  "https://www.usgs.gov/media/images/view-madison-slide-august-21-1959-rapidly-filling-earthquake-lake",
  "https://www.usgs.gov/media/images/dragline-working-lower-outlet-channel-earthquake-lake-october-18-1959",
  "https://www.usgs.gov/media/images/rockslide-damage-golden-gate-area-near-mammoth-hot-springs",
  "https://www.usgs.gov/media/images/sapphire-pool-upper-geyser-basin-erupting-after-1959-hebg",
  "https://www.usgs.gov/media/images/seismic-geyser-eruption-1970",
  "https://www.usgs.gov/media/images/earthquake-lake-and-madison-slide"
];
const FROZEN_BLOB='48e1ebf07207e948ba5802e714eb39659d2e1c1d';
function validate(a, frozen) {
 const errors=[];const check=(p,m)=>{if(!p)errors.push(m)};
 check(a?.schema==='fv-hebgen-407-eight-usgs-item-link-audit-v1','schema');
 if(!a||typeof a!=='object')return errors;
 check(a.post?.id===407&&a.post?.status==='publish'&&a.post?.image_count===8,'wp_article');
 check(a.post?.url==='https://finalvestige.com/2026/08/20/the-lake-wasnt-there-yesterday-hebgen/','article_path');
 check(a.frozen?.git_blob_sha===FROZEN_BLOB,'frozen_blob_provenance');
 check(a.snapshot_caveats?.posts===61&&a.snapshot_caveats?.images===355&&a.snapshot_caveats?.offsite_refs===288,'snapshot_counts');
 check(a.snapshot_caveats?.reported_broken_images_42==='UNVERIFIED'&&a.snapshot_caveats?.reported_wire_reduction_76_pct==='UNMEASURED','unsupported_claim');
 check(a.snapshot_caveats?.oversize_media_items===13&&a.snapshot_caveats?.oversize_orig_stored_bytes===43522829&&a.snapshot_caveats?.production_fixes===0,'oversize_storage_not_wire');
 const pins=(frozen&&Array.isArray(frozen.images))?frozen.images.filter(x=>x.post_id===407):[];
 check(pins.length===8,'frozen_rows');
 check(Array.isArray(a.rows)&&a.rows.length===8,'rows_count');
 if(!Array.isArray(a.rows))return errors;
 const seen=new Set();
 for(const [i,r] of a.rows.entries()){
   const old=pins.find(x=>x.key==='407:'+i);
   check(r?.image_key==='407:'+i&&!seen.has(r?.image_key)&&r?.post_id===407,'unique_key_'+i);seen.add(r?.image_key);
   check(!!old&&r?.published_src===old?.source_url&&r?.published_alt===old?.alt,'exact_original_source_'+i);
   check(r?.official_usgs_record===EXPECTED_CATALOGS[i]&&r?.live_caption_usgs_record===EXPECTED_CATALOGS[i]&&r?.usgs_original_link_exactly_matches_src===true,'official_item_link_'+i);
   check(r?.usgs_item_sources_usage==='Public Domain'&&typeof r?.catalog_credit==='string'&&r.catalog_credit.length>12,'item_rights_credit_'+i);
   check(r?.origin_http_status===null&&r?.guest_browser_http_status===null&&r?.guest_browser_natural_width===null&&r?.guest_browser_natural_height===null&&r?.guest_browser_transferred_bytes===null&&r?.visitor_broken===null,'browser_unknown_'+i);
   check((i===1&&r?.retriever_method==='UNSUPPORTED_BINARY_OCTET_STREAM_WRAPPER'&&r?.retriever_wrapper_status===400)||(i!==1&&r?.retriever_method==='SOURCE_IMAGE_RENDERED_IN_RETRIEVER'&&r?.retriever_wrapper_status===null),'method_status_'+i);
   check(r?.proposed_max_width_px===960&&r?.no_upscale===true&&r?.proposed_derivative_dimensions===null&&r?.original_binary_pixel_dimensions===null,'unverified_size_hold_'+i);
   check(r?.item_specific_rehost_review==='HOLD'&&r?.binary_identity_verified===false&&r?.wire_savings_measured===false,'rights_and_wire_hold_'+i);
   check(r?.wp_media_upload_authorized===false&&r?.media_caching_authorized===false&&r?.post_rewrite_authorized===false,'production_hold_'+i);
   const w=r?.html_declared_width,h=r?.html_declared_height;
   check((w===null&&h===null)||(Number.isInteger(w)&&w>0&&Number.isInteger(h)&&h>0),'html_dimensions_'+i);
   if(old)check(w===old.width_px&&h===old.height_px,'frozen_html_dimensions_'+i);
 }
 return errors;
}
module.exports={validate};
if(typeof require!=='undefined'&&require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const json=JSON.parse(fs.readFileSync(path.join(__dirname,'hebgen_407_usgs_eight_original_links_20261105.json'),'utf8'));
 const frozen=JSON.parse(fs.readFileSync(path.join(__dirname,'parts/02.json'),'utf8'));
 const errors=validate(json,frozen);
 if(errors.length){console.error(errors.join('\n'));process.exitCode=1}
 else console.log('Hebgen 407 eight exact USGS media links: PASS');
}
