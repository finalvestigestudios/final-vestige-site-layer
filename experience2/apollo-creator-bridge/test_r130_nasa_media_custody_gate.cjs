'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {auditMediaLedger}=require('./r130_nasa_media_custody_gate.cjs');
const dir=__dirname, ledger=JSON.parse(fs.readFileSync(path.join(dir,'r130_nasa_media_custody.json'),'utf8'));
const source=fs.readFileSync(path.join(dir,'landing-preview.html'),'utf8');
const run=(l,h)=>auditMediaLedger(l,h);
const mutate=(fn)=>{const copy=JSON.parse(JSON.stringify(ledger));fn(copy);return copy;};
test('exact NASA source custody has six direct NASA image-page records and zero commercial clearances',()=>{
 const result=run(ledger,source);
 assert.equal(result.status,'PASS_SOURCE_CUSTODY_ONLY',JSON.stringify(result.errors));
 assert.equal(result.record_count,6);assert.equal(result.official_metadata_verified_count,6);
 assert.equal(result.secondary_only_metadata_count,0);assert.equal(result.commercially_cleared_count,0);
 assert.equal(result.release_status,'STAGING_HOLD');
});
test('media rights cannot be auto-cleared by ledger editing',()=>{
 const x=mutate(l=>l.records[0].rights_status='CLEARED');assert.equal(run(x,source).status,'FAIL');
});
test('NASA official metadata confirmation cannot silently regress to secondary-only',()=>{
 const x=mutate(l=>l.records[3].metadata_evidence='SECONDARY_NASA_ORIGIN_REFERENCE_ONLY');assert.equal(run(x,source).status,'FAIL');
});
test('crew portrait catalog cannot be treated as confirmed',()=>{
 const x=mutate(l=>l.records[0].catalog_status='S67-19766_VERIFIED');assert.equal(run(x,source).status,'FAIL');
});
test('crew portrait event day cannot be guessed',()=>{
 const x=mutate(l=>l.records[0].record_date='1967-01-27');assert.equal(run(x,source).status,'FAIL');
});
test('source URL substitution fails even if link is on a NASA domain',()=>{
 const x=mutate(l=>l.records[2].source_url='https://www.nasa.gov/');assert.equal(run(x,source).status,'FAIL');
});
test('duplicate records fail custody audit',()=>{
 const x=mutate(l=>l.records[2]=l.records[1]);assert.equal(run(x,source).status,'FAIL');
});
test('retrospective 2017 exhibit cannot be reclassified as 1967 evidence',()=>{
 const x=mutate(l=>l.records[5].visual_role='FIRE_EVENT_PHOTOGRAPH');assert.equal(run(x,source).status,'FAIL');
});
test('record/worksheet rights marker removal fails',()=>{
 const changed=source.replace('data-fv-student-photo="01" data-fv-photo-rights="not-cleared"','data-fv-student-photo="01"');
 assert.notEqual(changed,source);assert.equal(run(ledger,changed).status,'FAIL');
});
test('table NASA destination drift fails',()=>{
 const changed=source.replace('href="https://www.nasa.gov/image-detail/amf-s67-15717/"','href="https://www.nasa.gov/image-detail/other-image/"');
 assert.notEqual(changed,source);assert.equal(run(ledger,changed).status,'FAIL');
});
test('commercial publicity is not waived for portraits',()=>{
 const x=mutate(l=>l.records[2].publicity_review='WAIVED');assert.equal(run(x,source).status,'FAIL');
});
test('photograph embedding triggers hold',()=>{
 const changed=source.replace('</main>','<img src="nasa-photo.jpg"></main>');
 assert.notEqual(changed,source);assert.equal(run(ledger,changed).status,'FAIL');
});
test('global media use policy and zero-cleared state cannot be stripped',()=>{
 const x=mutate(l=>{l.media_policy_sources=[];l.commercial_image_reuse='CLEARED';});
 assert.equal(run(x,source).status,'FAIL');
});
test('source role must remain visual context rather than instrument measurement',()=>{
 const x=mutate(l=>l.records[4].source_role='TECHNICAL_MEASUREMENT');
 assert.equal(run(x,source).status,'FAIL');
});
test('zero-cleared visible copy cannot be removed',()=>{
 const changed=source.replace('none of the six linked photographs is cleared for commercial republication (0/6)','all cleared');
 assert.notEqual(changed,source);assert.equal(run(ledger,changed).status,'FAIL');
});

test('visible NASA catalog date cannot drift from reviewed record',()=>{
 const changed=source.replace('Jan 3, 1967</td><td>Spacecraft preparation','Jan 4, 1967</td><td>Spacecraft preparation');
 assert.notEqual(changed,source);assert.equal(run(ledger,changed).status,'FAIL');
});
test('visible source credit cannot be silently reassigned',()=>{
 const changed=source.replace('Image Credit: NASA/Kim Shiflett</small>','Image Credit: Unverified Contributor</small>');
 assert.notEqual(changed,source);assert.equal(run(ledger,changed).status,'FAIL');
});

test('NASA 04 official record evidence cannot be replaced with secondary-only provenance',()=>{
 const x=mutate(l=>l.records[3].metadata_support='https://commons.wikimedia.org/wiki/File:Apollo_1_Tribute_spacecraft_mockup.JPG');
 assert.equal(run(x,source).status,'FAIL');
});
test('record 04 NASA/Kim Shiflett source credit drift is rejected',()=>{
 const x=mutate(l=>l.records[3].credit='Unverified contributor');
 assert.equal(run(x,source).status,'FAIL');
});
test('record 04 primary NASA catalog identifier drift is rejected',()=>{
 const x=mutate(l=>l.records[3].catalog_status='KSC-20170124-PH_KLS01_0000');
 assert.equal(run(x,source).status,'FAIL');
});
test('record 02 visual evidence cannot be elevated to technical measurement',()=>{
 const x=mutate(l=>l.records[1].visual_role='CABIN_OXYGEN_INSTRUMENT');
 assert.equal(run(x,source).status,'FAIL');
});
