'use strict';
// Offline evidence guard; no browser/WordPress/network/write operation.
const validate=function validate(a){
const errors=[],bad=s=>errors.push(s);
if(!a||a.schema!=="fv-malbone-two-virtual-derivative-hold-v1")return ["schema"];
if(a.post?.id!==621||a.post?.status!=="publish"||a.post?.modified!=="2026-09-09T12:03:35"||a.post?.raw_blocks_use_sizeSlug_large!==true||a.post?.raw_img_src_original!==true||a.post?.guest_currentSrc_measured!==false)bad("post");
const c=a.cohort||{},p=a.policy||{};
if(c.published_slots!==2||c.original_stored_bytes!==10352064||c.existing_site_oversize_count!==16||c.existing_site_oversize_original_bytes!==49107665||c.reported_42_broken_browser_confirmed!==false||c.proposed_76_percent_wire_saving_measured!==false)bad("cohort");
if(p.max_width_px!==960||p.no_upscale!==true||p.site_qa_collector_owner!==154||p.homepage_in_scope!==false||p.wp_write_authorized!==false||p.media_download_authorized!==false||p.rehost_or_cache_authorized!==false||p.release_authorized!==false)bad("policy");
if(!Array.isArray(a.items)||a.items.length!==2)return errors.concat("items");
const names=["edit-017-v01-malbone-tunnel-generalpunger-original.jpg","edit-017-v02-nypl-5003296-original.jpg"];
const spec=[[1257,0,4798395,4000,3000,1024,768,960,720],[1258,1,5553669,5667,3831,1024,692,960,649]];
let sum=0;
for(let i=0;i<2;i++){const r=a.items[i],v=spec[i];if(!r){bad("missing "+i);continue}
const source="https://finalvestige.com/wp-content/uploads/2026/08/"+names[i],large="https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/"+names[i]+"?fit="+v[5]+"%2C"+v[6]+"&ssl=1";
if(r.slot!==v[1]||r.media_id!==v[0]||r.stored_original_url!==source||r.stored_bytes!==v[2]||r.native_px?.[0]!==v[3]||r.native_px?.[1]!==v[4])bad("source "+i);
sum+=r.stored_bytes;
if(r.wordpress_large?.virtual!==true||r.wordpress_large?.url!==large||r.wordpress_large?.width!==v[5]||r.wordpress_large?.height!==v[6])bad("virtual "+i);
const d=r.conditional_960px||{};
if(d.width!==v[7]||d.height!==v[8]||d.css_dpr2_max!==480||d.derivative_url!==null||d.approved!==false)bad("size "+i);
if(r.visitor_http!==null||r.visitor_currentSrc!==null||r.visitor_bytes!==null||r.rights_approved!==false||r.release!=="HOLD"||r.provenance?.right_to_transform_verified!==false||r.provenance?.exact_file_identified!==false)bad("release "+i);
if(i===0&&(r.provenance?.primary_catalog_url!==null||r.provenance?.needs_license_link_and_sharealike!==true||r.provenance?.map_readability_hold!==false))bad("photo provenance");
if(i===1&&(r.provenance?.primary_catalog_url!=="https://old-digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0"||r.provenance?.map_readability_hold!==true))bad("map provenance");
}
if(sum!==10352064)bad("sum");
return errors;
};
module.exports={validate};
if(require.main===module){const fs=require('node:fs');let a=JSON.parse(fs.readFileSync(process.argv[2]||__dirname+'/malbone_621_two_media_preflight_20261114.json','utf8'));let e=validate(a);if(e.length){console.error(e);process.exitCode=1}else console.log('PASS original/virtual/960px release gate');}
