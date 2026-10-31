'use strict';
/*
 * Read-only source QA; does not reach WordPress, an affiliate, or a browser.
 * node mind/mcgurk-zen12-r27/qa.cjs
 * node mind/mcgurk-zen12-r27/privacy-off.cjs --selftest
 */
const fs=require('fs'),path=require('path'),assert=require('assert');
const dir=__dirname,read=n=>fs.readFileSync(path.join(dir,n),'utf8');
const a=read('zen12-guide-a.wp.html'),b=read('zen12-guide-b.wp.html'),article=read('investigation.md'),
  articleHtml=read('investigation.wp.html'),hub=read('mind-hub-alternative.wp.html'),
  poster=read('zen12-40s-poster.svg'),vtt=read('zen12-40s-captions-draft.vtt'),
  matrix=read('claim-evidence-permissions.csv'),brief=read('film-protocol.md');
let pass=0;const ok=(condition,name)=>{assert.ok(condition,name);pass++};
const no=(s,re,name)=>ok(!re.test(s),name);
const filmSection=/<section aria-labelledby="video-candidate">[\s\S]*?<\/section>/;
ok(!filmSection.test(a),'A no film');
ok(filmSection.test(b),'B film');
ok(b.replace(filmSection,'')===a.replace('<!-- VIDEO SLOT -->',''),'A/B exact parity');
for(const [label,s] of [['A',a],['B',b]]){
  ok(/Beginner[\s\S]*?24 MP3s/.test(s),label+' beginner');
  ok(/Premium[\s\S]*?48 MP3s/.test(s),label+' premium');
  ok(/Advanced[\s\S]*?24 MP3s/.test(s),label+' advanced');
  ok(/first six levels/i.test(s),label+' beginner coverage');
  ok(/final six levels/i.test(s),label+' advanced coverage');
  ok(/four listening styles/i.test(s),label+' formats');
  ok(/not independently established results/i.test(s),label+' seller boundary');
  ok(/52-page Seven Day Focus Fieldbook/.test(s),label+' one focus funnel');
  ok(s.indexOf('Commission disclosure:')>0&&s.indexOf('Commission disclosure:')<s.indexOf('<button'),'FTC near CTA');
  ok(/disabled aria-disabled="true"/.test(s),label+' disabled CTA');
  no(s,/<a[^>]+href="https?:\/\/(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com)/i,label+' no merchant URL');
  no(s,/<(script|iframe|form|input|video)\b/i,label+' no script/embed/form/unhosted player');
  no(s,/autoplay|tracking pixel|window\.location|dataLayer\.push/i,label+' no activation');
  no(s,/id="user|session_id=|fbclid=|gclid=/i,label+' no personal data');
  ok(/prefers-reduced-motion/.test(s),label+' reduced motion');
  ok(/:focus-visible/.test(s),label+' keyboard');
  ok(/<caption>/.test(s)&&/<th scope="col">/.test(s),label+' accessible table');
  ok(/aria-label="Prospective commercial relationship"/.test(s),label+' disclosure marker');
  ok(/<h1>/.test(s)&&/<h2>/.test(s),label+' heading semantics');
}
ok(article.length>9000,'substantive independent article');
ok(article.includes('10% to 60%'),'study range qualified');
ok(article.includes('not a global prevalence estimate'),'range population caveat');
ok(article.includes('not a validated replication'),'exercise disclaimer');
ok(article.includes('23 December 1976'),'original paper date');
ok(article.includes('10.1038/264746a0'),'primary source');
ok(article.includes('33884572'),'modern challenge');
ok(article.includes('9894660'),'review');
no(article,/buy now|use my link|guaranteed results/i,'article no sale');
ok(articleHtml.includes('<article')&&articleHtml.includes('fvm27'),'WordPress article markup');
no(articleHtml,/<script|<iframe/i,'article no embeds');
ok(hub.includes('PR #172'),'original hub preserved');
ok(hub.includes('puysegurs-animal-magnetism-files'),'real history link');
ok(hub.includes('finalvestige.com/focus/'),'one existing resource');
no(hub,/<form|jetpack-subscriptions/i,'no duplicate signup');
ok(poster.includes('<svg')&&poster.includes('<title'),'original poster');
no(poster,/<script|onload=|xlink:href|<image\b/i,'poster offline and safe');
ok(vtt.startsWith('WEBVTT'),'caption format');
ok(vtt.includes('00:00:40.000'),'40 sec cues');
ok(brief.includes('not synced captions'),'caption honesty');
ok(matrix.split('\n').length>=47,'46 matrix claims');
ok(matrix.includes('UNSUBSTANTIATED_PRODUCT_CLAIM'),'claim status');
ok(matrix.includes('PARTNER_APPROVAL'),'partner gate');
const privacy=require('./privacy-off.cjs');
ok(privacy.ENABLED===false,'tracking off');
ok(privacy.selfTest()>=30,'privacy executable checks');
function negativeMutants(){
 let n=0;
 const reject=(x,condition)=>{assert.ok(!condition(x));n++};
 reject(a.replace('disabled aria-disabled="true"',''),s=>/disabled aria-disabled="true"/.test(s));
 reject(a.replace('Commission disclosure:','Hidden commission:'),s=>s.indexOf('Commission disclosure:')>0);
 reject(a.replace('24 MP3s','18 MP3s'),s=>/Beginner[\s\S]*?24 MP3s/.test(s));
 reject(a.replace('48 MP3s','96 MP3s'),s=>/Premium[\s\S]*?48 MP3s/.test(s));
 reject(a+'<script src="https://tracker.invalid/"></script>',s=>!/<script\b/i.test(s));
 reject(a+'<a href="https://zen12.com/?aff=unverified">Buy</a>',s=>!/<a[^>]+href="https?:\/\/zen12\.com/i.test(s));
 reject(hub+'<form><input type="email"></form>',s=>!/<form/i.test(s));
 reject(vtt.replace('00:00:40.000','00:00:39.000'),s=>s.includes('00:00:40.000'));
 return n;
}
ok(negativeMutants()===8,'8 negative guard mutants rejected');
console.log('R27 source QA PASS '+pass+' guards, 8/8 negative mutants. No live/browser/WP/CI assertions.');
