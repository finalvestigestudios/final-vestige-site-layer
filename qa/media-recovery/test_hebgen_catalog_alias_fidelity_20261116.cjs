'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_hebgen_catalog_alias_fidelity_20261116.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'hebgen_catalog_alias_fidelity_20261116.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(original));
test('immutable twin catalog aliases pass on hold, no fake browser status',()=>{
 const v=validate(clone());assert.equal(v.status,'HOLD_GUEST_PIXEL_RIGHTS');assert.equal(v.post_slot,'407:1');
 assert.equal(v.originals_differ,true);assert.equal(v.visitor_http_status,null);assert.equal(v.wordpress_writes,0);
});
const mutants=[
 ['false guest 404',d=>d.wordpress.guest_http_status=404],
 ['false guest 200',d=>d.wordpress.guest_http_status=200],
 ['false visitor image failure',d=>d.gates.visitor_failure_confirmed=true],
 ['false currentSrc',d=>d.wordpress.guest_current_src=d.wordpress.rendered_rest_view_url],
 ['false encoded bytes',d=>d.wordpress.guest_transfer_bytes=40000],
 ['invented native 1000px',d=>d.wordpress.guest_natural_width=1000],
 ['fake guest decode',d=>d.wordpress.guest_decoded=true],
 ['swap WP source URL',d=>d.wordpress.authored_image_url=d.official_catalogs[1].catalog_original_link_url],
 ['swap WP proxy URL',d=>d.wordpress.rendered_rest_view_url=d.official_catalogs[1].catalog_original_link_url],
 ['wrong linked catalog',d=>d.wordpress.authored_catalog_hyperlink=d.official_catalogs[1].catalog],
 ['claim linked original is sibling original',d=>d.official_catalogs[0].catalog_original_link_url=d.official_catalogs[1].catalog_original_link_url],
 ['wrong sibling catalog',d=>d.official_catalogs[1].catalog='https://example.com'],
 ['wrong sibling image path',d=>d.official_catalogs[1].catalog_original_link_url=d.wordpress.authored_image_url],
 ['invented origin HTTP 404',d=>d.official_catalogs[0].origin_http_status=404],
 ['invented transport HTTP 400',d=>d.observations[0].numeric_origin_status=400],
 ['wrong reader method',d=>d.observations[1].method='logged-out-chromium'],
 ['wrong reader result',d=>d.observations[0].reader_result='origin_http_404'],
 ['omit Jetpack route',d=>d.observations.pop()],
 ['pretend official source rights differ',d=>d.official_catalogs[1].rights_label='CC BY'],
 ['premature image hash claim',d=>d.integrity.same_pixel_hash_proven=true],
 ['premature visual frame parity',d=>d.integrity.same_crop_and_frame_visually_approved=true],
 ['unapproved rehost',d=>d.integrity.copyright_rehost_approved=true],
 ['copied source asset',d=>d.integrity.image_downloaded=true],
 ['fabricated dimensions',d=>d.derivative.output_width_px=960],
 ['allow upscaling',d=>d.derivative.no_upscale=false],
 ['unapproved WP media staging',d=>d.derivative.wordpress_media_staging_approved=true],
 ['unapproved cache mirroring',d=>d.derivative.cache_mirroring_approved=true],
 ['wrong historical count',d=>d.unchanged_baselines.frozen_images=361],
 ['42 confirmed failures invented',d=>d.unchanged_baselines.browser_confirmed_broken=42],
 ['76% transfer measured invented',d=>d.unchanged_baselines.visitor_bytes_savings_percent=76],
 ['stored original bytes changed',d=>d.unchanged_baselines.original_storage_bytes=0],
 ['WP write slipped in',d=>d.gates.word_press_write_count=1],
 ['live site changed',d=>d.gates.live_website_changed=true],
 ['duplicate QA ownership',d=>d.next_gate='Make a second independent browser collector']
];
for(const [name,mutate] of mutants){test('reject '+name,()=>{let c=clone();mutate(c);assert.throws(()=>validate(c),/^Error: HOLD:/)});}
