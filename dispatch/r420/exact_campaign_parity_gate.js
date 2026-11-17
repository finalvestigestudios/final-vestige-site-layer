/* Dispatch R420 — read-only canonical email/preview parity; never sends or unlocks.
   Usage with already fetched UTF-8 files: R420.audit(manifest, records).
   records[i] = {source: canonical Markdown, html: R419 HTML, text: R419 TXT}.
   No network, browser APIs, cookies, subscriber identities or tracking.
*/
(function () {
  "use strict";
  const safeArray = x => Array.isArray(x) ? x : [];
  const linksFromMd = s => [...String(s).matchAll(/\[[^\]]+\]\((https:\/\/[^\s)]+)\)/g)].map(m => m[1]);
  const linksFromHtml = s => [...String(s).matchAll(/<a\b[^>]*\bhref="([^"]+)"/gi)].map(m => m[1]);
  function audit(manifest, records) {
    const report = {pass: false, tested: 0, passed: 0, failures: [], issues: [], release: "HOLD_UNSENT",
      merchant: {3:"HOLD_MERCHANT",5:"HOLD_MERCHANT"},
      authority: {founderFinalSend:false, confirmedRecipients:false, actualWelcomeReceipt:false,
        nativeJetpackPreview:false, verifiedPublisherPostalAddress:false, functionalUnsubscribe:false,
        namedAffiliateEmailRights:false, approvedLiveGuide:false, verifiedReferredCheckout:false,
        independentlySettledRevenue:false}};
    const check=(ok, label)=>{report.tested++;if(ok)report.passed++;else report.failures.push(label);};
    check(manifest && manifest.status === "DRAFT_UNSENT_NO_SCHEDULING","campaign:unsent");
    check(manifest && manifest.mix && manifest.mix.editorial===4 && manifest.mix.commercial_review_pending===2,"campaign:4-2-mix");
    check(records && records.length===6 && safeArray(manifest.issues).length===6,"campaign:six-pairs");
    const forbidden=/<\s*(script|iframe|form|img|object|embed|audio|video|input|svg)\b/i;
    safeArray(records).forEach((p,i)=>{
      const entry=safeArray(manifest.issues)[i]||{}, md=String(p?.source||""), html=String(p?.html||""), txt=String(p?.text||"");
      const sourceUrls=linksFromMd(md), htmlUrls=linksFromHtml(html);
      const commercial=i===2||i===4;
      const checks={
        sourcePresent: md.length>200,
        htmlPresent: html.length>200,
        textPresent: txt.length>200,
        subjectMd: md.includes("**Subject:** "+entry.subject),
        subjectHtml: html.includes(entry.subject||"SUBJECT_NOT_CONFIGURED"),
        subjectText: txt.includes("Subject: "+entry.subject),
        preheaderMd: md.includes(entry.preheader||"PREHEADER_NOT_CONFIGURED"),
        preheaderHtml: html.includes(entry.preheader||"PREHEADER_NOT_CONFIGURED"),
        preheaderText: txt.includes(entry.preheader||"PREHEADER_NOT_CONFIGURED"),
        oneSourceLink: sourceUrls.length===1,
        oneHtmlLink: htmlUrls.length===1,
        correctHtmlTarget: sourceUrls.length===1 && JSON.stringify(htmlUrls)===JSON.stringify(sourceUrls),
        correctTextTarget: sourceUrls.length===1 && txt.includes(sourceUrls[0]),
        firstPartyOnly: htmlUrls.every(u=>/^https:\/\/finalvestige\.com\/[a-z0-9\/_.-]*$/i.test(u)),
        noExecutableMarkup: !forbidden.test(html),
        oneHeading: (html.match(/<h1\b/gi)||[]).length===1,
        accessibleDocument: /<html lang="en">/i.test(html)&&/name="viewport"/i.test(html),
        hardPostalHold: html.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]") && md.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]"),
        hardOptoutHold: html.includes("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]") && md.includes("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"),
        offlineWarning: /OFFLINE REVIEW ONLY/i.test(txt)&&/HOLD — NEVER SEND/i.test(html),
        productSafety: !commercial ||
          (html.includes("[INACTIVE: APPROVED_") && txt.includes("APPROVED_") &&
           html.includes("Commercial disclosure") && !/href="https:\/\/(zen12|hypnosislive|inspire3)\./i.test(html)),
        correctKind: entry.kind===(commercial?"commercial-review-pending":"editorial"),
        nonblankSubject: typeof entry.subject==="string" && entry.subject.length>=10 && entry.subject.length<=80
      };
      Object.entries(checks).forEach(([key,ok])=>check(Boolean(ok),"issue"+(i+1)+":"+key));
      report.issues.push({number:i+1,commercial,activeFirstPartyCTAs:htmlUrls.length,
        commercialGuideCTA:commercial?"INACTIVE":"NOT_APPLICABLE",
        firstPartyDestination:htmlUrls.length===1?htmlUrls[0]:null,
        failures:Object.entries(checks).filter(([k,v])=>!v).map(([k])=>k)});
    });
    report.pass=report.failures.length===0;
    return report;
  }
  return {audit};
})()