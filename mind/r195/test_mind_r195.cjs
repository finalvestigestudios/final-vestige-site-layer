'use strict';
/* R195 reproducible source-level and negative controls.
   Execute: node mind/r195/test_mind_r195.cjs (from repository root)
   SOURCE CHECKS ONLY. NOT native WordPress, WCAG, browser, merchant, CI or sales testing. */
const fs=require('fs');
const files={
 article:'mind/r195/the-word-that-fought-the-color-STROOP-INVESTIGATION-UNPUBLISHED.md',
 hub:'mind/r195/mind-four-stream-stroop-WORDPRESS-UNPUBLISHED-PREVIEW.html',
 ledger:'mind/r195/STROOP-CLAIM-SOURCE-COMMERCE-PROOF-MATRIX.json',
 plan:'mind/r195/OFFER-FIRST-VERIFIED-PURCHASE-STROOP-CREATOR-FIT-AB.md',
 prior193:'mind/r193/the-gorilla-was-right-there-EXPERT-INATTENTION-UNPUBLISHED.md',
 prior194:'mind/r194/the-face-that-looked-normal-upside-down-THATCHER-INVESTIGATION-UNPUBLISHED.md',
 ledger194:'mind/r194/CLAIM-PROOF-PUBLISHER-ELIGIBILITY-REVENUE-GATES.json',
 A:'mind/r188/zen12-variant-A-independent-text-UNPUBLISHED.html',
 B:'mind/r188/zen12-variant-B-optional-42s-storyboard-UNPUBLISHED.html'
};
function evaluate(f){
 const checks=[],ok=(v,name)=>checks.push({pass:Boolean(v),name});
 let d={},ld={};try{d=JSON.parse(f.ledger)}catch{}try{ld=JSON.parse(f.ledger194)}catch{}
 const sources=d.sources||[],claims=d.claims||[],gates=d.gates||[],srcids=new Set(sources.map(x=>x.id));
 const buttons=s=>[...s.matchAll(/<button\b[^>]*>/gi)].map(x=>x[0]);
 const nativeDisabled=s=>buttons(s).length>0&&buttons(s).every(x=>/\sdisabled(?=\s|=|>)/i.test(x));
 ok(f.article.split(/\s+/).length>=2200,'original research >=2200 words');
 ok(/^# The Word That Fought the Color/m.test(f.article),'specific new title');
 for(const s of ['10.1037/h0054651','10.1037/0033-2909.109.2.163','11761035','PMC12602573','47.0 seconds','74.3 percent','2.3 seconds','5.6 percent'])
   ok(f.article.includes(s),'primary evidence '+s);
 ok(/EDITORIAL FIREWALL/.test(f.article)&&/no affiliate earning URL/i.test(f.article),'scientific editorial separation');
 ok(/neither archive is a modern clinical evaluation/i.test(f.article),'Puységur not evidence of modern efficacy');
 ok(/the existing Dispatch subscription system/i.test(f.article),'preserve single newsletter');
 ok(/https:\/\/finalvestige\.com\/focus\//.test(f.article),'optional existing Focus');
 ok(!/awin1\.com\/cread|[?&]refid=|[?&]affiliate_id=/i.test(f.article),'no earning URLs in investigation');
 ok(sources.length>=19,'19 or more source records');
 ok(claims.length>=23,'23 or more claim decisions');
 ok(gates.length>=17,'17 or more release gates');
 ok(srcids.size===sources.length&&sources.every(x=>x.id&&/^https:\/\//.test(x.url)),'source IDs unique and URLs HTTPS');
 ok(claims.every(x=>x.id&&x.source_ids?.length&&x.source_ids.every(id=>srcids.has(id))),'claim evidence references resolve');
 ok(new Set(claims.map(x=>x.id)).size===claims.length,'claim ids unique');
 ok(gates.every(x=>x.pass===false),'all commercial release gates remain false');
 for(const id of ['publisher_acceptance','allowed_channels','earning_url','owned_product_sku','confirmed_jetpack_lead','orders_reconciled','founder_release'])
  ok(gates.some(x=>x.id===id&&x.pass===false),'explicit gate '+id);
 ok(d.net_revenue_per_1000_qualified_humans==='NOT_COMPUTABLE'&&d.paid_orders_verified===null,'no invented paid result');
 ok(d.verified_commissions_received===null&&d.affiliate_earning_url===null,'no invented affiliate receipt or earning URL');
 ok(claims.find(x=>x.id==='zen12_12eq60')?.decision==='UNSUBSTANTIATED_SELLER_CLAIM','equivalence seller claim blocked');
 ok(claims.find(x=>x.id==='outbound_sale')?.decision==='FALSE_UNSAFE_PROXY','click never counted as sale');
 ok(/<!doctype html>/i.test(f.hub)&&/lang="en"/.test(f.hub),'valid HTML root/language');
 ok(/<meta name="viewport"/i.test(f.hub),'mobile viewport');
 ok(/<meta name="robots" content="noindex,nofollow"/i.test(f.hub),'unpublished noindex');
 ok(/class="skip"/.test(f.hub)&&/id="content"/.test(f.hub),'working skip target');
 ok(/focus-visible/.test(f.hub)&&/prefers-reduced-motion/.test(f.hub),'focus + motion respect');
 ok(/@media\(max-width:720px\)/.test(f.hub)&&/max-width:600px/.test(f.hub),'small screen CSS');
 ok(!/<script\b|<form\b|<(?:video|iframe|audio)\b|\sautoplay\b/i.test(f.hub),'no JS/forms/media/autoplay');
 ok(/role="img" aria-label="The word BLUE printed in red ink"/.test(f.hub),'demo non-color-dependent text description');
 ok(/Illustration only/.test(f.hub)&&/No score/.test(f.hub),'scientific demo not a diagnostic');
 ok(/2026\/11\/02\/change-blindness\//.test(f.hub),'published Change Blindness link');
 ok(/2026\/11\/02\/mesmerism\//.test(f.hub),'published Mesmerism link');
 ok(/puysegurs-animal-magnetism-files/.test(f.hub),'published Puységur');
 ok(/finalvestige\.com\/focus\//.test(f.hub),'original Focus route');
 ok(/https:\/\/zen12\.com\/hnp/.test(f.hub)&&/non-affiliate informational link/.test(f.hub),'exact seller informational source');
 ok(nativeDisabled(f.hub)&&buttons(f.hub).length===1,'one native disabled merchant control');
 ok(buttons(f.hub).every(x=>!/formaction|onclick|href=/.test(x)),'button has no active purchase action');
 const p=f.hub.indexOf('Final Vestige may earn a commission'),b=f.hub.indexOf('<button type="button"');
 ok(p>0&&b>p&&b-p<1000,'adjacent intelligible commission disclosure');
 ok(/HARD HOLD/.test(f.hub),'explicit merchant hard hold');
 ok(/NOT COMPUTABLE/.test(f.plan)&&/merchant_confirmed_paid_order/.test(f.plan),'verified net revenue contract');
 ok(/Grok owns/.test(f.plan)&&/utm_content=asset_id/.test(f.plan),'creator ownership and tracking dimensions');
 ok(/A\/B/.test(f.plan)&&/optional original ~42-second film/.test(f.plan),'A/B optional short-film experiment');
 ok(/confirmed_signup/.test(f.plan)&&/visible Fieldbook gift/.test(f.plan),'no false lead proxy');
 ok(nativeDisabled(f.A)&&nativeDisabled(f.B),'inherited both A/B purchase controls disabled');
 ok(/42.second|42s|00:42|42-second/i.test(f.B),'inherited B optional-film concept');
 ok(/more than 7,400 mm³/.test(f.prior193)&&/153 mm³/.test(f.prior193),'R193 correct nodule actual volume / gorilla bounding box');
 ok(!/mean nodule bounding volume|nodules' mean bounding volumes/.test(f.prior193),'R193 avoid unsupported nodule bounding volumes');
 ok(/gaze dwell time/.test(f.prior193),'R193 mean dwell not single gaze fixation');
 ok(/Thatcherization.*deliberate manipulation/.test(f.prior194),'R194 Thatcherization distinct from illusion');
 ok(/does not establish a separate familiar-face-identity explanation/.test(f.prior194),'R194 1997 inference removed');
 ok(/153 mm³ mean nodule volume/.test(JSON.stringify(ld)),'R194 scientific ledger consistent');
 return checks;
}
function adversarial(f){
 const m=[];
 const change=(name,key,fn)=>{const altered=fn(f[key]); if(altered===f[key])throw Error('Mutation did not edit: '+name);
   const c=evaluate({...f,[key]:altered});m.push({name,detected:c.some(x=>!x.pass)});};
 change('replace main title','article',s=>s.replace('The Word That Fought the Color','Unrelated Title'));
 change('remove primary original DOI','article',s=>s.replaceAll('10.1037/h0054651','BADDOI'));
 change('falsify historical 47.0 seconds','article',s=>s.replace('47.0 seconds','2.0 seconds'));
 change('falsify 74.3 percent','article',s=>s.replace('74.3 percent','1 percent'));
 change('replace Fieldbook route','article',s=>s.replace('finalvestige.com/focus/','finalvestige.com/incorrect/'));
 change('remove native disabled CTA','hub',s=>s.replace(/(<button\b[^>]*?)\sdisabled(?=\s|=|>)/i,'$1'));
 change('erase disclosed commission','hub',s=>s.replace('Final Vestige may earn a commission','We earn nothing'));
 change('add signup clone','hub',s=>s.replace('</footer>','<form><input type="email"></form></footer>'));
 change('add external script','hub',s=>s.replace('</footer>','<script src="https://bad.example/tag.js"></script></footer>'));
 change('add auto video','hub',s=>s.replace('</footer>','<video autoplay src="movie.mp4"></video></footer>'));
 change('remove noindex','hub',s=>s.replace('<meta name="robots" content="noindex,nofollow">',''));
 change('remove skip link','hub',s=>s.replace('class="skip"','class="no-skip"'));
 change('corrupt historical link','hub',s=>s.replace('/2026/11/02/mesmerism/','/2026/11/02/false-mesmerism/'));
 change('corrupt seller URL','hub',s=>s.replace('https://zen12.com/hnp','https://unapproved.example/offer'));
 change('remove demo accessible label','hub',s=>s.replace('role="img" aria-label="The word BLUE printed in red ink"','role="img"'));
 change('mark merchant approval true','ledger',s=>s.replace('"id": "publisher_acceptance",\n      "pass": false','"id": "publisher_acceptance",\n      "pass": true'));
 change('invent affiliate earning URL','ledger',s=>s.replace('"affiliate_earning_url": null','"affiliate_earning_url": "https://unapproved.example/"'));
 change('invent paid sales','ledger',s=>s.replace('"paid_orders_verified": null','"paid_orders_verified": 3'));
 change('falsify net revenue','ledger',s=>s.replace('"NOT_COMPUTABLE"','"52.00"'));
 change('break claim source ID','ledger',s=>s.replace('"source_ids": [\n        "stroop1935"','"source_ids": [\n        "nonexistent"'));
 change('recast equivalence as proven','ledger',s=>s.replace('"UNSUBSTANTIATED_SELLER_CLAIM"','"independently-proven"'));
 change('remove paid proof from plan','plan',s=>s.replace('merchant_confirmed_paid_order','merchant_click_proxy'));
 change('erase Grok ownership','plan',s=>s.replace('Grok owns','Social team owns'));
 change('reintroduce nodule bounding box error','prior193',s=>s.replace('the nodules\' reported mean volumes','the nodules\' mean bounding volumes'));
 change('reintroduce 1997 identity inference','prior194',s=>s.replace('does not establish a separate familiar-face-identity explanation','does establish a separate familiar-face-identity explanation'));
 change('A merchant control enabled','A',s=>s.replace(/(<button\b[^>]*?)\sdisabled(?=\s|=|>)/i,'$1'));
 change('B merchant control enabled','B',s=>s.replace(/(<button\b[^>]*?)\sdisabled(?=\s|=|>)/i,'$1'));
 return m;
}
function run(){
 const data=Object.fromEntries(Object.entries(files).map(([k,p])=>[k,fs.readFileSync(p,'utf8')]));
 const checks=evaluate(data),mutations=adversarial(data);
 const passed=checks.filter(x=>x.pass).length,detected=mutations.filter(x=>x.detected).length;
 const report={milestone:'R195',checks:{passed,total:checks.length,failed:checks.filter(x=>!x.pass)},negative:{detected,total:mutations.length,missed:mutations.filter(x=>!x.detected)}};
 console.log(JSON.stringify(report,null,2));
 if(passed!==checks.length||detected!==mutations.length)process.exitCode=1;
 return report;
}
if(require.main===module)run();
module.exports={files,evaluate,adversarial,run};
