/* R289: dependency-free source-only integrity tests.
 * CLI: node mind/r289/verify_r289.cjs <article.md> <matrix.json> <hub.html> <acceptance.md>
 * No network requests, WP calls, trackers, merchant calls or deployed behavior.
 * When imported: module.exports = { validate, adversarialTests }.
 */
'use strict';
const EXPECTED={
  matrixVersion:'R289',
  sourcesSig:'366c83a3',
  claimsSig:'747cf78e',
  gatesSig:'6042d2e0',
  sourceCount:22,
  claimCount:28,
  gateCount:18,
  publisher:'HARD_HOLD'
};
function fnv1a(s){let v=2166136261;for(let i=0;i<s.length;i++){v^=s.charCodeAt(i);v=Math.imul(v,16777619);}return (v>>>0).toString(16).padStart(8,'0');}
function req(ok,msg){if(!ok)throw Error(msg);}
function validate(bundle){
  req(bundle && typeof bundle==='object','bundle missing');
  const {article, matrix, hub, plan}=bundle;
  for(const [k,v] of Object.entries({article,matrix,hub,plan}))req(typeof v==='string'&&v.length>2500,k+' missing/short');
  let m;try{m=JSON.parse(matrix)}catch(e){throw Error('unparseable matrix')}
  req(m.version===EXPECTED.matrixVersion&&m.commercial==='HARD_HOLD'&&m.publication==='UNPUBLISHED','release metadata');
  req(m.parent_sha==='c08c3e2f48c0fadf7ed11d2fd6b6fcc5bf6809f7','wrong parent sha');
  req(m.scope==='ONLY_MIND','scope');
  req(m.sources.length===EXPECTED.sourceCount,'source count');
  req(m.claims.length===EXPECTED.claimCount,'claim count');
  const sm=m.sources.map(x=>[x.id,x.url]), cm=m.claims.map(x=>[x.id,x.statement,x.source_id,x.decision]);
  req(new Set(m.sources.map(x=>x.id)).size===m.sources.length,'duplicate source ID');
  req(new Set(m.claims.map(x=>x.id)).size===m.claims.length,'duplicate claim ID');
  req(fnv1a(JSON.stringify(sm))===EXPECTED.sourcesSig,'source ID to exact URL changed');
  req(fnv1a(JSON.stringify(cm))===EXPECTED.claimsSig,'claim ID/text/source/decision changed');
  req(m.claims.every(c=>m.sources.some(s=>s.id===c.source_id)),'orphan claim');
  req(m.claims.filter(c=>c.decision.startsWith('REJECT')).length>=8,'unjustified claim approvals');
  const keys=Object.keys(m.release_gates||{}).sort();
  req(keys.length===EXPECTED.gateCount,'gate count');
  req(fnv1a(JSON.stringify(keys))===EXPECTED.gatesSig,'commercial gate identity changed');
  req(keys.every(k=>m.release_gates[k].status===EXPECTED.publisher),'commercial gate prematurely activated');
  req(m.products.length===5&&m.products.find(x=>x.id==='ZEN12').commercial==='HOLD','product registry mutated');
  req(m.products.find(x=>x.id==='FV_OWNED_PAID_MIND').commercial==='HOLD','unverified owned product enabled');
  req(m.creator_routes.length===3&&m.creator_routes.every(x=>x.existing_asset_id===null&&x.confirmed_url===null),'unverified media attribution');
  req(m.measurement_contract.events.includes('merchant_confirmed_purchase')&&m.measurement_contract.events.includes('affiliate_outbound')&&m.measurement_contract.events.includes('settled_commission'),'paid vs outbound event separation');
  req(m.canonical_presell.length===2&&m.canonical_presell.every(x=>x.startsWith('mind/r284/')),'canonical pair changed or competitor introduced');
  req(typeof m.notes[2]==='string' && m.notes[2].includes('NOT a playable'),'false video status');

  req(article.includes('# The Second Number Vanished'),'original investigation missing');
  req(article.includes('three months')&&article.includes('brief')&&article.includes('2021'),'duration evidence boundary');
  req(article.includes('did not test')||article.includes('did not prove'),'merchant efficacy boundary');
  for(const u of ['https://pubmed.ncbi.nlm.nih.gov/1500880/','https://pubmed.ncbi.nlm.nih.gov/17488185/','https://doi.org/10.1007/s12671-021-01709-2','https://finalvestige.com/focus/'])req(article.includes(u),'article missing source: '+u);
  req(article.includes('No affiliate endorsement')||article.includes('No product-specific efficacy'),'editorial independence boundary');
  req(!/https?:\/\/(?:affiliates\.inspire3\.com|checkout\.inspire3\.com)\/\S*ref=/.test(article),'earning link in manuscript');
  req(!/<script\b|<form\b|<iframe\b|<video\b|<audio\b|<img\b|<link\b[^>]*href|<meta\b[^>]*http-equiv\s*=\s*["']?refresh/i.test(hub),'unauthorized markup or third-party resources');
  req(!/\bon(?:click|load|error|mouseover|focus|submit)\s*=|javascript:|data:text\/html|document\.cookie|localStorage|sessionStorage|sendBeacon|fetch\(|XMLHttpRequest|gtag\(|fbq\(|analytics\.ahrefs|googletagmanager/i.test(hub),'tracking or executable attribute');
  req(/<meta name="robots" content="noindex,nofollow">/.test(hub),'unpublished noindex missing');
  req(/<button type="button" disabled aria-disabled="true">Zen12 purchasing link — not authorized<\/button>/.test(hub),'purchasing button enabled/renamed');
  req(/If you purchase through an approved link in the future, Final Vestige may earn a commission at no additional cost to you/.test(hub),'FTC disclosure missing');
  const disclosure=hub.indexOf('Prospective affiliate disclosure:');
  const button=hub.indexOf('Zen12 purchasing link — not authorized');
  req(disclosure>=0&&button>disclosure&&button-disclosure<500,'FTC disclosure not adjacent');
  req(!/<a\b[^>]*href\s*=\s*["'](?:https?:\/\/)?(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|brainwaveshots\.com|hypnosislive\.com)/i.test(hub),'live merchant link');
  req(!/<a\b[^>]*href\s*=\s*["'](?:\/go\/|\/out\/|\/affiliate\/|\/buy)/i.test(hub),'outbound cloaking path');
  req(hub.includes('https://finalvestige.com/focus/')&&hub.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'),'real existing navigation absent');
  req(hub.includes('Static teaching image')&&hub.includes('not a playable film'),'misleading video/demo status');
  req(hub.includes('merchant')&&hub.includes('newsletter')&&hub.includes('Final Vestige'),'merchant vs FV consent missing');
  req(hub.includes('@media(max-width:700px)')&&hub.includes('prefers-reduced-motion')&&hub.includes('focus-visible'),'responsive focus/motion source checks absent');
  req(!/href="https?:\/\/[^"]+[?&](?:ref|aff|affiliate_id|clickid|subid)=/i.test(hub),'unapproved affiliate params');

  for(const s of ['NOT COMPUTABLE','qualified_human_landing','provider_confirmed_signup','affiliate_outbound','merchant_confirmed_purchase','settled_commission','refund','fees','R284','HARD_HOLD'])req(plan.includes(s),'conversion acceptance missing '+s);
  req(plan.includes('7- and 30-day')||plan.includes('7/30-day'),'cohorts missing');
  req(plan.includes('no autoplay')||plan.includes('no-autoplay'),'optional video constraint missing');
  req(!/\b[A-Z]{3}[0-9]{7,}\b/.test(plan),'invented Grok ID appears');
  return {ok:true,sources:m.sources.length,claims:m.claims.length,gates:keys.length};
}
function clone(b){return JSON.parse(JSON.stringify(b))}
function adversarialTests(bundle){
  const mutated=[];
  const add=(name,change)=>{const x=clone(bundle);change(x);mutated.push({name,bundle:x})};
  const alterMatrix=(name,fn)=>add(name,b=>{let m=JSON.parse(b.matrix);fn(m);b.matrix=JSON.stringify(m)});
  for(const k of Object.keys(JSON.parse(bundle.matrix).release_gates)){
    alterMatrix('premature gate '+k,m=>{m.release_gates[k].status='PASS'});
  }
  alterMatrix('delete one gate',m=>{delete m.release_gates.named_publisher_acceptance});
  alterMatrix('rename gate',m=>{m.release_gates.fake_new_gate=m.release_gates.issued_earning_url;delete m.release_gates.issued_earning_url});
  alterMatrix('source id/url drift',m=>{m.sources[0].url='https://example.org/false'});
  alterMatrix('source swap',m=>{[m.sources[0].url,m.sources[1].url]=[m.sources[1].url,m.sources[0].url]});
  alterMatrix('claim wrong source',m=>{m.claims[0].source_id='sharpe2021'});
  alterMatrix('claim false meaning',m=>{m.claims[4].statement='Zen12 proven to enhance brain function'});
  alterMatrix('claim reclassified',m=>{m.claims[12].decision='ALLOW_SPECIFIC_SCIENCE'});
  alterMatrix('fake creator id',m=>{m.creator_routes[0].existing_asset_id='fake-asset-1'});
  alterMatrix('fake creator URL',m=>{m.creator_routes[1].confirmed_url='https://example.org/video'});
  alterMatrix('owned product commercial live',m=>{m.products[4].commercial='LIVE'});
  alterMatrix('add competing presell',m=>{m.canonical_presell.push('mind/r289/new-presell.html')});
  alterMatrix('false live video',m=>{m.notes=m.notes.map(x=>x.replace('NOT a playable','now a playable'))});
  add('remove disclosure',b=>{b.hub=b.hub.replace('If you purchase through an approved link in the future, Final Vestige may earn a commission at no additional cost to you','No disclosure necessary')});
  add('remove disabled',b=>{b.hub=b.hub.replace('type="button" disabled aria-disabled="true"','type="button"')});
  add('merchant link injection',b=>{b.hub=b.hub.replace('</footer>',"<a href=\"https://zen12.com/getstarted\">BUY</a></footer>")});
  add('cloaked affiliate redirect',b=>{b.hub=b.hub.replace('</footer>',"<a href=\"/go/zen12\">BUY</a></footer>")});
  add('script injection',b=>{b.hub=b.hub.replace('</footer>',"<script>alert(1)</script></footer>")});
  add('new signup form',b=>{b.hub=b.hub.replace('</footer>',"<form><input type='email'></form></footer>")});
  add('new media request',b=>{b.hub=b.hub.replace('</footer>',"<img src='https://tracker.test/pixel.gif'></footer>")});
  add('event handler',b=>{b.hub=b.hub.replace('class="button"','class="button" onclick="reportPurchase()"')});
  add('missing noindex',b=>{b.hub=b.hub.replace('<meta name="robots" content="noindex,nofollow">','')});
  add('fictional article results',b=>{b.article=b.article.replace('# The Second Number Vanished','# Zen12 Proven')});
  add('removed primary source',b=>{b.article=b.article.replaceAll('https://pubmed.ncbi.nlm.nih.gov/1500880/','URL_REMOVED')});
  add('false monetized report',b=>{b.plan=b.plan.replaceAll('NOT COMPUTABLE','VERIFIED SALES COMPLETE')});
  add('claim affiliate click is sale',b=>{b.plan=b.plan.replaceAll('merchant_confirmed_purchase','click_count_revenue')});
  add('no creator ID uncertainty',b=>{b.plan=b.plan.replaceAll('HARD_HOLD','ACTIVE')});
  let rejected=0,accepted=[];
  for(const x of mutated){try{validate(x.bundle);accepted.push(x.name)}catch(e){rejected++;}}
  return {total:mutated.length,rejected,accepted,pass:rejected===mutated.length};
}
module.exports={validate,adversarialTests,fnv1a};
if(require.main===module){
 const fs=require('node:fs');
 const args=process.argv.slice(2);
 if(args.length!==4){process.stderr.write('Usage: node verify_r289.cjs article.md matrix.json hub.html plan.md\n');process.exit(2)}
 const keys=['article','matrix','hub','plan'];const b={};
 for(let i=0;i<4;i++)b[keys[i]]=fs.readFileSync(args[i],'utf8');
 const baseline=validate(b),tests=adversarialTests(b);
 if(!tests.pass){process.stderr.write('Unsafe mutants escaped: '+tests.accepted.join(', ')+'\n');process.exit(1)}
 process.stdout.write(JSON.stringify({baseline,tests},null,2)+'\n');
}
