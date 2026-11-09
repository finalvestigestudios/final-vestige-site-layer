"use strict";
function checkDraft({issue,html,plain,contract,ledger}) {
 const checks=[];
 function ok(name,pass){checks.push({name,pass:!!pass});}
 const forbidden=/https?:\/\/(?:www\.)?(?:zen12\.com|hypnosislive\.com|affiliates\.inspire3\.com|awin1\.com)\b/i;
 const script=/<\s*(?:script|iframe|form|img|video|audio|object)\b|on(?:load|click|error)\s*=|<\s*style\b/i;
 const legal=["[[VALID_POSTAL_ADDRESS_REQUIRED]]","[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"];
 ok("campaign and edition remain unsent",/STATUS: UNSENT DRAFT/i.test(issue)&&/UNSENT REVIEW ONLY/i.test(plain)&&/REVIEW ONLY/.test(html));
 ok("subject honest",issue.includes("The test that separated a sensation from its cause")&&plain.includes("Subject: The test that separated a sensation from its cause")&&html.includes("The test that separated a sensation from its cause"));
 ok("preheader present",issue.includes("In 1784, investigators asked")&&plain.includes("Preheader: In 1784")&&html.includes("In 1784, investigators asked"));
 ok("1784 distinct from 1785",/1784/.test(issue)&&/1785/.test(issue)&&/1784/.test(plain)&&/1785/.test(plain));
 ok("Deslon not Puységur directly tested",/Deslon/.test(issue)&&/not a controlled test of the Marquis de Puységur/.test(issue)&&/not<\/strong> the Marquis de Puységur/.test(html));
 ok("no falsely commercial product",!forbidden.test(issue+html+plain));
 ok("one primary CTA in HTML",html.split("href=\"https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/\"").length===2);
 ok("editorial CTA present in all",issue.includes("https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/")&&plain.includes("https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"));
 ok("independent primary source in all formats",issue.includes("gutenberg.org/files/78413")&&html.includes("gutenberg.org/files/78413")&&plain.includes("gutenberg.org/files/78413"));
 ok("separate historical edition holding",issue.includes("wellcomecollection.org/works/enhgscmf")&&html.includes("wellcomecollection.org/works/enhgscmf"));
 ok("Puységur independent scholarship",issue.includes("10.1002/jhbs.21974")&&html.includes("10.1002/jhbs.21974"));
 ok("email safe no active scripts/pixels/forms",!script.test(html));
 ok("email html has accessible heading/lang",/<html lang="en">/.test(html)&&/<h1\b/.test(html)&&/<h2\b/.test(html));
 ok("no exposed recipient identifiers",!/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i.test(issue+html+plain+JSON.stringify(contract)));
 ok("visible warning not in hidden preheader",/REVIEW ONLY · UNSENT/.test(html)&&/PRE-SEND COMPLIANCE HOLD/.test(html));
 for(const placeholder of legal){ok("legal hold "+placeholder,[issue,html,plain].every(s=>s.includes(placeholder)));}
 ok("original 4:2 preserved",contract.mix.editorial===4&&contract.mix.commercial_review_pending===2);
 ok("all partner gates remain false",contract.final_merchant_email_permission_verified===false&&contract.final_affiliate_earning_url_verified===false&&contract.offer_guide_published===false);
 ok("send cannot be enabled",contract.send_enabled===false&&contract.founder_final_campaign_approval===false&&contract.affiliate_url===null);
 ok("no invented paid revenue",contract.verified_paid_orders===null&&contract.net_revenue_per_1000_qualified_human_sessions===null);
 ok("legal/consent gating in ledger",/consent-gated/.test(ledger)&&/functional opt-out unverified/.test(ledger));
 ok("no duplicate scripts",!/gtag\(|fbq\(|analytics\.js|tracking pixel/i.test(html));
 return {pass:checks.every(x=>x.pass),checks};
}
module.exports={checkDraft};