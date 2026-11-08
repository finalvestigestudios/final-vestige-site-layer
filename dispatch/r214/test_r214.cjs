#!/usr/bin/env node
'use strict';
// UNSENT and offline: only reads repository files; never sends mail, calls network or touches WordPress.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname,'../..');
const issues = [
 ['01-when-the-person-changed.html','3148f1599714efa1decb188c40eae997892911ad','editorial'],
 ['02-the-patient-and-the-witness.html','b68dd602830ae041cd27a416d9517644a19e700a','editorial'],
 ['03-zen12-what-twelve-minutes-can-prove.html','f5a69e65130554f44db055e0cb55b2df9616b451','commercial'],
 ['04-apollo-one-why-the-record-matters.html','dd660257b9b1b90822b344091cce788f0e1c26cf','editorial'],
 ['05-total-focus-what-is-in-the-recording.html','6b0b05d72b4b0a6181e0cce0617c5d3237e63c2d','commercial'],
 ['06-the-notebook-is-not-the-verdict.html','16afce0c80d11ccffbe05aebf1bd2348b18b5c4b','editorial']
];
function gitBlob(text) {
 const b = Buffer.from(text,'utf8');
 return crypto.createHash('sha1').update(Buffer.from('blob '+b.length+'\\0'.replace('\\0','\0'))).update(b).digest('hex');
}
function check() {
 let count=0;
 for(const [file,expectedSource,type] of issues) {
  const original=fs.readFileSync(path.join(root,'dispatch/r211/preview',file),'utf8');
  const corrected=fs.readFileSync(path.join(__dirname,'preview',file),'utf8');
  assert.equal(gitBlob(original),expectedSource,'r211 upstream source has changed; STOP: '+file);count++;
  const m=corrected.match(/(<body\\b[^>]*>\\s*)(<div role="presentation" aria-hidden="true" data-fv-review-preheader="first-body-text"[^>]*>)([^<]+)(<\\/div>)/);
  assert.ok(m,'no first-body hidden preheader: '+file);count++;
  const visible=original.match(/<h1[^>]*>[^<]+<\\/h1>\\s*<p style="color:#d4dce7;font-size:15px;margin:0 0 28px">([^<]+)<\\/p>/);
  assert.ok(visible,'r211 preheader vanished: '+file);count++;
  assert.equal(m[3],visible[1]);count++;
  assert.match(m[2],/display:none!important/);count++;
  assert.match(m[2],/mso-hide:all/);count++;
  assert.equal(corrected.replace(m[1]+m[2]+m[3]+m[4],m[1]),original,'content changed beyond one hidden preheader: '+file);count++;
  assert.equal((corrected.match(/data-fv-review-preheader=/g)||[]).length,1);count++;
  assert.match(corrected,/REVIEW ONLY · UNSENT · NOT APPROVED/);count++;
  assert.match(corrected,/\\[\\[VALID_FINAL_VESTIGE_POSTAL_ADDRESS_REQUIRED\\]\\]/);count++;
  assert.match(corrected,/\\[\\[JETPACK_UNSUBSCRIBE_MUST_BE_VERIFIED\\]\\]/);count++;
  assert.doesNotMatch(corrected,/<script\\b|utm_source=|awin1\\.com|inspire3\\.com\\/affiliate\\//i);count++;
  if(type==='commercial'){
   assert.match(corrected,/may earn a commission/);count++;
   assert.match(corrected,/INACTIVE \\/ NOT APPROVED/);count++;
   assert.doesNotMatch(corrected,/<a[^>]+href=["'][^"']*(zen12\\.com|hypnosislive\\.com|awin1\\.com)/i);count++;
  }
 }
 assert.equal(issues.length,6);count++;
 console.log('R214 source-only preview assertions PASS:',count,'(no Jetpack/inbox claim; all HOLD_UNSENT)');
}
if(require.main===module)check();
module.exports={check,gitBlob};
