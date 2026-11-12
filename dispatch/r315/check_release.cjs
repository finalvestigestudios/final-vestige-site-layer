#!/usr/bin/env node
'use strict';
const fs = require('node:fs');
const assert = require('node:assert/strict');
const path = require('node:path');
const here = __dirname;
const src = JSON.parse(fs.readFileSync(path.join(here,'email_source.json'),'utf8'));
const gate = JSON.parse(fs.readFileSync(path.join(here,'release_gate.json'),'utf8'));
const html = fs.readFileSync(path.join(here,'issue03-review.html'),'utf8');
const txt = fs.readFileSync(path.join(here,'issue03-review.txt'),'utf8');
function inspect(s=src,g=gate,h=html,t=txt) {
 const issues=g.issue_3||{};const flags=['adopted','send_authorized','guide_live','affiliate_account_accepted','merchant_email_permission','approved_creative','earning_link_verified','subscriber_eligibility_verified','native_jetpack_preview_verified','postal_address_verified','unsubscribe_received_verified','founder_final_approval'];
 return {status:'HOLD_UNSENT_HOLD_MERCHANT',release_authorized:false,fail_closed:flags.every(k=>issues[k]===false)&&g.all_issues_send_authorized===false,
 one_cta:s.blocks.filter(x=>x.type==='cta').length===1,
 near_disclosure:s.blocks.findIndex(x=>x.type==='disclosure')===s.blocks.findIndex(x=>x.type==='cta')+1,
 no_affiliate_link:!/(affiliate_id=|hop=|clickbank|utm_medium=affiliate|https?:\/\/[^\s"'<>]*ref=)/i.test(h+t),
 no_live_cta:/data-primary-cta="inactive"/.test(h)&& !/<a[^>]+href=[^>]+data-primary-cta/i.test(h),
 preserved_holds:/\[\[VALID_FV_POSTAL_ADDRESS_REQUIRED\]\]/.test(h)&&/\[\[ACTUAL_UNSUBSCRIBE_RENDERING_REQUIRED\]\]/.test(h),
 docs_readable:/<html lang="en">/.test(h)&&/role="presentation"/.test(h)&&/name="viewport"/.test(h),
 subject_precise:s.subject.length<=68&&s.preheader.length<=120,
 no_cost_or_results_guarantee:!(/\$\d+|buy now|guaranteed results/i.test(s.blocks.map(x=>x.text).join(' '))),
 source_coverage:s.sources.length>=3
 };
}
if(require.main===module){const r=inspect();Object.entries(r).forEach(([k,v])=>{if(k!=='status'&&k!=='release_authorized')assert.equal(v,true,k)});assert.equal(r.release_authorized,false);process.stdout.write(JSON.stringify(r,null,2)+'\n');}
module.exports={inspect};
