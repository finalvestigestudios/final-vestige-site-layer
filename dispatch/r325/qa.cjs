'use strict';
/* Read-only, offline, zero network, fail-closed review guard. Usage: node dispatch/r325/qa.cjs */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const dir=__dirname;
const files=['issue04-apollo-review.md','issue04-apollo-review.html','issue04-apollo-review.txt','claim-and-conversion-audit.md','release-gates.json'];
const [md,html,txt,audit,raw]=files.map(f=>fs.readFileSync(path.join(dir,f),'utf8'));
const gates=JSON.parse(raw);
const check=(truth,label)=>{assert.ok(truth,label);return label;};
const tests=[
()=>check(files.every(f=>fs.statSync(path.join(dir,f)).size>500),'all five assets substantive'),
()=>check(gates.status==='NOT_ADOPTED_HOLD_UNSENT','release HOLD'),
()=>check(gates.pilot_mix.editorial===4&&gates.pilot_mix.commercial===2,'4:2 mix'),
()=>check(Object.values(gates.release_gates).every(x=>x===false),'no release attestations'),
()=>check(gates.wp_autosend===false,'autopost off'),
()=>check(gates.wp_counts.email_eligible==='UNKNOWN','no invented recipients'),
()=>check(gates.wp_counts.total===3&&gates.wp_counts.confirmed===3&&gates.wp_counts.unconfirmed===2,'overlapping snapshot explicit'),
()=>check(gates.headline.length<=65&&gates.preheader.length<=115,'subject/preheader mobile length'),
()=>check([md,txt,html].every(s=>s.includes(gates.headline)),'subject identical across previews'),
()=>check([md,txt,html].every(s=>s.includes(gates.preheader)),'preheader identical across previews'),
()=>check([md,html,txt].every(s=>s.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]')&&s.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]')),'footer send blockers'),
()=>check([md,txt,html].every(s=>s.includes(gates.primary_cta)),'one first-party investigation CTA consistent'),
()=>check((html.match(/href="https:\/\/finalvestige.com\//g)||[]).length===1,'exactly one promotional CTA anchor'),
()=>check(!/affiliate|zen12|hypnosislive/.test(html.toLowerCase()),'editorial email has no merchant link'),
()=>check(!/<script|<form|<iframe|tracking-pixel|onload=/i.test(html),'email HTML no active content'),
()=>check(/<h1\b/.test(html)&&/lang="en"/.test(html)&&/role="presentation"/.test(html),'HTML landmarks/table semantics'),
()=>check(/width:100%;max-width:600px/.test(html),'responsive email wrapper'),
()=>check([md,txt].every(s=>s.includes('23:31:04.7')&&s.includes('23:31:19')),'timing endpoints supported'),
()=>check([md,txt].every(s=>/seventeen seconds|seventeen seconds/.test(s)),'NASA 17-second different endpoint'),
()=>check([md,txt].every(s=>s.includes('could not identify a particular ignition source conclusively')),'no definitive arc claim'),
()=>check(!/guaranteed income|clinically proven|click here now|buy now before/i.test([md,html,txt].join('')),'no manufactured promotional promise'),
()=>check([md,txt,html].every(s=>s.includes('nasa.gov')&&s.includes('nssdc.gsfc.nasa.gov')),'source trail carried in all formats')
];
for(const f of tests)f();
process.stdout.write('R325 OFFLINE REVIEW: '+tests.length+'/'+tests.length+' checks PASSED; zero sends, no proof of actual Jetpack rendering.\n');