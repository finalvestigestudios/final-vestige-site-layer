#!/usr/bin/env node
'use strict';
/* Source-level tests only: run with node mind/r313/verify_r313.cjs.
 * Does NOT verify WordPress, WCAG, real browser, playable film, partner approval,
 * real analytics events, payment settlement or net revenue.
 */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const get=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
const A=get('ZEN12-A-TEXT-GUIDE-REVIEW.html');
const B=get('ZEN12-B-OPTIONAL-FILM-GUIDE-REVIEW.html');
const H=get('MIND-FOUR-STREAM-WP-REVIEW.html');
const article=get('THE-VOICE-NOBODY-REPORTED-HEARING-UNPUBLISHED.md');
const m=JSON.parse(get('SOURCE-CLAIM-OFFER-GATES.json'));
const plan=get('CONVERSION-SOURCE-RELEASE-ACCEPTANCE.md');
const vtt=get('ORIGINAL-42S-CAPTIONS.vtt');
let positive=0, negative=0;
const pass=(condition,message)=>{assert.ok(condition,message);positive++};
const buttons=s=>[...s.matchAll(/<button\b[^>]*>/gi)].map(x=>x[0]);
const filmRemoval=s=>s.replace(/<section class="film" data-optional-film[\s\S]*?<\/section>/,'');
function safeHtml(s){
  if(!s.includes('<html lang="en">')||!s.includes('name="viewport"'))return false;
  if(!s.includes('name="robots" content="noindex,nofollow"'))return false;
  if(!s.includes(':focus-visible')||!s.includes('prefers-reduced-motion'))return false;
  if(!s.includes('https://finalvestige.com/focus/'))return false;
  const controls=buttons(s);
  if(controls.length!==1||!/(?:\s)disabled(?=\s|>|=)/i.test(controls[0]))return false;
  if(!s.includes('may earn a commission')||!s.includes('no additional cost to you'))return false;
  if(/<\s*(?:script|iframe|form|video|audio|input)\b|<img\b[^>]+src\s*=|<link\b/i.test(s))return false;
  if(/\b(?:onload|onclick|onerror|onmouseover)\s*=|@import/i.test(s))return false;
  if(/href\s*=\s*["'](?:https?:)?\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(s))return false;
  if(/googletagmanager|gtag\s*\(|dataLayer|fbq\s*\(|affiliate_click\s*=|paid_order_verified\s*=/i.test(s))return false;
  const end=s.indexOf('</button>'),disc=s.indexOf('may earn a commission');
  if(end<0||disc<end||disc-end>650)return false;
  return true;
}
for(const [name,s] of [['A',A],['B',B],['hub',H]]){
  pass(safeHtml(s),name+': native disabled CTA, nearby disclosure, no merchant links or dynamic media');
  pass(buttons(s).length===1,name+': exactly one disabled purchase control');
  pass(!/\$\d+/.test(s),name+': no time-sensitive advertised price');
}
pass(filmRemoval(B)===A,'Core buyer copy must be byte-identical outside optional film');
pass(B.includes('data-optional-film')&&!A.includes('data-optional-film'),'Only B contains film');
pass(!/<video\b/i.test(B)&&B.includes('<svg')&&B.includes('Timed original transcript'),'B remains storyboard, no false playback claim');
pass(vtt.startsWith('WEBVTT')&&vtt.includes('00:00:42.000'),'Caption treatment terminates at 42 seconds');
pass(article.trim().split(/\s+/).length>=1800,'Deep original article');
for(const needle of ['Dalton','Fraenkel','Raveh','Lavie','nineteen','secondary published account','2023 systematic review','not a replication']){
 pass(article.toLowerCase().includes(needle.toLowerCase()),'Article source boundary: '+needle);
}
pass(m.sources.length>=20&&m.claims.length>=35,'Source and claim count');
pass(m.claims.every(c=>c.source_ids.every(id=>m.sources.some(s=>s.id===id))),'All source IDs resolve');
pass(Object.keys(m.authorization_gates).length===18&&Object.values(m.authorization_gates).every(v=>v==='HARD_HOLD'),'All authorization gates held');
pass(m.creator_map.length===3&&m.creator_map.every(c=>c.grok_asset_id===null),'No invented Grok asset ID');
pass(m.kpi.status==='NOT_COMPUTABLE'&&m.kpi.value===null,'No fabricated cleared revenue');
pass(plan.includes('NOT COMPUTABLE')&&plan.includes('refund')&&plan.includes('settled'),'Revenue contract distinguishes clicks from sales');
const mutations=[
['remove disabled',s=>s.replace(' disabled aria-describedby=',' aria-describedby=')],
['merchant link',s=>s.replace('</button>','</button><a href="https://zen12.com/getstarted">Buy</a>')],
['affiliate link',s=>s.replace('</button>','</button><a href="https://affiliates.inspire3.com/">Go</a>')],
['script',s=>s.replace('</body>','<script>alert(1)</script></body>')],
['iframe',s=>s.replace('</body>','<iframe src="https://example.org/"></iframe></body>')],
['input',s=>s.replace('</body>','<input type="email"></body>')],
['new signup',s=>s.replace('</body>','<form><input type="email"></form></body>')],
['pretend film',s=>s.replace('</body>','<video autoplay></video></body>')],
['pixel',s=>s.replace('</body>','<img src="https://pixel.example/x"></body>')],
['remove disclosure',s=>s.replace('may earn a commission','may earn a reward')],
['strip focus link',s=>s.replaceAll('https://finalvestige.com/focus/','/missing')],
['allow indexing',s=>s.replace('noindex,nofollow','index,follow')],
['remove lang',s=>s.replace('<html lang="en">','<html>')],
['remove focus outline',s=>s.replaceAll(':focus-visible',':hover')],
['remove motion support',s=>s.replaceAll('prefers-reduced-motion','prefers-any-motion')],
['add event',s=>s.replace('</body>','<div onclick="track()">bad</div></body>')],
['fake payout',s=>s.replace('</body>','<div paid_order_verified="1"></div></body>')],
['import',s=>s.replace('</style>','@import url(https://track.example/x.css);</style>')]
];
for(const [name,fn] of mutations){
 for(const original of [A,B,H]){
  const bad=fn(original);
  if(bad===original)continue;
  assert.equal(safeHtml(bad),false,'Unsafe mutation accepted: '+name);
  negative++;
 }
}
const forged=structuredClone(m);forged.authorization_gates.account_specific_publisher_acceptance='APPROVED';
pass(!Object.values(forged.authorization_gates).every(v=>v==='HARD_HOLD'),'Forged partner approval rejected');
const orphan=structuredClone(m);orphan.claims[0].source_ids=['UNREGISTERED'];
pass(!orphan.claims.every(c=>c.source_ids.every(id=>orphan.sources.some(s=>s.id===id))),'Orphan source rejected');
const revenue=structuredClone(m);revenue.kpi.value=300;
pass(!(revenue.kpi.status==='NOT_COMPUTABLE'&&revenue.kpi.value===null),'Forged KPI rejected');
console.log('PASS R313: '+positive+' positive assertions, '+negative+' unsafe HTML mutations rejected; source-only. Real browser, CMS, merchant, CI and settlement UNTESTED.');
