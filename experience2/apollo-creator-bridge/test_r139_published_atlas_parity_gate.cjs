'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {auditPublishedAtlas,EXPECTED_URL}=require('./r139_published_atlas_parity_gate.cjs');
const a=(href,label='Read')=>'<a href="'+href+'">'+label+'</a>';
const sample=()=>({id:2017,status:'publish',slug:'apollo-1-evidence-atlas',link:EXPECTED_URL,
 modified:'2026-11-04T17:09:24',content:'<main>'+
 Array.from({length:6},(_,i)=>'<section id="record-0'+(i+1)+'">Record '+(i+1)+'</section>').join('')+
 a('https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/')+
 Array.from({length:6},(_,i)=>a('https://www.nasa.gov/image-detail/source-0'+(i+1)+'/')).join('')+
 a('#record-02')+'<img src="https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/11/apollo1-nasa-photo.jpg" alt="Historic photograph" width="300" height="200">'+'</main>'});
test('published WP metadata does not establish independent browser acceptance',()=>{
 const r=auditPublishedAtlas(sample(),{independentlyReviewedLandingUrl:EXPECTED_URL});
 assert.equal(r.page.link,EXPECTED_URL);assert.equal(r.browser,'NOT_TESTED');
 assert.equal(r.release,'STAGING_HOLD');assert.equal(r.approved_to_publish,false);
 assert.equal(r.findings.record_count,6);
});
test('published Atlas with no worksheet CTA is flagged, not silently promoted',()=>{
 const r=auditPublishedAtlas(sample(),{independentlyReviewedLandingUrl:EXPECTED_URL});
 assert.ok(r.blockers.includes('NO_MATCHING_FREE_CLASSROOM_WORKSHEET_PATH'));
 assert.equal(r.findings.free_worksheet_route_present,false);
});
test('media evidence cannot self-certify NASA commercial rights',()=>{
 const p=sample();let r=auditPublishedAtlas(p);
 assert.equal(r.findings.nasa_branded_image_references,1);
 assert.ok(r.blockers.includes('NASA_MEDIA_IN_LIVE_HTML_WITHOUT_SUPPLIED_INDIVIDUAL_REUSE_RECEIPTS'));
 r=auditPublishedAtlas(p,{photoSpecificReuseReviewed:true});
 assert.ok(r.blockers.includes('PHOTO_RIGHTS_CLAIM_REQUIRES_INDEPENDENT_MANIFEST_AND_REVIEW'));
});
test('missing and duplicate chronology record anchors are detected',()=>{
 const p=sample();p.content=p.content.replace('id="record-06"','id="record-05"');
 assert.ok(auditPublishedAtlas(p).blockers.includes('SIX_ATLAS_RECORDS_NOT_VERIFIED_IN_SOURCE'));
});
test('a wrong live URL fails instead of defaulting to a synthetic permalink',()=>{
 const p=sample();p.link='https://finalvestige.com/investigations/apollo-1/';
 assert.ok(auditPublishedAtlas(p).blockers.includes('WP_PUBLISHED_ROUTE_METADATA_NOT_MATCHED'));
});
test('broken internal anchor is surfaced with no network request',()=>{
 const p=sample();p.content+=a('#missing-record');
 const r=auditPublishedAtlas(p);
 assert.ok(r.blockers.includes('BROKEN_INTERNAL_FRAGMENT_REFERENCES'));
 assert.deepEqual(r.findings.dead_internal_fragments,['#missing-record']);
});
test('alt and intrinsic dimensions are required for image structure',()=>{
 const p=sample();p.content=p.content.replace('alt="Historic photograph" width="300" height="200"','alt=""');
 const r=auditPublishedAtlas(p);
 assert.equal(r.findings.missing_alt_count,1);
 assert.equal(r.findings.unsized_image_count,1);
});
test('a valid no-JS worksheet anchor changes only source CTA finding',()=>{
 const p=sample();p.content+='<div id="classroom-preview">Teacher worksheet</div>'+a('#classroom-preview','Free classroom worksheet');
 const r=auditPublishedAtlas(p,{independentlyReviewedLandingUrl:EXPECTED_URL});
 assert.equal(r.findings.free_worksheet_route_present,true);
 assert.ok(!r.blockers.includes('NO_MATCHING_FREE_CLASSROOM_WORKSHEET_PATH'));
 assert.equal(r.browser,'NOT_TESTED');
});
test('unreviewed payment link is never merchant acceptance',()=>{
 const p=sample();p.content+=a('https://payhip.com/b/abcde','Purchase');
 const r=auditPublishedAtlas(p);
 assert.ok(r.blockers.includes('UNREVIEWED_COMMERCE_LINK_IN_ATLAS'));
 assert.equal(r.merchant_settled_sales,'NOT_OBSERVED');
});
test('missing WP body and invalid input fail safely',()=>{
 for(const p of [null,undefined,{},'not an object',{content:'<p>too short</p>'}]){
  const r=auditPublishedAtlas(p);
  assert.ok(r.blockers.includes('NO_READABLE_WORDPRESS_PAGE_SOURCE'));
  assert.equal(r.release,'STAGING_HOLD');
 }
});
test('result deterministic and redacts visitor/buyer private data',()=>{
 const p=sample();p.visitor_email='private@example.test';
 const r=auditPublishedAtlas(p);
 assert.deepEqual(auditPublishedAtlas(p),r);
 assert.ok(!JSON.stringify(r).includes('private@example.test'));
 assert.equal(r.attribution,'NOT_OBSERVED');
});
