'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const crypto=require('node:crypto'),fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const {prepare,writeReview}=require('./r145_review_preview_cli.cjs');
const {RECORDS}=require('./r144_gallery_media_custody.cjs');
const BAD="const photos = $(box, '[data-fvx-chrono-photo]');";
const FIX="const photos = $$(box, '[data-fvx-chrono-photo]');";
const BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const ARTICLE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
function fixture(){
 return '<style>.fv-ex2 [hidden] {display: none !important;}</style>'+
  '<section data-fvx-chronology><a href="'+BOARD+'">Review Board</a><div data-fvx-chrono-tool hidden><input type="range"></div>'+
  '<div data-fvx-chrono-gallery><p class="fvx-chrono-gallery__note">Historical context photographs, not the actual fire.</p>'+
  RECORDS.map(r=>'<figure data-fvx-chrono-photo="'+r.index+'"><img src="'+r.asset+'" width="1920" height="1080" alt="NASA archival contextual Apollo One historical photograph with documented source and accurate caption."><figcaption>NASA record '+r.id+' does not depict the actual fire. <a href="'+r.source+'">Original NASA source</a></figcaption></figure>').join('')+
  '</div></section><p>Editorial use only. Do not use these images in promotional, product or merchandise contexts.</p>'+
  '<a href="'+ARTICLE+'">Read the full investigation</a><script>(()=>{'+BAD+'})()</script>';
}
test('review artifact has exactly one extra selector character and no other source changes',()=>{
 const source=fixture(),r=prepare(source);
 assert.equal(r.html,source.replace(BAD,()=>FIX));
 assert.equal(r.html.length,source.length+1);
 assert.equal(r.manifest.source_sha256,sha(source));
 assert.equal(r.manifest.review_html_sha256,sha(r.html));
 assert.equal(r.manifest.release,'STAGING_HOLD');
 assert.equal(r.manifest.approved_to_publish,false);
});
test('same input gives byte-for-byte identical preview and manifest without clock dependence',()=>{
 const r1=prepare(fixture()),r2=prepare(fixture());
 assert.deepEqual(r1,r2);
});
test('already repaired source cannot be used for a silent live approval',()=>{
 assert.throws(()=>prepare(fixture().replace(BAD,()=>FIX)),/SOURCE_NOT_SINGLE_KNOWN_GALLERY_DEFECT/);
});
test('ghost media record in comment is a staging blocker',()=>{
 const src=fixture();
 const tampered=src.replace('<figure data-fvx-chrono-photo="1">','<!-- <figure data-fvx-chrono-photo="1">')
  .replace('</figure><figure data-fvx-chrono-photo="2">','</figure> --><figure data-fvx-chrono-photo="2">');
 assert.throws(()=>prepare(tampered),/SOURCE_NOT_SINGLE_KNOWN_GALLERY_DEFECT/);
});
test('writes only requested local artifacts and preserves original input bytes',()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'fv-r145-test-'));
 try{
  const source=fixture(),input=path.join(temp,'wp-read-only.html');
  fs.writeFileSync(input,source,'utf8');
  const r=writeReview(input,path.join(temp,'review'));
  assert.equal(fs.readFileSync(input,'utf8'),source);
  const preview=fs.readFileSync(r.paths[0],'utf8');
  assert.equal(preview,source.replace(BAD,()=>FIX));
  assert.equal(JSON.parse(fs.readFileSync(r.paths[1],'utf8')).review_html_sha256,sha(preview));
  assert.equal(r.manifest.browser,'NOT_TESTED');
  assert.equal(r.manifest.attributed_sales,'NOT_OBSERVED');
 } finally{fs.rmSync(temp,{recursive:true,force:true});}
});
