'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {audit,EXPECTED}=require('./r127_source_role_crosswalk.cjs');
const apollo=fs.readFileSync(path.join(__dirname,'landing-preview.html'),'utf8');
const kinds=['DOCUMENTED CONTEXT','PRIMARY REVIEW BOARD RECORD','INSTRUMENT CHRONOLOGY',
  'HARDWARE AND DESIGN FINDING','EVIDENCE BOUNDARY','ENGINEERING RESPONSE'];
const bodies=[
  'Crew prepared for the countdown test. NASA S67-19766.',
  'NASA measured high pressure oxygen during the test.',
  'The instrument record shows fire pressure chronology.',
  'An inward-opening hatch complicated egress.',
  'The specific ignition source was never conclusively identified.',
  'The redesigned hatch opened outward.'
];
function deskFixture() {
  return EXPECTED.map(([id,url],i)=>
    '<article id="fv-ex2-ledger-apollo1-record-'+id+'"><div class="fv-ex2-ledger__kind">'+
    kinds[i]+'</div><p>'+bodies[i]+'</p><a href="'+url+'">NASA photo</a></article>').join('\n');
}
test('Apollo has six typed, unembedded source references and a visible no-JS provenance note',()=>{
  const report=audit(apollo,deskFixture());
  assert.equal(report.link_integrity,'PASS');
  assert.equal(report.record_count,6);
  assert.equal(report.records.filter(r=>r.nasa_url_match).length,6);
  assert.match(apollo,/data-fv-source-role-warning/);
  assert.match(apollo,/The NASA Apollo 204 Review Board report supports the technical conclusions/);
});
test('six specific source-role editorial concerns are reported, never silently cleared',()=>{
  const report=audit(apollo,deskFixture());
  assert.deepEqual(report.editorial_flags,EXPECTED.map(row=>'R158_'+row[2]));
  assert.equal(report.release_status,'STAGING_HOLD');
  assert.equal(report.photograph_rights_approved,0);
  assert.equal(report.conversion_status,'NO_VERIFIED_MATCHING_PAID_SKU');
});
test('mismatched NASA photograph URL fails the crosswalk',()=>{
  const broken=deskFixture().replace(EXPECTED[2][1],'https://www.nasa.gov/image-detail/different/');
  assert.ok(audit(apollo,broken).integrity_errors.includes('NASA_URL_MISMATCH_03'));
});
test('missing Research Desk record blocks release rather than shrinking the denominator',()=>{
  const broken=deskFixture().replace(/<article id="fv-ex2-ledger-apollo1-record-06"[\s\S]*?<\/article>/,'');
  const report=audit(apollo,broken);
  assert.ok(report.integrity_errors.includes('MISSING_RECORD_06'));
  assert.equal(report.link_integrity,'FAIL');
});
test('removing a typed Apollo photograph role blocks integration',()=>{
  const broken=apollo.replace('data-fv-source-kind="photograph"','');
  assert.ok(audit(broken,deskFixture()).integrity_errors.includes('APOLLO_ROLE_NOT_MACHINE_READABLE_01'));
});
test('inserting an embedded image fails the source boundary',()=>{
  const report=audit(apollo.replace('</main>','<img src="https://example.org/unauthorized.jpg"></main>'),deskFixture());
  assert.ok(report.integrity_errors.includes('UNREVIEWED_EMBEDDED_MEDIA'));
});
test('explicit provisional label resolves only its corresponding editorial warning',()=>{
  const fixed=deskFixture().replace('Crew prepared for the countdown test. NASA S67-19766.',
    'Crew prepared for the countdown test. NASA S67-19766 provisional, day unconfirmed.');
  const report=audit(apollo,fixed);
  assert.ok(!report.editorial_flags.includes('R158_PORTRAIT_CATALOG_PROVISIONAL'));
  assert.equal(report.editorial_flags.length,5);
  assert.equal(report.photograph_rights_approved,0);
});
test('output is deterministic and does not assert fabricated orders or traffic',()=>{
  const a=audit(apollo,deskFixture()),b=audit(apollo,deskFixture());
  assert.equal(JSON.stringify(a),JSON.stringify(b));
  assert.equal(a.claims.net_revenue,'UNOBSERVABLE');
  assert.equal(a.claims.qualified_sessions,'UNOBSERVABLE');
  assert.equal(a.claims.merchant_paid_orders,'UNOBSERVABLE');
});
