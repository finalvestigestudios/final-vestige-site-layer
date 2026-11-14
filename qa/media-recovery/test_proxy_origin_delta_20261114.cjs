'use strict';
const assert=require('node:assert/strict');
const {test}=require('node:test');
const fs=require('node:fs'),path=require('node:path');
const {isOffsite,reconcile,validate}=require('./validate_proxy_origin_delta_20261114.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'proxy_origin_delta_61_posts_20261114.json'),'utf8'));
test('canonical 61-row report passes',()=>assert.equal(validate(original).ok,true));
test('both publisher-targeted WP proxy URLs are offsite',()=>{
 for(const c of original.cases)assert.equal(isOffsite(c.stored_src),true);
});
test('WP proxy targeting finalvestige.com is first party',()=>assert.equal(isOffsite('https://i0.wp.com/finalvestige.com/wp-content/uploads/a.png?ssl=1'),false));
test('direct external URL remains offsite',()=>assert.equal(isOffsite('https://commons.wikimedia.org/wiki/Special:Redirect/file/x.jpg'),true));
test('eight-part source reconciling uses URL path not proxy hostname',()=>{
 const parts=Array.from({length:8},()=>({posts:[],images:[]}));
 parts[0].posts=[{id:285},{id:291}];
 parts[0].images=[
  {key:'285:0',post_id:285,slot:0,source_url:'https://finalvestige.com/a.png',source_kind:'first_party'},
  {key:'285:1',post_id:285,slot:1,source_url:original.cases[0].stored_src,source_kind:'external'},
  {key:'291:0',post_id:291,slot:0,source_url:original.cases[1].stored_src,source_kind:'external'}
 ];
 const res=reconcile('post_id,stored_img_src_count,offsite_src_count\n285,2,0\n291,1,0',parts);
 assert.deepEqual(res.map(r=>[r.post_id,r.delta]),[[285,1],[291,1]]);
});
test('reconcile rejects false external label for first-party source',()=>{
 const parts=Array.from({length:8},()=>({posts:[],images:[]}));
 parts[0].posts=[{id:285}];
 parts[0].images=[{key:'285:0',post_id:285,slot:0,source_url:'https://finalvestige.com/a.png',source_kind:'external'}];
 assert.throws(()=>reconcile('post_id,stored_img_src_count,offsite_src_count\n285,1,0',parts));
});
const mutations=[
 ['invented 404',a=>a.cases[0].visitor_http_status=404],
 ['fabricated body pixels',a=>a.cases[1].visitor_natural_px=[960,720]],
 ['fabricated bytes',a=>a.cases[0].visitor_wire_bytes=1024],
 ['retriever 200 misrepresented',a=>a.cases[1].retriever_http_status=200],
 ['wrong media ownership',a=>a.cases[0].stored_src='https://i0.wp.com/finalvestige.com/x.jpg'],
 ['wrong origin',a=>a.cases[1].target_origin='finalvestige.com'],
 ['invented native dimensions',a=>a.cases[1].native_px=[960,540]],
 ['illegal caching',a=>a.cases[0].cache_allowed=true],
 ['invented reuse license',a=>a.cases[1].rights_cleared=true],
 ['approval to replace',a=>a.cases[0].replacement_allowed=true],
 ['upscaling',a=>a.cases[1].no_upscale=false],
 ['width > 960',a=>a.cases[0].max_conditional_width_px=1200],
 ['false actual broken total',a=>a.current_issues.actual_guest_broken=42],
 ['false 76 percent savings',a=>a.current_issues.actual_visitor_weight_reduction_pct=76],
 ['changed QA offsite number',a=>a.rows[0].qa_offsite++],
 ['inverted delta',a=>a.rows.find(r=>r.post_id===285).delta=-1],
 ['lost post row',a=>a.rows.pop()],
 ['mismatched evidence blob',a=>a.sources.media.parts[0].blob='bad'],
 ['unsupported causal certainty',a=>a.root_cause='CONFIRMED_BUG'],
 ['Site QA collector touched',a=>a.release.siteqa_browser_collector_touched=true],
 ['WordPress written',a=>a.release.wp_production_write=true],
 ['media downloaded',a=>a.release.media_downloads=2]
];
for(const [name,mutate] of mutations)test('fail closed: '+name,()=>{
 const a=structuredClone(original);mutate(a);assert.equal(validate(a).ok,false);
});

