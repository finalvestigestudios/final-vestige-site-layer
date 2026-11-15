'use strict';
const {test}=require('node:test');const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_herculaneum_252_20261114.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'herculaneum_252_six_visual_identity_20261114.json'),'utf8'));
const clone=()=>structuredClone(original);
test('committed six-image audit is safe',()=>assert.deepEqual(validate(clone()),[]));
const mutations=[
['invented 404',d=>d.items[0].browser_status=404],
['invented natural pixels',d=>d.items[1].visitor_natural_width=100],
['invented bytes',d=>d.items[2].visitor_transfer_bytes=123],
['invented binary digest',d=>d.items[3].source_binary_sha256='ab'],
['fake 42 broken',d=>d.claimed_42_broken_in_visitor_browser=42],
['fake 76 savings',d=>d.claimed_76_percent_network_savings=76],
['production writes',d=>d.production_changes=1],
['unsafe rehost rights',d=>d.items[0].rights_cleared_for_rehost=true],
['unsafe upload',d=>d.items[0].wp_media_upload_authorized=true],
['fabricated replacement binary',d=>d.items[0].replacement_binary_created=true],
['source URL swapped',d=>d.items[0].source_url='https://commons.wikimedia.org/wiki/Special:Redirect/file/other.jpg'],
['relative source',d=>d.items[0].source_url='/bad'],
['misbound slot',d=>d.items[2].key='252:6'],
['upscale small file 2',d=>d.items[2].max_width_960_preserve_aspect_px.width=960],
['upscale small file 4',d=>d.items[4].max_width_960_preserve_aspect_px.width=960],
['bad aspect',d=>d.items[0].max_width_960_preserve_aspect_px.height=11],
['bad catalog URL',d=>d.items[1].catalog_url='https://example.org/a'],
['wrong source filename',d=>d.items[3].catalog_filename='British.jpg'],
['mismatch silently cleared',d=>d.items[1].identity_disposition='accurate_subject'],
['wrong drawing classification',d=>d.items[4].identity_disposition='accurate_subject'],
['wrong handwritten classification',d=>d.items[5].identity_disposition='accurate_subject'],
['missing correction proposal',d=>d.items[5].proposed_alt_review_only=null],
['license removed',d=>d.items[0].catalog_rights_claim='PD'],
['false post ID',d=>d.post_id=215],
['stale source modification',d=>d.post_modified_wp_local='2026-10-29T18:00:00'],
['missing item',d=>d.items.pop()]
];
for(const [label,mutate]of mutations)test('rejects '+label,()=>{const d=clone();mutate(d);assert.ok(validate(d).length>0,label)});
