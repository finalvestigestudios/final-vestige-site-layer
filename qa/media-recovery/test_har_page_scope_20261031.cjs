'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {articlePath,scopeHarToArticle} = require('./har_page_scope_core.cjs');
const article = 'https://finalvestige.com/2026/08/18/they-painted-over-archimedes/';
const other = 'https://finalvestige.com/2026/08/18/other-article/';
const file = 'https://archimedespalimpsest.org/assets/img/imaging_x8.jpg';
const page=(id='p1',title=article)=>({id,title});
const doc=(id='p1',status=200,url=article,type='document',mime='text/html; charset=utf-8')=>({
 pageref:id,_resourceType:type,request:{method:'GET',url},
 response:{status,content:{mimeType:mime}}});
const img=(id='p1',status=404)=>({pageref:id,_resourceType:'image',request:{method:'GET',url:file},response:{status,content:{mimeType:'text/html'}}});
const H=(pages,entries)=>({log:{pages,entries}});
test('page match keeps only current article image requests',()=>{const r=scopeHarToArticle(H([page(),page('p2',other)],[doc(),img(),doc('p2',200,other),img('p2')]),article);assert.equal(r.ok,true);assert.equal(r.scoped_entries.length,2);assert.equal(r.excluded_unscoped_entries,2)});
test('missing pages rejects all image responses',()=>{const r=scopeHarToArticle({log:{entries:[doc(),img()]}},article);assert.equal(r.ok,false);assert.equal(r.reason,'MISSING_HAR_PAGE_METADATA');assert.deepEqual(r.scoped_entries,[])});
test('unrelated article rejects seemingly identical image URL',()=>{const r=scopeHarToArticle(H([page('p1',other)],[doc(),img()]),article);assert.equal(r.reason,'ARTICLE_PAGE_NOT_IN_HAR');assert.equal(r.scoped_entries.length,0)});
test('duplicate page IDs fail closed',()=>assert.equal(scopeHarToArticle(H([page(),page('p1',other)],[doc(),img()]),article).reason,'DUPLICATE_OR_INVALID_HAR_PAGE_IDS'));
test('two declared copies of same article fail closed',()=>assert.equal(scopeHarToArticle(H([page(),page('p2',article)],[doc(),img()]),article).reason,'AMBIGUOUS_ARTICLE_PAGES'));
test('document 403 is not successful navigation',()=>assert.equal(scopeHarToArticle(H([page()],[doc('p1',403),img()]),article).reason,'MATCHING_SUCCESSFUL_DOCUMENT_REQUEST_MISSING'));
test('document HTML content type required',()=>assert.equal(scopeHarToArticle(H([page()],[doc('p1',200,article,'document','image/png'),img()]),article).ok,false));
test('XHR 200 does not certify article navigation',()=>assert.equal(scopeHarToArticle(H([page()],[doc('p1',200,article,'xmlhttprequest'),img()]),article).ok,false));
test('document from another site does not certify declared article',()=>assert.equal(scopeHarToArticle(H([page()],[doc('p1',200,'https://evil.example/'),img()]),article).ok,false));
test('missing pageref does not get attached to image report',()=>{const e=img();delete e.pageref;const r=scopeHarToArticle(H([page()],[doc(),e]),article);assert.equal(r.ok,true);assert.equal(r.scoped_entries.length,1)});
test('URL tracking query ignored for article page identity',()=>assert.equal(scopeHarToArticle(H([page('p1',article+'?utm_source=mail')],[doc()]),article).ok,true));
test('articlePath enforces first-party HTTPS and no embedded credentials',()=>{assert.equal(articlePath('https://finalvestige.com/foo/?utm=1'),'https://finalvestige.com/foo');assert.equal(articlePath('http://finalvestige.com/foo/'),null);assert.equal(articlePath('https://user:pass@finalvestige.com/foo/'),null);assert.equal(articlePath('https://not-finalvestige.com/foo/'),null)});
test('invalid page ID rejected',()=>assert.equal(scopeHarToArticle(H([{id:0,title:article}],[doc()]),article).reason,'DUPLICATE_OR_INVALID_HAR_PAGE_IDS'));
test('valid final XHTML navigation permitted',()=>assert.equal(scopeHarToArticle(H([page()],[doc('p1',200,article,'Document','application/xhtml+xml')]),article).ok,true));

