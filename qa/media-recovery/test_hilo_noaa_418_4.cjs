'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const original=require('./hilo_noaa_theb2705_418_4_20261101.json');
const {validate}=require('./validate_hilo_noaa_418_4.cjs');
const copy=()=>structuredClone(original);
test('true frozen NOAA archival lead is valid but does not authorize publication',()=>{assert.deepEqual(validate(copy()),[]);assert.equal(original.record.rights.cache_or_republication_review,'HOLD')});
const changes=[
 ['changed source photo',d=>d.record.stored_url='https://example.com/another.jpg'],
 ['changed alt/historical scene',d=>d.record.stored_alt='Bridge replacement in 1987'],
 ['replaced NOAA accession',d=>d.record.primary_candidate.catalog_id='theb2706'],
 ['changed official NOAA catalog',d=>d.record.primary_candidate.catalog_url='https://www.noaa.gov/another.jpg'],
 ['pretended exact hash verification',d=>d.record.primary_candidate.published_original_exact_binary_match_verified=true],
 ['invented source master dimensions',d=>d.record.primary_candidate.source_master_dimensions_px=[960,540]],
 ['visitor 200 fabricated',d=>d.record.visitor.http_status=200],
 ['visitor broken 404 fabricated',d=>d.record.visitor.verified_broken=true],
 ['retriever 405 mislabelled origin HTTP',d=>d.record.retrieval_observations[2].origin_http_status=405],
 ['promoted license without item verification',d=>d.record.rights.cache_or_republication_review='APPROVED'],
 ['approved WordPress upload',d=>d.record.rights.wp_media_upload_authorized=true],
 ['silently authorized post rewrite',d=>d.record.rights.wordpress_post_rewrite_authorized=true],
 ['upscaled to 1280',d=>d.record.dimensions.max_width_px=1280],
 ['invented 960 derivative',d=>d.record.dimensions.proposed_width_px=960],
 ['falsely claimed 42 broken verified',d=>d.baseline.reported_broken_42_verified=true],
 ['falsely claimed 76 percent reduction',d=>d.baseline.claimed_transfer_savings_76_percent_measured=true],
 ['incorrectly asserted fully verified P0 photos',d=>d.baseline.now_p0_candidates_with_contextual_primary_lead=37],
 ['identified person usage gate silently cleared',d=>d.record.rights.photo_of_identifiable_person=false]
];
for(const [name,mutate]of changes)test('reject '+name,()=>{let d=copy();mutate(d);assert.ok(validate(d).length>0)});
