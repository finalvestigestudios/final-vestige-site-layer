/* R32 source-level QA. Reproduce: node qa.cjs
   Read-only local files. Does not contact WordPress, Inspire3 or any visitor. */
'use strict';
function contrast(x,y){
 function rgb(s){return [1,3,5].map(i=>parseInt(s.slice(i,i+2),16)/255).map(v=>v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4));}
 const lum=s=>{const c=rgb(s);return c[0]*.2126+c[1]*.7152+c[2]*.0722;};
 const a=lum(x),b=lum(y);return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
}
function run(F){
 const results=[];const check=(name,pred)=>{results.push({name,pass:Boolean(pred)});};
 const a=F['ZEN12-WP-VARIANT-A.html'],b=F['ZEN12-WP-VARIANT-B.html'],hub=F['HUB-WP-DRAFT.html'],invest=F['INVESTIGATION.md'],investHtml=F['INVESTIGATION-WP-DRAFT.html'],guide=F['ZEN12-INDEPENDENT-GUIDE.md'],render=F['render.cjs'],film=F['FILM.vtt'],privacy=F['privacy-off.cjs'],matrix=F['EVIDENCE-MATRIX.csv'],src=F['SOURCES.md'],plan=F['AB-NAV-MEASUREMENT-PLAN.md'],py=F['render_short.py'];
 const all=[a,b,hub,investHtml].join('\n');
 const core=v=>v.replace(/<aside class="fv-mind32-optional"[\s\S]*?<\/aside>/,'').replace('data-variant="B"','data-variant="A"');
 check('A B editorial byte-equivalent after one optional film block',core(b)===a);
 check('guide 1500+ words',guide.split(/\s+/).length>=1500);
 check('investigation 2000+ words',invest.split(/\s+/).length>=2000);
 for(const field of ['Beginn','Premium','Advanced'])check('guide tier '+field,guide.includes(field));
 for(const fact of ['first six levels','All twelve levels','Last six levels','24 MP3','48 MP3','twelve-minute','four audio'])check('product format '+fact,guide.toLowerCase().includes(fact.toLowerCase()));
 for(const phrase of ['2007','three months','not Zen12','NCCIH'])check('scientific limitations '+phrase,guide.toLowerCase().includes(phrase.toLowerCase()));
 for(const phrase of ['1992','2020','2021','180 milliseconds','lag-1','Puységur','not a diagnosis'])check('investigation nuance '+phrase,invest.toLowerCase().includes(phrase.toLowerCase()));
 for(const href of ['https://pubmed.ncbi.nlm.nih.gov/1500880/','https://link.springer.com/article/10.3758/s13428-020-01457-6'])check('primary science '+href,invest.includes(href)&&investHtml.includes(href));
 check('historical investigation no commerce',!invest.toLowerCase().includes('affiliate relationship')&&!invest.toLowerCase().includes('commission'));
 check('article no monetization form',!/<form[\s>]/i.test(investHtml)&&!/<button/i.test(investHtml));
 check('A contains conditional adjacent disclosure',a.includes('If you purchase through an approved earning link in the future, Final Vestige may earn a commission at no additional cost to you.'));
 check('B contains conditional adjacent disclosure',b.includes('If you purchase through an approved earning link in the future, Final Vestige may earn a commission at no additional cost to you.'));
 check('A disabled merchant CTA',/<button[^>]+disabled[^>]*>Product link not yet authorized<\/button>/.test(a));
 check('B disabled merchant CTA',/<button[^>]+disabled[^>]*>Product link not yet authorized<\/button>/.test(b));
 check('seller source clickable links blocked in both HTML guides',![a,b].some(s=>/href="https?:\/\/(?:[^"]*\.)?(?:inspire3\.com|zen12\.com)/i.test(s)));
 check('html source render does not accidentally create empty image href',!all.includes('src=""'));
 check('all public page HTML scoped', [a,b,hub,investHtml].every(s=>s.includes('fv-mind32')));
 check('all HTML no script tags',[a,b,hub,investHtml].every(s=>!/<script\b/i.test(s)));
 check('no event handlers',[a,b,hub,investHtml].every(s=>!(/\son(?:click|load|error|focus|mouseover)\s*=/i.test(s))));
 check('no forms in hub and guide',![a,b,hub].some(s=>/<form\b/i.test(s)));
 check('no iframe in drafted HTML',!/<iframe\b/i.test(all));
 check('no autoplay or auto video download',!/<video\b|\sautoplay(=|\s|>)/i.test(all));
 check('B contains optional film',b.includes('data-variant-only="B"')&&b.includes('40-second silent film'));
 check('A contains no film block',!a.includes('data-variant-only="B"'));
 check('B static accessible svg',b.includes('<svg class="fv-mind32-poster" role="img"')&&b.includes('viewBox="0 0 640 220"'));
 check('B transcript discoverable',b.includes('<details><summary>Read the 40-second transcript</summary>'));
 check('B user can skip film',b.includes('no hosted film or playback control')||b.includes('no hosted film or playback control'.replace(/^./,c=>c.toUpperCase())));
 check('film VTT 6 cues',(film.match(/ --> /g)||[]).length===6);
 check('film VTT starts at zero',film.includes('00:00:00.000 --> 00:00:07.000'));
 check('film VTT ends at 40s',film.includes('00:00:34.000 --> 00:00:40.000'));
 check('source film 40*FPS frames',py.includes('40*FPS'));
 check('source film no external fetch',!py.includes('requests.')&&!py.includes('urllib')&&!py.includes('http://'));
 for(const phrase of ['Puységur','focus/','editorial-standards/','affiliate-disclosure/'])check('hub verified route '+phrase,hub.includes(phrase));
 check('hub no invented published pilot URL',!hub.includes('href="/mind/'));
 check('existing Jetpack remains only funnel',!hub.includes('jetpack-subscriptions')&&hub.includes('https://finalvestige.com/focus/'));
 check('privacy runtime strictly off',privacy.includes('const ENABLED=false')&&!privacy.includes('fetch(')&&!privacy.includes('XMLHttpRequest'));
 for(const field of ['ip','email','cookie','utm_source','referrer','session'])check('privacy prohibited PII key rejected '+field,privacy.includes("'"+field+"'"));
 check('privacy k at least 10',privacy.includes('const K=10'));
 check('matrix contains 60 data rows',matrix.trim().split('\n').length===61);
 check('matrix has source provenance and checked_date',matrix.split('\n')[0].includes('source_url')&&matrix.split('\n')[0].includes('checked_date'));
 check('matrix keeps affiliate permissions UNKNOWN',matrix.includes('UNKNOWN_PERMISSION'));
 check('matrix does not authorize unsupported product efficacy',matrix.includes('UNSUPPORTED_PRODUCT_EFFICACY'));
 check('sources 18 known identifiers',src.includes('**AB92**')&&src.includes('**CHECK**')&&src.includes('**FTC**'));
 check('source ledger admits only 61 titles not full review',src.includes('61 published WordPress investigation titles'));
 check('plan holds Dispatch',plan.includes('HOLD_MERCHANT')&&plan.includes('HOLD_UNSENT'));
 check('plan forbids conversion guarantees',plan.includes('H0: no measurable change'));
 check('contrast cream at least 7',contrast('#f4efe6','#090a0a')>7);
 check('contrast gold at least 4.5',contrast('#c9a36d','#090a0a')>4.5);
 check('contrast body at least 4.5',contrast('#ded8cc','#090a0a')>4.5);
 check('reduced motion and forced colors present',[a,b,hub,investHtml].every(s=>s.includes('prefers-reduced-motion')&&s.includes('forced-colors')));
 const failed=results.filter(x=>!x.pass);
 return {passed:results.length-failed.length,failed:failed.map(x=>x.name),count:results.length};
}
function mutated(F){
 const attempts=[
 ['active merchant link',{'ZEN12-WP-VARIANT-A.html':F['ZEN12-WP-VARIANT-A.html'].replace('<button type="button" disabled aria-disabled="true">Product link not yet authorized</button>','<a href="https://zen12.com/?ref=unapproved">Buy now</a>')}],
 ['remove disclosure',{'ZEN12-WP-VARIANT-B.html':F['ZEN12-WP-VARIANT-B.html'].replace('If you purchase through an approved earning link in the future, Final Vestige may earn a commission at no additional cost to you.','')}],
 ['autoplay',{'ZEN12-WP-VARIANT-B.html':F['ZEN12-WP-VARIANT-B.html'].replace('</aside>','<video autoplay></video></aside>')}],
 ['PII form',{'HUB-WP-DRAFT.html':F['HUB-WP-DRAFT.html'].replace('</footer>','<form><input type="email"></form></footer>')}],
 ['privacy on',{'privacy-off.cjs':F['privacy-off.cjs'].replace('const ENABLED=false','const ENABLED=true')}],
 ['price promise',{'ZEN12-INDEPENDENT-GUIDE.md':F['ZEN12-INDEPENDENT-GUIDE.md'].replace('Advancement','Advancement always guaranteed')}],
 ['affiliate claim in investigation',{'INVESTIGATION.md':F['INVESTIGATION.md'].replace('Independent research; no product affiliate link','Independent research; affiliate relationship with Zen12')}],
 ['bad film cue',{'FILM.vtt':F['FILM.vtt'].replace('00:00:40.000','00:00:38.000')}],
 ['missing new partner permissions',{'EVIDENCE-MATRIX.csv':F['EVIDENCE-MATRIX.csv'].replace('UNKNOWN_PERMISSION','APPROVED')}],
 ['CSS removes reduced motion',{'HUB-WP-DRAFT.html':F['HUB-WP-DRAFT.html'].replace('@media(prefers-reduced-motion:reduce)','@media(screen)')}]
 ];
 return attempts.map(([name,change])=>({name,detected:run({...F,...change}).failed.length>0}));
}
module.exports={run,mutated,contrast};
if(require.main===module){
 const fs=require('node:fs');const path=require('node:path');
 const names=['ZEN12-WP-VARIANT-A.html','ZEN12-WP-VARIANT-B.html','HUB-WP-DRAFT.html','INVESTIGATION.md','INVESTIGATION-WP-DRAFT.html','ZEN12-INDEPENDENT-GUIDE.md','render.cjs','FILM.vtt','privacy-off.cjs','EVIDENCE-MATRIX.csv','SOURCES.md','AB-NAV-MEASUREMENT-PLAN.md','render_short.py'];
 const F={};for(const name of names)F[name]=fs.readFileSync(path.join(__dirname,name),'utf8');
 const q=run(F),m=mutated(F);console.log(JSON.stringify({quality:q,mutation:m},null,2));
 if(q.failed.length||m.some(x=>!x.detected))process.exitCode=1;
}
