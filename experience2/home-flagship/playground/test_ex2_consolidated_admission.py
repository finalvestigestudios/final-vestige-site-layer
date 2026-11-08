"""Network-free, self-contained negative controls for flagship release admission."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile, ZIP_STORED
import verify_ex2_consolidated_admission as gate


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name)
        plugin=b'<?php /* offline mock only */'
        plugin_hash=gate.sha256(plugin)
        bp=root/'test_blueprint.zip'
        manifest={'files_sha256':{'mu-plugins/fv-ex2-playground-review.php':plugin_hash},
                  'local_only_preflight_first':True}
        with ZipFile(bp,'w',ZIP_STORED) as z:
            z.writestr('blueprint.json','{}')
            z.writestr('SOURCE_CUSTODY.json',json.dumps(manifest))
            z.writestr('mu-plugins/fv-ex2-playground-review.php',plugin)
            z.writestr('mu-plugins/fv-ex2-private-browser-receipt.php','<?php')
        bundle_hash=gate.sha256(bp.read_bytes())
        self.pinned=patch.multiple(gate,PINNED_BLUEPRINT=bundle_hash,PINNED_PLUGIN=plugin_hash)
        self.pinned.start();self.addCleanup(self.pinned.stop)
        php={'identity':'OFFLINE_PHP_HOOK_STUB_NOT_WORDPRESS_CORE',
             'baseline_sha256':bundle_hash,'plugin_sha256':plugin_hash,
             'scenarios':[{'scenario':'valid','pass':True,'html_bytes':50938},
                          {'scenario':'flag_off','pass':True,'html_bytes':0},
                          {'scenario':'wrong_page','pass':True,'html_bytes':0}]}
        browser={'bundle_sha256':bundle_hash,'scope':'OFFLINE Chromium NOT WordPress',
                 'configs':28,'passed':28,
                 'interactions':{x:{'pass':True} for x in gate.INTERACTIONS},
                 'negative_controls':{x:{'correctly_rejected':True} for x in gate.NEGATIVES},
                 'results':[{'width':w,'zoom':zoom,'javascript':js,'pass':True,
                             'measurements':{'chapters':7,'margins':72,'focus_count':5,
                                             'chapter_targets_present':True,'overflow':False,
                                             'firstscreen_focus':1}}
                            for w in gate.WIDTHS for zoom in (1,2) for js in (False,True)]}
        media={'identity':'SOURCE_ATTESTED_PHP_OUTPUT_OFFLINE_NOT_WORDPRESS_ASSEMBLER',
               'candidate_plugin_sha256':plugin_hash,'bundle_sha256':bundle_hash,
               'results':[{'scenario':sc,'image_gate_pass_on_real_host':False,'release_pass':False}
                          for sc in ('offline-blocked','fixture-valid') for _ in range(5)]}
        self.inputs=[bp]+[root/(n+'.json') for n in ('php','browser','media')]
        for obj,path in zip((php,browser,media),self.inputs[1:]):
            path.write_text(json.dumps(obj))

    def test_known_good_receipts_hold_release(self):
        r=gate.inspect(*self.inputs)
        self.assertEqual(r['offline_evidence_integrity'],'PASS')
        self.assertEqual(r['decision'],'HOLD')
        self.assertFalse(r['release_authorized'])
        self.assertTrue(all(not f['pass'] for f in r['findings'] if f['scope']=='RELEASE'))

    def override_json(self,ix,change):
        src=list(self.inputs)
        d=json.loads(src[ix].read_text())
        change(d)
        path=Path(self.tmp.name)/('modified'+str(ix)+'.json')
        path.write_text(json.dumps(d));src[ix]=path
        return gate.inspect(*src)

    def test_swapped_plugin_receipt_rejected(self):
        self.assertEqual(self.override_json(1,lambda o:o.update(plugin_sha256='f'*64))['offline_evidence_integrity'],'FAIL')

    def test_forged_wordpress_identity_rejected(self):
        self.assertEqual(self.override_json(1,lambda o:o.update(identity='REAL_WORDPRESS_CORE'))['offline_evidence_integrity'],'FAIL')

    def test_seven_chapters_enforced(self):
        self.assertEqual(self.override_json(2,lambda o:o['results'][0]['measurements'].update(chapters=6))['offline_evidence_integrity'],'FAIL')

    def test_all_five_focus_paths_enforced(self):
        self.assertEqual(self.override_json(2,lambda o:o['results'][0]['measurements'].update(focus_count=4))['offline_evidence_integrity'],'FAIL')

    def test_required_viewport_grid_enforced(self):
        self.assertEqual(self.override_json(2,lambda o:o['results'][0].update(width=999))['offline_evidence_integrity'],'FAIL')

    def test_adversarial_negative_controls_enforced(self):
        self.assertEqual(self.override_json(2,lambda o:o['negative_controls']['missing_margin'].update(correctly_rejected=False))['offline_evidence_integrity'],'FAIL')

    def test_media_cannot_claim_real_network_success(self):
        self.assertEqual(self.override_json(3,lambda o:o['results'][0].update(image_gate_pass_on_real_host=True))['offline_evidence_integrity'],'FAIL')

    def test_media_sha_mismatch_rejected(self):
        self.assertEqual(self.override_json(3,lambda o:o.update(candidate_plugin_sha256='0'*64))['offline_evidence_integrity'],'FAIL')

    def test_extra_pseudoproof_never_approves_release(self):
        r=self.override_json(3,lambda o:o.update(axe='PASS',wp_core='PASS',sales=999999))
        self.assertEqual(r['decision'],'HOLD')
        self.assertFalse(r['release_authorized'])

    def test_modified_bundle_bytes_rejected(self):
        p=Path(self.tmp.name)/'tampered.zip';p.write_bytes(self.inputs[0].read_bytes()+b'x')
        self.assertEqual(gate.inspect(p,*self.inputs[1:])['offline_evidence_integrity'],'FAIL')

    def test_reviewer_report_does_not_claim_commercial_results(self):
        s=gate.as_markdown(gate.inspect(*self.inputs))
        self.assertIn('Net revenue per 1,000 qualified sessions:** unknown',s)
        self.assertIn('HOLD',s)
        self.assertNotIn('RELEASE APPROVED',s)


if __name__=='__main__':
    unittest.main()
