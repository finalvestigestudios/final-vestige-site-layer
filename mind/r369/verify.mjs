import fs from 'node:fs';import assert from 'node:assert/strict';
const read=n=>fs.readFileSync(new URL(n,import.meta.url),'utf8');
const a=read('ZEN12_A_TEXT.html'),b=read('ZEN12_B_OPTIONAL_FILM.html'),h=read('MIND_HUB_REVIEW_ONLY.html'),v=read('ORIGINAL_42S_CAPTIONS.vtt'),m=JSON.parse(read('CLAIM_SOURCE_AUTHORIZATION_MATRIX.json')),d=read('CONVERSION_ACCEPTANCE.md'),s=read('THE_HALF_SECOND_YOUR_MIND_MISSES.md');
let n=0;const ok=(x,t)=>{assert.ok(x,t);n++};const main=x=>x.match(/<main id="main">[\s\S]*?<\/main>/)?.[0];
ok(main(a)===main(b),'A/B main parity');
for(const [variant,txt] of [['A',a],['B',b]]) {ok(/<button type="button" disabled/.test(txt),variant+' merchant button must be disabled');ok(/prospective commission disclosure/i.test(txt),variant+' disclosure missing');ok(txt.indexOf('Prospective commission disclosure')<txt.indexOf('<button'),variant+' disclosure must precede button');ok(!/<script\b|<form\b|<iframe\b|autoplay|<video\b/i.test(txt),variant+' forbidden active media/script/form');ok(!/<a[^>]*href="https?:\/\/(zen12|affiliates\.inspire3|hypnosislive|brainwaveshots)/i.test(txt),variant+' merchant link active');ok(/noindex,nofollow/.test(txt),variant+' noindex missing');ok(/https:\/\/finalvestige.com\/focus\//.test(txt),variant+' fieldbook absent');}
ok(/<svg role="img"/.test(b),'SVG needs text alternative');
ok(/transcript/i.test(b),'transcript missing');
ok((v.match(/-->/g)||[]).length===6,'six VTT cues');
ok(v.includes('00:00:35.000 --> 00:00:42.000'),'42 second duration');
for(const term of ['Perception &amp; Attention','History of Suggestion','Practice &amp; Reflection','Tools Under Review'])ok(h.includes(term),'hub stream missing '+term);
ok(m.commercial_gates.length===32&&m.commercial_gates.every(g=>g.status==='HOLD'),'all 32 commercial holds closed');
ok(m.claims.some(c=>c.claim.includes('equals one hour')&&c.status.includes('DO_NOT_ENDORSE')),'equivalence not excluded');
ok(d.includes('NOT COMPUTABLE')&&d.includes('Asset ID unverified'),'attribution boundaries');
ok(s.includes('Raymond')&&s.includes('Slagter')&&s.includes('Puységur'),'source trail');
console.log('PASS '+n+'/ '+n+' static checks (source only; not native browser/merchant verification)');
