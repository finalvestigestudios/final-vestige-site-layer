"use strict";
/* Dispatch R234 source-only guard. Execute: node dispatch/r234/tests/check_r234.js
 * No network, email, WordPress, subscriber or merchant operations.
 */
const fs=require("node:fs");
const path=require("node:path");
const assert=require("node:assert/strict");
const root=path.resolve(__dirname,"..");
const contract=JSON.parse(fs.readFileSync(path.join(root,"DELIVERY-AND-CONVERSION-CONTRACT.json"),"utf8"));
const alternative=fs.readFileSync(path.join(root,"03-INTENT-BRIDGE-ALTERNATIVE-UNSENT.md"),"utf8");
const readme=fs.readFileSync(path.join(root,"README.md"),"utf8");
function problems(c,letter,overview) {
  const e=[];
  const flag=(bad,msg)=>{if(bad)e.push(msg)};
  flag(c.status!=="HOLD_UNSENT","release status");
  flag(c.jetpack.auto_new_post_emails!==false,"email default");
  flag(c.jetpack.native_email_requires_publishing_new_post!==true,"post-bound delivery");
  for(const k of ["send_test_email_authorized","post_creation_authorized","publication_authorized","actual_unsubscribe_verified","final_welcome_delivered_verified","subscriber_reachability_verified"])flag(c.jetpack[k]!==false,k);
  flag(c.provider_counters_reported.do_not_add_together!==true,"nonadditive counters");
  flag(c.provider_counters_reported.eligible_email_recipients!==null,"eligible audience presumed");
  flag(c.cta_action_map.length!==6,"six issues");
  flag(c.cta_action_map.filter(x=>x.kind==="editorial").length!==4,"four editorial");
  flag(c.cta_action_map.filter(x=>x.kind==="commercial-review-pending").length!==2,"two commercial");
  for(const item of c.cta_action_map) {
    flag(!item.release.includes("HOLD"),"unguarded issue "+item.issue);
    if(item.kind==="commercial-review-pending"){
      for(const k of ["merchant_approval_verified","email_permission_verified","affiliate_earning_url_verified","offer_guide_live"]){
        flag(item[k]!==false,"unsupported authorization "+item.issue+"/"+k);
      }
      flag(item.destination!==null,"early commercial destination "+item.issue);
    }
  }
  flag(c.measurement.public_download_is_not_confirmation!==true,"download conflated with confirmation");
  flag(c.measurement.affiliate_outbound_is_not_purchase!==true,"click conflated with purchase");
  flag(c.measurement.realized_net_revenue_per_1000_qualified_sessions!==null,"unsupported KPI");
  for(const s of ["UNSENT DRAFT","[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]","[[VALID_POSTAL_ADDRESS_REQUIRED]]","[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]","Commercial disclosure","https://zen12.com/hnp","https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety","work-starting","meditation"]){
    flag(!letter.includes(s),"missing editorial proof: "+s);
  }
  flag(!overview.includes("publishing a qualifying post"),"Jetpack action boundary");
  flag(!overview.includes("HOLD_MERCHANT"),"merchant hold missing");
  return e;
}
function mutant(f){return structuredClone(f);}
let checks=0;
function test(label,fn){fn();checks++;console.log("PASS",label);}
test("baseline fail-closed",()=>assert.deepEqual(problems(contract,alternative,readme),[]));
const mutations=[
 ["draft released",c=>c.status="READY_TO_SEND"],
 ["global new-post email enabled",c=>c.jetpack.auto_new_post_emails=true],
 ["false no-post send assumption",c=>c.jetpack.native_email_requires_publishing_new_post=false],
 ["unauthorized preview send",c=>c.jetpack.send_test_email_authorized=true],
 ["unauthorized WP draft",c=>c.jetpack.post_creation_authorized=true],
 ["unauthorized publication",c=>c.jetpack.publication_authorized=true],
 ["claimed legal footer",c=>c.jetpack.actual_unsubscribe_verified=true],
 ["claimed welcome",c=>c.jetpack.final_welcome_delivered_verified=true],
 ["claimed email-eligible list",c=>c.jetpack.subscriber_reachability_verified=true],
 ["add counters",c=>c.provider_counters_reported.do_not_add_together=false],
 ["invent eligible count",c=>c.provider_counters_reported.eligible_email_recipients=3],
 ["invent seventh email",c=>c.cta_action_map.push(mutant(c.cta_action_map[0]))],
 ["wrong editorial allocation",c=>c.cta_action_map[0].kind="commercial-review-pending"],
 ["unblocked editorial release",c=>c.cta_action_map[0].release="READY"],
 ["invent Zen12 URL",c=>c.cta_action_map[2].destination="https://example.invalid"],
 ["invent Zen12 approval",c=>c.cta_action_map[2].merchant_approval_verified=true],
 ["invent Zen12 EMAIL rights",c=>c.cta_action_map[2].email_permission_verified=true],
 ["invent earning URL",c=>c.cta_action_map[2].affiliate_earning_url_verified=true],
 ["invent live guide",c=>c.cta_action_map[2].offer_guide_live=true],
 ["invent Total Focus permission",c=>c.cta_action_map[4].email_permission_verified=true],
 ["download counted as consent",c=>c.measurement.public_download_is_not_confirmation=false],
 ["affiliate click counted as sale",c=>c.measurement.affiliate_outbound_is_not_purchase=false],
 ["invent net KPI",c=>c.measurement.realized_net_revenue_per_1000_qualified_sessions=100]
];
for(const [name,mutate] of mutations){test(name,()=>{const c=mutant(contract);mutate(c);assert(problems(c,alternative,readme).length>0);});}
test("legal footer alteration rejected",()=>assert(problems(contract,alternative.replace("[[VALID_POSTAL_ADDRESS_REQUIRED]]","a verified address"),readme).length>0));
test("no activated offer placeholder",()=>assert(problems(contract,alternative.replace("[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]","https://example.invalid/offer"),readme).length>0));
test("no removal of source",()=>assert(problems(contract,alternative.replace("https://zen12.com/hnp","https://example.invalid/seller"),readme).length>0));
console.log(checks+"/"+checks+" offline source-level Node checks passed; not an email delivery or WordPress test");
