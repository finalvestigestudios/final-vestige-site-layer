'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {audit}=require('./validate_thresher_220_navy_20261105.cjs');
const data=require('./thresher_220_navy_catalog_20261105.json');
const copy=()=>JSON.parse(JSON.stringify(data));
const clone=x=>JSON.parse(JSON.stringify(x));
test('seven live WordPress images, six primary Navy catalogs; no publication',()=>assert.deepEqual(audit(data).errors,[]));
const cases=[
 ["invented 42 failures", v=>v.actual_broken_image_count=42],
 ["invented 76% savings", v=>v.sitewide_wire_reduction_percent=76],
 ["claim site wide measured", v=>v.inventory_context.claimed_76_percent_wire_savings="VERIFIED"],
 ["seven not six official", v=>v.official_exact_subject_catalogs=7],
 ["wrong post", v=>v.source_post.id=221],
 ["missing row", v=>v.records.pop()],
 ["duplicated row", v=>v.records[6]=clone(v.records[5])],
 ["changed image", v=>v.records[3].current_published_source_url="https://example.com/fake.jpg"],
 ["deceptive Commons source", v=>v.records[3].current_published_source_url="https://commons.wikimedia.org.evil.test/wiki/Special:Redirect/file/USS_Thresher_(SSN-593)_watertight_door.jpg"],
 ["faked catalog", v=>v.records[0].official_navy_catalog_id="NH 00000"],
 ["invented Trieste primary", v=>v.records[4].same_subject_primary_catalog_caption_verified=true],
 ["wrong Trieste archival URL", v=>v.records[4].official_navy_catalog_url="https://example.com"],
 ["wrong published alt", v=>v.records[0].current_published_alt=""],
 ["wrong dimensions", v=>v.records[2].commons_original_pixels.width=960],
 ["upscaled Skylark", v=>v.records[2].proposed_derivative_pixels.width=960],
 ["crop drift", v=>v.records[0].proposed_derivative_pixels.height=1000],
 ["fake browser 200", v=>v.records[0].guest_browser.http_status=200],
 ["fake browser 404", v=>v.records[0].guest_browser.verified_broken=true],
 ["fake browser decoded", v=>v.records[0].guest_browser.decoded_natural_width=320],
 ["fake Chrome bytes", v=>v.records[0].guest_browser.cdp_transfer_bytes=12000],
 ["rights pre-cleared", v=>v.records[2].rights.item_specific_review="APPROVED"],
 ["permission invented", v=>v.records[4].rights.localization_permission_granted_by_this_audit=true],
 ["binary downloaded", v=>v.records[0].release.binary_downloaded=true],
 ["WordPress upload", v=>v.records[0].release.wp_media_upload=true],
 ["WordPress block rewrite", v=>v.records[0].release.wp_post_edit=true],
 ["public publish", v=>v.records[0].release.public_publish=true],
 ["source filename drift", v=>v.records[1].commons_filename="another.jpg"],
 ["wrong source slot", v=>v.records[2].image_key="220:1"],
 ["wrong source provenance", v=>v.records[4].commons_file_page="https://example.org/"],
 ["archive chronology stripped", v=>v.records[6].photographic_chronology_note=""],
];
for(const [name,change] of cases)test('reject '+name,()=>{const d=copy();change(d);assert.equal(audit(d).ok,false,name)});
