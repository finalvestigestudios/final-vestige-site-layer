'use strict';
const assert=require('node:assert/strict');
const {test}=require('node:test');
const fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_skyway_visual_fidelity_287_20261114.cjs');
const baseline=JSON.parse(fs.readFileSync(path.join(__dirname,'skyway_visual_fidelity_287_20261114.json'),'utf8'));
test('two source-and-scene faithful suggestions, zero production release',()=>{
 const r=validate(baseline);assert.equal(r.ok,true,JSON.stringify(r.errors));assert.equal(r.proposed_editorial_items,2);assert.equal(r.ready_for_publication,false);
});
const cases=[
 ['swapped slots',a=>a.items.reverse()],
 ['changed original src',a=>a.items[0].published_source_url='https://example.com/image.jpg'],
 ['fake same-binary claim',a=>a.items[1].same_binary_or_crop_verified=true],
 ['copyright silently cleared',a=>a.items[0].rights_to_copy_or_cache=true],
 ['copyright review forged',a=>a.items[1].copyright_review_complete=true],
 ['invented guest 404',a=>a.items[1].actual_guest_http_status=404],
 ['invented natural pixels',a=>a.items[0].actual_guest_natural_dimensions_px=[505,541]],
 ['invented native pixels',a=>a.items[1].native_file_dimensions_px=[1000,667]],
 ['invented wire bytes',a=>a.items[0].guest_wire_bytes=1],
 ['falsified wrapper as origin HTTP',a=>a.items[1].original_retriever_observation='ORIGIN_HTTP_404'],
 ['fake replacement authorization',a=>a.items[1].proposed_image_src_change=true],
 ['upscaling allowed',a=>a.items[0].no_upscale=false],
 ['oversized 1200px derivative',a=>a.items[1].max_conditional_derivative_width_px=1200],
 ['changes not the exact proposed alt',a=>a.items[0].proposed_alt='Summit Venture in the image'],
 ['untested caption edit',a=>a.items[1].proposed_caption_html='Different article'],
 ['disguised second bridge in ALT',a=>a.items[1].proposed_alt='New bridge beside wreckage'],
 ['silently drops figure correction',a=>a.items.pop()],
 ['extra unsolicited field',a=>a.items[0].license='public domain'],
 ['false 42 visitor failures',a=>a.context.reported_broken_42_guest_confirmed=true],
 ['false 76 percent realized',a=>a.context.proposed_76_pct_wire_reduction_measured=true],
 ['wrong over-threshold inventory',a=>a.context.oversize_stored_bytes_last_confirmed=0],
 ['wordpress production write',a=>a.policy.wordpress_production_writes=1],
 ['rights cache made true',a=>a.policy.cache_or_rehost=true],
 ['site qa collector collision',a=>a.policy.siteqa_browser_collector_modified=true],
 ['homepage work',a=>a.policy.homepage_design_modified=true],
 ['paid tool',a=>a.policy.spend_usd=1]
];
for(const [label,change] of cases)test('HOLD on '+label,()=>{const a=structuredClone(baseline);change(a);assert.equal(validate(a).ok,false)});
