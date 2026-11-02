'use strict';
/** Native Node regression suite for #154/#183 source-count reconciliation. */
const assert=require('node:assert/strict');
const {validateCrosswalk,offsiteByStoredUrl,loadRepo}
  =require('./validate_qa154_183_origin_crosswalk_20261102.cjs');
const original=loadRepo();
const clone=x=>JSON.parse(JSON.stringify(x));
let checks=0;
function ok(name, mutator) {
  const l=clone(original.ledger), p=clone(original.parts);
  mutator(l,p);
  const result=validateCrosswalk(l,p);
  assert.equal(result.ok,false,'unsafe change accepted: '+name);
  assert.ok(result.errors.length>0,name+': missing failure reason');
  checks++;
}
const baseline=validateCrosswalk(original.ledger,original.parts);
assert.equal(baseline.ok,true,baseline.errors.join(', '));checks++;
assert.deepEqual(baseline.metrics,original.ledger.summary);checks++;
assert.equal(offsiteByStoredUrl('https://i0.wp.com/finalvestige.com/a.jpg?ssl=1'),false);checks++;
assert.equal(offsiteByStoredUrl('https://i0.wp.com/text-message.blogs.archives.gov/a.jpg?ssl=1'),true);checks++;
assert.equal(offsiteByStoredUrl('https://i0.wp.com/www.squawkpoint.com/a.jpg?ssl=1'),true);checks++;
assert.equal(offsiteByStoredUrl('bad://url'),null);checks++;
ok('inflate Site QA offsite',l=>l.rows.find(x=>x.post_id===291).offsite_count_site_qa++);
ok('invent Site QA slot',l=>l.rows.find(x=>x.post_id===285).stored_img_src_count_site_qa++);
ok('invent visitor HTTP',l=>l.discrepancies[0].candidate_slots[0].visitor_browser_status=200);
ok('approve caching without rights',l=>l.discrepancies[0].candidate_slots[0].rights_to_cache_confirmed=true);
ok('authorize silent replacement',l=>l.discrepancies[0].candidate_slots[0].automatic_replacement_authorized=true);
ok('swap source URL',l=>l.discrepancies[0].candidate_slots[0].source_url='https://example.com/a.jpg');
ok('swap historical ALT',l=>l.discrepancies[0].candidate_slots[0].stored_alt='Different historical event');
ok('swap image key',l=>l.discrepancies[0].candidate_slots[0].image_key='291:1');
ok('rewrite aggregate',l=>l.summary.offsite_media_recovery=0);
ok('drop post',l=>l.rows.pop());
ok('duplicate post',l=>l.rows[1]=l.rows[0]);
ok('change source slot origin',(l,p)=>p[1].images.find(x=>x.key==='291:0').source_url='https://finalvestige.com/cover.jpg');
ok('invent census 404',(l,p)=>p[2].images.find(x=>x.key==='285:1').actual_http_status=404);
ok('mislabel origin',(l,p)=>p[1].images.find(x=>x.key==='291:0').source_kind='first_party');
ok('authorize WordPress write',l=>l.decision.wordpress_write_authorized=true);
ok('claim 42 confirmed failures',l=>l.decision.prior_42_broken_images_confirmed=true);
ok('claim 76 percent measured',l=>l.decision.claimed_76pct_image_weight_reduction_measured=true);
ok('tamper Site QA CSV SHA',l=>l.sources.site_qa_aggregate_csv_blob_sha='0'.repeat(40));
console.log('MEDIA_SOURCE_COUNT_CROSSWALK: '+checks+'/'+checks+' PASS; 61 posts, 355 images, 286 vs 288 offsite; 2 localized discrepancies; 0 browser claims');
