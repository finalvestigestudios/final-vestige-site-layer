'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validateHebgenSecondary}=require('./validate_hebgen_407_secondary_20261103.cjs');
const a=JSON.parse(fs.readFileSync(path.join(__dirname,'hebgen_407_secondary_same_photo_20261103.json'),'utf8'));
const part=JSON.parse(fs.readFileSync(path.join(__dirname,'parts/02.json'),'utf8'));
const changes=[
 ['fabricated 404',x=>x.source_observation.guest_http_status=404],
 ['wrapper promoted to HTTP',x=>x.source_observation.origin_http_status=400],
 ['false browser decoded',x=>x.source_observation.guest_image_decodes=true],
 ['fake transfer bytes',x=>x.source_observation.wire_bytes=1500],
 ['faked visitor currentSrc',x=>x.source_observation.visitor_current_src=x.official_usgs.original_link_url],
 ['declared broken without browser',x=>x.source_observation.visitor_broken_confirmed=true],
 ['published source rewritten',x=>x.source_url=x.official_usgs.original_link_url],
 ['published alt revised',x=>x.source_alt='random'],
 ['USGS original substituted with medium',x=>x.official_usgs.original_link_url=x.official_usgs.medium_url],
 ['USGS official full-width substituted',x=>x.official_usgs.page_display_url='https://example.com/image.jpg'],
 ['false official dimensions',x=>x.official_usgs.original_intrinsic_dimensions_binary_verified=true],
 ['imaginary 960 crop',x=>x.official_usgs.proposed_960_derivative={width:960,height:960}],
 ['Commons larger than real',x=>x.verified_secondary_archive.catalog_dimensions_px.width=960],
 ['Commons filesize invented',x=>x.verified_secondary_archive.catalog_original_file_bytes=10000],
 ['Commons altered host',x=>x.verified_secondary_archive.original_file_url='https://example.org/a.jpg'],
 ['Commons falsely binary identical',x=>x.verified_secondary_archive.binary_identical_to_usgs=true],
 ['visual crop equivalence asserted',x=>x.verified_secondary_archive.relationship_to_usgs='BITWISE_IDENTICAL'],
 ['upscaled fallback',x=>x.verified_secondary_archive.conditional_no_upscale_derivative_px.width=960],
 ['rights silently cleared',x=>x.publication_safeguards.rights_item_review='APPROVED'],
 ['localization enabled',x=>x.publication_safeguards.first_party_localization_approved=true],
 ['WordPress writes',x=>x.publication_safeguards.wordpress_upload_approved=true],
 ['production repair invented',x=>x.publication_safeguards.production_repairs=1],
 ['false sitewide reduction',x=>x.totals_context.reported_76_percent_reduction_measured=true],
 ['invalid source pin',x=>x.frozen_source_part_git_blob_sha='deadbeef'],
 ['census alt drift',x=>x.source_alt='changed'],
 ['fake 42 failures',x=>x.totals_context.reported_42_broken_browser_verified=true],
 ['remove browser QA requirement',x=>x.visitor_verification.confirmed_404=true],
];
assert.equal(validateHebgenSecondary(a,part).ok,true,'positive exact source archive audit');
let i=1;for(const [name,fn] of changes){const x=structuredClone(a);fn(x);
 assert.equal(validateHebgenSecondary(x,part).ok,false,name);i++}
console.log(i+'/'+i+' USGS/Commons secondary-route release-gate checks PASS');
