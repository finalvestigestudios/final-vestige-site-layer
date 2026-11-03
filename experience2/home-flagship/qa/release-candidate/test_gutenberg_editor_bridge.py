#!/usr/bin/env python3
"""Native PHP adversarial tests for synthetic-only Gutenberg editor bridge.

These are mock WordPress contracts. They DO NOT prove an actual Gutenberg
browser/editor save, Assembler rendering, hosted Jetpack, or WCAG compliance.
"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRIDGE = HERE / "playground_gutenberg_editor_gate.php"

MOCK = r'''<?php
function wp_json_encode($v) { return json_encode($v); }
function wp_parse_url($v,$part) { return parse_url($v,$part); }
function home_url() { return getenv('FV_HOME') ?: 'http://localhost:9473/'; }
function wp_slash($v) { return $v; }
function is_wp_error($v) { return false; }
function get_users($args) { return array((object)array('ID'=>1)); }
function wp_set_current_user($id) {}
function current_user_can($cap) { return getenv('FV_CAN_UNFILTERED') !== '0'; }
function wp_set_auth_cookie($id,$remember,$ssl) {}
function is_ssl() { return false; }
function clean_post_cache($id) {}
function wp_insert_post($a,$return_error) {
    if (getenv('FV_INSERT_ERROR')==='1') return false;
    file_put_contents(__DIR__.'/db.json',json_encode(array(
      'id'=>42,'post_type'=>$a['post_type'],'post_title'=>$a['post_title'],
      'post_status'=>$a['post_status'],'post_content'=>$a['post_content']
    )));
    return 42;
}
function fv_mock_record() {
    $p=__DIR__.'/db.json';
    return file_exists($p) ? json_decode(file_get_contents($p),true) : null;
}
function add_post_meta($id,$key,$value,$unique) {
    file_put_contents(__DIR__.'/meta.json',json_encode(array($key=>$value)));
    return true;
}
function get_post_meta($id,$key,$single) {
    $p=__DIR__.'/meta.json';
    $r=file_exists($p) ? json_decode(file_get_contents($p),true) : array();
    return $r[$key] ?? '';
}
function get_post($id) {
    $r=fv_mock_record();
    return $r && $id === 42 ? (object)$r : null;
}
function get_post_field($name,$id,$context) {
    $r=fv_mock_record();
    return $r[$name] ?? null;
}
function get_post_status($id) { return get_post_field('post_status',$id,'raw'); }
function wp_delete_post($id,$force) {
    if (getenv('FV_DELETE_FAIL')==='1') return false;
    $p=__DIR__.'/db.json';
    if (!file_exists($p)) return false;
    unlink($p);
    @unlink(__DIR__.'/meta.json');
    return (object)array('ID'=>$id);
}
function parse_blocks($content) {
    return array(array('blockName'=>'core/html'),array('blockName'=>'core/html'));
}
'''

def fixture():
    spans = "".join(
        '<span class="fv-margin-strip__item" style="--i:%d">Mock record %d</span>' % (i, i)
        for i in range(72)
    )
    return ("<!-- wp:html --><style>/* FV-EX2 PAGE6 REVIEW-ONLY */</style>"
            + spans + "<div class='fv-hf__chapter-nav'>Focus Fieldbook</div>"
            + "<!-- /wp:html --><!-- wp:jetpack/subscriptions /-->")


class EditorBridge(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "wp-content").mkdir()
        shutil.copyfile(BRIDGE, self.root / "fv_ex2_editor_qa_once.php")
        (self.root / "wp-load.php").write_text(MOCK, encoding="utf-8")
        self.token = "a"*64
        (self.root / "wp-content/fv-ex2-editor-token").write_text(self.token+"\n")
        (self.root / "wp-content/fv-ex2-synthetic-only.marker").write_text("SYNTHETIC_TEST_FIXTURE_ONLY\n")
        (self.root / "wp-content/fv-ex2-synthetic-candidate.html").write_text(fixture())
        (self.root / "runner.php").write_text(
            "<?php $_SERVER['REQUEST_METHOD']=getenv('FV_METHOD') ?: 'POST';"
            "$_SERVER['HTTP_HOST']=getenv('FV_HTTP_HOST') ?: 'localhost:9473';"
            "$_SERVER['HTTP_X_FV_EX2_EDITOR_TOKEN']=getenv('FV_TOKEN') ?: '';"
            "$_GET['action']=getenv('FV_ACTION') ?: '';"
            "require __DIR__.'/fv_ex2_editor_qa_once.php';",
            encoding="utf-8"
        )

    def call(self, action, **params):
        env = dict(os.environ, FV_ACTION=action, FV_TOKEN=params.pop("token",self.token),
                   FV_HTTP_HOST=params.pop("host","localhost:9473"),
                   FV_METHOD=params.pop("method","POST"), **params)
        run = subprocess.run(["php",str(self.root/"runner.php")],cwd=self.root,
                             env=env,text=True,capture_output=True,timeout=10)
        self.assertEqual(run.returncode,0,run.stderr)
        return json.loads(run.stdout)

    def set_saved(self, **changes):
        path=self.root/"db.json"
        item=json.loads(path.read_text())
        item.update(changes)
        path.write_text(json.dumps(item))

    def test_complete_create_gutenberg_title_save_verify_cleanup(self):
        c=self.call("create")
        self.assertEqual(c["result"],"CREATED")
        self.assertEqual(c["draft_id"],42)
        self.assertEqual(self.call("verify")["result"],"FAIL")
        self.set_saved(post_title="FV EX2 SYNTHETIC EDITOR SAVED")
        v=self.call("verify")
        self.assertEqual(v["result"],"PASS")
        self.assertEqual(len(v["checks"]),9)
        self.assertTrue(all(v["checks"].values()))
        d=self.call("cleanup")
        self.assertEqual(d["result"],"DELETED")
        self.assertTrue(d["verified_absent"])
        self.assertFalse((self.root/"db.json").exists())
        self.assertFalse((self.root/"wp-content/fv-ex2-editor-draft-id").exists())

    def test_missing_session_token_refuses(self):
        self.assertEqual(self.call("create",token="")["result"],"FAIL")
        self.assertFalse((self.root/"db.json").exists())

    def test_wrong_session_token_refuses(self):
        self.assertEqual(self.call("create",token="b"*64)["result"],"FAIL")

    def test_http_host_production_refuses(self):
        self.assertEqual(self.call("create",host="finalvestige.com")["result"],"FAIL")
        self.assertFalse((self.root/"db.json").exists())

    def test_site_home_production_refuses(self):
        self.assertEqual(self.call("create",FV_HOME="https://finalvestige.com")["result"],"FAIL")

    def test_unfiltered_html_capability_required(self):
        r = self.call("create", FV_CAN_UNFILTERED="0")
        self.assertEqual(r["result"], "FAIL")
        self.assertFalse((self.root/"db.json").exists())

    def test_missing_marker_refuses(self):
        (self.root/"wp-content/fv-ex2-synthetic-only.marker").unlink()
        self.assertEqual(self.call("create")["result"],"FAIL")

    def test_post_only(self):
        self.assertEqual(self.call("create",method="GET")["result"],"FAIL")
        self.assertFalse((self.root/"db.json").exists())

    def test_reject_existing_draft(self):
        self.assertEqual(self.call("create")["result"],"CREATED")
        self.assertEqual(self.call("create")["result"],"FAIL")

    def test_reject_missing_candidate(self):
        (self.root/"wp-content/fv-ex2-synthetic-candidate.html").unlink()
        self.assertEqual(self.call("create")["result"],"FAIL")

    def test_reject_missing_margins(self):
        p=self.root/"wp-content/fv-ex2-synthetic-candidate.html"
        p.write_text(fixture().replace('style="--i:71"','style="--i:XX"'))
        self.assertEqual(self.call("create")["result"],"FAIL")

    def test_editor_content_mutation_fail_closed(self):
        self.assertEqual(self.call("create")["result"],"CREATED")
        self.set_saved(post_title="FV EX2 SYNTHETIC EDITOR SAVED",
                       post_content=fixture()+"illicit mutation")
        v=self.call("verify")
        self.assertEqual(v["result"],"FAIL")
        self.assertFalse(v["checks"]["byte_exact_after_editor_save"])
        self.assertEqual(self.call("cleanup")["result"],"DELETED")

    def test_changed_title_cannot_strand_proven_owned_draft(self):
        self.assertEqual(self.call("create")["result"],"CREATED")
        self.set_saved(post_title="Unrelated title")
        self.assertEqual(self.call("cleanup")["result"],"DELETED")
        self.assertFalse((self.root/"db.json").exists())

    def test_tampered_ownership_marker_refuses_delete(self):
        self.assertEqual(self.call("create")["result"],"CREATED")
        (self.root/"meta.json").write_text(json.dumps({"_fv_ex2_editor_qa_owner":"tampered"}))
        self.assertEqual(self.call("cleanup")["result"],"FAIL")
        self.assertTrue((self.root/"db.json").exists())

    def test_unknown_action_refused(self):
        self.assertEqual(self.call("publish")["result"],"FAIL")
        self.assertFalse((self.root/"db.json").exists())

    def test_failed_delete_not_claimed(self):
        self.assertEqual(self.call("create")["result"],"CREATED")
        self.assertEqual(self.call("cleanup",FV_DELETE_FAIL="1")["result"],"FAIL")
        self.assertTrue((self.root/"db.json").exists())


if __name__=="__main__":
    unittest.main()
