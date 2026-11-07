
'use strict';
// Run in native Node: node --test dispatch/r187/test_r187.cjs
const t=require('node:test'), a=require('node:assert/strict'),g=require('./proof_gate.cjs');
t.test('3 total / 3 confirmed / 2 pending is NONADDITIVE',()=>{const s=g.summary({total:3,confirmed:3,unconfirmed:2,suppressed:0});a.equal(s.email_eligible,null);a.equal(s.pending,2)});
t.test('impossible counters rejected',()=>a.throws(()=>g.summary({total:2,confirmed:3,unconfirmed:2,suppressed:0})));
t.test('negative counters rejected',()=>a.throws(()=>g.summary({total:3,confirmed:3,unconfirmed:-2,suppressed:0})));
t.test('PII fields forbidden',()=>a.throws(()=>g.summary({total:3,confirmed:3,unconfirmed:2,suppressed:0,email:'private@example.test'})));
t.test('no email audience without receipt',()=>a.equal(g.emailEligibleAggregate({count:3}).count,null));
t.test('attested synthetic provider aggregate',()=>a.equal(g.emailEligibleAggregate({source:'jetpack_subscribers_filter',status:'Subscribed',count:2,independently_attested:true,private_receipt:'internal:wp/receipt'}).count,2));
t.test('fake CSS or query never confirms signup',()=>a.equal(g.confirmedSignup({query:'subscribe=anything',class:'is-subscriber'}),false));
t.test('unattested provider not confirmed',()=>a.equal(g.confirmedSignup({source:'jetpack',status:'Subscribed',consent_scope:'Dispatch',provider_confirmed:true,receipt_independently_attested:false,opaque_key:'subref_12345678',private_receipt:'internal:wp/receipt'}),false));
t.test('synthetic repeat signup deduplicated',()=>{const e={source:'jetpack',status:'Subscribed',consent_scope:'Dispatch',provider_confirmed:true,receipt_independently_attested:true,opaque_key:'subref_12345678',private_receipt:'internal:wp/receipt'};a.equal(g.uniqueConfirmed([e,{...e}]).count,1)});
t.test('no newsletter release by default',()=>a.equal(g.release({kind:'editorial'}).send,false));
t.test('merchant authorization is an independent hard stop',()=>{const s=Object.fromEntries(['founder_send_approval','eligible_recipients_attested','native_jetpack_preview_reviewed','fv_physical_postal_in_email','recipient_unsubscribe_verified','final_content_schedule_approved'].map(k=>[k,true]));a.equal(g.release({kind:'commercial',shared:s}).reason,'HOLD_MERCHANT')});
t.test('email attribution is not revenue',()=>a.equal(g.emailAttribution({utm_source:'jetpack',utm_medium:'email',utm_campaign:'dsp_03',utm_content:'issue_03',destination:'https://finalvestige.com/focus/'}).classification,'VISIT_OR_CLICK_NOT_PURCHASE'));
t.test('fake campaign rejected',()=>a.equal(g.emailAttribution({utm_source:'jetpack',utm_medium:'email',utm_campaign:'dsp_07',utm_content:'issue_07',destination:'https://finalvestige.com/focus/'}).accepted,false));
t.test('external merchant direct-link not a first-party CTA',()=>a.equal(g.emailAttribution({utm_source:'jetpack',utm_medium:'email',utm_campaign:'dsp_03',utm_content:'issue_03',destination:'https://merchant.example'}).accepted,false));
t.test('unknown settled evidence cannot compute revenue',()=>a.equal(g.revenuePerThousand({gross:100,refunds:0,fees:0,qualified_human_sessions:1000}),null));
t.test('zero human sessions not computable',()=>a.equal(g.revenuePerThousand({independently_reconciled:true,gross:100,refunds:0,fees:0,qualified_human_sessions:0}),null));
t.test('synthetic reconciled example arithmetic',()=>a.equal(g.revenuePerThousand({independently_reconciled:true,gross:100,refunds:20,fees:10,qualified_human_sessions:1000}),70));
