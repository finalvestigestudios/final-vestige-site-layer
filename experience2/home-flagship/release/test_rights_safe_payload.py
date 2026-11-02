"""Hostile, offline tests of ACTUAL proposed page-6 release payload; no CMS writes."""
import copy
import json
import unittest
from pathlib import Path
from verify_rights_safe_payload import HOME, TARGET, STYLE_NAMES, SCRIPT_NAMES, audit, read_and_audit

BASE = HOME / TARGET


def inputs():
    return (
        (HOME/"index.html").read_text("utf-8"),
        (BASE/"replacement-block-index1.html").read_text("utf-8"),
        {n:(HOME/("wp-candidate" if n=="wp-integration.css" else "")/n).read_text("utf-8")
         for n in STYLE_NAMES},
        {n:(HOME/n).read_text("utf-8") for n in SCRIPT_NAMES},
        json.loads((BASE/"PROPOSED_PRODUCTION_CHANGE.json").read_text("utf-8")),
        (BASE/"original-block-index1.html").read_text("utf-8"),
    )


class ReleasePayloadTests(unittest.TestCase):
    def test_current_actual_release_payload_exact_parity_and_hashes(self):
        self.assertEqual(read_and_audit(), [])

    def assertRejected(self, name, mutate):
        parts=list(inputs())
        mutate(parts)
        errors=audit(*parts)
        self.assertTrue(errors,name+" unexpected PASS")

    def test_uncleared_map_added(self):
        self.assertRejected("nypl",lambda v:v.__setitem__(
            1,v[1]+'<img src="edit-017-v02-nypl-5003296-original.jpg">'))

    def test_misleading_public_domain_statement(self):
        self.assertRejected("rights",lambda v:v.__setitem__(
            0,v[0]+'NYPL believes this item is in the public domain under United States law.'))

    def test_inline_css_drift_fails(self):
        self.assertRejected("CSS",lambda v:v.__setitem__(
            3,{**v[3], "flagship.js":v[3]["flagship.js"]+"\n// tampered"}))
        self.assertRejected("CSS",lambda v:v.__setitem__(
            2,{**v[2], "flagship.css":v[2]["flagship.css"]+"\n.extra{color:red}"}))

    def test_older_nav_css_not_released(self):
        self.assertRejected("chronicle",lambda v:v.__setitem__(
            2,{**v[2], "chronicle.css":v[2]["chronicle.css"]+"\n/* stale */"}))

    def test_missing_research_source_plate(self):
        self.assertRejected("source",lambda v:v.__setitem__(
            1,v[1].replace("ARCHIVAL REFERENCE · IMAGE NOT REPRODUCED","unreviewed map")))

    def test_production_manifest_wrong_sha256(self):
        self.assertRejected("sha256",lambda v:v[4]["apply"].update(replacement_sha256="0"*64))

    def test_rollback_expected_hash_wrong(self):
        self.assertRejected("rollback",lambda v:v[4]["rollback"]["params"].update(
            expected_block_hash="0"*40))

    def test_release_block_outside_parity_changes(self):
        self.assertRejected("edit",lambda v:v.__setitem__(
            1,v[1].replace("EDITORIAL TYPESETTING · NOT A FACSIMILE",
                            "unverified historical facsimile")))

    def test_fourth_image_is_rejected(self):
        self.assertRejected("extra",lambda v:v.__setitem__(1,v[1]+'<img src="data:image/png;base64,AAAA">'))

    def test_original_rollback_contract_is_immutable(self):
        self.assertRejected("rollback snapshot",lambda v:v.__setitem__(5,v[5]+" "))

    def test_no_false_release_approval(self):
        self.assertRejected("release authorization",lambda v:v[4].update(status="PRODUCTION APPROVED"))


if __name__ == "__main__":
    unittest.main()
