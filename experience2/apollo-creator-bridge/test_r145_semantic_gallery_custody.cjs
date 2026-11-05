'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {audit}=require('./r145_semantic_gallery_custody.cjs');
const {inspect,RECORDS}=require('./r144_gallery_media_custody.cjs');
const BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const BAD="const photos = $(box, '[data-fvx-chrono-photo]');";
const FIX="const photos = $$(box, '[data-fvx-chrono-photo]');";
function figure(r){
 return '<figure data-fvx-chrono-photo="'+r.index+'"><img src="'+r.asset+'" alt="NASA archival Apollo historical photograph in contextual source illustration and accompanying caption." width="1920" height="1080"><figcaption>NASA record '+r.id+' does not depict the actual fire. <a href="'+r.source+'">Original NASA source</a></figcaption></figure>';
}
function fixture(){
 return '<style>.fv-ex2 [hidden]{display: none !important;}</style><section data-fvx-chronology>'+
  '<a href="'+BOARD+'">NASA Board report</a><div data-fvx-chrono-tool hidden><input type="range"></div>'+
  '<div data-fvx-chrono-gallery><p class="fvx-chrono-gallery__note">These source photographs are not the actual fire.</p>'+
  RECORDS.map(figure).join('')+'</div></section><p>Editorial use only. Do not use these images in promotional, product or merchandise contexts.</p>'+
  '<script>'+FIX+'</script>';
}
const blocked=(h,code)=>assert.ok(audit(h).blockers.includes(code),JSON.stringify(audit(h)));
test('all three real-structure gallery source records pass source audit only',()=>{
 const r=audit(fixture());assert.deepEqual(r.blockers,[]);
 assert.equal(r.sourceGate,'SOURCE_STRUCTURE_PASS');assert.equal(r.release,'STAGING_HOLD');
 assert.equal(r.findings.sourceRecordCount,3);assert.equal(r.photoCommercialRights,'NOT_APPROVED');
 assert.equal(r.browser,'NOT_TESTED');assert.equal(r.verifiedSales,'NOT_OBSERVED');
});
test('published gallery selector continues to fail until staged fix approved',()=>{
 const r=audit(fixture().replace(FIX,BAD));
 assert.deepEqual(r.blockers,['PUBLISHED_GALLERY_ENHANCEMENT_DEFECT']);
});
test('regression: old regex incorrectly counts a figure inside an HTML comment',()=>{
 const h=fixture().replace('<figure data-fvx-chrono-photo="1">','<!-- <figure data-fvx-chrono-photo="1">')
   .replace('</figure><figure data-fvx-chrono-photo="2">','</figure> --><figure data-fvx-chrono-photo="2">');
 assert.deepEqual(inspect(h).blockers,[]);blocked(h,'THREE_VISIBLE_SCOPED_FIGURES_NOT_CONFIRMED');
});
test('regression: source in a template is not a navigable figure',()=>{
 const h=fixture().replace('<figure data-fvx-chrono-photo="1">','<template><figure data-fvx-chrono-photo="1">')
  .replace('</figure><figure data-fvx-chrono-photo="2">','</figure></template><figure data-fvx-chrono-photo="2">');
 assert.deepEqual(inspect(h).blockers,[]);blocked(h,'THREE_VISIBLE_SCOPED_FIGURES_NOT_CONFIRMED');
});
test('regression: hidden gallery ancestor defeats purported no-JS access',()=>{
 const h=fixture().replace('<div data-fvx-chrono-gallery>','<div data-fvx-chrono-gallery hidden>');
 assert.deepEqual(inspect(h).blockers,[]);blocked(h,'SOURCE_CONTENT_INACCESSIBLE_WITHOUT_JS');
});
test('a style-hidden ancestor similarly defeats source access',()=>{
 const h=fixture().replace('<div data-fvx-chrono-gallery>','<div data-fvx-chrono-gallery style="display:none">');
 blocked(h,'SOURCE_CONTENT_INACCESSIBLE_WITHOUT_JS');
});
test('an inert gallery is not credited as accessible',()=>{
 blocked(fixture().replace('<div data-fvx-chrono-gallery>','<div data-fvx-chrono-gallery inert>'),'SOURCE_CONTENT_INACCESSIBLE_WITHOUT_JS');
});
test('a hidden NASA original link does not count as an accessible link',()=>{
 const h=fixture().replace('<a href="'+RECORDS[0].source+'"','<a hidden href="'+RECORDS[0].source+'"');
 assert.deepEqual(inspect(h).blockers,[]);blocked(h,'SOURCE_CONTENT_INACCESSIBLE_WITHOUT_JS');
});
test('duplicate NASA links inside one caption are rejected',()=>{
 const link='<a href="'+RECORDS[0].source+'">Original NASA source</a>';
 const h=fixture().replace(link,link+link);
 assert.deepEqual(inspect(h).blockers,[]);blocked(h,'VISIBLE_ORIGINAL_SOURCE_LINK_NOT_CONFIRMED');
});
test('source text in HTML comments cannot replace a genuine anchor',()=>{
 const link='<a href="'+RECORDS[0].source+'">Original NASA source</a>';
 const h=fixture().replace(link,'<!-- '+link+' -->');
 assert.deepEqual(inspect(h).blockers,[]);blocked(h,'VISIBLE_ORIGINAL_SOURCE_LINK_NOT_CONFIRMED');
});
test('NASA source link outside its caption does not prove custody',()=>{
 const link='<a href="'+RECORDS[0].source+'">Original NASA source</a>';
 blocked(fixture().replace(link,'</figcaption>'+link+'<figcaption>'), 'FIGURE_IMAGE_CAPTION_STRUCTURE_DRIFT');
});
test('non-NASA link is not allowed to take the canonical original source slot',()=>{
 blocked(fixture().replace(RECORDS[0].source,'https://example.org/source'),'VISIBLE_ORIGINAL_SOURCE_LINK_NOT_CONFIRMED');
});
test('extra hidden or tracking image in one figure fails exact image custody',()=>{
 const needle='<figcaption>NASA record '+RECORDS[0].id;
 const h=fixture().replace(needle,'<img src="https://tracker.example/pixel.gif" alt=" ">'+needle);
 blocked(h,'FIGURE_IMAGE_CAPTION_STRUCTURE_DRIFT');
});
test('wrong asset path is not certified',()=>{
 blocked(fixture().replace(RECORDS[0].asset,'https://example.org/unknown.jpg'),'VISIBLE_IMAGE_CUSTODY_NOT_CONFIRMED');
});
test('figures inside a second chronology fail unique scope',()=>{
 const h=fixture().replace('</section>','</section><section data-fvx-chronology><p>duplicate</p></section>');
 blocked(h,'GALLERY_SCOPE_NOT_UNIQUE');
});
test('duplicate gallery attr flags ambiguous custody',()=>{
 const h=fixture().replace('data-fvx-chrono-gallery','data-fvx-chrono-gallery data-fvx-chrono-gallery');
 blocked(h,'GALLERY_MARKUP_AMBIGUOUS');
});
test('unterminated HTML comment is a fail-closed parsing error',()=>{
 blocked(fixture()+'<!-- unfinished','GALLERY_MARKUP_AMBIGUOUS');
});
test('missing figure or incorrect source sequence is not allowed',()=>{
 const h=fixture().replace('<figure data-fvx-chrono-photo="2">','<figure data-fvx-chrono-photo="1">');
 blocked(h,'THREE_VISIBLE_SCOPED_FIGURES_NOT_CONFIRMED');
});
test('source-only report is deterministic and never asserts sales, rights or live acceptance',()=>{
 const a=audit(fixture());assert.deepEqual(a,audit(fixture()));
 assert.equal(a.axe,'NOT_TESTED');assert.equal(a.lcp_cls,'NOT_MEASURED');
 assert.equal(a.merchant,'NOT_VERIFIED');assert.equal(a.release,'STAGING_HOLD');
});
test('wrong input type is rejected, not converted into a plausible source report',()=>{
 assert.throws(()=>audit(null),/Expected read-only HTML|Expected read-only HTML export/);
});
