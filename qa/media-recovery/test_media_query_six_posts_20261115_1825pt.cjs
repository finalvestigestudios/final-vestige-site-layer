'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const {validate}=require('./validate_media_query_six_posts_20261115_1825pt.cjs');
const original=JSON.parse(fs.readFileSync(__dirname+'/media_query_six_posts_20261115_1825pt.json','utf8'));
const clone=()=>structuredClone(original);
test('known six-post snapshot is valid',()=>assert.deepEqual(validate(original),[]));
const cases={
 'reject false HTTP status':x=>x.rows[0].guest_http_status=404,
 'reject presumed visitor breakage':x=>x.rows[0].visitor_broken=true,
 'reject made-up network reduction':x=>x.claims.claimed_76_percent_network_reduction_measured=true,
 'reject forged source host':x=>x.rows[0].source_url='https://example.com/img.jpg?by=cms_fixed_width',
 'reject falsely preserved query':x=>x.rows[0].view_query_outcome='preserved',
 'reject view query injection':x=>x.rows[0].view_url+='&by=cms_fixed_width',
 'reject unauthorized cache':x=>x.rows[0].cache_authorized=true,
 'reject unauthorized WordPress upload':x=>x.rows[0].wp_upload_authorized=true,
 'reject invented dimensions':x=>x.rows[1].proportional_review_height_px=640,
 'reject unreviewed rights approval':x=>x.rows[0].rights_status='CLEARED',
 'reject exact-frame falsehood':x=>x.rows[0].official_candidates[0].source_fidelity='EXACT_FRAME',
 'reject cohort inflation':x=>x.counts.inline_image_slots=39,
 'reject missing slot':x=>x.rows.pop(),
 'reject flipped direct route':x=>x.rows[2].view_url='https://i0.wp.com/example.net/altered.jpg?ssl=1',
 'reject oversize derivative':x=>x.rows[0].official_candidates[0].conditional_review_pixels.width=1024,
 'reject wrong source query key':x=>x.rows[1].source_query_keys=['token']
};
for(const [name,mutate] of Object.entries(cases))test(name,()=>{let x=clone();mutate(x);assert.ok(validate(x).length>0,name);});
