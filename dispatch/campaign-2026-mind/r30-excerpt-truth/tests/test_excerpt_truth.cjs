'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {audit}=require('../audit_excerpt_truth.cjs');
const root=path.resolve(__dirname,'../..');
const data=JSON.parse(fs.readFileSync(path.join(root,'delivery/wordpress_excerpt_copy.json'),'utf8'));
const manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
const sources=manifest.issues.map(x=>fs.readFileSync(path.join(root,'issues',String(x.number).padStart(2,'0')+'-'+x.slug+'.md'),'utf8'));
let assertions=0,mutations=0;
function verify(ok,msg){assert.ok(ok,msg);assertions++}
function copy(x){return JSON.parse(JSON.stringify(x))}
const good=audit(data,manifest,sources);
verify(good.errors.length===0,'current six excerpts must be source-aligned');
verify(good.rows.length===6&&!good.ready_to_send,'six safely held');
for(const row of good.rows){verify(row.source_matched,'source '+row.number);verify(row.characters<=350,'preview char '+row.number);verify(row.words>=45&&row.words<=100,'preview words '+row.number);verify(row.release_status.startsWith('HOLD_'),'hold '+row.number)}
for(const i of [2,4])verify(good.rows[i].commercial_disclosure_within_first_350===true,'commercial disclosure '+i);
for(const i of [0,1,3,5])verify(good.rows[i].commercial_disclosure_within_first_350===null,'noncommercial '+i);
const attacks=[
 ['wrong century',d=>d.entries[0].excerpt+=' Eighteenth-century archives.'],
 ['first clue overclaim',d=>d.entries[3].excerpt=d.entries[3].excerpt.replace('first recorded crew report of fire','first indication')],
 ['unauthorized affiliate URL',d=>d.entries[2].excerpt+=' https://example.com/?aff_id=17'],
 ['guaranteed effect',d=>d.entries[4].excerpt+=' Guaranteed!'],
 ['missing disclosure',d=>d.entries[2].excerpt=d.entries[2].excerpt.replace('may earn a commission','does not earn')],
 ['wrong subject',d=>d.entries[0].subject='Buy now'],
 ['unauthorized readiness',d=>d.status='APPROVED'],
 ['sneaky HTML',d=>d.entries[0].excerpt='<a href="https://bad.example">go</a>'+d.entries[0].excerpt],
 ['too long',d=>d.entries[5].excerpt+=' A'.repeat(200)],
 ['missing source anchor',d=>d.entries[5].excerpt=d.entries[5].excerpt.replace('2002','1999')],
 ['manufactured testimonial',d=>d.entries[4].excerpt+=' Clinically proven'],
 ['commercial role leak',d=>d.entries[0].excerpt+=' Affiliate offer'],
];
for(const [name,attack] of attacks){const d=copy(data);attack(d);const bad=audit(d,manifest,sources);verify(bad.errors.length>0,'reject '+name);mutations++}
{const d=copy(manifest);d.issues[2].merchant_affiliate_url='https://merchant.example';verify(audit(data,d,sources).errors.length>0,'reject merchant activation');mutations++}
{const d=copy(manifest);d.issues[4].editorial_cta='https://hypnosislive.com';verify(audit(data,d,sources).errors.length>0,'reject unapproved guide');mutations++}
{const d=copy(manifest);d.mix.editorial=5;verify(audit(data,d,sources).errors.length>0,'reject 5-1 ratio');mutations++}
{const d=[...sources];d[0]=d[0].replaceAll('Simons','Unknown');verify(audit(data,manifest,d).errors.length>0,'reject missing proof');mutations++}
console.log(JSON.stringify({status:'PASS',assertions,adversarial_mutations_rejected:mutations,real_email_test:false,wordpress_write:false}));
