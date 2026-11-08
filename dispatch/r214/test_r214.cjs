#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..');
const issues=[
 ['01-when-the-person-changed.html','3148f1599714efa1decb188c40eae997892911ad','editorial'],
 ['02-the-patient-and-the-witness.html','b68dd602830ae041cd27a416d9517644a19e700a','editorial'],
 ['03-zen12-what-twelve-minutes-can-prove.html','f5a69e65130554f44db055e0cb55b2df9616b451','commercial'],
 ['04-apollo-one-why-the-record-matters.html','dd660257b9b1b90822b344091cce788f0e1c26cf','editorial'],
 ['05-total-focus-what-is-in-the-recording.html','6b0b05d72b4b0a6181e0cce0617c5d3237e63c2d','commercial'],
 ['06-the-notebook-is-not-the-verdict.html','16afce0c80d11ccffbe05aebf1bd2348b18b5c4b','editorial']
];
function gitBlob(text) {
 const b=Buffer.from(text,'utf8');
 return crypto.createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');
}
function check() {
 let n=0;
 for(const [file,sha,type] of issues) {
  const a=fs.readFileSync(path.join(root,'dispatch/r211/preview',file),'utf8');
  const b=fs.readFileSync(path.join(__dirname,'preview',file),'utf8');
  assert.equal(gitBlob(a),sha,'R211 source changed: '+file);n++;
  const h=b.match(/(<body\b[^>]*>\s*)(<div role="presentation" aria-hidden="true" data-fv-review-preheader="first-body-text"[^>]*>)([^<]+)(<\/div>)/);
  assert.ok(h,'first-body preheader missing: '+file);n++;
  const p=a.match(/<h1[^>]*>[^<]+<\/h1>\s*<p style="color:#d4dce7;font-size:15px;margin:0 0 28px">([^<]+)<\/p>/);
  assert.ok(p,'source visible preheader missing: '+file);n++;
  assert.equal(h[3],p[1]);n++;
  assert.match(h[2],/display:none!important/);n++;
  assert.match(h[2],/mso-hide:all/);n++;
  assert.equal(b.replace(h[0],h[1]),a,'modified existing copy: '+file);n++;
  assert.equal((b.match(/data-fv-review-preheader=/g)||[]).length,1);n++;
  assert.match(b,/REVIEW ONLY · UNSENT · NOT APPROVED/);n++;
  assert.match(b,/\[\[VALID_FINAL_VESTIGE_POSTAL_ADDRESS_REQUIRED\]\]/);n++;
  assert.match(b,/\[\[JETPACK_UNSUBSCRIBE_MUST_BE_VERIFIED\]\]/);n++;
  assert.doesNotMatch(b,/<script\b|utm_source=|awin1\.com|inspire3\.com\/affiliate\//i);n++;
  if(type==='commercial'){
   assert.match(b,/may earn a commission/);n++;
   assert.match(b,/INACTIVE \/ NOT APPROVED/);n++;
   assert.doesNotMatch(b,/<a[^>]+href=["'][^"']*(zen12\.com|hypnosislive\.com|awin1\.com)/i);n++;
  }
 }
 assert.equal(issues.length,6);n++;
 console.log('PASS',n,'R214 offline assertions; native Jetpack and actual inbox UNVERIFIED');
}
if(require.main===module)check();
module.exports={check,gitBlob};