'use strict';
/** Source-custody regression suite. No remote HTTP, image bytes, browser or WordPress calls. */
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_pelee_413_loc_20261114.cjs');
const source=JSON.parse(fs.readFileSync(path.join(__dirname,'pelee_413_loc_20261114.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(source));
const rejection=(name,mutate,code)=>test(name,()=>{
  const candidate=clone();mutate(candidate);
  const result=validate(candidate);
  assert.equal(result.ok,false,JSON.stringify(result));
  assert.ok(result.errors.some(e=>e.includes(code)),JSON.stringify(result));
});
test('historical source ledger remains internally valid but strictly HOLD',()=>{
 assert.deepEqual(validate(source),{ok:true,errors:[]});
 assert.equal(source.summary.guest_broken_verified,null);
 assert.equal(source.release.rights_review_required,true);
});
for(let i=0;i<4;i++){
 rejection('false timestamp/eruption provenance row '+i,a=>{
  a.rows[i].provenance='Photographed at 8 a.m. on 8 May 1902 during the lethal eruption, verified by an authoritative archive';
 },'provenance_or_chronology_drift');
 rejection('invented reuse clearance in provenance row '+i,a=>{
  a.rows[i].provenance='This exact image is unrestricted and approved for WordPress caching and full republication';
 },'provenance_or_chronology_drift');
 rejection('generic substituted provenance row '+i,a=>{
  a.rows[i].provenance='Historical photograph of St. Pierre, Martinique, taken by an identified photographer in 1902';
 },'provenance_or_chronology_drift');
}
rejection('rights note cannot be rewritten as blanket license',a=>{
 a.rights_note='https://data.labs.loc.gov/stereographs/README.html confirms unrestricted WordPress upload rights for every item';
},'evidence_custody_drift');
rejection('method cannot become fabricated guest-browser success',a=>{
 a.source_method='Verified uncached guest Chrome images with 200 statuses and network bytes on 2026-11-14';
},'evidence_custody_drift');
rejection('published article identity cannot change',a=>{
 a.post.url='https://finalvestige.com/another-post/';
},'evidence_custody_drift');
rejection('source snapshot PR identity cannot drift',a=>{
 a.source_snapshot.pr=999;
},'source_snapshot');
rejection('the unmatched 413:3 record cannot gain false event-time certainty',a=>{
 a.rows[1].provenance='LOC confirms photograph of exactly the early morning of May 8 1902; copyright cleared, original identified';
},'provenance_or_chronology_drift');
rejection('site metadata cannot claim a license via source note',a=>{
 a.rights_note+=' General unrestricted license granted';
},'evidence_custody_drift');
