'use strict';
const {test}=require('node:test'); const assert=require('node:assert/strict');
const {auditReaderContinuity,ATLAS,ARTICLE,BOARD}=require('./r140_reader_continuity_gate.cjs');
const fixture=()=>({
 atlas:{id:2017,slug:'apollo-1-evidence-atlas',status:'publish',link:ATLAS,content:'<main>'+'<a class="fv-ex2-button" href="'+ARTICLE+'">Read the full investigation</a>'+'<a href="'+BOARD+'">NASA Board</a>'+'<p>'+('Evidence '.repeat(30))+'</p></main>'},
 article:{id:434,slug:'the-hatch-opened-inward-apollo-1',status:'publish',link:ARTICLE,title:'The Hatch Opened Inward',content:'<main><p>'+('Hatch design '.repeat(25))+'</p><a href="'+BOARD+'">Apollo 204 Review Board</a></main>'}
});
const run=x=>auditReaderContinuity(x.atlas,x.article);
test('complete static Atlas to published article custody is SOURCE ONLY',()=>{let r=run(fixture()); assert.equal(r.source_gate,'SOURCE_LINK_CONTINUITY_ONLY'); assert.equal(r.findings.valid_reader_cta_count,1);assert.equal(r.findings.no_js_link_in_html,true);assert.equal(r.browser,'NOT_TESTED');assert.equal(r.release,'STAGING_HOLD');});
test('removing CTA is reported, never invents worksheet',()=>{let x=fixture();x.atlas.content=x.atlas.content.replace('Read the full investigation','Other link');let r=run(x);assert.ok(r.blockers.includes('READ_INVESTIGATION_CTA_NOT_ONE_VALID_STATIC_LINK'));assert.equal(r.next_action,null);});
test('duplicate named CTAs fail',()=>{let x=fixture();x.atlas.content+='<a href="'+ARTICLE+'">Read the full investigation</a>';assert.equal(run(x).findings.static_reader_cta_count,2);assert.equal(run(x).source_gate,'REVIEW_REQUIRED');});
test('deceptive destination does not pass',()=>{let x=fixture();x.atlas.content=x.atlas.content.replace(ARTICLE,'https://finalvestige.com.evil.example/');assert.equal(run(x).source_gate,'REVIEW_REQUIRED');});
test('query parameters are not silently accepted for unreviewed CTA',()=>{let x=fixture();x.atlas.content=x.atlas.content.replace(ARTICLE,ARTICLE+'?utm_source=unknown');assert.equal(run(x).source_gate,'REVIEW_REQUIRED');});
test('nonpublished target post fails',()=>{let x=fixture();x.article.status='draft';assert.ok(run(x).blockers.includes('ARTICLE_METADATA_UNVERIFIED'));});
test('fake article slug or ID fails',()=>{let x=fixture();x.article.id=555; assert.ok(run(x).blockers.includes('ARTICLE_METADATA_UNVERIFIED'));});
test('source custody fails when NASA Board missing from article',()=>{let x=fixture();x.article.content=x.article.content.replace(BOARD,'https://example.test/');assert.ok(run(x).blockers.includes('APOLLO_REVIEW_BOARD_CROSS_SOURCE_MISSING'));});
test('source custody fails when NASA Board missing from atlas',()=>{let x=fixture();x.atlas.content=x.atlas.content.replace(BOARD,'https://example.test/');assert.ok(run(x).blockers.includes('APOLLO_REVIEW_BOARD_CROSS_SOURCE_MISSING'));});
test('target blank forbidden on primary reader action',()=>{let x=fixture();x.atlas.content=x.atlas.content.replace('class="fv-ex2-button"','target="_blank" class="fv-ex2-button"');assert.equal(run(x).source_gate,'REVIEW_REQUIRED');});
test('hidden primary anchor cannot pass',()=>{let x=fixture();x.atlas.content=x.atlas.content.replace('class="fv-ex2-button"','aria-hidden="true" class="fv-ex2-button"');assert.equal(run(x).source_gate,'REVIEW_REQUIRED');});
test('inaccessible keyboard tabIndex cannot pass',()=>{let x=fixture();x.atlas.content=x.atlas.content.replace('class="fv-ex2-button"','tabindex="-1" class="fv-ex2-button"');assert.equal(run(x).source_gate,'REVIEW_REQUIRED');});
test('missing HTML fails safely',()=>{let r=auditReaderContinuity(null,{});assert.ok(r.blockers.includes('HTML_SOURCE_MISSING')); assert.equal(r.release,'STAGING_HOLD');});
test('no buyer emails, fake rights or caller-declared approvals appear in report',()=>{let x=fixture();x.atlas.customer_email='sensitive@example.test';let r=auditReaderContinuity(x.atlas,x.article,{paidOrder:true,mediaRights:true});assert.equal(r.paid_order,'NOT_OBSERVED');assert.equal(r.approved_to_publish,false);assert.ok(!JSON.stringify(r).includes('sensitive@example.test'));});
test('identical inputs produce identical evidence digests',()=>{let x=fixture();assert.deepEqual(run(x),run(x)); assert.match(run(x).source_pair.atlas_sha256,/^[0-9a-f]{64}$/);});
test('script-generated link is NOT a no-JS primary action',()=>{let x=fixture();x.atlas.content=x.atlas.content.replace('<a class="fv-ex2-button" href="'+ARTICLE+'">Read the full investigation</a>','<script>const s="<a class=\"fv-ex2-button\" href=\"'+ARTICLE+'\">Read the full investigation</a>";</script>');assert.equal(run(x).source_gate,'REVIEW_REQUIRED');});
