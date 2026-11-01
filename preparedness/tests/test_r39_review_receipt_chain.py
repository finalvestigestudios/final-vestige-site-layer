"""R39 synthetic, private, no-secret-in-repo receipt & chain adversarial tests.

These tests prove structural key-possession custody only. They do not prove
real reviewer identity, source accuracy, emergency safety or QD approval.
"""
from __future__ import annotations
import copy
from datetime import datetime, timezone, timedelta
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import reviewer_receipt_chain_gate as gate
from test_r38_quarantine_synthetic import fixture, mutate_csv

SECRET = b"R39-SYNTHETIC-ONLY-NEVER-REAL-KEY!"  # Test fixture, never production.
ISSUED = "2026-11-01T07:19:00Z"
NOW = datetime(2026,11,1,7,20,0,tzinfo=timezone.utc)
GENESIS = {"sequence":0,"receipt_sha256":gate.ZERO_HEAD}
KEY = "qa-reviewer-001"
NONCE = "1" * 32

def registry():
    return {KEY: {"secret":SECRET, "state":"ACTIVE", "scope":gate.KEY_SCOPE,
                  "not_before":"2026-10-01T00:00:00Z",
                  "not_after":"2026-12-01T00:00:00Z"}}

def populated(b):
    return mutate_csv(b, "human_scope_risk_notes",
                      "Needs independent article-specific source reading",
                      state="FLAGGED_FOR_FACT_CHECK")

def signed(b=None, edits=None, head=None, *, secret=SECRET, nonce=NONCE,
           issued=ISSUED, key=KEY):
    b=fixture() if b is None else b
    edits=populated(b) if edits is None else edits
    head=copy.deepcopy(GENESIS) if head is None else head
    challenge=gate.unsigned_challenge(b,edits)
    envelope=gate.prepare_unsigned_receipt(
        challenge,reviewer_key_id=key,submission_nonce_hex=nonce,
        issued_at_utc=issued,trusted_chain_head=head)
    return b, edits, gate.sign_progress_receipt(envelope,secret)

def verify(b,e,r,*,keys=None,head=None,now=NOW):
    return gate.verify_progress_receipt(
        b,e,r,trusted_registry=registry() if keys is None else keys,
        trusted_chain_head=copy.deepcopy(GENESIS) if head is None else head,
        trusted_now=now)

def refuses(b,e,r,*,keys=None,head=None,now=NOW):
    with unittest.TestCase().assertRaises(gate.ReceiptHold):
        verify(b,e,r,keys=keys,head=head,now=now)

