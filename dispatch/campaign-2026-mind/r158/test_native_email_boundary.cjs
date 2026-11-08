'use strict';
const test=require('node:test'), assert=require('node:assert/strict');
const v=require('./native_email_boundary.cjs');
const base={number:3,subject:'An honest question',preheader:'Specific and true.',kind:'commercial-review-pending',editorial_cta:'[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]',merchant_affiliate_url:null};
function letter(e=base){return `# THE DISPATCH\n> UNSENT DRAFT DO NOT PUBLISH\n**Subject:** ${e.subject}\n**Preheader:** ${e.preheader}\n**Content type:** ${e.kind}\nThis is a substantive, source-led question about a recording and evidence, not a claim of effectiveness. A comparison needs an actual control, and a claim needs a source. This paragraph makes the fixture sufficiently lengthy to mimic our editorial material.\n**Commercial disclosure:** If a buyer uses a qualifying guide link we may earn a commission.\n${e.editorial_cta}\n[[VALID_POSTAL_ADDRESS_REQUIRED]] [[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]`}
const exampleStatus={subscribers:{total:3,confirmed:3,unconfirmed:2,suppressed:0,paid:0}};
for(const [name,mutation] of [
 ['original fixture',s=>s],['no address',s=>s.replace(v.HARD_STOPS[0],'')],['no unsubscribe',s=>s.replace(v.HARD_STOPS[1],'')],
 ['missing subject',s=>s.replace('**Subject:**','**Label:**')],['missing preheader',s=>s.replace('**Preheader:**','**Preview:**')],
 ['no disclosure',s=>s.replace('**Commercial disclosure:**','**Sales:**')],
 ['merchant host',s=>s+' https://zen12.com/?sid=x'],['PII query',s=>s+' https://finalvestige.com/focus/?email=secret'],
 ['no hold banner',s=>s.replace('UNSENT DRAFT DO NOT PUBLISH','MANUSCRIPT')]
]) test('draft mutation '+name,()=>{const r=v.reviewDraft(3,mutation(letter()),base);assert.equal(r.status,'HOLD_UNSENT');assert.equal(r.metadata_valid,name==='original fixture');assert.equal(r.send_allowed,false);});
test('legitimate offline aggregate remains unknown',()=>{const a=v.readOnlyAudience(exampleStatus,{wpcom:3,email:0});assert.equal(a.eligible_recipients,null);assert.equal(a.reported_total,3);assert.equal(a.reported_unconfirmed,2);assert.equal(a.provider_confirmed_signup_events,null);});
test('bad provider data fail closed',()=>assert.equal(v.readOnlyAudience({subscribers:{...exampleStatus.subscribers,confirmed:'3'}},{}).status,'INVALID_PROVIDER_AGGREGATES'));
test('editorial URL acceptance',()=>{assert.equal(v.firstPartyHref('https://finalvestige.com/focus/'),true);assert.equal(v.firstPartyHref('https://evil.com/focus/'),false);assert.equal(v.firstPartyHref('http://finalvestige.com/focus/'),false);assert.equal(v.firstPartyHref('https://finalvestige.com@evil.com/focus/'),false);});
test('active merchant url forbidden even in a valid draft',()=>{assert.equal(v.reviewDraft(3,letter(),{...base,merchant_affiliate_url:'https://anywhere.example/x'}).metadata_valid,false)});
test('wrong edition identity fails',()=>{assert.equal(v.reviewDraft(5,letter(),base).metadata_valid,false)});
test('safely detects 6 uniquely numbered campaign records',()=>{
 const editions=[1,2,3,4,5,6].map(n=>({...base,number:n}));const a=v.nativeJetpackChecklist({status:'DRAFT_UNSENT_NO_SCHEDULING',issues:editions},{settings:{subscriptions:true,email_new_posts_by_default:false,email_content_format:'full',from_name:'Final Vestige Studios',welcome_message:'Fieldbook'}});
 assert.equal(a.status,'REHEARSAL_NOT_A_EMAIL_PREVIEW');assert.equal(a.editions.length,6);assert.equal(a.founder_send_approval,false);assert.equal(a.live_jetpack_preview_verified,false);assert.equal(a.editions[0].preheader_delivery,'UNVERIFIED');
});
test('rejects duplicate editions',()=>assert.throws(()=>v.nativeJetpackChecklist({status:'DRAFT_UNSENT_NO_SCHEDULING',issues:[1,2,3,4,5,5].map(number=>({number}))},{settings:{}}),/Six unique/));
test('rejects non-draft manifest',()=>assert.throws(()=>v.nativeJetpackChecklist({status:'PUBLISHED',issues:[1,2,3,4,5,6].map(number=>({number}))},{settings:{}})));
test('URL parser rejects userinfo and bad protocol',()=>{for(const u of ['https://someone@finalvestige.com/focus/','javascript:alert(1)','ftp://finalvestige.com','not-a-url'])assert.equal(v.firstPartyHref(u),false)});
test('no commercial promo link without partner permission',()=>assert.equal(v.urlSafety('Read at https://hypnosislive.com/mental-skills/total-focus'),false));
