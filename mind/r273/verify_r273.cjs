
'use strict';
const FROZEN={"sources":[["S01","https://pmc.ncbi.nlm.nih.gov/articles/PMC10198548/"],["S02","https://pubmed.ncbi.nlm.nih.gov/38458383/"],["S03","https://pubmed.ncbi.nlm.nih.gov/33049431/"],["S04","https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety"],["S05","https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking"],["S06","https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance"],["S07","https://inspire3.com/"],["S08","https://zen12.com/hnp"],["S09","https://zen12.com/secret/"],["S10","https://hypnosislive.com/mental-skills/total-focus"],["S11","https://zen12.com/about"],["S12","https://finalvestige.com/focus/"],["S13","https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"],["S14","https://finalvestige.com/2026/11/02/change-blindness/"],["S15","https://finalvestige.com/2026/11/02/mesmerism/"],["S16","https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171"],["S17","https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820"],["S18","https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1894"],["S19","https://github.com/finalvestigestudios/final-vestige-site-layer/pull/172"],["S20","https://pubmed.ncbi.nlm.nih.gov/16210542/"],["S21","https://pubmed.ncbi.nlm.nih.gov/20637455/"],["S22","https://pubmed.ncbi.nlm.nih.gov/17049881/"],["S23","https://www.lunduniversity.lu.se/publication/261789cd-c588-4dbd-afeb-f708fae90c52"],["S24","https://www.lucs.lu.se/research/choice-blindness-lab/publications/"]],"claims":[["C01","supported_mechanism",["S01"]],["C02","supported_scientific_review",["S01"]],["C03","not_supported_do_not_claim",["S01"]],["C04","supported_scientific_review",["S02"]],["C05","supported_scientific_review",["S03"]],["C06","unsupported_product_extrapolation",["S03"]],["C07","seller_description_only",["S08"]],["C08","seller_description_only",["S08"]],["C09","seller_claim_not_substantiated",["S08"]],["C10","false_evidence_transfer",["S01"]],["C11","not_verified_do_not_claim",["S08","S09"]],["C12","not_verified_do_not_claim",["S08"]],["C13","seller_description_only",["S10"]],["C14","seller_claim_not_substantiated",["S10"]],["C15","not_verified_do_not_claim",["S10"]],["C16","seller_claim_not_substantiated",["S07"]],["C17","false_absolute",["S04"]],["C18","regulatory_guidance",["S06"]],["C19","false_disclosure_standard",["S05"]],["C20","verified_first_party_live",["S12"]],["C21","false_historical_transfer",["S13"]],["C22","not_verified_hard_hold",["S07"]],["C23","false_measurement",["S17"]],["C24","not_verified_hard_hold",["S17"]],["C25","false_media_status",["S18"]],["C26","false_funnel_equivalence",["S12"]],["C27","supported_primary_abstract",["S20"]],["C28","supported_primary_abstract",["S21"]],["C29","supported_university_record",["S23"]],["C30","false_evidence_transfer",["S20","S21"]],["C31","not_supported_do_not_claim",["S22"]],["C32","false_historical_transfer",["S13"]],["C33","false_media_status",["S18"]],["C34","not_verified_hard_hold",["S07","S17"]]],"gates":["named_inspire3_acceptance","issued_publisher_specific_earning_url","exact_zen12_offer_identity","current_authenticated_cart_total","refund_policy_scope_and_fulfillment","approved_web_promotion_channels","approved_email_promotion_channels","approved_creatives_or_swipe_terms","product_specific_claim_substantiation","affiliate_attribution_permissions","ftc_adjacent_disclosure_qa","signed_out_mobile_browser_qa","word_press_sanitization_qa","founder_commercial_release_approval","independent_settled_commission_report","verified_product_sales_and_refunds_reconciliation"],"offers":[{"id":"zen12_premium","seller":"Inspire3 / Zen12","exact_seller_page":"https://zen12.com/hnp","distinct_promo":"https://zen12.com/secret/","offer_fit":"Structured downloadable meditation sounds and guides, not demonstrated treatment","authorization":"NOT_VERIFIED","issued_earning_url":null,"cart_total":null,"refunded_transaction_evidence":null,"product_specific_health_evidence":"NOT_ESTABLISHED","action":"NO_ACTIVE_AFFILIATE_LINK"},{"id":"hypnosis_live_total_focus","seller":"Inspire3 / Hypnosis Live","exact_seller_page":"https://hypnosislive.com/mental-skills/total-focus","offer_fit":"Specific 33-minute hypnosis audio; seller efficacy claims withheld","authorization":"NOT_VERIFIED","issued_earning_url":null,"checkout_total":null,"refund_terms":null,"action":"NO_ACTIVE_AFFILIATE_LINK"},{"id":"brainwave_shots","seller":"Inspire3","catalog_url":"https://inspire3.com/","exact_track_page":null,"offer_fit":"Short audio family; no precise eligible track yet","authorization":"NOT_VERIFIED","issued_earning_url":null,"action":"NO_ACTIVE_AFFILIATE_LINK"},{"id":"owned_paid_mind_product","seller":"Final Vestige","sku":null,"rights_cleared":"NOT_VERIFIED","active_checkout":"NOT_VERIFIED","refunds":"NOT_VERIFIED","paid_orders":null,"action":"DO_NOT_ADVERTISE"},{"id":"seven_day_focus_fieldbook","seller":"Final Vestige","public_url":"https://finalvestige.com/focus/","pricing":"FREE","new_form":false,"paid_order":false,"confirmed_jetpack_leads":"NOT_VERIFIED","action":"EXISTING_FREE_ROUTE_ONLY"}],"release":{"cms_write":false,"homepage_change":false,"menu_write":false,"newsletter_send":false,"social_post":false,"new_tracking_script":false,"affiliate_url_active":false,"autoplay":false,"merge_approved":false,"founder_release_approval":false}};
const CUES=[["0-6","00:00–00:06"],["6-12","00:06–00:12"],["12-18","00:12–00:18"],["18-24","00:18–00:24"],["24-30","00:24–00:30"],["30-36","00:30–00:36"],["36-42","00:36–00:42"]];
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function validate(d){
 const e=[];let m;
 try{m=JSON.parse(d.matrix)}catch(x){return ['unparseable JSON']}
 if(m.status!=='UNPUBLISHED_DRAFT'||m.decision!=='HARD_HOLD')e.push('matrix inactive release');
 const src=m.sources.map(x=>[x.id,x.url]),claims=m.claims.map(x=>[x.id,x.status,x.source_ids]);
 if(!eq(src,FROZEN.sources)||new Set(m.sources.map(x=>x.id)).size!==24)e.push('source identity or URL changed');
 if(!eq(claims,FROZEN.claims)||new Set(m.claims.map(x=>x.id)).size!==34||m.claims.some(x=>!x.source_ids.length))e.push('claim identity/status/source changes');
 if(!eq(m.commercial_gates.map(x=>x.id),FROZEN.gates)||m.commercial_gates.some(x=>x.status!=='HARD_HOLD'||x.evidence!=='NOT_VERIFIED'||x.release_blocker!==true))e.push('approval gate bypass or missing gate');
 if(!eq(m.release,FROZEN.release)||Object.values(m.release).some(v=>v!==false))e.push('release flags not frozen');
 if(!eq(m.offers,FROZEN.offers))e.push('seller permissions, rights, SKU, links, fulfillment or refund drift');
 if(m.measurement.metrics_status!=='NOT_COMPUTABLE'||!m.creator_fit.every(x=>!x.asset_id))e.push('invented revenue or media provenance');
 if(!m.validation_scope.no_proven_commissions||!m.validation_scope.video_not_playable||m.validation_scope.release_approval!==false)e.push('false commercial state');
 if(m.canonical_editorial_status!=='DUPLICATE_TOPIC_HARD_HOLD_R203_R244'||m.canonical_reference.public_slug_approved!==false||m.validation_scope.canonical_duplicate_review!=='BLOCKED_R203_R244'||!d.article.includes('CANONICAL EDITORIAL HOLD'))e.push('R203/R244 topic overlap was silently cleared');
 const hostAllowed=['finalvestige.com','www.ftc.gov','pubmed.ncbi.nlm.nih.gov','www.nccih.nih.gov','pmc.ncbi.nlm.nih.gov'];
 for(const[n,h]of [['A',d.a],['B',d.b],['HUB',d.hub]]){
  if(/<\s*(script|form|iframe|video|audio|source|track|img|picture|link|base|object|embed|use)\b/i.test(h))e.push(n+' unapproved media/script/form/embed');
  if(/\b(?:onclick|onload|onerror|autoplay|srcset|poster|xlink:href)\s*=/i.test(h)||/(?:url\s*\(|@import|@font-face|<meta[^>]*http-equiv)/i.test(h))e.push(n+' resource or injected CSS');
  for(const match of h.matchAll(/<a\b[^>]*?\bhref\s*=\s*(['"])(.*?)\1/gi)){
   const href=match[2];if(href[0]==='#')continue;
   const u=/^https:\/\/([^/?#]+)/.exec(href);
   if(!u||!hostAllowed.includes(u[1].toLowerCase()))e.push(n+' unsafe outbound destination '+href);
  }
  if(!h.includes('href="https://finalvestige.com/focus/"'))e.push(n+' Focus missing');
 }
 for(const[n,h]of [['A',d.a],['B',d.b]]){
  const buttons=[...h.matchAll(/<button\b[^>]*>/gi)].map(x=>x[0]),card=(h.match(/<div class="card" id="commercial-card">[\s\S]*?<\/div>/)||[])[0]||'';
  if(buttons.length!==1||!buttons[0].includes(' disabled ')||!buttons[0].includes('aria-disabled="true"')||!buttons[0].includes('id="zen12-buy-button"'))e.push(n+' active CTA');
  const p=card.indexOf('id="zen12-buy-button"'),q=card.indexOf('id="affiliate-disclosure"');
  if(p<0||q<p||q-p>350||!card.includes('Final Vestige may earn a commission')||!card.includes('no active affiliate link'))e.push(n+' disclosure adjacency');
  if(h.includes('The cited semantic-processing study did not test these recordings.')||!h.includes('Neither the 2023 binaural-beat EEG review nor the 2024 auditory-stimulation review tested Zen12 Premium'))e.push(n+' stale independent-science wording');
 }
 const commerce=h=>h.slice(h.indexOf('<section id="choice">'),h.indexOf('</main>'));
 if(!commerce(d.a)||commerce(d.a)!==commerce(d.b))e.push('A/B buyer copy drift');
 const cues=[...d.b.matchAll(/<p data-time="([^"]+)">([^<]+)<\/p>/g)].map(x=>[x[1],x[2].slice(0,11)]);
 if(!eq(cues,CUES))e.push('incorrect 42-second visible caption intervals or order');
 if(!d.b.includes('NOT HOSTED')||!d.b.includes('static poster')||d.b.includes('src="https://'))e.push('film actually hosted or false state');
 if(d.article.split(/\s+/).length<1900||!d.article.includes('16210542')||!d.article.includes('20637455')||!d.article.includes('Puységur'))e.push('weak source-driven article');
 if(d.plan.split(/\s+/).length<1000||!d.plan.includes('NOT COMPUTABLE')||!d.plan.includes('NO VERIFIED MATCH'))e.push('weak revenue acceptance plan');
 return e;
}
function adversarial(d){
 const v=validate(d);if(v.length)throw Error('baseline '+v.join('; '));
 let passed=0,failed=[],total=0;
 function probe(name,key,value){total++;const input={...d,[key]:value};if(validate(input).length)passed++;else failed.push(name)}
 const orig=JSON.parse(d.matrix);
 function matrixTest(name,fn){const x=JSON.parse(d.matrix);fn(x);probe(name,'matrix',JSON.stringify(x))}
 for(const id of FROZEN.gates)matrixTest('approve '+id,x=>x.commercial_gates.find(y=>y.id===id).status='APPROVED');
 for(const [name,fn]of [
 ['missing release',x=>x.release={}],['active link',x=>x.release.affiliate_url_active=true],
 ['Total Focus approval',x=>x.offers[1].authorization='APPROVED'],['Brainwave Shots earning',x=>x.offers[2].issued_earning_url='https://x.invalid/'],
 ['paid FV SKU',x=>x.offers[3].sku='fake'],['Fieldbook extra signup',x=>x.offers[4].new_form=true],
 ['source switch',x=>x.sources[1].url='https://x.invalid/source'],['duplicate source',x=>x.sources[1].id='S01'],
 ['claim evidence switch',x=>x.claims[3].status='PROVEN'],['historical transfer',x=>x.claims.find(y=>y.id==='C21').status='supported'],
 ['missing claim',x=>x.claims.pop()],['missing gate',x=>x.commercial_gates.pop()],
 ['invent paid revenue',x=>x.measurement.metrics_status='VERIFIED'],['invent media asset',x=>x.creator_fit[0].asset_id='FAKE'],
 ['false public article clearance',x=>x.canonical_reference.public_slug_approved=true],['duplicate gate quietly removed',x=>x.validation_scope.canonical_duplicate_review='PASSED'],['new release flag',x=>x.release.external_pixel=true]
 ])matrixTest(name,fn);
 for(const[name,key,old,replacement]of [
 ['A button enabled','a','type="button" disabled','type="button"'],
 ['B button enabled','b','type="button" disabled','type="button"'],
 ['A remove disclosure','a','id="affiliate-disclosure"','id="broken"'],
 ['B remove disclosure','b','id="affiliate-disclosure"','id="broken"'],
 ['A merchant link','a','href="https://finalvestige.com/focus/"','href="https://zen12.com/hnp"'],
 ['B protocol relative redirect','b','href="https://finalvestige.com/focus/"','href="//unknown.example/'],
 ['A CSS tracking request','a','</style>','body{background:url(//unknown.example/p.gif)}</style>'],
 ['B foreign SVG','b','</svg>','<use href="//unknown.example/"></use></svg>'],
 ['B wrong visible time','b','00:00–00:06','00:00–06:00'],
 ['B swapped cue','b','data-time="0-6"','data-time="6-0"'],
 ['A stale research citation','a','Neither the 2023 binaural-beat EEG review','The cited semantic-processing study did not test these recordings. Neither the 2023 binaural-beat EEG review'],
 ['B injected signup','b','</main>','<form action="/submit"></form></main>'],
 ['A forced video','a','</main>','<video autoplay></video></main>'],
 ['hub hidden script','hub','</main>','<script src="//bad.invalid/p.js"></script></main>'],
 ['article missing original source','article','16210542','00000000'],
 ['plan fake revenue','plan','NOT COMPUTABLE','DEFINITELY ZERO']
 ]){if(!d[key].includes(old))throw Error('ineffective negative test '+name);probe(name,key,d[key].replace(old,replacement))}
 return {total,passed,failed};
}
module.exports={validate,adversarial};
if(typeof require!=='undefined'&&require.main===module){
 const fs=require('fs');
 const paths={a:'mind/r268/ZEN12-A-TEXT-UNPUBLISHED.html',b:'mind/r268/ZEN12-B-OPTIONAL-FILM-UNPUBLISHED.html',hub:'mind/r268/MIND-ARCHIVE-UNPUBLISHED-PREVIEW.html',matrix:'mind/r273/CHOICE-BLINDNESS-OFFER-CLAIM-EVIDENCE-HARDHOLD.json',article:'mind/r273/THE-JAM-YOU-DIDNT-CHOOSE-CHOICE-BLINDNESS-UNPUBLISHED.md',plan:'mind/r273/ONE-OFFER-CHOICE-BLINDNESS-CONVERSION-AND-RELEASE-ACCEPTANCE.md'};
 const d={};for(const[k,p]of Object.entries(paths))d[k]=fs.readFileSync(p,'utf8');
 const errors=validate(d),n=adversarial(d);
 console.log('R273 baseline:',errors.length?'FAIL '+errors.join(' | '):'PASS');
 console.log('R273 negative cases:',n.passed+'/'+n.total,'rejected',n.failed.join(', '));
 if(errors.length||n.failed.length)process.exitCode=1;
}
