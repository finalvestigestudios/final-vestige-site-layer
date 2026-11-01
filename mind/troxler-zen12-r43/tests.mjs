import assert from "node:assert/strict";import{readFileSync}from"node:fs";import{ENABLED,normalizeSynthetic,aggregateSynthetic,recordLive}from"./privacy-synthetic.mjs";
const read=n=>readFileSync(new URL(n,import.meta.url),"utf8"),a=read("zen12-text.html"),b=read("zen12-video-concept.html"),hub=read("mind-hub-review.html");
let count=0;const ok=(x,m)=>{assert.ok(x,m);count++};const stripFilm=x=>x.replace(/<aside class="film"[\s\S]*?<\/aside>/,"");
ok(stripFilm(b)===a,"A/B exactly identical substantive copy");
const vendor=x=>/<a\b[^>]*href\s*=\s*["'][^"']*(zen12\.com|inspire3\.com|hypnosislive\.com)/i.test(x);
for(const [name,x]of[["A",a],["B",b],["hub",hub]]){ok(!vendor(x),name+" no merchant click");ok(!/<script\b|<form\b|<iframe\b/i.test(x),name+" no script/form/embed");ok(!/<video\b|<audio\b/i.test(x),name+" no fake media");ok(/<main\b/i.test(x),name+" main landmark");ok(/:focus-visible/.test(x),name+" keyboard focus");ok(/prefers-reduced-motion/.test(x),name+" motion setting");}
for(const x of[a,b]){ok(/Prospective affiliate disclosure/.test(x),"disclosure near CTA");ok(/<button[^>]*disabled/.test(x),"disabled CTA");ok(x.includes("finalvestige.com/focus/"),"existing Focus funnel");}
ok(b.includes('src="poster.svg"'),"poster");ok(b.includes("Complete readable transcript"),"transcript");ok(read("claims-permissions.csv").split("\n").length>45,"matrix >=44 decisions");ok(read("editor-sources.md").includes("https://zen12.com/hnp"),"exact offer editor register");
const v={variant:"A",source:"organic",topic:"zen12",event:"guide-view"};ok(normalizeSynthetic(v)!==null,"valid synthetic");
for(const f of[{email:"a@b.com"},{ip:"127.0.0.1"},{referrer:"https://example.org"},{utm:"secret"},{cookie:"x"},{user_id:"U1"}])ok(normalizeSynthetic({...v,...f})===null,"reject PII");
ok(normalizeSynthetic({...v,source:"x"})===null,"strict allowlist");ok(normalizeSynthetic(null)===null,"reject null");ok(aggregateSynthetic(Array(19).fill(v)).length===0,"suppress <20");ok(aggregateSynthetic(Array(20).fill(v))[0].count===20,">=20 aggregate");ok(ENABLED===false&&recordLive()===false,"off");
for(const s of["<a href='https://zen12.com/hnp'>buy</a>","<a href='https://inspire3.com/'>buy</a>","<a href='https://hypnosislive.com/buy'>buy</a>"])ok(vendor(a+s),"vendor mutation caught");
console.log("PASS "+count+" native assertions (synthetic only)");
