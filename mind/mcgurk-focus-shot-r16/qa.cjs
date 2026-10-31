/* Final Vestige Mind R16: reproducible static source audit; not a browser or WordPress test.
 * Run: node mind/mcgurk-focus-shot-r16/qa.cjs
 * Run mutation checks: node mind/mcgurk-focus-shot-r16/qa.cjs --mutation
 * API: module.exports = { audit, mutationalChecks }
 */
(function () {
  "use strict";
  function audit(html, guide, raw, protocol) {
    const checks = [];
    function check(name, ok) { checks.push({ name: name, pass: !!ok }); }
    let data;
    try { data = typeof raw === "string" ? JSON.parse(raw) : raw; } catch (err) { data = null; }
    const H = typeof html === "string" ? html : "";
    const G = typeof guide === "string" ? guide : "";
    const P = typeof protocol === "string" ? protocol : "";
    const D = data || {};
    const srcs = Array.isArray(D.sources) ? D.sources : [];
    const claims = Array.isArray(D.claims) ? D.claims : [];
    const offer = D.current_offer || {};
    const cmb = D.commerce_block || {};
    const text = H.replace(/<style[\s\S]*?<\/style>/gi," ").replace(/<[^>]*>/g," ").replace(/&(?:amp|nbsp|lt|gt);/g," ");
    check("HTML exists and substantial >17k", H.length > 17000);
    check("Guide exists and substantive >9k", G.length > 9000);
    check("Protocol exists and substantive >6k", P.length > 6000);
    check("Matrix valid JSON schema", !!data && D.schema_version === "1.0.0");
    check("Correct owner Issue 171", D.owner_issue === 171);
    check("Release state explicit HOLD", D.release_state === "UNPUBLISHED_HOLD");
    check("Exactly 61 existing posts checked read-only", D.existing_site && D.existing_site.published_investigations_read === 61);
    check("Puységur real page id", D.existing_site && D.existing_site.puysegur_page_id === 1377);
    check("Focus real page id", D.existing_site && D.existing_site.focus_page_id === 1579);
    check("No claimed live Mind hub", D.existing_site && D.existing_site.published_mind_hub === false);
    check("No added Jetpack list", D.existing_site && D.existing_site.duplicate_jetpack_form_added === false);
    check("49 distinct evidence claim decisions", claims.length === 49 && new Set(claims.map(c=>c.id)).size===49);
    check("20 distinct source records", srcs.length===20 && new Set(srcs.map(s=>s.id)).size===20);
    check("Every source exact HTTPS URL", srcs.every(s=> /^https:\/\//.test(s.url)));
    check("Source roles populated", srcs.every(s=>s.title && s.type && s.checked_on==="2026-10-31"));
    check("No empty disposition entries", claims.every(c=>typeof c.disposition==="string" && c.disposition.length>2));
    check("All live external editorial anchors in source ledger", (()=>{const allowed=new Set(srcs.map(x=>x.url));return [...H.matchAll(/<a\b[^>]*href=["'](https:\/\/[^"']+)["']/g)].every(m=>allowed.has(m[1]));})());
    check("Claim references resolve or legitimately empty", claims.every(c=>Array.isArray(c.source_ids) && c.source_ids.every(id=>srcs.some(s=>s.id===id))));
    check("Every claim has publisher safe-copy boundary", claims.every(c=>typeof c.copy_limit==="string" && c.copy_limit.length>3));
    check("Exact Focus Shot not conflated with general catalog",offer.exact_sku === "Focus Shot" && offer.actual_seller_page === "https://brainwaveshots.com/focus-shot");
    check("Current merchant includes official FAQ", offer.seller_faq === "https://brainwaveshots.com/faq");
    check("Partner acceptance false", offer.affiliate_account_accepted === false);
    check("Specific SKU eligibility not assumed", offer.sku_eligibility_verified === false);
    check("Approved link is null", offer.affiliate_earning_url === null);
    check("Tracking rights not assumed", offer.tracking_terms_verified === false);
    check("Merchant creative rights not assumed", offer.authorized_creative_verified === false);
    check("Social promotion permission not assumed", offer.authorized_social_promotion === false);
    check("Opt-in email permission not assumed", offer.authorized_opted_in_email_promotion === false);
    check("No claim of personal product trial", offer.firsthand_product_tested === false);
    check("No claim of audio-signal analysis", offer.product_signal_analyzed === false);
    check("No unverified fixed product price", offer.price_quoted === false);
    check("No invented refund promise", offer.refund_promise_made === false);
    check("No outbound measurement activated", offer.outbound_tracking_enabled === false);
    check("Commercial CTA explicitly disabled in JSON", cmb.cta_disabled === true && cmb.cta_href === null && cmb.merchant_recommendation_active === false);
    check("Commission disclosure specific and intelligible", /Final Vestige may earn a commission at no additional cost to you/.test(cmb.near_CTA_disclosure));
    check("HTML contains no merchant anchor", !/<a\b[^>]*href\s*=\s*["']https:\/\/(?:www\.)?(?:brainwaveshots\.com|inspire3\.com|zen12\.com|affiliates\.inspire3\.com)/i.test(H));
    check("HTML contains no checkout redirect anchor", !/<a\b[^>]*href\s*=\s*["'][^"']*(?:getstarted|checkout|buy-now|add-to-cart)/i.test(H));
    check("No embedded scripts", !/<script\b/i.test(H));
    check("No iframe or object embed", !/<(?:iframe|object|embed)\b/i.test(H));
    check("No new signup or payment forms", !/<form\b/i.test(H));
    check("No inline event handlers", !/\son(?:click|load|error|submit|pointerdown|mouseover)\s*=/i.test(H));
    check("No third-party ad pixel image", !/<img\b/i.test(H));
    check("No video element before approved media assets", !/<video\b/i.test(H));
    check("No tracking data in article", !/(?:\bgtag\s*\(|\bfbq\s*\(|google-analytics|pixel\.facebook|dataLayer\.push|navigator\.sendBeacon|localStorage\.)/i.test(H));
    check("Inactivated commerce control visible", /<button\b[^>]*\sdisabled(?:\s|>)[^>]*>Product link unavailable/i.test(H));
    const near = H.match(/<p class="disclosure">([\s\S]{30,450}?)<\/p>\s*<button\b([^>]*)>/i);
    check("Disclosure immediately precedes CTA", !!near && /Final Vestige may earn a commission at no additional cost to you/.test(near[1]) && /(?:^|\s)disabled(?:\s|$)/.test(near[2]));
    check("Article scope properly titled", /<section class="fvm16" aria-labelledby="fvm16-title">/.test(H) && /<h1 id="fvm16-title">/.test(H));
    check("No duplicate heading IDs", /<h1 id="fvm16-title">/.test(H) && (H.match(/<h1\b/g)||[]).length===1);
    check("Internal fragment destinations all exist", [...H.matchAll(/href="#(fvm16-[\w-]+)"/g)].every(m=>H.indexOf('id="'+m[1]+'"')>=0));
    check("Unique HTML IDs", (()=>{const ids=[...H.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);return ids.length===new Set(ids).size;})());
    check("Explicit source list section", /<section class="chapter" id="fvm16-sources">/.test(H));
    check("At least 18 article citation IDs", (H.match(/<li id="fvm16-s\d+"/g)||[]).length>=18);
    check("No-JS perception schematic", /<figure class="scene"/.test(H) && /not an audiovisual stimulus/i.test(H));
    check("Free nonclinical independent exercise", /id="fvm16-practice"/.test(H) && /not a psychological diagnostic/i.test(H));
    check("Distinguishes binaural from isochronic", /isochronic/i.test(text) && /binaural/i.test(text));
    check("Explains result not product validation", /not trials of hypnosis, neuroacoustic products/i.test(text));
    check("Merchant reviewed rather than recommended", /Separately labeled commercial review/i.test(text));
    check("Puységur live direct link", /href="https:\/\/finalvestige\.com\/free-resources\/puysegurs-animal-magnetism-files\/"/.test(H));
    check("Focus existing real route", /href="https:\/\/finalvestige\.com\/focus\/"/.test(H));
    check("Media query for narrow viewport", /@media\(max-width:720px\)/.test(H));
    check("Reduced-motion compliance provisions", /prefers-reduced-motion:reduce/.test(H));
    check("Forced colors provision", /forced-colors:active/.test(H));
    check("Visible focus-state CSS provision", /:focus-visible/.test(H));
    check("Mobile content spacing", /\.wrap\{padding:0 18px\}/.test(H));
    check("Native expanders without JS", /<details><summary>/.test(H));
    check("No fabricated psychological test", /not a validated test/i.test(H));
    check("No fake claims of personal purchase or tests", !/we (?:purchased|listened to|tested) (?:Focus Shot|Zen12)/i.test(H+" "+G));
    check("No fake medical, money, sales guarantees", !/Final Vestige guarantees (?:health|wealth|focus|concentration|results)/i.test(H+" "+G));
    check("Explicit seller claim separation", /seller-reported specifications/i.test(H));
    check("Risk/epilepsy addressed", /epilepsy/i.test(H) && /epilepsy/i.test(G));
    check("2019 review is not exact SKU proof", /not a product endorsement/i.test(H) && /not a product endorsement/i.test(G));
    check("Buyer guide links exact official SKU", /https:\/\/brainwaveshots\.com\/focus-shot/.test(G));
    check("Buyer guide openly discloses no personal trial", /not downloaded, listened to, analyzed, or personally tested/i.test(G));
    check("Buyer guide has free alternative", /Set a fifteen-minute timer/i.test(G));
    check("Guide includes near-CTA conditional disclosure", /Final Vestige may earn a commission at no additional cost to you/.test(G));
    check("Film A/B comparison laid out", /A = text only/.test(P) && /B = same text plus optional film/.test(P));
    check("Video not hosted or asserted ready", /UNHOSTED/.test(P) && /No fake player/i.test(P));
    check("Portrait integrity record present", /c4cb33fef60dfa773e65a46b9167c0581e58cf07f09c42b744f90c60af48ebbc/.test(P));
    check("Caption integrity record present", /5924d265a8081acbef9d1599a012bae75e71096e4f60e2f17511e96a5422785d/.test(P));
    check("No autoplay in proposed video markup", /<video controls playsinline preload="none"/.test(P) && !/<video[^>]*\bautoplay/i.test(P));
    check("Transcript is required in design", /Full visual transcript/.test(P));
    check("No-JS requirements in protocol", /without JavaScript/.test(P));
    check("Privacy collection disabled by default", /analytics_enabled false/.test(P));
    check("A/B uplift expressly unclaimed", /do not claim uplift/i.test(P));
    check("No extra newsletter stack", /No duplicate list/i.test(P));
    check("Main branch homepage freeze clearly recognized", /PR #49/.test(P) && /PR #172/.test(P));
    check("Dispatch separate and unsent", /Dispatch #174/.test(P) && /no email draft edits/i.test(P));
    check("Publication and affiliate approval required", /founder separate publishing and commerce/i.test(P));
    // Contrast math checks: source palette, not browser computed colors.
    function luminance(hex) {
      const channels = hex.match(/\w\w/g).map(x=>parseInt(x,16)/255).map(x=>x<=.04045?x/12.92:Math.pow((x+.055)/1.055,2.4));
      return .2126*channels[0]+.7152*channels[1]+.0722*channels[2];
    }
    function ratio(a,b){ const L=[luminance(a),luminance(b)].sort((a,b)=>b-a);return (L[0]+.05)/(L[1]+.05); }
    const pairs=[
      ["f4efe6","090a0a"], ["d8d2c7","090a0a"], ["b6afa4","090a0a"],
      ["c7a66c","090a0a"], ["d8d2c7","101111"], ["f4efe6","151615"],
      ["f3e6cd","151510"], ["e6d8be","34312b"]];
    pairs.forEach((p,i)=>check("Static palette WCAG normal text contrast "+(i+1), ratio(p[0],p[1])>=4.5));
    return {passed:checks.filter(c=>c.pass).length, total:checks.length, failures:checks.filter(c=>!c.pass).map(c=>c.name), checks:checks};
  }
  function mutationalChecks(html,guide,raw,protocol) {
    const f = [{name:"merchant checkout URL",i:0,a:"<button type=\"button\" disabled",b:"<a href=\"https://brainwaveshots.com/focus-shot\">Buy now</a><button type=\"button\" disabled"},
      {name:"lost finance disclosure",i:0,a:"If you eventually purchase through an approved link on this page, Final Vestige may earn a commission at no additional cost to you.",b:""},
      {name:"enabled CTA",i:0,a:"<button type=\"button\" disabled",b:"<button type=\"button\""},
      {name:"script injection",i:0,a:"<article>",b:"<script>fetch('/track')</script><article>"},
      {name:"new signup",i:0,a:"<article>",b:"<form><input type=\"email\"></form><article>"},
      {name:"tracking pixel",i:0,a:"<article>",b:"<img src=\"https://tracker.example/pixel\"><article>"},
      {name:"fake video",i:0,a:"<article>",b:"<video autoplay src=\"fake.mp4\"></video><article>"},
      {name:"missing first party Focus link",i:0,a:'href="https://finalvestige.com/focus/"',b:'href="https://invalid.local/"'},
      {name:"missing Puységur link",i:0,a:'href="https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"',b:'href="https://invalid.local/"'},
      {name:"missing reduced motion",i:0,a:"prefers-reduced-motion:reduce",b:"deleted-motion-rule"},
      {name:"invalid source fragment",i:0,a:'id="fvm16-s1"',b:'id="broken-s1"'},
      {name:"duplicated heading id",i:0,a:'<h1 id="fvm16-title">',b:'<h1 id="fvm16-title"><span id="fvm16-title">'},
      {name:"fictitious approval",i:2,change:d=>{d.current_offer.affiliate_account_accepted=true}},
      {name:"insert fabricated earning link",i:2,change:d=>{d.current_offer.affiliate_earning_url="https://example.invalid/offer"}},
      {name:"unapproved analytics toggle",i:2,change:d=>{d.current_offer.outbound_tracking_enabled=true}},
      {name:"unverified seller verdict",i:2,change:d=>{d.current_offer.firsthand_product_tested=true}},
      {name:"unsupported universal claim",i:0,a:"</article>",b:"<p>Final Vestige guarantees concentration results.</p></article>"},
      {name:"missing video proof",i:3,a:"UNHOSTED",b:"HOSTED"}];
    const originals=[html,guide,JSON.parse(raw),protocol];
    return f.map(m=>{
      const copy=originals.map((x,i)=>i===2?JSON.parse(JSON.stringify(x)):x);
      if(m.change) m.change(copy[m.i]); else { if(!copy[m.i].includes(m.a)) return {name:m.name,caught:false,reason:"mutation input absent"}; copy[m.i]=copy[m.i].replace(m.a,m.b); }
      const result=audit(copy[0],copy[1],copy[2],copy[3]);
      return {name:m.name,caught:result.failures.length>0,failures:result.failures.slice(0,3)};
    });
  }
  if(typeof module!=="undefined"){module.exports={audit,mutationalChecks};}
  if (typeof require === "function" && typeof module !== "undefined" && require.main === module) {
    const fs=require("fs"),path=require("path");const folder=__dirname;
    const inputs=["wordpress-draft.html","focus-shot-evidence-guide.md","claims-and-product-evidence.json","conversion-video-measurement-protocol.md"].map(x=>fs.readFileSync(path.join(folder,x),"utf8"));
    const r=audit(...inputs); console.log("Source QA "+r.passed+"/"+r.total,r.failures);
    let failed=r.failures.length>0;
    if(process.argv.includes("--mutation")){const m=mutationalChecks(...inputs);const caught=m.filter(x=>x.caught).length;console.log("Mutations "+caught+"/"+m.length);m.filter(x=>!x.caught).forEach(x=>console.log("NOT CAUGHT",x));failed=failed||caught!==m.length;}
    process.exitCode=failed?1:0;
  }
})();