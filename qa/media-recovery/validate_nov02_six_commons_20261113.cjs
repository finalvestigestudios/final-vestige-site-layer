'use strict';
/** Offline, fail-closed verifier for the exact Nov 2 FV five-post/six-image audit.
 *  No network, media downloads, WordPress writes, or browser collection.
 */
const expected=[
 ['1917:0',1917,'Piri%20reis%20world%20map%2001.jpg?width=1280','Piri_reis_world_map_01.jpg',1280,1964,2619,960,1280,'PD_ART','Public domain'],
 ['1917:1',1917,'Cantino%20planisphere%20%281502%29.jpg?width=1280','Cantino_planisphere_(1502).jpg',1280,10643,4998,960,451,'PD_SCAN','Public domain'],
 ['1920:0',1920,'Front%20of%204th%20century%20CE%20Roman%20Lycurgus%20Cup%2C%20British%20Museum%20%281958%2C1202.1%29.jpg?width=1280','Front_of_4th_century_CE_Roman_Lycurgus_Cup,_British_Museum_(1958,1202.1).jpg',1280,2720,3649,960,1288,'CC_BY_4_0','Chappsnet, CC BY 4.0'],
 ['1920:1',1920,'Top%20view%20of%20the%20famed%20Lycurgus%20Cup%20in%20the%20British%20Museum%2C%20showing%20the%20glass%20both%20green%20and%20ruby%20red.jpg?width=1280','Top_view_of_the_famed_Lycurgus_Cup_in_the_British_Museum,_showing_the_glass_both_green_and_ruby_red.jpg',1280,3024,4032,960,1280,'CC_BY_4_0','Chappsnet, CC BY 4.0'],
 ['1924:0',1924,'%22Le%20Baquet%20de%20Mesmer%22%20Wellcome%20M0006352.jpg?width=900','"Le_Baquet_de_Mesmer"_Wellcome_M0006352.jpg',900,2988,3538,960,1137,'CC_BY_4_0','CC BY 4.0'],
 ['1926:0',1926,'Crystal%20Skull%20British%20Museum%2026072013%2005.jpg?width=900','Crystal_Skull_British_Museum_26072013_05.jpg',900,1436,2001,960,1338,'CC0_1_0','Vassil, CC0']
];
const postIds=[1917,1920,1922,1924,1926],postCounts=[2,2,0,1,1];
const rootKeys='schema observed_local_date method historical live posts images release caveats'.split(' ');
const historicalKeys='post_count stored_inline_images media_recovery_offsite siteqa_offsite historical_reported_broken guest_confirmed_broken claimed_wire_reduction_pct measured_wire_reduction_pct'.split(' ');
const liveKeys='post_count stored_inline_images new_post_count new_inline_images new_commons_external_images expanded_same_method_offsite_count'.split(' ');
const postKeys='post_id title url status modified_local featured_media inline_image_count'.split(' ');
const imageKeys='slot post_id post_url published_src published_alt published_figcaption html_width_attr html_height_attr requested_redirect_width_px origin_type official_catalog_url catalog_original_px catalog_license catalog_attribution catalog_original_is_visitor_transfer conditional_max_derivative_px sensitive_scene_gate editorial_same_scene_review_required visitor_http_status visitor_current_src visitor_encoded_transfer_bytes visitor_pixels rendered_css_width dpr source_binary_sha256 rights_rehosting_approved wordpress_media_write_approved third_party_cache_approved derivative_approved status'.split(' ');
const releaseKeys='max_width_px no_upscale keep_map_zoom_and_labels require_browser_cdp_and_css_dpr require_attribution_license_links_and_change_notices_for_cc_by media_downloads third_party_cache_writes wp_production_writes homepage_changes merges deployments subscription_spend_usd siteqa_browser_owner_pr p0_queue_unchanged'.split(' ');
function keysAre(o,keys){return o&&typeof o==='object'&&!Array.isArray(o)&&
 Object.keys(o).sort().join('|')===keys.slice().sort().join('|');}