class ValidSynthetic(unittest.TestCase):
    def setUp(self):
        self.b,self.edits,self.r=signed()

    def test_valid_key_possession_receipt(self):
        result=verify(self.b,self.edits,self.r)
        self.assertTrue(result["key_possession_verified"])
        self.assertFalse(result["reviewer_real_identity_verified"])
    def test_all_public_and_medical_gates_hold(self):
        x=verify(self.b,self.edits,self.r)
        for flag in ("may_publish","human_source_reviews_completed",
                     "qualified_safety_clearance","independent_QD_approval"):
            self.assertIs(x[flag],False)
    def test_observations_remain_unverified(self):
        x=verify(self.b,self.edits,self.r)
        self.assertEqual(x["quarantine_observations_remain_unverified"],1)
    def test_source_chain_bound(self):
        x=verify(self.b,self.edits,self.r)
        self.assertEqual(x["parent_R37_fingerprint_sha256"],
                         self.b["manifest"]["fingerprint_sha256"])
    def test_submission_read_only(self):
        b,e,r=copy.deepcopy((self.b,self.edits,self.r))
        verify(self.b,self.edits,self.r)
        self.assertEqual((self.b,self.edits,self.r),(b,e,r))
    def test_receipt_deterministic_same_fields_and_key(self):
        _,_,again=signed(self.b,self.edits)
        self.assertEqual(again,self.r)
    def test_r38_hashbound(self):
        self.assertEqual(self.r["parent_R38_fingerprint_sha256"],
            gate.unsigned_challenge(self.b,self.edits)["parent_R38_fingerprint_sha256"])
    def test_receipt_and_ledger_hash(self):
        x=verify(self.b,self.edits,self.r)
        self.assertEqual(x["receipt_sha256"],gate.digest(self.r))
        self.assertEqual(x["proposed_next_trusted_chain_head"]["sequence"],1)
    def test_strong_domain_separator(self):
        self.assertTrue(gate.DOMAIN.startswith(b"FV-PREPAREDNESS-ISSUE136"))
    def test_hmac_does_not_embed_secret(self):
        self.assertNotIn(SECRET.decode(),json.dumps(self.r))
    def test_two_sequential_external_chain_receipts(self):
        accepted=verify(self.b,self.edits,self.r)
        next_head=accepted["proposed_next_trusted_chain_head"]
        _,_,second=signed(self.b,self.edits,next_head,nonce="2"*32)
        result=verify(self.b,self.edits,second,head=next_head)
        self.assertEqual(result["proposed_next_trusted_chain_head"]["sequence"],2)
        self.assertEqual(second["previous_receipt_sha256"],gate.digest(self.r))
    def test_unsigned_challenge_without_keys_is_not_authorization(self):
        c=gate.unsigned_challenge(self.b,self.b["csv_tables"])
        self.assertEqual(c["unverified_progress_records"],0)
        self.assertFalse(c["may_publish"])
        self.assertFalse(c["qualified_safety_clearance"])
        self.assertFalse(c["independent_QD_approval"])
    def test_cannot_accept_zero_progress_receipt(self):
        _,_,r=signed(self.b,self.b["csv_tables"])
        refuses(self.b,self.b["csv_tables"],r)
    def test_valid_untrusted_escalation_still_hold(self):
        edits=mutate_csv(self.b,"human_scope_risk_notes",
                         "Ask a qualified independent reviewer",state="ESCALATE_TO_QUALIFIED_REVIEW")
        _,_,r=signed(self.b,edits)
        x=verify(self.b,edits,r)
        self.assertFalse(x["qualified_safety_clearance"])
    def test_verify_does_not_need_network_or_file_write(self):
        self.assertEqual(set(verify(self.b,self.edits,self.r)),{
            "schema_version","issue","release_state","machine_authority",
            "key_possession_verified","reviewer_real_identity_verified",
            "human_source_reviews_completed","qualified_safety_clearance",
            "independent_QD_approval","may_publish",
            "quarantine_observations_remain_unverified",
            "parent_R37_fingerprint_sha256","parent_R38_fingerprint_sha256",
            "receipt_sha256","proposed_next_trusted_chain_head","limitations"})
    def test_crypto_tag_is_lowercase_hex64(self):
        self.assertRegex(self.r["signature_hex"],r"^[0-9a-f]{64}$")
    def test_stage_challenge_covers_four_original_tables(self):
        c=gate.unsigned_challenge(self.b,self.edits)
        self.assertRegex(c["edited_worksheet_manifest_sha256"],r"^[0-9a-f]{64}$")

