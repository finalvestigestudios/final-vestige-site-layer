'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_live_110_media_20261103.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'live_110_media_13_oversize_scotch418_20261103.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(original));
test('real 110-media WordPress evidence passes fail-closed audit gate',()=>assert.equal(validate(clone()).assets,110));
const bad=[
  ['invent 76% compression',a=>a.summary.claimed_76_percent_savings_verified=true],
  ['invent 42 confirmed failures',a=>a.summary.claimed_42_broken_verified=true],
  ['invent Chrome transfer',a=>a.summary.guest_transfer_bytes=43522829],
  ['pretend live repair',a=>a.summary.production_replacements=1],
  ['remove one media record',a=>a.media_library_index.pop()],
  ['duplicate media identifier',a=>a.media_library_index[1].id=a.media_library_index[0].id],
  ['duplicate source URL',a=>a.media_library_index[1].source_url=a.media_library_index[0].source_url],
  ['invent original media size',a=>a.media_library_index[0].original_bytes+=1],
  ['erase media pixel dimensions',a=>a.media_library_index[0].original_pixels=null],
  ['claim nonexistent responsive sizes',a=>a.oversized_items.find(x=>x.id===39).registered_size_keys.push('large')],
  ['lower sum without reconciling',a=>a.summary.oversized_original_storage_bytes-=1],
  ['upscale archival image',a=>a.oversized_items.find(x=>x.id===388).conditional_no_upscale_px[0]=1440],
  ['wrong aspect ratio',a=>a.oversized_items.find(x=>x.id===388).conditional_no_upscale_px[1]+=2],
  ['fabricate guest HTTP status',a=>a.oversized_items.find(x=>x.id===388).guest_http_status=200],
  ['fabricate guest currentSrc',a=>a.oversized_items.find(x=>x.id===388).guest_current_src='https://example.test/'],
  ['fabricate download bytes',a=>a.oversized_items.find(x=>x.id===388).guest_transfer_bytes=1000],
  ['rights bypass',a=>a.oversized_items.find(x=>x.id===388).upstream_rights_clearance='CLEARED'],
  ['WordPress write bypass',a=>a.oversized_items.find(x=>x.id===39).wordpress_write_approved=true],
  ['alter photo identity',a=>a.scotch_cap_p0_recheck.priority_sources[1].published_src='https://other.example/'],
  ['invent browser 403',a=>a.scotch_cap_p0_recheck.priority_sources[1].guest_http_status=403],
  ['relabel retriever 403 as origin',a=>a.scotch_cap_p0_recheck.priority_sources[1].web_open_403_is_origin_http=true],
  ['automatic image replacement',a=>a.scotch_cap_p0_recheck.priority_sources[2].replacement_approved=true],
  ['hide item rights hold',a=>a.scotch_cap_p0_recheck.priority_sources[2].rights_decision=''],
  ['invent 76% measured',a=>a.guest_wire_method.measured_savings_percent=76],
  ['enable unlicensed rehost',a=>a.safety.unlicensed_asset_rehosting=true],
  ['claim a source download',a=>a.safety.third_party_binaries_downloaded=true],
  ['change threshold',a=>a.summary.oversize_threshold_bytes_strictly_greater_than=1500000],
];
for(const [name,mutate] of bad)test('reject: '+name,()=>{const x=clone();mutate(x);assert.throws(()=>validate(x))});
