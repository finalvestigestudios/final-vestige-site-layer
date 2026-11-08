import test from 'node:test';
import assert from 'node:assert/strict';
import {reviewSubscriberPromise,verifyOriginalCampaign,draftEmailAttribution} from './audit.mjs';

const status=()=>({origin:'connected_wordpress_jetpack_newsletter_status',
  as_of:'2026-11-04T11:31:36Z',subscribers:{total:2,confirmed:2,unconfirmed:2,suppressed:0},
  recent_sends:[{status:'never_sent_opted_out',dispatched_at:null}]});
const settings=()=>({origin:'connected_wordpress_jetpack_newsletter_settings',
  as_of:'2026-11-04T11:31:39Z',email_new_posts_by_default:false,
  email_content_format:'excerpt',
  welcome_message:"You'll hear from us when there's a new investigation."});
const pages=()=>({origin:'connected_wordpress_published_content',
  focus:'Occasionally we may recommend resources that earn us a commission.',
  dispatch:'Get new investigations by email when we publish them. Unsubscribe anytime.'});
const snap=()=>({status:status(),settings:settings(),pages:pages()});
const url={
  1:'https://finalvestige.com/the-missing-caption/',
  2:'https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/',
  4:'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/',
  6:'https://finalvestige.com/focus/'
};
const published=()=>Object.entries(url).map(([edition,link])=>({
  edition:Number(edition),url:link,status:'publish',source:'connected_wordpress_published_destination'
}));
const manifest=()=>({status:'DRAFT_UNSENT_NO_SCHEDULING',
  issues:Array.from({length:6},(_,i)=>{const n=i+1;return {
    number:n,kind:(n===3||n===5)?'commercial-review-pending':'editorial',
    editorial_cta:url[n]??'[[APPROVED_WARMUP_REQUIRED]]',
    merchant_affiliate_url:null,publish_state:'hold'
  };})
});

