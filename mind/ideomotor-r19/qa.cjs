/* Final Vestige R19, zero-dependency source contract.
   Reproduce: node mind/ideomotor-r19/qa.cjs --mutation
   Source checks != WordPress rendering, science review, browser WCAG, CI or media hosting. */
'use strict';
const FILES=['INVESTIGATION.html','TOTAL_FOCUS_BUYER_GUIDE.md','PILOT_A.html','PILOT_B_STAGING.html','ZEN12_R19_POSTER.svg','ZEN12_R19_CAPTIONS_DRAFT.vtt','EXPERIMENT_AND_RELEASE.md','README.md'];
const htmlFiles=['INVESTIGATION.html','PILOT_A.html','PILOT_B_STAGING.html'];
function audit(files,matrix){
 const checks=[],errors=[];
 function test(name,result){const ok=!!result;checks.push({name,ok});if(!ok)errors.push(name);}
 for(const name of FILES)test('file exists '+name,typeof files[name]==='string'&&files[name].length>200);
 for(const name of htmlFiles){
  const h=files[name]||'';
  test(name+': only one h1',(h.match(/<h1\b/ig)||[]).length===1);
  test(name+': disabled native CTA',/<button\b[^>]*\bdisabled\b/i.test(h));
  test(name+': aria-disabled CTA',/<button\b[^>]*aria-disabled="true"/i.test(h));
  test(name+': near CTA commission disclosure',/If you purchase through[^<]{0,150}Final Vestige may earn a commission at no additional cost to you/.test(h));
  test(name+': no active anchor to merchant',!/<a\b[^>]*href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|affiliates\.inspire3\.com)/i.test(h));
  test(name+': no active merchant URL via button',!/<button\b[^>]*(?:onclick|data-href|formaction)=/i.test(h));
  test(name+': no form or duplicate signup',!/<form\b|<input\b[^>]*type\s*=\s*["']email|jetpack-subscriptions__form-elements/i.test(h));
  test(name+': no scripts or third-party embeds',!/<script\b|<iframe\b|<object\b|<embed\b/i.test(h));
  test(name+': no pixel or localStorage',!/google-analytics|googletagmanager|fbq\(|facebook\.com\/tr|sendBeacon|localStorage|document\.cookie|dataLayer/i.test(h));
  test(name+': no autoplay or prefetch',!/<video\b[^>]*\bautoplay\b|rel="(?:prefetch|preload|prerender)"/i.test(h));
  test(name+': live focus route',h.includes('https://finalvestige.com/focus/'));
  test(name+': live Puységur route',h.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'));
  test(name+': keyboard focus CSS',h.includes(':focus-visible'));
  test(name+': reduced motion CSS',h.includes('prefers-reduced-motion'));
  test(name+': forced colors CSS',h.includes('forced-colors'));
  test(name+': responsive CSS',h.includes('@media('));
  test(name+': no specific sale price amount',!/\$\s*\d+(?:\.\d{2})?/.test(h));
  const ids=[...h.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
  test(name+': no duplicate IDs',new Set(ids).size===ids.length);
 }
 const I=files['INVESTIGATION.html']||'', G=files['TOTAL_FOCUS_BUYER_GUIDE.md']||'',
 A=files['PILOT_A.html']||'',B=files['PILOT_B_STAGING.html']||'',
 S=files['ZEN12_R19_POSTER.svg']||'',V=files['ZEN12_R19_CAPTIONS_DRAFT.vtt']||'',P=files['EXPERIMENT_AND_RELEASE.md']||'';
 test('historical primary instrument',I.includes('Michael Faraday')&&I.includes('layered cards')&&I.includes('hand pressure'));
 test('historical specific citation',I.includes('Experimental_Researches_in_Chemistry_and_Physics/Table-turning'));
 test('2022 pendulum negative finding',I.includes('2022')&&I.includes('at chance')&&I.includes('did not reproduce'));
 test('2018 agency field investigation',I.includes('2018')&&I.includes('eye trackers'));
 test('1976 study study scope',I.includes('60 college students')&&I.includes('1976'));
 test('original no-script history figure',I.includes('<svg')&&I.includes('<figcaption>')&&I.includes('<desc'));
 test('historical source list',I.includes('Evidence ledger')&&(I.match(/<li>/g)||[]).length>=7);
 test('article practical non-diagnostic exercise',I.includes('not a diagnostic')&&I.includes('weight may move'));
 test('guide exact seller URL',G.includes('https://hypnosislive.com/mental-skills/total-focus'));
 test('guide seller format and author',G.includes('33-minute')&&G.includes('47 MB')&&G.includes('J.A. Amos'));
 test('guide rejects SKU-specific efficacy leap',G.includes('product-specific')&&G.includes('reprogram'));
 test('guide free seven-minute method',G.includes('seven-minute timer')&&G.includes('seven-minute'));
 test('guide FTC terms and affiliate link held',G.includes('MERCHANT BUTTON: DISABLED'));
 test('pilot exact Zen12 offer four formats', ['Guided','Music','White noise','Nature'].every(t=>A.includes(t)));
 test('pilot exact Zen12 twelve levels and session duration',A.includes('twelve progression levels')&&A.includes('twelve-minute'));
 test('pilot objections about checkout',A.includes('mobile-phone')&&A.includes('countdown'));
 test('pilot no hour-equivalence adoption',A.includes('does not')&&A.includes('hour of ordinary meditation'));
 test('pilot full free twelve-minute alternative',A.includes('first two minutes')&&A.includes('next eight')&&A.includes('final two'));
 test('pilot transcript useful without video',A.includes('Read the full 40-second video transcript'));
 test('A text-only',!/<video\b/i.test(A));
 test('A video substitution anchor',A.includes('<!--VIDEO_SLOT-->'));
 test('B video controls',/<video\b[^>]*controls\b[^>]*playsinline\b[^>]*preload="none"/i.test(B));
 test('B hidden unhosted video',/<video\b[^>]*hidden\b[^>]*data-media-approved="false"/i.test(B));
 test('B VTT caption track',/<track\b[^>]*kind="captions"/i.test(B)&&B.includes('ZEN12_R19_CAPTIONS_DRAFT.vtt'));
 test('B local poster',B.includes('ZEN12_R19_POSTER.svg'));
 test('B no external video source',!/<source\b[^>]*src="https?:\/\//i.test(B));
 test('B placeholder explicitly unhosted',B.includes('REVIEW_ONLY_UNHOSTED_40_SECOND_FILM.mp4'));
 test('B acknowledges no playable media',B.includes('No playable media is available'));
 const norm=h=>h.replace(/<!-- VERSION [AB][^]*?; NOT FOR WORDPRESS CMS WITHOUT APPROVAL -->/,'<!--PILOT-->').replace(/<section class="panel" aria-labelledby="fv-z19-film-h">[\s\S]*?<\/section>/,'<!--VIDEO_SLOT-->');
 test('A/B identical base copy',norm(A)===norm(B));
 test('poster original SVG with accessible info',S.includes('<svg')&&S.includes('<title')&&S.includes('<desc')&&S.includes('width="960"'));
 test('draft VTT actual time cues',V.startsWith('WEBVTT')&&V.includes('00:00:00.000 --> 00:00:07.000')&&V.includes('00:00:32.000 --> 00:00:40.000'));
 test('VTT not treated as synchronized final',P.includes('draft English VTT')&&P.includes('caption'));
 test('privacy OFF',P.includes('Privacy')||P.includes('Tracking'));
 test('no live assignment',P.includes('no approved link')&&P.includes('No JavaScript instrumentation'));
 test('fair A/B controls',P.includes('identical copy')&&P.includes('Hypothesis'));
 test('internal nav plan',P.includes('/mind/')&&P.includes('Tools Under Review')&&P.includes('Puységur'));
 test('separate Dispatch ownership',P.includes('Dispatch #174')&&P.includes('source-only'));
 test('preserve homepage flagship',P.includes('PR #49')||P.includes('homepage #49'));
 test('explicit real accessibility QA gate',P.includes('NVDA/VoiceOver')&&P.includes('390/768/1440/1920'));
 test('product promo permissions held',P.includes('account approval')&&P.includes('social/TikTok/email'));
 test('no product approval claimed',matrix.partner_approval_verified===false);
 test('no earning URL',matrix.affiliate_earning_url===null);
 test('no tracking',matrix.affiliate_tracking_enabled===false&&matrix.collection_enabled===false);
 test('no product firsthand use',matrix.original_products_tested===false);
 test('social/email rights unknown',matrix.social_promotion_allowed===null&&matrix.email_promotion_allowed===null);
 const z=matrix.claims||[],src=matrix.source_urls||{};
 test('matrix >=55 individual dispositions',z.length>=55);
 test('matrix >=16 real URLs',Object.keys(src).length>=16&&Object.values(src).every(v=>/^https:\/\//.test(v)));
 test('matrix ids unique',new Set(z.map(x=>x.id)).size===z.length);
 test('matrix claims sourced',z.every(x=>x.claim&&x.disposition&&x.qualification&&x.source_ids.length&&x.source_ids.every(id=>Object.prototype.hasOwnProperty.call(src,id))));
 test('matrix exact seller source',src.TOTAL_FOCUS==='https://hypnosislive.com/mental-skills/total-focus'&&src.ZEN12_CHECKOUT==='https://zen12.com/getstarted');
 test('unsubstantiated claims appropriately marked',z.some(x=>x.disposition==='unsubstantiated_product_claim'&&x.claim.includes('one hour'))&&z.some(x=>x.disposition==='unsubstantiated_product_claim'&&x.claim.includes('brain')));
 test('FTC sources present',!!src.FTC_END&&!!src.FTC_HEALTH);
 const ratios=[['article ink','#f4efe6','#090a0a'],['article body','#ded7ca','#090a0a'],['article muted','#b4aa9b','#090a0a'],['article link','#f4dcaa','#090a0a'],['pilot body','#ddd5c8','#090a0a'],['pilot muted','#beb4a6','#090a0a'],['pilot gold','#dfbb81','#090a0a'],['button ink','#f4efe6','#302b22']];
 ratios.forEach(([name,a,b])=>test('contrast '+name,contrast(a,b)>=4.5));
 return {passed:checks.filter(x=>x.ok).length,total:checks.length,failed:errors,checks};
}
function contrast(a,b){
 function lum(h){const x=h.replace('#','');const v=[0,2,4].map(n=>parseInt(x.slice(n,n+2),16)/255).map(v=>v<=0.04045?v/12.92:Math.pow((v+0.055)/1.055,2.4));return 0.2126*v[0]+0.7152*v[1]+0.0722*v[2];}
 const l=lum(a),r=lum(b);return (Math.max(l,r)+0.05)/(Math.min(l,r)+0.05);
}
function mutations(files,matrix){
 const scenarios=[
 ['affiliate anchor',f=>f['PILOT_A.html']=f['PILOT_A.html'].replace('<!--VIDEO_SLOT-->','<a href="https://zen12.com/getstarted">Buy now</a><!--VIDEO_SLOT-->')],
 ['missing disclaimer',f=>f['PILOT_A.html']=f['PILOT_A.html'].replace('If you purchase through this link, Final Vestige may earn a commission at no additional cost to you','No disclosure needed')],
 ['JS analytics',f=>f['PILOT_A.html']+='<script src="https://example.com/analytics.js"></script>'],
 ['tracking pixel',f=>f['PILOT_B_STAGING.html']+='<img src="https://www.facebook.com/tr?id=1">'],
 ['new email form',f=>f['PILOT_A.html']+='<form><input type="email"></form>'],
 ['autoplay',f=>f['PILOT_B_STAGING.html']=f['PILOT_B_STAGING.html'].replace('<video hidden','<video autoplay hidden')],
 ['live video incorrectly exposed',f=>f['PILOT_B_STAGING.html']=f['PILOT_B_STAGING.html'].replace('<video hidden','<video')],
 ['captions removed',f=>f['PILOT_B_STAGING.html']=f['PILOT_B_STAGING.html'].replace('kind="captions"','kind="subtitles"')],
 ['bad video poster',f=>f['PILOT_B_STAGING.html']=f['PILOT_B_STAGING.html'].replace('ZEN12_R19_POSTER.svg','missing.png')],
 ['fake checkout URL button',f=>f['PILOT_A.html']=f['PILOT_A.html'].replace('<button type="button" disabled','<button onclick="location.href=\'https://zen12.com/getstarted\'" type="button" disabled')],
 ['duplicate IDs',f=>f['INVESTIGATION.html']=f['INVESTIGATION.html'].replace('id="fv-im-h1"','id="fv-im-section-4"')],
 ['duplicate signup',f=>f['INVESTIGATION.html']+='<div class="jetpack-subscriptions__form-elements"></div>'],
 ['invented price',f=>f['PILOT_A.html']+='<p>Only $19.99!</p>'],
 ['changed B benefit copy',f=>f['PILOT_B_STAGING.html']=f['PILOT_B_STAGING.html'].replace('a twelve-minute appointment','a one-minute appointment')],
 ['lost Focus link',f=>f['PILOT_A.html']=f['PILOT_A.html'].replace(/https:\/\/finalvestige\.com\/focus\//g,'/deleted-focus/')],
 ['merchant acceptance forged',(_,z)=>z.partner_approval_verified=true],
 ['firsthand product trial forged',(_,z)=>z.original_products_tested=true],
 ['affiliate click tracking enabled',(_,z)=>z.affiliate_tracking_enabled=true],
 ['false approved earning URL',(_,z)=>z.affiliate_earning_url='https://example.com/payout'],
 ['matrix claims removed',(_,z)=>z.claims=z.claims.slice(0,10)],
 ['source proof erased',(_,z)=>z.claims[0].source_ids=['INVALID_SOURCE']],
 ['VTT cues erased',f=>f['ZEN12_R19_CAPTIONS_DRAFT.vtt']='WEBVTT\n']
 ];
 return scenarios.map(([name,change])=>{
 const f={...files},z=JSON.parse(JSON.stringify(matrix));change(f,z);
 const out=audit(f,z);return {name,caught:out.failed.length>0,first_failure:out.failed[0]||null};
 });
}
module.exports={audit,mutations,contrast,FILES};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const files=Object.fromEntries(FILES.map(f=>[f,fs.readFileSync(path.join(__dirname,f),'utf8')]));
 const matrix=JSON.parse(fs.readFileSync(path.join(__dirname,'EVIDENCE_MATRIX.json'),'utf8'));
 const result=audit(files,matrix);
 const mutationResults=process.argv.includes('--mutation')?mutations(files,matrix):[];
 console.log(JSON.stringify({source_audit:{passed:result.passed,total:result.total,failed:result.failed},mutations:{detected:mutationResults.filter(x=>x.caught).length,total:mutationResults.length,failed:mutationResults.filter(x=>!x.caught)}},null,2));
 if(result.failed.length||mutationResults.some(x=>!x.caught))process.exitCode=1;
}
