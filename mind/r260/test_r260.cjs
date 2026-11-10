'use strict';
// Mind R260 source-only regression: native Node `node mind/r260/test_r260.cjs`.
// No external network, paid services, merchant activation, WP or file writes.
const REQUIRED=[
 'mind/r260/THE-MOMENT-YOU-NOTICE-YOU-WERE-GONE-UNPUBLISHED.md',
 'mind/r260/INDEPENDENT-SCIENCE-PRODUCT-COMMERCIAL-GATES.json',
 'mind/r260/CONVERSION-FIRST-CANONICAL-RELEASE-AND-NAVIGATION.md'
];
const EXPECTED_GATES=['publisher_named_acceptance','issued_affiliate_url','specific_zen12_product_and_destination','website_channel_permission','social_channel_permission','email_channel_permission','approved_creative_usage_rights','exact_checkout_price_and_currency','merchant_tax_shipping_or_extra_charges','product_inclusion_equivalence_promo_vs_standard','refund_terms_specific_offer','merchant_refund_actual_process','buyer_facing_compliant_disclosure','first_party_event_definition_owner_signoff','merchant_confirmed_paid_commission_feed','founder_editorial_QA_release_approval'];
const RELEASE=['wordpress_published','newsletter_sent','merchant_link_enabled','analytics_script_added','merge_or_deploy','paid_service'];
const HELD=['C04','C05','C07','C08','C09','C10','C12','C13','C15','C18','C28','C29','C30'];
function validate(files){
 const e=[];
 if(REQUIRED.some(p=>typeof files[p]!=='string'||files[p].length<800))return ['missing required source'];
 const article=files[REQUIRED[0]], plan=files[REQUIRED[2]];
 let m;try{m=JSON.parse(files[REQUIRED[1]])}catch(err){return ['invalid evidence JSON']}
 if(article.split(/\s+/).length<2300)e.push('insufficient research depth');
 for(const s of ['10.1126/science.1192439','26993740','21684189','23538911','33582570','10.1002/acp.70056','PMC10198548','Puységur','Seven Day Focus Fieldbook','UNPUBLISHED','not a clinical trial'])
  if(!article.includes(s))e.push('missing article grounding: '+s);
 if(/we (personally |independently )?(used|tested|purchased) Zen12/i.test(article))e.push('fabricated product experience');
 if(/\]\(https?:\/\/(?:www\.)?(?:awin1\.com|clickbank\.net)/i.test(article))e.push('affiliate link injection');
 if(article.includes('Zen12 is scientifically proven to provide an hour'))e.push('unsupported product endorsement');
 if(m.partner_verified!==false||m.affiliate_link_authorized!==false||m.live_experiment!==false)e.push('unverified commercial activation');
 if(!Array.isArray(m.sources)||m.sources.length!==25||!Array.isArray(m.claims)||m.claims.length!==30)e.push('source/claim counts');
 const sources=new Set((m.sources||[]).map(x=>x.id)),claims=new Set((m.claims||[]).map(x=>x.id));
 if(sources.size!==25||claims.size!==30||m.claims.some(c=>(c.source_ids||[]).some(id=>!sources.has(id))))e.push('source integrity');
 for(const id of HELD)if(m.claims.find(c=>c.id===id)?.eligible_for_copy!==false)e.push('promotional hold '+id);
 if(m.claims.find(c=>c.id==='C01')?.text!=='Participants detected some choice-outcome swaps in a 2005 attractiveness choice task while others passed unnoticed')e.push('research actor confused');
 const ids=(m.commercial_gates||[]).map(g=>g.id);
 if(ids.length!==16||new Set(ids).size!==16||EXPECTED_GATES.some(id=>!ids.includes(id))||m.commercial_gates.some(g=>g.status!=='HARD_HOLD'||g.verified_at!==null))e.push('commercial gate identity/status');
 if(!m.release_boundary||Object.keys(m.release_boundary).length!==RELEASE.length||RELEASE.some(id=>m.release_boundary[id]!==false))e.push('release boundary');
 if(m.attribution_contract?.zero_denominator!=='NOT_COMPUTABLE'||m.owned_product_fallback?.status!=='UNKNOWN_NOT_AUTHENTICATED')e.push('fictitious revenue or SKU');
 if(!Array.isArray(m.social_join_paths)||m.social_join_paths.length!==3||m.social_join_paths.some(p=>p.grok_asset_id!=='NOT_VERIFIED'))e.push('invented Grok IDs');
 for(const s of ['PR #172','R257','TASK-008','7/30','affiliate_outbound_click','merchant_confirmed_paid_commission','360, 390, 768, 1440, 1920','no live WordPress','HARD HOLD','NOT COMPUTABLE'])
   if(!plan.includes(s))e.push('plan acceptance missing:'+s);
 if(/(commissions? (have|were) paid|A\/B (is )?live|we are approved by Inspire3)/i.test(plan))e.push('implied commercial success');
 return e;
}
function mutations(){
 const [A,M,P]=REQUIRED;
 return [
 ['missing main paper',A,s=>s.replaceAll('10.1126/science.1192439','omitted')],
 ['missing intentional study',A,s=>s.replaceAll('26993740','omitted')],
 ['missing meta review',A,s=>s.replaceAll('33582570','omitted')],
 ['invented product trial',A,s=>s+'\nWe independently tested Zen12 and it is amazing.'],
 ['unsupported endorsement',A,s=>s+'\nZen12 is scientifically proven to provide an hour.'],
 ['malicious affiliate destination',A,s=>s+'\n[Buy](https://awin1.com/click)'],
 ['fake partner',M,s=>{let m=JSON.parse(s);m.partner_verified=true;return JSON.stringify(m)}],
 ['fake link authorization',M,s=>{let m=JSON.parse(s);m.affiliate_link_authorized=true;return JSON.stringify(m)}],
 ['fake live test',M,s=>{let m=JSON.parse(s);m.live_experiment=true;return JSON.stringify(m)}],
 ...HELD.map(id=>['held claim '+id,M,s=>{let m=JSON.parse(s);m.claims.find(x=>x.id===id).eligible_for_copy=true;return JSON.stringify(m)}]),
 ...RELEASE.map(id=>['release boundary '+id,M,s=>{let m=JSON.parse(s);m.release_boundary[id]=true;return JSON.stringify(m)}]),
 ['fake gate',M,s=>{let m=JSON.parse(s);m.commercial_gates[1].id='manufactured_gate';return JSON.stringify(m)}],
 ['duplicate gate',M,s=>{let m=JSON.parse(s);m.commercial_gates[1].id=m.commercial_gates[0].id;return JSON.stringify(m)}],
 ['fake revenue',M,s=>{let m=JSON.parse(s);m.attribution_contract.zero_denominator='0';return JSON.stringify(m)}],
 ['fake Grok asset',M,s=>{let m=JSON.parse(s);m.social_join_paths[0].grok_asset_id='12345';return JSON.stringify(m)}],
 ['remove social join',M,s=>{let m=JSON.parse(s);m.social_join_paths.pop();return JSON.stringify(m)}],
 ['remove 7/30',P,s=>s.replaceAll('7/30','1')],
 ['remove canonical hub',P,s=>s.replaceAll('PR #172','PR #999')],
 ['fabricated revenue',P,s=>s+'\nA/B is live and commissions have paid.']
 ];
}
function test(files){
 const initial=validate(files);if(initial.length)throw Error('R260 baseline: '+initial.join('; '));
 const labels=new Set();let n=0;
 for(const [name,path,fn]of mutations()){
  if(labels.has(name))throw Error('duplicate mutation: '+name);
  labels.add(name);
  const changed=fn(files[path]);if(changed===files[path])throw Error('ineffective mutation: '+name);
  const errs=validate({...files,[path]:changed});
  if(!errs.length)throw Error('undetected mutation: '+name);
  n++;
 }
 return {status:'PASS',baseline:'PASS',rejected:n,total:mutations().length,distinct:labels.size,required:REQUIRED.length};
}
module.exports={REQUIRED,validate,test};
if(require.main===module){const fs=require('node:fs'),path=require('node:path');const root=path.resolve(__dirname,'../..');const files=Object.fromEntries(REQUIRED.map(p=>[p,fs.readFileSync(path.join(root,p),'utf8')]));process.stdout.write(JSON.stringify(test(files),null,2)+'\n')}
