"""Offline, zero-provider-call validation for the FV cloud relay pilot."""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

module_path=Path(__file__).resolve().parents[1]/"scripts"/"fv_cloud_relay.py"
spec=importlib.util.spec_from_file_location("fv_cloud_relay",module_path)
relay=importlib.util.module_from_spec(spec)
spec.loader.exec_module(relay)

def comment(event,who="finalvestigestudios"):
    return {"user":{"login":who},
            "body":relay.FENCE+"json\n"+json.dumps(event)+"\n"+relay.FENCE}

def evt(id=relay.SOURCE,who="chatgpt",action="CREATE",status="READY_FOR_WORK",nxt="claude"):
    return {"schema":"fv-handoff-v1","event_id":id,"campaign_id":relay.CAMPAIGN,
            "actor":who,"action":action,"status":status,"next_owner":nxt}

class RelayTests(unittest.TestCase):
    def setUp(self):
        self.source=[comment(evt())]

    def test_disabled_by_default(self):
        with patch.dict(os.environ,{},clear=True):
            self.assertFalse(relay.allowed("CLAUDE"))
            self.assertFalse(relay.allowed("GROK"))
            with patch.object(relay,"call_model",side_effect=AssertionError("billable call")):
                relay.scheduled.__globals__["get_comments"]=lambda:self.source
                relay.scheduled()

    def test_all_three_flags_required(self):
        with patch.dict(os.environ,{"FV_PAID_CALLS_ALLOWED":"true","FV_CLOUD_RELAY_ENABLED":"true"},clear=True):
            self.assertFalse(relay.allowed("CLAUDE"))
        with patch.dict(os.environ,{"FV_PAID_CALLS_ALLOWED":"true","FV_CLOUD_RELAY_ENABLED":"true","FV_CLAUDE_API_ENABLED":"true"},clear=True):
            self.assertTrue(relay.allowed("CLAUDE"))
            self.assertFalse(relay.allowed("GROK"))

    def test_public_comment_untrusted(self):
        self.assertFalse(relay.has_source([comment(evt(),"untrusted-public-user")]))
        self.assertFalse(relay.qa_ready([comment(evt(relay.QA,"chatgpt","QA_RESULT","READY_FOR_APPROVAL","grok"),"untrusted-public-user")]))

    def test_stage_and_claim_idempotency(self):
        self.assertEqual(relay.stage(self.source),"CLAUDE_PENDING")
        self.assertEqual(relay.stage(self.source+[{"body":"FV_CLOUD_CLAIM "+relay.CLAUDE}]),"CLAUDE_CLAIMED")
        self.assertEqual(relay.stage([]),"NO_TRUSTED_SOURCE")

    def test_parser_rejects_broken_record(self):
        self.assertEqual(relay.parsed({"body":relay.FENCE+"json\n{bad\n"+relay.FENCE}),[])

    def test_generated_copy_has_no_urls(self):
        with self.assertRaises(RuntimeError):
            relay.safe_copy("Publish https://example.com this fictional lighthouse mystery immediately!")

    def test_qa_transition_requires_actual_claude_cloud_event(self):
        claude=evt(relay.CLAUDE,"claude","UPDATE","READY_FOR_QA","chatgpt")
        body=("FV_CLOUD_OUTPUT "+relay.CLAUDE+"\n\nFICTIONAL TEST COPY\n\n"
              "A keeper found an old envelope. The storm had already begun.\n\n"+
              relay.FENCE+"json\n"+json.dumps(claude)+"\n"+relay.FENCE)
        bot={"user":{"login":"github-actions[bot]"},"body":body}
        self.assertEqual(relay.stage(self.source+[bot]),"QA_PENDING")
        qa=comment(evt(relay.QA,"chatgpt","QA_RESULT","READY_FOR_APPROVAL","grok"))
        self.assertEqual(relay.stage(self.source+[bot,qa]),"GROK_PENDING")

    def test_smoke_is_zero_cost_and_once(self):
        payload={"issue":{"number":3090},"comment":{
            "user":{"login":"finalvestigestudios"},
            "body":comment(evt(relay.SMOKE,"chatgpt","HELLO","IN_PROGRESS","claude"))["body"],
            "html_url":"https://github.com/finalvestigestudios/final-vestige-site-layer/issues/3090#issuecomment-100"}}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"event.json";p.write_text(json.dumps(payload))
            with patch.dict(os.environ,{"GITHUB_EVENT_PATH":str(p)}),\
                 patch.object(relay,"get_comments",return_value=[]),\
                 patch.object(relay,"emit") as post,\
                 patch.object(relay,"call_model",side_effect=AssertionError("paid call")):
                relay.smoke()
                self.assertEqual(post.call_count,1)
                self.assertIn("FV_CLOUD_RELAY_SMOKE",post.call_args.args[0])

if __name__=="__main__":
    unittest.main()
