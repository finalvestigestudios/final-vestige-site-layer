"use strict";
const fs=require("node:fs");
const path=require("node:path");
const IDS=["NH 69586","NH 69059","UG 21-01.02","NH 84820","NH 84822",null];
const OBS=["FETCH_TIMEOUT","RENDERED_IMAGE","FETCH_TIMEOUT","RENDERED_IMAGE","RENDERED_IMAGE","RENDERED_IMAGE"];
const REL=["official-URL-ID","rendered-photo-heading-NH-69059","official-URL-ID","rendered-photo-heading-NH-84820","official-URL-ID-and-heading","publisher-only-not-NHHC-exact"];
function validate(d,c){
 let e=[],fail=s=>e.push(s);
 if(d?.schema_version!==1||d.post_id!==288||d.wp_readback!=="6/6 exact src and ALT")fail("metadata");
 if(d?.source_inventory_sha!==c?.__blob_sha)fail("census SHA");
 let st=d?.sitewide;
 if(!st||st.posts!==61||st.image_slots!==355||st.external_image_slots!==288||st.originals_over_1_5_mib!==13||st.reported_42_broken_verified!==false||st.claimed_76_pct_transferred_savings_measured!==false||st.production_repaired!==0)fail("unsupported sitewide claim");
 let orig=c?.images?.filter(x=>x.post_id===288).sort((a,b)=>a.slot-b.slot)||[];
 if(orig.length!==6||!Array.isArray(d?.rows)||d.rows.length!==6){fail("slot count");return e;}
 d.rows.forEach((r,i)=>{
 let o=orig[i],v=r?.retriever,a=r?.authority,g=r?.dimensions,b=r?.guest,p=r?.permissions;
 if(r?.key!==`288:${i}`||r?.slot!==i||r?.post_id!==288||r.original_src!==o.source_url||r.original_alt!==o.alt||r.post_url!==o.post_url||r.wordpress_exact_src_alt_read_only_verified!==true)fail("post source "+i);
 if(v?.method!=="web_open_image_retriever_NOT_visitor"||v?.observation!==OBS[i]||v?.http_status!==null||v?.content_type!==null||v?.transferred_bytes!==null)fail("fabricated HTTP "+i);
 if(a?.catalog_id!==IDS[i]||a?.relationship!==REL[i]||a.exact_image_binary_sha256!==null||a.exact_binary_comparison_done!==false||a.rights_status!=="HOLD"||a.rights_and_attribution_verified!==false||!a.record_url?.startsWith(i===5?"https://www.usni.org/":"https://www.history.navy.mil/"))fail("archive identity "+i);
 if(g?.max_width!==960||g.no_upscale!==true||g.published_original_binary_dimensions_known!==false)fail("geometry gate "+i);
 if(i!==5){let w=g.catalog_master_width,h=g.catalog_master_height;if(!Number.isSafeInteger(w)||!Number.isSafeInteger(h)||w<1||h<1||g.conditional_target_width!==Math.min(960,w)||g.conditional_target_height!==Math.round(h*Math.min(960,w)/w))fail("geometry "+i);}
 else if(g.catalog_master_width!==null||g.catalog_master_height!==null||g.conditional_target_width!==null||g.conditional_target_height!==null)fail("invented size "+i);
 if(!b||Object.values(b).some(x=>x!==null))fail("invented browser "+i);
 if(!p||Object.values(p).some(x=>x!==false))fail("unauthorized write "+i);
 });
 return e;
}
module.exports={validate};
if(require.main===module){
let d=JSON.parse(fs.readFileSync(path.join(__dirname,"honda_288_nhhc_20261101.json"))),c=JSON.parse(fs.readFileSync(path.join(__dirname,"parts/03.json")));c.__blob_sha=d.source_inventory_sha;
let errs=validate(d,c);if(errs.length){console.error(errs.join("\n"));process.exitCode=1}else console.log("PASS Honda post 288: six source-locked rights-held records");
}
