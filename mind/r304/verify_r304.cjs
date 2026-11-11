#!/usr/bin/env node
// FV Mind R304 — exact-file fail-closed source validator. Run: node mind/r304/verify_r304.cjs
// Does not authorize publication. Source checks are NOT substitutes for browser/a11y or merchant verification.
'use strict';
const fs=require('node:fs'), path=require('node:path');
const read=(n)=>fs.readFileSync(path.join(__dirname,n),'utf8');
const files={
  article:read('THE-PENDULUM-THAT-ANSWERED-BEFORE-YOU-DID-UNPUBLISHED.md'),
  buyer:read('ZEN12-TRUTHFUL-BUYER-HYBRID-REVIEW-ONLY.html'),
  hub:read('MIND-ARCHIVE-FOUR-STREAM-WP-REVIEW-ONLY.html'),
  captions:read('ZEN12-42S-EXPLAINER.vtt'),
  dossier:read('ONE-OFFER-CREATOR-FIT-REVENUE-AND-RELEASE-ACCEPTANCE.md'),
  matrix:JSON.parse(read('IDEOMOTOR-CLAIM-SOURCE-OFFER-GATES.json'))
};
function ck(label,ok){if(!ok)throw new Error(label);}
function verify(f){
 const j=f.matrix;
 ck('SCHEMA',j.schema==='fv-mind-r304-commercial-evidence-v1');
 ck('SOURCE_COUNT',Array.isArray(j.sources)&&j.sources.length>=18);
 const ids=new Set(j.sources.map(s=>s.id));
 ck('SOURCE_UNIQUE',ids.size===j.sources.length);
 ck('SOURCE_VALID',j.sources.every(s=>s.id&&/^https:\/\/[^\s]+$/.test(s.url)&&s.reading_scope));
 ck('CLAIMS',Array.isArray(j.claims)&&j.claims.length>=30);
 ck('CLAIM_LINK',j.claims.every(c=>c.id&&c.statement&&ids.has(c.source_id)&&c.decision));
 ck('INELIGIBLE_CLAIM',j.claims.filter(c=>/approved|earning URL|perfect concentration|four hours|therapy|meditation benefits|fabrication|supernatural/i.test(c.statement)).every(c=>/EXCLUDE|QUALIFY|REQUIRED|SELLER/.test(c.decision)));
 ck('GATES',Array.isArray(j.commercial_gates)&&j.commercial_gates.length===18&&j.commercial_gates.every(g=>g.status==='HARD_HOLD'&&g.proof===null));
 ck('REVENUE_NULL',j.realized_revenue&&j.realized_revenue.net_revenue_per_1000===null&&j.realized_revenue.cleared_affiliate_commissions===null&&j.realized_revenue.status==='NOT_COMPUTABLE');
 ck('CREATOR_IDS',j.creator_paths.length===3&&j.creator_paths[0].asset_id===null&&j.creator_paths[2].asset_id===null);
 ck('DISCLOSURE_TEMPLATE',j.disclosure_template.includes('may earn a commission'));
 for(const [name,html] of [['BUYER',f.buyer],['HUB',f.hub]]){
   ck(name+'_DOCTYPE',/^<!doctype html>/i.test(html));
   ck(name+'_LANG',/<html lang="en">/.test(html));
   ck(name+'_VIEWPORT',/name="viewport"/.test(html));
   ck(name+'_NOINDEX',/noindex,nofollow/.test(html));
   ck(name+'_MAIN',/<main\b[^>]*id=/.test(html));
   ck(name+'_SKIP',/class="skip"/.test(html));
   ck(name+'_RESPONSIVE',/@media\(max-width:/.test(html));
   ck(name+'_REDUCED_MOTION',/prefers-reduced-motion:reduce/.test(html));
   ck(name+'_NO_SCRIPT',!/<script\b|<iframe\b|<form\b|<object\b|<embed\b/i.test(html));
   ck(name+'_NO_REDIRECT',!/<meta[^>]*http-equiv\s*=\s*["']?refresh/i.test(html));
   ck(name+'_NO_JS_ATTR',!/\bon(?:click|load|error|mouseover|submit|focus)\s*=/i.test(html));
   ck(name+'_NO_MERCHANT_LINK',!/<a\b[^>]*href\s*=\s*["'][^"']*(zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(html));
   ck(name+'_NO_ACTIVE_COMMERCE',!/<a[^>]*>(?:\s*buy now|purchase Zen12|claim offer)/i.test(html));
   ck(name+'_DISABLED',/<button\b[^>]*\bdisabled\b[^>]*>/.test(html));
   ck(name+'_DISCLOSURE',/may earn a commission at no additional cost to you/.test(html));
   ck(name+'_FREE_ROUTE',/https:\/\/finalvestige\.com\/focus\//.test(html));
 }
 ck('BUYER_GUARD_PROXIMITY',/class="disclosure"[\s\S]{0,1000}<button\b[^>]*disabled/.test(f.buyer));
 ck('HUB_GUARD_PROXIMITY',/class="disclose"[\s\S]{0,1000}<button\b[^>]*disabled/.test(f.hub));
 ck('BUYER_NO_PLAYBACK_CLAIM',/not encoded, hosted or playable media/i.test(f.buyer));
 ck('BUYER_NO_COUNTDOWN',!/15:00\.00|limited time|act now|only today/i.test(f.buyer));
 ck('BUYER_SELLER_FORMAT',/twelve levels and 48 MP3 recordings/i.test(f.buyer));
 ck('BUYER_CONTRAST',/not every recording is a guided session/i.test(f.buyer));
 ck('BUYER_SOURCES',/pubmed\.ncbi\.nlm\.nih\.gov\/35184700/.test(f.buyer));
 ck('HUB_FOUR_STREAMS',/Perception &amp; Attention/.test(f.hub)&&/History of Suggestion/.test(f.hub)&&/Practice &amp; Reflection/.test(f.hub)&&/Tools Under Review/.test(f.hub));
 ck('CAPTIONS_HEADER',/^WEBVTT\s/.test(f.captions));
 ck('CAPTIONS_END',/00:00:31\.000 --> 00:00:42\.000/.test(f.captions));
 ck('CAPTIONS_CONTENT',/twelve levels[\s\S]*forty-eight MP3/.test(f.captions));
 ck('ARTICLE_LENGTH',f.article.trim().split(/\s+/).length>=1800);
 ck('ARTICLE_SOURCE',/## Source trail/.test(f.article)&&/pubmed\.ncbi\.nlm\.nih\.gov\/22377138/.test(f.article));
 ck('ARTICLE_PUYSEGUR',/Puységur/.test(f.article));
 ck('DOSSIER_REVENUE',/NOT COMPUTABLE/.test(f.dossier)&&/cleared_affiliate_commission/.test(f.dossier));
 ck('DOSSIER_EXPERIMENT',/text only vs identical guide plus optional video/i.test(f.dossier));
 ck('DOSSIER_RELEASE_HOLD',/HARD HOLD/.test(f.dossier));
 return true;
}
function clone(f){return {...f,matrix:JSON.parse(JSON.stringify(f.matrix))};}
function test(name,mutate,expected){
 const f=clone(files);mutate(f);
 try{verify(f);throw new Error('MUTATION_NOT_REJECTED:'+name);}
 catch(e){if(e.message==='MUTATION_NOT_REJECTED:'+name||e.message!==expected)throw new Error(name+' expected '+expected+' got '+e.message);}
}
const mutations=[
 ['activate gate',f=>{f.matrix.commercial_gates[0].status='APPROVED';},'GATES'],
 ['invent approval proof',f=>{f.matrix.commercial_gates[0].proof='yes';},'GATES'],
 ['invent revenue',f=>{f.matrix.realized_revenue.net_revenue_per_1000=12;},'REVENUE_NULL'],
 ['invent settled commission',f=>{f.matrix.realized_revenue.cleared_affiliate_commissions=5;},'REVENUE_NULL'],
 ['invent creator asset',f=>{f.matrix.creator_paths[0].asset_id='invented';},'CREATOR_IDS'],
 ['broken claim link',f=>{f.matrix.claims[0].source_id='FAKE';},'CLAIM_LINK'],
 ['truncate claim matrix',f=>{f.matrix.claims=f.matrix.claims.slice(0,2);},'CLAIMS'],
 ['bad source',f=>{f.matrix.sources[0].url='javascript:evil';},'SOURCE_VALID'],
 ['duplicate source',f=>{f.matrix.sources[1].id=f.matrix.sources[0].id;},'SOURCE_UNIQUE'],
 ['remove disclosure template',f=>{f.matrix.disclosure_template='';},'DISCLOSURE_TEMPLATE'],
 ['buyer executable JS',f=>{f.buyer+='<script>bad()</script>';},'BUYER_NO_SCRIPT'],
 ['hub executable JS',f=>{f.hub+='<script>bad()</script>';},'HUB_NO_SCRIPT'],
 ['buyer checkout link',f=>{f.buyer+='<a href="https://zen12.com/getstarted">Buy now</a>';},'BUYER_NO_MERCHANT_LINK'],
 ['hub checkout link',f=>{f.hub+='<a href="https://hypnosislive.com/mental-skills/total-focus">Buy</a>';},'HUB_NO_MERCHANT_LINK'],
 ['buyer iframe',f=>{f.buyer+='<iframe src="https://example.com"></iframe>';},'BUYER_NO_SCRIPT'],
 ['hub signup',f=>{f.hub+='<form action="/subscribe"></form>';},'HUB_NO_SCRIPT'],
 ['meta redirect',f=>{f.buyer+='<meta http-equiv="refresh" content="0;url=https://evil.test">';},'BUYER_NO_REDIRECT'],
 ['inline click',f=>{f.hub+='<div onclick="alert(1)">go</div>';},'HUB_NO_JS_ATTR'],
 ['buyer no disabled CTA',f=>{f.buyer=f.buyer.replace('type="button" disabled','type="button"');},'BUYER_DISABLED'],
 ['hub no disabled CTA',f=>{f.hub=f.hub.replace('type="button" disabled','type="button"');},'HUB_DISABLED'],
 ['buyer disclosure missing',f=>{f.buyer=f.buyer.replace('may earn a commission at no additional cost to you','potential earnings');},'BUYER_DISCLOSURE'],
 ['hub disclosure missing',f=>{f.hub=f.hub.replace('may earn a commission at no additional cost to you','potential earnings');},'HUB_DISCLOSURE'],
 ['buyer lost free path',f=>{f.buyer=f.buyer.replaceAll('https://finalvestige.com/focus/','/other/');},'BUYER_FREE_ROUTE'],
 ['hub lost free path',f=>{f.hub=f.hub.replaceAll('https://finalvestige.com/focus/','/other/');},'HUB_FREE_ROUTE'],
 ['caption header',f=>{f.captions=f.captions.replace('WEBVTT','TEXT');},'CAPTIONS_HEADER'],
 ['caption duration',f=>{f.captions=f.captions.replace('00:00:42.000','00:01:20.000');},'CAPTIONS_END'],
 ['article source removed',f=>{f.article=f.article.replace('## Source trail','## Unsupported');},'ARTICLE_SOURCE'],
 ['article context removed',f=>{f.article=f.article.replaceAll('Puységur','Puysegur');},'ARTICLE_PUYSEGUR'],
 ['dossier attribution removed',f=>{f.dossier=f.dossier.replaceAll('NOT COMPUTABLE','0');},'DOSSIER_REVENUE'],
 ['dossier release hold removed',f=>{f.dossier=f.dossier.replaceAll('HARD HOLD','ACTIVE');},'DOSSIER_RELEASE_HOLD'],
];
if(require.main===module){
 verify(files);let passed=0;for(const [name,mutate,expected] of mutations){test(name,mutate,expected);passed++;}
 console.log(JSON.stringify({baseline:'PASS',negative_mutations_passed:passed,total_negative_mutations:mutations.length,commercial_gates:'18/18 HARD_HOLD',source_count:files.matrix.sources.length,claim_count:files.matrix.claims.length,live_or_browser_or_merchant_tested:false},null,2));
}
module.exports={verify,test,mutations};
