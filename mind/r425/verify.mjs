#!/usr/bin/env node
/**
 * Final Vestige Mind R425 offline source-only acceptance gate.
 * Run: node mind/r425/verify.mjs
 * Read-only, no network, no paid API, no WordPress mutation.
 * Checks content safety, consistent experiment variants and held commercial permissions.
 * NOT a replacement for browser, accessibility, checkout or product science review.
 */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const dir = dirname(fileURLToPath(import.meta.url));
const names = ['THE_FACE_THAT_ONLY_LOOKED_WRONG.md','ZEN12_A_TEXT_ONLY.html','ZEN12_B_OPTIONAL_VIDEO_CONCEPT.html','ZEN12_42S_CAPTIONS.vtt','MIND_HUB_WP_SOURCE_ONLY.html','CLAIM_SOURCE_PERMISSION_MATRIX.json','CONVERSION_ACCEPTANCE_AND_CREATOR_FIT.md'];
const files = Object.fromEntries(names.map(n=>[n,readFileSync(join(dir,n),'utf8')]));
const check = (truth, label) => { assert.ok(truth,label); };
function examine(f) {
 let count=0;
 const ok=(v,n)=>{check(v,n);count++;};
 const article=f['THE_FACE_THAT_ONLY_LOOKED_WRONG.md'];
 const a=f['ZEN12_A_TEXT_ONLY.html'],b=f['ZEN12_B_OPTIONAL_VIDEO_CONCEPT.html'];
 const hub=f['MIND_HUB_WP_SOURCE_ONLY.html'],vtt=f['ZEN12_42S_CAPTIONS.vtt'];
 const matrix=JSON.parse(f['CLAIM_SOURCE_PERMISSION_MATRIX.json']);
 const plan=f['CONVERSION_ACCEPTANCE_AND_CREATOR_FIT.md'];
 const pages=[a,b,hub];
 ok(article.trim().split(/\s+/).length>=1900,'article sufficiently substantive');
 for(const doi of ['10.1068/p090483','10.1068/p6659','10.1068/p5508','10.1068/p7755','10.1177/0956797613501521'])ok(article.includes(doi),'article research trail '+doi);
 for(const url of ['https://finalvestige.com/focus/','https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'])ok(article.includes(url),'article connects existing free path '+url);
 ok(article.includes('**not** reproducing'),'rights language in article');
 ok(article.includes('not')&&article.includes('product-specific evidence'),'product claim limits');
 ok(matrix.claim_count===matrix.claims.length&&matrix.claims.length>=25,'claim count self-consistent');
 ok(matrix.release_gates.length===28,'all 28 gating items');
 ok(matrix.release_gates.every(x=>x.state==='HOLD'),'all commercial gates held');
 ok(matrix.no_active_affiliate_links===true,'active partner links disabled');
 ok(matrix.referral_price===null&&matrix.referral_commission===null,'no invented money');
 ok(matrix.verified_orders===null&&matrix.verified_net_revenue_per_1000_qualified_sessions===null,'no invented orders');
 ok(matrix.claims.some(x=>x.id==='Z04'&&x.decision.includes('excluded')),'equivalence promise excluded');
 ok(matrix.claims.some(x=>x.id==='A02'&&x.decision==='UNVERIFIED'),'partner eligibility unknown');
 for(const [i,p] of pages.entries()){
   ok(/<html lang="en">/.test(p),'lang present '+i);
   ok(/<meta name="viewport"/.test(p),'responsive viewport '+i);
   ok(/<meta name="robots" content="noindex,nofollow"/.test(p),'noindex source prototype '+i);
   ok(!/<script\b|<iframe\b|<form\b|<audio\b|<video\b/i.test(p),'no scripts/embeds/forms '+i);
   ok(!/\bautoplay\b\s*(=|>|\/)/i.test(p),'no autoplay attribute '+i);
   ok(!/href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(p),'no merchant outbound anchor '+i);
   ok(!/utm_(?:source|campaign|content)=|fbclid=|gclid=/i.test(p),'no live URL tracking '+i);
   ok(!/\$\s*\d+[\d.,]*/.test(p),'no unverified offer price '+i);
   ok(/focus\//.test(p),'one existing free Focus route '+i);
 }
 for(const [i,p] of [a,b].entries()){
   ok(/<button[^>]+disabled[^>]*>/.test(p),'native disabled offer '+i);
   ok(/aria-describedby="affiliate-disclosure"/.test(p),'adjacent disclosure binding '+i);
   ok(/id="affiliate-disclosure"/.test(p),'disclosure presence '+i);
   ok(p.replace(/<[^>]*>/g,'').includes(matrix.disclosure_literal),'disclosure matches approved matrix '+i);
   ok(/source[- ]first|evidence|scientific/i.test(p),'source-first trust copy '+i);
 }
 const content=(p)=>p.slice(p.indexOf('<div class="grid">'),p.indexOf('</main>'));
 ok(content(a)===content(b),'same substantive buyer content in A/B');
 ok(!a.includes('id="film"')&&b.includes('id="film"'),'only B adds film concept');
 ok(b.includes('<svg ')&&b.includes('role="img"')&&b.includes('<details>'),'accessible static poster/transcript');
 ok(!b.includes('src="https://')&&!b.includes('<source'),'no external video/player');
 const cues=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d\d\d) --> (\d\d):(\d\d):(\d\d)\.(\d\d\d)/g)];
 ok(cues.length===6,'6 VTT cues');
 const milliseconds=(h,m,s,ms)=>((Number(h)*60+Number(m))*60+Number(s))*1000+Number(ms);
 for(let i=0;i<cues.length;i++){
   const v=cues[i],start=milliseconds(...v.slice(1,5)),end=milliseconds(...v.slice(5,9));
   ok(end>start,'cue positive duration '+i);
   ok(start===i*7000&&end===(i+1)*7000,'contiguous 7-second cue '+i);
 }
 ok(plan.includes('NOT COMPUTABLE'),'revenue unknown');
 ok(plan.includes('Grok retains')&&plan.includes('Praxxis'),'creator ownership');
 ok(plan.includes('merchant_confirmed_purchase')&&plan.includes('affiliate_outbound'),'sales event distinction');
 ok(plan.includes('No product URL is inserted as an earning link'),'authorization hold in spec');
 ok(hub.includes('Tools under review')&&hub.includes('History of suggestion')&&hub.includes('Perception and attention')&&hub.includes('Practice and reflection'),'four-stream hub');
 ok(!hub.includes('name="email"'),'single Jetpack funnel preserved');
 return count;
}
const passed=examine(files);
const mutations=[
 ['active merchant link', f=>f['ZEN12_A_TEXT_ONLY.html']+=' <a href="https://zen12.com/">Buy here</a>'],
 ['commercial button armed', f=>f['ZEN12_B_OPTIONAL_VIDEO_CONCEPT.html']=f['ZEN12_B_OPTIONAL_VIDEO_CONCEPT.html'].replace('class="cta" disabled','class="cta"')],
 ['remove disclosure', f=>f['ZEN12_A_TEXT_ONLY.html']=f['ZEN12_A_TEXT_ONLY.html'].replace('id="affiliate-disclosure"','id="removed"')],
 ['tracking script', f=>f['ZEN12_B_OPTIONAL_VIDEO_CONCEPT.html']+=' <script src="/track.js"></script>'],
 ['signup duplication', f=>f['MIND_HUB_WP_SOURCE_ONLY.html']+='<form><input name="email"></form>'],
 ['fake price', f=>f['ZEN12_A_TEXT_ONLY.html']+=' Price $2.00'],
 ['unheld gate', f=>{const x=JSON.parse(f['CLAIM_SOURCE_PERMISSION_MATRIX.json']);x.release_gates[0].state='PASS';f['CLAIM_SOURCE_PERMISSION_MATRIX.json']=JSON.stringify(x)}],
 ['fabricated money', f=>{const x=JSON.parse(f['CLAIM_SOURCE_PERMISSION_MATRIX.json']);x.referral_commission=500;f['CLAIM_SOURCE_PERMISSION_MATRIX.json']=JSON.stringify(x)}],
 ['VTT gap', f=>f['ZEN12_42S_CAPTIONS.vtt']=f['ZEN12_42S_CAPTIONS.vtt'].replace('00:00:14.000 --> 00:00:21.000','00:00:15.000 --> 00:00:21.000')],
 ['invented payout outcome', f=>{const x=JSON.parse(f['CLAIM_SOURCE_PERMISSION_MATRIX.json']);x.verified_orders=12;f['CLAIM_SOURCE_PERMISSION_MATRIX.json']=JSON.stringify(x)}]
];
let caught=0;
for(const [label,mutate] of mutations){
 const copy={...files};
 mutate(copy);
 try{examine(copy);}catch{caught++;continue;}
 throw new Error('Unsafe mutation not detected: '+label);
}
console.log('PASS '+passed+'/'+passed+' source checks; '+caught+'/'+mutations.length+' unsafe mutations rejected. Native Node offline. No browser/merchant/CI claim.');
