"use strict";
/**
 * Final Vestige Mind R299 fail-closed SOURCE safety test.
 * Run from repository root: node mind/r299/verify_r299.cjs
 * Offline, standard-library Node only, no network and no changes.
 * Fingerprints pin reviewed exact source. FNV64 is NOT a crypto signature.
 * Does not replace browser/WCAG, WordPress sanitizer, merchant or finance QA.
 */
const fs=require("node:fs");
const path=require("node:path");
const paths={
 article:"mind/r299/THE-PATIENT-THE-STUDY-COULD-NOT-ACCOUNT-FOR-UNPUBLISHED.md",
 guide:"mind/r299/CANONICAL-ZEN12-BUYER-GUIDE-COPY-AND-42S-STORYBOARD.md",
 matrix:"mind/r299/CLAIMS-SOURCES-OFFERS-AND-REVENUE-GATES.json",
 hub:"mind/r299/MIND-ARCHIVE-RESEARCH-ROOM-WP-HTML-CANDIDATE.html",
 dossier:"mind/r299/CREATOR-MATCH-ONE-OFFER-REVENUE-AND-RELEASE-ACCEPTANCE.md",
 A:"mind/r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html",
 B:"mind/r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html"
};
const pins={
  "article": "e23f348d15236e92",
  "guide": "3dd8926ec41a776b",
  "matrix": "ea12a8acae7a9390",
  "hub": "5ce4fa668194f20e",
  "dossier": "e31bafb29ab19c14",
  "A": "e0bbb529cff3f5e4",
  "B": "4b1b9fe38a5a89a1"
};
const fail=(message)=>{throw new Error(message)};
const ok=(v,message)=>{if(!v)fail(message)};
function fnv64(s){let h=0xcbf29ce484222325n;for(let i=0;i<s.length;i++){h^=BigInt(s.charCodeAt(i));h=(h*0x100000001b3n)&0xffffffffffffffffn}return h.toString(16).padStart(16,"0")}
const hosts=new Set(["finalvestige.com","www.ftc.gov"]);
function checkHub(s){
 ok(/<html\b[^>]*lang=["']en["']/i.test(s),"HTML_LANG");
 ok(/<meta[^>]*name=["']viewport["']/i.test(s),"HTML_VIEWPORT");
 ok(/<meta[^>]*name=["']robots["'][^>]*noindex/i.test(s),"HTML_UNPUBLISHED");
 ok(/<main\b[^>]*id=["']main["'][^>]*>/i.test(s)&&/<h1\b/i.test(s),"HTML_SEMANTICS");
 ok(/href=["']#main["']/i.test(s),"HTML_SKIP_LINK");
 ok(/prefers-reduced-motion/i.test(s)&&/@media\(max-width:760px\)/i.test(s),"HTML_RESPONSIVE");
 ok(!/<(?:script|iframe|form|base|link|img|picture|video|audio|source|object|embed|svg|template)\b/i.test(s),"HTML_UNSAFE_ELEMENT");
 ok(!/<meta\b[^>]*http-equiv\s*=\s*["']?refresh/i.test(s),"HTML_REDIRECT");
 ok(!/\b(?:src|srcset|poster|action|formaction|data-url|data-href|data-target)\s*=/i.test(s),"HTML_REMOTE_RESOURCE");
 ok(!/\b(?:on[a-z]+)\s*=|\baria-hidden\s*=\s*["']?true/i.test(s),"HTML_EVENT_OR_HIDDEN");
 ok(!/@import\b|url\s*\(|expression\s*\(|display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0(?:\s*[;}])/i.test(s),"HTML_HIDDEN_OR_REMOTE_CSS");
 ok(!/\\u0*03a|\\u0*02f|&(?:#x?[0-9a-f]+|colon|sol);/i.test(s),"HTML_OBFUSCATED_URL");
 ok(!/\bhref\s*=\s*[^"'\s>]/i.test(s),"HTML_UNQUOTED_HREF");
 for(const a of s.matchAll(/\bhref\s*=\s*(["'])(.*?)\1/gi)){
   const link=a[2];
   if(link[0]==="#"){ok(/^#[a-z][a-z0-9_-]*$/i.test(link),"HTML_FRAGMENT");continue}
   ok(/^https:\/\//.test(link),"HTML_NONHTTPS_LINK");
   const u=new URL(link);
   ok(hosts.has(u.hostname)&&!u.username&&!u.password&&!u.port&&!u.search&&!u.hash,"HTML_LINK_HOST_OR_PARAMS");
 }
 const buttons=[...s.matchAll(/<button\b[^>]*>/gi)];
 ok(buttons.length===1,"HTML_BUTTON_COUNT");
 const button=buttons[0];ok(/\sdisabled(?:\s|=|>)/i.test(button[0]),"HTML_BUY_BUTTON_ENABLED");
 ok(!/\b(?:href|onclick|formaction|data-url)\s*=/i.test(button[0]),"HTML_BUTTON_HAS_LINK");
 const prior=s.slice(Math.max(0,button.index-900),button.index);
 ok(/may earn a commission/i.test(prior)&&/Prospective affiliate disclosure/i.test(prior),"HTML_DISCLOSURE_ADJACENT");
 ok(!/<input\b/i.test(s),"HTML_EXTRA_SIGNUP");
 ok(/Text transcript and visual storyboard only/i.test(s)&&/No playable file/i.test(s),"HTML_FALSE_VIDEO");
 ok(/Merchant offer unavailable/.test(s)&&/approval pending/i.test(s),"HTML_COMMERCE_HOLD");
}
function validate(d,opt={}){
 for(const k of Object.keys(paths)){
  ok(typeof d[k]==="string"&&d[k].length>400,"MISSING_"+k);
  if(opt.pin!==false)ok(fnv64(d[k])===pins[k],"PIN_"+k);
 }
 const m=JSON.parse(d.matrix);
 ok(m.release_state==="UNPUBLISHED_HARD_HOLD","MATRIX_RELEASE");
 ok(m.sources.length===21&&m.claims.length===30&&m.gates.length===18&&m.offers.length===4&&m.creator_pathways.length===3,"MATRIX_COUNTS");
 const sourceIds=new Set(m.sources.map(x=>x.id));
 ok(sourceIds.size===21&&new Set(m.sources.map(x=>x.url)).size===21,"SOURCE_DISTINCT");
 for(const s of m.sources)ok(/^https:\/\//.test(s.url)&&s.limitation&&s.read_depth,"SOURCE_VERIFICATION");
 for(const c of m.claims)ok(c.source_ids.length&&c.source_ids.every(x=>sourceIds.has(x))&&c.decision&&c.reason,"CLAIM_SOURCE_"+c.id);
 ok(new Set(m.claims.map(x=>x.id)).size===30,"CLAIMS_UNIQUE");
 const decisions=Object.fromEntries(m.claims.map(c=>[c.id,c.decision]));
 for(const id of ["C02","C07","C09","C13","C14","C17","C18","C20","C22","C23","C25","C26","C27","C29","C30"])ok(decisions[id]==="OMIT","UNSUPPORTED_CLAIM_"+id);
 ok(m.gates.every(g=>g.status==="HARD_HOLD"&&g.evidence===null),"AFFILIATE_GATES");
 ok(new Set(m.gates.map(g=>g.id)).size===18,"AFFILIATE_GATES_IDS");
 ok(m.offers[0].id==="ZEN12"&&m.offers[0].affiliate_approved===false&&m.offers[0].earning_url===null&&m.offers[0].active_cta===false,"ZEN12_NOT_APPROVED");
 ok(m.offers[1].active_cta===false&&m.offers[2].active_cta===false,"OTHER_MERCHANTS_INACTIVE");
 ok(m.offers[3].id==="FOCUS_FIELDBOOK"&&m.offers[3].price_usd===0,"FREE_FOCUS_PRESERVED");
 ok(m.creator_pathways[0].asset_id==="zctcIECAZ2s"&&m.creator_pathways[0].merchant_bridge.startsWith("NO"),"ROSENHAN_NO_COMMERCE_JUMP");
 for(const c of m.creator_pathways.slice(1))ok(c.asset_id===null,"NO_FABRICATED_GROK_ID");
 const mm=m.measurement;
 for(const name of ["net_revenue_per_1000_qualified_humans","verified_orders","confirmed_commissions","qualified_human_sessions","refunds","fees","affiliate_clicks","confirmed_leads"])ok(mm[name]===null,"NO_FAKE_METRICS_"+name);
 ok(mm.no_duplicate_analytics===true&&mm.status==="UNINSTRUMENTED_PROPOSED_ONLY","NO_NEW_ANALYTICS");
 ok(m.release_approval.founder===false&&m.release_approval.partner===false&&m.release_approval.video_playable===false&&m.release_approval.affiliate_links_active===false,"FALSE_RELEASE_APPROVAL");
 checkHub(d.hub);
 ok(d.article.trim().split(/\s+/).length>=1900,"ARTICLE_DEPTH");
 for(const p of ["Rosenhan","Spitzer","Lando","Cahalan","Scull","1973","1976","2019","2023","cannot verify","not proof"]){
  ok(d.article.toLowerCase().includes(p.toLowerCase()),"ARTICLE_EVIDENCE_"+p);
 }
 ok(d.guide.trim().split(/\s+/).length>=1400,"BUYER_GUIDE_DEPTH");
 for(const p of ["twelve levels","48 MP3","one-year","affiliate","not established","Variant A","Variant B","42-second","not encoded video"]){
  ok(d.guide.toLowerCase().includes(p.toLowerCase()),"BUYER_RESTRICTION_"+p);
 }
 ok(d.dossier.includes("NOT COMPUTABLE")&&d.dossier.includes("mind_pilot_2026_11")&&d.dossier.includes("mind_proposed_2026_11"),"DATA_AND_CAMPAIGN_DRIFT");
 ok(d.dossier.includes("zctcIECAZ2s")&&d.dossier.includes("direct platform")&&d.dossier.includes("HARD HOLD"),"CREATOR_PROVENANCE");
 for(const k of ["A","B"])ok(d[k].includes("<html")&&d[k].includes("disabled"),"INHERITED_AB_"+k);
 return true;
}
const root=path.resolve(__dirname,"../..");
const load=()=>Object.fromEntries(Object.entries(paths).map(([k,p])=>[k,fs.readFileSync(path.join(root,p),"utf8")]));
const negative=[
 ["removed_disclosure","hub",s=>s.replace("may earn a commission","may receive payment"),"HTML_DISCLOSURE_ADJACENT"],
 ["enabled_purchase","hub",s=>s.replace('type="button" disabled','type="button"'),"HTML_BUY_BUTTON_ENABLED"],
 ["script","hub",s=>s.replace("</body>","<script>alert(1)</script></body>"),"HTML_UNSAFE_ELEMENT"],
 ["iframe","hub",s=>s.replace("</body>",'<iframe src="https://third.example"></iframe></body>'),"HTML_UNSAFE_ELEMENT"],
 ["form","hub",s=>s.replace("</body>",'<form><input></form></body>'),"HTML_UNSAFE_ELEMENT"],
 ["input","hub",s=>s.replace("</body>","<input></body>"),"HTML_EXTRA_SIGNUP"],
 ["meta_refresh","hub",s=>s.replace("</head>",'<meta http-equiv="refresh" content="0;url=https://bad.example"></head>'),"HTML_REDIRECT"],
 ["inline_event","hub",s=>s.replace('<main id="main">','<main id="main" onload="alert(1)">'),"HTML_EVENT_OR_HIDDEN"],
 ["css_import","hub",s=>s.replace("</style>",'@import url(https://tracker.example/x.css);</style>'),"HTML_HIDDEN_OR_REMOTE_CSS"],
 ["css_hide","hub",s=>s.replace("</style>",'.disclosure{display:none}</style>'),"HTML_HIDDEN_OR_REMOTE_CSS"],
 ["external_href","hub",s=>s.replace('href="https://finalvestige.com/focus/"','href="https://merchant.invalid/buy"'),"HTML_LINK_HOST_OR_PARAMS"],
 ["javascript_href","hub",s=>s.replace('href="https://finalvestige.com/focus/"','href="javascript:alert(1)"'),"HTML_NONHTTPS_LINK"],
 ["unquoted_href","hub",s=>s.replace('href="https://finalvestige.com/focus/"','href=https://finalvestige.com/focus/'),"HTML_UNQUOTED_HREF"],
 ["remote_img","hub",s=>s.replace("</body>",'<img src="https://merchant.invalid/pixel"></body>'),"HTML_UNSAFE_ELEMENT"],
 ["missing_accessibility","hub",s=>s.replace('href="#main"','href="#wrong"'),"HTML_SKIP_LINK"],
 ["false_playable","hub",s=>s.replace("No playable file","A playable file"),"HTML_FALSE_VIDEO"],
 ["source_tamper","matrix",s=>s.replace("https://zen12.com/getstarted","https://zen12.com/altered"),"PIN_matrix"],
 ["false_account_approval","matrix",s=>s.replace('"affiliate_approved": false','"affiliate_approved": true'),"ZEN12_NOT_APPROVED"],
 ["fake_earning_url","matrix",s=>s.replace('"earning_url": null','"earning_url": "https://bad.invalid/affiliate"'),"ZEN12_NOT_APPROVED"],
 ["gate_open","matrix",s=>s.replace('"status": "HARD_HOLD"','"status": "PASS"'),"AFFILIATE_GATES"],
 ["fake_order","matrix",s=>s.replace('"verified_orders": null','"verified_orders": 1'),"NO_FAKE_METRICS_verified_orders"],
 ["fake_commission","matrix",s=>s.replace('"confirmed_commissions": null','"confirmed_commissions": 100'),"NO_FAKE_METRICS_confirmed_commissions"],
 ["fake_grok_id","matrix",s=>s.replace('"asset_id": null','"asset_id": "fictional"'),"NO_FABRICATED_GROK_ID"],
 ["false_research","article",s=>s.replace("not proof that its subject never existed","proof that its subject never existed"),"PIN_article"],
 ["alter_buyer","guide",s=>s.replace("not established by independently reviewed","established by independently reviewed"),"PIN_guide"],
 ["alter_original_A","A",s=>s+" manipulated","PIN_A"],
 ["alter_original_B","B",s=>s+" manipulated","PIN_B"]
];
function run(){
 const actual=load();validate(actual);let passed=0;
 for(const [name,key,mutate,code] of negative){
  const modified={...actual,[key]:mutate(actual[key])};
  ok(modified[key]!==actual[key],"MUTATION_DID_NOT_CHANGE_"+name);
  let thrown=null;
  try{validate(modified,{pin:(key==="hub"||(key==="matrix"&&name!=="source_tamper"))?false:true})}catch(e){thrown=e.message}
  // Where pin is off for structure attacks, require the intended relevant guard.
  ok(thrown&&(thrown===code||((key==="hub"||key==="matrix")&&thrown.startsWith(code))),"MUTATION_NOT_CAUGHT_"+name+":"+thrown);
  passed++;
 }
 console.log(JSON.stringify({status:"PASS",files:Object.keys(paths).length,sources:21,claims:30,holds:18,negative_rejected:passed,mode:"offline_node_source_only",browser_qa:"NOT_TESTED",wordpress:"NOT_TESTED",merchant:"NOT_VERIFIED"},null,2));
}
if(require.main===module)run();
module.exports={validate,checkHub,fnv64};
