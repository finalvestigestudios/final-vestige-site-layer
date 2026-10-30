'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const {canonicalPath,linkedPaths,audit} = require('./public_preview_gate.cjs');
const root = 'https://finalvestige.com/accountability/';
const doc = (overrides = {}) => ({
  id:1312, url:'https://finalvestige.com/accountability/failures-to-protect/gabriel-fernandez-warnings-in-the-system/',
  status:'publish',noindex:true,editorial_label:'Research Draft',...overrides
});
const snap = (documents=[doc()],changes={}) => ({landing:{id:1304,status:'publish',noindex:false,
  seo_title:'',seo_description:'',markup:`<a href="${documents[0]?.url || root}">Research preview</a>`, ...changes},documents});
test('canonicalizes relative site URLs, fragments and duplicate slashes',()=>{
  assert.equal(canonicalPath('/focus/#subscribe-blog'),'/focus/');
  assert.equal(canonicalPath('https://finalvestige.com/foo///'),'/foo/');
});
test('rejects external and malformed URLs',()=>{
  assert.equal(canonicalPath('https://elsewhere.example/a'),null);
  assert.equal(canonicalPath('javascript:alert(1)'),null);
  assert.equal(canonicalPath(null),null);
});
test('collects only href destinations, not arbitrary URLs embedded in text',()=>{
  const x=linkedPaths('<p>/accountability/private/</p><a href="/accountability/">Start</a>');
  assert.deepEqual([...x],['/accountability/']);
});
test('flags linked, published, explicitly labeled research preview without asserting browser issue',()=>{
  const a=audit(snap());
  assert.equal(a.published_research_previews,1);
  assert.equal(a.production_browser_verified,false);
  assert.ok(a.findings.some(x=>x.code==='REVIEW_PUBLIC_RESEARCH_PREVIEW'));
  assert.ok(!a.findings.some(x=>x.level==='high'));
});
test('does not claim unlinked drafts are publicly promoted',()=>{
  const s=snap();s.landing.markup='<a href="/accountability/">Hub</a>';
  assert.equal(audit(s).published_research_previews,0);
});
test('flags linked nonpublished page as unresolved destination',()=>{
  const x=audit(snap([doc({status:'draft'})]));
  assert.ok(x.findings.some(f=>f.code==='HIGH_LINKED_UNPUBLISHED'));
});
test('flags linked indexable Research Draft independent of metadata gap',()=>{
  const x=audit(snap([doc({noindex:false})]));
  assert.ok(x.findings.some(f=>f.code==='HIGH_INDEXABLE_RESEARCH_DRAFT'));
});
test('indexable public hub with missing saved metadata is review, not proven search snippet issue',()=>{
  const x=audit(snap());
  assert.ok(x.findings.some(f=>f.code==='REVIEW_INDEXABLE_HUB_METADATA'));
});
test('complete hub metadata suppresses metadata-review message',()=>{
  const x=audit(snap([doc()],{seo_title:'Public Record',seo_description:'Official records and sourced analysis'}));
  assert.ok(!x.findings.some(f=>f.code==='REVIEW_INDEXABLE_HUB_METADATA'));
});
test('final published content does not trigger Research Draft review',()=>{
  const x=audit(snap([doc({editorial_label:'Established Criminal Accountability'})]));
  assert.ok(!x.findings.some(f=>f.code==='REVIEW_PUBLIC_RESEARCH_PREVIEW'));
});
test('does not treat noindex as a privacy gate',()=>{
  const x=audit(snap());
  assert.ok(x.findings.some(f=>f.code==='REVIEW_PUBLIC_RESEARCH_PREVIEW'));
});
test('handles zero documents and rejects malformed snapshots',()=>{
  assert.equal(audit({landing:{status:'publish'},documents:[]}).checked,0);
  assert.throws(()=>audit({landing:{}}),TypeError);
});
