/* Mind & Perception R14 source-contract audit; no network access or side effects. */
'use strict';
function audit(html, guide, ledger, plan) {
  const checks=[];
  const check=(name,passed)=>checks.push({name,passed:Boolean(passed)});
  const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
  const evidenceIds=new Set(ledger.sources.map(s=>s.id));
  check('original substantial investigation',html.length>25000 && (html.match(/<section>/g)||[]).length===12);
  check('one article and no nested main', (html.match(/<article\b/g)||[]).length===1 && !/<main\b/i.test(html));
  check('has 11 cited scientific, official and policy references',(html.match(/<li id="r-/g)||[]).length>=11);
  check('all IDs unique',new Set(ids).size===ids.length);
  check('all footnotes resolve',[...html.matchAll(/href="#(r-[^"]+)"/g)].every(m=>ids.includes(m[1])));
  check('published Focus direct route',html.includes('https://finalvestige.com/focus/'));
  check('published Puységur direct route',html.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'));
  check('correct conditional commission disclosure',/Commercial disclosure:[\s\S]*?may earn a commission at no additional cost/.test(html));
  check('disclosure within same offer block as CTA',/<aside class="fv-cb-offer"[\s\S]*?Commercial disclosure:[\s\S]*?<button type="button" disabled/.test(html));
  check('merchant CTA disabled',/<button type="button" disabled aria-disabled="true">Merchant link not yet available<\/button>/.test(html));
  check('no active merchant links',!/href=["']https?:\/\/(?:zen12|hypnosislive|inspire3|affiliates\.inspire3)\./i.test(html));
  check('no form/script/iframe/input',!/<(?:form|script|iframe|input)\b/i.test(html));
  check('no autoload third-party media',!/<video\b|<source\b|\bautoplay\b/i.test(html));
  check('no email list added',!/(?:<form\b|mailchimp|beehiiv|<input\b)/i.test(html));
  check('original accessible non-scored practice',html.includes('<details>')&&html.includes('not a validated psychological test')&&html.includes('blue</b> notebook')&&html.includes('green</b> notebook'));
  check('focused keyboard outline',html.includes(':focus-visible'));
  check('reduced-motion support',html.includes('prefers-reduced-motion'));
  check('high contrast mode',html.includes('forced-colors'));
  check('mobile adaptation',html.includes('@media(max-width:640px)'));
  check('no externally imported fonts or CSS',!/@import\b|<link\b[^>]*stylesheet/i.test(html));
  check('source-cited product limits',html.includes('seller')&&html.includes('not established by the independent research'));
  check('guide is substantive',guide.length>11000);
  check('exact seller URLs in guide',guide.includes('https://zen12.com/about')&&guide.includes('https://zen12.com/getstarted'));
  check('guide rejects claims of direct personal use',guide.includes('has not purchased')&&guide.includes('has not inspected the purchased collection'));
  check('no invented checkout price or commission amount',!/[\$£€]\s?\d/.test(html)&&!/[\$£€]\s?\d/.test(guide));
  check('ledger at least 15 sources',ledger.sources.length>=15);
  check('ledger >=40 explicit claims',ledger.claims.length>=40);
  check('unique claim IDs',new Set(ledger.claims.map(c=>c.id)).size===ledger.claims.length);
  check('source links HTTPS',ledger.sources.every(s=>/^https:\/\//.test(s.url)));
  check('claim source IDs resolve',ledger.claims.every(c=>c.source_ids.every(id=>evidenceIds.has(id))));
  check('claim dispositions whitelisted',ledger.claims.every(c=>['SUPPORTED','QUALIFIED','REJECTED','UNVERIFIED'].includes(c.status)));
  check('partner approval remains false',ledger.account_authorization.approved===false);
  check('tracking URL null',ledger.account_authorization.authorized_affiliate_url===null);
  check('email permission null',ledger.account_authorization.email_channel_permission===null);
  check('creative rights null',ledger.account_authorization.creative_rights===null);
  check('draft remains unreleased',ledger.status==='UNPUBLISHED_DRAFT_HOLD');
  check('plan is privacy OFF',plan.includes('No analytics or outbound beacon ships'));
  check('two variant plan remains hypothesis',plan.includes('A: full source-cited')&&plan.includes('B: the same guide'));
  check('optional media no autoplay',plan.includes('preload=none')&&plan.includes('no autoplay'));
  check('no live CMS writes proposed',plan.includes('no CMS writes'));
  check('correct source-direct internal linking',plan.includes('https://finalvestige.com/focus/')&&plan.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'));
  return {checks,passed:checks.filter(c=>c.passed).length,total:checks.length,failures:checks.filter(c=>!c.passed).map(c=>c.name)};
}
if(typeof module!=='undefined')module.exports={audit};
if(typeof require!=='undefined' && require.main===module){
 const fs=require('node:fs'),path=require('node:path'),p=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
 const result=audit(p('wordpress-draft.html'),p('zen12-buyer-guide.md'),JSON.parse(p('claim-source-matrix.json')),p('EXPERIMENT_AND_NAV.md'));
 console.log(JSON.stringify(result,null,2));if(result.failures.length)process.exitCode=1;
}
