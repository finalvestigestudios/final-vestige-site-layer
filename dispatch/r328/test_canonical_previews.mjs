import {readFileSync} from "node:fs";import {strict as assert} from "node:assert";import {buildIssue} from "./build_canonical_previews.mjs";
const base=new URL("../campaign-2026-mind/",import.meta.url);
const manifest=JSON.parse(readFileSync(new URL("manifest.json",base),"utf8"));
assert.equal(manifest.status,"DRAFT_UNSENT_NO_SCHEDULING");
assert.equal(manifest.issues.filter(i=>i.kind==="editorial").length,4);
assert.equal(manifest.issues.filter(i=>i.kind==="commercial-review-pending").length,2);
for(const issue of manifest.issues){
 const md=readFileSync(new URL("issues/"+String(issue.number).padStart(2,"0")+"-"+issue.slug+".md",base),"utf8");
 const got=buildIssue(md,issue);
 const n=String(issue.number).padStart(2,"0");
 assert.equal(got.html,readFileSync(new URL("./previews/issue-"+n+".html",import.meta.url),"utf8"));
 assert.equal(got.txt,readFileSync(new URL("./previews/issue-"+n+".txt",import.meta.url),"utf8"));
 assert.match(got.html,/UNSENT OFFLINE REVIEW/);
 assert.match(got.html,/\[\[VALID_POSTAL_ADDRESS_REQUIRED\]\]/);
 assert.match(got.html,/\[\[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED\]\]/);
 assert.doesNotMatch(got.html,/<(?:script|iframe|form|img)\b/i);
 assert.doesNotMatch(got.html,/href="https:\/\/(?:zen12|hypnosislive|inspire3)\./i);
 assert.equal((got.html.match(/<h1\b/g)||[]).length,1);
 if(issue.kind==="commercial-review-pending"){assert.match(got.html,/Commercial disclosure:/);assert.match(got.html,/\[\[APPROVED_/);}
 console.log("PASS canonical issue "+n);
}
console.log("PASS: 6 deterministic source-equal previews, 4:2, hold guards; NEVER SEND");
