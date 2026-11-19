// Mind R483 local/offline deterministic tests (Node.js >=18).
// Usage from repo root: node mind/r483/qa.test.cjs
// No network, no paid services and no persistent test state.
const fs=require('node:fs');
const assert=require('node:assert/strict');
const path=require('node:path');
const root=__dirname;
const read=n=>fs.readFileSync(path.join(root,n),'utf8');
const A=read('HYPNOSIS_LIVE_GUIDE_A_TEXT.html'),B=read('HYPNOSIS_LIVE_GUIDE_B_STORYBOARD.html');
const article=read('THE_WORD_YOUR_EYES_REFUSE_TO_IGNORE.md');
const hub=read('MIND_ARCHIVE_GUTENBERG_SOURCE_ONLY.html');
const matrix=JSON.parse(read('CLAIM_PERMISSION_SOURCE_AND_RELEASE_MATRIX.json'));
const docket=read('CREATOR_OFFER_FUNNEL_NET_REVENUE_AND_QA.md'),captions=read('OPTIONAL_STROOP_FILM_42S.vtt');
let n=0;
const check=(name,predicate)=>{assert.ok(predicate,name);n++};
for(const [name,html] of [['A',A],['B',B]]){
 check(name+' html/lang',html.startsWith('<!doctype html>')&&html.includes('<html lang="en">'));
 check(name+' viewport',html.includes('name="viewport"'));
 check(name+' noindex',html.includes('noindex,nofollow'));
 check(name+' native disabled CTA',/<button[^>]+disabled\b[^>]*>/.test(html));
 check(name+' no merchant payment href',!/href=["'][^"']*(?:hypnosislive\.com|refersion|zen12\.com\/secret)/i.test(html));
 check(name+' no third-party tracking',!/<script\b|<iframe\b|<form\b/i.test(html));
 check(name+' near-link disclosure',html.indexOf('Prospective affiliate disclosure')>=0&&Math.abs(html.indexOf('Prospective affiliate disclosure')-html.indexOf('<button class="cta"'))<750);
 check(name+' no actual ad price',!/\$\d+(?:\.\d{2})?/.test(html));
 check(name+' existing Focus only',html.includes('https://finalvestige.com/focus/'));
 check(name+' explicit status',html.includes('SOURCE-ONLY / DRAFT'));
 check(name+' accessibility',html.includes('focus-visible')&&html.includes('prefers-reduced-motion'));
 check(name+' no medical guarantee',html.includes('not</strong> established'));
}
const bOnly=/\<details class="film" data-variant-only="b"\>[\s\S]*?\<\/details\>/;
check('B visual block',bOnly.test(B)&&!bOnly.test(A));
check('A/B editorial body identical',B.replace(bOnly,'')===A);
check('B storyboard explicit',B.includes('not a playable video yet'));
check('B includes accessible SVG',B.includes('role="img"'));
check('B has full transcript',B.includes('42-second narration transcript'));
check('captions valid',captions.startsWith('WEBVTT')&&(captions.match(/-->/g)||[]).length===6);
check('captions terminate at 42s',captions.includes('00:00:42.000'));
check('hub 4 streams',(hub.match(/<article\b/g)||[]).length===4);
check('hub no newsletter duplicate',!/<form\b/.test(hub));
check('hub existing archive',hub.includes('puysegurs-animal-magnetism-files'));
check('source-led article',article.includes('https://doi.org/10.1037/h0054651')&&article.includes('https://pubmed.ncbi.nlm.nih.gov/12470132/'));
check('2006 suggestion nuance',article.includes('without that induction'));
check('article sources are not affiliate URLs',!article.includes('refersion.com'));
check('matrix source count',matrix.sources.length===17);
check('matrix claim count',matrix.claims.length===26);
check('commercial gates all closed',matrix.release_gates.length===26&&matrix.release_gates.every(x=>x.status==='not-cleared'));
check('all matrix claim sources exist',matrix.claims.every(c=>c.evidence.every(id=>matrix.sources.some(s=>s.id===id))));
check('docket distinguishes sale from outbound',docket.includes('affiliate_outbound')&&docket.includes('merchant_confirmed_paid_order'));
check('docket 3 creator map rows',docket.includes('TBD_STROOP')&&docket.includes('TBD_BLINDNESS')&&docket.includes('TBD_MESMER'));
check('privacy',docket.includes('No browser fingerprinting')&&docket.includes('No extra tracking scripts'));
check('net revenue unknown',docket.includes('NOT COMPUTABLE'));
const unsafe=[
 [A.replace('disabled aria-describedby','aria-describedby'),'disabled CTA removal'],
 [A.replace('Prospective affiliate disclosure:','No commission disclosure:'),'disclosure removed'],
 [A.replace('class="cta"','class="cta" formaction="https://evil.example/checkout"'),'injected action'],
 [B.replace('not a playable video yet','playable video ready'),'false video readiness'],
 [docket.replace('NOT COMPUTABLE','100.00'),'manufactured revenue'],
 [A.replace('not</strong> established','proven</strong> established'),'unsupported efficacy']
];
const guard=(html)=>/<button[^>]+disabled\b[^>]*>/.test(html)&&!/<button[^>]+formaction=/.test(html)&&html.includes('Prospective affiliate disclosure:')&&html.includes('not</strong> established');
const caught=[
 !guard(unsafe[0][0]),!guard(unsafe[1][0]),!guard(unsafe[2][0]),
 !unsafe[3][0].includes('not a playable video yet'),
 !unsafe[4][0].includes('NOT COMPUTABLE'),
 !guard(unsafe[5][0])];
check('6 deliberately unsafe mutations caught',caught.every(Boolean));
console.log('R483 QA '+n+'/'+n+' passed; 6/6 deliberate unsafe synthetic mutations detected. Source-only checks, not browser, WordPress, video playback, merchant or real buyer tests.');
