// Native excerpt gate mutation smoke. Offline only; never touches WordPress or mail.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
const parent=path.resolve(here,'..');
const nums=[1,2,3,4,5,6];
function withFixture(callback){
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'fv-dispatch-native-'));
  const campaign=path.join(tmp,'dispatch');
  fs.mkdirSync(path.join(campaign,'native-email-contract'),{recursive:true});
  fs.mkdirSync(path.join(campaign,'delivery'),{recursive:true});
  fs.mkdirSync(path.join(campaign,'issues'),{recursive:true});
  for(const name of ['manifest.json']){
    fs.copyFileSync(path.join(parent,name),path.join(campaign,name));
  }
  fs.copyFileSync(path.join(parent,'delivery','wordpress_excerpt_copy.json'),path.join(campaign,'delivery','wordpress_excerpt_copy.json'));
  fs.copyFileSync(path.join(here,'NATIVE_DELIVERY_PARITY.json'),path.join(campaign,'native-email-contract','NATIVE_DELIVERY_PARITY.json'));
  fs.copyFileSync(path.join(here,'source_gate.mjs'),path.join(campaign,'native-email-contract','source_gate.mjs'));
  for(const file of fs.readdirSync(path.join(parent,'issues'))){
    if(file.endsWith('.md'))fs.copyFileSync(path.join(parent,'issues',file),path.join(campaign,'issues',file));
  }
  try{callback(campaign);}finally{fs.rmSync(tmp,{recursive:true,force:true});}
}
function run(dir){
  const cp=spawnSync(process.execPath,[path.join(dir,'native-email-contract','source_gate.mjs')],{encoding:'utf8',timeout:10000});
  return {status:cp.status,output:cp.stdout,err:cp.stderr};
}
function withJSON(campaign,relative,fn){
  const p=path.join(campaign,relative),obj=JSON.parse(fs.readFileSync(p,'utf8'));
  fn(obj);
  fs.writeFileSync(p,JSON.stringify(obj));
}
test('baseline six-edition source audit never grants sending',()=>{
 withFixture(d=>{const x=run(d);assert.equal(x.status,0,x.err+x.output);
 const r=JSON.parse(x.output);assert.equal(r.release,'HOLD_UNSENT');assert.equal(r.real_WordPress_MIME_received,false);});
});
test('rejects campaign release changed to live',()=>withFixture(d=>{
 withJSON(d,'manifest.json',x=>x.status='READY');assert.equal(run(d).status,1);
}));
test('rejects a fifth editorial-to-offer reallocation',()=>withFixture(d=>{
 withJSON(d,'manifest.json',x=>x.issues[0].kind='commercial-review-pending');assert.equal(run(d).status,1);
}));
test('rejects direct merchant earning URL',()=>withFixture(d=>{
 withJSON(d,'manifest.json',x=>x.issues[2].merchant_affiliate_url='https://zen12.com/getstarted');assert.equal(run(d).status,1);
}));
test('rejects commercial guide falsely marked approved',()=>withFixture(d=>{
 withJSON(d,'manifest.json',x=>x.issues[4].editorial_cta='https://finalvestige.com/mind/total-focus-guide/');assert.equal(run(d).status,1);
}));
test('rejects missing commission disclosure in custom excerpt',()=>withFixture(d=>{
 withJSON(d,'delivery/wordpress_excerpt_copy.json',x=>x.entries[2].excerpt='This section now merely describes the product and its advertised features. '.repeat(4));assert.equal(run(d).status,1);
}));
test('rejects a merchant URL hidden in plain excerpt',()=>withFixture(d=>{
 withJSON(d,'delivery/wordpress_excerpt_copy.json',x=>x.entries[4].excerpt+=' https://hypnosislive.com/mental-skills/total-focus');assert.equal(run(d).status,1);
}));
test('rejects subject drift',()=>withFixture(d=>{
 withJSON(d,'delivery/wordpress_excerpt_copy.json',x=>x.entries[1].subject='Totally unrelated claim');assert.equal(run(d).status,1);
}));
test('rejects disappearance of required postal HOLD',()=>withFixture(d=>{
 const file=fs.readdirSync(path.join(d,'issues')).find(s=>s.startsWith('04-'));
 const p=path.join(d,'issues',file);
 fs.writeFileSync(p,fs.readFileSync(p,'utf8').replace('[[VALID_POSTAL_ADDRESS_REQUIRED]]','INVENTED ADDRESS'));
 assert.equal(run(d).status,1);
}));
test('rejects a guessed opted-in audience',()=>withFixture(d=>{
 withJSON(d,'native-email-contract/NATIVE_DELIVERY_PARITY.json',x=>x.subscribers.unique_permissioned_deliverable=2);
 assert.equal(run(d).status,1);
}));
test('rejects false claim of received WordPress MIME',()=>withFixture(d=>{
 withJSON(d,'native-email-contract/NATIVE_DELIVERY_PARITY.json',x=>x.rows[1].actual_received_mime='PASS');
 assert.equal(run(d).status,1);
}));


