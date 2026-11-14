'use strict';
const assert = require('node:assert/strict');
function validate(a) {
 const fail = [];
 const eq = (x,y) => JSON.stringify(x) === JSON.stringify(y);
 if(a.schema !== 'fv-4182-uscg-museum-same-scene-bridge-v1') fail.push('schema');
 if(a.site_post?.slot !== '418:2' || a.site_post?.stored_src !== 'https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg' || a.site_post?.current_wp_src_reverified_this_run !== false) fail.push('source-lock');
 if(a.source_observation?.retriever_status !== 403 || a.source_observation?.retriever_semantics !== 'WEB_TOOL_FORBIDDEN_NOT_ORIGIN_OR_GUEST_HTTP' || ['origin_http','guest_http','guest_current_src','guest_natural_px','guest_encoded_bytes','guest_broken'].some(k => a.source_observation[k] !== null)) fail.push('method-boundary');
 const names = ['5_-Scotch_Cap_debris2_1946-600x463.jpg','Scotch_Cap_debris3_1946-600x458.jpg','Scotch_Cap_debris1_1946-600x471.jpg','6_-Scotch-Cap-remains-e1728394850930-600x474.jpg'];
 const heights = [463,458,471,474];
 const labels = ['SAME_FILENAME_STEM_AND_VISUALLY_SAME_1946_SCENE_NOT_BINARY_PROVEN','DIFFERENT_1946_AFTER_SCENE_NOT_DROP_IN','DIFFERENT_1946_OVERHEAD_SCENE_NOT_DROP_IN','DIFFERENT_1946_AERIAL_SCENE_NOT_DROP_IN'];
 if(!Array.isArray(a.candidates) || a.candidates.length !== 4) fail.push('candidate-count');
 else for(let i=0;i<4;i++){
 const c=a.candidates[i];
 if(c.rank !== i+1 || c.url !== 'https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/'+names[i] || c.catalog_url !== 'https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/' || c.relation !== labels[i] || c.event_date !== '1946-04-01' || c.attribution !== 'U.S. Coast Guard' || c.observed_method !== 'web.click' || c.retriever_displayed !== true || !eq(c.published_image_px,[600,heights[i]]) || !eq(c.allowable_max_960_no_upscale_px,[600,heights[i]]) || c.right_to_rehost !== null || c.license !== 'USCG_CREDITED_FEDERAL_WORK_PROVENANCE_NEEDS_ITEM_CONFIRMATION' || c.sha256 !== null || c.byte_size !== null || c.crop_match_original !== null || c.pixels_match_original !== (i===0 ? null : false)) fail.push('candidate:'+i);
 }
 if(!a.editorial_hazards?.[0]?.includes('1964') || !a.editorial_hazards?.[0]?.includes('1946') || !a.source_links?.noaa_date_conflict?.startsWith('https://oceanexplorer.noaa.gov/')) fail.push('date-conflict');
 const g=a.gate || {};
 if(g.confirmed_browser_failure !== false || g.release !== 'HOLD_GUEST_RIGHTS_PIXEL_PARITY' || g.right_to_cache !== false || g.wordpress_media_write !== false || g.wordpress_post_write !== false || g.full_block_rewrite !== false || g.homepage_change !== false || g.subscription_spend_usd !== 0 || g.downloaded_binaries !== 0 || g.source_max_width_px !== 960 || g.no_upscale !== true || g.qa_owner_pr !== 154 || !eq(g.first_priority,['285:5','285:2','287:5','418:1','418:2','407:1'])) fail.push('release-gate');
 if(a.context?.reported_broken_unverified !== 42 || a.context?.measured_visitor_wire_reduction_percent !== null || a.context?.oversize_decimal_mb_originals_current !== 16 || a.context?.oversize_stored_bytes_current !== 49107665) fail.push('aggregate');
 return {ok:fail.length===0,violations:fail};
}
module.exports={validate};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const input=process.argv[2]||path.join(__dirname,'scotch_cap_418_2_museum_scene_bridge_20261113.json');
 const res=validate(JSON.parse(fs.readFileSync(input,'utf8')));
 assert.equal(res.ok,true,JSON.stringify(res.violations));
 console.log('PASS museum same-scene audit (release remains HOLD)');
}
