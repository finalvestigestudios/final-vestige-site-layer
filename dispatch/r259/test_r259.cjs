"use strict";
const fs = require("node:fs");
const path = require("node:path");
const base = __dirname;
const read = p => fs.readFileSync(path.join(base,p),"utf8");
const md=read("ISSUE04_OPTIONAL.md"), txt=read("ISSUE04_PREVIEW.txt"), html=read("ISSUE04_PREVIEW.html"), doc=read("SOURCE_AND_CONVERSION_REVIEW.md"), snapshot=JSON.parse(read("HOLD_SNAPSHOT.json"));
function ensure(c,msg){if(!c)throw new Error(msg);}
const cases=[
["standalone original preserved",()=>ensure(md.includes("NOT ADOPTED") && !md.includes("Subject:** Fourteen seconds"),"replacement")],
["precise non-deceptive subject",()=>ensure(md.includes("Apollo 1: the failure wasn't just a spark")&&txt.includes("SUBJECT: Apollo 1: the failure wasn't just a spark")&&html.includes("Apollo 1: the failure wasn't just a spark"),"subject")],
["preheader parity",()=>ensure(md.includes("NASA's investigators reconstructed a chain")&&txt.includes("PREHEADER: NASA's investigators reconstructed")&&html.includes("NASA's investigators reconstructed"),"preheader")],
["one CTA",()=>ensure((html.match(/href="https:\/\/finalvestige\.com/g)||[]).length===1,"one FV CTA")],
["primary NASA full citations",()=>ensure(["/Apollo204/find.html","/Apollo204/seamans3.html","sma.nasa.gov/sma-disciplines/accllp/apollo-1"].every(s=>md.includes(s)&&txt.includes(s)&&html.includes(s)),"sources")],
["no false certainty",()=>ensure(md.includes("did not conclusively identify a single ignition source")&&md.includes("most probable initiator"),"uncertainty")],
["two observed timings caveated",()=>ensure(md.includes("23:30:55 GMT")&&md.includes("6:31:04")&&md.includes("6:31:19")&&md.includes("not an exact clock for ignition"),"timing")],
["legal footer intentionally cannot pass",()=>ensure([md,html,txt].every(s=>s.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]")&&s.includes("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]")),"incomplete footer")],
["no merchant promotion in this editorial",()=>ensure(!/href="https:\/\/(?:zen12|hypnosislive|affiliates\.inspire3)/.test(html),"merchant link")],
["no sending or credentials",()=>ensure([md,html,txt,doc].every(s=>!s.includes("mailto:")&&!s.includes("api_key=")),"send path")],
["commercial rights remain all false",()=>ensure(["affiliate_named_acceptance","email_promotion_permission","issued_earning_url","warmup_guides_published_approved","merchant_exact_price_verified_at_checkout"].every(k=>snapshot[k]===false),"merchant")],
["subscriber counts remain nonadditive",()=>ensure(snapshot.wordPress_diagnostic.nonadditive===true&&snapshot.provider_subscribed_aggregate===false,"subscribers")],
["real preview not mistaken for static specimen",()=>ensure(snapshot.native_wordpress_email_preview===false&&html.includes("NOT JETPACK-RENDERED"),"preview")],
["net sales not inferred",()=>ensure(snapshot.settled_revenue_verification===false&&snapshot.net_revenue_per_1000_qualified_sessions===null,"money")],
["preserve six-issue guardrails",()=>ensure(snapshot.release==="HOLD_UNSENT"&&snapshot.commercial_03_05==="HOLD_MERCHANT"&&snapshot.issue04_variant==="OPTIONAL_NOT_ADOPTED","hold")],
["seller paths separate",()=>ensure(snapshot.source_documents.zen12_standard!==snapshot.source_documents.zen12_coupon_distinct,"offers")],
["no urgency copying",()=>ensure(!/buy now before|limited-time offer|only \d+ minutes left/i.test([md,html,txt].join(" ")),"urgency")],
["full explicit source ledger",()=>ensure(Object.keys(snapshot.source_documents).length>=7 && doc.includes("https://www.ftc.gov/"),"ledger")]
];
let passed=0;for(const [name,fn] of cases){fn();passed++;}console.log("R259 PASS "+passed+"/"+cases.length+" offline invariants; NOT a delivery/merchant-authorization or legal test.");
