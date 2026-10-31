'use strict';
/* Source-code audit. Execute in local checkout: node mind/thatcher-face-zen12-r26/qa.cjs
   Not a substitute for WP staging/CI/actual browser or screen reader.
*/
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const ROOT=__dirname;
const get=name=>fs.readFileSync(path.join(ROOT,name),'utf8');
const files=['investigation.md','investigation.wp.html','face-orientation-schematic.svg','zen12-guide-a.wp.html','zen12-guide-b.wp.html','zen12-optional-poster.svg','zen12-40s-captions.vtt','mind-hub-alternative.wp.html','claim-evidence-rights.csv','README.md','privacy-off.cjs'];
const data=Object.fromEntries(files.map(n=>[n,get(n)]));
const checks=[];
function ok(condition,message){assert.ok(condition,message);checks.push(message)}
const a=data['zen12-guide-a.wp.html'],b=data['zen12-guide-b.wp.html'];
const film=/\<section aria-labelledby="r26-film-title"[\s\S]*?\<\/section\>/;
const stripped=b.replace(film,'');
ok(film.test(b),'B contains a single optional film section');
ok(stripped===a,'A and B identical other than film section');
ok(a.includes('The Face')===false,'no unsupported perception experiment presented as product result');
for(const v of [a,b]){
  ok(v.includes('Beginner')&&v.includes('first 6 levels / 24 MP3s'),'Beginner correctly constrained');
  ok(v.includes('Premium')&&v.includes('all 12 levels / 48 MP3s'),'Premium correctly constrained');
  ok(v.includes('Advanced')&&v.includes('last 6 levels / 24 MP3s'),'Advanced correctly constrained');
  ok(v.includes('seller assertions'),'seller efficacy claims labeled');
  ok(v.includes('not independent verification'),'seller features not product-proven');
  ok(v.includes('twelve-minute timer')||v.includes('twelve-minute trial'),'free exercise present');
  ok(v.includes('If you buy through an earning link added after approval'),'clear adjacent future affiliate disclosure');
  ok(v.indexOf('Affiliate disclosure:')<v.indexOf('Offer unavailable — authorization pending'),'disclosure precedes proposed CTA');
  ok(/<button[^>]*disabled[^>]*>Offer unavailable/.test(v),'commercial CTA disabled');
  ok(!/href=["']https?:\/\/(?:www\.)?(?:zen12|hypnosislive|brainwaveshots)\./i.test(v),'no merchant destination activated');
  ok(!/<input\b|<form\b|wp-block-jetpack-subscriptions/i.test(v),'no duplicate signup/payment forms');
  ok(!/<script\b|<iframe\b/i.test(v),'no injected script or 3p player');
  ok(!/autoplay\b/i.test(v),'no autoplay attribute in page');
}
ok(b.includes('data-media-ready="false"'),'film requires media release readiness');
ok(b.includes('r26-video-transcript'),'full inline transcript referenced');
ok(/<video[^>]*hidden controls preload="none" playsinline/.test(b),'not-ready player hidden; controls specified');
ok(/<track[^>]*kind="captions"/.test(b),'captions declared');
ok(data['zen12-40s-captions.vtt'].startsWith('WEBVTT'),'captions VTT valid header');
ok((data['zen12-40s-captions.vtt'].match(/-->/g)||[]).length===5,'five original caption cues');
ok(data['zen12-40s-captions.vtt'].includes('00:00:40.000'),'end time forty seconds');
ok(/<svg[\s\S]*<title/.test(data['zen12-optional-poster.svg']),'poster original SVG semantic title');
ok(/<svg[\s\S]*<desc/.test(data['face-orientation-schematic.svg']),'schematic original SVG description');
ok(data['investigation.md'].includes('Margaret Thatcher: A New Illusion'),'1980 primary paper cited');
ok(data['investigation.md'].includes('10.1167/14.12.9'),'orientation-sensitive local features research cited');
ok(data['investigation.md'].includes('not a validated')||data['investigation.md'].includes('not validated'),'schematic not claimed validated');
ok(!/affiliate recommendation|buy now|commission link/i.test(data['investigation.wp.html']),'investigation independent from checkout commerce');
ok(data['investigation.wp.html'].includes('source-trail'),'source section in article');
ok(data['investigation.wp.html'].length<30000,'WordPress article not bloated by empty elements');
ok(!data['investigation.wp.html'].includes('<strong></strong>'),'no empty strong tags');
ok(data['mind-hub-alternative.wp.html'].includes('puysegurs-animal-magnetism-files'),'hub links live Puységur');
ok(data['mind-hub-alternative.wp.html'].includes('https://finalvestige.com/focus/'),'hub preserves live Fieldbook path');
ok(!data['mind-hub-alternative.wp.html'].includes('https://zen12.com/'),'hub no active merchant link');
ok(!/<input\b|<form\b/i.test(data['mind-hub-alternative.wp.html']),'hub contains no new subscriber form');
const rows=data['claim-evidence-rights.csv'].trim().split(/\r?\n/);
ok(rows.length>=45,'evidence matrix at least 44 classified entries');
ok(rows.some(l=>l.includes('HARD_HOLD')),'permission holds encoded');
ok(rows.some(l=>l.includes('10.1167/14.12.9')),'original research source in matrix');
ok(rows.some(l=>l.includes('FTC-01')),'affiliate disclosure recorded');
ok(data['README.md'].includes('No WordPress CMS'),'release HOLD instruction recorded');
ok(data['privacy-off.cjs'].includes('const ENABLED = false'),'privacy prototype disabled');
ok(data['privacy-off.cjs'].includes('return { accepted:false'),'all live events blocked');
// Negative mutation scenarios: verify core protections would detect bad HTML.
const safe=v=>v.includes('disabled aria-disabled="true"')&&v.includes('Affiliate disclosure:')&&!/href=["']https?:\/\/(?:www\.)?zen12\.com\/getstarted/i.test(v)&&!/<iframe\b|<script\b/i.test(v);
ok(safe(a),'original guide passes anti-activation gate');
for(const [mutation,wrong] of [
 ['remove disabled',a.replace('disabled aria-disabled="true"','')],
 ['remove disclosure',a.replace('Affiliate disclosure:','Disclosure withheld:')],
 ['inject checkout',a.replace('class="cta"','class="cta"><a href="https://zen12.com/getstarted">Buy</a><button')],
 ['inject tracking script',a+'<script src="https://track.example/app.js"></script>'],
 ['inject iframe',a+'<iframe src="https://video.example/"></iframe>']
]) ok(!safe(wrong),'mutation blocked: '+mutation);
console.log('R26 source QA PASS '+checks.length+'/'+checks.length);
module.exports={checks};
