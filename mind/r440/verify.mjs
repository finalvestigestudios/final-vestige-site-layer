/**
 * R440 reproducible local static safety verifier.
 * Run: node mind/r440/verify.mjs from a complete checkout.
 * It does NOT prove WCAG conformance, WordPress sanitization, partner rights,
 * video playback, analytics, Jetpack delivery or paid conversions.
 */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const read = name => readFileSync(new URL(name, import.meta.url), 'utf8');
const names = ['TWELVE_MINUTES_IS_NOT_AN_HOUR.md','ZEN12_A_TEXT_ONLY.html',
  'ZEN12_B_OPTIONAL_FILM_CONCEPT.html','R440_42S_CAPTIONS.vtt',
  'MIND_HUB_WORDPRESS_SOURCE_ONLY.html','CLAIM_SOURCE_PERMISSION_MATRIX.json',
  'OFFER_FUNNEL_CONVERSION_ACCEPTANCE.md'];
const [article,a,b,vtt,hub,json,plan] = names.map(read);
const matrix = JSON.parse(json);
let passed = 0, failed = 0;
const check=(label,truth)=>{
  try { assert.ok(truth,label); passed++; process.stdout.write('PASS '+label+'\n'); }
  catch(e) { failed++; process.stderr.write('FAIL '+label+': '+e.message+'\n'); }
};
const merchantLink = html => /<a\b[^>]*href\s*=\s*["'][^"']*(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(html);
const activeControls=html => /<button\b(?![^>]*\bdisabled\b)[^>]*>[\s\S]*?(?:buy|purchase|merchant offer)/i.test(html);
const security=(label,html)=>{
 check(label+' has no active seller href',!merchantLink(html));
 check(label+' has no script',!/<script\b/i.test(html));
 check(label+' has no iframe',!/<iframe\b/i.test(html));
 check(label+' has no form',!/<form\b/i.test(html));
 check(label+' has no tracker pixel',!/<img\b[^>]*src\s*=\s*["']https?:/i.test(html));
 check(label+' has no active buy button',!activeControls(html));
 check(label+' has no autoplay on video',!/<video\b[^>]*\bautoplay\b/i.test(html));
 check(label+' has responsive viewport',/name="viewport"/i.test(html));
 check(label+' declares language',/<html lang="en">/.test(html));
 check(label+' noindex source draft',/name="robots" content="noindex,nofollow"/.test(html));
 check(label+' keyboard focus styling',/:focus-visible/.test(html));
 check(label+' reduced-motion support',/prefers-reduced-motion/.test(html));
};
security('variant A',a);security('variant B',b);security('hub',hub);
const stripped = b.replace(/<section aria-labelledby="film-title" class="panel">[\s\S]*?<\/section>/,'');
check('A/B buyer-copy parity exact',stripped===a);
check('A includes adjacent prospective disclosure',/Prospective affiliate disclosure:[\s\S]{0,250}<button type="button" disabled/.test(a));
check('B includes adjacent prospective disclosure',/Prospective affiliate disclosure:[\s\S]{0,250}<button type="button" disabled/.test(b));
check('A links established free Focus route',a.includes('https://finalvestige.com/focus/'));
check('B links established free Focus route',b.includes('https://finalvestige.com/focus/'));
check('B original poster semantic title/description',/<svg\b[\s\S]*?<title id="poster-title">/.test(b)&&b.includes('<desc id="poster-desc">'));
check('B transcript available via details',b.includes('<details>')&&b.includes('six scenes'));
check('film is explicitly unencoded',b.includes('not an encoded playable video'));
check('VTT includes WEBVTT header',vtt.startsWith('WEBVTT\n'));
check('VTT contains six complete cues',(vtt.match(/-->/g)||[]).length===6);
check('VTT ends at 42 seconds',vtt.includes('00:00:42.000'));
check('VTT cues have no overlap',(()=>{
 const m=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d\d\d) --> (\d\d):(\d\d):(\d\d)\.(\d\d\d)/g)].map(x=>[Number(x[3])*1000+Number(x[4]),Number(x[7])*1000+Number(x[8])]);return m.length===6&&m.every((r,i)=>r[0]<r[1]&&(i===0||r[0]===m[i-1][1]));
})());
check('matrix 28 claim reviews',matrix.claims.length===28);
check('matrix 28 commercial holds',matrix.commercial_release_gates.length===28 && matrix.commercial_release_gates.every(g=>g.status==='HOLD'&&g.evidence===null));
check('matrix has no earning link',matrix.commerce.earning_link===null && matrix.commerce.cta_enabled===false);
check('matrix has no fictional paid commission',matrix.commerce.settled_commissions===null);
check('matrix net KPI null',matrix.commerce.net_revenue_per_1000_qualified_humans===null);
check('matrix source set FTC+primary+merchant',[matrix.sources.ftc,matrix.sources.health,matrix.sources.basso,matrix.sources.palmer,matrix.sources.review,matrix.sources.zenmain,matrix.sources.zenpromo].every(Boolean));
check('article source Basso',article.includes('https://pubmed.ncbi.nlm.nih.gov/30153464/'));
check('article source Palmer',article.includes('https://doi.org/10.1038/s41598-023-46578-y'));
check('article source meta-analysis',article.includes('https://pmc.ncbi.nlm.nih.gov/articles/PMC10902202/'));
check('article disclaimers',article.includes('no active affiliate link') && article.includes('not Zen12 trials'));
check('article links to genuine Puységur archive',article.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'));
check('hub uses four in-page streams',['id="attention"','id="history"','id="field"','id="tools"'].every(x=>hub.includes(x)));
check('hub preserves existing change-blindness URL',hub.includes('https://finalvestige.com/2026/11/02/change-blindness/'));
check('hub links no merchant domain',!/(?:href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3))/i.test(hub));
check('plan separates click and settlement',plan.includes('affiliate_click_outbound') && plan.includes('merchant_commission_settled'));
check('plan refuses vanity-sales conflation',plan.includes('clicks not orders') || plan.includes('clicks alone') || plan.includes('not orders'));
check('plan says Grok IDs UNMATCHED',plan.includes('Immutable Grok asset_id: UNMATCHED'));
check('plan protects single Jetpack',plan.includes('single Jetpack'));
check('plan holds commerce',plan.includes('commercial HOLD'));
check('plan contains 7/30 cohorts',plan.includes('7- and 30-day cohorts'));
check('plan mentions net/1000',plan.includes('net_revenue_per_1000'));
const unsafe=[
 a.replace('<button type="button" disabled','<button type="button"'),
 a.replace('No such link is active','Click here to buy now'),
 a.replace('<body>','<body><script>alert(1)</script>'),
 a.replace('<body>','<body><iframe src="https://example.org"></iframe>'),
 a.replace('<body>','<body><form><input name="email"></form>'),
 a.replace('<body>','<body><a href="https://zen12.com/secret/">Merchant offer</a>'),
 a.replace('<body>','<body><img src="https://tracker.invalid/pixel">'),
 a.replace('name="robots" content="noindex,nofollow"','name="robots" content="index,follow"'),
 b.replace('<section aria-labelledby="film-title" class="panel">','<section aria-labelledby="film-title" class="panel"><video autoplay>'),
 b.replace('<details>',''),
];
const detectors=[
 x=>activeControls(x),x=>!x.includes('No such link is active'),x=>/<script\b/i.test(x),
 x=>/<iframe\b/i.test(x),x=>(/<form\b/i).test(x),x=>merchantLink(x),
 x=>(/<img\b[^>]*src\s*=\s*["']https?:/i).test(x),
 x=>!x.includes('noindex,nofollow'),x=>/<video autoplay/.test(x),x=>!x.includes('<details>')
];
unsafe.forEach((variant,i)=>check('unsafe synthetic mutation '+(i+1)+' detected',detectors[i](variant)));
process.stdout.write('RESULT '+passed+' passed; '+failed+' failed\n');
if(failed) process.exitCode=1;
