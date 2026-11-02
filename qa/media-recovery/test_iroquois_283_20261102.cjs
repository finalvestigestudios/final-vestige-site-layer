'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {validate}=require('./validate_iroquois_283_20261102.cjs');
const original=require('./iroquois_283_media_visual_integrity_20261102.json');
const fresh=()=>JSON.parse(JSON.stringify(original));
test('seven source URLs and all rights hold, historical caption error documented',()=>assert.deepEqual(validate(original),[]));
const cases=[
 ['false browser status',x=>x.records[0].independent_viewer_observation.logged_out_browser_status=200],
 ['false image 404',x=>x.records[3].independent_viewer_observation.origin_http_status=404],
 ['false renderer 403',x=>x.records[3].independent_viewer_observation.status_code_reported_by_retriever=403],
 ['invented bytes',x=>x.records[4].independent_viewer_observation.transferred_bytes=900],
 ['fake decoded width',x=>x.records[4].independent_viewer_observation.decoded_width_px=1000],
 ['fabricated currentSrc',x=>x.records[2].independent_viewer_observation.chrome_current_src='https://x.example/a.jpg'],
 ['misreported inaccessible source',x=>x.records[3].independent_viewer_observation.result='displayed_web_image_viewer'],
 ['invalid image source',x=>x.records[0].published_url='https://fake.invalid/doors.jpg'],
 ['fabricated ALT rewrite',x=>x.records[0].published_alt='A composite explaining fire doors'],
 ['wrong source census hash',x=>x.source_inventory_blob_sha='f'.repeat(40)],
 ['changed archive ID',x=>x.records[6].candidate.catalog_id='ICHi-36010'],
 ['miscredited Clark',x=>x.records[6].candidate.creator_credit='Public domain anonymous'],
 ['LOC same scene claim',x=>x.records[5].candidate.relation='exact_same_image'],
 ['image diagram called photo again',x=>x.records[0].visual_editorial_finding.finding='no_proven_factual_alt_mismatch'],
 ['unreviewed ALT approved',x=>x.records[0].visual_editorial_finding.editorial_change_authorized=true],
 ['editorial proposal missing',x=>x.records[0].visual_editorial_finding.suggested_alt_subject_to_editor_review=null],
 ['false image viewed',x=>x.records[3].visual_editorial_finding.visual_verified_in_independent_viewer=true],
 ['false image broken total',x=>x.confirmed_browser_broken_count=42],
 ['false percent savings',x=>x.claimed_76_percent_savings_measured=true],
 ['false production repair',x=>x.production_image_repairs=1],
 ['premature rights approval',x=>x.records[0].rights.copyright_clearance='APPROVED'],
 ['publisher means reuse',x=>x.records[4].rights.existing_publisher_display_not_republication_license=false],
 ['unauthorized archive fetch',x=>x.records[5].rights.download_authorized=true],
 ['unauthorized WordPress rehost',x=>x.records[6].rights.wordpress_upload_authorized=true],
 ['unverified source master pixels',x=>x.records[0].optimization.current_original_dimensions_verified=true],
 ['guessed target height',x=>x.records[0].optimization.target_height_px=500],
 ['unjustified upscaling',x=>x.records[0].optimization.allow_upscale=true],
 ['too wide target',x=>x.records[0].optimization.maximum_width_px=1280],
 ['fake source image sha',x=>x.records[0].optimization.source_image_sha256='f'.repeat(64)],
 ['stage despite hold',x=>x.records[0].staging.wordpress_write_approved=true],
 ['rights approval despite hold',x=>x.records[5].staging.rights_approved=true],
 ['binary asserted identical',x=>x.records[2].staging.candidate_pixel_identical=true],
 ['faked screenshot review',x=>x.records[0].staging.identity_and_crop_review_passed=true],
 ['dropped source record',x=>x.records.pop()],
 ['reordered source record',x=>x.records.reverse()],
 ['incorrect image view count',x=>x.image_viewer_displayed_count=7]
];
cases.forEach(([title,mutate])=>test('reject '+title,()=>{const x=fresh();mutate(x);assert.ok(validate(x).length>0,title)}));
