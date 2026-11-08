"use strict";
/** Run: node --test experience2/review/test_ex2_homepage_exact_delta_gate.cjs
 * Synthetic private data; independently repeat on authenticated WP exports.
 * CI failure/skip is NOT a successful test.
 */
const test=require("node:test"), assert=require("node:assert/strict");
const {review}=require("./ex2_homepage_exact_delta_gate.cjs");
const {assemble,PIN,REPLACEMENTS,CHAPTERS}=require("./atomic_page6_review.cjs");
const {admit}=require("./ex2_homepage_no_loss_gate.cjs");
const injected={hashFn:()=>PIN}; // Synthetic fixture only; never a production bypass.

function fixture(){
 const source=[
  '<div class="fv-margin-strip">'+Array.from({length:72},(_,i)=>
    '<span class="fv-margin-strip__item">Record '+String(i+1).padStart(3,"0")+'</span>').join("")+'</div>',
  '<nav class="fv-hf__chapter-nav">'+CHAPTERS.map(c=>
    '<a href="#fv-hf-'+c+'">Section</a>').join("")+'</nav>',
  CHAPTERS.map(c=>'<section id="fv-hf-'+c+'">Evidence</section>').join(""),
  '<!-- wp:jetpack/subscriptions -->',
  '<img src="/assets/s67-19766.webp"><img src="/assets/Franklinexpeditionnote.jpg">',
  '<img src="/assets/nypl-5003296-original.jpg"><img src="/assets/fourth.jpg">',
  '<a href="/focus/">Focus</a>'.repeat(4),
  REPLACEMENTS.map(r=>r[1]).join("\n")
 ].join("\n");
 const home={id:6,status:"publish",modified:"2026-11-05T12:07:24",content:source};
 const focus={id:1579,status:"publish",modified:"2026-11-05T17:44:02",
   content:"our email of new investigations and archive finds, sent when we publish them. fvf-gift-v2"};
 return {home,focus,approved:assemble(home,focus,injected).proposed_content};
}
const f=fixture();
test("exact reviewed five-edit candidate passes but is NEVER releasable",()=>{
 const receipt=review(f.home,f.focus,f.approved,injected);
 assert.equal(receipt.status,"EXACT_DELTA_PASS_RELEASE_HOLD");
 assert.equal(receipt.release_approved,false);
 assert.equal(receipt.production_write,false);
 assert.equal(receipt.before.margins,72);
 assert.equal(receipt.after.jetpack,1);
 assert.equal(receipt.after.focus,5);
 assert.equal(receipt.operations.length,5);
});
const malicious={
 "identity is not the reviewed five-edit candidate":f.home.content,
 "injected tracking":f.approved+'<script src="https://unreviewed.example/t.js"></script>',
 "affiliate merchant":f.approved+'<a href="https://merchant.example/order">Buy</a>',
 "undisclosed brain claim":f.approved.replace("New investigations, delivered when we publish.","Proven brain reprogramming!"),
 "commission disclosure removed":f.approved.replace("Some emails may contain recommendations that earn us a commission.",""),
 "commission disclosure duplicated":f.approved+REPLACEMENTS[2][2],
 "checkout substituted for privacy":f.approved.replace('href="/privacy-policy/"','href="https://seller.example/pay"'),
 "Jetpack block removed":f.approved.replace("wp:jetpack/subscriptions","wp:paragraph"),
 "evidence text silently altered":f.approved.replace("Record 001","Record 000"),
 "chapter nav duplicated":f.approved+'<nav class="fv-hf__chapter-nav">Second nav</nav>',
 "archive image substituted":f.approved.replace("nypl-5003296-original.jpg","unreviewed.jpg"),
 "focus goes offsite":f.approved.replace('href="https://finalvestige.com/focus/"','href="https://seller.example/pay/"'),
 "single whitespace changed":f.approved+" ",
 "CSS hides experience":f.approved+"<style>.fv-hf{display:none}</style>",
 "privacy terms changed":f.approved.replace("Privacy Policy</a>","Personal Data Policy</a>")
};
for(const [name,candidate] of Object.entries(malicious))
 test("fails closed: "+name,()=>assert.throws(()=>review(f.home,f.focus,candidate,injected),/HOLD:/));
test("reproduces original structural gate blindspot: injected script passes old gate",()=>{
 const maliciousHtml=malicious["injected tracking"];
 assert.equal(admit(f.home.content,maliciousHtml).status,"STRUCTURAL_PASS_RELEASE_HOLD");
 assert.throws(()=>review(f.home,f.focus,maliciousHtml,injected),/HOLD:/);
});
test("rejects changed Focus landing-page date",()=>{
 assert.throws(()=>review(f.home,{...f.focus,modified:"2030-01-01"},f.approved,injected),/HOLD:/);
});
test("rejects missing raw edit-source instead of treating rendered HTML as authority",()=>{
 assert.throws(()=>review({id:6,content:{rendered:"x"}},f.focus,f.approved,injected),/HOLD:/);
});
test("native cryptographic pin blocks untrusted synthetic input",()=>{
 assert.throws(()=>review(f.home,f.focus,f.approved),/HOLD: exact homepage SHA mismatch/);
});
test("test-only hash bypass never changes production default",()=>{
 assert.equal(typeof injected.hashFn,"function");
 assert.throws(()=>review(f.home,f.focus,f.approved),/HOLD: exact homepage SHA mismatch/);
});
