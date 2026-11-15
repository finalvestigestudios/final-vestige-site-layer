'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {verify}=require('./validate_official_original_route_20261115.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'official_original_route_pair_20261115.json'),'utf8'));
const copy=()=>structuredClone(original);
test('actual two-slot catalog ledger accepts only QA hold',()=>assert.deepEqual(verify(original),[]));
const cases=[
 ['fake guest 404',d=>{d.records[0].http_status_jetpack=404;}],
 ['fake transferred bytes',d=>{d.records[0].guest_transferred_bytes=98000;}],
 ['fake confirmed 42 broken',d=>{d.guest_browser_failed_images_verified=42;}],
 ['fabricated 76% savings',d=>{d.sitewide_visitor_weight_reduction_percent=76;}],
 ['rogue original host',d=>{d.records[0].candidate_official_original_url='https://example.org/image.jpg';}],
 ['Drupal token style proxy disguised as Original',d=>{d.records[0].candidate_official_original_url=d.records[0].editor_image_url;}],
 ['claim rehost rights approved',d=>{d.records[0].cache_or_rehost_rights_cleared=true;}],
 ['allow production upload',d=>{d.records[0].production_media_upload_authorized=true;}],
 ['wrong native dimensions',d=>{d.records[0].original_dimensions_px={width:960,height:800};}],
 ['invent exact hash',d=>{d.records[0].identical_pixel_hash_verified=true;}],
 ['Navy alternative promoted as identical',d=>{d.records[1].candidate_official_original_url='https://www.history.navy.mil/fake.jpg';}],
 ['copyright/source-unknown caveat removed',d=>{d.records[0].source_rights_statement='Public Domain';}],
 ['original link falsely relabeled',d=>{d.records[0].official_catalog_link_label='Thumbnail';}],
 ['post rewrite enabled',d=>{d.records[0].published_post_rewrite_authorized=true;}],
 ['spend changed',d=>{d.safety.subscription_spend_usd=1;}],
 ['token added to view url',d=>{d.records[0].wordpress_view_url+='&itok=ASMRCahz';}],
 ['remove key scene detail',d=>{d.records[0].scene_cues=['car beneath tsunami debris'];}]
];
for(const [name,modify] of cases) test('reject: '+name,()=>{const d=copy();modify(d);assert.ok(verify(d).length>0,name);});
