// Offline contract for the isolated R426 correction candidates. Never sends mail.
const fs=require('node:fs'),assert=require('node:assert/strict'),path=require('node:path');
const dir=__dirname;
let tested=0;
for(const id of ['04','06']){
 const md=fs.readFileSync(path.join(dir,'issue_'+id+'_editorial_candidate.md'),'utf8');
 const html=fs.readFileSync(path.join(dir,'preview_issue_'+id+'.html'),'utf8');
 const txt=fs.readFileSync(path.join(dir,'preview_issue_'+id+'.txt'),'utf8');
 const m=md.match(/^Subject: (.+)$/m),p=md.match(/^Preheader: (.+)$/m);
 for(const s of [md,html,txt]){assert(s.includes('HOLD')||s.includes('REVIEW ONLY'));tested++;}
 assert(html.includes('<html lang="en">')&&html.includes('role="presentation"')&&!/<script|<form|<img|<iframe|onload=|onclick=/i.test(html));tested++;
 assert(m&&p&&m[1].length<=65&&p[1].length<=115);tested++;
 assert(html.includes(m[1])&&html.includes(p[1])&&txt.includes(m[1])&&txt.includes(p[1]));tested++;
 const hrefs=[...html.matchAll(/href="([^"]+)"/g)].map(m=>m[1]);assert(hrefs.length>1);tested++;
 assert(hrefs.every(u=>u.startsWith('https://')&&!/affiliate|track|clickbank|utm_|ref=/i.test(u)));tested++;
 assert(hrefs.filter(u=>u.includes('finalvestige.com')).length>=1);tested++;
 for(const s of [md,html,txt]){assert(s.includes('[[FV_VERIFIED_BUSINESS_POSTAL_ADDRESS_REQUIRED]]')&&s.includes('[[JETPACK_ACTUAL_UNSUBSCRIBE_RENDERING_AND_FUNCTION_REQUIRED]]'));tested++}
 assert(!/12 minutes = 1 hour|guaranteed results|100% concentration/i.test(md+txt+html));tested++;
 if(id==='04'){assert(md.includes('approximately fifteen seconds')&&md.includes('not a measurement of how long the fire')&&md.includes('not conclusively'));tested++;}
 if(id==='06'){assert(md.includes('do not need to subscribe again')&&txt.includes('wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf'));tested++;}
}
const s=JSON.parse(fs.readFileSync(path.join(dir,'REDACTED_SOURCE_SNAPSHOT.json'),'utf8'));
assert(s.total===3&&s.confirmed===3&&s.unconfirmed===2&&s.recipient_identity_count==='NOT_VERIFIED');tested++;
assert(s.email_merchant_permission==='NOT_VERIFIED'&&s.actual_jetpack_preview==='NOT_VERIFIED'&&!s.candidate_04_06_approved);tested++;
assert(s.realized_revenue_per_1000_qualified_sessions==='NOT_COMPUTABLE');tested++;
console.log('R426 offline contract PASS: '+tested+' assertions (NOT native Jetpack/inbox verification).');
