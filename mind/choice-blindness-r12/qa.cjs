#!/usr/bin/env node
"use strict";
const fs=require("node:fs"),p=require("node:path");
function check(input){let tests=[],t=(name,ok)=>tests.push({name,ok:!!ok}),{html,article,claims,plan,measurement}=input;
t("Original source investigation >=2000 words",article.trim().split(/\s+/).length>=2000);
t("Complete WordPress candidate >14000 bytes",html.length>14000);
t("One article landmark",/<article class="fv-r12"/.test(html)&&!/<main\b/i.test(html));
t("Exactly one H1",(html.match(/<h1\b/g)||[]).length===1);
t("No scripts, forms, iframe or autoplay",!/<script\b|<form\b|<iframe\b|autoplay/i.test(html));
t("No active merchant links",!/href=["'][^"']*(zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i.test(html));
t("Affiliate disclosure adjacent to disabled offer",/fv-r12__commerce[\s\S]*Affiliate disclosure:[\s\S]{0,450}fv-r12__disabled/.test(html));
t("Offer not anchor",html.includes('<span class="fv-r12__disabled" role="status">'));
t("Live Focus route",html.includes('href="https://finalvestige.com/focus/"'));
t("Historical archive route",html.includes('href="https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"'));
t("Editorial and disclosure route",html.includes("https://finalvestige.com/editorial-standards/")&&html.includes("https://finalvestige.com/affiliate-disclosure/"));
t("References linked",html.includes('id="fv-r12-source-3"')&&html.includes('href="#fv-r12-source-3"'));
let ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);t("Unique IDs",ids.length===new Set(ids).size);
t("Keyboard focus, responsive and reduced motion",html.includes(":focus-visible")&&html.includes("max-width:390px")&&html.includes("prefers-reduced-motion:reduce"));
t("No analytics scripts or second list",!/gtag\(|google-analytics|facebook\.com\/tr|sendBeacon\(/i.test(html));
t("40 dispositioned claims",claims.claims.length>=40);
t("Claim sources defined",claims.claims.every(c=>claims.sources[c.source]?.url===c.source_url));
t("No partner approval or invented link",!claims.partner_approved&&claims.affiliate_url===null);
t("Unsupported efficacy rejected",claims.claims.some(x=>x.claim.includes("12 minutes equals")&&x.disposition==="unsupported-seller-claim"));
t("Quantitative study distinction",article.includes("69%")&&article.includes("53%"));
t("Evidence 2005 2010 2012",article.includes("2005")&&article.includes("2010")&&article.includes("2012"));
t("Video script is concept only",plan.includes("NOT produced"));
t("Tracking disabled",measurement.enabled===false&&measurement.affiliate_approval===false);
t("PII excluded",measurement.disallowed_fields.includes("ip")&&measurement.disallowed_fields.includes("email")&&measurement.disallowed_fields.includes("full_referrer"));
t("No bogus published Mind href",!/href=["']https:\/\/finalvestige\.com\/mind\//.test(html));
return {passed:tests.filter(x=>x.ok).length,failed:tests.filter(x=>!x.ok).map(x=>x.name),tests};}
function load(){return {html:fs.readFileSync(p.join(__dirname,"page.wp.html"),"utf8"),article:fs.readFileSync(p.join(__dirname,"investigation.md"),"utf8"),claims:JSON.parse(fs.readFileSync(p.join(__dirname,"claims.json"),"utf8")),plan:fs.readFileSync(p.join(__dirname,"conversion-plan.md"),"utf8"),measurement:JSON.parse(fs.readFileSync(p.join(__dirname,"measurement-contract.json"),"utf8"))};}
if(require.main===module){let r=check(load());console.log(JSON.stringify(r,null,2));if(r.failed.length)process.exitCode=1;}
module.exports={check,load};