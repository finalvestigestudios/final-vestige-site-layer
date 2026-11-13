'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {review, GATES} = require('./non_sending_decision_audit.cjs');
const original = JSON.parse(fs.readFileSync(path.join(__dirname,'../campaign-2026-mind/manifest.json'),'utf8'));
const ledger = JSON.parse(fs.readFileSync(path.join(__dirname,'SIX_ISSUE_DECISION_LEDGER.json'),'utf8'));
const change = (fn) => {const a=JSON.parse(JSON.stringify(original)), b=JSON.parse(JSON.stringify(ledger)); fn(a,b); return review(a,b)};
let passes=0;function check(label, outcome) {assert.ok(typeof outcome==='function'?outcome():outcome,label);passes++;}
const baseline=review(original,ledger);
check('baseline never sends',baseline.send_allowed===false&&baseline.release_status==='HOLD_UNSENT');
check('original issue slots 4/2',baseline.editorial_slots===4&&baseline.commercial_slots===2);
check('no false active source errors',baseline.problems.length===0);
check('duplicate first two CTAs visible',baseline.improvements.includes('01_02_same_destination'));
check('redundant issue six CTA visible',baseline.improvements.includes('06_repeats_acquisition_cta'));
check('Apollo clock issue visible',baseline.improvements.includes('04_define_clock_endpoints_before_subject'));
check('generic hypnosis offer visible',baseline.improvements.includes('05_identify_specific_total_focus_offer'));
check('overlapping count never added',baseline.limitations.includes('newsletter_status_counts_overlap'));
check('different follower channels not recipients',baseline.independently_verified_eligible_audience===null);
check('commercial outcome not computable',baseline.realized_net_revenue_per_1000_qualified_sessions===null);
const cases=[
['wrong original id',(a)=>a.id='not-the-original','original_master_identity_invalid'],
['wrong master SHA',(_,b)=>b.original_master_sha='deadbeef','original_commit_identity_invalid'],
['scheduled state',(a)=>a.status='SCHEDULED','master_not_draft_unsent'],
['seventh issue',(a)=>a.issues.push({...a.issues[0],number:7}),'campaign_must_have_six'],
['duplicate issue',(a)=>a.issues[1].number=1,'duplicate_or_unexpected_issue'],
['wrong mix',(a)=>a.mix.editorial=5,'original_mix_must_be_four_two'],
['commercial misclassified',(a)=>a.issues[2].kind='editorial','allocation_drift_3'],
['changed subject',(a)=>a.issues[3].subject='Deceptive title','source_drift_4'],
['live publication',(a)=>a.issues[0].publish_state='publish','active_publication_1'],
['direct affiliate merchant url',(a)=>a.issues[2].merchant_affiliate_url='https://example.invalid/earning','unexpected_merchant_link_3'],
['unapproved alternative',(_,b)=>b.issues[0].alternative_status='ADOPTED','unapproved_alternative_1'],
['live guide without merchant proof',(a)=>a.issues[2].editorial_cta='https://finalvestige.com/mind/','source_drift_3'],
['external editorial CTA',(a,b)=>{a.issues[0].editorial_cta='https://example.org/';b.issues[0].original_cta='https://example.org/'},'editorial_cta_not_first_party_1'],
['merchant hold removed',(_,b)=>b.issues[4].issue_state='HOLD_UNSENT','merchant_hold_missing_5'],
['send flag changed',(_,b)=>b.policy.send_allowed=true,'send_flag_not_explicit_hold'],
['email auto publish enabled',(_,b)=>b.policy.auto_email_new_posts=true,'send_flag_not_explicit_hold'],
['audience invented',(_,b)=>b.audience.eligible_recipients=3,'fabricated_recipient_truth'],
['welcome invented',(_,b)=>b.audience.welcome_delivered=3,'fabricated_recipient_truth'],
['attributed subscriber invented',(_,b)=>b.audience.confirmed_new_signups_attributed=1,'fabricated_recipient_truth'],
['net sales invented',(_,b)=>b.realized_net_revenue_per_1000_qualified_sessions=99,'fabricated_revenue_metric'],
];
for(const [name,mutate,code] of cases){const r=change(mutate);check(name+' rejected',r.problems.includes(code)&&!r.send_allowed)}
for(const gate of GATES) {const r=change((_,b)=>b.policy[gate]=true);check('attestation '+gate+' not forged',r.problems.includes('unattested_or_unsafe_flag_'+gate))}
check('even unsafe all-attested never sends',change((_,b)=>{for(const k of GATES)b.policy[k]=true;b.policy.send_allowed=true}).send_allowed===false);
console.log('R333 exact-source non-sending QA: '+passes+'/'+passes+' PASS');