function eqArray(a,b){return Array.isArray(a)&&a.length===b.length&&a.every((x,i)=>x===b[i]);}
function validateAudit(a){
 const errors=[],bad=(v)=>errors.push(v);
 if(!keysAre(a,rootKeys))return {ok:false,errors:['root_schema_fields_modified']};
 if(a.schema!=='fv-nov02-five-post-six-commons-audit-v1'||a.observed_local_date!=='2026-11-13'||
 typeof a.method!=='string'||!a.method.includes('read-only WordPress'))bad('method_or_date');
 const h=a.historical,l=a.live,r=a.release;
 if(!keysAre(h,historicalKeys)||h.post_count!==61||h.stored_inline_images!==355||
 h.media_recovery_offsite!==288||h.siteqa_offsite!==286||h.historical_reported_broken!==42||
 h.guest_confirmed_broken!==null||h.claimed_wire_reduction_pct!==76||h.measured_wire_reduction_pct!==null)bad('historical_evidence_modified');
 if(!keysAre(l,liveKeys)||l.post_count!==66||l.stored_inline_images!==361||
 l.new_post_count!==5||l.new_inline_images!==6||l.new_commons_external_images!==6||
 l.expanded_same_method_offsite_count!==294)bad('expanded_counts_modified');
 if(!keysAre(r,releaseKeys)||r.max_width_px!==960||r.no_upscale!==true||
 r.keep_map_zoom_and_labels!==true||r.require_browser_cdp_and_css_dpr!==true||
 r.require_attribution_license_links_and_change_notices_for_cc_by!==true||
 !eqArray(r.p0_queue_unchanged,['285:5','285:2','287:5','418:1','418:2','407:1'])||
 r.siteqa_browser_owner_pr!==154||
 ['media_downloads','third_party_cache_writes','wp_production_writes','homepage_changes',
 'merges','deployments','subscription_spend_usd'].some(k=>r[k]!==0))bad('release_policy_modified');
 if(!Array.isArray(a.caveats)||a.caveats.length!==6||a.caveats.some(v=>typeof v!=='string'))bad('caveats_missing');
 if(!Array.isArray(a.posts)||a.posts.length!==5)bad('post_cohort_missing');
 else for(let i=0;i<5;i++){
 const p=a.posts[i],id=postIds[i];if(!keysAre(p,postKeys)||p.post_id!==id||
 p.status!=='publish'||p.inline_image_count!==postCounts[i]||
 typeof p.url!=='string'||!p.url.startsWith('https://finalvestige.com/2026/11/02/')||
 p.featured_media!==0||!/^2026-11-0[35]T/.test(p.modified_local||'')||
 typeof p.title!=='string'||p.title.length<12)bad('post_source_mutation:'+id);
 }
 if(!Array.isArray(a.images)||a.images.length!==6)bad('six_source_rows_required');
 else for(let i=0;i<6;i++){
 const x=a.images[i],e=expected[i];
 if(!keysAre(x,imageKeys)){bad('image_schema:'+i);continue;}
 const src='https://commons.wikimedia.org/wiki/Special:Redirect/file/'+e[2];
 const cat='https://commons.wikimedia.org/wiki/File:'+e[3];
 const post=a.posts?.find(p=>p.post_id===e[1]);
 if(x.slot!==e[0]||x.post_id!==e[1]||x.post_url!==post?.url||
 x.published_src!==src||x.official_catalog_url!==cat||
 x.origin_type!=='WIKIMEDIA_COMMONS_SPECIAL_REDIRECT'||
 x.requested_redirect_width_px!==e[4]||
 !eqArray(x.catalog_original_px,[e[5],e[6]])||
 !eqArray(x.conditional_max_derivative_px,[e[7],e[8]])||
 x.catalog_license!==e[9]||
 typeof x.catalog_attribution!=='string'||x.catalog_attribution.length<5||
 typeof x.published_alt!=='string'||x.published_alt.length<30||
 typeof x.published_figcaption!=='string'||!x.published_figcaption.includes(e[10])||
 x.html_width_attr!==null||x.html_height_attr!==null||
 !['MAP_ZOOM','COLOR_CROP','ENGRAVING_DETAIL','PHOTO_CROP'].includes(x.sensitive_scene_gate)||
 x.catalog_original_is_visitor_transfer!==false||
 x.editorial_same_scene_review_required!==true||
 ['visitor_http_status','visitor_current_src','visitor_encoded_transfer_bytes','visitor_pixels',
 'rendered_css_width','dpr','source_binary_sha256'].some(k=>x[k]!==null)||
 ['rights_rehosting_approved','wordpress_media_write_approved','third_party_cache_approved',
 'derivative_approved'].some(k=>x[k]!==false)||
 x.status!=='HOLD_BROWSER_RIGHTS_DENSITY')bad('slot_source_rights_or_browser_forgery:'+e[0]);
 }
 return{ok:errors.length===0,errors};
}
module.exports={validateAudit};
if(require.main===module){const fs=require('node:fs');
 const src=process.argv[2];if(!src){console.error('Usage: node validate_nov02_six_commons_20261113.cjs AUDIT.json');process.exitCode=2;}
 else{let r;try{r=validateAudit(JSON.parse(fs.readFileSync(src,'utf8')));}catch(e){r={ok:false,errors:['invalid_json:'+e.message]};}
 console.log(JSON.stringify(r));if(!r.ok)process.exitCode=2;}
}
