'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {inspect,pathOnly,linksFromMarkup} = require('./related_story_permalink_guard.cjs');
const origin='https://finalvestige.com';
const post34={id:34,slug:'the-morning-san-francisco-lost-its-water',status:'publish',url:origin+'/2026/08/16/the-morning-san-francisco-lost-its-water/'};
const post38={id:38,slug:'the-cisterns-beneath-san-francisco',status:'publish',url:origin+'/2026/08/16/the-cisterns-beneath-san-francisco/'};
const base=()=>({site_origin:origin,posts:[{...post34},{...post38}],published_page_paths:['/focus/','/dispatch/'],articles:[{id:34,title:'San Francisco Water',links:['/the-cisterns-beneath-san-francisco/']},{id:38,title:'Cisterns',links:['/the-morning-san-francisco-lost-its-water/']}]});

test('authenticated snapshot produces two specific REVIEW records',()=>{
 const snapshot=JSON.parse(fs.readFileSync(path.join(__dirname,'wp_readonly_20261030_related_links.json'),'utf8'));
 const r=inspect(snapshot);
 assert.equal(r.status,'REVIEW');assert.equal(r.reviewed_articles,2);assert.equal(r.findings.length,2);
 assert.deepEqual(r.findings.map(x=>x.source_id).sort((a,b)=>a-b),[34,38]);
 assert.equal(r.findings[0].severity,'REVIEW');
});
test('both dated canonical links are accepted',()=>{
 const s=base();s.articles[0].links=[post38.url];s.articles[1].links=[post34.url];
 assert.equal(inspect(s).findings.length,0);
});
test('external domains are ignored',()=>{const s=base();s.articles[0].links=['https://not-finalvestige.com/the-cisterns-beneath-san-francisco/'];s.articles.splice(1,1);assert.equal(inspect(s).findings.length,0);});
test('unpublished post slugs are not offered as canonical matches',()=>{const s=base();s.posts[1].status='draft';s.articles.splice(1,1);assert.equal(inspect(s).findings.length,0);});
test('published page collision suppresses ambiguous review',()=>{const s=base();s.published_page_paths.push('/the-cisterns-beneath-san-francisco/');s.articles.splice(1,1);assert.equal(inspect(s).findings.length,0);});
test('unrelated root slug is ignored',()=>{const s=base();s.articles=[{id:7,links:['/nonexistent-route/']}];assert.equal(inspect(s).findings.length,0);});
test('fragments and query strings do not alter canonical comparison',()=>{const s=base();s.articles=[{id:34,links:['/the-cisterns-beneath-san-francisco/?x=1#sources']}];assert.equal(inspect(s).findings.length,1);});
test('same-site HTTP and HTTPS references are considered but no redirect status is asserted',()=>{const s=base();s.articles=[{id:34,links:['http://finalvestige.com/the-cisterns-beneath-san-francisco/']}];const r=inspect(s);assert.equal(r.findings.length,1);assert.match(r.note,/not a browser HTTP-status test/);});
test('path extractor rejects dangerous schemes',()=>{for(const value of ['javascript:alert(1)','data:text/html,hi','mailto:team@example.com'])assert.equal(pathOnly(value,origin),null);});
test('relative and absolute URL paths normalize trailing slash',()=>{assert.equal(pathOnly('/focus/',origin),'/focus');assert.equal(pathOnly('https://finalvestige.com/focus/?s=1',origin),'/focus');});
test('href extractor recognizes single and double quoted markup',()=>{assert.deepEqual(linksFromMarkup('<a href="/a/">A</a><a href=\'/b/\'>B</a>'),['/a/','/b/']);});
test('markup input produces the same mismatch as explicit links',()=>{const s=base();s.articles=[{id:34,markup:'<a class="more" href="/the-cisterns-beneath-san-francisco/">Read</a>'}];assert.equal(inspect(s).findings.length,1);});
test('missing and malformed snapshot data is rejected',()=>{assert.throws(()=>inspect({}),TypeError);assert.throws(()=>inspect({...base(),articles:undefined}),TypeError);});
test('does not treat offsite first-party lookalike or in-page anchor as defect',()=>{const s=base();s.articles=[{id:34,links:['https://finalvestige.com.evil.example/the-cisterns-beneath-san-francisco/','#subscribe-blog']}];assert.equal(inspect(s).findings.length,0);});
test('check is deterministic and leaves source snapshot unchanged',()=>{const s=base();const before=JSON.stringify(s);assert.deepEqual(inspect(s),inspect(s));assert.equal(JSON.stringify(s),before);});
