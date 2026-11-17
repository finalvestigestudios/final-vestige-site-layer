'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const audit=require('./apollo12_257_catalog_20261104.json');
const frozen=require('./parts/04.json');
const {validate}=require('./validate_apollo12_257_20261104.cjs');
const clone=()=>structuredClone(audit);
test('7 Apollo 12 original URLs, catalog metadata and rights HOLD reconcile with frozen source',()=>assert.deepEqual(validate(audit,frozen),[]));
const changes=[
 ['fabricated browser HTTP 200',d=>d.rows[0].final_browser_http_status=200],
 ['invented origin 403',d=>d.rows[0].retriever_origin_http_status=403],
 ['fake broken visitor image',d=>d.rows[0].visitor_broken_image_confirmed=true],
 ['unmeasured visitor byte count',d=>d.rows[0].final_browser_image_bytes=2000],
 ['invented currentSrc',d=>d.rows[0].final_browser_current_src='https://elsewhere.test/a.png'],
 ['unverified 76 percent reduction',d=>d.summary.claimed_76_percent_wire_reduction_measured=true],
 ['unverified 42 breaks',d=>d.summary.alleged_42_broken_visitor_verified=true],
 ['altered inventory SHA',d=>d.source_snapshot_blob_sha='fake'],
 ['changed source URL same host',d=>d.rows[1].published_source_url='https://commons.wikimedia.org/wiki/Special:Redirect/file/WRONG.jpg?width=1280'],
 ['changed exact ALT',d=>d.rows[2].published_alt='different scene'],
 ['swapped source slots',d=>[d.rows[0],d.rows[1]]=[d.rows[1],d.rows[0]]],
 ['removed seventh image',d=>d.rows.pop()],
 ['LRO file upscaled',d=>d.rows[6].conditional_staged_width_px=960],
 ['incorrect proportional height',d=>d.rows[5].conditional_staged_height_px=999],
 ['WordPress post edit allowed',d=>d.rows[2].wordpress_post_edit_authorized=true],
 ['cache without rights',d=>d.rows[4].cache_authorized=true],
 ['false licensing approval',d=>d.rows[4].rights_item_cleared=true],
 ['binary similarity assumed',d=>d.rows[1].same_published_image_binary_hash_verified=true],
 ['lookalike catalog host',d=>d.rows[0].commons_catalog_url='https://commons.wikimedia.org.evil.test/wiki/File:x'],
 ['unofficial primary',d=>d.rows[0].nasa_primary_subject_reference_url='https://example.com/'],
 ['nonpositive catalog byte claim',d=>d.rows[0].commons_catalog_original_bytes=0],
 ['fabricated HTML dimensions',d=>d.rows[0].published_html_width_px=960],
 ['technical GIF replaced',d=>d.rows[4].commons_catalog_url='https://commons.wikimedia.org/wiki/File:Panel.jpg'],
 ['unsupported transfer savings',d=>d.rows[6].performance_transfer_reduction_measured=true]
];
for(const [name,change] of changes)test('fail closed: '+name,()=>{const d=clone();change(d);assert.notDeepEqual(validate(d,frozen),[])});
