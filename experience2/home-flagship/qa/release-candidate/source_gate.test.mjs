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
 "unresponsive retained image":h=>h.replace(/ srcset="[^"]+" sizes="[^"]+"/,""),
 "unverified NYPL capture added":h=>h.replace('<div class="fv-hf__source-plate"', '<img src="https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg"><div class="fv-hf__source-plate"'),
 "NYPL source plate removed":h=>h.replace('class="fv-hf__source-plate"','class="fv-hf__uncited-plate"'),
 "unsupported merchant pitch":h=>h+"<p>guaranteed brain reprogramming</p>",
 "remote executable":h=>h.replace("./flagship.js","https://unverified.invalid/script.js"),
};for(const [name,mutate] of Object.entries(bad))test("fail closed "+name,()=>{const changed=mutate(html);assert.notEqual(changed,html);assert.equal(check(changed).source.status,"FAIL")});

test("exact source retains only two original locally generated SVG grain textures",()=>{
  const result=check(html);
  assert.equal(result.source.checks.two_original_noise_textures_byte_pinned,true);
  assert.equal(result.source.checks.no_unreviewed_embedded_image_transport,true);
  assert.equal(result.source.checks.no_unreviewed_css_image_url_or_image_set,true);
});
const nonHttpHostiles=[
  ["inline raster data URI", (h,f)=>[h+'<div style="background-image:url(data:image/jpeg;base64,ZmFrZQ==)"></div>',f]],
  ["inline svg evidence facsimile", (h,f)=>[h+'<svg aria-label="unreviewed archival drawing"><image href="data:image/png;base64,ZmFrZQ=="/></svg>',f]],
  ["embedded canvas reproduction", (h,f)=>[h+'<canvas width="500" height="800"></canvas>',f]],
  ["direct blob URL", (h,f)=>[h+'<div style="background-image:url(blob:https://finalvestige.com/abc)"></div>',f]],
  ["unexpected CSS data URL", (h,f)=>{f["chronicle.css"]+='\\n.fv-hf__bogus {background:url("data:image/png;base64,ZmFrZQ==")}';return[h,f]}],
  ["unexpected external CSS background", (h,f)=>{f["inquiry.css"]+='\\n.fv-hf__bogus {background:url(https://unreviewed.example/archive.jpg)}';return[h,f]}],
  ["unexpected CSS image-set", (h,f)=>{f["observer-lab.css"]+='\\n.fv-hf__bogus {background:image-set("https://unreviewed.example/old.jpg" 1x)}';return[h,f]}],
  ["runtime image constructor", (h,f)=>{f["reading-trail.js"]+='\\nnew Image().src="data:image/jpeg;base64,ZmFrZQ==";';return[h,f]}],
  ["runtime blob creation", (h,f)=>{f["flagship.js"]+='\\nURL.createObjectURL(new Blob([]));';return[h,f]}],
  ["runtime canvas creation", (h,f)=>{f["flagship.js"]+='\\ndocument.createElement("canvas");';return[h,f]}],
  ["runtime svg creation", (h,f)=>{f["observer-lab.js"]+='\\ndocument.createElement("svg");';return[h,f]}]
];
for(const [name,modify] of nonHttpHostiles){
  test("reject unreviewed non-HTTP image path: "+name,()=>{
    const [h,changed]=modify(html,{...assets});
    const result=check(h,manifest,changed);
    assert.equal(result.source.status,"FAIL",name);
    assert.ok(["no_unreviewed_embedded_image_transport",
      "no_unreviewed_css_image_url_or_image_set"].some(k=>result.source.checks[k]===false),
      name+": "+result.source.errors.join(", "));
  });
}
test("the original inline noise texture may not be silently revised",()=>{
  const changed={...assets,
    "flagship.css":assets["flagship.css"].replace("baseFrequency='.7'","baseFrequency='.71'")};
  assert.notEqual(changed["flagship.css"],assets["flagship.css"]);
  const result=check(html,manifest,changed);
  assert.equal(result.source.checks.two_original_noise_textures_byte_pinned,false);
  assert.equal(result.source.status,"FAIL");
});
test("missing runtime asset fails",()=>{const x={...assets};delete x["reading-trail.js"];assert.equal(check(html,manifest,x).source.status,"FAIL")});
test("prose alone cannot grant copyright clearance",()=>{const m=structuredClone(manifest);m.records.forEach(x=>x.media_rights_status="Approved");assert.equal(check(html,m).media.status,"HOLD")});
