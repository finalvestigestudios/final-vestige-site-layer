'use strict';
const EXPECTED={'289:2':['by','dropped','k.sinaimg.cn'],'283:3':['resize','dropped','bloximages.chicago2.vip.townnews.com'],'291:0':['ssl','preserved','i0.wp.com'],'291:3':['url','preserved','brightspotcdn.byui.edu'],'279:5':['e,v,t','preserved','media.licdn.com'],'276:2':['id','preserved','ids.si.edu'],'274:4':['image,rendition','preserved','www.history.navy.mil']};
const IDS=new Map([[289,6],[283,7],[291,6],[279,6],[276,6],[274,7]]);
const NIL=['guest_http_status','origin_http_status','jetpack_http_status','guest_current_src','guest_natural_width','guest_transfer_bytes','visitor_broken','source_native_pixels','proportional_review_height_px'];
function validate(d){
 const e=[];const bad=(x)=>e.push(x);
 if(d?.schema!=='fv-media-six-post-source-query-fidelity-v1'||d?.observed_date_pt!=='2026-11-15')bad('schema_or_date');
 if(d?.counts?.published_posts!==6||d?.counts?.inline_image_slots!==38||d?.counts?.query_bearing_source_slots!==7||d?.counts?.query_preserved!==5||d?.counts?.query_dropped!==2)bad('counts');
 if(!Array.isArray(d?.posts)||d.posts.length!==6)bad('posts');
 else {const seen=new Set();let total=0;for(const p of d.posts){if(!IDS.has(p.id)||seen.has(p.id)||p.slots!==IDS.get(p.id)||!/^https:\/\/finalvestige\.com\//.test(p.link||'')||!p.modified)bad('post_identity');seen.add(p.id);total+=p.slots;}if(seen.size!==6||total!==38)bad('post_total');}
 if(!Array.isArray(d?.rows)||d.rows.length!==7)bad('rows');
 else {const seen=new Set();let lost=0;for(const r of d.rows){const expect=EXPECTED[r?.key];if(!expect||seen.has(r.key)){bad('key');continue;}seen.add(r.key);try{const u=new URL(r.source_url),v=new URL(r.view_url);const keys=[...u.searchParams.keys()];if(u.protocol!=='https:'||v.protocol!=='https:'||u.hostname!==expect[2]||keys.join(',')!==expect[0]||JSON.stringify(keys)!==JSON.stringify(r.source_query_keys))bad('source_identity:'+r.key);if(r.view_query_outcome!==expect[1])bad('outcome:'+r.key);if(expect[1]==='preserved'){if(v.href!==u.href)bad('preserved_url:'+r.key);}else{lost++;if(v.hostname!=='i0.wp.com'||v.pathname!=='/'+u.hostname+u.pathname||keys.some(k=>v.searchParams.has(k))||v.searchParams.get('ssl')!=='1')bad('dropped_query_route:'+r.key);} }catch{bad('invalid_url:'+r.key);}
 if(NIL.some(k=>r[k]!==null)||r.max_review_width_px!==960||r.no_upscale!==true||r.cache_authorized!==false||r.wp_upload_authorized!==false||r.post_rewrite_authorized!==false||r.rights_status!=='HOLD_UNVERIFIED')bad('unverified_or_authorized:'+r.key);
 if(!Array.isArray(r.official_candidates)||(!['289:2','283:3'].includes(r.key)&&r.official_candidates.length))bad('candidates:'+r.key);
 for(const c of r.official_candidates||[]){if(c.rights_status!=='HOLD_ITEM_LEVEL_REVIEW'||c.source_fidelity==='EXACT_FRAME'||!/^https:\/\//.test(c.catalog_url||'')||c.conditional_review_pixels?.width>960||c.catalog_high_pixels&&(!Number.isInteger(c.catalog_high_pixels.width)||!Number.isInteger(c.catalog_high_pixels.height)))bad('candidate_hold:'+r.key);}
 }if(seen.size!==7||lost!==2)bad('slot_totals');}
 if(d?.claims?.reported_42_broken_guest_verified!==false||d?.claims?.claimed_76_percent_network_reduction_measured!==false)bad('fabricated_claim');
 if(d?.historical_cohorts?.original_media_oversize_stored_bytes!==64385752||d?.historical_cohorts?.original_media_over_1500000_bytes!==20||d?.historical_cohorts?.current_posts!==66||d?.historical_cohorts?.frozen_posts!==61)bad('cohort');
 return e;
}
module.exports={validate};
if(require.main===module){const fs=require('node:fs');const p=process.argv[2];const issues=validate(JSON.parse(fs.readFileSync(p||__dirname+'/media_query_six_posts_20261115_1825pt.json','utf8')));if(issues.length){console.error(issues.join('\n'));process.exitCode=1}else console.log('PASS: 7 exact URLs, 2 query losses, 0 guest claims');}
