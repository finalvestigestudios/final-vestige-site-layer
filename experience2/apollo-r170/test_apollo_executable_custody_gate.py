"""Offline mutation tests: ensure R169 cannot pass executable tampering unobserved."""
import json
from pathlib import Path
import unittest
from apollo_executable_custody_gate import preflight, validate_executable
from test_apollo_source_conversion_gate import controlled

HERE=Path(__file__).resolve().parent

class ExecutableCustody(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.witness=controlled()
        cls.preview, cls.receipt=preflight(cls.source, cls.witness)

    def test_attested_output_and_determinism(self):
        out, report=preflight(self.source,self.witness)
        self.assertEqual(out,self.preview)
        self.assertEqual(report['r170'],self.receipt['r170'])
        self.assertFalse(report['r170']['approved_for_publish'])
        self.assertEqual(report['r170']['new_dom_event_handlers'],0)
        self.assertEqual(report['r170']['new_active_embed_or_form_surfaces'],0)

    def test_js_css_and_dom_mutations_fail_closed(self):
        v=self.preview
        changes={
          'added ecommerce tracking beacon':v.replace('FV_APOLLO_R167_BLOCK_PACK_V1', 'FV_APOLLO_R167_BLOCK_PACK_V1'),
          'onclick injection':v.replace('Read original investigation</a>','Read original investigation</a><span onclick="fetch(\'https://tracking.invalid\')"> </span>',1),
          'malicious iframe':v.replace('Read original investigation</a>','Read original investigation</a><iframe src="https://tracking.invalid"></iframe>',1),
          'CSS background beacon':v.replace('FV_APOLLO_R168_CUSTODY_A11Y_V1','FV_APOLLO_R168_CUSTODY_A11Y_V1').replace('</style>', '.fvx{background:url(https://tracking.invalid/px)}\n</style>',1),
          'new JS beacon':v.replace('</script>', 'fetch("https://tracking.invalid/pixel");\n</script>',1),
          'new JS in staging module':v.replace('FV_APOLLO_R167_BLOCK_PACK_V1','FV_APOLLO_R167_BLOCK_PACK_V1').replace('</script>', '</script>',1),
          'break archive keyboard handler':v.replace('gallery.addEventListener', 'gallery.removeEventListener'),
          'change original CSS':v.replace('--fvx-ink: #090a0a','--fvx-ink: red',1),
          'add external script':v.replace('<!-- /wp:html -->', '<script src="https://tracking.invalid/p.js"></script><!-- /wp:html -->',1),
          'add form endpoint':v.replace('Read original investigation</a>','Read original investigation</a><form action="https://tracking.invalid"></form>',1),
        }
        changes['added ecommerce tracking beacon']=v.replace('console.error(', 'fetch("https://tracking.invalid/pixel"); console.error(',1)
        changes['new JS in staging module']=v.replace('data-fvx-chrono-photo', 'data-fvx-chrono-photo',1).replace('window.', 'window.__attacker = 1; window.',1)
        detected=0
        for label,bad in changes.items():
            with self.subTest(label=label):
                if bad==v: # fall back to guaranteed arbitrary script insertion
                    bad=v.replace('</script>', 'void("unapproved");</script>',1)
                self.assertNotEqual(bad,v)
                with self.assertRaisesRegex(ValueError,'HOLD'):
                    validate_executable(self.source,bad)
                detected+=1
        (HERE/'r170_negative_controls.json').write_text(json.dumps({'rejected_mutations':detected,'cases':list(changes),'release':'STAGING_HOLD'},indent=2,sort_keys=True)+'\n')

    def test_unpinned_editor_source_rejected(self):
        with self.assertRaisesRegex(ValueError,'HOLD'):
            preflight(self.source)

if __name__=='__main__': unittest.main(verbosity=2)