test('live subscriber counts do NOT add to four',()=>{
 const a=reviewSubscriberPromise(snap());
 assert.equal(a.counts.newsletter_total,2);
 assert.equal(a.counts.unconfirmed_excluded,2);
 assert.equal(a.email_reachable,null);
});
test('new-post default remains off',()=>assert.equal(reviewSubscriberPromise(snap()).automatic_new_posts,false));
test('checked opted-out non-sends are not delivery',()=>assert.equal(reviewSubscriberPromise(snap()).recent_send_recorded,false));
test('truth-in-promise manual-send review flagged',()=>assert.ok(reviewSubscriberPromise(snap()).blockers.includes('publisher_promise_needs_manual_send_expectation_review')));
test('dispatch commercial disclosure gap detected',()=>assert.equal(reviewSubscriberPromise(snap()).consent_parity,'dispatch_copy_not_equivalent'));
test('configuring PDF in welcome is not receiving PDF',()=>assert.equal(reviewSubscriberPromise(snap()).welcome_delivered,null));
test('missing actual transport preview always held',()=>assert.ok(reviewSubscriberPromise(snap()).blockers.includes('native_preheader_and_excerpt_received_rendering_unverified')));
test('legal footer unverified even for editorial send',()=>assert.ok(reviewSubscriberPromise(snap()).blockers.includes('commercial_postal_address_and_functional_optout_unverified')));
test('invalid authority rejected',()=>{const a=snap();a.status.origin='social_click';assert.equal(reviewSubscriberPromise(a).state,'INVALID_EVIDENCE');});
test('missing authoritative read rejected',()=>assert.equal(reviewSubscriberPromise({}).sending_authorized,false));
test('invalid date rejected',()=>{const a=snap();a.status.as_of='yesterday';assert.equal(reviewSubscriberPromise(a).state,'INVALID_EVIDENCE');});
test('negative count rejected',()=>{const a=snap();a.status.subscribers.total=-1;assert.equal(reviewSubscriberPromise(a).state,'INVALID_EVIDENCE');});
test('confirmed greater than total rejected',()=>{const a=snap();a.status.subscribers.confirmed=5;assert.equal(reviewSubscriberPromise(a).state,'INVALID_EVIDENCE');});
test('word-heavy content cannot be injected',()=>{const a=snap();a.pages.dispatch='x'.repeat(10001);assert.equal(reviewSubscriberPromise(a).state,'INVALID_EVIDENCE');});
test('unexpected auto-send toggle triggers manual review',()=>{const a=snap();a.settings.email_new_posts_by_default=true;assert.ok(reviewSubscriberPromise(a).blockers.includes('automatic_new_post_default_not_proven_off'));assert.equal(reviewSubscriberPromise(a).automatic_new_posts,true);});
test('transport full-mode drift triggers re-review',()=>{const a=snap();a.settings.email_content_format='full';assert.ok(reviewSubscriberPromise(a).blockers.includes('native_transport_contract_changed_review_again'));});
test('proof of welcome can change only welcome field, never enable send',()=>{
 const a=snap();a.received={origin:'independent_authorized_mime_review',kind:'fieldbook_welcome',result:'received_with_pdf_link_and_download_verified'};
 const r=reviewSubscriberPromise(a);assert.equal(r.welcome_delivered,true);assert.equal(r.sending_authorized,false);
});
test('fake proof source cannot claim received',()=>{const a=snap();a.received={origin:'configured_wordpress_settings',kind:'fieldbook_welcome',result:'received_with_pdf_link_and_download_verified'};assert.equal(reviewSubscriberPromise(a).welcome_delivered,null);});
test('promise softened does not resolve legal holds',()=>{const a=snap();a.pages.dispatch='Subscribe for carefully selected updates and research.';a.settings.welcome_message='Thanks for joining';const r=reviewSubscriberPromise(a);assert.equal(r.sending_authorized,false);});
test('simple consent parity copy does not imply merchant approval',()=>{const a=snap();a.pages.dispatch+=' We may earn a commission from recommendations.';assert.equal(reviewSubscriberPromise(a).sending_authorized,false);});
test('canonical 4:2 preserved and commercial items held',()=>{const r=verifyOriginalCampaign(manifest(),published());assert.equal(r.valid,true);assert.deepEqual(r.allocation,{editorial:4,commercial_reserved:2});assert.equal(r.issue_readiness.filter(x=>x.verified_cta).length,4);assert.equal(r.issue_readiness.filter(x=>x.state==='HOLD_MERCHANT').length,2);assert.equal(r.sending_authorized,false);});
test('published CTA proof cannot activate sending',()=>assert.equal(verifyOriginalCampaign(manifest(),published()).sending_authorized,false));
test('missing published route blocks its own edition',()=>assert.equal(verifyOriginalCampaign(manifest(),published().slice(1)).issue_readiness[0].verified_cta,false));
test('untrusted destination ignored',()=>{const p=published();p[0].source='grok_guess';assert.equal(verifyOriginalCampaign(manifest(),p).issue_readiness[0].verified_cta,false);});
test('unpublished destination ignored',()=>{const p=published();p[1].status='draft';assert.equal(verifyOriginalCampaign(manifest(),p).issue_readiness[1].verified_cta,false);});
test('external merchant link never considered approved published route',()=>{const p=published();p[0].url='https://zen12.com/hnp';assert.equal(verifyOriginalCampaign(manifest(),p).issue_readiness[0].verified_cta,false);});
test('missing evidence list invalid manifest',()=>assert.equal(verifyOriginalCampaign(manifest(),null).valid,false));
test('merchant affiliate URL mutation rejected',()=>{const m=manifest();m.issues[2].merchant_affiliate_url='https://zen12.com/hnp';assert.equal(verifyOriginalCampaign(m,published()).reason,'campaign_allocation_or_activation_drift');});
test('draft to publish drift rejected',()=>{const m=manifest();m.issues[0].publish_state='publish';assert.equal(verifyOriginalCampaign(m,published()).valid,false);});
test('missing edition rejected',()=>{const m=manifest();m.issues.pop();assert.equal(verifyOriginalCampaign(m,published()).valid,false);});
test('commercial allocation swap rejected',()=>{const m=manifest();m.issues[0].kind='commercial-review-pending';assert.equal(verifyOriginalCampaign(m,published()).valid,false);});
test('only published first-party editorial CTA gets suggested UTM',()=>{
const r=draftEmailAttribution({edition:4,destination:url[4],campaign:'dispatch_pilot_2026_11'});
assert.equal(r.status,'UNSENT_ATTRIBUTION_DRAFT_ONLY');
const parsed=new URL(r.url);assert.equal(parsed.searchParams.get('utm_source'),'dispatch');
assert.equal(parsed.searchParams.get('utm_medium'),'email');
assert.equal(parsed.searchParams.get('utm_content'),'issue04');
assert.equal(r.clicked,null);assert.equal(r.paid_order,null);assert.equal(r.net_revenue,null);
});
test('commercial 03/05 never get earning link or fake UTM route',()=>{
for(const edition of [3,5])assert.equal(draftEmailAttribution({edition,destination:'https://zen12.com/hnp',campaign:'dispatch_pilot_2026_11'}).url,null);
});
test('external affiliate landing refused',()=>assert.equal(draftEmailAttribution({edition:1,destination:'https://inspire3.com/',campaign:'dispatch_pilot_2026_11'}).url,null));
test('wrong campaign refused',()=>assert.equal(draftEmailAttribution({edition:1,destination:url[1],campaign:'not_a_campaign'}).url,null));
test('active personalized query URL refused',()=>assert.equal(draftEmailAttribution({edition:1,destination:url[1]+'?email=a@example.com',campaign:'dispatch_pilot_2026_11'}).url,null));
