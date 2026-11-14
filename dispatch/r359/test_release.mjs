// R359 independent source-only guards. No network, no sending, no subscriber PII.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const read=n=>fs.readFileSync(new URL(n, import.meta.url),'utf8');
const j=JSON.parse(read('RELEASE_EVIDENCE.json'));
const md=read('ISSUE03_OPTIONAL.md'), html=read('ISSUE03_OPTIONAL.html'), txt=read('ISSUE03_OPTIONAL.txt');
const cases=[
['six originals stay intact',j.campaign.original_issue_count===6],
['four editorial roles',j.campaign.original_editorial_count===4],
['commercial only issues 03/05',j.campaign.original_commercial_issues.join(',')==='3,5'],
['global unsent hold',j.campaign.all_six==='HOLD_UNSENT'],
['commercial merchant hold',j.campaign.commercial==='HOLD_MERCHANT'],
['candidate unadopted',j.campaign.this_issue03_alternative==='NOT_ADOPTED'],
['no founder final approval',j.campaign.founder_final_send_approval===false],
['new post auto emails remain disabled',j.wordpress.post_default_email===false],
['no configured welcome equated with receipt',j.wordpress.welcome_message_configured===true&&!j.wordpress.welcome_receipt_verified],
['Jetpack native preview unverified',!j.wordpress.native_jetpack_preview_verified],
['subscriber arithmetic not conflated',j.wordpress.subscriber_total===3&&j.wordpress.confirmed_count===3&&j.wordpress.unconfirmed_count===2&&j.wordpress.counts_overlap],
['follower source separated',j.wordpress.wpcom_followers===3&&j.wordpress.email_followers===0&&j.wordpress.eligible_recipients===null],
['commercial acceptance all unknown',Object.values(j.merchant).every(v=>v===false)],
['CAN-SPAM source attestations all false',Object.values(j.compliance).every(v=>v===false)],
['not claiming commercial conversion',Object.values(j.analytics).every(v=>v===null)],
['no email or test email sent',!j.test_mail_sent&&!j.newsletter_sent],
['no WordPress or merchant changes',!j.wordpress_written&&!j.merchant_activated],
['subject editorial honest',md.includes('Subject:** What twelve minutes can actually tell you')],
['native preheader not asserted',md.includes('Proposed preheader')&&!j.wordpress.native_jetpack_preview_verified],
['editorial body substantial',md.split(/\s+/).length>=850],
['original 1784 primary linked',md.includes('wellcomecollection.org/works/enhgscmf')],
['2019 modern review linked',md.includes('doi.org/10.1007/s12671-019-01163-1')],
['SKU package details sourced',md.includes('48 MP3')],
['unsupported equivalence qualified',md.includes('not independently')||md.includes('not an independent')],
['no invented checkout price',!(/\$\d/.test(md))],
['disclosure in all three versions',md.includes('commission')&&txt.includes('commission')&&html.includes('commission')],
['commercial destination explicit placeholder',md.includes('[[APPROVED_LIVE_ZEN12_PRESELL_GUIDE_URL_REQUIRED]]')],
['commercial destination disabled in HTML',html.includes('HOLD_MERCHANT')&&!html.includes('href="[[APPROVED')],
['HTML correct language',html.includes('lang="en"')],
['HTML email table',html.includes('role="presentation"')&&html.includes('max-width:640px')],
['mobile viewport included',html.includes('name="viewport"')],
['no dangerous email markup',!/<script|<iframe|<form|<img/i.test(html)],
['legal footer placeholders on HTML',html.includes('[[VALID_FV_POSTAL_ADDRESS_UNVERIFIED]]')&&html.includes('[[JETPACK_OPT_OUT_UNVERIFIED]]')],
['source citations retained in HTML',html.includes('gutenberg.org')&&html.includes('doi.org')],
['subject length 70 or fewer','What twelve minutes can actually tell you'.length<=70],
['proposed preheader length 120 or fewer',"A blindfold in 1784, 85 modern studies, and a buyer's question.".length<=120],
];
for(const [name,passed] of cases)test(name,()=>assert.equal(passed,true,name));
