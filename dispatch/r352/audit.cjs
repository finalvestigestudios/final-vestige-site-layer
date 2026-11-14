// Offline invariant guard only: NEVER grants release or sends email.
module.exports = function audit(r){
const {meta,md,txt,html}=r,errors=[];
if(meta.state!=="OPTIONAL_NOT_ADOPTED_HOLD_UNSENT")errors.push("unsent state");
if(meta.original_campaign_pr!==175||meta.original_issue!==1||meta.issue_kind!=="editorial")errors.push("campaign scope");
for(const [k,v] of Object.entries(meta.flags||{})){if(v!==false)errors.push("permission gate "+k)}
const must=[meta.subject,meta.preheader,"[[VALID_POSTAL_ADDRESS_REQUIRED]]","[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"];
for(const [name,body] of [["markdown",md],["plaintext",txt],["html",html]])for(const token of must)if(!body.includes(token.replace(/&/g,"&amp;"))&&!body.includes(token))errors.push("missing "+name+" token "+token);
if(!html.includes('lang="en"')||!html.includes('role="presentation"')||!html.includes('name="viewport"')||!html.includes('data-primary-cta="true"'))errors.push("offline html structure");
if((html.match(/data-primary-cta="true"/g)||[]).length!==1)errors.push("primary CTA not unique");
if(!html.includes('href="'+meta.primary_cta_url+'"')||!md.includes("]("+meta.primary_cta_url+")")||!txt.includes(meta.primary_cta_url))errors.push("canonical CTA mismatch");
if((md.match(/\*\*One primary CTA:\*\*/g)||[]).length!==1)errors.push("markdown CTA count");
for(const s of meta.sources.slice(0,2))for(const [name,body] of [["markdown",md],["text",txt],["html",html]])if(!body.includes(s.url))errors.push("missing source "+name+" "+s.url);
if(!/OFFLINE REVIEW ONLY/.test(html)||!/NOT A JETPACK PREVIEW/.test(html)||!/RELEASE BLOCKED/.test(html))errors.push("review preview disclaimer");
if(/<script\b|<form\b|input\s+type\s*=\s*["']email|autofocus|onload=/i.test(html))errors.push("interactive or tracking email markup");
if(/https?:\/\/(?:affiliates\.)?(?:zen12|hypnosislive|inspire3)\.com/i.test(meta.primary_cta_url))errors.push("unapproved merchant CTA");
if(/guaranteed (?:results|improvement)|clinically proven to (?:cure|reprogram)|buy now before midnight/i.test(md))errors.push("unsupported hype");
if(!md.includes("1998")||!md.includes("1999")||!md.includes("not a universal estimate"))errors.push("study caveats");
if(meta.preheader.length>110||meta.subject.length>65)errors.push("subject length");
return {pass:errors.length===0,errors,subject_length:meta.subject.length,preheader_length:meta.preheader.length,source_count:meta.sources.length,release:"HOLD_UNSENT"};
};
