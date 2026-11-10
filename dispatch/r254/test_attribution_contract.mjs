import test from 'node:test';
import assert from 'node:assert/strict';
import {validateSocialLanding,validateEmailGuideLink,evaluateSignupEvidence,reportCommercialKPI} from './attribution_contract.mjs';
const social='https://finalvestige.com/focus/?utm_source=tiktok&utm_medium=organic_social&utm_campaign=mind_pilot_2026_11&utm_content=tk_mind_0001';
const guide='https://finalvestige.com/mind/zen12-guide/?utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026_11&utm_content=issue03_zen12_guide';
const approval={guideLiveAndEditoriallyApproved:true,partnerEmailPermissionVerified:true,founderApprovedFinalCampaign:true};
test('canonical #820 social URL is syntax only',()=>{
  const r=validateSocialLanding(social);assert.equal(r.ok,true);
  assert.match(r.classification,/NOT_TRAFFIC_VERIFIED/);
});
const edits=[
 ['agent not platform','utm_source','grok'],['video not organic_social','utm_medium','video'],
 ['wrong platform','utm_source','threads'],['wrong topic','utm_campaign','vanity_pilot_2026_11'],
 ['bad month','utm_campaign','mind_pilot_2026_13'],['short asset','utm_content','x'],
 ['empty asset','utm_content',''],['extra ID','utm_content','a@b.com'],
 ['paid source masquerade','utm_medium','paid_social']
];
for(const [title,key,val] of edits)
  test('reject '+title,()=>{
    const u=new URL(social);u.searchParams.set(key,val);
    assert.equal(validateSocialLanding(u.href).ok,false);
  });
for(const [title,url] of [
 ['PII field',social+'&email=some%40example.com'],
 ['duplicate source',social+'&utm_source=youtube'],
 ['external origin',social.replace('finalvestige.com','bad.example')],
 ['http only',social.replace('https:','http:')],
 ['unsupported route',social.replace('/focus/','/commerce/')],
 ['fragment',social+'#private'],
])
  test('reject '+title,()=>assert.equal(validateSocialLanding(url).ok,false));
test('commercial CTA held with missing merchant proof',()=>{
 assert.equal(validateEmailGuideLink(guide).ok,false);
 assert.equal(validateEmailGuideLink(guide,{guideLiveAndEditoriallyApproved:true}).ok,false);
});
test('even hypothetical all-true attestations are not send authorization',()=>{
 const r=validateEmailGuideLink(guide,approval);
 assert.equal(r.ok,true);assert.match(r.classification,/NOT_SEND_AUTHORIZATION/);
});
for(const url of [
 guide.replace('utm_source=dispatch','utm_source=affiliate'),
 guide.replace('utm_campaign=dispatch_pilot_2026_11','utm_campaign=dispatch_pilot_2026'),
 guide.replace('utm_content=issue03_zen12_guide','utm_content=x'),
 guide+'&subscriber_id=0123',
 guide.replace('zen12-guide','store')
])test('reject misrouted offer guide',()=>assert.equal(validateEmailGuideLink(url,approval).ok,false));
for(const item of [
 {gift_ui_shown:true},{focus_pdf_click:true},{signup_form_submitted:true},
 {providerSubscriptionStatus:'Subscribed',gift_ui_shown:true},
 {providerSubscriptionStatus:'Subscribed',providerConfirmedTransition:true,
  consentForDispatchVerified:true,deduplicatedProviderTransition:true}
])test('UI status cannot become confirmed_signup or sale',()=>{
 const r=evaluateSignupEvidence(item);
 assert.equal(r.confirmed_signup,false);assert.equal(r.mayEmail,false);
 assert.equal(r.verifiedPaidSale,false);
});
test('authenticated hypothetical provider transition remains unsent',()=>{
 const r=evaluateSignupEvidence({providerSubscriptionStatus:'Subscribed',
 providerConfirmedTransition:true,consentForDispatchVerified:true,
 deduplicatedProviderTransition:true,providerSourceAuthenticated:true});
 assert.equal(r.confirmed_signup,true);assert.equal(r.mayEmail,false);
});
for(const item of [
 {},{qualifiedHumanSessions:250,netRevenueCents:12500,cohortDays:7},
 {qualifiedHumanSessions:0,netRevenueCents:12500,cohortDays:7,
  settlementIndependentlyAuthenticated:true,refundsAndFeesReconciled:true,qualifiedSessionSourceVerified:true},
 {qualifiedHumanSessions:250,netRevenueCents:12500,cohortDays:60,
  settlementIndependentlyAuthenticated:true,refundsAndFeesReconciled:true,qualifiedSessionSourceVerified:true}
])test('no fictional monetization KPI',()=>assert.equal(reportCommercialKPI(item).status,'NOT_COMPUTABLE'));
test('hypothetical complete evidence permits provisional arithmetic only',()=>{
 const r=reportCommercialKPI({qualifiedHumanSessions:250,netRevenueCents:12500,cohortDays:7,
 settlementIndependentlyAuthenticated:true,refundsAndFeesReconciled:true,qualifiedSessionSourceVerified:true});
 assert.equal(r.value,500);assert.equal(r.status,'PROVISIONAL_CALCULATION_ONLY');
});
