"use strict";
const fs=require("node:fs"), path=require("node:path"),assert=require("node:assert/strict");
const root=__dirname;
const files={issue:fs.readFileSync(path.join(root,"ISSUE02_1784_REPORT_ALTERNATIVE_UNSENT.md"),"utf8"),html:fs.readFileSync(path.join(root,"ISSUE02_OFFLINE_REVIEW.html"),"utf8"),plain:fs.readFileSync(path.join(root,"ISSUE02_OFFLINE_REVIEW.txt"),"utf8"),ledger:fs.readFileSync(path.join(root,"SOURCE_AND_CONVERSION_REVIEW.md"),"utf8"),contract:JSON.parse(fs.readFileSync(path.join(root,"RELEASE_CONTRACT.json"),"utf8"))};
const {checkDraft}=require("./R238_GUARD.cjs");
const baseline=checkDraft(files);
assert(baseline.pass,baseline.checks.filter(x=>!x.pass).map(x=>x.name).join("; "));
const bad=[
 ["unsent switched", {...files,contract:{...files.contract,send_enabled:true}}],
 ["merchant approved without proof", {...files,contract:{...files.contract,final_merchant_email_permission_verified:true}}],
 ["fake money", {...files,contract:{...files.contract,verified_paid_orders:10}}],
 ["lost full gate", {...files,html:files.html.replace("[[VALID_POSTAL_ADDRESS_REQUIRED]]","a guessed address")}],
 ["unsafe pixel", {...files,html:files.html.replace("</body>","<img src='https://example.test/track'></body>")}],
 ["wrong historical target", {...files,issue:files.issue.replace("not a controlled test of the Marquis de Puységur","a controlled test of the Marquis de Puységur")}],
 ["drifted html preheader", {...files,html:files.html.replace("In 1784, investigators asked","In 1786, investigators asked")}],
 ["fake approved link", {...files,issue:files.issue+"https://zen12.com/hnp"}],
 ["newsletter source removed", {...files,plain:files.plain.replace("gutenberg.org/files/78413","example.org/unknown")}],
 ["missing second source", {...files,html:files.html.replace("wellcomecollection.org/works/enhgscmf","example.org/unknown")}]
];
for(const [name,mutated] of bad)assert(!checkDraft(mutated).pass,name);
console.log("R238 native Node: "+baseline.checks.length+" baseline checks PASS; "+bad.length+" negative controls rejected. NO SEND.");
