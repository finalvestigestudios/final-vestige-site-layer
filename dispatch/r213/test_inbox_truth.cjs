#!/usr/bin/env node
'use strict';
// Native Node offline assertions. Zero network, mail, WordPress or subscriber writes.
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const {visibleText,attributeLinks,safeTrackingUrl,audit,subscriberAssessment}=require('./inbox_truth.cjs');
const root=path.resolve(__dirname,'..','..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'dispatch/r212/specimens_manifest.json'),'utf8'));
let checks=0;
function check(condition,why){checks++;assert.ok(condition,why)}
check(manifest.status==='UNSENT_OFFLINE_SPECIMENS_ONLY','manifest is unsent');
check(manifest.editions.length===6,'six issued');
check(manifest.editions.filter(e=>e.kind==='editorial').length===4,'4 editorial');
check(manifest.editions.filter(e=>e.kind==='commercial-review-pending').length===2,'2 commercial');
check(Object.values(manifest.release).every(v=>v===false),'release attestations all false');
let report=[];
for(const e of manifest.editions){
 const html=fs.readFileSync(path.join(root,e.html_path),'utf8');
 const text=fs.readFileSync(path.join(root,'dispatch/r212/specimens',String(e.issue).padStart(2,'0')+'.txt'),'utf8');
 const eml=fs.readFileSync(path.join(root,'dispatch/r212/specimens',String(e.issue).padStart(2,'0')+'.eml'),'utf8');
 const a=audit(e,html,eml,text);report.push(a);
 check(a.release==='HOLD_UNSENT','never authorize a send');
 check(a.source_h1_matches_subject,'subject matches H1');
 check(a.source_preheader_first===false,'preheader is NOT at top of source-visible text');
 check(a.source_visible_opening.startsWith('FINAL VESTIGE STUDIOS'),'brand banner begins source-visible text');
 check(a.review_scaffold_in_body,'review banner is present in body');
 check(a.placeholder_postal&&a.placeholder_unsubscribe,'both legal blockers');
 check(a.specimen_invalid_sender&&a.specimen_x_header_is_only_metadata,'not provider mail/preheader');
 check(!a.verified_native_jetpack_render&&!a.verified_received_welcome,'no fake delivery proof');
 check(a.preview_diagnostic_only&&a.blockers.includes('founder_final_send_approval_not_granted'),'review not send proof');
 check(a.additional_commercial_hold===(e.kind==='commercial-review-pending'),'isolate merchant gate');
 check(!a.earning_href_present,'no active earning href');
 check(attributeLinks(html).every(x=>!x.includes('mailto:')),'no recipient path');
 check(visibleText(html).includes(e.subject),'subject visible somewhere');
}
check(report.length===6,'report covers all six');
check(report.every(x=>x.blockers.includes('preheader_not_first_source_visible_text')),'all six first visible text conflicts');
check(report.every(x=>x.blockers.includes('x_header_is_not_a_standard_inbox_preheader')),'X-header is metadata only');
check(report.filter(x=>x.additional_commercial_hold).map(x=>x.issue).join(',')==='3,5','03/05 additional hold');
const e=manifest.editions[0],h=fs.readFileSync(path.join(root,e.html_path),'utf8'),p='DO NOT SEND',m='X-FV-Intended-Preheader: example';
check(audit({...e,subject:'WRONG SUBJECT'},h,m,p).blockers.includes('subject_h1_mismatch'),'subject drift rejected');
check(audit(e,h.replace('REVIEW ONLY','REVIEW ONLY'),m,p).release==='HOLD_UNSENT','cosmetic edits cannot authorize');
check(audit(e,'<body><p>'+e.preheader+'</p></body>',m,p).source_preheader_first===true,'true first-visible control detected');
check(audit(e,'<body><p>'+e.preheader+'</p></body>',m,p).release==='HOLD_UNSENT','even true synthetic preheader not send approval');
const good='https://finalvestige.com/mind/guide/?utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026_11&utm_content=issue_03_zen12';
check(safeTrackingUrl(good),'allow first-party non-personal tags');
for(const bad of ['http://finalvestige.com/','https://evil.example/','https://finalvestige.com/?email=someone%40example.com',
'https://finalvestige.com/?utm_content=someone@example.com','https://finalvestige.com/?utm_medium=paid',
'https://finalvestige.com/?utm_source=youtube','https://finalvestige.com/?utm_content=issue_03_x',
'https://finalvestige.com/?token=secret','https://finalvestige.com/#private','https://test:secret@finalvestige.com/']){
 check(!safeTrackingUrl(bad),'reject unsafe tracking URL');
}
const s=subscriberAssessment({subscribers:{total:3,confirmed:3,unconfirmed:2},followers:{wpcom:3,email:0}});
check(s.email_eligible_unique_recipients===null,'do not invent email recipients');
check(s.provider_confirmed_signup_events===null&&s.welcome_delivered===null,'do not invent confirmations or welcomes');
check(s.nonadditive_counters&&s.provider_counters.total===3&&s.provider_counters.unconfirmed_requests===2,'do not sum dashboards');
check(!Object.keys(s).some(k=>/address|contact|email_list/i.test(k)),'no list data');
console.log('Dispatch R213 offline source/inbox QA:',checks+'/'+checks,'PASS; native Node; NO provider preview, email or send');
console.log('All six preheaders NOT first in source-visible text; 03/05 HOLD_MERCHANT; every issue HOLD_UNSENT.');
