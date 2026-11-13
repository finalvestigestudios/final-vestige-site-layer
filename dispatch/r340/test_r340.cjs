'use strict';
const {test}=require('node:test'),a=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const dir=__dirname,m=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json'),'utf8'));
const get=(n,s)=>fs.readFileSync(path.join(dir,'issue'+String(n).padStart(2,'0')+'.'+s),'utf8');
test('source master frozen',()=>{a.equal(m.original_pr,175);a.equal(m.original_head,'d57ccdba3aee8f065e143e101c2945f4f3d01647');a.equal(m.parent_pr,2393);});
test('4/2 mix and six held slots',()=>{a.deepEqual(m.mix,{editorial:4,merchant_reserved:2});a.equal(m.slot_state.length,6);a(m.slot_state.every(s=>s.release==='HOLD_UNSENT'&&!s.alternative_adopted));a.deepEqual(m.slot_state.filter(s=>s.merchant==='HOLD_MERCHANT').map(s=>s.number),[3,5]);});
test('all signoffs fail closed',()=>a(Object.values(m.approvals).every(v=>v===false)));
test('provider numbers not added as deliverable audience',()=>{a.equal(m.provider_snapshot.counts_overlap,true);a.equal(m.provider_snapshot.eligible_recipient_count,null);a.equal(m.provider_snapshot.auto_email_new_posts,false);a.equal(m.provider_snapshot.welcome_receipt_verified,false);});
test('no invented revenue or deployed instrumentation',()=>{a.equal(m.measurement.net_revenue_per_1000,'NOT_COMPUTABLE');a.equal(m.measurement.tracking_changes_deployed,false);});
for(const n of [1,6]){const e=m.candidates.find(x=>x.number===n);
test('issue '+n+' has honest subject/preheader',()=>{a(e.subject.length<65);a(e.preheader.length<110);for(const s of ['md','txt','html'])a(get(n,s).includes(e.preheader));});
test('issue '+n+' is nonadopted editorial and does not earn merchant links',()=>{a.equal(e.kind,'editorial');a.equal(e.status,'OPTIONAL_NOT_ADOPTED_HOLD_UNSENT');a(e.cta_url.startsWith('https://finalvestige.com/'));a(!/utm_|affiliat(e|es)|clickbank|gclid|fbclid/i.test(e.cta_url));});
test('issue '+n+' one labelled conversion CTA in HTML',()=>{const h=get(n,'html');a.equal((h.match(/data-editorial-cta="true"/g)||[]).length,1);for(const s of ['md','txt','html'])a(get(n,s).includes(e.cta_url));});
test('issue '+n+' deliberately invalid compliance/footer in every format',()=>{for(const s of ['md','txt','html']){const x=get(n,s);a(x.includes('[[VALID_FV_POSTAL_ADDRESS_REQUIRED]]'));a(x.includes('[[VERIFIED_JETPACK_UNSUBSCRIBE_REQUIRED]]'));a(/DO NOT SEND|NOT A SENDABLE|not approved/i.test(x));}});
test('issue '+n+' static accessible source-led HTML',()=>{const h=get(n,'html');a(h.includes('<html lang="en">'));a(h.includes('<table role="presentation"'));a(h.includes('<h1'));a(!/<script|<iframe|<form|<img|<style|javascript:|@import/i.test(h));});
test('issue '+n+' source links exact in all three formats',()=>{for(const url of e.sources){for(const s of ['md','txt','html'])a(get(n,s).includes(url.replaceAll('&',s==='html'?'&amp;':'&')));}});
}
