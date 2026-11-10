"use strict";
const fs = require("node:fs");const path=require("node:path");const assert=require("node:assert/strict");
const root=__dirname;
const m=JSON.parse(fs.readFileSync(path.join(root,"source_claim_ledger.json"),"utf8"));
const md=fs.readFileSync(path.join(root,"issue-02-optional.md"),"utf8");
const txt=fs.readFileSync(path.join(root,"issue-02-optional.txt"),"utf8");
const html=fs.readFileSync(path.join(root,"issue-02-optional.html"),"utf8");
const a=[];function test(name,fn){try{fn();a.push(name);}catch(e){throw Error(name+": "+e.message)}}
test("hold",()=>assert.equal(m.status,"DRAFT_UNSENT_NO_ADOPTION"));
test("edition",()=>assert.equal(m.edition,2));
test("commercial off",()=>assert.equal(m.commercial_placement,false));
test("no merchants",()=>assert.deepEqual(m.affiliate_links,[]));
test("no release",()=>assert.equal(m.blocked,true));
test("all proofs false",()=>assert(Object.values(m.live_checks).every(v=>v===false)));
for(const body of [md,txt,html]){
  test("subject parity",()=>assert(body.includes(m.planned_subject)));
  test("preheader parity",()=>assert(body.includes(m.planned_preheader)));
  test("CTA parity",()=>assert(body.includes(m.single_editorial_cta)));
  test("footer hold",()=>assert(body.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]")&&body.includes("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]")));
  for(const s of m.research_claims){for(const url of s.sources)test("source included",()=>assert(body.includes(url)));}
}
test("HTML presentation tables",()=>assert(/role="presentation"/.test(html)));
test("HTML descriptive heading",()=>assert(/<h1/.test(html)));
test("HTML language",()=>assert(/lang="en"/.test(html)));
test("HTML mail no script",()=>assert(!/<script/i.test(html)));
test("HTML no remote images",()=>assert(!/<img/i.test(html)));
test("no active merchant links",()=>assert(!/href=["']https?:\/\/(zen12|hypnosislive|inspire3)/i.test(html)));
test("one principal CTA",()=>assert((html.match(/Read the archival case file/g)||[]).length===1));
test("marketing timing not invented",()=>assert(!/buy now|limited offer|guaranteed results/i.test(md+" "+txt)));
console.log("R267 exact-source native JS QA: "+a.length+" checks passed; release remains UNSENT / NOT ADOPTED.");
