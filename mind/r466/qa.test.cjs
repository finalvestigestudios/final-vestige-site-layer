// R466 native Node tests — AUTHORING ONLY until run in a real checkout.
// Run: node mind/r466/qa.test.cjs from the repository root.
// No dependencies, no network, no payment account, no WP mutation.
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const dir=__dirname;
const read=n=>fs.readFileSync(path.join(dir,n),'utf8');
const A=read('ZEN12_A_TEXT_GUIDE.html'), B=read('ZEN12_B_OPTIONAL_42S_GUIDE.html');
const hub=read('MIND_HUB_WORDPRESS_SOURCE_ONLY.html'), article=read('THE_SUGGESTION_BEFORE_THE_TRANCE.md');
const vtt=read('ZEN12_42S_CONCEPT.vtt'), matrix=JSON.parse(read('PRODUCT_CLAIM_PARTNER_RELEASE_MATRIX.json'));
const acceptance=read('OFFER_TO_REVENUE_ACCEPTANCE.md');
const results=[];
function test(name,fn){try{fn();results.push({name,pass:true});process.stdout.write('PASS '+name+'\n')}catch(e){results.push({name,pass:false});process.stderr.write('FAIL '+name+': '+e.message+'\n')}}
const justCore=html=>html.substring(html.indexOf('<header>'));
const noActiveMerchant=html=>!/<a\s[^>]*href\s*=\s*["'][^"']*(affiliates\.inspire3\.com|buy\.zen12\.com|payhip\.com)/i.test(html);
const noAutoplay=html=>!/<(?:video|audio)[^>]*\sautoplay(?:\s|>|=)/i.test(html);
const disabled=html=>/<button[^>]+disabled\s+aria-disabled="true"[^>]*>Purchase option unavailable/.test(html);
const adjacent=html=>{const d=html.indexOf('Prospective disclosure:'),b=html.indexOf('<button class="btn"');return d>=0&&b>d&&b-d<475};
[
['same substantive buyer copy',()=>assert.equal(justCore(A),justCore(B))],
['HTML A has accessible language',()=>assert.match(A,/<html lang="en">/)],
['HTML B has accessible language',()=>assert.match(B,/<html lang="en">/)],
['responsive viewport A',()=>assert.match(A,/name="viewport"/)],
['responsive viewport B',()=>assert.match(B,/name="viewport"/)],
['no active earning URLs',()=>assert.ok(noActiveMerchant(A)&&noActiveMerchant(B))],
['both merchant buttons disabled natively',()=>assert.ok(disabled(A)&&disabled(B))],
['affiliate disclosure visually adjacent',()=>assert.ok(adjacent(A)&&adjacent(B))],
['plain-English commission language',()=>assert.ok(A.includes('may earn a commission'))],
['no extra capture forms',()=>assert.ok(!/<form\b/i.test(A+B))],
['no executable scripts',()=>assert.ok(!/<script\b/i.test(A+B+hub))],
['no auto play',()=>assert.ok(noAutoplay(A)&&noAutoplay(B))],
['no required JavaScript or third-party video',()=>assert.ok(!B.includes('<iframe'))],
['original concept poster accessible',()=>assert.match(B,/<svg role="img" aria-labelledby="poster-title poster-desc"/)],
['optional film full transcript',()=>assert.ok(B.includes('00–07:')&&B.includes('35–42:'))],
['captions last to exactly 42s',()=>assert.ok(vtt.includes('00:00:42.000'))],
['six VTT caption cues',()=>assert.equal(vtt.match(/ --> /g).length,6)],
['poster controls accessible without JS',()=>assert.match(B,/<details><summary>/)],
['no mobile one-column omission',()=>assert.ok(A.includes('max-width:760px')&&B.includes('grid-template-columns:1fr'))],
['no new signup or welcome override',()=>assert.ok(hub.includes('no new signup form')===false || !hub.includes('<form'))],
['all four hub editorial streams',()=>['Perception &amp; Attention','Perception & Attention','History of Suggestion','Practice & Reflection','Tools Under Review'].slice(1).forEach(s=>assert.ok(hub.includes(s)))],
['real published archive routes',()=>assert.ok(hub.includes('/puysegurs-animal-magnetism-files/')&&hub.includes('/2026/11/02/change-blindness/'))],
['primary research cited in article',()=>['15823785','16649870','17447869','34297008','41217756'].forEach(id=>assert.ok(article.includes(id)))],
['seller claim evidence separated',()=>assert.ok(article.includes('not a')&&article.includes('source'))],
['no unapproved product price',()=>assert.ok(!A.includes('$37')&&!B.includes('$87'))],
['release gates all on hold',()=>assert.ok(matrix.release_gates.length>=30&&matrix.release_gates.every(g=>g.status==='HOLD'))],
['matrix contains no actual earning link',()=>assert.equal(matrix.kpi.net_revenue_per_1000_sessions,null)],
['claim matrix includes named FTC rules',()=>assert.ok(matrix.sources.S21.includes('ftc.gov')&&matrix.sources.S22.includes('ftc.gov'))],
['revenue plan rejects click as sale',()=>assert.ok(acceptance.includes('Never infer a purchase from click or signup'))],
['no actual film falsely claimed',()=>assert.ok(B.includes('no playable film yet'))],
].forEach(([name,fn])=>test(name,fn));
const changed=A.replace('disabled aria-disabled="true"','');test('negative control catches enabled purchase button',()=>assert.ok(!disabled(changed)));
const leaked=A.replace('</body>','<script src="https://tracker.example/collect.js"></script></body>');test('negative control catches tracking insertion',()=>assert.ok(/<script\b/i.test(leaked)));
const falsified=JSON.parse(JSON.stringify(matrix));falsified.release_gates[0].status='PASS';test('negative control catches false commercial release status',()=>assert.ok(!falsified.release_gates.every(g=>g.status==='HOLD')));
const fails=results.filter(r=>!r.pass);process.stdout.write('TOTAL '+(results.length-fails.length)+'/'+results.length+' passed\n');if(fails.length)process.exitCode=1;
