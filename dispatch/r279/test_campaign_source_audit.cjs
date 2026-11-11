'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {audit}=require('./campaign_source_audit.cjs');
const root=path.join(__dirname,'../campaign-2026-mind');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
const source=Object.fromEntries(manifest.issues.map(i=>[i.slug,fs.readFileSync(path.join(root,'issues',String(i.number).padStart(2,'0')+'-'+i.slug+'.md'),'utf8')]));
const dup=x=>JSON.parse(JSON.stringify(x)), run=(m=manifest,s=source)=>audit(m,s);
let count=0;
function test(name,fn){fn();count++;console.log('PASS '+count+' '+name)}
function has(a,code){return a.findings.some(x=>x.code===code)}
test('source bound six edition hold',()=>assert.equal(run().status,'HOLD_NO_SEND'));
test('all six commercial-purpose checks',()=>assert.equal(run().findings.filter(x=>x.code==='CAN_SPAM_PRIMARY_PURPOSE_AND_FOOTER_REVIEW').length,6));
test('duplicate early destination surfaced',()=>assert.ok(has(run(),'ISSUES_01_02_DUPLICATE_CTA')));
test('repeat Fieldbook surfaced',()=>assert.ok(has(run(),'ISSUE_06_REPEATS_WELCOME_FIELD_BOOK')));
test('Apollo 14-second subject review surfaced',()=>assert.ok(has(run(),'ISSUE_04_SUBJECT_NUMBER_NOT_EXPLAINED')));
for(const [name,idx,change,expected] of [
 ['missing source',0,s=>null,'MISSING_SOURCE'],
 ['changed subject',0,s=>s.replace('**Subject:**','**Different:**'),'SUBJECT_PREHEADER_DRIFT'],
 ['changed preheader',0,s=>s.replace('**Preheader:**','**Different:**'),'SUBJECT_PREHEADER_DRIFT'],
 ['postal guard missing',1,s=>s.replace('[[VALID_POSTAL_ADDRESS_REQUIRED]]',''),'FOOTER_GUARD_MISSING'],
 ['unsub guard missing',1,s=>s.replace('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]',''),'FOOTER_GUARD_MISSING'],
 ['no-send guard missing',0,s=>s.replace('DO NOT PUBLISH OR EMAIL',''),'NO_SEND_GUARD'],
 ['affiliate disclosure missing',2,s=>s.replace('**Commercial disclosure:**',''),'COMMERCIAL_DISCLOSURE_NOT_NEAR_CTA'],
 ['direct merchant link even after footer',2,s=>s+'\nhttps://zen12.com/getstarted','MERCHANT_LINK_IN_DRAFT'],
 ['primary CTA stripped',5,s=>s.replace('**Open the free Fieldbook:**',''),'PRIMARY_CTA_MISSING'],
 ['guide target mismatch',4,s=>s.replace('[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]','https://example.org'),'CTA_DESTINATION_DRIFT']
]) test(name,()=>{let s=dup(source);s[manifest.issues[idx].slug]=change(s[manifest.issues[idx].slug]);assert.ok(has(run(manifest,s),expected))});
test('activated affiliate link in manifest refused',()=>{let m=dup(manifest);m.issues[2].merchant_affiliate_url='https://zen12.com/getstarted';assert.ok(has(run(m),'AFFILIATE_ACTIVATED'))});
test('activated guide target refused',()=>{let m=dup(manifest);let s=dup(source);const i=m.issues[2];s[i.slug]=s[i.slug].replace(i.editorial_cta,'https://finalvestige.com/guide');i.editorial_cta='https://finalvestige.com/guide';assert.ok(has(run(m,s),'UNAPPROVED_GUIDE_ACTIVATED'))});
test('wrong editorial allocation refused',()=>{let m=dup(manifest);m.issues[0].kind='commercial-review-pending';assert.ok(has(run(m),'EDITORIAL_COMMERCIAL_MIX'))});
test('scheduled status refused',()=>{let m=dup(manifest);m.status='READY';assert.ok(has(run(m),'UNSENT_STATUS'))});
test('caller supplied approval cannot switch to READY',()=>{let m=dup(manifest);m.approved=true;assert.equal(run(m).authorized_to_send,false)});
console.log('TOTAL '+count+'/'+count+' PASS (source-level only, no live compliance attestation)');