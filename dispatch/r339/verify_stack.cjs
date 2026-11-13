'use strict';
// Dispatch R339: offline snapshot auditor. DOES NOT call GitHub, WordPress or send.
const fs = require('node:fs');
const path = require('node:path');
const expectedChain = [175,2337,2343,2348,2354,2360,2366,2372,2375,2377,2383,2389];
const requiredGates = ['affiliate_accepted','email_channel_permitted','earning_link_issued','buyer_guide_live_approved','product_claims_approved','price_checkout_checked','refund_terms_checked','publisher_postal_verified','native_received_email_verified','unsubscribe_functional','welcome_received_verified','provider_eligible_audience_verified','founder_final_send_approval'];
function validate(snapshot) {
  const problems = [];
  const reject = (condition,why) => { if (condition) problems.push(why); };
  reject(!snapshot || typeof snapshot !== 'object' || Array.isArray(snapshot), 'snapshot_object_required');
  if (!snapshot || typeof snapshot !== 'object') return {pass:false,problems,decision:'HOLD_UNSENT'};
  reject(snapshot.type !== 'OFFLINE_READ_ONLY_SNAPSHOT','snapshot_type');
  reject(!/^2026-11-13T\d\d:\d\d:\d\dZ$/.test(snapshot.captured_at),'time_not_explicit_utc');
  const prs = snapshot.prs || [];
  reject(!Array.isArray(prs) || prs.length!==expectedChain.length + 1, 'pr_count');
  const byN = new Map(prs.map(p=>[p.number,p]));
  reject(byN.size !== prs.length,'duplicate_pr');
  expectedChain.forEach((n,i)=> {
    const p=byN.get(n);
    if (!p) {problems.push('missing_pr_'+n);return;}
    reject(p.state !== 'open' || p.draft !== true, 'pr_not_draft_open_'+n);
    reject(!/^[0-9a-f]{40}$/.test(p.head_sha), 'sha_invalid_'+n);
    reject(!p.head_branch || !p.base_branch, 'branch_missing_'+n);
    if (i) {
      const parent=byN.get(expectedChain[i-1]);
      reject(!parent || p.base_branch !== parent.head_branch || p.base_sha !== parent.head_sha, 'broken_stack_'+n);
    } else reject(p.base_branch !== 'main', 'master_not_based_main');
  });
  const separate=byN.get(201);
  reject(!separate || separate.base_branch===byN.get(175)?.head_branch || separate.number!==201,'parallel_201_wrongly_stacked');
  const issues=snapshot.editions;
  reject(!Array.isArray(issues) || issues.length!==6, 'six_editions_required');
  if (Array.isArray(issues)) {
    reject(new Set(issues.map(e=>e.number)).size!==6,'duplicate_edition');
    for (let i=1;i<=6;i++) {
      const e=issues.find(x=>x.number===i);
      if (!e) {problems.push('missing_edition_'+i);continue;}
      reject(e.status!=='HOLD_UNSENT','edition_not_held_'+i);
      reject((e.type==='merchant') !== (i===3||i===5),'four_two_mismatch_'+i);
      reject((e.merchant_status==='HOLD_MERCHANT') !== (i===3||i===5),'merchant_hold_mismatch_'+i);
      reject(e.alternative_adopted!==false,'unapproved_alternative_'+i);
    }
  }
  const g=snapshot.gates||{};
  for(const k of requiredGates) reject(g[k]!==false,'unverified_gate_'+k);
  const s=snapshot.subscribers||{}, f=snapshot.followers||{};
  reject(s.total!==3 || s.confirmed!==3 || s.unconfirmed!==2,'subscriber_snapshot_changed_reverify');
  reject(s.eligible_recipients!==null,'recipient_count_invented');
  reject(f.wpcom!==3 || f.email!==0,'follower_snapshot_changed_reverify');
  const newsletter=snapshot.newsletter||{};
  reject(newsletter.enabled!==true || newsletter.new_post_auto_send!==false || newsletter.email_content_format!=='full','newsletter_settings_changed');
  reject(newsletter.welcome_configured!==true || newsletter.welcome_received_verified!==false,'welcome_config_is_not_receipt');
  const actions=snapshot.actions||{};
  for (const k of ['email_sent','test_email_sent','subscriber_contacted','wordpress_written','affiliate_link_activated','production_analytics_changed','pr_merged','paid_service_started']) reject(actions[k]!==false,'prohibited_action_'+k);
  reject(snapshot.confirmed_orders !== null || snapshot.net_revenue_usd !== null || snapshot.qualified_human_sessions !== null,'revenue_must_remain_unknown');
  reject(snapshot.kpi !== 'NOT_COMPUTABLE', 'kpi_not_computable');
  reject(/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/i.test(JSON.stringify(snapshot)), 'email_address_in_public_snapshot');
  return {pass:problems.length===0, problems, decision:'HOLD_UNSENT', merchant_decision:'HOLD_MERCHANT', may_send:false, may_merge:false, kpi:'NOT_COMPUTABLE'};
}
if (require.main === module) {
  const p=process.argv[2] || path.join(__dirname,'stack_snapshot.json');
  const r=validate(JSON.parse(fs.readFileSync(p,'utf8')));
  process.stdout.write(JSON.stringify(r,null,2)+'\n');
  process.exitCode=r.pass ? 0 : 1;
}
module.exports={validate,expectedChain,requiredGates};
