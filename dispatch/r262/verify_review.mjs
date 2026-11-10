// R262 self-contained, read-only preflight. Run: node dispatch/r262/verify_review.mjs
import fs from 'node:fs';
import path from 'node:path';
const root = new URL('.', import.meta.url);
const read=n=>fs.readFileSync(new URL(n,root),'utf8');
let checked=0;
function insist(condition,label){ checked++; if(!condition)throw Error('BLOCKING QA FAILURE: '+label); }
const lock=JSON.parse(read('RELEASE_LOCK.json'));
insist(lock.all_six_send_state==='HOLD_UNSENT','all six hold');
insist(lock.commercial_03_05==='HOLD_MERCHANT','commercial hold');
insist(Object.values(lock.attestations).every(v=>v===false),'no invented attestations');
for(const id of ['01','06']){
  const md=read('ISSUE'+id+'_OPTIONAL.md'),txt=read('ISSUE'+id+'_PLAINTEXT.txt'),html=read('ISSUE'+id+'_EMAIL_REVIEW.html');
  const subject=id==='01'?'The person changed. The witness kept talking.':'Seven days of notes. What can they actually prove?';
  const cta=id==='01'?'Read the change-blindness investigation':'Use the free Seven Day Focus Fieldbook';
  const url=id==='01'?'https://finalvestige.com/2026/11/02/change-blindness/':'https://finalvestige.com/focus/';
  insist(md.includes(subject)&&txt.includes(subject)&&html.includes(subject),'subject consistency '+id);
  insist(md.includes(cta)&&txt.includes(cta)&&html.includes(cta),'primary CTA consistency '+id);
  insist((html.match(/<a href=/g)||[]).length===1,'one primary CTA button '+id);
  insist(html.includes('role="presentation"')&&html.includes('lang="en"'),'email semantics '+id);
  insist(html.includes('UNSENT STATIC REVIEW')&&txt.includes('NOT APPROVED'),'hold banners '+id);
  insist([md,txt,html].every(s=>s.includes('[[VALID_FV_POSTAL_ADDRESS_NOT_ATTESTED]]')),'legal postal unresolved '+id);
  insist([md,txt,html].every(s=>s.includes('[[REAL_JETPACK_RENDERED_OPT_OUT_NOT_VERIFIED]]')),'opt-out unresolved '+id);
  insist([md,txt,html].every(s=>s.includes(url)),'verified internal CTA '+id);
  insist(!/affiliates\.inspire3\.com\/?\S*\?/.test(html),'no affiliate activation '+id);
  insist(md.includes('https://doi.org/')||md.includes('https://www.nccih.nih.gov/'),'sources '+id);
}
insist(read('SOURCE_AND_REVENUE_QA.md').includes('NOT COMPUTABLE'),'honest KPI');
console.log('R262 review offline checks PASSED: '+checked+'/'+checked+'; no email/client/production check performed.');
