'use strict';
// Pure mutation suite. Run: node qa/media-recovery/test_lituya_277_visual_20261102.cjs
function runTests(validate, raw, frozen) {
  const deep = value => JSON.parse(JSON.stringify(value));
  const cases = [];
  const expect = (title,mutator,shouldPass=false) => {
    const a=deep(raw),s=deep(frozen);
    mutator(a,s);
    const result=validate(a,s);
    const passed=result.ok===shouldPass;
    cases.push({title,passed,errors:result.errors});
    if(!passed) throw Error(title+': expected '+shouldPass+' got '+result.ok+' '+result.errors.join('; '));
  };
  expect('exact snapshot and audit accepted',()=>{},true);
  expect('one missing image',a=>a.images.pop());
  expect('extra image',a=>a.images.push(deep(a.images[5])));
  expect('swapped image keys',a=>{a.images[0].image_key='277:2';});
  expect('replaced historical src',a=>{a.images[0].original_src='https://example.com/invented.jpg';});
  expect('rewritten published ALT',a=>{a.images[0].original_alt='generic old photo';});
  expect('modified frozen source URL',(a,s)=>{s.images.find(x=>x.key==='277:0').source_url='https://example.com/fake.jpg';});
  expect('modified snapshot SHA',a=>{a.snapshot.git_blob_sha='f'.repeat(40);});
  expect('modified source post URL',(a,s)=>{s.posts.find(p=>p.id===277).url='https://example.com/wrong';});
  expect('visitor 404 fabricated',a=>{a.images[1].guest_browser.actual_http_status=404;});
  expect('visitor final URL fabricated',a=>{a.images[1].guest_browser.final_url='https://example.com';});
  expect('visitor image decoding invented',a=>{a.images[0].guest_browser.decode_success=true;});
  expect('visitor naturalWidth invented',a=>{a.images[0].guest_browser.natural_width_px=800;});
  expect('visitor wire bytes invented',a=>{a.images[0].guest_browser.encoded_data_length_bytes=50000;});
  expect('view tool refusal called HTTP 404',a=>{a.images[3].independent_viewer.numeric_origin_http_status=404;});
  expect('researchgate source wrongly marked displayed',a=>{a.images[1].independent_viewer.result='IMAGE_RENDERED_IN_INDEPENDENT_VIEWER';});
  expect('reported 42 broken as measured',a=>{a.result.confirmed_visitor_broken=42;});
  expect('invented 76 percent saving',a=>{a.result.percent_weight_reduction=76;});
  expect('NASA file improperly upscaled',a=>{a.images[5].optimization.conditional_width_px=960;});
  expect('NASA master width falsified',a=>{a.images[5].primary_source_candidate.master_width_px=960;});
  expect('unverified 277:4 width invented',a=>{a.images[4].optimization.conditional_width_px=960;});
  expect('unverified USGS original resize invented',a=>{a.images[4].primary_source_candidate.conditional_width_px=960;});
  expect('image licensed without approval',a=>{a.images[0].rights_review.status='CLEARED';});
  expect('wordpress cache approval forged',a=>{a.images[5].publication.cache_approved=true;});
  expect('source rewrite approval forged',a=>{a.images[4].publication.source_rewrite_approved=true;});
  expect('fabricated asset binary hash',a=>{a.images[5].publication.binary_sha256='a'.repeat(64);});
  expect('annotated scientific collage misrepresented',a=>{a.images[0].editorial.finding='NO_VISUAL_MISMATCH_OBSERVED';});
  expect('USGS annotated photo omitted from editorial issues',a=>{a.images[4].editorial.finding='NO_VISUAL_MISMATCH_OBSERVED';});
  expect('NASA false color issue lost',a=>{a.images[5].editorial.finding='NO_VISUAL_MISMATCH_OBSERVED';});
  expect('Site QA bypassed',a=>{a.release_gates.site_qa_guest_chrome_evidence_required=false;});
  expect('homepage interference authorized',a=>{a.release_gates.homepage_design_unchanged=false;});
  expect('silent subscription spend',a=>{a.release_gates.subscription_spend_usd=20;});
  return {pass:cases.filter(t=>t.passed).length,total:cases.length,cases};
}
module.exports={runTests};
if(require.main===module) {
  const fs=require('node:fs'),path=require('node:path');
  const dir=__dirname;
  const audit=JSON.parse(fs.readFileSync(path.join(dir,'lituya_277_visual_rights_20261102.json'),'utf8'));
  const inventory=JSON.parse(fs.readFileSync(path.join(dir,'parts/04.json'),'utf8'));
  const {validate}=require('./validate_lituya_277_visual_20261102.cjs');
  const {pass,total}=runTests(validate,audit,inventory);
  console.log('Lituya 277 provenance and rights: '+pass+'/'+total+' PASS');
}
