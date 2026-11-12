#!/usr/bin/env node
'use strict';
// Mind R305 release-safety regression and evidence guard. Usage: node mind/r305/verify_r305.cjs
// Pure local filesystem checks only. No network, marketing actions, CMS writes or checkout.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=__dirname;
const names={article:'THE-MEMORY-THAT-ARRIVED-IN-THE-QUESTION-UNPUBLISHED.md',buyer:'ZEN12-EVIDENCE-CONTRACT-PRESELL-REVIEW-ONLY.html',hub:'MIND-ARCHIVE-EVIDENCE-READING-ROOM-REVIEW-ONLY.html',matrix:'SUGGESTION-SOURCE-CLAIM-AND-COMMERCE-GATES.json',video:'make-42-second-silent-evidence-video.sh',captions:'ZEN12-42-SECOND-CAPTIONS.vtt'};
const files=Object.fromEntries(Object.entries(names).map(([k,v])=>[k,fs.readFileSync(path.join(root,v),'utf8')]));
const fail=(condition,message)=>{if(!condition)throw new Error(message)};
function checkArticle(a){
 fail(a.split(/\s+/).length>=1800,'ARTICLE_NOT_SUBSTANTIVE');
 for(const s of ['Loftus','Palmer','Gabbert','Puységur','https://doi.org/10.1016/S0022-5371(74)80011-3','https://pubmed.ncbi.nlm.nih.gov/16027179/','1974','2003','source'])fail(a.includes(s),'ARTICLE_SOURCE_'+s);
 fail(/full article paywalled|complete articles and underlying participant data.*not/i.test(a),'READING_SCOPE_MISSING');
 fail(!/all witnesses are unreliable|Zen12 is clinically proven|guaranteed focus|we tested Zen12/i.test(a),'ARTICLE_UNSUPPORTED_EFFECT');
}
function checkHtml(h,type){
 fail(/<!doctype html>/i.test(h)&&/<html lang="en">/i.test(h),'SEMANTIC_ROOT_'+type);
 for(const r of [/<main\b/,/<h1\b/,/href="#content"/,/@media\(max-width:/,/prefers-reduced-motion/,/noindex,nofollow/,/https:\/\/finalvestige\.com\/focus\//])fail(r.test(h),'BASIC_A11Y_'+type+'_'+r);
 for(const r of [/<script\b/i,/<iframe\b/i,/<form\b/i,/\bonclick\s*=/i,/\bautoplay\b/i,/<a[^>]*\bhref=["']https?:\/\/(?:www\.)?(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i])fail(!r.test(h),'UNAUTHORIZED_HTML_'+type+'_'+r);
 fail(!/guaranteed (focus|memory|income|cure)|clinically proven Zen12|we have used Zen12/i.test(h),'UNSUPPORTED_COPY_'+type);
 const btns=[...h.matchAll(/<button\b[^>]*>/gi)].map(x=>x[0]);
 fail(btns.length===1,'SINGLE_MERCHANT_CONTROL_'+type);
 fail(/(?:\s|^)disabled(?:\s|>)/i.test(btns[0]),'MUST_HAVE_REAL_DISABLED_ATTRIBUTE_'+type);
 fail(/aria-disabled="true"/.test(btns[0]),'MUST_HAVE_ARIA_DISABLED_'+type);
 fail(/commission/i.test(h)&&/no such link is active|no earning link is active|no merchant referral/i.test(h),'ADJACENT_DISCLOSURE_'+type);
 const b=h.indexOf(btns[0]);const d=h.lastIndexOf('class="disclosure"',b);
 fail(d>=0&&b-d<1400,'DISCLOSURE_PROXIMITY_'+type);
 fail(!/<video\b/i.test(h),'NO_FALSE_PLAYABLE_VIDEO_'+type); // B film hosted only in separate approved preview
}
function checkMatrix(raw){
 let m;try{m=JSON.parse(raw)}catch(e){throw new Error('INVALID_JSON')}
 fail(m.schema==='fv-mind-r305-evidence-commerce-v1','SCHEMA');
 fail(m.status==='DRAFT_UNPUBLISHED_HARD_HOLD','RELEASE_HOLD');
 fail(m.sources.length>=18,'SOURCES_UNDERSUPPLIED');
 const ids=new Set(m.sources.map(x=>x.id));
 fail(ids.size===m.sources.length&&m.sources.every(x=>/^https:\/\//.test(x.url)&&x.scope),'SOURCE_INTEGRITY');
 fail(m.claims.length>=25,'CLAIMS_UNDERSUPPLIED');
 fail(m.claims.every(x=>ids.has(x.source_id)&&x.decision&&x.statement),'CLAIM_SOURCE_INTEGRITY');
 fail(m.claims.some(x=>x.id==='V1'&&x.decision==='CORRECT_PRIOR_DRAFT'),'PRAXXIS_CORRECTION_MISSING');
 fail(m.gates.length===18&&m.gates.every(x=>x.status==='HARD_HOLD'),'MERCHANT_GATE_NOT_VERIFIED');
 fail(m.offers[0].status==='NOT_ACTIVATABLE','ACTIVE_AFFILIATE');
 fail(m.creator_map.filter(x=>x.asset_id).every(x=>x.status==='OWNER_REPORTED_NOT_PLATFORM_VERIFIED'),'INVENTED_CREATOR_PROOF');
 const v=m.event_contract.observed;
 fail(v.qualified_human_sessions===null&&v.attributed_paid_orders===null&&v.net_realized_earnings===null&&v.kpi===null,'FABRICATED_FINANCIAL_KPI');
 fail(m.event_contract.privacy.includes('No PII'),'PRIVACY_REMOVED');
 return m;
}
function checkVideo(s,c){
 fail(s.startsWith('#!/usr/bin/env bash')&&/(?:^|\n)ffmpeg -hide_banner/.test(s),'VIDEO_GENERATOR_MISSING');
 fail(s.includes('d=42')&&s.includes('-an -t 42'),'VIDEO_LENGTH_OR_AUDIO');
 fail(!/curl|wget|https?:\/\//.test(s),'VIDEO_EXTERNAL_FETCH');
 fail(c.startsWith('WEBVTT')&&c.includes('00:00:33.000 --> 00:00:42.000'),'CAPTIONS_MISSING_42S');
}
function baseline(f){checkArticle(f.article);checkHtml(f.buyer,'buyer');checkHtml(f.hub,'hub');checkMatrix(f.matrix);checkVideo(f.video,f.captions);}
baseline(files);
const mutations=[
['buyer','no-disabled',s=>s.replace('type="button" disabled aria-disabled','type="button" aria-disabled')],
['buyer','aria-only',s=>s.replace(' disabled aria-disabled',' aria-disabled')],
['buyer','no-aria-disabled',s=>s.replace('aria-disabled="true"','aria-disabled="false"')],
['buyer','checkout-anchor',s=>s.replace('</body>','<a href="https://zen12.com/getstarted">Buy</a></body>')],
['buyer','hidden-affiliate',s=>s.replace('</body>','<a href="https://affiliates.inspire3.com/">Pay</a></body>')],
['buyer','script',s=>s.replace('</body>','<script>console.log("x")</script></body>')],
['buyer','iframe',s=>s.replace('</body>','<iframe src="https://example.org"></iframe></body>')],
['buyer','form',s=>s.replace('</body>','<form><input></form></body>')],
['buyer','onclick',s=>s.replace('</body>','<p onclick="foo()">X</p></body>')],
['buyer','autoplay',s=>s.replace('</body>','<video autoplay></video></body>')],
['buyer','no-disclosure',s=>s.replace('class="disclosure"','class="unknown"')],
['buyer','fake-proof',s=>s.replace('</body>','<p>Zen12 is clinically proven</p></body>')],
['hub','new-signup',s=>s.replace('</body>','<form><input type="email"></form></body>')],
['hub','active-purchase',s=>s.replace('type="button" disabled aria-disabled','type="button" aria-disabled')],
['hub','merchant-link',s=>s.replace('</body>','<a href="https://brainwaveshots.com/focus-shot">Buy</a></body>')],
['hub','missing-focus',s=>s.replaceAll('https://finalvestige.com/focus/','https://example.org/free')],
['matrix','active-gate',s=>s.replace('"status": "HARD_HOLD"','"status": "APPROVED"')],
['matrix','cleared-orders',s=>s.replace('"attributed_paid_orders": null','"attributed_paid_orders": 42')],
['matrix','net-revenue',s=>s.replace('"net_realized_earnings": null','"net_realized_earnings": 100')],
['matrix','published-status',s=>s.replace('DRAFT_UNPUBLISHED_HARD_HOLD','LIVE')],
['matrix','missing-source-id',s=>s.replace('"source_id": "LOFTUS74"','"source_id": "MISSING"')],
['matrix','prx-correction',s=>s.replace('"decision": "CORRECT_PRIOR_DRAFT"','"decision": "ALLOW"')],
['matrix','invented-video-id',s=>s.replace('"asset_id": null','"asset_id": "fabricated"')],
['article','too-short',s=>s.slice(0,800)],
['article','false-claim',s=>s+'\nAll witnesses are unreliable.'],
['video','no-ffmpeg',s=>s.replace('ffmpeg -hide_banner','noencoder -hide_banner')],
['video','external-media',s=>s+'\ncurl https://unapproved.invalid\n'],
['captions','no-final-caption',s=>s.replace('00:00:33.000 --> 00:00:42.000','00:00:33.000 --> 00:00:34.000')]
];
let pass=0;
for(const [field,name,mutate] of mutations){
 const corrupted={...files,[field]:mutate(files[field])};
 fail(corrupted[field]!==files[field],'BAD_MUTATION_FIXTURE_'+name);
 try{baseline(corrupted);throw new Error('UNSAFE_MUTATION_ACCEPTED_'+name)}catch(e){
 if(String(e.message).startsWith('UNSAFE_MUTATION_ACCEPTED_'))throw e;
 pass++;
 }
}
console.log(JSON.stringify({status:'PASS',source_files:Object.keys(files).length,negative_mutations_passed:pass,commercial_gates:18,claims:checkMatrix(files.matrix).claims.length,mode:'local source checks only; not browser, WordPress or merchant checkout'},null,2));
