import test from 'node:test';
import assert from 'node:assert/strict';
import {checkOfferScope,SEND_ENABLED,PILOT,PROOF_KEYS} from './offer_scope_gate.mjs';
const manifest={issues:[
 {number:1,kind:'editorial'},{number:2,kind:'editorial'},
 {number:3,kind:'commercial-review-pending',editorial_cta:PILOT[3].token,merchant_affiliate_url:null,publish_state:'hold'},
 {number:4,kind:'editorial'},
 {number:5,kind:'commercial-review-pending',editorial_cta:PILOT[5].token,merchant_affiliate_url:null,publish_state:'hold'},
 {number:6,kind:'editorial'}
]};
const p=()=>Object.fromEntries(PROOF_KEYS.map(k=>[k,{verified:true,evidence_ref:'opaque-proof-'+k,source_type:'owner_authenticated'}]));
const verify=(n,s,x={},m=manifest)=>checkOfferScope(m,n,s,x);
test('send pathway permanently absent',()=>assert.equal(SEND_ENABLED,false));
test('unknown proof stays on hold',()=>assert.equal(verify(3,{family:'Zen12',sku:'Zen12 levels'}).review_ready,false));
test('cannot borrow Limitless Labs authorization',()=>assert.ok(verify(3,{family:'Zen12',sku:'Zen12 levels'},{...p(),email_channel_permission:{verified:true,evidence_ref:'limitlesslabs-swipe',source_type:'seller_catalog'}}).issues.includes('MISSING_PROOF_EMAIL_CHANNEL_PERMISSION')));
test('wrong merchant family is rejected',()=>assert.ok(verify(5,{family:'Total Focus',sku:'Total Focus'},p()).issues.includes('WRONG_MERCHANT_PRODUCT_FAMILY')));
test('Total Focus requires parent catalog and scope approval',()=>assert.ok(verify(5,{family:'Hypnosis Live',sku:'Total Focus'},p()).issues.includes('CHILD_SKU_IS_NOT_EQUIVALENT_TO_CATALOG')));
test('Total Focus without founder scope approval is rejected',()=>assert.ok(verify(5,{family:'Hypnosis Live',sku:'Total Focus',scope:'specific_child_sku'},{...p(),founder_scope_approval:{verified:false,evidence_ref:'pending-approval',source_type:'owner_authenticated'}}).issues.includes('CHILD_SKU_REQUIRES_FOUNDER_APPROVAL')));
test('valid synthetic total focus proof is review only',()=>{let r=verify(5,{family:'Hypnosis Live',sku:'Total Focus',scope:'specific_child_sku'},p());assert.equal(r.review_ready,true);assert.equal(r.status,'HOLD_UNSENT');assert.equal(r.send_enabled,false)});
test('Zen12 valid synthetic proofs still cannot send',()=>{let r=verify(3,{family:'Zen12',sku:'Zen12 levels'},p());assert.equal(r.review_ready,true);assert.equal(r.send_enabled,false)});
test('activated merchant link is blocked',()=>assert.ok(verify(3,{family:'Zen12',sku:'Zen12 levels',active_merchant_link:true},p()).issues.includes('LIVE_LINKS_NOT_AUTHORIZED_IN_SOURCE_DRAFT')));
test('activated guide link is blocked',()=>assert.ok(verify(5,{family:'Hypnosis Live',sku:'Hypnosis Live catalog',active_guide_link:true},p()).issues.includes('LIVE_LINKS_NOT_AUTHORIZED_IN_SOURCE_DRAFT')));
test('current seller price cannot silently become newsletter claim',()=>assert.ok(verify(5,{family:'Hypnosis Live',sku:'Total Focus',price_to_publish:'$24.44'},p()).issues.includes('UNAPPROVED_PUBLIC_PRICE_OR_REFUND')));
test('refund language cannot silently become newsletter promise',()=>assert.ok(verify(5,{family:'Hypnosis Live',sku:'Total Focus',refund_to_publish:'14 days'},p()).issues.includes('UNAPPROVED_PUBLIC_PRICE_OR_REFUND')));
test('six campaign allocation enforced',()=>assert.ok(verify(3,{family:'Zen12',sku:'Zen12 levels'},p(),{issues:manifest.issues.slice(0,5)}).issues.includes('CANONICAL_SIX_ISSUE_4_TO_2_MIX_CHANGED')));
test('slot reassignment blocked',()=>{let changed=structuredClone(manifest);changed.issues[2].kind='editorial';changed.issues[3].kind='commercial-review-pending';assert.ok(verify(3,{family:'Zen12',sku:'Zen12 levels'},p(),changed).issues.includes('COMMERCIAL_SLOT_REASSIGNED'))});
test('canonical placeholder is immutable',()=>{let changed=structuredClone(manifest);changed.issues[4].editorial_cta='https://example.org/';assert.ok(verify(5,{family:'Hypnosis Live',sku:'Hypnosis Live catalog'},p(),changed).issues.includes('CANONICAL_UNSENT_DESTINATION_CHANGED'))});
test('catalog screenshots are not partner rights',()=>assert.equal(verify(3,{family:'Zen12',sku:'Zen12 levels'},Object.fromEntries(PROOF_KEYS.map(k=>[k,{verified:true,evidence_ref:'catalog-page-'+k,source_type:'seller_catalog'}]))).review_ready,false));
test('absence of postal evidence fails',()=>{let x=p();delete x.publisher_postal_footer;assert.ok(verify(3,{family:'Zen12',sku:'Zen12 levels'},x).issues.includes('MISSING_PROOF_PUBLISHER_POSTAL_FOOTER'))});
test('absence of eligible audience fails',()=>{let x=p();delete x.filtered_eligible_recipients;assert.ok(verify(3,{family:'Zen12',sku:'Zen12 levels'},x).issues.includes('MISSING_PROOF_FILTERED_ELIGIBLE_RECIPIENTS'))});
test('all proofs require external owner authenticity review',()=>{let x=p();x.issued_earning_link={verified:true,evidence_ref:'x',source_type:'owner_authenticated'};assert.equal(verify(3,{family:'Zen12',sku:'Zen12 levels'},x).review_ready,false)});
