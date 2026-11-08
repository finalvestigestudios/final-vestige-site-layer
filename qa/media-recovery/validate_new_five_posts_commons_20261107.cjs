"use strict";
// Offline safe QA; does not touch CMS, network, images or disk outside reading its local ledger.
function verify(a){
 const ck=(ok,name)=>{if(!ok)throw Error(name)};
 ck(a.schema==="fv-new-5-posts-6-commons-v1","schema");ck(a.baseline.posts===61&&a.baseline.inline_src===355,"61 cohort");ck(a.current.posts===66&&a.current.inline_src===361,"66 cohort");
 ck(a.current.posts-a.baseline.posts===5&&a.current.inline_src-a.baseline.inline_src===6,"cohort difference");
 const expected={1926:1,1924:1,1922:0,1920:2,1917:2};
 ck(a.posts.length===5&&new Set(a.posts.map(p=>p.id)).size===5,"five posts");
 for(const p of a.posts)ck(Object.prototype.hasOwnProperty.call(expected,p.id)&&expected[p.id]===p.count,"post image count");
 ck(a.rows.length===6&&a.posts.reduce((s,p)=>s+p.count,0)===6,"six image refs");
 ck(new Set(a.rows.map(r=>r.key)).size===6,"duplicate slot");
 for(const r of a.rows){
  ck(r.key===r.post_id+":"+r.slot&&expected[r.post_id]>0,"mapping");
  const aurl="https://commons.wikimedia.org/wiki/Special:Redirect/file/",burl="https://commons.wikimedia.org/wiki/File:";
  ck(r.source_url.startsWith(aurl)&&r.file_page.startsWith(burl),"source host");
  ck(decodeURIComponent(r.source_url.slice(aurl.length).split("?")[0])===decodeURIComponent(r.file_page.slice(burl.length)).replaceAll("_"," "),"exact source filename");
  ck(r.source_url.endsWith("?width="+r.source_requested_width),"requested variant");
  const [w,h]=r.image_orig_catalog_px,[pw,ph]=r.preview_max_960_px;
  ck(w>0&&h>0&&Number.isInteger(w)&&Number.isInteger(h)&&pw===Math.min(w,960)&&ph===Math.round(h*pw/w)&&pw<=w&&ph<=h,"960 no crop");
  ck(r.html_width_attr===null&&r.html_height_attr===null,"invented HTML dims");
  ck(r.alt.length>20&&r.catalog_html_opened===true&&r.catalog_credit.length>3&&["CC0 1.0","CC BY 4.0","PD-art","PD-mechanical scan"].includes(r.catalog_license),"catalog data");
  ck(r.map_zoom_original_link_required===(r.subject==="detail-heavy historic map"),"map zoom");
  ck([r.source_origin_http,r.guest_chrome_http,r.guest_decode,r.wire_encoded_bytes].every(x=>x===null),"invented browser");
  ck([r.rights_review_complete,r.attribution_review_complete,r.cache_approved,r.wp_upload_approved,r.wp_post_edit_approved].every(x=>x===false),"premature release");
 }
 ck(a.older_61_post_srcs_full_diff_verified===false,"unverified older source diff");
 ck(a.claimed_broken_42==="UNVERIFIED"&&a.claimed_76_percent_wire_saving==="UNMEASURED"&&a.wire_before===null&&a.wire_after===null,"false outcome");
 for(const k of ["no_wp_write","no_asset_download","no_third_party_cache","no_homepage_change","no_spend","no_new_browser_probe"])ck(a[k]===true,k);
 return {pass:true,posts:5,image_refs:6};
}
module.exports={verify};
if(require.main===module){const fs=require("node:fs"),path=require("node:path");console.log(JSON.stringify(verify(JSON.parse(fs.readFileSync(process.argv[2]||path.join(__dirname,"new_five_posts_six_commons_20261107.json"),"utf8")))));}
