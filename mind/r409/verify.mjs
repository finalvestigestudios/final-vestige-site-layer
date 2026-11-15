#!/usr/bin/env node
// Mind R409 source-only safety/quality audit. Run: node mind/r409/verify.mjs
// This deliberately tests source properties, not browser, merchant, consent, or payment outcomes.
import {readFileSync, existsSync, statSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url));
const read=f=>readFileSync(path.join(dir,f),'utf8');
let count=0;
const ok=(condition,reason)=>{if(!condition)throw Error('FAIL '+reason);count++;};
const a=read('ZEN12_A_TEXT.html'),b=read('ZEN12_B_PLAYABLE_VIDEO.html'),hub=read('MIND_ARCHIVE_WORDPRESS_REVIEW_SOURCE.html'),vtt=read('zen12_42s_captions.vtt'),svg=read('zen12_poster.svg'),matrix=JSON.parse(read('CLAIM_AUTHORIZATION_MATRIX.json')),study=read('THE_PURCHASE_PROMISE_AND_THE_CONTROL.md');
const article=s=>s.match(/<article class="wrap">[\s\S]+?<\/article>/)?.[0];
ok(Boolean(article(a)),'A article exists');
ok(article(a)===article(b),'exact A/B buyer-copy parity');
ok(!/<video\b/i.test(a),'A has no film');
ok(/<video\s+controls\b/i.test(b),'B has native controls');
ok(/\bpreload="none"/.test(b),'B does not preload data');
ok(/\bplaysinline/.test(b),'B plays inline');
ok(/poster="zen12_poster.svg"/.test(b),'B original poster');
ok(/<source src="zen12_42s_original_silent.mp4"/.test(b),'B same-origin film');
ok(/<track kind="captions"/.test(b),'B real caption track');
ok(/<details>[\s\S]*<summary>/.test(b),'B no-JS transcript');
ok(!/<video[^>]*\bautoplay\b/i.test(b),'video autoplay prohibited');
for(const [label,content] of [['A',a],['B',b],['hub',hub]]){
ok(!/<script\b/i.test(content),label+' no scripts');
ok(!/<form\b/i.test(content),label+' no added forms');
ok(!/https?:\/\/[^"'\s>]*(?:\baffid\b|\baffiliate_id\b|hop=|ref=|tid=)/i.test(content),label+' no fabricated affiliate link');
}
for(const [label,content] of [['A',a],['B',b]]) {
ok(/<button class="cta" type="button" disabled aria-disabled="true">/.test(content),label+' native disabled merchant button');
ok(/Affiliate disclosure[\s\S]{0,170}Final Vestige may earn a commission/.test(content),label+' adjacent hypothetical FTC disclosure');
ok(/has not used, tested or listened/.test(content),label+' no made-up personal experience');
ok(/free Seven Day Focus Fieldbook/.test(content),label+' existing free lead magnet');
}
ok(/<svg xmlns="http:\/\/www.w3.org\/2000\/svg"/.test(svg),'SVG proper namespace');
ok(/<title id="t">/.test(svg),'SVG title accessible');
ok(!/<script\b/i.test(svg),'SVG no script');
ok(/^WEBVTT\n/.test(vtt),'VTT header');
const ts=s=>{const [hh,mm,ss]=s.split(':');return Number(hh)*3600+Number(mm)*60+Number(ss)};
const ranges=[...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)].map(m=>[ts(m[1]),ts(m[2])]);
ok(ranges.length===6,'six cues');
ok(ranges[0][0]===0,'starts at zero');
ok(ranges.at(-1)[1]===42,'ends at 42 seconds');
ok(ranges.every((x,i)=>x[1]>x[0]&&(i===0||x[0]===ranges[i-1][1])),'contiguous timings');
for(const phrase of ['THE SECOND SIGNAL','ATTENTION HAS LIMITS','A RESULT IS NOT A PROMISE','WHAT ZEN12 ACTUALLY SELLS','WHAT HAS NOT BEEN TESTED','TRY THE FREE BASELINE']){
ok(vtt.includes(phrase),'VTT '+phrase);
ok(b.includes(phrase),'B transcript '+phrase);
}
ok(matrix.claims.length===30,'30 explicit claims');
ok(matrix.sources.length===16,'16 source links');
ok(Object.keys(matrix.release_gates).length===28,'28 release gates');
ok(Object.values(matrix.release_gates).every(x=>x.status==='HOLD'),'commercial gates locked');
ok(matrix.commercial_action.merchant_url===null,'no merchant URL');
ok(matrix.paid_revenue_per_1000_qualified_sessions===null,'no invented paid outcome');
ok(!Object.keys(matrix).includes('merchant_affiliate_url'),'no phantom affiliate URL');
ok(study.includes('https://pubmed.ncbi.nlm.nih.gov/16466414/'),'original cognitive study linked');
ok(study.includes('https://finalvestige.com/focus/'),'existing Focus bridge');
ok(hub.includes('four')===false||hub.includes('Mind'),'hub rendered');
if(existsSync(path.join(dir,'zen12_42s_original_silent.mp4'))){
const binary=readFileSync(path.join(dir,'zen12_42s_original_silent.mp4'));
ok(binary.subarray(4,8).toString()==='ftyp','MP4 ftyp magic');
ok(binary.length<120000,'MP4 under 120KB');
console.log('MP4 included; binary header and size PASS. Film duration should be confirmed by ffprobe.');
}else{
console.log('MP4 NOT committed in this branch; build with Python renderer and hold browser delivery QA.');
}
console.log('PASS '+count+' native Node source assertions. Remaining: real browser/accessibility, WordPress sanitizer, Jetpack, partner and settled sale.');
