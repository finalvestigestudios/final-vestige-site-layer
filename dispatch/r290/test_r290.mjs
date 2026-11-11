// Non-sending, dependency-free, static checks. Execute from repo root: node dispatch/r290/test_r290.mjs
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
const dir=dirname(fileURLToPath(import.meta.url));
const load=name=>readFileSync(join(dir,name),'utf8');
const [md,txt,html]=['issue-01.review.md','issue-01.review.txt','issue-01.review.html'].map(load);
const evidence=JSON.parse(load('evidence.json'));
const checklist=load('preview-and-consent-acceptance.md');
const subject='What a careful observer can still miss';
const pre='A 1999 attention experiment changes how we read a confident account of what happened.';
const cta='https://finalvestige.com/2026/11/02/change-blindness/';
let count=0; const assert=(x,m)=>{if(!x)throw Error(m);count++};
for(const src of [md,txt,html]){
  for(const term of [subject,pre,cta,'https://doi.org/10.1068/p281059','https://pubmed.ncbi.nlm.nih.gov/10694957/','[[VALID_FINAL_VESTIGE_POSTAL_ADDRESS_REQUIRED]]','[[JETPACK_RECEIVED_UNSUBSCRIBE_REQUIRED]]','[[FOUNDER_FINAL_CAMPAIGN_APPROVAL_REQUIRED]]'])assert(src.includes(term),'missing '+term);
  assert(!/zen12\.com|hypnosislive\.com|affiliates\.inspire3\.com/i.test(src),'merchant URL leaked');
  assert(!/utm_(?:source|campaign|medium)/i.test(src),'tracking deployed without approval');
}
assert(html.includes('<html lang="en">')&&html.includes('role="presentation"'),'accessible table/email structure');
assert(!/<script|<iframe|@import/i.test(html),'active markup in email');
assert(!/<img\b/i.test(html),'unnecessary image in issue');
assert(evidence.campaign.total===6 && evidence.campaign.editorial_issues.length===4 && evidence.campaign.commercial_issues.length===2,'4:2 mix changed');
assert(evidence.draft_mode==='OPTIONAL_NOT_ADOPTED' && evidence.campaign.send_authorized===false,'draft treated as approved');
assert(evidence.jetpack.confirmed_send_eligible===null && evidence.jetpack.counts_additive===false,'fake eligible audience');
assert(evidence.jetpack.total===3 && evidence.jetpack.confirmed===3 && evidence.jetpack.unconfirmed_requests===2,'counter states lost');
assert(evidence.jetpack.actual_jetpack_preview_verified===false && evidence.jetpack.received_mail_preview_verified===false,'fake preview evidence');
assert(evidence.jetpack.valid_publisher_postal_verified===false && evidence.jetpack.unsubscribe_function_verified===false,'fake FTC proof');
for(const m of Object.values(evidence.merchant_gate)){assert(!m.account_accepted&&!m.email_marketing_authorized&&!m.issued_earning_url&&!m.approved_live_guide,'unverified merchant accepted');}
assert(evidence.analytics.qualified_human_sessions===null && evidence.analytics.settled_net_revenue===null && evidence.analytics.net_revenue_per_1000===null,'fabricated financial numbers');
assert(evidence.analytics.proposed_only===true && evidence.analytics.Grok_medium==='organic_social','unapproved analytics deployment');
assert(checklist.includes('Preview email') && checklist.includes('Send test email') && checklist.includes('not performed'),'preview confused with test send');
assert(checklist.includes('confirmed_signup') && checklist.includes('suppressed/unsubscribed'),'consent spec incomplete');
console.log('PASS '+count+' offline R290 source / legal / consent / 4:2 invariants');
