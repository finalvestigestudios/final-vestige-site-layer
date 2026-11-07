'use strict';
const {inspect,kpi}=require('./release_gate.cjs'),fs=require('fs'),p=require('path'); let count=0;
function ok(b,m){if(!b)throw Error(m);count++}
const e=JSON.parse(fs.readFileSync(p.join(__dirname,'READONLY_SNAPSHOT.json'),'utf8'));
const arr=['04_MARS_OPTIONAL_UNSENT.md','04_MARS_OPTIONAL_UNSENT.txt','04_MARS_OPTIONAL_UNSENT.html'].map(n=>fs.readFileSync(p.join(__dirname,n),'utf8'));
ok(!inspect(e).release_allowed,'fail closed');ok(inspect(e).holds.length>=6,'multiple blockers');
ok(e.newsletter.counted_subscribers===3,'three counted');ok(e.newsletter.unconfirmed_requests===2,'two unconfirmed, nonadditive');ok(e.newsletter.authoritative_unique_email_eligible===null,'eligible unknown');ok(e.newsletter.email_only_followers===0,'followers separate');
ok(e.newsletter.welcome_received_verified===false,'welcome not evidenced');ok(e.founder_send_approval===false,'no send approval');ok(e.allocation.filter(x=>x==='editorial').length===4,'4 editorial');ok(e.allocation.filter(x=>x==='commercial').length===2,'2 commercial');
ok(kpi({reconciled:false,sessions:100,net:0})===null,'no fake zero');ok(kpi({reconciled:true,sessions:100,net:12})===120,'hypothetical only');ok(kpi({reconciled:true,sessions:0,net:12})===null,'zero denominator');
for(const s of arr){ok(s.includes('The canals that weren’t on Mars'),'same subject');ok(s.includes('An mapped')===false,'subject grammar');ok(s.includes('https://science.nasa.gov/mars/triumph-of-mariner-4/'),'NASA source');ok(s.includes('https://finalvestige.com/2026/11/02/change-blindness/'),'CTA route');ok(s.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]'),'postal hold');ok(s.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]'),'optout hold');}
ok(arr[2].includes('lang="en"'),'html language');ok(arr[2].includes('role="presentation"'),'email tables');ok((arr[2].match(/<h1\b/g)||[]).length===1,'one heading');ok(!/<script|<img/i.test(arr[2]),'no active scripts/images');ok(!/awin1\.com|affiliates\.inspire3\.com/i.test(arr[2]),'no merchant links');
console.log('R194 source checks PASS: '+count+' (not real email delivery or CI)');