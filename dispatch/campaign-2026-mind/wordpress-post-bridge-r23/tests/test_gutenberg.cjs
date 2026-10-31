"use strict";
/* No-send candidate tests; use: node tests/test_gutenberg.cjs */
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const bridge=require("../build_native_candidates.cjs");
const root=path.resolve(__dirname,"../..");
const m=JSON.parse(fs.readFileSync(path.join(root,"manifest.json"),"utf8"));
const rows=m.issues.map((x,i)=>bridge.adapt(x,fs.readFileSync(path.join(root,"issues",String(i+1).padStart(2,"0")+"-"+x.slug+".md"),"utf8")));
let count=0;function ok(x,msg){assert.ok(x,msg);count++}
ok(rows.length===6,"six source editions");ok(m.mix.editorial===4&&m.mix.commercial_review_pending===2,"4:2");
for(let i=0;i<6;i++){
 const r=rows[i],src=fs.readFileSync(path.join(root,"issues",String(i+1).padStart(2,"0")+"-"+m.issues[i].slug+".md"),"utf8");
 ok(r.issue===i+1,"edition order");ok(r.post_title===m.issues[i].subject,"subject matches");
 ok(r.preheader_unverified===m.issues[i].preheader,"preheader label accurate");
 ok(!r.post_created&&!r.send_to_subscribers&&!r.release_ready,"held");
 ok(!r.legal_footer_proven&&!r.unsubscribe_proven&&!r.actual_native_email_preview,"no false legal/email proof");
 ok(r.blocks_html.includes("DO NOT PUBLISH OR EMAIL"),"visible hold");ok(r.blocks_html.includes("<!-- wp:paragraph -->"),"WordPress blocks");
 ok(!r.blocks_html.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]"),"legal token not publishable");
 ok(!/javascript:|<script|\bdata:|utm_source=/i.test(r.blocks_html),"no script/tracking");
 if(r.issue===3||r.issue===5){
  ok(r.blocks_html.includes("Commercial disclosure:"),"disclosure kept");ok(r.blocks_html.includes("GUIDE NOT LIVE — NO LINK"),"no live guide");
 }else ok(r.blocks_html.includes('href="'+m.issues[i].editorial_cta+'"'),"editorial CTA");
}
const source=(i)=>fs.readFileSync(path.join(root,"issues",String(i).padStart(2,"0")+"-"+m.issues[i-1].slug+".md"),"utf8");
for(const bad of [
 ()=>bridge.inl("<img src=x onerror=alert(1)>"),
 ()=>bridge.inl("[link](javascript:alert(1))"),
 ()=>bridge.inl("[link](http://example.com)"),
 ()=>bridge.inl("[link](https://affiliates.inspire3.com/a)"),
 ()=>bridge.adapt({...m.issues[2],publish_state:"publish"},source(3)),
 ()=>bridge.adapt({...m.issues[2],merchant_affiliate_url:"https://merchant.example/"},source(3)),
 ()=>bridge.adapt(m.issues[2],source(3).replace("Commercial disclosure:","Marketing note:")),
 ()=>bridge.adapt(m.issues[0],source(1).replace("[[VALID_POSTAL_ADDRESS_REQUIRED]]","REMOVED")),
 ()=>bridge.adapt(m.issues[0],source(1).replace("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]","REMOVED")),
 ()=>bridge.adapt(m.issues[0],source(1).replace("**Subject:** The mind is not a camera","**Subject:** Fake urgency"))
]){
 assert.throws(bad);count++;
}
assert.doesNotThrow(()=>bridge.compile(false));count++;
const page=fs.readFileSync(path.resolve(__dirname,"../proofs/OFFLINE_POST_REVIEW.html"),"utf8");
ok((page.match(/<article /g)||[]).length===6,"six accessible preview cards");
ok(page.includes('lang="en"')&&page.includes("NOT A WORDPRESS EMAIL PREVIEW"),"offline scope explicit");
const ledger=JSON.parse(fs.readFileSync(path.resolve(__dirname,"../proofs/RELEASE_COMPATIBILITY.json"),"utf8"));
ok(ledger.sent_emails===0&&ledger.created_posts===0&&ledger.live_wordpress_format==="excerpt","no delivery claimed");
console.log(count+" read-only Gutenberg candidate guard assertions passed; NO send/WordPress claims");
