'use strict';
/* R28 exact-current-source regression tests. No network, WordPress writes or mail. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {auditCampaign,words,markdownText,markupText}=require('../audit_surfaces.cjs');
const root=path.resolve(__dirname,'../..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const manifest=JSON.parse(read('manifest.json'));
const id=n=>String(n).padStart(2,'0');
function sourceBundle(){
 const data={manifest:structuredClone(manifest),issues:[],previews_html:[],previews_txt:[],
  gutenberg:[],ledger:JSON.parse(read('wordpress-post-bridge-r23/proofs/RELEASE_COMPATIBILITY.json')),
  board:read('wordpress-post-bridge-r23/proofs/OFFLINE_POST_REVIEW.html')};
 for(const issue of manifest.issues){
  const name=id(issue.number)+'-'+issue.slug;
  data.issues.push(read('issues/'+name+'.md'));
  data.previews_html.push(read('previews/'+name+'.html'));
  data.previews_txt.push(read('previews/'+name+'.txt'));
  data.gutenberg.push(read('wordpress-post-bridge-r23/proofs/issue-'+id(issue.number)+'.blocks.html'));
 }
 return data;
}
const genuine=sourceBundle(),passed=auditCampaign(genuine);
assert.equal(passed.status,'SOURCE_SURFACES_PASS_RELEASE_HOLD',
 'Original source surfaces must agree, without pretending to be send-ready');
assert.equal(passed.failures.length,0);
assert.equal(passed.editions.length,6);
assert.equal(passed.editions.filter(x=>x.status==='HOLD_UNSENT_AND_MERCHANT').length,2);
assert.equal(passed.editions.filter(x=>x.status==='HOLD_UNSENT').length,4);
let cases=5;
function reject(name,mutate,expected){
 const data=structuredClone(genuine);mutate(data);
 const result=auditCampaign(data);
 assert.equal(result.status,'INVALID_HOLD',name+' must fail closed');
 assert(result.failures.some(x=>x.id===expected),
  name+' failed for wrong reason: '+JSON.stringify(result.failures));
 cases++;
}
reject('commercial send-state mutation',x=>x.manifest.issues[2].publish_state='publish','I03-sequence');
reject('invented affiliate URL',x=>x.manifest.issues[4].merchant_affiliate_url='https://example.com/earn','I05-sequence');
reject('editorial became commercial',x=>x.manifest.issues[0].kind='commercial-review-pending','I01-classification');
reject('four/two drift',x=>x.manifest.mix.editorial=5,'campaign-manifest');
reject('dishonest subject',x=>x.manifest.issues[0].subject='You must click now','I01-metadata');
reject('missing preheader',x=>x.previews_txt[0]=x.previews_txt[0].replace('Preheader:','Preview:'),'I01-metadata');
reject('legal postal marker removed',x=>x.issues[5]=x.issues[5].replace('[[VALID_POSTAL_ADDRESS_REQUIRED]]',''),'I06-legal-hold');
reject('missing unsub marker',x=>x.previews_txt[0]=x.previews_txt[0].replace('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]',''),'I01-legal-hold');
reject('commercial guide prematurely enabled',x=>x.manifest.issues[2].editorial_cta='https://finalvestige.com/mind/zen12-guide/','I03-disabled-guide');
reject('commercial disclosure deleted',x=>x.issues[4]=x.issues[4].replace('Commercial disclosure:','Reader note:'),'I05-near-cta-disclosure');
reject('commercial Gutenberg CTA switched on',x=>x.gutenberg[2]=x.gutenberg[2].replace('GUIDE NOT LIVE — NO LINK','<a href="https://site.test/">BUY</a>'),'I03-disabled-guide');
reject('merchant direct earning link',x=>x.previews_html[4]+='<a href="https://hop.clickbank.net/?affiliate=fake">Offer</a>','I05-no-live-affiliate');
reject('narrative deleted from plaintext',x=>x.previews_txt[3]='UNSENT DRAFT — DO NOT SEND','I04-opening-middle-closing');
reject('lost academic citation',x=>x.previews_html[5]=x.previews_html[5].replace('https://www.bmj.com/content/324/7347/1193',''),'I06-source-links');
reject('review board lacks warning',x=>x.board='Six issues approved to publish','review-board-is-unsent');
reject('release attestation falsely green',x=>x.ledger.editions[0].release_ready=true,'I01-release-ledger');
reject('release ledger recipient toggle',x=>x.ledger.editions[4].send_to_subscribers=true,'I05-release-ledger');
reject('converted content changed',x=>x.gutenberg[1]=x.gutenberg[1].replace('May 4, 1784','May 5, 1784'),'I02-opening-middle-closing');
reject('missing entire source',x=>x.issues[0]='','I01-body-boundaries');
// Normalization tests distinguish harmless escaped quotes from altered evidence.
assert.equal(markupText('<p>brain &quot;reprogramming&quot;</p>'),words('brain "reprogramming"'));
assert.equal(markdownText('**Observed:** [NASA](https://www.nasa.gov/)'),words('Observed NASA'));
cases+=2;
console.log('R28 SOURCE SURFACE TESTS: '+cases+' assertions passed; '+passed.checked+
 ' current-source checks; no sends, WordPress writes, merchant promotions or live email asserted.');
