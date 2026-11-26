'use strict';
const assert=require('node:assert/strict');
const {validate}=require('./validate_hebgen407_usgs_eight.cjs');
const source=require('./hebgen407_usgs_eight_custody_20261116_1830pt.json');
let passed=0;
function caseRun(label,fn){fn();passed++;}
const clone=()=>JSON.parse(JSON.stringify(source));
caseRun('baseline 8 catalog records',()=>assert.equal(validate(clone()).validated_slots,8));
const mutations=[
 ['schema',m=>m.schema='bogus'],
 ['post id',m=>m.wp_post_id=408],
 ['revision drift',m=>m.wp_modified='2026-11-16'],
 ['browser capture invented',m=>m.guest_browser_captures=1],
 ['tool status as HTTP',m=>m.direct_media_probe_numerical_http_status=400],
 ['census inflated',m=>m.history.inline_images=356],
 ['42 verified claim',m=>m.history.guest_verified_broken_images=42],
 ['76 percent falsely measured',m=>m.history.measured_wire_reduction_percent=76],
 ['storage bytes overwritten',m=>m.history.oversized_stored_bytes=0],
 ['write enable',m=>m.wordpress_changes=1],
 ['mirror permit',m=>m.licensed_asset_mirrors=1],
 ['missing image',m=>m.rows.pop()],
 ['duplicate slot',m=>m.rows[7].key='407:0'],
 ['wrong authored',m=>m.rows[0].authored_source_url='https://evil.example/p.jpg'],
 ['wrong runtime',m=>m.rows[0].published_jetpack_url='https://evil.example/a.jpg'],
 ['unrelated alt',m=>m.rows[1].alt_text=''],
 ['nonUSGS catalog',m=>m.rows[1].usgs_item_url='https://example.com'],
 ['rights override',m=>m.rows[2].rights_review='APPROVED'],
 ['credit suppressed',m=>m.rows[3].usgs_catalog_credit='x'],
 ['invented canonical',m=>m.rows[1].usgs_original_link_url=m.rows[1].authored_source_url],
 ['wrong route label',m=>m.rows[0].canonical_path_relationship='CANONICAL_PATH_DIFFERS'],
 ['forged displayed direct',m=>m.rows[1].original_retriever_observation='DISPLAYED_DIRECT'],
 ['browser HTTP invented',m=>m.rows[1].browser_http_status=404],
 ['browser src invented',m=>m.rows[1].browser_current_src='https://example.com'],
 ['wire fabricated',m=>m.rows[2].browser_wire_bytes=100000],
 ['decode fabricated',m=>m.rows[2].browser_decode_success=true],
 ['claim failed visitor',m=>m.rows[1].broken_for_visitors_confirmed=true],
 ['rehost approval',m=>m.rows[1].rehosting_approved=true],
 ['WordPress approval',m=>m.rows[1].wordpress_write_approved=true],
 ['premature exact-frame match',m=>m.rows[1].same_frame_hash_verified=true],
 ['native pixels invented',m=>m.rows[1].native_pixel_dimensions_verified=true],
 ['markup width invented',m=>m.rows[1].authored_dimensions_px=[960,600]],
 ['markup resized incorrectly',m=>m.rows[2].conditional_960px_ratio_from_markup=[960,100]],
 ['layout size removed',m=>m.rows[3].published_width_height_explicit=false],
 ['fake responsive variants',m=>m.rows[3].published_srcset_present=true],
 ['misstate fetched origin',m=>m.rows[3].official_original_retriever_observation='HTTP_200'],
 ['mime invented',m=>m.rows[7].browser_mime_type='image/jpeg']
];
for(const [label,mutate] of mutations){
 caseRun(label,()=>{const m=clone();mutate(m);assert.throws(()=>validate(m),Error);});
}
console.log('PASS '+passed+'/'+(mutations.length+1)+' Hebgen canonical-source fail-closed checks');
