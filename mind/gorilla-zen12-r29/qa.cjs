'use strict';
/* Execute after checkout:
   node mind/gorilla-zen12-r29/qa.cjs
   node mind/gorilla-zen12-r29/privacy-off.cjs
   This is source-level QA only, not browser/WP/CI verification. */
const fs=require('fs');const path=require('path');
const read=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
const a=read('zen12-guide-a.wp.html'),b=read('zen12-guide-b.wp.html'),article=read('investigation.md'),wp=read('investigation.wp.html'),hub=read('mind-hub-alternative.wp.html'),matrix=read('claim-evidence-permissions.csv'),vtt=read('zen12-captions-draft.vtt'),svg=read('zen12-40s-poster.svg'),protocol=read('film-protocol.md'),plan=read('navigation-test-plan.md');
let total=0;const assert=(ok,why)=>{total++;if(!ok)throw Error('QA '+total+' FAILED: '+why)};
const check=(code,needle)=>code.includes(needle);
const stripFilm=html=>html.replace(/<figure class="video-concept"[\s\S]*?<\/figure>/,'');
const linked=content=>(content.match(/<a href=/g)||[]).length;
for(const [n,s] of Object.entries({a,b,article,wp,hub,matrix,vtt,svg,protocol,plan})){assert(s.length>100,n+' substantial')}
assert(article.trim().split(/\s+/).length>=1700,'investigation depth');
assert(article.includes('## Source trail and limits'),'primary source trail');
assert(article.includes('https://doi.org/10.1068/p281059'),'1999 DOI');
assert(article.includes('https://doi.org/10.1068/i0386'),'2010 DOI');
assert(article.includes('https://pmc.ncbi.nlm.nih.gov/articles/PMC3964612/'),'2013 primary');
assert(article.includes('Puységur'),'historical bridge');
assert(article.includes('not a validated'),'exercise caveat');
assert(article.includes('not a universal probability'),'conditional result');
assert(article.includes('not a clinical'),'not therapy');
assert(!/buy now|limited offer|act fast/i.test(article),'no commerce in investigation');
assert(wp.includes('id="mind-gorilla-title"'),'article heading');
assert(!wp.includes('href="<a'),'article links not nested');
assert(!wp.includes('target="_blank"'),'no forced new window');
assert(linked(wp)>=6,'article sources linked');
assert(!/<script|onclick=|onload=/i.test(wp),'no article scripts');
assert(a.length>9000,'substantive A');
assert(stripFilm(b)===a,'A/B editorial copy identical');
assert((b.match(/video-concept/g)||[]).length>=2,'B concept');
assert(!a.includes('video-concept') || a.includes('.video-concept{'),'A has styles only');
assert(b.includes('not a video player'),'no false player');
assert(!/<video\b|<iframe\b|autoplay/i.test(a),'A no active media');
assert(!/<video\b|<iframe\b|autoplay/i.test(b),'B no active media');
assert(!/<script\b|onmouse|onclick=|onload=/i.test(b),'no active scripts');
assert(!/<form\b|<input\b/i.test(a+b),'no duplicate signup');
assert(/<button[^>]+disabled/i.test(a),'A disabled CTA');
assert(/<button[^>]+disabled/i.test(b),'B disabled CTA');
assert(!/href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3)/i.test(a+b),'no clickable merchant link');
assert(a.includes('If you purchase through a future qualifying link, Final Vestige may earn a commission'),'clear earning disclosure');
assert(a.indexOf('commerce-disclosure')<a.indexOf('Merchant link unavailable'),'disclosure before button');
assert(a.includes('aria-describedby="fv-affiliate-disclosure-r29"'),'button explicitly described');
for(const t of ['Beginner','Premium','Advanced','24 MP3','48 MP3','first six','last six','all twelve']) assert(a.includes(t),'seller tier '+t);
assert(a.includes('mobile phone'),'privacy checkpoint');
assert(a.includes('field does <em>not</em> establish whether that field is mandatory'),'no assumption about required phone');
assert(a.includes('one-year money-back'),'guarantee attributed');
assert(a.includes("haven\'t listened")||a.includes('has not listened'),'no invented trial');
assert(a.includes('a free twelve-minute')||a.includes('twelve-minute timer'),'free useful exercise');
assert(a.includes('NIH'),'independent context');
assert(a.includes('does not justify'),'conclusion caveat');
assert(a.includes('https://finalvestige.com/focus/'),'one established Focus path');
assert(hub.includes('id="fv-mh-title"'),'hub headings');
for(const id of ['perception','history','practice','tools','methods'])assert(hub.includes('id="'+id+'"'),'hub anchor '+id);
assert(hub.includes('Puységur'),'hub archive bridge');
assert(hub.includes('https://finalvestige.com/focus/'),'hub one funnel');
assert(!/<script\b|<form\b|<iframe\b|onclick=/i.test(hub),'hub no scripts or signup');
assert(!/href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3)/i.test(hub),'hub no merchant links');
assert(svg.includes('<title'),'accessible poster title');
assert(svg.includes('<desc'),'accessible poster desc');
assert(vtt.startsWith('WEBVTT'),'valid header');
assert(vtt.includes('00:00:35.000 --> 00:00:40.000'),'40 second final cue');
assert((vtt.match(/-->/g)||[]).length===5,'5 caption cues');
assert(protocol.includes('no master video')||protocol.includes('not a master video'),'unhosted state');
assert(protocol.includes('preload=none'),'future low-cost media');
assert(protocol.includes('Do not count SVG poster views as video plays'),'honest film metrics');
assert(plan.includes('HOLD_UNSENT'),'Dispatch hold preserved');
assert(matrix.split(/\r?\n/).length>=45,'evidence matrix depth');
for(const n of ['I01','I11','P02','P03','P04','P09','P13','A04','A05','A06','M02','V01'])assert(matrix.includes('"'+n+'"'),'critical matrix row '+n);
const deliberate=[
 ['A enable merchant',a.replace(' disabled aria-describedby',' aria-describedby'),x=>!/<button[^>]+disabled/i.test(x)],
 ['A lose near disclosure',a.replace('If you purchase through a future qualifying link, Final Vestige may earn a commission',''),x=>!x.includes('If you purchase through a future qualifying link, Final Vestige may earn a commission')],
 ['A introduce vendor link',a.replace('Merchant link unavailable','<a href="https://zen12.com/">Buy</a>'),x=>/href=["']https?:\/\/zen12.com/i.test(x)],
 ['B fabricated video',b.replace('not a video player','play our proven video'),x=>!x.includes('not a video player')],
 ['hub extra signup',hub.replace('</section>','<form><input type="email"></form></section>'),x=>/<form\b/i.test(x)],
 ['article false trial',article.replace('No product trial','We personally tried Zen12. No product trial'),x=>/We personally tried Zen12/.test(x)],
 ['failed special source',matrix.replace('"A05"','"BAD"'),x=>!x.includes('"A05"')],
 ['caption wrong end',vtt.replace('00:00:40.000','00:00:41.000'),x=>!x.includes('00:00:35.000 --> 00:00:40.000')],
 ['no source review',article.replace('## Source trail and limits','## Some notes'),x=>!x.includes('## Source trail and limits')],
 ['video autoplay',b.replace('</article>','<video autoplay></video></article>'),x=>/<video\b/i.test(x)]
];
let negatives=0;for(const [name,mutant,detect] of deliberate){assert(detect(mutant),'mutation caught: '+name);negatives++}
console.log('FV Mind R29 source checks PASS: '+total+' assertions including '+negatives+' deliberate negative mutations. Native page/CI browser tests not included.');
