// R326 review-only logic: cannot send or deploy.
export function checkDraft(d){
const issues=[];
if(!d.manuscript.includes("OPTIONAL_EDITORIAL_REVIEW_ONLY / HOLD_UNSENT")||!d.manuscript.includes("NOT ADOPTED"))issues.push("release state");
if((d.html.match(/data-primary-cta="true"/g)||[]).length!==1)issues.push("exactly one CTA");
if(!d.html.includes('href="https://finalvestige.com/2026/11/02/change-blindness/"'))issues.push("published CTA");
if(/<script[\s>]|<form[\s>]|on(click|load)=/i.test(d.html))issues.push("unsafe HTML");
if(/href="https?:\/\/(?:zen12|hypnosislive|affiliates\.inspire3)/i.test(d.html))issues.push("unauthorized merchant URL");
for(const token of ["[[VALID_FV_POSTAL_ADDRESS_REQUIRED]]","[[JETPACK_RENDERED_UNSUBSCRIBE_REQUIRED]]","[[NATIVE_JETPACK_PREVIEW_REQUIRED]]","[[FOUNDER_SEND_APPROVAL_REQUIRED]]"])if(!d.html.includes(token)||!d.plaintext.includes(token)||!d.manuscript.includes(token))issues.push("missing "+token);
if(!d.html.includes("psychologicalscience.org")||!d.html.includes("10.3758/BF03208840"))issues.push("independent research");
if(!d.manuscript.includes("Your focus log isn't a verdict")||!d.plaintext.includes("SUBJECT: Your focus log isn't a verdict")||!d.html.includes("Your focus log isn't a verdict"))issues.push("subject");
if(!d.dossier.includes("NOT COMPUTABLE")||!d.dossier.includes("HOLD_MERCHANT"))issues.push("revenue hold");
if(/guaranteed success|12 minutes = 1 hour|100% razor-sharp focus/i.test(d.manuscript+d.html))issues.push("unverified promises");
return{ok:!issues.length,issues};
}
