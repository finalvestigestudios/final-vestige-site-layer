'use strict';
/* R34 reproducible read-only source checks; run: node mind/chevreul-zen12-r34/qa-r34.cjs
 * This verifies source contracts, NOT WordPress staging/browser behavior or hosted media.
 */
const fs=require('fs'), path=require('path');
function runTests(){
  const report={passed:0,failed:0,failures:[],mutationsKilled:0};
  const read=f=>fs.readFileSync(path.join(__dirname,f),'utf8');
  function check(pred,label){if(pred){report.passed++;return;}report.failed++;report.failures.push(label);}
  const art=read('investigation-chevreul.md'), ah=read('investigation-chevreul.wp.html');
  const guide=read('zen12-independent-guide.md'), a=read('zen12-a-text.wp.html'),b=read('zen12-b-film.wp.html');
  const hub=read('mind-hub-alternative.wp.html'), matrix=read('claims-and-permissions.csv'), vtt=read('film-chevreul.vtt');
  const story=read('film-storyboard-transcript.md'), plan=read('navigation-and-organic-plan.md'), privacy=read('privacy-hard-off.cjs');
  const words=s=>s.trim().split(/\s+/).filter(Boolean).length;
  const hasLink=(s,domain)=>new RegExp('<a\\b[^>]*href=["\\x27]https?:\\/\\/'+domain.replace(/\./g,'\\.')+'\\b','i').test(s);
  const htmlSafe=s=>!/<script\b|<iframe\b|<form\b|<input\b|\bonload\s*=|\bonerror\s*=|javascript:|<video\b|<audio\b[^>]*\bautoplay\b/i.test(s);
  const commerceOff=s=>!hasLink(s,'zen12.com') && !hasLink(s,'affiliates.inspire3.com') && !/<a\b[^>]+(affiliate|buy-now|checkout)/i.test(s) && !/<button\b/i.test(s);
  const disclosureNearCTA=s=>{const block=s.match(/<aside class="disclosure"[\s\S]*?<\/aside>/i)?.[0]||'';const d=block.indexOf('If you purchase through this link, Final Vestige may earn a commission');const c=block.indexOf('Review the current Zen12 offer');return d>=0&&c>d&&c-d<800&&block.slice(d,c).includes('no additional cost');};
  const sourceLinks=['wellcomecollection.org/works/k532hmn2','doi.org/10.1016/j.humov.2021.102879','doi.org/10.1080/00221309.1976.9710871','pubmed.ncbi.nlm.nih.gov/35184700/'];
  check(words(art)>=2000,'investigation >=2000 words');
  check(words(guide)>=1500,'buyer guide >=1500 words');
  check(art.includes('Puységur'),'historical bridge');
  for(const link of sourceLinks)check(art.includes(link),'source '+link);
  for(const link of sourceLinks.slice(0,3))check(ah.includes(link),'wp source '+link);
  for(const phrase of ['not a retrospective diagnosis','not a diagnostic test','one kind of involuntary-looking movement'])check(art.toLowerCase().includes(phrase.toLowerCase()),'evidence limit '+phrase);
  check(!/commission|affiliate offer|buy now/i.test(art),'editorial no commerce');
  check(ah.includes('class="fv-ideomotor"'),'article scoped CSS');
  check(htmlSafe(ah),'article no script or tracking');
  for(const phrase of ['Beginner','Premium','Advanced','24 MP3','48 MP3','twelve-minute quiet routine','not purchased','refund','mobile-phone field'])check(guide.toLowerCase().includes(phrase.toLowerCase()),'guide '+phrase);
  check(/Ingendoh, Posny and Heine/.test(guide),'reviewer attribution correct');
  check(!/Garcia-Argibay et al/.test(guide),'wrong attribution absent');
  check(/fourteen EEG studies/i.test(guide),'guide scientific context');
  for(const [variant,s] of [['A',a],['B',b]]){
    check(s.includes('data-pilot-variant="'+variant+'"'),variant+' variant identity');
    check(s.includes('class="fvz"'),variant+' scoped layout');
    check(htmlSafe(s),variant+' no JS/video until hosted');
    check(commerceOff(s),variant+' no merchant anchor/button');
    check(disclosureNearCTA(s),variant+' near-action commission disclosure');
    check(s.includes('aria-disabled="true"'),variant+' disabled action state');
    check(s.includes('one existing Jetpack funnel'),variant+' one-funnel language');
    check(s.includes('https://finalvestige.com/focus/'),variant+' Focus link');
    check(s.includes('https://pubmed.ncbi.nlm.nih.gov/37205669/'),variant+' review link');
    check(!/\$\s*\d/.test(s),variant+' no volatile offer price');
    check(!/\bid=["\x27](?!fvz-)/i.test(s),variant+' scoped IDs');
  }
  const start='<h1 id="fvz-title">', end='<aside class="disclosure"';
  function core(s){return s.slice(s.indexOf(start),s.indexOf(end));}
  check(core(a)===core(b),'identical substantive A/B guide core');
  check(b.includes('complete proposed 40-second transcript'),'B accessible transcript');
  check(b.includes('concept only'),'B no fake film availability');
  check(!a.includes('class="film"'),'A text-only');
  check(b.includes('role="img"')&&b.includes('aria-label="Original illustrated poster'),'B accessible poster');
  check(!/<(?:video|audio)\b[^>]*\bautoplay\b/i.test(b),'B no autoplay attribute');
  check(hub.includes('aria-labelledby="fv-mind-hub-title"'),'hub labeled');
  check(htmlSafe(hub),'hub no forms/scripts');
  check(hub.includes('PR #172 is authoritative'),'hub preserves main owner');
  check(hub.includes('NO LIVE LINK'),'unpublished cards not linked');
  check(hub.includes('https://finalvestige.com/focus/'),'hub links existing lead magnet');
  check(hub.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'),'hub connects history');
  check(!hasLink(hub,'zen12.com'),'hub no merchant link');
  const csvLines=matrix.trim().split(/\r?\n/);
  check(csvLines.length===51,'50 source-mapped claims');
  check(matrix.includes('https://zen12.com/getstarted'),'checkout evidence');
  check(matrix.includes('https://inspire3.com/ll/'),'specific swipe scope');
  check(matrix.includes('UNKNOWN'),'missing affiliate approval explicit');
  check(matrix.includes('REJECT'),'unsupported effects rejected');
  check(matrix.includes('FTC1')&&matrix.includes('FTC2'),'FTC references');
  check(vtt.startsWith('WEBVTT'),'caption file type');
  const times=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d\d\d) --> (\d\d):(\d\d):(\d\d)\.(\d\d\d)/g)];
  check(times.length===6,'six cues');
  const toMs=(m,k)=>((+m[k]*3600)+(+m[k+1]*60)+(+m[k+2]))*1000+(+m[k+3]);
  check(times.length>0&&toMs(times[0],1)===0,'start zero');
  check(times.length>0&&toMs(times[times.length-1],5)===40000,'ends 40s');
  for(let i=0;i<times.length;i++){check(toMs(times[i],5)>toMs(times[i],1),'positive cue '+i);if(i>0)check(toMs(times[i-1],5)===toMs(times[i],1),'gapless '+i);}
  check(story.includes('NO Chevreul film render or approved website hosting'),'storyboard film limit');
  check(story.includes('Original')&&story.includes('Carpenter'),'original sourced film plan');
  check(plan.includes('Issue #174')&&plan.includes('PR #172'),'ownership');
  check(plan.includes('k>=10'),'privacy threshold documented');
  check(privacy.includes('const ENABLED = false'),'privacy hard disabled');
  check(!/fetch\(|sendBeacon\(|XMLHttpRequest|localStorage|document\.cookie|navigator\./.test(privacy),'no network/browser collection');
  const mutants=[
    a.replace('If you purchase through this link, Final Vestige may earn a commission',''),
    a.replace('aria-disabled="true"','aria-disabled="false"'),
    a+'<a href="https://zen12.com/getstarted">Buy now</a>',
    a+'<script>alert(1)</script>',
    a+'<form><input type="email"></form>',
    b.replace('complete proposed 40-second transcript','transcript removed'),
    b.replace('concept only','available now'),
    b+'<video controls autoplay src="test.mp4"></video>',
  ];
  const guards=[
    x=>!disclosureNearCTA(x),x=>!x.includes('aria-disabled="true"'),
    x=>!commerceOff(x),x=>!htmlSafe(x),
    x=>!htmlSafe(x),x=>!x.includes('complete proposed 40-second transcript'),
    x=>!x.includes('concept only'),x=>!htmlSafe(x)
  ];
  mutants.forEach((x,i)=>{const killed=guards[i](x);check(killed,'dangerous mutation '+i);if(killed)report.mutationsKilled++;});
  return report;
}
if(typeof module!=='undefined')module.exports={runTests};
if(typeof require!=='undefined'&&typeof module!=='undefined'&&require.main===module){const report=runTests();console.log(JSON.stringify(report,null,2));if(report.failed)process.exitCode=1;}