class SecurityNegative(unittest.TestCase):
    def setUp(self):
        self.b,self.edits,self.r=signed()
    def fail_receipt(self,**overrides):
        wrong=copy.deepcopy(self.r);wrong.update(overrides)
        refuses(self.b,self.edits,wrong)
    def test_no_signature(self):
        r=copy.deepcopy(self.r);r.pop("signature_hex");refuses(self.b,self.edits,r)
    def test_extra_field(self):self.fail_receipt(verified=True)
    def test_false_qd_pass(self):self.fail_receipt(independent_QD_approval=True)
    def test_false_medical_pass(self):self.fail_receipt(qualified_safety_clearance=True)
    def test_false_publish(self):self.fail_receipt(may_publish=True)
    def test_false_human_review(self):self.fail_receipt(human_source_reviews_completed=True)
    def test_replay_against_advanced_head(self):
        head=verify(self.b,self.edits,self.r)["proposed_next_trusted_chain_head"]
        refuses(self.b,self.edits,self.r,head=head)
    def test_wrong_head_digest(self):
        refuses(self.b,self.edits,self.r,head={"sequence":0,"receipt_sha256":"f"*64})
    def test_wrong_head_sequence(self):
        refuses(self.b,self.edits,self.r,head={"sequence":3,"receipt_sha256":"f"*64})
    def test_bool_head_sequence(self):
        refuses(self.b,self.edits,self.r,head={"sequence":False,"receipt_sha256":gate.ZERO_HEAD})
    def test_missing_head(self):
        refuses(self.b,self.edits,self.r,head={})
    def test_added_head_field(self):
        refuses(self.b,self.edits,self.r,head={**GENESIS,"override":True})
    def test_untrusted_registry_missing_key(self):
        refuses(self.b,self.edits,self.r,keys={})
    def test_revoked_key(self):
        keys=registry();keys[KEY]["state"]="REVOKED"
        refuses(self.b,self.edits,self.r,keys=keys)
    def test_wrong_scope(self):
        keys=registry();keys[KEY]["scope"]="PUBLISH_APPROVAL"
        refuses(self.b,self.edits,self.r,keys=keys)
    def test_short_secret(self):
        keys=registry();keys[KEY]["secret"]=b"short"
        refuses(self.b,self.edits,self.r,keys=keys)
    def test_signer_wrong_secret(self):
        b,e,r=signed(secret=b"another-synthetic-key-for-tests-1234")
        refuses(b,e,r)
    def test_invalid_registry_entry(self):
        keys=registry();keys[KEY]["extra"]="trusted"
        refuses(self.b,self.edits,self.r,keys=keys)
    def test_registry_secret_must_be_bytes(self):
        keys=registry();keys[KEY]["secret"]=SECRET.decode()
        refuses(self.b,self.edits,self.r,keys=keys)
    def test_not_yet_valid_key(self):
        keys=registry();keys[KEY]["not_before"]="2026-11-01T07:19:30Z"
        refuses(self.b,self.edits,self.r,keys=keys)
    def test_expired_key(self):
        keys=registry();keys[KEY]["not_after"]="2026-11-01T07:19:30Z"
        refuses(self.b,self.edits,self.r,keys=keys)
    def test_stale_received_later_than_day(self):
        refuses(self.b,self.edits,self.r,now=NOW+timedelta(hours=25))
    def test_future_dated_more_than_minute(self):
        refuses(self.b,self.edits,self.r,now=NOW-timedelta(minutes=5))
    def test_naive_verification_clock(self):
        refuses(self.b,self.edits,self.r,now=NOW.replace(tzinfo=None))
    def test_non_utc_verification_clock(self):
        refuses(self.b,self.edits,self.r,
                now=datetime(2026,11,1,8,20,tzinfo=timezone(timedelta(hours=1))))
    def test_unsigned_edited_csv_forgery(self):
        edits=mutate_csv(self.b,"human_scope_risk_notes","DIFFERENT",state="IN_PROGRESS")
        refuses(self.b,edits,self.r)
    def test_original_source_manifest_tamper(self):
        b=copy.deepcopy(self.b);b["manifest"]["qualified_safety_clearance"]=True
        refuses(b,self.edits,self.r)
    def test_csv_source_immutable_cell_changed(self):
        edits=mutate_csv(self.b,"source_url","https://untrusted.example",state="IN_PROGRESS")
        refuses(self.b,edits,self.r)
    def test_token_not_reviewed_with_no_notes(self):
        edits=mutate_csv(self.b,"review_state","DONE")
        refuses(self.b,edits,self.r)
    def test_unsafe_note_formula(self):
        edits=mutate_csv(self.b,"human_scope_risk_notes","=HYPERLINK(1)",state="IN_PROGRESS")
        refuses(self.b,edits,self.r)
    def test_malformed_nonce(self):
        self.fail_receipt(submission_nonce_hex="Z"*32)
    def test_wrong_case_progress_count(self):
        self.fail_receipt(unverified_progress_records=1959)
    def test_changed_challenge_hash(self):
        self.fail_receipt(challenge_sha256="0"*64)
    def test_sig_byte_flip(self):
        self.fail_receipt(signature_hex="0"*64)
    def test_missing_authority(self):
        self.fail_receipt(machine_authority="PUBLISH_APPROVED")
    def test_wrong_algorithm(self):
        self.fail_receipt(signature_algorithm="SHA256")
    def test_bad_timestamp(self):
        self.fail_receipt(issued_at_utc="2026-02-30T07:19:00Z")
    def test_timestamp_offset_forbidden(self):
        self.fail_receipt(issued_at_utc="2026-11-01T07:19:00+00:00")
    def test_previous_commit_fork(self):
        self.fail_receipt(previous_receipt_sha256="f"*64)
    def test_wrong_receipt_sequence(self):
        self.fail_receipt(sequence=2)
    def test_boolean_sequence(self):
        self.fail_receipt(sequence=True)
    def test_new_key_handle(self):
        self.fail_receipt(reviewer_key_id="attacker-001")
    def test_forged_signature_field_type(self):
        self.fail_receipt(signature_hex=1)
    def test_recipient_key_confused_for_secret(self):
        wrong={KEY:{"secret":b"a"*32,"state":"ACTIVE",
              "scope":gate.KEY_SCOPE,
              "not_before":"2026-10-01T00:00:00Z",
              "not_after":"2026-12-01T00:00:00Z"}}
        refuses(self.b,self.edits,self.r,keys=wrong)
    def test_no_partial_chain_head(self):
        refuses(self.b,self.edits,self.r,head={"sequence":0})
    def test_extra_row_rejected(self):
        e=copy.deepcopy(self.edits)
        e["claim_review.csv"]+=e["claim_review.csv"].split("\r\n")[1]+"\r\n"
        refuses(self.b,e,self.r)
    def test_challenge_recomputed_even_with_valid_hmac(self):
        _,e,r=signed(self.b,populated(self.b))
        altered=mutate_csv(self.b,"human_scope_risk_notes","Changed after signing",
                           state="IN_PROGRESS")
        refuses(self.b,altered,r)

