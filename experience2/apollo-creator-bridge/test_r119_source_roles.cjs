'use strict';
/* R119 source contract mutation tests. Browser, axe and real merchant checks are separate gates. */
const assert=require('node:assert/strict');
const test=require('node:test');
const fs=require('node:fs');
const path=require('node:path');
const {R,audit}=require('./qa_r119_source_roles.cjs');
const apollo=fs.readFileSync(path.join(__dirname,'landing-preview.html'),'utf8');
function desk(){
 const types=['DOCUMENTED CONTEXT','PRIMARY REVIEW BOARD RECORD','INSTRUMENT CHRONOLOGY',
 'HARDWARE AND DESIGN FINDING','EVIDENCE BOUNDARY','ENGINEERING RESPONSE'];
 return R.map(([num,id,url],i)=>
  '<article id="fv-ex2-ledger-apollo1-record-'+num+'"><div>'+types[i]+'</div>'+
  '<span>NASA '+id+'</span><a href="'+url+'">NASA photographic page</a></article>').join('\n');
}
const fixture=desk();
test('01 current Apollo page and six-record Research Desk-compatible fixture are source complete',()=>{
 const r=audit(apollo,fixture);
 assert.equal(r.releasable,false);
 assert.equal(r.gate,'STAGING_HOLD');
 assert.equal(r.records.length,6);
 assert.equal(r.blockers.length,0);
 assert.equal(r.editorial_review_flags.length,6);
});
test('02 source role label is mandatory',()=>{
 assert.ok(audit(apollo.replace('data-fv-source-role-key','data-fv-removed-role'),fixture)
 .blockers.includes('MISSING_ON_PAGE_SOURCE_ROLE_EXPLANATION'));
});
test('03 rights warning is mandatory',()=>{
 assert.ok(audit(apollo.replaceAll('INDIVIDUAL_REVIEW_REQUIRED','rights_unknown')
 .replaceAll('(0/6)','(??? )'),fixture).blockers
 .includes('UNRESOLVED_RIGHTS_OR_CATALOG_WARNING_MISSING'));
});
test('04 catalog uncertainty is mandatory',()=>{
 assert.ok(audit(apollo.replaceAll('S67-19766 (provisional)','S67-19766 (confirmed)'),fixture)
 .blockers.includes('UNRESOLVED_RIGHTS_OR_CATALOG_WARNING_MISSING'));
});
test('05 Apollo photo source tampering is detected',()=>{
 const corrupted=apollo.replace(R[2][2],'https://example.invalid/unsourced');
 assert.ok(audit(corrupted,fixture).blockers.includes('PHOTO_SOURCE_URL_MISMATCH:03'));
});
test('06 Research Desk source-link tampering is detected',()=>{
 const corrupted=fixture.replace(R[1][2],'https://example.invalid/unsourced');
 assert.ok(audit(apollo,corrupted).blockers.includes('PHOTO_SOURCE_URL_MISMATCH:02'));
});
test('07 catalog identifier drift is detected',()=>{
 const corrupted=fixture.replace('S67-21294','S67-21293');
 assert.ok(audit(apollo,corrupted).blockers.includes('PHOTO_CATALOG_DRIFT:05'));
});
test('08 removal of a source row is detected',()=>{
 const corrupted=apollo.replace(/<tr id="photo-source-05"[\s\S]*?<\/tr>/,'');
 assert.ok(audit(corrupted,fixture).blockers.includes('APOLLO_NOT_SIX_PHOTO_ROWS:5'));
});
test('09 injected photo binary is rejected',()=>{
 assert.ok(audit(apollo+'<img src="https://untrusted.invalid/photo.jpg">',fixture)
 .blockers.includes('UNREVIEWED_MEDIA_OR_GEO_ADDED'));
});
test('10 invented geospatial coordinates are rejected',()=>{
 assert.ok(audit(apollo+'<aside data-lat="28.5">pin</aside>',fixture)
 .blockers.includes('UNREVIEWED_MEDIA_OR_GEO_ADDED'));
});
test('11 visitor collection form is rejected',()=>{
 assert.ok(audit(apollo+'<form action="/capture"><input></form>',fixture)
 .blockers.includes('UNAPPROVED_CAPTURE_COMMERCE_OR_REMOTE_SCRIPT'));
});
test('12 unapproved merchant link is rejected',()=>{
 assert.ok(audit(apollo+'<a href="https://payhip.com/no-verified-offer">Buy</a>',fixture)
 .blockers.includes('UNAPPROVED_CAPTURE_COMMERCE_OR_REMOTE_SCRIPT'));
});
test('13 duplicate primary CTA is rejected',()=>{
 assert.ok(audit(apollo+'<a href="#classroom-preview" data-fv-primary-cta>More</a>',fixture)
 .blockers.includes('PRIMARY_CTA_NOT_UNIQUE'));
});
test('14 no automatic release on clean synthetic reconciliation',()=>{
 const normalized=fixture.replace('NASA S67-19766','NASA S67-19766 (provisional)')
 .replace('PRIMARY REVIEW BOARD RECORD','PHOTO CONTEXT')
 .replace('INSTRUMENT CHRONOLOGY','PHOTO CONTEXT')
 .replace('HARDWARE AND DESIGN FINDING','PHOTO CONTEXT')
 .replace('EVIDENCE BOUNDARY','PHOTO CONTEXT')
 .replace('ENGINEERING RESPONSE','PHOTO CONTEXT');
 const r=audit(apollo,normalized);
 assert.equal(r.blockers.length,0);
 assert.equal(r.editorial_review_flags.length,0);
 assert.equal(r.gate,'STAGING_HOLD');
 assert.equal(r.releasable,false);
});
