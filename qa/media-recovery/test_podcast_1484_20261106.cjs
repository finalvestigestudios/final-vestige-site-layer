'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_podcast_1484_20261106.cjs');
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'podcast_1484_drive_commons_four_20261106.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(fixture));
test('four authentic page slots pass the read-only source catalog/rights gate',()=>assert.deepEqual(validate(fixture),[]));
const cases=[
['missing asset',a=>a.images.pop()],
['invented broken image',a=>a.images[0].visitor_broken=true],
['fabricated browser 404',a=>a.images[0].browser_http=404],
['fabricated cold bytes',a=>a.images[1].visitor_wire_bytes=1125],
['claimed 42 browser failures',a=>a.reported_42_visitor_broken=42],
['claimed 76 percent saving',a=>a.measured_76_percent_transfer_reduction=76],
['different Drive artwork',a=>a.images[0].src+='&id=wrong'],
['broken historic photo identity',a=>a.images[1].src=a.images[2].src],
['lost incident chronology',a=>a.images[1].historical_parity_note=''],
['upscaled AP aftermath',a=>a.images[2].conditional_960_no_upscale_pixels=[960,769]],
['cropped memorial',a=>a.images[3].conditional_960_no_upscale_pixels=[960,600]],
['loss of QuesterMark attribution',a=>a.images[3].credit_proposal='Museum memorial'],
['incorrect CC BY SA license',a=>a.images[3].license_reference='https://creativecommons.org/licenses/by/2.0/'],
['assumed AP photo rights cleared',a=>a.images[2].rights_review_complete=true],
['premature local caching',a=>a.third_party_caches=1],
['premature WP write',a=>a.wordpress_writes=1],
['premature WP image publishing flag',a=>a.images[0].wordpress_write_allowed=true],
['false binary identity proof',a=>a.images[3].same_binary_verified=true],
['mixing page inventory with post cohort',a=>a.article_cohort_excluded=false],
['incorrectly claiming requested width measures wire bytes',a=>a.requested_width_is_transfer_bytes=true],
['duplicate photo slot',a=>a.images[3].slot='1484:2'],
['false current HTML dimensions',a=>a.images[2].height=609],
['mislabelled Commons as first party',a=>a.images[1].source_class='first_party']
];
for(const [name,mutate] of cases){
 test('reject: '+name,()=>{const a=clone();mutate(a);assert.ok(validate(a).length>0,name)});
}
