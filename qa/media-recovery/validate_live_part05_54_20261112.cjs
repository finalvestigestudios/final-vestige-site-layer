"use strict";
function need(ok,why){if(!ok)throw Error("MEDIA_HOLD: "+why)}
function https(s){return typeof s==="string"&&s.startsWith("https://")&&s.length>12}
function validate(d){
 need(d.schema==="fv-media-live-part05-54-commons-v1"&&d.method==="READ_ONLY_WP_EDIT_VS_FROZEN_PART05","schema/method");
 need(d.baseline.blob==="9b16b828342a9ac338f3e65610fd3d8d508355e9"&&d.catalog_register.blob==="4965a862f7de7de46c1f4a1e26f3ca70a8c38805","frozen-source custody");
 need(d.baseline.posts===61&&d.baseline.images===355&&d.baseline.external===288&&d.siteqa_pr===154&&d.draft_pr===1703,"ownership/cohort");
 need(d.unverified.historical_broken_claim===42&&d.unverified.guest_confirmed_failures===0&&d.unverified.network_saving_76pct_measured===false&&d.unverified.real_guest_transfer===null&&d.unverified.real_cls===null,"no invented results");
 need(d.unverified.originals_over_1500000_bytes===15&&d.unverified.stored_original_bytes===47096779,"stored weight");
 for(const [k,v]of Object.entries(d.policy))need(v===true,"policy "+k);
 need(Array.isArray(d.posts)&&d.posts.length===8&&Array.isArray(d.rows)&&d.rows.length===54,"rows");
 let ids=new Set(d.posts.map(p=>p.post_id)),seen=new Set();need(ids.size===8,"unique post IDs");
 for(const p of d.posts)need(p.status==="publish"&&https(p.post_url)&&p.live_image_count===p.frozen_image_count&&d.rows.filter(r=>r.post_id===p.post_id).length===p.live_image_count,"post integrity");
 for(const r of d.rows){
 need(!seen.has(r.slot),"duplicate image");seen.add(r.slot);
 need(ids.has(r.post_id)&&r.slot.startsWith(r.post_id+":"),"slot binding");
 need(https(r.live_src)&&r.live_src===r.frozen_src&&r.source_equal===true&&r.live_alt===r.frozen_alt&&r.alt_equal===true,"source/ALT drift");
 need(r.source_host==="commons.wikimedia.org"&&r.is_commons_redirect===true&&r.live_src.startsWith("https://commons.wikimedia.org/wiki/Special:Redirect/file/"),"Commons origin");
 need(r.html_width===null&&r.html_height===null&&r.literal_srcset_present===false,"unobserved dimensions/srcset");
 for(const k of ["origin_http_status","guest_http_status","guest_current_src","guest_natural_px","guest_wire_bytes","guest_broken"])need(r[k]===null,"fabricated HTTP/guest "+k);
 for(const k of ["source_native_dimensions_verified","actual_css_width_verified","rights_cleared","exact_pixel_match_verified","rehost_or_cache_approved","wordpress_write_approved"])need(r[k]===false,"unauthorized rights/operation "+k);
 const s=r.staging;need(s.conditional_max_width_px===960&&s.no_upscale===true&&s.require_scene_identity===true&&s.require_label_legibility===true&&s.require_individual_rights_review===true,"unsafe derivatives");
 need(Array.isArray(r.catalog_candidates)&&r.catalog_candidates.length>0,"missing source provenance");
 for(const a of r.catalog_candidates){
 need(https(a.catalog_url)||https(a.authoritative_primary_url),"invalid catalog");
 need(a.exact_image_match_verified===false&&a.item_rights_cleared===false,"premature rights/pixel clearance");
 if(a.conditional_960px!==null)need(Array.isArray(a.conditional_960px)&&a.conditional_960px.length===2&&a.conditional_960px.every(x=>Number.isInteger(x)&&x>0)&&a.conditional_960px[0]<=960,"960 geometry");
 }}
 const c=d.counts,t={posts:d.posts.length,images:d.rows.length,frozen_images:d.rows.length,source_equal:d.rows.filter(r=>r.source_equal).length,alt_equal:d.rows.filter(r=>r.alt_equal).length,missing_dimensions:d.rows.filter(r=>r.html_width===null&&r.html_height===null).length,both_dimensions:d.rows.filter(r=>r.html_width!==null&&r.html_height!==null).length,partial_dimensions:d.rows.filter(r=>(r.html_width===null)!==(r.html_height===null)).length,literal_srcset:d.rows.filter(r=>r.literal_srcset_present).length,commons_redirect:d.rows.filter(r=>r.is_commons_redirect).length,candidate_mapped:d.rows.filter(r=>r.catalog_candidates.length>0).length,candidates_with_conditional_px:d.rows.filter(r=>r.catalog_candidates.some(x=>x.conditional_960px)).length};
 for(const [k,v]of Object.entries(t))need(c[k]===v,"aggregate "+k);
 need(t.images===54&&t.source_equal===54&&t.alt_equal===54&&t.missing_dimensions===54&&t.commons_redirect===54&&t.candidate_mapped===54&&t.literal_srcset===0,"exact frozen cohort");
 return t;
}
if(typeof require!=="undefined"&&require.main===module){const fs=require("node:fs"),path=require("node:path");const d=JSON.parse(fs.readFileSync(process.argv[2]||path.join(__dirname,"live_part05_8posts_54_commons_20261112.json"),"utf8"));console.log(JSON.stringify(validate(d)));}
module.exports={validate};
