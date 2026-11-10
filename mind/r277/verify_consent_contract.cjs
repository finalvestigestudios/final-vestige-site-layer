'use strict';
// Mind R277 reproducible source-only contract. Run from full checkout:
// node mind/r277/verify_consent_contract.cjs
// No HTTP, no account writes, no tracking or paid calls.
const gateNames=[
'publisher_identity_verified','named_inspire3_acceptance','signed_partner_terms',
'approved_promotion_channels','issued_account_tracking_url','offer_slug_exact',
'final_checkout_total_verified','tax_fees_terms_verified',
'refund_policy_offer_specific_verified','customer_delivery_tested',
'claims_substantiated_or_excluded','ftc_near_cta_disclosure',
'no_merchant_newsletter_consent_transfer','privacy_no_pii_transfer',
'founder_release_approval','merchant_commission_settlement_evidence'
];
function ok(cond,label){if(!cond)throw Error('FAIL '+label)}
function validate(b){
const {html,guide,article,plan,matrix:m}=b;
ok(html&&guide&&article&&plan&&m,'five artifacts');
ok(m.schema==='fv_mind_r277_evidence_v1'&&m.release==='DRAFT_UNPUBLISHED'&&m.commercial==='HARD_HOLD','identity and hold');
ok(m.source_links.length===15&&m.claims.length===36,'source and claim inventory');
ok(m.claims.every(c=>c.id&&c.statement&&Array.isArray(c.source_ids)&&c.assessment),'classified claims complete');
ok(m.source_links.every(s=>/^https:\/\//.test(s.url)),'real source URLs');
const byId=Object.fromEntries(m.claims.map(c=>[c.id,c]));
ok(new Set(m.claims.map(c=>c.id)).size===36,'unique claims');
for(const id of ['C05','C08','C09','C10','C14','C17','C22','C26','C27','C28','C29','C30','C34','C35','C36'])
ok(/unverified|unsubstantiated|prohibited/.test(byId[id].assessment),'uncleared scientific or commercial claim '+id);
ok(byId.C15.assessment==='verified_page_observation_no_submission'&&byId.C16.assessment==='verified_page_observation_no_submission','seller signups not submitted');
ok(byId.C11.assessment==='independent_supported'&&byId.C13.assessment==='independent_supported','independent science classifications');
const gates=m.commercial_gates;
ok(gates.length===16&&new Set(gates.map(x=>x.id)).size===16,'16 unique gates');
ok(gateNames.every(n=>gates.some(g=>g.id===n))&&gates.every(g=>gateNames.includes(g.id)),'exact gate identities');
ok(gates.every(g=>g.status==='HARD_HOLD'&&g.verified===false&&g.approval_evidence===null),'16 hard holds not falsely cleared');
ok(m.revenue.label==='NOT_COMPUTABLE_NOT_ZERO','revenue label');
for(const n of ['qualified_human_sessions','merchant_confirmed_paid_orders','cleared_commissions','refunds','fees','net_revenue_per_1000_qualified_sessions'])
ok(m.revenue[n]===null,'unknown revenue field '+n);
ok(Object.values(m.release_guards).every(x=>x===false),'no release or attribution enabled');
const paths=m.separate_consent_paths;
ok(paths.length===4&&new Set(paths.map(x=>x.id)).size===4,'four distinct consent paths');
const find=id=>paths.find(x=>x.id===id);
ok(find('none').owner==='none'&&find('none').email_required===false,'no-account path');
ok(find('focus').owner==='Final Vestige / existing Jetpack Dispatch'&&find('focus').active_site_url==='https://finalvestige.com/focus/','existing FV only');
ok(find('zen12_free_audio').owner==='Zen12/Inspire3'&&find('zen12_free_audio').active_site_url===null,'unactivated separate seller list');
ok(find('zen12_premium').owner==='Zen12/Inspire3'&&find('zen12_premium').active_site_url===null,'no premium merchant CTA');
ok(m.creator_topic_fit.length===3&&m.creator_topic_fit.every(x=>x.grok_media_id===null),'no invented Grok IDs');
ok(m.ab_hypothesis.implementation==='NOT_LIVE','no fabricated live AB');
ok(html.includes('<meta name="robots" content="noindex,nofollow">'),'draft noindex');
ok(!/<(?:script|form|iframe|video|audio)\b/i.test(html),'no third party scripts forms or fake video');
ok(!/autoplay|localStorage|sendBeacon|dataLayer\.push/i.test(html),'no autoplay or tracker');
ok(html.includes('aria-labelledby="consent-map"'),'accessible consent section');
const consent=html.split('aria-labelledby="consent-map"')[1].split('aria-labelledby="optional-film"')[0];
for(const phrase of ["A free recording can still ask for your email","seller's own newsletter","No account: a free timer",
"FV Focus Fieldbook","Zen12 seller's free MP3 invitation","Zen12 Premium purchase",
"Consent is not transferable","zen12.com/welcome","zen12.com/freeaudio"])
ok(consent.includes(phrase),'specific seller consent warning '+phrase);
const held=html.split('aria-label="Held affiliate recommendation"')[1]||'';
ok(held.includes('disabled aria-disabled="true"'),'disabled commercial control');
const p=held.indexOf('</button>'),d=held.indexOf('If you purchase through a future authorized link');
ok(p>=0&&d>p&&d-p<250,'immediately adjacent commission disclosure');
ok(held.includes('may earn a commission'),'plain earning disclosure');
ok(!/href="https:\/\/(?:affiliates\.inspire3\.com|payhip\.com)/.test(html),'no earning link');
ok(html.includes("Does the merchant's free audio also join a mailing list?"),'free audio FAQ');
for(const phrase of ['Zen12 free-audio invitation',"seller's newsletter",'There are therefore **four distinct decisions**','No FV customer emails may be forwarded'])
ok(guide.includes(phrase),'canonical guide update '+phrase);
for(const phrase of ['The Free Track and the Second Permission','Four doors that must stay separate',
'The history problem','The three-question trial','A transparent offer','https://zen12.com/welcome',
'https://zen12.com/freeaudio','https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance'])
ok(article.includes(phrase),'new buyer investigation '+phrase);
ok(plan.includes('SV9m07PFTYk')&&plan.includes('not a verified immutable Grok internal asset ID'),'public video ID distinct from internal asset');
ok(plan.includes('PR #49')&&plan.includes('PR #172')&&plan.includes('Issue #150'),'other owner scope protected');
ok(/NOT COMPUTABLE|NOT_COMPUTABLE/.test(plan),'net revenue unknown');
return {status:'PASS',claims:36,gates:16,sources:15};
}
function mutate(base){const rows=[];
const add=(name,fn)=>rows.push({name,copy:()=>{const b=JSON.parse(JSON.stringify(base));fn(b);return b}});
for(const name of gateNames)add('forged approval '+name,b=>{b.matrix.commercial_gates.find(x=>x.id===name).verified=true});
add('missing gates',b=>b.matrix.commercial_gates=[]);
add('invented gate',b=>b.matrix.commercial_gates[0].id='invented');
add('approved gate',b=>b.matrix.commercial_gates[1].status='CLEARED');
add('claimed affiliate cash',b=>b.matrix.revenue.cleared_commissions=10);
add('zero masquerades as verified',b=>b.matrix.revenue.net_revenue_per_1000_qualified_sessions=0);
add('invented Grok asset',b=>b.matrix.creator_topic_fit[0].grok_media_id='fake');
add('AB falsely live',b=>b.matrix.ab_hypothesis.implementation='LIVE');
add('vendor consent becomes FV',b=>b.matrix.separate_consent_paths[2].owner='Final Vestige / existing Jetpack Dispatch');
add('activate seller signup',b=>b.matrix.separate_consent_paths[2].active_site_url='https://zen12.com/welcome');
add('activate seller checkout',b=>b.matrix.separate_consent_paths[3].active_site_url='https://zen12.com/hnp');
add('new tracking',b=>b.matrix.release_guards.web_analytics_script_added=true);
add('merchant science as proven',b=>b.matrix.claims.find(c=>c.id==='C14').assessment='independent_supported');
add('seller newsletter fake tested',b=>b.matrix.claims.find(c=>c.id==='C15').assessment='delivered');
add('remove consent section',b=>b.html=b.html.replace('aria-labelledby="consent-map"','aria-labelledby="missing-consent"'));
add('change vendor sender',b=>b.html=b.html.replace("seller's own newsletter","the FV Dispatch newsletter"));
add('activate button',b=>b.html=b.html.replace('disabled aria-disabled="true"','aria-disabled="false"'));
add('delete disclosure',b=>b.html=b.html.replace('If you purchase through a future authorized link','This is the best deal'));
add('capture email',b=>b.html+='<form><input type="email"></form>');
add('external JS',b=>b.html+='<script src="https://x.example/t.js"></script>');
add('autoplay',b=>b.html+='<video autoplay></video>');
add('remove noindex',b=>b.html=b.html.replace('<meta name="robots" content="noindex,nofollow">',''));
add('change FV route',b=>b.matrix.separate_consent_paths[1].active_site_url='https://another-list.example');
add('delete transfer guard',b=>b.guide=b.guide.replace('No FV customer emails may be forwarded','Emails may be forwarded'));
add('source fraud',b=>b.article=b.article.replaceAll('https://zen12.com/freeaudio','https://no-source.example'));
add('missing expected claims',b=>b.matrix.claims.pop());
return rows;
}
if(typeof module!=='undefined')module.exports={validate,mutate};
if(typeof require!=='undefined'&&require.main===module){
const fs=require('node:fs'),path=require('node:path'),root=path.resolve(__dirname,'../..');
const read=f=>fs.readFileSync(path.join(root,f),'utf8');
const base={
html:read('mind/r276/ZEN12-PURCHASE-EVIDENCE-ROOM-UNPUBLISHED.html'),
guide:read('mind/r276/ZEN12-IS-A-STRUCTURED-LIBRARY-NOT-A-CLINICAL-PROMISE-UNPUBLISHED.md'),
article:read('mind/r277/THE-FREE-TRACK-AND-THE-SECOND-PERMISSION-UNPUBLISHED.md'),
plan:read('mind/r277/OFFER-TO-REVENUE-DUAL-CONSENT-ACCEPTANCE.md'),
matrix:JSON.parse(read('mind/r277/SOURCE-CLAIM-CONSENT-AND-REVENUE-GATES.json'))
};
const result=validate(base);let rejected=0;const tests=mutate(base);
for(const c of tests){
let failure=false;try{validate(c.copy())}catch(e){failure=true}
if(!failure)throw Error('UNSAFE ACCEPTED: '+c.name);rejected++;
}
console.log('R277 source-only baseline '+result.status+'; '+rejected+'/'+tests.length+' deliberate unsafe mutations REJECTED.');
console.log('Native checkout/browser/email/hosted video/merchant payment all NOT TESTED.');
}
