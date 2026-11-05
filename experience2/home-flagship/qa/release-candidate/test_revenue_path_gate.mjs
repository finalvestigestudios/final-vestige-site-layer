import test from 'node:test';
import assert from 'node:assert/strict';
import {extractLinks,classifyLink,commercialRouteReceipt} from './revenue_path_gate.mjs';
const a=(url,label)=>'<a href="'+url+'">'+label+'</a>';
const H=a('/focus/','Get the free Fieldbook')+a('#fv-hf-evidence','Read archive');
const C=a('/focus/','Free Fieldbook')+a('https://www.awin1.com/cread.php?awinmid=5&amp;awinaffid=7','View this navigation tool');
const F='<h1>Seven Day Focus Fieldbook</h1><div class="wp-block-jetpack-subscriptions"></div>';
test('public site collection is classified lead + affiliate not paid',()=>{
 const r=commercialRouteReceipt(H,C,F);
 assert.equal(r.status,'OWNED_REVENUE_ROUTE_NOT_EXPOSED');
 assert.equal(r.flags.published_home_to_focus,true);
 assert.equal(r.flags.affiliate_outbound_present,true);
 assert.equal(r.flags.owned_paid_catalog_destination_present,false);
 assert.equal(r.commercialEvidence.netRevenuePer1000QualifiedSessions,'NOT_MEASURABLE');
});
test('approved Payhip URL marks merchant verification required, never sale',()=>{
 const r=commercialRouteReceipt(H,C+a('https://payhip.com/b/ABC','Buy the dossier'),F);
 assert.equal(r.status,'MERCHANT_CHECK_REQUIRED');
 assert.equal(r.commercialEvidence.paidOrders,'NOT_CHECKED');
 assert.deepEqual(r.distinctOwnedCheckoutDestinations,['payhip.com']);
});
test('false positive: affiliate outbound cannot be paid order',()=>{
 assert.equal(classifyLink('https://www.awin1.com/cread.php?awinmid=10').type,'affiliate_outbound');
});
test('false positive: affiliate query with payhip text cannot be owned sale',()=>{
 assert.equal(classifyLink('https://www.awin1.com/cread.php?ued=https%3A%2F%2Fpayhip.com%2Fb%2FABC').type,'affiliate_outbound');
});
test('false positive: deceptive merchant hostname rejected',()=>{
 assert.equal(classifyLink('https://payhip.com.evil.test/b/abc').type,'other_external');
});
test('HTML entity decoded before URL parsing',()=>{
 const l=extractLinks(a('https://www.awin1.com/cread.php?x=1&amp;y=2','Affiliate'));
 assert.equal(l[0].href,'https://www.awin1.com/cread.php?x=1&y=2');
});
test('discovered link labels preserve nonempty context',()=>{
 assert.deepEqual(extractLinks(a('/focus/','<strong>Get Focus Fieldbook</strong>'))[0],{
  href:'/focus/',label:'Get Focus Fieldbook',hasDisclosure:false});
});
test('broken focus link fails source path',()=>{
 assert.equal(commercialRouteReceipt(a('/wrong/','Free Fieldbook'),C,F).flags.published_home_to_focus,false);
});
test('missing focus form does not become confirmed subscription',()=>{
 assert.equal(commercialRouteReceipt(H,C,'<h1>Seven Day Focus Fieldbook</h1>').flags.focus_landing_form_markup_present,false);
});
test('missing product name cannot be passed by form alone',()=>{
 assert.equal(commercialRouteReceipt(H,C,'<div class="wp-block-jetpack-subscriptions"></div>').flags.focus_landing_source_offer_present,false);
});
test('javascript links, data URLs and malformed inputs cannot be revenue paths',()=>{
 for(const x of ['javascript:alert(1)','data:text/html,hi','{{invalid}}']){
  assert.notEqual(classifyLink(x).type,'potential_owned_checkout');
 }
});
test('merchant links on homepage only do not prove Collection monetization',()=>{
 const r=commercialRouteReceipt(H+a('https://payhip.com/b/x','Paid'),C,F);
 assert.equal(r.flags.owned_paid_catalog_destination_present,false);
});
test('empty collection fails closed',()=>{
 assert.equal(commercialRouteReceipt(H,'',F).status,'OWNED_REVENUE_ROUTE_NOT_EXPOSED');
});
test('large inputs fail bounded',()=>{
 assert.throws(()=>commercialRouteReceipt('x'.repeat(2_000_001),C,F));
});
