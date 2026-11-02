import {test} from "node:test";import {strict as assert} from "node:assert";import {readFileSync} from "node:fs";import {resolve,join} from "node:path";import {fileURLToPath} from "node:url";import {auditHomepage} from "./source_gate.mjs";
const root=resolve(fileURLToPath(new URL(".",import.meta.url)),"../..");
const styles=["flagship.css","chronicle.css","chronicle-lens.css","inquiry.css","observer-lab.css","reading-trail.css"],scripts=["flagship.js","observer-lab.js","chronicle-lens.js","reading-trail.js"];
const html=readFileSync(join(root,"index.html"),"utf8"),manifest=JSON.parse(readFileSync(join(root,"source-manifest.json"),"utf8"));
const assets=Object.fromEntries([...styles,...scripts].map(n=>[n,readFileSync(join(root,n),"utf8")]));
const check=(h,m=manifest,files=assets)=>auditHomepage(h,m,files);
test("real seven-chapter canonical source PASS and release HOLD",()=>{const r=check(html);assert.equal(r.source.status,"PASS",r.source.errors.join(","));assert.equal(r.release.status,"HOLD");assert.equal(r.media.status,"HOLD")});
const bad={
 "duplicate ids":h=>h.replace('id="fv-hf-observer"','id="fv-hf-title"'),
 "unresolved anchor":h=>h.replace('href="#fv-hf-observer"','href="#invalid"'),
 "missing source":h=>h.replaceAll("https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/","/unsourced/"),
 "broken image provenance":h=>h.replace("https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp","https://unverified.invalid/photo.jpg"),
 "hidden no-JS case":h=>h.replace('data-fv-case="apollo" id="fv-hf-apollo"','data-fv-case="apollo" hidden id="fv-hf-apollo"'),
 "unresponsive map":h=>h.replace(/ srcset="[^"]+" sizes="[^"]+"/,""),
 "unsupported merchant pitch":h=>h+"<p>guaranteed brain reprogramming</p>",
 "remote executable":h=>h.replace("./flagship.js","https://unverified.invalid/script.js"),
};for(const [name,mutate] of Object.entries(bad))test("fail closed "+name,()=>{const changed=mutate(html);assert.notEqual(changed,html);assert.equal(check(changed).source.status,"FAIL")});
test("missing runtime asset fails",()=>{const x={...assets};delete x["reading-trail.js"];assert.equal(check(html,manifest,x).source.status,"FAIL")});
test("prose alone cannot grant copyright clearance",()=>{const m=structuredClone(manifest);m.records.forEach(x=>x.media_rights_status="Approved");assert.equal(check(html,m).media.status,"HOLD")});