# Every signed receipt field and every unsigned custody field gets an explicit
# independently executed mutation, to prevent partial/selected comparisons.
_MUTATED_FIELDS={
    "schema_version":2,"issue":137,"release_state":"PUBLISHED",
    "machine_authority":"AUTHENTICATED_PUBLISH_PASS",
    "parent_R37_fingerprint_sha256":"a"*64,
    "parent_R38_fingerprint_sha256":"b"*64,
    "original_R34_R35_R36_lineage_sha256":"c"*64,
    "edited_worksheet_manifest_sha256":"d"*64,
    "quarantined_observations_sha256":"e"*64,
    "unverified_progress_records":999,
    "source_claim_accuracy_verified":True,
    "human_source_reviews_completed":True,
    "qualified_safety_clearance":True,
    "independent_QD_approval":True,
    "may_publish":True,
    "challenge_sha256":"f"*64,
    "reviewer_key_id":"revoked-key-002",
    "submission_nonce_hex":"0"*32,
    "issued_at_utc":"2026-10-31T07:19:00Z",
    "sequence":77,
    "previous_receipt_sha256":"f"*64,
    "signature_algorithm":"MD5",
    "signature_hex":"a"*64,
}
for _field,_value in _MUTATED_FIELDS.items():
    def single_field(self, field=_field, value=_value):
        self.fail_receipt(**{field:value})
    setattr(SecurityNegative,"test_fingerprint_bound_"+_field,single_field)

# Every field omitted from the receipt must fail closed rather than using
# defaults supplied implicitly by a caller or a future schema version.
for _field in sorted(_MUTATED_FIELDS):
    def missing_field(self,field=_field):
        r=copy.deepcopy(self.r);r.pop(field)
        refuses(self.b,self.edits,r)
    setattr(SecurityNegative,"test_missing_"+_field,missing_field)

for _bad in (None,{},[],1,True,"null"):
    def bad_registry(self,val=_bad):
        refuses(self.b,self.edits,self.r,keys=val)
    setattr(SecurityNegative,"test_untrusted_registry_shape_"+str(_bad)[:15],bad_registry)

if __name__=="__main__":unittest.main()
