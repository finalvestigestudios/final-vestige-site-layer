#!/usr/bin/env node
'use strict';const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const dir=path.resolve(__dirname,'..'),m=JSON.parse(fs.readFileSync(path.join(dir,'specimens_manifest.json'),'utf8'));
assert.equal(m.status,'UNSENT_OFFLINE_SPECIMENS_ONLY');assert.deepEqual(m.editions.filter(e=>e.kind==='editorial').map(e=>e.issue),[1,2,4,6]);assert.deepEqual(m.editions.filter(e=>e.kind==='commercial-review-pending').map(e=>e.issue),[3,5]);assert.ok(Object.values(m.release).every(x=>x===false));let checks=4;
for(const e of m.editions){const k=String(e.issue).padStart(2,'0'),txt=fs.readFileSync(path.join(dir,'specimens',k+'.txt'),'utf8'),eml=fs.readFileSync(path.join(dir,'specimens',k+'.eml'),'utf8'),b='fv-r212-offline-'+k;
assert.ok(txt.startsWith('FINAL VESTIGE STUDIOS — OFFLINE REVIEW ONLY')&&txt.includes('DO NOT SEND'));checks++;
assert.ok(txt.includes('Subject: '+e.subject)&&txt.includes('Preheader: '+e.preheader));checks++;
assert.ok(txt.includes('ONE CTA')&&txt.includes('VALID_FINAL_VESTIGE_POSTAL_ADDRESS_REQUIRED'));checks++;
assert.ok(eml.includes('X-FV-Release-State: HOLD_UNSENT')&&eml.includes('review@dispatch.invalid')&&eml.includes('reader@dispatch.invalid'));checks++;
assert.ok(!/^(Bcc|Cc|List-Unsubscribe):/m.test(eml));checks++;
assert.equal((eml.match(/Content-Transfer-Encoding: base64/g)||[]).length,2);checks++;
assert.equal((eml.match(new RegExp('--'+b,'g'))||[]).length,3);checks++;
assert.ok(eml.endsWith('--'+b+'--\r\n'));checks++;
const ps=eml.split('\r\n--'+b+'\r\n');assert.equal(ps.length,3);checks++;
const decode=p=>Buffer.from(p.split('\r\n\r\n')[1].replace(/\r\n/g,''),'base64').toString('utf8');
const ptext=decode(ps[1]),html=decode(ps[2].split('\r\n--'+b+'--')[0]);assert.equal(ptext,txt);checks++;
assert.ok(html.includes('lang="en"')&&html.includes('role="presentation"'));checks++;
assert.ok(!/<script|<img[^>]+tracking/i.test(html));checks++;
if(e.kind==='commercial-review-pending'){assert.ok(txt.includes('Commercial disclosure immediately beside')&&txt.includes('APPROVED_LIVE_'));checks++;assert.ok(!/href=["'][^"']*(awin1|affiliates.inspire3|ref=)/i.test(html));checks++}else{assert.ok(txt.includes('https://finalvestige.com/'));checks++}}
console.log('R212 offline MIME/alternative tests PASS:',checks,'(NOT a Jetpack delivery test)');