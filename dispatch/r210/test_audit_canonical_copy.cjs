'use strict';
// Exact canonical files are loaded from the checked out original campaign, with no network/list/sending.
const assert=require('node:assert/strict'), fs=require('node:fs'), path=require('node:path');
const audit=require('./audit_canonical_copy.cjs').auditCanonical;
const root=path.join(__dirname,'../campaign-2026-mind');
const m=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
const docs={};for(const e of m.issues){docs[e.number]=fs.readFileSync(path.join(root,'issues',String(e.number).padStart(2,'0')+'-'+e.slug+'.md'),'utf8');}
const r=audit(m,docs);
const expected=[['DUPLICATE_DESTINATION_WITH_ISSUE_02',1],['DUPLICATE_DESTINATION_WITH_ISSUE_01',2],['SECONDARY_ACTIVE_LINK_COMPETES_WITH_HELD_GUIDE',3],['APOLLO_14_SECONDS_NO_EXPLANATION_IN_EMAIL',4],['TOTAL_FOCUS_OFFER_NOT_NAMED',5],['EXISTING_SUBSCRIBERS_REENTER_SIGNUP',6]];
let passed=0;const t=(n,f)=>{f();console.log('PASS '+n);passed++;};
t('six campaign issues',()=>assert.equal(r.issues.length,6));
t('4 editorials / 2 potential merchant issues',()=>{assert.equal(r.editorial,4);assert.equal(r.prospective_commercial,2);});
t('all email remains held',()=>{assert.equal(r.status,'HOLD_UNSENT');assert.equal(r.send_authorized,false);});
for(const [flag,n] of expected)t('canonical issue '+n+' flags '+flag,()=>assert.ok(r.issues[n-1].findings.includes(flag)));
t('two merchant guides remain held',()=>{assert.ok(r.issues[2].findings.includes('MERCHANT_EMAIL_RIGHTS_GUIDE_AND_LINK_UNVERIFIED'));assert.ok(r.issues[4].findings.includes('MERCHANT_EMAIL_RIGHTS_GUIDE_AND_LINK_UNVERIFIED'));});
t('six legal placeholders intact',()=>assert.ok(r.issues.every(x=>!x.findings.includes('LEGAL_PLACEHOLDER_OR_PROOF_MISSING'))));
t('reject tampered subject',()=>assert.throws(()=>audit(m,{...docs,1:docs[1].replace('The mind is not a camera','Miracle cure')}),/subject/));
t('reject malformed allocation',()=>{const altered=structuredClone(m);altered.issues[2].kind='editorial';assert.throws(()=>audit(altered,docs),/allocation/);});
t('reject missing canonical issue',()=>assert.throws(()=>audit(m,{...docs,6:''}),/manuscript/));
t('detect missing postal hold',()=>assert.ok(audit(m,{...docs,4:docs[4].replace('[[VALID_POSTAL_ADDRESS_REQUIRED]]','')}).issues[3].findings.includes('LEGAL_PLACEHOLDER_OR_PROOF_MISSING')));
t('detect missing commercial disclosure',()=>assert.ok(audit(m,{...docs,3:docs[3].replace('Commercial disclosure:','Removed:')}).issues[2].findings.includes('MERCHANT_PLACEHOLDER_OR_DISLCOSURE_MISSING')));
console.log('TOTAL '+passed+' PASSED (native Node when run, but no send authorization)');