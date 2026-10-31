// Node 20+ dependency-free, synthetic mutations. No online access, no mail.
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { auditEvidence } from "./r12_evidence_gate.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = JSON.parse(fs.readFileSync(path.join(here,"R12_EVIDENCE_LEDGER.json"),"utf8"));
const copy = () => structuredClone(base);
const expectInvalid = (code, mutate) => {
  const e=copy();mutate(e);
  const result=auditEvidence(e);
  assert.equal(result.release,"HOLD_UNSENT");
  assert.equal(result.can_send,false);
  assert.equal(result.source_only,"INVALID");
  assert.ok(result.violations.includes(code), JSON.stringify(result));
};
test("baseline holds everything even with a source-only pass",()=>{
  const r=auditEvidence(copy());assert.equal(r.source_only,"SOURCE_ONLY_PASS");
  assert.equal(r.release,"HOLD_UNSENT");assert.equal(r.can_send,false);
  assert.equal(r.blocker_count,7);
});
test("manifest cannot be marked send-ready",()=>expectInvalid("CAMPAIGN_RELEASE_DRIFT",e=>{e.release="SEND_READY"}));
test("six unique numbers required",()=>expectInvalid("MANIFEST_NOT_SIX_UNIQUE",e=>{e.issues[5].number=5}));
test("4-to-2 offer allocation cannot silently change",()=>expectInvalid("MIX_DRIFT",e=>{e.issues[0].kind="commercial-review-pending"}));
test("no issue may activate",()=>expectInvalid("ISSUE_NOT_HELD",e=>{e.issues[3].release="READY"}));
test("unpublished offer guide URL cannot be inserted",()=>expectInvalid("PROMO_DESTINATION_ACTIVATED",e=>{e.issues[2].planned_destination="https://finalvestige.com/mind/zen12/"}));
test("merchant acceptance cannot be presumed",()=>expectInvalid("AFFILIATE_APPROVAL_ASSUMED",e=>{e.account_partner.approval_for_final_vestige="APPROVED"}));
test("email promotion permission cannot be presumed",()=>expectInvalid("AFFILIATE_APPROVAL_ASSUMED",e=>{e.account_partner.written_email_channel_permission="APPROVED"}));
test("affiliate link cannot be preactivated",()=>expectInvalid("AFFILIATE_APPROVAL_ASSUMED",e=>{e.account_partner.approved_zen12_product_link="https://zen12.com/"}));
test("unpublished guide must remain unpublished",()=>expectInvalid("WARMUP_PRETENDED_LIVE",e=>{e.pages.total_focus_guide.published=true}));
test("WordPress sending cannot be re-enabled in ledger",()=>expectInvalid("JETPACK_DELIVERY_DRIFT",e=>{e.site.email_new_posts_by_default=true}));
test("simulated email preview cannot be called received",()=>expectInvalid("JETPACK_DELIVERY_DRIFT",e=>{e.site.received_native_campaign_mime=true}));
test("configured welcome is not proof of receipt",()=>expectInvalid("WELCOME_DELIVERY_INFERRED",e=>{e.site.welcome_delivery_proven=true}));
test("inconsistent subscriber counts cannot become known audience",()=>expectInvalid("RECIPIENTS_INFERRED",e=>{e.site.unique_permissioned_deliverable=2}));
test("counts cannot silently be changed",()=>expectInvalid("AGGREGATES_CHANGED",e=>{e.site.subscriber_aggregates.unconfirmed=0}));
test("physical business sender address cannot be asserted verified",()=>expectInvalid("LEGAL_EVIDENCE_INFERRED",e=>{e.site.address_of_FV_verified=true}));
test("unsubscribe cannot be asserted verified",()=>expectInvalid("LEGAL_EVIDENCE_INFERRED",e=>{e.site.actual_commercial_unsubscribe_verified=true}));
test("merchant outcome claim cannot become Final Vestige endorsed",()=>expectInvalid("UNSUPPORTED_OUTCOME_APPROVED",e=>{e.offer_claims.find(x=>x.id==="zen-outcome-04").public_email_safe="Scientifically established"}));
test("Total Focus effectiveness not independently proven",()=>expectInvalid("UNSUPPORTED_OUTCOME_APPROVED",e=>{e.offer_claims.find(x=>x.id==="tf-outcome-06").approved_as_fv_result=true}));
test("seller claims cannot be lost from evidence tiers",()=>expectInvalid("OFFERS_INSUFFICIENTLY_DISTINGUISHED",e=>{e.offer_claims=e.offer_claims.filter(x=>x.id!=="tf-outcome-06")}));
test("unknown citation host is not valid in claim map",()=>expectInvalid("UNTRUSTED_PUBLIC_LINK",e=>{e.offer_claims[0].source="https://example.invalid/"}));
test("private email field must never be stored in ledger",()=>expectInvalid("SENSITIVE_LEDGER_FIELDS",e=>{e.subscriber_email="not-to-be-recorded@example.test"}));
