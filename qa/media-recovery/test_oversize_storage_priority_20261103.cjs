'use strict';
// Run: node qa/media-recovery/test_oversize_storage_priority_20261103.cjs
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {verify}=require('./validate_oversize_storage_priority_20261103.cjs');
const load=p=>JSON.parse(fs.readFileSync(path.join(__dirname,p),'utf8'));
const base=load('oversize_storage_priority_20261103.json'),source=load('oversize_originals_20261030.json'),summary=load('summary_20261030.json'),parts=Array.from({length:8},(_,i)=>load('parts/'+String(i+1).padStart(2,'0')+'.json'));
const copy=x=>JSON.parse(JSON.stringify(x));let assertions=0;
function check(data,accepted,name){const result=verify(data,source,parts,summary);assert.equal(result.ok,accepted,name+': '+result.errors.join('; '));assertions++;}
check(base,true,'exact corpus passes');
const mutations=[
 ['invent browser 200',x=>x.rows[0].exact_original_http_status=200],
 ['invent decode success',x=>x.rows[0].guest_image_decode_success=true],
 ['invent transfer 200K',x=>x.rows[0].guest_transferred_bytes=200000],
 ['invent currentSrc',x=>x.rows[0].current_runtime_currentSrc='https://example.com/a.jpg'],
 ['pretend rights approved',x=>x.rows[0].cache_permission_verified=true],
 ['authorize WP write',x=>x.rows[0].wordpress_write_authorized=true],
 ['pretend download',x=>x.rows[0].original_binary_downloaded=true],
 ['falsify original bytes',x=>x.rows[0].original_bytes=50],
 ['falsify 960 geometry',x=>x.rows[0].conditional_max_width_px=1024],
 ['falsify proportional height',x=>x.rows[0].conditional_height_px=900],
 ['misclassify unlinked',x=>x.rows[0].is_referenced_in_61_post_snapshot=true],
 ['invent inline slot',x=>x.rows[0].exact_oct30_inline_slots=['621:0']],
 ['change original URL',x=>x.rows[0].original_url='https://evil.invalid/foo.jpg'],
 ['claim 76 percent success',x=>x.metrics.validated_weight_reduction_pct=76],
 ['invent 76 verified',x=>x.metrics.reported_76_percent_reduction_verified=true],
 ['invent 42 verified',x=>x.metrics.reported_42_browser_broken_verified=true],
 ['invent before bytes',x=>x.metrics.site_cold_image_transfer_baseline_bytes=64900772],
 ['invent after bytes',x=>x.metrics.site_cold_image_transfer_after_bytes=15576185],
 ['alter storage share',x=>x.metrics.oversized_share_original_media_pct=76],
 ['change linked total',x=>x.metrics.oversized_with_exact_inline_source_original_bytes=0],
 ['duplicate media ID',x=>x.rows[1].media_id=x.rows[0].media_id],
 ['drop a row',x=>x.rows.pop()],
 ['change candidate URL',x=>x.rows[1].existing_wp_1024_variant_url='https://evil.invalid'],
 ['change source dimensions',x=>x.rows[1].original_width_px=300]
];
for(const [name,change] of mutations){const x=copy(base);change(x);check(x,false,name);}
assert.equal(base.metrics.oversized_original_bytes,43522829);assertions++;
assert.equal(base.metrics.oversized_with_exact_inline_source_original_bytes,23619602);assertions++;
assert.equal(base.metrics.oversized_without_exact_inline_source_original_bytes,19903227);assertions++;
assert.equal(base.metrics.oversized_share_original_media_pct,67.06);assertions++;
console.log('PASS '+assertions+'/'+assertions+' assertions; offline source/rights/960px/claims fail-closed');
