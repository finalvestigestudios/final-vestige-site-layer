'use strict';
const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const {validate}=require('./validate_hebgen_407_20261107.cjs');
const base=JSON.parse(fs.readFileSync(path.join(__dirname,'hebgen_407_usgs_evidence_20261107.json')));
const clone=()=>structuredClone(base);
test('authentic source audit passes',()=>assert.deepEqual(validate(base),[]));
const cases=[
 ['invented verified browser 404',d=>d.images[1].viewer.guest_browser_http_status=404],
 ['invented healthy browser decode',d=>d.images[1].viewer.guest_decode_ok=true],
 ['invented visitor bytes',d=>d.images[0].viewer.wire_bytes=500],
 ['claim 42 confirmed',d=>d.status_summary.claimed_42_broken_verified=true],
 ['claim 76 percent achieved',d=>d.status_summary.claim_76_percent_measured=true],
 ['invented wire savings',d=>d.performance.measured_savings_pct=76],
 ['stored library bytes misused for wire',d=>d.performance.visitor_image_transfer_bytes=43522829],
 ['rehost without permission',d=>d.images[1].allowed_to_download_or_cache=true],
 ['false clearance',d=>d.images[2].rights_gate='APPROVED'],
 ['release to WordPress',d=>d.restrictions.no_wordpress_writes=false],
 ['downloads enabled',d=>d.restrictions.no_media_downloads_or_cache=false],
 ['unsafe width',d=>d.restrictions.max_preview_width_px=1280],
 ['upscaling allowed',d=>d.restrictions.no_upscale=false],
 ['fabricated native dimensions',d=>d.images[0].native_source_geometry_px=[1000,600]],
 ['fake approved derivative',d=>d.images[0].approved_960px_derivative_px=[960,540]],
 ['wrong provenance USGS',d=>d.images[1].primary_record_url='https://example.com/missing'],
 ['wrong source host',d=>d.images[2].source_url='https://example.net/bad.jpg'],
 ['unverified original status claim',d=>d.images[1].viewer.origin_http_status=400],
 ['wrapper error confused with origin',d=>d.images[1].viewer.retriever_wrapper_error_code=404],
 ['duplicate slot',d=>d.images[7].slot='407:1'],
 ['duplicate URL',d=>d.images[7].source_url=d.images[6].source_url],
 ['lost Hall credit',d=>d.images[2].catalog_rights_note='catalog_public_domain; unknown'],
 ['lost Nile credit',d=>d.images[3].catalog_rights_note='catalog_public_domain; unknown'],
 ['false 1959 geyser dating',d=>d.images[6].note='Seismic geyser in 1959'],
 ['false 1959 modern photograph',d=>d.images[7].note='1959 snapshot'],
 ['unsafe stored aspect math',d=>d.images[2].provisional_resize_from_stored_geometry_px=[960,540]],
 ['fabricate geometry absent from inventory',d=>d.images[1].provisional_resize_from_stored_geometry_px=[960,540]],
 ['invented 8 rendered images',d=>d.status_summary.viewer_rendered_eventually=8]
];
for(const [name,mutate] of cases)test('rejects '+name,()=>{const d=clone();mutate(d);assert.ok(validate(d).length>0,name)});
