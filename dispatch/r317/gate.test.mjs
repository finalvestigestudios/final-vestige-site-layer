import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {TIERS,inspectTierClaims,audienceSnapshot,inspectRevenue,auditDraft,CANONICAL_ISSUE03_BLOB} from './gate.mjs';
const base=new URL('./',import.meta.url);
const read=p=>fs.readFileSync(new URL(p,base),'utf8');
const text=read('issue03-tier-review.txt');
const html=read('issue03-tier-review.html');
const manifest=JSON.parse(read('snapshot.json')).manifest;
test('tier chart is seller-accurate and Premium is full course',()=>{
 assert.deepEqual([TIERS.beginner.levels,TIERS.beginner.mp3s],[6,24]);
 assert.deepEqual([TIERS.premium.levels,TIERS.premium.mp3s],[12,48]);
 assert.deepEqual([TIERS.advanced.levels,TIERS.advanced.mp3s],[6,24]);
});
test('review copy does not assume all tiers contain 48 MP3s',()=>{
 assert.equal(inspectTierClaims(text).length,0);
 assert.equal(CANONICAL_ISSUE03_BLOB,'aeeef34efea0cc281f69901488e4501fea851245');
});
test('bad full-course and tier promises are flagged',()=>{
 assert.ok(inspectTierClaims('Zen12 includes 48 MP3s.').includes('UNQUALIFIED_FULL_PACKAGE'));
 assert.ok(inspectTierClaims('Beginner includes 48 MP3s.').includes('PARTIAL_TIER_MISDESCRIBED'));
 assert.ok(inspectTierClaims('Advanced includes all 12 levels.').includes('PARTIAL_TIER_MISDESCRIBED'));
 assert.ok(inspectTierClaims('Premium includes 24 MP3s.').includes('PREMIUM_MISDESCRIBED'));
});
test('unsupported efficacy and urgency flagged',()=>{
 assert.ok(inspectTierClaims('Clinically proven Zen12 delivers same as an hour of meditation.').includes('UNSUBSTANTIATED_EFFICACY'));
 assert.ok(inspectTierClaims('Zen12 special discount ends tonight').includes('UNVERIFIED_OFFER_OR_URGENCY'));
});
test('WP counts are overlapping aggregate not live delivery counts',()=>{
 const v=audienceSnapshot({total:3,confirmed:3,unconfirmed:2,suppressed:0,wpcom_followers:3,direct_email_followers:0});
 assert.equal(v.overlapping_status_counts,true);
 assert.equal(v.email_eligible_recipients,null);
 assert.equal(v.confirmed_signup_event_verified,false);
});
test('a zero direct-email follower statistic does not imply zero eligible WP.com followers',()=>{
 const v=audienceSnapshot({total:3,confirmed:3,unconfirmed:2,wpcom_followers:3,direct_email_followers:0});
 assert.equal(v.email_eligible_recipients,null);
});
test('revenue blocks on clicks, estimated orders and missing denominator',()=>{
 for(const r of [{},{qualified_human_sessions:100,settled_orders:2,gross_revenue:40,refunds:0,fees:2,orders_source:'CLICK_EVENTS',sessions_source:'FIRST_PARTY_RECONCILED',attribution_reconciled:true},{qualified_human_sessions:0,settled_orders:0,gross_revenue:0,refunds:0,fees:0,orders_source:'INDEPENDENT_SETTLEMENT',sessions_source:'FIRST_PARTY_RECONCILED',attribution_reconciled:true}])
 assert.equal(inspectRevenue(r).status,'NOT_COMPUTABLE');
});
test('even synthetic fully attributed economics are advisory only',()=>{
 const x=inspectRevenue({qualified_human_sessions:100,settled_orders:2,gross_revenue:40,refunds:4,fees:2,orders_source:'INDEPENDENT_SETTLEMENT',sessions_source:'FIRST_PARTY_RECONCILED',attribution_reconciled:true});
 assert.equal(x.status,'MODEL_ONLY_REQUIRES_REAL_WITNESS');
 assert.equal(x.net_revenue_per_1000,340);
});
test('all original issues preserved and review is never sendable',()=>{
 const snap=JSON.parse(read('snapshot.json'));
 const x=auditDraft({text,html,manifest:snap.manifest,snapshot:snap.wordpress});
 assert.deepEqual(x.issues,[]);assert.equal(x.send_allowed,false);
 assert.equal(x.merchant_link_allowed,false);
});
test('remove disclosure or activate CTA cannot make email sendable',()=>{
 const snap=JSON.parse(read('snapshot.json'));
 const noDisclosure=text.replace(/Commercial disclosure[^\n]+/,'');
 const x=auditDraft({text:noDisclosure,html,manifest:snap.manifest,snapshot:snap.wordpress});
 assert.ok(x.issues.includes('DISCLOSURE_MISSING'));assert.equal(x.send_allowed,false);
});
test('HTML review cannot contain script/form/affiliate ref parameter',()=>{
 assert.ok(!/<script|<form|<iframe/i.test(html));
 assert.ok(!/href\s*=\s*["'][^"']*(?:\?|ref=|aff=)/i.test(html));
 assert.equal((html.match(/PROPOSED GUIDE CTA — INACTIVE/g)||[]).length,1);
});
test('canonical 4 editorial / 2 commercial kept in manifest',()=>{
 const s=JSON.parse(read('snapshot.json'));
 assert.equal(s.manifest.issues.length,6);
 assert.equal(s.manifest.mix.editorial,4);
 assert.equal(s.manifest.mix.commercial_review_pending,2);
 assert.equal(s.manifest.issues[2].merchant_affiliate_url,null);
});