"use strict";
const fs=require("node:fs"),path=require("node:path"),{audit}=require("./audit.cjs");
const root=path.resolve(__dirname,"..");
const read=x=>fs.readFileSync(path.join(root,x),"utf8");
const payload={article:read("article-invisible-gorilla.md"),html:read("page-invisible-gorilla.blocks.html"),ledger:JSON.parse(read("source-claim-ledger.json")),nav:JSON.parse(read("navigation.json")),playbook:read("offer-bridge-and-attribution.md"),film:read("video-42s-script.md")};
const result=audit(payload);
for(const x of result.checks)console.log((x.pass?"PASS ":"FAIL ")+x.label+(x.error?" — "+x.error:""));
console.log(result.passed+" passed, "+result.failed+" failed");
if(result.failed)process.exitCode=1;