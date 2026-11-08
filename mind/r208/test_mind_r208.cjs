'use strict';
/* Execute: node mind/r208/test_mind_r208.cjs
 * Pure source-level validators. Never interpret as browser, CI, merchant, or paid-sales proof.
 */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const dir=__dirname,read=name=>fs.readFileSync(path.join(dir,name),'utf8');
const a=read('zen12-attention-A-TEXT-UNPUBLISHED.html');
const b=read('zen12-attention-B-OPTIONAL-FILM-UNPUBLISHED.html');
const hub=read('mind-archive-ATTENTIONAL-BLINK-WP-PREVIEW-UNPUBLISHED.html');
const vtt=read('zen12-attention-42s-UNRENDERED.vtt');
const article=read('the-second-thing-you-didnt-see-ATTENTIONAL-BLINK-UNPUBLISHED.md');
const plan=read('OFFER-TO-SETTLED-REVENUE-PRIVACY-AB-ACCEPTANCE.md');
const m=JSON.parse(read('ATTENTIONAL-BLINK-ZEN12-SOURCE-CLAIM-COMMERCE-GATES.json'));
let pass=0,mutants=0;
function check(name,fn){fn();pass++;process.stdout.write('PASS '+pass+' '+name+'\n');}
function mustFail(name,fn){assert.throws(fn,undefined,name+' must be rejected');mutants++;process.stdout.write('BLOCK '+mutants+' '+name+'\n');}
function validateStatic(html){
 assert.match(html,/<!doctype html>/i);assert.match(html,/<html lang="en">/);
 assert.match(html,/<meta name="robots" content="noindex,nofollow">/);
 assert.doesNotMatch(html,/<script\b|<iframe\b|<form\b|<video\b|autoplay\s*=|<source\b|<link\b[^>]*href=|<img\b[^>]*src=|<object\b/i);
 assert.doesNotMatch(html,/href=["'](?:https?:)?\/\/(?:www\.)?(?:awin1\.com|clickbank\.net)|(?:aff_id|clickref|subid|utm_email)=/i);
 assert.doesNotMatch(html,/href=["']\/mind\//i);
}
function validateOffer(html){
 validateStatic(html);
 assert.match(html,/<button[^>]*\sdisabled(?:\s|>|=)/i);
 assert.match(html,/If you purchase through a future affiliate link, Final Vestige may earn a commission at no additional cost to you/i);
 let p=html.indexOf('may earn a commission at no additional cost to you');
 let q=html.indexOf('<button',p);
 assert(p>=0 && q>p && q-p<220,'FTC disclosure near CTA');
 assert.match(html,/HARD HOLD/);
 assert.match(html,/No active earning or purchasing link/i);
 assert.match(html,/https:\/\/finalvestige\.com\/focus\//);
 assert.match(html,/https:\/\/pmc\.ncbi\.nlm\.nih\.gov\/articles\/PMC1865565\//);
}
function validateHub(html){validateStatic(html);for(const id of ['perception','history','practice','tools'])assert.match(html,new RegExp('id="'+id+'"'));assert.match(html,/<button[^>]*\sdisabled(?:\s|>|=)/);assert.match(html,/may earn a commission at no additional cost to you/);assert.match(html,/UNPUBLISHED/);assert.match(html,/https:\/\/finalvestige\.com\/focus\//);}
function validateVTT(txt){
 assert.match(txt,/^WEBVTT\s/);
 const cues=[...txt.matchAll(/(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})/g)];
 assert.equal(cues.length,5,'exactly five timed cues');
 const ms=s=>{let [h,min,sec]=s.split(':');return ((+h*3600)+(+min*60)+(+sec))*1000;};
 assert.equal(ms(cues[0][1]),0);
 assert.equal(ms(cues.at(-1)[2]),42000);
 for(let i=0;i<cues.length;i++){assert(ms(cues[i][1])<ms(cues[i][2]));if(i)assert.equal(ms(cues[i-1][2]),ms(cues[i][1]));}
}
function validateMatrix(x){
 assert.equal(x.milestone,'R208');assert.equal(x.status,'UNPUBLISHED_NO_MERCHANT_ACTIVATION');
 const ids=new Set(x.sources.map(s=>s.id));
 assert.equal(ids.size,x.sources.length);
 assert.equal(new Set(x.claims.map(c=>c.id)).size,x.claims.length);
 for(const c of x.claims){assert(c.source_ids.length>0);for(const id of c.source_ids)assert(ids.has(id),'unresolved source '+id);}
 assert(x.authorization_gates.length>=15);
 x.authorization_gates.forEach(g=>assert.equal(g.state,'OPEN'));
 assert.equal(x.offer.publisher_approved,false);assert.equal(x.offer.affiliate_url,null);
 assert.equal(x.offer.active_cta,false);assert.equal(x.offer.owned_fallback.status,'NOT_VERIFIED');
 assert.equal(x.measurement.status,'NOT_COMPUTABLE');
 assert.deepEqual(x.measurement.cohorts,[7,30]);
 assert.equal(x.measurement.confirmed_paid_orders,null);
 assert.equal(x.measurement.cleared_commissions,null);
 assert.equal(x.measurement.qualified_human_sessions,null);
 assert.match(x.measurement.formula,/settled_owned_product_receipts/);
 assert.match(x.measurement.formula,/cleared_affiliate_commissions/);
 assert.doesNotMatch(x.measurement.formula,/confirmed_paid_orders\s*\+/);
 assert(x.measurement.chain.includes('merchant_confirmed_paid_conversion'));
 assert(x.measurement.chain.includes('merchant_outbound_click_if_authorized'));
 assert.equal(x.measurement.asset_ids_verified,false);
 x.creator_funnel.forEach(x=>{assert.equal(x.actual_asset_id,null);assert.equal(x.post_url,null);});
 assert.equal(x.creator_funnel[2].article_url,null);
 assert.equal(x.experiment.status,'DESIGNED_NOT_RUN');
}
function stripFilm(s){
 const start=s.indexOf('<section id="optional-film"');
 const end=s.indexOf('<section id="try"',start);
 assert(start>0&&end>start);
 return s.slice(0,start)+s.slice(end);
}
check('A/B/hub semantic English noindex',()=>[a,b,hub].forEach(validateStatic));
check('A guide disabled, disclosed, no affiliate links',()=>validateOffer(a));
check('B guide disabled, disclosed, no affiliate links',()=>validateOffer(b));
check('hub four published-safe streams and disabled CTA',()=>validateHub(hub));
check('A/B identical core after optional film removed',()=>assert.equal(stripFilm(b).replace('guide + optional 42-second concept',"buyer's guide"),a));
check('optional original poster has title, desc, alt role',()=>{for(const p of ['<svg','<title id="poster-title">','<desc id="poster-desc">','role="img"','<figcaption>'])assert(b.includes(p));});
check('optional film 42s captions are real timed cues',()=>validateVTT(vtt));
check('video still unrendered; static poster only',()=>{assert.match(b,/NOT RENDERED/);assert.doesNotMatch(b,/<video\b|<iframe\b/);});
check('article substantial and contains primary sources',()=>{assert(article.split(/\s+/).length>2400);for(const s of ['1500880','7707027','19933555','PMC1865565','NOT PUBLISHED'])assert(article.includes(s));});
check('article maintains independent commercial status',()=>{assert.doesNotMatch(article,/awin1\.com|clickref=|aff_id=/);assert.match(article,/independent buying guide/i);});
check('source ledger every claim resolves and 18 gates open',()=>validateMatrix(m));
check('plan contains conversion prioritized evidence not clicks as orders',()=>{for(const s of ['OFFER','FUNNEL STEP','#820','#171','#150','#172','#174','NOT COMPUTABLE','settled_owned_product_receipts','qualified_human_sessions','privacy'])assert(plan.toLowerCase().includes(s.toLowerCase()));});
check('internal links only published live resources',()=>assert.doesNotMatch(hub,/href=["']\/mind\//i));
check('Focus is one existing lead path, no duplicate form',()=>[a,b,hub].forEach(x=>{assert.match(x,/finalvestige\.com\/focus\//);assert.doesNotMatch(x,/<form\b/i);}));
check('claim matrix forbids unsupported efficacy',()=>{assert(m.claims.some(c=>c.decision==='EXCLUDE_UNSUBSTANTIATED'));assert(m.claims.some(c=>c.decision==='EXCLUDE_UNSUBSTANTIATED'&&c.claim.includes('Zen12')));});
check('latest R207 scientific QA scoped',()=>{let parent=fs.readFileSync(path.join(dir,'../r207/the-song-that-stole-a-sentence-AUDIO-ATTENTION-UNPUBLISHED.md'),'utf8');assert.match(parent,/54 studies/);assert.match(parent,/13 studies for reading speed/);assert.match(parent,/stop the audio/i);});
check('Mestry recruited and analyzed samples distinguished',()=>{let parent=fs.readFileSync(path.join(dir,'../r206/the-face-that-changes-thatcher-illusion-UNPUBLISHED.md'),'utf8');assert.match(parent,/seven excluded/);assert.match(parent,/16 in the primary analysis/);});
mustFail('enabled CTA',()=>validateOffer(a.replace(/type="button" disabled/,'type="button" enabled')));
mustFail('missing disclosure',()=>validateOffer(a.replace('may earn a commission at no additional cost to you','')));
mustFail('injected script',()=>validateStatic(a+'<script>send()</script>'));
mustFail('tracking pixel',()=>validateStatic(a+'<img src="https://tracker.invalid/pixel">'));
mustFail('new subscription form',()=>validateHub(hub+'<form action="/signup"></form>'));
mustFail('affiliate earning URL',()=>validateStatic(a+'<a href="https://www.awin1.com/cread.php?x=y">purchase</a>'));
mustFail('unapproved film player',()=>validateStatic(b+'<video autoplay controls></video>'));
mustFail('broken WebVTT signature',()=>validateVTT(vtt.replace('WEBVTT','SRT')));
mustFail('caption duration changed',()=>validateVTT(vtt.replace('00:00:42.000','00:00:50.000')));
mustFail('merchant gate improperly closed',()=>validateMatrix({...m,authorization_gates:m.authorization_gates.map((g,i)=>i===0?{...g,state:'CLOSED'}:g)}));
mustFail('invented affiliate approval',()=>validateMatrix({...m,offer:{...m.offer,publisher_approved:true}}));
mustFail('fabricated completed sale state',()=>validateMatrix({...m,measurement:{...m.measurement,status:'VERIFIED',cleared_commissions:999}}));
mustFail('fictitious Grok asset',()=>validateMatrix({...m,creator_funnel:m.creator_funnel.map((x,i)=>i===0?{...x,actual_asset_id:'fake-123'}:x)}));
mustFail('broken citation source ID',()=>validateMatrix({...m,claims:m.claims.map((c,i)=>i===0?{...c,source_ids:['NONEXISTENT']}:c)}));
mustFail('invented internal unpublished article URL',()=>validateHub(hub+'<a href="/mind/attentional-blink/">Read</a>'));
process.stdout.write('R208 SOURCE PASS '+pass+' validations; '+mutants+' altered artifacts correctly rejected. NOT browser, CI, WordPress, merchant or revenue evidence.\n');