// R11 review-board provenance mutations: no review row can silently drift
// away from the six original manuscript/excerpt sources.
test('rejects parity subject changed without changing actual email subject',()=>withFixture(d=>{
 withJSON(d,'native-email-contract/NATIVE_DELIVERY_PARITY.json',x=>x.rows[0].subject='An unrelated headline');
 assert.equal(run(d).status,1);
}));
test('rejects a fabricated native preheader',()=>withFixture(d=>{
 withJSON(d,'native-email-contract/NATIVE_DELIVERY_PARITY.json',x=>x.rows[1].actual_native_preheader='CONFIRMED');
 assert.equal(run(d).status,1);
}));
test('rejects parity preheader drift',()=>withFixture(d=>{
 withJSON(d,'native-email-contract/NATIVE_DELIVERY_PARITY.json',x=>x.rows[2].preheader_plan='Not the manuscript plan');
 assert.equal(run(d).status,1);
}));
test('rejects altered review excerpt not matching the proposed copy',()=>withFixture(d=>{
 withJSON(d,'native-email-contract/NATIVE_DELIVERY_PARITY.json',x=>x.rows[2].proposed_custom_excerpt_NOT_APPLIED='A shortened and misleading promotional claim');
 assert.equal(run(d).status,1);
}));
test('rejects review row allocating a third commercial email',()=>withFixture(d=>{
 withJSON(d,'native-email-contract/NATIVE_DELIVERY_PARITY.json',x=>x.rows[3].kind='commercial-review-pending');
 assert.equal(run(d).status,1);
}));
test('rejects a false published warm-up destination displayed in review board',()=>withFixture(d=>{
 withJSON(d,'native-email-contract/NATIVE_DELIVERY_PARITY.json',x=>x.rows[4].original_editorial_cta='https://finalvestige.com/mind/live-zen12/');
 assert.equal(run(d).status,1);
}));
test('rejects duplicate parity issue numbers masking a missing issue',()=>withFixture(d=>{
 withJSON(d,'native-email-contract/NATIVE_DELIVERY_PARITY.json',x=>x.rows[5].number=5);
 assert.equal(run(d).status,1);
}));
test('rejects a false read-more proof',()=>withFixture(d=>{
 withJSON(d,'native-email-contract/NATIVE_DELIVERY_PARITY.json',x=>x.rows[0].actual_read_more='VERIFIED');
 assert.equal(run(d).status,1);
}));
test('rejects a false physical-address footer verification',()=>withFixture(d=>{
 withJSON(d,'native-email-contract/NATIVE_DELIVERY_PARITY.json',x=>x.rows[4].actual_postal_footer='VERIFIED');
 assert.equal(run(d).status,1);
}));
test('rejects false receipt proof for welcome message',()=>withFixture(d=>{
 withJSON(d,'native-email-contract/NATIVE_DELIVERY_PARITY.json',x=>x.site.welcome_delivered='VERIFIED');
 assert.equal(run(d).status,1);
}));
test('rejects unearned founder and affiliate permissions',()=>withFixture(d=>{
 withJSON(d,'native-email-contract/NATIVE_DELIVERY_PARITY.json',x=>{x.all_issues_send_approval=true;x.commercial_offer_permissions='APPROVED';});
 assert.equal(run(d).status,1);
}));
test('rejects unsubscribe verification claim with no native MIME evidence',()=>withFixture(d=>{
 withJSON(d,'native-email-contract/NATIVE_DELIVERY_PARITY.json',x=>x.rows[3].actual_unsubscribe='VERIFIED');
 assert.equal(run(d).status,1);
}));
