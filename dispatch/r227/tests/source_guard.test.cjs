// Node.js source-review contract. Safe to execute offline: node --test dispatch/r227/tests/source_guard.test.cjs
// This never sends, publishes, updates analytics, or contacts anyone.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root=path.resolve(__dirname,'..');
const parent=path.resolve(root,'..','campaign-2026-mind');
const read=p=>fs.readFileSync(p,'utf8');
const r=f=>read(path.join(root,f));
const blob=s=>{const b=Buffer.from(s,'utf8');return crypto.createHash('sha1').update(Buffer.from('blob '+b.length+'\\0')).update(b).digest('hex')};
const lock=JSON.parse(r('SOURCE_LOCK.json'));
const c05=r('alternates/05-before-you-press-play-subscriber-safe.md'), c06=r('alternates/06-evidence-log-direct-pdf.md');
const originals=[
 ['05', 'issues/05-before-you-press-play.md'],
 ['06', 'issues/06-the-evidence-log.md']
];
test('source identities unchanged from audited R226',()=>{for(const [n,p] of originals){assert.equal(blob(read(path.join(parent,p))),lock.source_blobs[n]);}});
test('no schedule or list activation in parent manifest',()=>{const m=JSON.parse(read(path.join(parent,'manifest.json')));assert.equal(m.status,'DRAFT_UNSENT_NO_SCHEDULING');assert.equal(m.issues.filter(i=>i.kind==='editorial').length,4);assert.equal(m.issues.filter(i=>i.kind==='commercial-review-pending').length,2);assert.ok(m.issues.every(i=>i.merchant_affiliate_url===null));});
test('candidate 05 is exactly surgical source delta',()=>{const x=read(path.join(parent,originals[0][1]));assert.equal(c05,x.replace("You can use our [Seven Day Focus Fieldbook](https://finalvestige.com/focus/) without buying anything.","The free Seven Day Focus Fieldbook is another way to observe your routine without buying anything; you do not need to subscribe again or buy an audio product to try the exercise above."));});
test('candidate 06 is exactly surgical source delta',()=>{const x=read(path.join(parent,originals[1][1]));assert.equal(c06,x.replace("**Open the free Fieldbook:** [Seven Day Focus Fieldbook](https://finalvestige.com/focus/).","**Open the free Fieldbook:** [Seven Day Focus Fieldbook — Complete Edition (PDF)](https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf).\n\nIf you're already reading The Dispatch, there's no reason to enter your email again just to open the book. This is the direct PDF named in the configured welcome message; if an in-app browser does not open it, use your regular browser."));});
test('05 retains commercial disclosure and is not a second Focus signup CTA',()=>{assert.ok(c05.includes('**Commercial disclosure:**'));assert.ok(c05.includes('[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]'));assert.equal(c05.includes('https://finalvestige.com/focus/'),false);assert.equal(c05.includes('https://www.awin1.com'),false);});
test('06 one primary free resource CTA direct not signup',()=>{assert.equal(c06.includes('https://finalvestige.com/focus/'),false);assert.equal(c06.split("https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf").length-1,1);assert.ok(c06.includes('no reason to enter your email again'));});
test('both candidates hard-block legal footer and remain unsent',()=>{for(const t of [c05,c06]){assert.ok(t.includes('UNSENT DRAFT'));assert.ok(t.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]'));assert.ok(t.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]'));assert.ok(!/https?:\/\/(?:affiliates?\.|clickbank|www\.awin1)/i.test(t));}});
test('two previews safe and consistent with manuscript heading',()=>{for(const [f,c] of [['previews/05-review-only.html',c05],['previews/06-review-only.html',c06]]){const h=r(f);assert.ok(h.includes('REVIEW ONLY'));assert.ok(h.includes('<h1 '));assert.ok(h.includes('role="presentation"'));assert.ok(!/<(script|form|img|iframe)\b/i.test(h));assert.ok(h.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]'));assert.ok(h.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]'));}});
test('plaintext companions explain they cannot be sent',()=>{for(const f of ['previews/05-review-only.txt','previews/06-review-only.txt']){const x=r(f);assert.ok(x.includes('OFFLINE REVIEW ONLY'));assert.ok(x.includes('PRE-SEND LEGAL BLOCK'));}});
test('missing permissions and revenue remain absent',()=>{assert.equal(lock.send_authorized,false);assert.equal(lock.publication_authorized,false);assert.equal(lock.actual_eligible_recipient_count,null);assert.equal(lock.net_revenue_per_1000_qualified_human_sessions,null);assert.equal(lock.planned_editions[0].email_rights,'NOT_VERIFIED');});
