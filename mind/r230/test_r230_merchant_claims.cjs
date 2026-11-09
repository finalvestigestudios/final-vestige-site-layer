'use strict';
// node mind/r230/test_r230_merchant_claims.cjs
// Release HOLD guard, no network, secrets, forms or commercial writes.
const fs=require('node:fs'),path=require('node:path');
const root=path.join(__dirname,'..','r229');
const read=(p)=>fs.readFileSync(path.join(root,p),'utf8');
const baseline={
 a:read('zen12-A-TEXT-UNPUBLISHED.html'),b:read('zen12-B-OPTIONAL-42S-UNRENDERED.html'),
 h:read('mind-hub-WP-PREVIEW-UNPUBLISHED.html'),m:JSON.parse(read('SOURCE-CLAIM-COMMERCE-GATES.json')),
 art:read('THE-BEAT-YOUR-EARS-INVENT-UNPUBLISHED.md'),
 plan:read('CONVERSION-FIRST-CREATOR-REVENUE-ACCEPTANCE.md'),
 vtt:read('zen12-42s-concept.vtt'),
 dossier:fs.readFileSync(path.join(__dirname,'INDEPENDENT-AUDIO-BUYER-EVIDENCE-AND-PARTNER-DECISION-UNPUBLISHED.md'),'utf8')
};
const sourceURLs={
 R01:'https://doi.org/10.1371/journal.pone.0286023',
 R02:'https://doi.org/10.1038/s41598-025-88517-z',
 R03:'https://doi.org/10.1016/j.ijpsycho.2024.112328',
 R04:'https://pubmed.ncbi.nlm.nih.gov/40989974/',
 S01:'https://inspire3.com/',S02:'https://zen12.com/hnp',
 S03:'https://brainwaveshots.com/focus-shot',
 S04:'https://hypnosislive.com/mental-skills/total-focus',
 F01:'https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking',
 F02:'https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance',
 V01:'https://finalvestige.com/focus/',
 V02:'https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/',
 V03:'https://finalvestige.com/2026/11/02/change-blindness/',
 V04:'https://finalvestige.com/2026/11/02/mesmerism/',
 G01:'https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171',
 G02:'https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820'
};
const claimStates={
 B01:'SUPPORTED_PERCEPTUAL_PHENOMENON',B02:'REVIEW_BOUNDED',
 B03:'PRIMARY_BOUNDED',B04:'PRIMARY_BOUNDED',B05:'REVIEW_BOUNDED',B06:'TRANSFER_NOT_SUPPORTED',
 S01:'SELLER_DESCRIBED_ONLY',S02:'SELLER_PROMISE_UNVERIFIED_FULFILLMENT',
 S03:'PRODUCT_EFFICACY_UNSUBSTANTIATED',S04:'CHECKOUT_NOT_VERIFIED',
 S05:'SELLER_DESCRIBED_ONLY',S06:'PRODUCT_EFFICACY_UNSUBSTANTIATED',
 S07:'SELLER_DESCRIBED_ONLY',S08:'PRODUCT_EFFICACY_UNSUBSTANTIATED',
 A01:'UNVERIFIED_HARD_HOLD',A02:'UNVERIFIED_HARD_HOLD',A03:'UNVERIFIED_HARD_HOLD',
 A04:'UNVERIFIED_HARD_HOLD',A05:'UNVERIFIED_HARD_HOLD',A06:'UNVERIFIED_HARD_HOLD',
 A07:'FTC_REQUIREMENT',A08:'FTC_REQUIREMENT',A09:'NOT_VERIFIED',A10:'NOT_RENDERED'
};
const gateIDs=[
'named_partner_approval','authorized_website_channel','authorized_social_channel',
'authorized_email_channel','account_issued_link','cookie_and_tracking_terms',
'commission_settlement_terms','merchant_checkout_total','merchant_refund_conditions',
'creative_usage_rights','product_specific_benefit_substantiation',
'founder_release_approval','qa_accessibility_browser','qa_security_and_privacy',
'merchant_sale_reconciliation','owned_product_rights_and_checkout'
];
const clone=x=>({...x,m:JSON.parse(JSON.stringify(x.m))});
function validate(x=baseline){
const errors=[];const ok=(v,msg)=>{if(!v)errors.push(msg);};
const eqIDs=(list,manifest,label)=>{const actual=list.map(o=>o.id);const expected=Array.isArray(manifest)?manifest:Object.keys(manifest);ok(actual.length===expected.length && new Set(actual).size===expected.length && expected.every(k=>actual.includes(k)),label+' exact unique IDs');};
ok(x.m.state==='UNPUBLISHED_HARD_HOLD','unpublished state');
ok(x.m.sprint==='R229','source snapshot identity');
eqIDs(x.m.sources,sourceURLs,'sources');
for(const [id,url] of Object.entries(sourceURLs)){const s=x.m.sources.find(s=>s.id===id);ok(s?.url===url,'source URL '+id);}
eqIDs(x.m.claims,claimStates,'claims');
for(const [id,status] of Object.entries(claimStates)){const c=x.m.claims.find(c=>c.id===id);
ok(c?.status===status,'claim status '+id);
ok(typeof c?.statement==='string'&&c.statement.length>12,'claim statement '+id);
ok(Array.isArray(c?.evidence)&&c.evidence.length>0&&c.evidence.every(e=>sourceURLs[e]),'claim refs '+id);}
eqIDs(x.m.release_gates,gateIDs,'gates');
for(const id of gateIDs){const g=x.m.release_gates.find(g=>g.id===id);ok(g?.status==='HARD_HOLD'&&g?.evidence===null,'gate hold '+id);}
ok(x.m.commerce?.activated===false,'commerce inactive');
ok(x.m.commerce?.affiliate_earning_url===null,'no earning URL');
ok(x.m.commerce?.lead_form_added===false,'no new signup form');
ok(x.m.commerce?.first_party_tracking_script_added===false,'no new tracking');
ok(x.m.commerce?.net_revenue_per_1000_qualified_sessions==='NOT_COMPUTABLE','no invented revenue');
for(const [label,html] of [['A',x.a],['B',x.b],['hub',x.h]]){
ok(/noindex,nofollow/i.test(html),label+' robots off');
ok(!/<script\b|<form\b|<iframe\b|<video\b|<audio\b|\bon[a-z]+\s*=|javascript:/i.test(html),label+' no scripts/forms/players/handlers');
const buttons=[...html.matchAll(/<button\b[^>]*>/gi)].map(z=>z[0]);
ok(buttons.length===1,label+' exactly one button');
ok(buttons.every(z=>/\sdisabled(?:\s|>|=)/i.test(z)),label+' all buttons natively disabled');
const buttonIndex=html.indexOf('<button');
ok(/(?:affiliate disclosure|prospective affiliate disclosure)/i.test(html.slice(Math.max(0,buttonIndex-520),buttonIndex)),label+' proximate disclosure');
for(const anchor of html.matchAll(/<a\b[^>]*>/gi)){
 const h=(anchor[0].match(/\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i)||[]);
 const href=h[1]||h[2]||h[3]||'';
 ok(!/(?:awin1\.com|clickbank\.net|payhip\.com|affiliates\.inspire3\.com|zen12\.com|hypnosislive\.com|brainwaveshots\.com|checkout\.|javascript:)/i.test(href),label+' no merchant or checkout anchor');
}
ok(html.includes('https://finalvestige.com/focus/'),label+' one existing Focus path');
}
ok(x.a.includes('If you eventually purchase through an approved earning link')&&x.b.includes('If you eventually purchase through an approved earning link'),'near-offer FTC text');
ok(!x.a.includes('id="optional-film"')&&x.b.includes('id="optional-film"'),'B only optional film');
ok(x.b.replace(/<!-- Optional original video treatment only:[\s\S]*?<\/section>/,'').replace(' · Video concept',' · Text')===x.a,'A/B identical except optional video');
const cues=[...x.vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.\d{3} --> (\d\d):(\d\d):(\d\d)\.\d{3}/g)];
const seconds=(h,m,s)=>Number(h)*3600+Number(m)*60+Number(s);
ok(cues.length===5,'five caption cues');
let cursor=0;for(const c of cues){const start=seconds(c[1],c[2],c[3]),end=seconds(c[4],c[5],c[6]);ok(start===cursor && end>start,'caption continuity');cursor=end;}ok(cursor===42,'42 sec exactly');
ok(x.art.includes('64 participants in the analyzed sample'),'article attrition');
ok(x.art.includes('p = .385')&&x.art.includes('p = .038'),'article inferential qualification');
ok(x.art.includes('Only one study in that broad review'),'review denominator');
ok(x.art.includes('white-noise masking weakened'),'masking reversal');
ok(x.m.sources.find(s=>s.id==='R02')?.notes.includes('p=.385'),'matrix source denominator');
ok(x.m.claims.find(c=>c.id==='B03')?.statement.includes('64 analyzed'),'claim denominator');
ok(x.m.claims.find(c=>c.id==='B05')?.statement.includes('only one binaural-beat study'),'review source scope');
ok(x.a.includes('sixty-four')&&x.b.includes('sixty-four'),'A/B denominator');
ok(x.a.includes('p = .385')&&x.b.includes('p = .385'),'A/B overall nonsignificance');
ok(x.plan.includes('is not an invisible-gorilla page') && x.plan.includes('DISTINCT phenomenon'),'no false creator match');
ok(x.plan.includes('NOT COMPUTABLE')&&x.plan.includes('lead_confirmed'),'provider and paid revenue');
ok(x.dossier.includes('UNPUBLISHED_RESEARCH_ONLY')&&x.dossier.includes('HARD_HOLD'),'unpublished guide');
ok(x.dossier.includes('not significant (**p=.385**)')&&x.dossier.includes('64 analyzed'),'dossier source precision');
ok(!/https?:\/\/(?:www\.)?awin1\.com\//.test(x.dossier),'no affiliate earning link');
return errors;
}
const errs=validate();if(errs.length){console.error('BASELINE FAIL',errs);process.exit(1);}
const probes=[];
for(const [id] of Object.entries(sourceURLs)){
 probes.push(['delete source '+id,x=>x.m.sources=x.m.sources.filter(s=>s.id!==id)]);
 probes.push(['duplicate source '+id,x=>x.m.sources.push({...x.m.sources.find(s=>s.id===id)})]);
 probes.push(['swap URL '+id,x=>x.m.sources.find(s=>s.id===id).url='https://example.org/changed']);
}
for(const [id] of Object.entries(claimStates)){
 probes.push(['false status '+id,x=>x.m.claims.find(c=>c.id===id).status='VERIFIED']);
 probes.push(['delete claim '+id,x=>x.m.claims=x.m.claims.filter(c=>c.id!==id)]);
}
for(const id of gateIDs){
 probes.push(['false gate '+id,x=>x.m.release_gates.find(g=>g.id===id).status='CLEARED']);
 probes.push(['duplicate gate '+id,x=>x.m.release_gates.push({...x.m.release_gates.find(g=>g.id===id)})]);
}
probes.push(
['LIVE state',x=>x.m.state='LIVE'],
['activated commerce',x=>x.m.commerce.activated=true],
['earning link',x=>x.m.commerce.affiliate_earning_url='https://example.com/track'],
['fake net revenue',x=>x.m.commerce.net_revenue_per_1000_qualified_sessions=43],
['enable A',x=>x.a=x.a.replace(' disabled aria',' aria')],
['enable B',x=>x.b=x.b.replace(' disabled aria',' aria')],
['enable hub',x=>x.h=x.h.replace('<button disabled','<button')],
['unquoted merchant href',x=>x.a+='<a href=https://zen12.com/hnp>buy</a>'],
['single quoted earning href',x=>x.b+="<a href='https://awin1.com/fake'>buy</a>"],
['second enabled control',x=>x.h+='<button>Buy now</button>'],
['remove near affiliate disclose',x=>x.a=x.a.replace('Affiliate disclosure: If you eventually purchase through an approved earning link on this guide, Final Vestige Studios may earn a commission at no additional cost to you. No earning link is active here.','No earning link is active.')],
['form injection',x=>x.a+='<form><input type=email></form>'],
['script injection',x=>x.h+='<script src=/analytics.js></script>'],
['inline handler',x=>x.b+='<p onclick="buy()">click</p>'],
['turn B into another offer',x=>x.b=x.b.replace('Buyer checklist','Claimed miracle')],
['delete VTT',x=>x.vtt='WEBVTT'],
['remove article 64',x=>x.art=x.art.replace('64 participants in the analyzed sample','80 participants in the analyzed sample')],
['remove p=.385',x=>x.art=x.art.replace('p = .385','p = .01')],
['remove Chee scope',x=>x.art=x.art.replace('Only one study in that broad review','Thirty-one studies in that review')],
['false creator topic',x=>x.plan=x.plan.replaceAll('DISTINCT phenomenon','SAME phenomenon')],
['erase dossier gate',x=>x.dossier=x.dossier.replace('UNPUBLISHED_RESEARCH_ONLY','LIVE')],
['fake A/B randomized winner',x=>x.plan=x.plan.replaceAll('NOT COMPUTABLE','WINNER')]);
let rejected=0;for(const [label,mutate] of probes){const x=clone(baseline);mutate(x);const v=validate(x);if(!v.length){console.error('UNSAFE MUTATION ACCEPTED',label);process.exit(1);}rejected++;}
console.log('PASS R230 source-level: baseline 0 violations; '+rejected+'/'+probes.length+' unsafe mutations rejected; no production or commercial execution.');
