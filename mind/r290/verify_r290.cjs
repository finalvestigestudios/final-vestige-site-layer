/* R290 cumulative source-level acceptance; no CMS/network/commerce actions.
CLI: node mind/r290/verify_r290.cjs <article> <matrix> <hub> <plan> <R284_A_html> <R284_B_html>
Unlike R289, R290 must actually load and validate BOTH inherited canonical guide bytes. */
'use strict';
const E={parent:'0c4bbde23c765246782ea3dde85f06c59e710fc9',A:'ed05f7c4',B:'7a5e3be1',sources:'1c1a4290',claims:'7177d427',gates:'3f10db94',
paths:['mind/r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html','mind/r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html']};
function hash(s){let n=2166136261;for(let i=0;i<s.length;i++){n^=s.charCodeAt(i);n=Math.imul(n,16777619)}return (n>>>0).toString(16).padStart(8,'0')}
function ok(x,m){if(!x)throw Error(m)}
function html(t,label){
 ok(/^<!doctype html>/i.test(t.trim())&&/<html lang="en"/.test(t)&&/<main\b/.test(t),label+' semantics');
 ok(/name="viewport"/.test(t)&&/noindex,nofollow/.test(t),label+' unpublished layout');
 ok(!/<\s*(script|iframe|form|object|embed|input|link|audio|video|source)\b/i.test(t),label+' forbidden active content');
 ok(!/\bon(click|load|error|submit|focus)\s*=|javascript\s*:|data\s*:\s*text\/html|srcdoc\s*=/i.test(t),label+' dangerous attributes');
 // Decode numeric/HTML escapes to catch obfuscated URL attributes; never load network.
 const raw=t.replace(/&#x([0-9a-f]+);?/gi,(_,h)=>String.fromCharCode(parseInt(h,16))).replace(/&#([0-9]+);?/g,(_,n)=>String.fromCharCode(+n)).replace(/&sol;/gi,'/').replace(/&colon;/gi,':').replace(/&amp;/gi,'&');
 const anchors=[...raw.matchAll(/<a\b[^>]*href=["']([^"']+)["']/gi)].map(x=>x[1]);
 ok(anchors.every(a=>a.startsWith('#')||/^https:\/\/(finalvestige\.com|www\.ftc\.gov|pubmed\.ncbi\.nlm\.nih\.gov|doi\.org)\//.test(a)),label+' anchor allowlist');
 ok(!/\b(?:src|action|href|formaction)\s*=\s*["'][^"']*(?:zen12|hypnosislive|inspire3|brainwaveshots)\.com/i.test(raw),label+' merchant link withheld');
 const buttons=[...raw.matchAll(/<button\b[^>]*>/gi)].map(x=>x[0]);
 ok(buttons.filter(x=>/\bdisabled\b/i.test(x)).length===1,label+' one disabled commercial control');
 const btn=buttons.find(x=>/\bdisabled\b/i.test(x));ok(/type="button"/i.test(btn)&&!/\b(href|onclick|formaction)\b/i.test(btn),label+' inert button');
 const i=raw.indexOf(btn),near=raw.slice(Math.max(0,i-950),i);
 ok(/commission at no additional cost to you/i.test(near)&&/affiliate/i.test(near),label+' adjacent FTC disclosure');
 ok(raw.includes('https://finalvestige.com/focus/'),label+' free existing funnel');
 ok(!/guaranteed cognitive enhancement|guaranteed wealth|FDA approved brainwave|official FV affiliate partner approved/i.test(raw),label+' prohibited efficacy/approval copy');
 return {anchors:anchors.length,disabled:1};
}
function validate(b){
 for(const k of ['article','matrix','hub','plan','a','b'])ok(typeof b[k]==='string'&&b[k].length>3000,'missing '+k);
 const m=JSON.parse(b.matrix);
 ok(m.version==='R290'&&m.parent_sha===E.parent&&m.scope==='ONLY_MIND','lineage and scope');
 ok(m.commercial==='HARD_HOLD'&&m.publication==='UNPUBLISHED'&&m.merchant_specific_affiliate_approval==='NOT_AUTHENTICATED','commercial release gate');
 ok(JSON.stringify(m.canonical_presell)===JSON.stringify(E.paths),'canonical A/B path identity');
 ok(m.sources.length===18&&m.claims.length===28,'source and claim counts');
 ok(hash(JSON.stringify(m.sources.map(x=>[x.id,x.url])))===E.sources,'source/URL exact joins');
 ok(hash(JSON.stringify(m.claims.map(x=>[x.id,x.statement,x.source_id,x.decision])))===E.claims,'claim/decision/source joins');
 ok(new Set(m.sources.map(x=>x.id)).size===18&&new Set(m.claims.map(x=>x.id)).size===28,'duplicate IDs');
 ok(m.claims.every(c=>m.sources.some(s=>s.id===c.source_id)),'unknown source');
 const names=Object.keys(m.release_gates);
 ok(names.length===18&&hash(JSON.stringify(names))===E.gates,'exact release-gate roster');
 ok(names.every(n=>m.release_gates[n].status==='HARD_HOLD'),'release gate activated');
 ok(m.media_status==='B_IS_STATIC_STORYBOARD_NOT_PLAYABLE','fake playable film');
 ok(m.creator_routes.length===3&&m.creator_routes.every(r=>r.asset_id===null&&r.video_url===null&&r.go_live===false),'fake Grok asset');
 ok(m.measurement_contract.revenue_numerator.includes('CLEARED FV AFFILIATE COMMISSIONS')&&m.measurement_contract.revenue_numerator.includes('never use affiliate merchant retail sale total'),'gross vs net receipts');
 ok(/4,493/.test(b.article)&&/83%|Eighty-three percent/.test(b.article)&&/Puységur/.test(b.article),'scientific precision');
 ok(/NOT COMPUTABLE/.test(b.plan)&&/HARD HOLD/.test(b.plan),'unverified revenue/release');
 const hub=html(b.hub,'hub'),A=html(b.a,'A'),B=html(b.b,'B');
 ok(hash(b.a)===E.A&&hash(b.b)===E.B,'frozen canonical A/B bytes, re-review if updated');
 for(const [label,t] of [['A',b.a],['B',b.b]]){
  ok(/12 levels/i.test(t)&&/48 MP3/i.test(t),label+' merchant feature');
  ok(/14 days/i.test(t)&&/five refunded sessions|five sessions|5 sessions/i.test(t),label+' Hypnosis Live limits');
  ok(/six.month/i.test(t)&&/fewer than half|less than half/i.test(t),label+' Brainwave refund constraints');
  ok(/merchant newsletters/i.test(t),label+' external seller consent separation');
 }
 ok(/Storyboard only/i.test(b.b)&&/no playable video yet/i.test(b.b)&&/42-second/i.test(b.b),'B is static film concept');
 ok(!/42-second buyer's question/i.test(b.a),'A has no B concept');
 return {pass:true,canonicalGuidesLoaded:2,sources:18,claims:28,gates:18,hub,A,B};
}
function adversarialTests(b){
 const cases=[];const add=(n,f)=>{let v={...b};f(v);cases.push([n,v])};
 add('missing A',x=>x.a='');
 add('missing B',x=>x.b='');
 add('swapped A',x=>x.a=b.b);
 add('swapped B',x=>x.b=b.a);
 add('A merchant anchor',x=>x.a=x.a.replace('</main>','<a href="https://zen12.com/getstarted">Buy</a></main>'));
 add('B encoded merchant anchor',x=>x.b=x.b.replace('</main>','<a href="https:&#x2f;&#x2f;zen12.com/getstarted">Buy</a></main>'));
 add('A active button',x=>x.a=x.a.replace('type="button" disabled','type="button"'));
 add('B active button',x=>x.b=x.b.replace('type="button" disabled','type="button"'));
 add('A form',x=>x.a=x.a.replace('</body>','<form><input type="email"></form></body>'));
 add('B script',x=>x.b=x.b.replace('</body>','<script>alert(1)</script></body>'));
 add('A disclosure',x=>x.a=x.a.replace('commission at no additional cost','commission not mentioned'));
 add('B disclosure',x=>x.b=x.b.replace('commission at no additional cost','no commission'));
 add('A refund rule',x=>x.a=x.a.replace(/fewer than half/i,'any amount'));
 add('B refund rule',x=>x.b=x.b.replace(/six.month/i,'unlimited'));
 add('A changed product',x=>x.a=x.a.replace('48 MP3','80 MP3'));
 add('B fake film',x=>x.b=x.b.replace('no playable video yet','playable now'));
 add('hub merchant anchor',x=>x.hub=x.hub.replace('</main>','<a href="https://zen12.com/getstarted">BUY</a></main>'));
 add('hub script',x=>x.hub=x.hub.replace('</main>','<script>1</script></main>'));
 add('hub form',x=>x.hub=x.hub.replace('</main>','<form></form></main>'));
 add('hub active control',x=>x.hub=x.hub.replace('type="button" disabled','type="button"'));
 add('hub disclosure',x=>x.hub=x.hub.replace('commission at no additional cost','payment undisclosed'));
 add('hub unsupported claim',x=>x.hub=x.hub.replace('</main>','<p>guaranteed cognitive enhancement</p></main>'));
 add('source swapped',x=>{let m=JSON.parse(x.matrix);m.sources[0].url=m.sources[1].url;x.matrix=JSON.stringify(m)});
 add('claim source swapped',x=>{let m=JSON.parse(x.matrix);m.claims[0].source_id='zen12order';x.matrix=JSON.stringify(m)});
 add('claim altered',x=>{let m=JSON.parse(x.matrix);m.claims[0].statement='Zen12 cures inattentional blindness';x.matrix=JSON.stringify(m)});
 add('gate dropped',x=>{let m=JSON.parse(x.matrix);delete m.release_gates.founder_production_release_approval;x.matrix=JSON.stringify(m)});
 add('gate activated',x=>{let m=JSON.parse(x.matrix);m.release_gates.issued_earning_url.status='APPROVED';x.matrix=JSON.stringify(m)});
 add('affiliate approved',x=>{let m=JSON.parse(x.matrix);m.merchant_specific_affiliate_approval='APPROVED';x.matrix=JSON.stringify(m)});
 add('fictional Grok ID',x=>{let m=JSON.parse(x.matrix);m.creator_routes[0].asset_id='madeup';x.matrix=JSON.stringify(m)});
 add('fake video',x=>{let m=JSON.parse(x.matrix);m.media_status='PLAYABLE';x.matrix=JSON.stringify(m)});
 add('retail gross counted',x=>{let m=JSON.parse(x.matrix);m.measurement_contract.revenue_numerator='merchant retail sales';x.matrix=JSON.stringify(m)});
 add('plan zero for unknown',x=>x.plan=x.plan.replaceAll('NOT COMPUTABLE','ZERO'));
 add('plan released',x=>x.plan=x.plan.replaceAll('HARD HOLD','APPROVED'));
 add('article missing sample',x=>x.article=x.article.replaceAll('4,493','many'));
 let rejected=0,escaped=[];
 for(const [name,x] of cases){try{validate(x);escaped.push(name)}catch(_){rejected++}}
 return {total:cases.length,rejected,escaped,pass:rejected===cases.length};
}
module.exports={validate,adversarialTests,hash};
if(require.main===module){
 const fs=require('node:fs'),args=process.argv.slice(2);
 if(args.length!==6){console.error('Usage: verify_r290 article matrix hub plan R284_A R284_B');process.exit(2)}
 const b={};['article','matrix','hub','plan','a','b'].forEach((k,i)=>b[k]=fs.readFileSync(args[i],'utf8'));
 const baseline=validate(b),tests=adversarialTests(b);
 console.log(JSON.stringify({baseline,tests},null,2));if(!tests.pass)process.exit(1);
}