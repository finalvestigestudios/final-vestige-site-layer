"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {check}=require("./source_gate.cjs");const root=path.join(__dirname,"..");const m=JSON.parse(fs.readFileSync(path.join(root,"campaign-2026-mind/manifest.json"),"utf8"));
const s=m.issues.map((e,i)=>fs.readFileSync(path.join(root,"r429","issue_0"+(i+1)+"_wp_blocks.html"),"utf8"));
let n=0;const eq=(x,y)=>{assert.deepEqual(x,y);n++},bad=fn=>{assert.throws(fn);n++};const r=s.map((x,i)=>check(i+1,x,m.issues[i]));
eq(r.length,6);eq(r.filter(x=>x.kind==="editorial").length,4);eq(r.filter(x=>x.kind!=="editorial").length,2);
for(const x of r){eq(x.status,"HOLD_UNSENT");eq(x.send_authorized,false);eq(x.real_source_first_paragraph.startsWith("EDITORIAL HOLD"),true);eq(x.actual_jetpack_preview_verified,false);eq(x.source_footer_hardstop,true);}
eq(r[0].first_party_hrefs[0],r[1].first_party_hrefs[0]);eq(r[3].risk,"FACTUAL_SUBJECT_HOLD");eq(r[5].risk,"REPEAT_SIGNUP_RISK");
bad(()=>check(1,s[0].replace("EDITORIAL HOLD — DO NOT PUBLISH OR EMAIL.","READY"),m.issues[0]));
bad(()=>check(2,s[1].replace("[[VALID_POSTAL_ADDRESS_REQUIRED]]",""),m.issues[1]));
bad(()=>check(3,s[2].replace("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",""),m.issues[2]));
bad(()=>check(4,s[3].replace("</p><!-- /wp:paragraph -->","</p><!-- /wp:paragraph --><script>unsafe</script>"),m.issues[3]));
bad(()=>check(5,s[4].replace("https://finalvestige.com/free-resources/","https://merchant.invalid/free-resources/"),m.issues[4]));
bad(()=>check(6,s[5].replace("PRE-SEND BLOCKER","READY"),m.issues[5]));
bad(()=>check(3,s[2],{...m.issues[2],merchant_affiliate_url:"https://merchant.invalid/ref"}));
bad(()=>check(1,s[0],{...m.issues[0],number:2}));
console.log("PASS "+n+"/"+n+" native Node assertions when executed; HOLD_UNSENT");
