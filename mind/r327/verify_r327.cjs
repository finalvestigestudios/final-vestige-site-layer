'use strict';
const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const here=__dirname;
const a=fs.readFileSync(path.join(here,'ZEN12-A-TEXT-REVIEW.html'),'utf8');
const b=fs.readFileSync(path.join(here,'ZEN12-B-OPTIONAL-FILM-REVIEW.html'),'utf8');
const h=fs.readFileSync(path.join(here,'MIND-HUB-WP-REVIEW-ONLY.html'),'utf8');
const paper=fs.readFileSync(path.join(here,'THE-SECOND-LETTER-THAT-VANISHED-UNPUBLISHED.md'),'utf8');
const vtt=fs.readFileSync(path.join(here,'ORIGINAL-42S-CAPTIONS.vtt'),'utf8');
const m=JSON.parse(fs.readFileSync(path.join(here,'SOURCE-CLAIM-COMMERCE.json'),'utf8'));
let n=0;const check=(desc,fn)=>{fn();n++;console.log('PASS',desc)};
check('A/B identical substantive buyer copy',()=>assert.equal(a.replace(/<!doctype[\s\S]*?<main class="wrap">/,'').replace(/<!-- FILM START -->[\s\S]*?<!-- FILM END -->/,'').replace(/<\/main>[\s\S]*/,'').replace(/\s+/g,' '),b.replace(/<!doctype[\s\S]*?<main class="wrap">/,'').replace(/<!-- FILM START -->[\s\S]*?<!-- FILM END -->/,'').replace(/<\/main>[\s\S]*/,'').replace(/\s+/g,' ')));
for(const [name,x] of [['buyer A',a],['buyer B',b],['hub',h]]) {
check(name+' no forms, scripts, live merchant links',()=>{assert(!/<script\b|<form\b|<iframe\b/i.test(x));assert(!/href=["'][^"']*(zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(x));assert(!/\bautoplay\b/i.test(x.replace(/no autoplay/ig,'')));});
check(name+' valid accessible basics',()=>{assert(/<html lang="en">/.test(x));assert(/<meta name="viewport"/.test(x));assert(/<main\b/.test(x));assert(/<h1>/.test(x));assert(/prefers-reduced-motion/.test(x));});
}
for(const [name,x] of [['buyer A',a],['buyer B',b]]) {
check(name+' genuinely disabled checkout + near-link disclosure',()=>{assert(/<button[^>]*\bdisabled\b[^>]*>/.test(x));assert(x.indexOf('may earn a commission')>x.indexOf('<button type="button" disabled'));assert(x.indexOf('may earn a commission')-x.indexOf('<button type="button" disabled')<650);assert(x.includes('https://finalvestige.com/focus/'));});
check(name+' no price or unverified universal guarantee',()=>{assert(!/\$\d/.test(x));assert(!/guaranteed cognitive|100% focus|cures anxiety|results in hours/i.test(x));});
}
check('optional film present B only, transcript and original SVG',()=>{assert(!a.includes('<!-- FILM START -->'));assert(b.includes('<!-- FILM START -->'));assert(b.includes('aria-labelledby="fvfilm-title fvfilm-desc"'));assert(b.includes('<details>'));assert(b.includes('00:35–00:42'));});
check('VTT contiguous exact 42s',()=>{let lines=vtt.match(/00:00:\d\d\.000 --> 00:00:\d\d\.000/g)||[];assert.equal(lines.length,6);assert(lines[0].startsWith('00:00:00.000'));assert(lines.at(-1).endsWith('00:00:42.000'));for(let i=0;i<lines.length-1;i++)assert.equal(lines[i].slice(-12),lines[i+1].slice(0,12));});
check('no faux historical/media licensing',()=>assert(!/<img\b[^>]*src=["']https?:/i.test(a+b+h)));
check('citation source ids valid',()=>{const ids=new Set(m.sources.map(s=>s.id));for(const c of m.claims){assert(c.source_ids.length>0);for(const id of c.source_ids)assert(ids.has(id),c.id+': '+id)}});
check('all authorization holds strictly closed',()=>{assert.equal(m.commercial_holds.length,18);assert(m.commercial_holds.every(x=>x.passed===false));assert.equal(m.partner_status,'NOT VERIFIED')});
check('no misleading claim passed off as proven',()=>{for(const c of m.claims)if(c.status==='seller_claim_excluded')assert(/exclude|not|unverified|unsupported|no /i.test(c.limitation));});
check('source article has primary limits and lived content',()=>{assert(paper.split(/\s+/).length>1400);for(const x of ['1992','1994','2005','2006','2007','2019','Puységur','not a randomized trial','Source limitation'])assert(paper.includes(x),x);});
check('hub has accurate published paths and no fake mind publication',()=>{for(const x of ['change-blindness/','mesmerism/','puysegurs-animal-magnetism-files/','/focus/','not created in WordPress CMS'])assert(h.toLowerCase().includes(x.toLowerCase()))});
console.log('TOTAL PASS:',n);
