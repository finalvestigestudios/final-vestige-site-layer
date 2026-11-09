/* R240 offline source guard. Pure JavaScript; no dependencies, requests, PII or sends. */
function runR240Tests(files){
  const fail=[], passed=[];
  function ck(label,ok){if(ok)passed.push(label);else fail.push(label)}
  const md=files.markdown,html=files.html,txt=files.plaintext,c=JSON.parse(files.contract),matrix=files.matrix;
  const link="https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf";
  const look=["[[VALID_POSTAL_ADDRESS_REQUIRED]]","[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"];
  ck("original unchanged explicitly",md.includes("master PR #175")&&c.source_commit==="d57ccdba3aee8f065e143e101c2945f4f3d01647");
  ck("one editorial issue 06",md.includes("ISSUE 06")&&c.kind==="editorial");
  ck("subject and preheader match",md.includes(c.subject)&&md.includes(c.preheader)&&txt.includes(c.subject)&&txt.includes(c.preheader)&&html.includes(c.subject));
  ck("no re-subscribe CTA",md.includes(link)&&html.includes(link)&&txt.includes(link)&&!md.includes("https://finalvestige.com/focus/)"));
  ck("free PDF is canonical configured welcome",link.includes("Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf"));
  ck("research primary record all formats",[md,html,txt].every(v=>v.includes("26479070")));
  ck("science sample size accurate",[md,html,txt].every(v=>v.includes("138")&&v.includes("19,951")));
  ck("one CTA to PDF", (md.match(/\[Reopen your free 52-page Focus Fieldbook\]/g)||[]).length===1);
  ck("HTML safe",!/<script\b|<form\b|<img\b|<iframe\b|<video\b|<meta[^>]+http-equiv\s*=\s*['"]refresh/i.test(html));
  ck("HTML lang and presentation layout",/<html lang="en"/.test(html)&&/role="presentation"/.test(html)&&/<h1/.test(html));
  ck("no tracking pixel or merchants",[md,html,txt].every(v=>!/(awin1\.com|clickbank|partner_id=|utm_content=[0-9a-f]{16,})/i.test(v)));
  ck("unverified legal footers",[md,html,txt].every(v=>look.every(p=>v.includes(p))));
  ck("no send permission",c.status==="HOLD_UNSENT_NOT_ADOPTED"&&Object.values(c.release_gates).every(v=>v===false)&&c.measurement.no_sends===true);
  ck("affiliate hold isolated",c.commercial.commercial_slots.join(",")==="3,5"&&c.commercial.merchant_links.length===0);
  ck("revenue not invented",c.measurement.net_revenue_per_1000_qualified_sessions===null&&c.measurement.affiliate_paid_orders===null&&matrix.includes("NOT COMPUTABLE"));
  ck("subscriber eligible unknown",c.last_known_subscriber_counters.actual_email_eligible===null&&matrix.includes("total=3")&&matrix.includes("unconfirmed=2"));
  ck("no inferred confirmation",c.measurement.canonical_confirmed_signup.includes("provider-confirmed")&&matrix.includes("authenticated provider state transition"));
  ck("provenance source",matrix.includes("https://zen12.com/hnp")&&matrix.includes("https://jetpack.com/support/newsletter/"));
  ck("source boundaries",/does \*\*not\*\* test this Fieldbook/i.test(md)&&matrix.includes("seller claim"));
  ck("release gate permits nobody",c.release_gates.founder_final_campaign_approval===false);
  return {passed:passed.length,failed:fail.length,fail,passedNames:passed};
}
