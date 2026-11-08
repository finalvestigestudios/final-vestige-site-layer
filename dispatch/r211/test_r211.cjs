// Development-only source integrity guard. It CANNOT send email or approve releases.
const fs=require('node:fs'), assert=require('node:assert/strict'), path=require('node:path');
const root=path.join(__dirname); const m=JSON.parse(fs.readFileSync(path.join(root,'release_manifest.json'),'utf8'));
assert.equal(m.status,'UNSENT_REVIEW_ALTERNATIVES_ONLY');
assert.deepEqual(m.allocation.editorial,[1,2,4,6]);assert.deepEqual(m.allocation.commercial_pending,[3,5]);
assert.equal(m.emails.length,6); assert.equal(new Set(m.emails.map(e=>e.issue)).size,6);
assert.ok(Object.values(m.release).every(x=>x===false));
let checks=4;
for(const e of m.emails){
  const src=fs.readFileSync(path.join(root,'revisions',e.slug+'.md'),'utf8');
  const html=fs.readFileSync(path.join(root,'preview',e.slug+'.html'),'utf8');
  assert.ok(src.includes('UNSENT REVIEW ALTERNATIVE')); checks++;
  assert.ok(src.includes('**Subject:** '+e.subject)&&src.includes('**Preheader:** '+e.preheader)); checks++;
  assert.equal((src.match(/\\*\\*ONE CTA/g)||[]).length,1); checks++;
  assert.ok(src.includes('VALID_FINAL_VESTIGE_POSTAL_ADDRESS_REQUIRED')&&src.includes('JETPACK_UNSUBSCRIBE_MUST_BE_VERIFIED')); checks++;
  assert.ok(html.includes('role="presentation"')&&html.includes('lang="en"')&&html.includes('max-width:600px')&&html.includes('overflow-wrap:anywhere'));checks++;
  assert.ok(!/<script|<img|tracking|pixel.gif/i.test(html));checks++;
  assert.ok(e.approved===false&&e.send_authorized===false);checks++;
  if(e.kind==='commercial-review-pending'){
    assert.ok(e.proposed_destination.startsWith('[[')&&src.includes('Commercial disclosure immediately beside'));checks++;
    assert.ok(html.includes('INACTIVE / NOT APPROVED')&&!html.includes('href="[['));checks++;
    assert.ok(src.includes('HOLD:')&&src.includes('EMAIL'));checks++;
  }else{
    assert.ok(e.proposed_destination.startsWith('https://finalvestige.com/'));checks++;
  }
}
const s1=fs.readFileSync(path.join(root,'revisions','01-when-the-person-changed.md'),'utf8');
const s4=fs.readFileSync(path.join(root,'revisions','04-apollo-one-why-the-record-matters.md'),'utf8');
const s5=fs.readFileSync(path.join(root,'revisions','05-total-focus-what-is-in-the-recording.md'),'utf8');
const s6=fs.readFileSync(path.join(root,'revisions','06-the-notebook-is-not-the-verdict.md'),'utf8');
assert.ok(s1.includes('BF03208840')&&s1.includes('/2026/11/02/change-blindness/'));checks++;
assert.ok(s4.includes('approximately fourteen')&&s4.includes('roughly fifteen')&&s4.includes('different reference points'));checks++;
assert.ok(s5.includes('five sessions per year')&&s5.includes('33-minute')&&s5.includes('47-MB'));checks++;
assert.ok(!s6.includes('**ONE CTA:** Open the free Fieldbook — https://finalvestige.com/focus/'));checks++;
console.log('R211 offline source checks passed:',checks,'(no recipient, render, or merchant verification)');
