'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {validate}=require('./validate_tmi_285_fig4_upstream_20261103.cjs');
const data=require('./tmi_285_fig4_upstream_20261103.json');
const copy=()=>structuredClone(data);
test('frozen source, release gates and official provenance pass',()=>assert.deepEqual(validate(copy()),[]));
const mutations=[
['invent origin status',x=>x.investigated_slots[0].retriever.numeric_origin_http_status=500],
['invent browser 404',x=>x.investigated_slots[1].guest_browser.http_status=404],
['invent browser decode',x=>x.investigated_slots[0].guest_browser.decoded=true],
['invent visitor breakage',x=>x.investigated_slots[1].guest_browser.broken=true],
['invent transfer bytes',x=>x.investigated_slots[1].guest_browser.encoded_transfer_bytes=1024],
['claim 42 proven',x=>x.sitewide_baseline.reported_broken_42_visitor_confirmed=true],
['claim 76 percent',x=>x.sitewide_baseline.claimed_76_percent_wire_saving_verified=true],
['swap live WordPress src',x=>x.investigated_slots[0].published_src='https://example.org/image.jpg'],
['wrong redirect target',x=>x.investigated_slots[0].retriever.final_declared_url='https://example.org'],
['pretend 500 is origin 500',x=>x.investigated_slots[0].retriever.result='origin_http_500'],
['lose displayed exact source',x=>x.investigated_slots[0].image_search.result='not_displayed'],
['erase historical maintenance tags',x=>x.investigated_slots[0].editorial_issue='regular control'],
['erase attribution',x=>x.candidates[0].creator_credit=''],
['invent pixel match',x=>x.candidates[0].pixel_crop_sha_match=true],
['pretend rights approved',x=>x.candidates[0].rights_item_verified_for_rehosting=true],
['authorize WP upload',x=>x.candidates[0].wp_upload_authorized=true],
['authorize live edit',x=>x.release.production_changes_made=true],
['claim live repair',x=>x.release.repairs_confirmed=1],
['upscale 604 image',x=>x.candidates[0].proposed_width=960],
['upscale 819 image',x=>x.candidates[1].proposed_width=960],
['stretch candidate',x=>x.candidates[0].proposed_height=400],
['forge 285:5 pixel geometry',x=>x.candidates[1].intrinsic_width=1220],
['wrong retouched identity',x=>x.candidates[0].candidate_type='exact_binary'],
['wrong 2010 publisher identity',x=>x.candidates[1].candidate_type='exact_binary'],
['claim CDC same exact photo',x=>x.optional_nonidentical_backup.source_binary_identity_verified=true],
['approve CDC alternate',x=>x.optional_nonidentical_backup.editorial_approved=true],
['remove browser acceptance',x=>x.release.requires_logged_out_browser_decode=false],
['turn off hold',x=>x.release.all_caching_and_publication_on_hold=false],
['corrupt source freeze SHA',x=>x.source_snapshot.source_git_blob='0'.repeat(40)],
['wrong source modified',x=>x.source_snapshot.modified='2026-11-03T00:00:00'],
['duplicate slot',x=>x.investigated_slots[1].key='285:2'],
['drop catalog',x=>x.candidates.pop()]
];
for(const [name,change] of mutations)test('fail-closed: '+name,()=>{const d=copy();change(d);assert.ok(validate(d).length>0,name);});
