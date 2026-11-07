'use strict';
const assert=require('node:assert/strict'), fs=require('node:fs'), path=require('node:path'), test=require('node:test');
const read=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
const md=read('04_OPTIONAL_SPIRIT_PHOTOGRAPH.md'), txt=read('04_PLAINTEXT.txt'), html=read('04_EMAIL_SAFE_REVIEW.html'), gb=read('04_GUTENBERG_DRAFT.txt'), doc=read('SOURCE_PERMISSION_AND_NATIVE_PREVIEW.md');
const j=JSON.parse(read('SIX_ISSUE_PORT_MANIFEST.json'));const all=[md,txt,html,gb];
const checks=[
['subject aligned',()=>assert.ok(all.every(x=>x.includes('The ghost who was still alive')))],
['one first-party CTA',()=>assert.ok(all.every(x=>x.includes('https://finalvestige.com/2026/11/02/mesmerism/')))],
['met museum source',()=>assert.ok(all.every(x=>x.includes('metmuseum.org/art/collection/search/296300')))],
['white house source',()=>assert.ok(all.every(x=>x.includes('whitehousehistory.org/photos/')))],
['smithsonian source',()=>assert.ok(all.every(x=>x.includes('smithsonianmag.com/')))],
['preheader consistent',()=>assert.ok([md,txt,html].every(x=>x.includes('In a nineteenth-century')))],
['postal hard stop',()=>assert.ok(all.every(x=>x.includes('VALID_FINAL_VESTIGE_PUBLISHER_POSTAL_ADDRESS_REQUIRED')))],
['unsubscribe hard stop',()=>assert.ok(all.every(x=>x.includes('ACTUAL_JETPACK_RENDERED_UNSUBSCRIBE_TO_VERIFY')))],
['no earning URLs',()=>assert.ok(all.every(x=>!/(awin1\.com|clickbank\.net|aff_id=|hop=)/i.test(x)))],
['HTML language',()=>assert.match(html,/<html lang="en">/)],
['HTML presentation tables',()=>assert.match(html,/role="presentation"/)],
['HTML no dynamic elements',()=>assert.doesNotMatch(html,/<(script|form|iframe|input)\b/i)],
['Gutenberg block tokens',()=>assert.match(gb,/<!-- wp:paragraph -->/)],
['four editorial two commercial',()=>assert.deepEqual(j.issues.map(x=>x.kind),['editorial','editorial','commercial_reserved','editorial','commercial_reserved','editorial'])],
['no campaign approval',()=>assert.equal(j.pilot.approved_to_send,false)],
['all release held',()=>assert.ok(j.issues.every(x=>x.state.startsWith('HOLD')))],
['merchant rights not invented',()=>assert.ok(j.issues.filter(x=>x.kind==='commercial_reserved').every(x=>x.merchant_email_permission===false&&x.earning_url===false))],
['no fake email-eligible denominator',()=>assert.equal(j.wp.email_eligible_count,null)],
['no fake net revenue',()=>assert.equal(j.conversion.realized_net_per_1000,null)],
['welcome receipt not inferred',()=>assert.equal(j.wp.welcome_received_verified,false)],
['preview not inferred',()=>assert.equal(j.native_jetpack_preview_obtained,false)],
['address not inferred',()=>assert.equal(j.valid_publisher_postal_verified,false)],
['unsubscribe not inferred',()=>assert.equal(j.received_unsubscribe_verified,false)],
['original master SHA',()=>assert.equal(j.sources.master_sha,'d57ccdba3aee8f065e143e101c2945f4f3d01647')],
['legal and merchant sources',()=>assert.ok(doc.includes('ftc.gov/business-guidance')&&doc.includes('zen12.com/hnp')&&doc.includes('hypnosislive.com/mental-skills/total-focus'))],
['no guaranteed cures',()=>assert.doesNotMatch(md,/(guaranteed|cure|proven meditation product)/i)]
];for(const [name,check] of checks)test(name,check);
