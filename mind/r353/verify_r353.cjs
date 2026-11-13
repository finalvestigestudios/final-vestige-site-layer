'use strict';
/* R353 standalone non-network source/commerce guard. Run: node mind/r353/verify_r353.cjs */
const fs=require('node:fs'), path=require('node:path'), assert=require('node:assert/strict');
const dir=__dirname;
const read=n=>fs.readFileSync(path.join(dir,n),'utf8');
const files={
a:read('ZEN12_A_TEXT_GUIDE.html'),
b:read('ZEN12_B_OPTIONAL_FILM_GUIDE.html'),
hub:read('MIND_HUB_WP_REVIEW_ONLY.html'),
poster:read('ORIGINAL_SUGGESTION_POSTER.svg'),
vtt:read('original_suggestion_42s.vtt'),
article:read('THE_EXPERIMENT_THAT_SEPARATED_TRANCE_FROM_SUGGESTION.md'),
dossier:read('CONVERSION_ACCEPTANCE.md'),
matrix:JSON.parse(read('CLAIMS_AND_RELEASE_GATES.json'))
};
let assertionCount=0,adverseDetected=0,financeCount=0;
function ensure(pred,msg){assert.ok(pred,msg);assertionCount++;}
function core(html){let m=html.match(/<div data-comparison-core="true">([\s\S]*?)<\/div><footer>/);return m&&m[1];}
function safeCommerce(html){
 const bad=/<script\b|<iframe\b|<form\b|\bonclick\s*=|\bonload\s*=|<video[^>]+autoplay|\bdata:application\/javascript/i;
 if(bad.test(html))throw Error('active/script/form/iframe unsafe');
 if(/<a\b[^>]*href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(html))throw Error('unapproved merchant outbound');
 if(!/may earn a commission at no additional cost/i.test(html))throw Error('adjacent material disclosure missing');
 if(!/<button\b(?=[^>]*\sdisabled(?:\s|>|=))[^>]*>/i.test(html))throw Error('merchant CTA not natively disabled');
 if(!/No earning link is active here/i.test(html))throw Error('false activated offer');
 if(!/https:\/\/finalvestige\.com\/focus\//.test(html))throw Error('original focus route missing');
 if((html.match(/<div data-comparison-core="true">/g)||[]).length!==1)throw Error('core absent or duplicate');
}
function check(){
 ensure(files.a.includes('Unpublished test A'),'A marked draft');
 ensure(files.b.includes('Unpublished test B'),'B marked draft');
 ensure(files.a.includes('name="robots" content="noindex,nofollow"'),'A noindex');
 ensure(files.b.includes('name="robots" content="noindex,nofollow"'),'B noindex');
 ensure(files.a.includes('class="skip"'),'A keyboard skip');
 ensure(files.b.includes('class="skip"'),'B keyboard skip');
 ensure(files.a.includes('prefers-reduced-motion'),'reduced motion CSS');
 ensure(files.b.includes('prefers-reduced-motion'),'B reduced motion CSS');
 ensure(files.a.includes('grid-template-columns:1fr'),'mobile CSS');
 ensure(files.b.includes('grid-template-columns:1fr'),'mobile CSS B');
 safeCommerce(files.a);ensure(true,'A commercial guard');
 safeCommerce(files.b);ensure(true,'B commercial guard');
 ensure(core(files.a)===core(files.b),'A/B substantive buyer core exact match');
 ensure(!files.a.includes('id="optional-film"'),'A without movie intervention');
 ensure(files.b.includes('id="optional-film"'),'B with optional film concept');
 ensure(files.b.includes('not</strong> a playable/hosted video'),'B no false playable claim');
 ensure(files.b.includes('ORIGINAL_SUGGESTION_POSTER.svg'),'B real original poster');
 ensure(files.poster.includes('viewBox="0 0 1280 720"'),'poster dimension');
 ensure(files.poster.includes('<title'),'accessible poster title');
 ensure(files.poster.includes('<desc'),'accessible poster description');
 ensure(files.vtt.startsWith('WEBVTT'),'caption syntax');
 ensure((files.vtt.match(/ --> /g)||[]).length===6,'six timed caption cues');
 ensure(files.vtt.includes('00:00:35.000 --> 00:00:42.000'),'42-second coverage');
 ensure(files.b.includes('<details>')&&files.b.includes('<summary>'),'no-JS transcript details');
 ensure(!/<script|<iframe|<form/i.test(files.hub),'hub no form/scripts');
 ensure(/https:\/\/finalvestige\.com\/2026\/11\/02\/change-blindness\//.test(files.hub),'hub link published');
 ensure(/https:\/\/finalvestige\.com\/free-resources\/puysegurs-animal-magnetism-files\//.test(files.hub),'hub Puységur');
 ensure(/66 on 13 November 2026/.test(files.hub),'inventory conflict noted, not old 61');
 ensure(/not an approved\/live \/mind\//i.test(files.hub),'no invented hub publication');
 ensure(files.article.split(/\s+/).length>=1800,'substantive original investigation');
 ensure(files.article.includes('https://doi.org/10.1016/j.concog.2025.103948'),'article primary source');
 ensure(files.article.includes('https://pubmed.ncbi.nlm.nih.gov/39032268/'),'article competing theory');
 ensure(files.article.includes('less suggestible'),'article effect heterogeneity');
 ensure(files.article.includes('not a Zen12 outcome study')||files.article.includes('Zen12 itself'),'article avoids product trial fiction');
 ensure(files.matrix.claims.length===30,'30 classified claims');
 ensure(Object.keys(files.matrix.sources).length===18,'18 distinct source URLs');
 ensure(files.matrix.release_gates.length===28,'28 release gates');
 ensure(files.matrix.release_gates.every(x=>x.status==='HOLD'),'all release gates hold');
 ensure(files.matrix.commercial_status.issued_link===null,'no invented earning link');
 ensure(files.matrix.commercial_status.realized_net_revenue===null,'no invented revenue');
 ensure(files.dossier.includes('NOT COMPUTABLE'),'revenue unknown');
 ensure(files.dossier.includes('Praxxis')&&files.dossier.includes('Grok'),'creator boundary');
 ensure(files.dossier.includes('NO')===false || files.dossier.includes('HARD HOLD'),'release hold');
 return true;
}
function financialKpi(d) {
 const forbidden=['email','name','phone','ip','address','health','fingerprint','payment_card','ssn'];
 if(!d || typeof d!=='object'||Object.keys(d).some(k=>forbidden.some(w=>k.toLowerCase().includes(w))))throw Error('PII/invalid payload');
 if(d.qualified_human_sessions==null||!Number.isSafeInteger(d.qualified_human_sessions)||d.qualified_human_sessions<=0)throw Error('qualified human denominator unavailable');
 if(!Array.isArray(d.orders)||d.orders.length===0)throw Error('no verified orders');
 const keys=new Set();let net=0,orders=0;
 for(const x of d.orders){
 if(x.source!=='merchant_settlement'&&x.source!=='partner_settlement')throw Error('unverified settlement source');
 if(!x.confirmed_paid||!x.finalized||typeof x.id!=='string'||!x.id.trim())throw Error('unconfirmed order');
 if(keys.has(x.id))throw Error('double counted order');keys.add(x.id);
 for(const k of ['gross','refunds','fees','chargebacks'])if(typeof x[k]!=='number'||!Number.isFinite(x[k])||x[k]<0)throw Error('incomplete/nonfinite accounting');
 if(x.refunds+x.chargebacks>x.gross)throw Error('impossible refund total');
 net+=x.gross-x.refunds-x.chargebacks-x.fees;orders++;
 }
 return {orders,net,net_per_1000:1000*net/d.qualified_human_sessions};
}
function financeTests(){
 const good={qualified_human_sessions:1000,orders:[{id:'synthetic001',source:'merchant_settlement',confirmed_paid:true,finalized:true,gross:100,refunds:10,fees:3,chargebacks:0}]};
 const o=financialKpi(good);assert.equal(o.net,87);assert.equal(o.net_per_1000,87);financeCount+=2;
 const cases=[
 {qualified_human_sessions:0,orders:good.orders},
 {orders:good.orders},
 {qualified_human_sessions:1000,orders:[]},
 {qualified_human_sessions:1000,orders:[{...good.orders[0],source:'affiliate_click'}]},
 {qualified_human_sessions:1000,orders:[{...good.orders[0],confirmed_paid:false}]},
 {qualified_human_sessions:1000,orders:[{...good.orders[0],fees:undefined}]},
 {qualified_human_sessions:1000,orders:[{...good.orders[0],refunds:101}]},
 {qualified_human_sessions:1000,orders:[{...good.orders[0],id:''}]},
 {qualified_human_sessions:1000,orders:[good.orders[0],good.orders[0]]},
 {...good,email:'synthetic@invalid.test'},
 {...good,ip:'127.0.0.1'},
 {...good,health_condition:'none'},
 {qualified_human_sessions:1000,orders:[{...good.orders[0],gross:NaN}]},
 {qualified_human_sessions:-1,orders:good.orders}
 ];
 for(const p of cases){assert.throws(()=>financialKpi(p));financeCount++;}
}
function mutations(){
 const bad=[
 files.a.replace('may earn a commission at no additional cost to you','may earn money'),
 files.a.replace(' disabled aria-disabled',' aria-disabled'),
 files.a+'<script src="https://example.com/track.js"></script>',
 files.a+'<iframe src="https://zen12.com"></iframe>',
 files.a+'<form action="https://example.com"><input name="email"></form>',
 files.a.replace('No earning link is active here','Our earning link is active here'),
 files.a.replaceAll('https://finalvestige.com/focus/','https://finalvestige.com/water/'),
 files.a.replace('source reference only','source reference only')+'<a href="https://zen12.com/">Buy Zen12</a>',
 files.a+'<video autoplay src="https://example.com/media.mp4"></video>',
 files.a.replace('data-comparison-core="true"','data-comparison-core="false"')
 ];
 for(const s of bad){assert.throws(()=>safeCommerce(s));adverseDetected++;}
}
check();financeTests();mutations();
console.log(JSON.stringify({status:'PASS',source_assertions:assertionCount,synthetic_finance_assertions:financeCount,adversarial_mutations_rejected:adverseDetected,commercial_release:'HARD HOLD',real_settlement_tests:'NOT RUN',real_browser_tests:'NOT RUN'}));
