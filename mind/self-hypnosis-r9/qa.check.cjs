/* Final Vestige Mind R9 standalone source-and-safety QA.
 * No packages, no network, no WordPress writes.
 * Node: node mind/self-hypnosis-r9/qa.check.cjs
 * API: audit({ "feature.md":..., "page-self-hypnosis.html":..., "evidence.json":..., "conversion.md":...})
 */
(function(scope) {
  function audit(files) {
    const article=files["feature.md"]||"",html=files["page-self-hypnosis.html"]||"",
          plan=files["conversion.md"]||"",ledger=JSON.parse(files["evidence.json"]||"{}");
    const results=[];
    function test(name, ok) {results.push({name:name, pass:Boolean(ok)});}
    const count=(txt,fragment)=>txt.split(fragment).length-1;
    const ids=Array.from(html.matchAll(/\bid="([^"]+)"/g)).map(x=>x[1]);
    const offerPos=Array.from(html.matchAll(/class="inactive"/g)).map(x=>x.index);
    const disclosurePos=Array.from(html.matchAll(/class="disclosure"/g)).map(x=>x.index);
    const refs=ledger.sources||[], claims=ledger.claims||[];
    test("substantive original article >= 1900 words",article.trim().split(/\s+/).length>=1900);
    test("source list S1 through S13 present",Array.from({length:13},(_,i)=>article.includes("[S"+(i+1)+"]")).every(Boolean));
    test("published Puységur archive referenced",article.includes("Puységur")&&article.includes("https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"));
    test("1843 Braid historical source and boundary",article.includes("1843")&&article.includes("Braid")&&article.includes("Wellcome"));
    test("RCT summary 576 retrieved and 22 included",article.includes("576")&&article.includes("22")&&article.includes("randomized"));
    test("clinical methods access limitation clear",article.includes("complete article")&&article.includes("not"));
    test("NCCIH and sleep mixed evidence",article.includes("NCCIH")&&article.includes("47.7%")&&article.includes("29.5%"));
    test("self-hypnosis distinction from a recording",article.includes("independent")&&article.includes("recording")&&article.includes("skill"));
    test("seller specific Total Focus and Zen12 names",article.includes("Total Focus")&&article.includes("Zen12"));
    test("article clearly not testimonial",article.includes("has **not** personally tested")||article.includes("has **not** personally"));
    test("source ledger has >=13 official sources",refs.length>=13);
    test("ledger has >=30 claim dispositions",claims.length>=30);
    test("all row ids unique",new Set(claims.map(x=>x.id)).size===claims.length);
    test("all sources contain https URLs",refs.every(x=>/^https:\/\//.test(x.url)));
    test("all claims map to existing source IDs",claims.every(x=>x.decision&&x.sources.length&&x.sources.every(s=>refs.some(r=>r.id===s))));
    test("unsupported Total Focus claims rejected",claims.some(x=>x.claim.includes("Total Focus guarantees")&&x.decision==="reject"));
    test("unsupported Zen12 1hr in 12m claim rejected",claims.some(x=>x.claim.includes("12-minute Zen12 yields")&&x.decision==="reject"));
    test("no affiliate acceptance or link asserted",ledger.affiliate_approved===false&&ledger.affiliate_url===null);
    test("HTML is a standalone main landmark",html.includes('<main class="fvsh"')&&html.includes("</main>"));
    test("HTML single descriptive H1",count(html,"<h1")===1&&html.includes('id="fvsh-title"'));
    test("HTML 5+ semantic H2 sections",count(html,"<h2")>=5);
    test("no duplicated element ids",ids.length>5&&new Set(ids).size===ids.length);
    test("all in-page nav anchors resolve",Array.from(html.matchAll(/href="#([^"]+)"/g)).every(x=>ids.includes(x[1])));
    test("page-scoped class stylesheet",html.includes(".fvsh{")&&!/(^|[},\s])body\s*[{,:]/m.test(html));
    test("responsive columns collapse",html.includes("@media(max-width:780px)"));
    test("visible keyboard focus styles",html.includes(":focus-visible"));
    test("reduced motion and forced colors",html.includes("prefers-reduced-motion")&&html.includes("forced-colors:active"));
    test("five step nonclinical exercise",count(html,'<li><div><strong>Minute')>=4&&html.includes("nonclinical")&&html.includes("Stop if uncomfortable"));
    test("links to already published Focus and Puységur",html.includes('href="https://finalvestige.com/focus/"')&&html.includes('href="https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"'));
    test("includes editorial and affiliate standards routes",html.includes('href="https://finalvestige.com/editorial-standards/"')&&html.includes('href="https://finalvestige.com/affiliate-disclosure/"'));
    test("no extra email form",!/<form\b/i.test(html)&&!/(mailchimp|beehiiv|substack)/i.test(html));
    test("no unapproved mind guide link",!/<a[^>]*href="\/mind\//i.test(html));
    test("no merchant purchase anchor in HTML",!/<a[^>]*href="https?:\/\/(?:www\.)?(?:inspire3\.com|zen12\.com|hypnosislive\.com|affiliates\.inspire3\.com)/i.test(html));
    test("two clearly distinct product panels",html.includes("Total Focus")&&html.includes("Zen12")&&html.includes("47 MB")&&html.includes("four listening"));
    test("affiliate disclosures are twice adjacent to inactive offers",offerPos.length===2&&disclosurePos.length===2&&offerPos.every((m,i)=>disclosurePos[i]<m&&m-disclosurePos[i]<350));
    test("merchant links disabled using status not click",count(html,'class="inactive"')===2&&!/<a[^>]*class="inactive"/i.test(html));
    test("no JavaScript tracking or remote media",!/<script\b/i.test(html)&&!/<iframe\b/i.test(html)&&!/<video\b/i.test(html)&&!/(googletagmanager|facebook\.com\/tr|sendBeacon|XMLHttpRequest|dataLayer)/i.test(html));
    test("no price or countdown",!/\$\d/.test(html)&&!/(countdown|limited spots|only today)/i.test(html));
    test("unsubstantiated guarantees are NOT endorsed",!/(we guarantee|clinically proven to reprogram|we tested and confirmed|you will achieve 100%)/i.test(html));
    test("published official seller page inspectable in plan",plan.includes("https://inspire3.com/")&&plan.includes("https://hypnosislive.com/mental-skills/total-focus")&&plan.includes("https://zen12.com/about"));
    test("seller terms caveat and newsletter consent",plan.includes("five refunded sessions")&&plan.includes("newsletter"));
    test("partner acceptance expressly unverified",plan.includes("no Final Vestige-specific authorization")||plan.includes("not Final Vestige-specific authorization"));
    test("privacy design disallows identifying analytics",plan.includes("no raw referer string")&&plan.includes("email, IP, user agent")&&plan.includes("third-party analytics"));
    test("conversions distinguished from clicks",plan.includes("paid sales require merchant-confirmed reporting"));
    test("existing Zen12 optional video reused not autoplayed",plan.includes("Zen12 PR #229")&&plan.includes("preload none")&&plan.includes("Do not autoplay"));
    test("publication, CI, QD approvals withheld",plan.includes("independent QD")&&plan.includes("do not publish")&&plan.includes("No commerce activation"));
    /* Numerically verify representative normal-text combinations.
       This is not a substitute for computed-style/browser accessibility. */
    function luminance(hex) {
      let v=hex.replace("#","").match(/.{2}/g).map(x=>parseInt(x,16)/255);
      const c=v.map(x=>x<=0.04045?x/12.92:Math.pow((x+0.055)/1.055,2.4));
      return c[0]*0.2126+c[1]*0.7152+c[2]*0.0722;
    }
    function contrast(fore,back) {
      const v=[luminance(fore),luminance(back)].sort((a,b)=>b-a);
      return (v[0]+0.05)/(v[1]+0.05);
    }
    const colors=[
      ["body on page","#e0d9ce","#090b0b"],
      ["gold on page","#e3bd7d","#090b0b"],
      ["muted on card","#c8c0b3","#121716"],
      ["heading on card","#f6f0e7","#121716"],
      ["inactive label on control","#e0d9ce","#343a37"],
      ["gold link on card","#e3bd7d","#121716"],
      ["black focus button label on gold","#121614","#e3bd7d"]
    ];
    colors.forEach(c=>test("AA contrast ratio >=4.5: "+c[0],contrast(c[1],c[2])>=4.5));
    const failed=results.filter(t=>!t.pass);
    return {passed:results.length-failed.length,total:results.length,failed:failed,results:results};
  }
  scope.fvMindAudit=audit;
  if(typeof module!=="undefined"&&module.exports)module.exports={audit:audit};
})(typeof globalThis!=="undefined"?globalThis:this);

if(typeof require==="function"&&typeof module!=="undefined"&&require.main===module){
  const fs=require("fs"),path=require("path"),files={};
  for(const name of ["feature.md","page-self-hypnosis.html","evidence.json","conversion.md"])
    files[name]=fs.readFileSync(path.join(__dirname,name),"utf8");
  const r=module.exports.audit(files);
  r.results.forEach(x=>process.stdout.write((x.pass?"PASS ":"FAIL ")+x.name+"\n"));
  process.stdout.write(r.passed+"/"+r.total+" source guards passed\n");
  if(r.failed.length)process.exitCode=1;
}