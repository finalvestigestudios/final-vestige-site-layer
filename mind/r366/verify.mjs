/**
 * Mind R366 offline/source-only acceptance gates.
 * Run from a checked-out branch: node mind/r366/verify.mjs
 * Tests do not touch WP, any merchant, Jetpack, analytics or user data.
 * This file has not been run natively unless a separate exact-SHA report explicitly confirms it.
 */
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url));
const load=f=>fs.readFileSync(path.join(dir,f),'utf8');
const A=load('ZEN12_A_INDEPENDENT_GUIDE.html'),B=load('ZEN12_B_OPTIONAL_FILM_GUIDE.html');
const hub=load('MIND_ARCHIVE_WORDPRESS_REVIEW_ONLY.html');
const article=load('THE_VOICE_THAT_WASNT_ON_THE_RECORDING.md');
const caps=load('ORIGINAL_42S_CAPTIONS.vtt');
const matrix=JSON.parse(load('CLAIM_SOURCE_AUTHORIZATION_MATRIX.json'));
const handoff=load('CONVERSION_ACCEPTANCE_AND_OWNER_HANDOFF.md');
let passed=0;
const ok=(p,label)=>{assert.ok(p,label);passed++};
const merchantAnchor=s=/<a\b[^>]*\bhref\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\./i.test(s);
const unsafe=s=/<script\b|<iframe\b|<form\b|<input\b|<video\b|\sonclick\s*=|\sonsubmit\s*=|\sautoplay\b|\bdataLayer\b|\bgtag\s*\(/i.test(s);
const nativeDisabled=s=/<button\b[^>]*\sdisabled(?:\s|>)[^>]*>/.test(s);
const disclose=s=>/Affiliate disclosure:[\s\S]*?Final Vestige may earn a commission at no additional cost to you/.test(s);
const safe=s=>nativeDisabled(s)&&disclose(s)&&!merchantAnchor(s)&&!unsafe(s);
const normalized=s=>s.replace(/<section class="film" data-optional-film[\s\S]*?<\/section>/,'').replace(/Version [AB]/g,'Version X').replace(/Draft [AB]/g,'Draft X');
ok(article.trim().split(/\s+/).length>=2300,'substantive new original investigation');
ok(article.includes('status: SOURCE_CONTROL_ONLY_NOT_PUBLISHED'),'draft-only editorial status');
for(const p of ['https://doi.org/10.1038/264746a0','https://doi.org/10.1371/journal.pone.0207160','https://doi.org/10.1371/journal.pone.0202908','https://doi.org/10.1371/journal.pone.0286023','https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/','https://finalvestige.com/focus/'])ok(article.includes(p),'article source '+p);
for(const p of ['not a test of suggestibility','not evidence that','seller','no product','one-year','not independently tested'])ok(article.toLowerCase().includes(p.toLowerCase()),'article nuance '+p);
ok(normalized(A)===normalized(B),'A/B core copy identical after optional film removal');
for(const [name,s] of [['A',A],['B',B]]){
ok(s.includes('name="viewport"'),name+' responsive');
ok(s.includes('lang="en"'),name+' explicit language');
ok(s.includes('noindex,nofollow'),name+' protected indexing');
ok(s.includes('Skip to guide'),name+' keyboard skip');
ok(s.includes('prefers-reduced-motion'),name+' motion styles');
ok(s.includes('https://finalvestige.com/focus/'),name+' existing Fieldbook');
ok(s.includes('https://doi.org/10.1371/journal.pone.0286023'),name+' primary review');
ok(s.includes('https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance'),name+' FTC');
ok(safe(s),name+' truly disabled, disclosed, no merchant link or unsafe markup');
ok(s.includes('NOT ACTIVE'),name+' offer visibly inactive');
ok(!/\b(?:price is|pay now|discount ends in)\b/i.test(s),name+' no invented checkout claim');
}
ok(!A.includes('data-optional-film'),'A text only');
ok(B.includes('data-optional-film'),'B optional film treatment');
ok(B.includes('<svg')&&B.includes('role="img"')&&B.includes('posterDesc'),'B original accessible static poster');
ok(B.includes('<details>')&&B.includes('42-second film transcript'),'B full expandable transcript');
ok(B.includes('No encoded film')||B.includes('no encoded film')||B.includes('no encoded'),'B honest nonplayable status');
ok(caps.startsWith('WEBVTT'),'valid VTT header');
const matches=[...caps.matchAll(/(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})/g)];
ok(matches.length===6,'exact 6 caption cues');
const milliseconds=x=>(Number(x[0])*3600+Number(x[1])*60+Number(x[2]))*1000+Number(x[3]);
const times=matches.map(m=>[milliseconds(m.slice(1,5)),milliseconds(m.slice(5,9))]);
ok(times[0][0]===0,'caption starts at 0');
ok(times.at(-1)[1]===42000,'caption ends 42s');
ok(times.every(([s,e],i)=>s<e&&(i===0||s===times[i-1][1])),'captions continuous and non-overlapping');
ok((hub.match(/class="stream"/g)||[]).length===4,'four editorial streams');
ok(hub.includes('https://finalvestige.com/2026/11/02/change-blindness/'),'verified live article');
ok(hub.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'),'historical source bridge');
ok(hub.includes('https://finalvestige.com/focus/'),'free existing funnel');
ok(hub.includes('noindex,nofollow'),'hub noindex');
ok(!merchantAnchor(hub)&&!unsafe(hub),'hub no merchant link, scripts, forms or video');
ok(matrix.claims.length>=40,'40+ evidence decisions');
ok(Object.keys(matrix.sources).length>=16,'16+ independent/seller/FTC source URLs');
ok(matrix.release_gates.length===32,'32 explicit commerce gates');
ok(matrix.release_gates.every(g=>g.state==='HOLD'),'every commerce gate HOLD');
for(const k of ['accepted_publisher','issued_link','allowed_channels','approved_creatives','owned_mind_payhip_sku'])ok(matrix.commerce_authorization[k]==='not_authenticated','cannot invent '+k);
ok(matrix.commerce_authorization.buyer_cta==='DISABLED','no live CTA');
ok(matrix.revenue.net_revenue_per_1000_qualified_human_sessions==='NOT_COMPUTABLE','no fake ROI');
ok(handoff.includes('Grok')&&handoff.includes('Praxxis')&&handoff.includes('Claude'),'creator+engineering ownership retained');
ok(handoff.includes('utm_content')&&handoff.includes('asset_id'),'asset attribution spec');
ok(handoff.includes('7-day')&&handoff.includes('30-day'),'cohorts');
ok(handoff.includes('NOT COMPUTABLE'),'commercial uncertainty');
const mutations=[
s=>s.replace('type="button" disabled','type="button"'),
s=>s.replace('Affiliate disclosure:','Information:'),
s=>s.replace('Final Vestige may earn a commission at no additional cost to you','This is guaranteed to reprogram your brain'),
s=>s+'<a href="https://zen12.com/">Buy now</a>',
s=>s+'<script>console.log("tracker")</script>',
s=>s+'<iframe src="https://example.com/pixel"></iframe>',
s=>s+'<form><input type="email"></form>',
s=>s+'<video autoplay src="/generated.mp4"></video>',
s=>s+'<button onclick="location.href=\'https://example.com\'">Buy</button>'
];
for(const [i,fn] of mutations.entries())ok(!safe(fn(A)),'unsafe markup mutation '+(i+1));
console.log('R366 static/source acceptance: '+passed+'/'+passed+' PASS; 9/9 intentional unsafe modifications rejected. NOT A BROWSER, WP, NATIVE VIDEO, MERCHANT, OR SETTLEMENT TEST.');
