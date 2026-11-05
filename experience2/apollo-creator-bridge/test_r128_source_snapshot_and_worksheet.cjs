'use strict';
/** Run: node --test experience2/apollo-creator-bridge/test_r128_source_snapshot_and_worksheet.cjs */
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {audit,EXPECTED,gitBlobSha,TRUSTED_RESEARCH_BLOB}=require('./r127_source_role_crosswalk.cjs');
const apollo=fs.readFileSync(path.join(__dirname,'landing-preview.html'),'utf8');
const labels=['DOCUMENTED CONTEXT','PRIMARY REVIEW BOARD RECORD','INSTRUMENT CHRONOLOGY',
  'HARDWARE AND DESIGN FINDING','EVIDENCE BOUNDARY','ENGINEERING RESPONSE'];
const summaries=['Crew prepared for countdown rehearsal, NASA S67-19766.',
  'NASA documented elevated oxygen pressure.', 'Instrument readings during the fire.',
  'Inward hatch complicated escape.','Electrical arc did not prove a specific ignition point.',
  'Outward hatch followed redesign.'];
const desk=()=>EXPECTED.map(([id,url],i)=>
  '<article id="fv-ex2-ledger-apollo1-record-'+id+'"><div class="fv-ex2-ledger__kind">'+
  labels[i]+'</div><p>'+summaries[i]+'</p><a href="'+url+'">NASA</a></article>').join('\n');
const errors=(html=apollo)=>audit(html,desk()).integrity_errors;
test('Git blob digest follows the actual git-blob framing convention',()=>{
  assert.equal(gitBlobSha('hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0');
  assert.equal(gitBlobSha('hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a');
  assert.equal(TRUSTED_RESEARCH_BLOB,'403d128c57b9bc82dac7c619651689070edef86c');
});
test('fixture URL alignment does not masquerade as the pinned Research Desk PR #158',()=>{
  const r=audit(apollo,desk());
  assert.equal(r.link_integrity,'PASS');
  assert.equal(r.source_custody,'BLOCKED_UNREVIEWED_SOURCE');
  assert.equal(r.research_desk_snapshot.status,'UNREVIEWED_SOURCE_DRIFT');
  assert.equal(r.release_status,'STAGING_HOLD');
});
test('six worksheet image links and six main photo links are exact URL matches',()=>{
  assert.deepEqual(errors(),[]);
  const r=audit(apollo,desk());
  assert.equal(r.records.filter(x=>x.nasa_url_match).length,6);
  assert.equal(r.photograph_rights_approved,0);
});
test('main source privacy is checked on matching anchor rather than any sibling',()=>{
  const broken=apollo.replace('rel="noreferrer noopener">NASA crew training portrait','rel="noopener">NASA crew training portrait');
  assert.ok(errors(broken).includes('APOLLO_PHOTO_REFERRER_LEAK_01'));
});
test('second photograph link cannot silently pass the custody record count',()=>{
  const broken=apollo.replace('NASA crew training portrait</a>',
    'NASA crew training portrait</a><a href="https://www.nasa.gov/image-detail/apollo-1-crew-honored/">duplicate</a>');
  assert.ok(errors(broken).includes('PHOTO_SOURCE_LINK_CARDINALITY_01'));
});
test('worksheet source privacy is independent of main source register',()=>{
  const broken=apollo.replace('rel="noreferrer noopener">NASA crew portrait record',
    'rel="noopener">NASA crew portrait record');
  assert.ok(errors(broken).includes('STUDENT_WORKSHEET_SOURCE_PRIVACY_01'));
});
test('worksheet record cannot quietly switch to a different official NASA photograph',()=>{
  const broken=apollo.replace(
    'https://www.nasa.gov/image-detail/apollo-1-crew-honored/" rel="noreferrer noopener">NASA crew portrait record',
    'https://www.nasa.gov/image-detail/amf-s67-15717/" rel="noreferrer noopener">NASA crew portrait record');
  assert.ok(errors(broken).includes('STUDENT_WORKSHEET_SOURCE_MISMATCH_01'));
});
test('missing student record fails instead of shrinking the denominator',()=>{
  const broken=apollo.replace(/<li data-fv-student-photo="06">[\s\S]*?<\/li>/,'');
  assert.ok(errors(broken).includes('STUDENT_WORKSHEET_SOURCE_COUNT'));
});
test('duplicated student record fails instead of passing by total source-count alone',()=>{
  const part=(apollo.match(/<li data-fv-student-photo="01">[\s\S]*?<\/li>/)||[])[0];
  assert.ok(part);
  const broken=apollo.replace('<li data-fv-student-photo="06">','<li data-fv-student-photo="01">');
  assert.ok(errors(broken).includes('STUDENT_WORKSHEET_SOURCE_COUNT'));
});
test('calendar-day checkpoint drift fails source chronology acceptance',()=>{
  const broken=apollo.replace('data-fv-photo-day="1967-01-03"','data-fv-photo-day="1967-01-04"');
  assert.ok(errors(broken).includes('PHOTO_CHRONOLOGY_DATE_DRIFT'));
});
test('unverified crew portrait may not be silently inserted into dated checkpoints',()=>{
  const broken=apollo.replace('<aside data-fv-photo-month-uncertain',
    '<aside data-fv-photo-day="1967-01-27"');
  assert.ok(errors(broken).includes('PROVISIONAL_PORTRAIT_DATE_MISSING'));
});
test('report is deterministic, external permissions unknown, revenue not invented',()=>{
  const a=audit(apollo,desk()), b=audit(apollo,desk());
  assert.equal(JSON.stringify(a),JSON.stringify(b));
  assert.equal(a.claims.merchant_paid_orders,'UNOBSERVABLE');
  assert.equal(a.claims.net_revenue,'UNOBSERVABLE');
  assert.equal(a.conversion_status,'NO_VERIFIED_MATCHING_PAID_SKU');
});
