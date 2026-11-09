/* R253 reproducible static commercial guard. Run from repository root: node mind/r253/test_r253.cjs . No requests/network required. */
const fs=require("node:fs"), assert=require("node:assert/strict"), path=require("node:path");
const base=__dirname;
const read=n=>fs.readFileSync(path.join(base,n),"utf8");
const A=read("zen12-A-text-UNPUBLISHED.html"), B=read("zen12-B-optional-video-UNPUBLISHED.html"), art=read("BUYER-EVIDENCE-INVESTIGATION-UNPUBLISHED.md"), mat=JSON.parse(read("CLAIM-PROOF-RELEASE-GATES.json")), accept=read("CONVERSION-AND-CANONICAL-ACCEPTANCE.md");
function validate(a,b,m){
 assert.match(a,/data-variant="A"/);assert.match(b,/data-variant="B"/);
 for(const x of [a,b]){
 assert.match(x,/<html lang="en">/);assert.match(x,/<meta name="robots" content="noindex,nofollow">/);
 assert.match(x,/button type="button" disabled aria-describedby="commercial-reason"/);
 assert.match(x,/Affiliate disclosure \(prospective\):/);assert.match(x,/If you purchase through an approved link, Final Vestige may earn a commission at no additional cost to you/);
 assert.match(x,/account-issued destination/);assert.match(x,/https:\/\/finalvestige\.com\/focus\//);
 assert.doesNotMatch(x,/<script\b|<form\b|<iframe\b|<source\b|<video\b|autoplay|on[a-z]+\s*=|javascript:|http-equiv="refresh"/i);
 assert.doesNotMatch(x,/<a[^>]+href="https?:\/\/(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3|brainwaveshots|hypnosislive)\./i);
 assert.equal((x.match(/<button /g)||[]).length,1);
 assert.ok(x.indexOf('class="disclosure"')<x.indexOf('<button '));
 assert.ok(x.indexOf('<button ')-x.indexOf('class="disclosure"')<650);
 }
 assert.doesNotMatch(a,/class="film"/);assert.match(b,/class="film"/);
 assert.match(b,/<details>/);assert.match(b,/<summary>/);assert.match(b,/<svg /);assert.match(b,/<desc id="poster-desc"/);
 const times=[...b.matchAll(/<time>(\d\d):(\d\d)–(\d\d):(\d\d)<\/time>/g)].map(x=>[+x[1]*60+(+x[2]),+x[3]*60+(+x[4])]);
 assert.equal(times.length,7);
 for(let i=0;i<times.length;i++){assert.ok(times[i][1]>times[i][0]);if(i) assert.equal(times[i][0],times[i-1][1]);}
 assert.equal(times[0][0],0); assert.equal(times.at(-1)[1],42);
 const removeFilm=s=>s.replace(/<section class="film"[\s\S]*?<\/section>/,"");
 assert.equal(removeFilm(b).replace('data-variant="B"','data-variant="A"').replace('UNPUBLISHED B','UNPUBLISHED A'),a);
 assert.equal(m.authorization_gates.length,16);assert.ok(m.authorization_gates.every(g=>g.status==="HARD_HOLD"));
 assert.ok(m.sources.every(s=>/^https:\/\//.test(s.url)));
 const ids=new Set(m.sources.map(s=>s.id));
 assert.ok(m.claims.every(c=>c.source_ids.every(id=>ids.has(id))));
 assert.ok(Object.values(m.measured).every(v=>v===null));assert.equal(m.status.live,false);
}
validate(A,B,mat);
assert.ok(art.length>8500);assert.match(art,/PLOS ONE/);assert.match(accept,/NOT_COMPUTABLE/);
let negatives=0;
const bad=(mutate)=>{const [a,b,m]=mutate(A,B,structuredClone(mat));assert.throws(()=>validate(a,b,m));negatives++};
bad((a,b,m)=>[a.replace(" disabled aria-describedby"," aria-describedby"),b,m]);
bad((a,b,m)=>[a,b.replace(" disabled aria-describedby"," aria-describedby"),m]);
bad((a,b,m)=>[a.replace("Affiliate disclosure (prospective):","ADVERTISEMENT:"),b,m]);
bad((a,b,m)=>[a,b.replace("Affiliate disclosure (prospective):","ADVERTISEMENT:"),m]);
bad((a,b,m)=>[a.replace("Final Vestige may earn a commission","Final Vestige never earns commission"),b,m]);
bad((a,b,m)=>[a,b.replace("<details>","<article>"),m]);
bad((a,b,m)=>[a,b.replace("00:36–00:42","00:36–00:43"),m]);
bad((a,b,m)=>[a.replace("</main>","<script src='https://example.com/tracker.js'></script></main>"),b,m]);
bad((a,b,m)=>[a,b.replace("</main>","<form><input></form></main>"),m]);
bad((a,b,m)=>[a.replace("<button ","<a href=\"https://zen12.com/hnp\" >Purchase</a><button "),b,m]);
bad((a,b,m)=>[a,b.replace("noindex,nofollow","index,follow"),m]);
bad((a,b,m)=>{m.authorization_gates[0].status="APPROVED";return[a,b,m]});
bad((a,b,m)=>{m.measured.net_revenue=500;return[a,b,m]});
bad((a,b,m)=>{m.sources[0].url="javascript:alert(1)";return[a,b,m]});
bad((a,b,m)=>{m.claims[0].source_ids.push("INVENTED");return[a,b,m]});
console.log("R253 baseline PASS; "+negatives+"/"+negatives+" adversarial mutations rejected; native Node static commercial guard only.");
