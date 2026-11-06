import base64, json, re, tempfile, unittest
from pathlib import Path
from zipfile import ZipFile
import make_private_playground_launcher as launch

# Run from this source-controlled directory:
# python -m unittest -v test_make_private_playground_launcher.py
# The original review Blueprint must be present beside this test.
SOURCE=(Path(__file__).parent/'FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json').read_bytes()

class Checks(unittest.TestCase):
    def test_exact_pinned_source(self):
        self.assertEqual(launch.validate(SOURCE),launch.BLOB)
    def mutated(self,f):
        bp=json.loads(SOURCE);f(bp)
        with self.assertRaises(ValueError):launch.validate(json.dumps(bp).encode())
    def test_unauthorized_extra_step(self):
        self.mutated(lambda b:b['steps'].append({'step':'wp-cli','command':'wp site empty --yes'}))
    def test_wrong_theme(self):
        self.mutated(lambda b:b['steps'][0]['themeData'].__setitem__('ref','HEAD'))
    def test_mutated_public_record(self):
        self.mutated(lambda b:b['steps'][2].__setitem__('data',b['steps'][2]['data'].replace('class="fv-margin-strip__item"','class="lost"',1)))
    def test_wrong_preview_path(self):
        self.mutated(lambda b:b['steps'][2].__setitem__('path','/wordpress/wp-content/themes/assembler/functions.php'))
    def test_package_fragment_roundtrip_and_determinism(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'source.json';p.write_bytes(SOURCE)
            a=Path(tmp)/'a.zip';b=Path(tmp)/'b.zip'
            launch.package(p,a);launch.package(p,b)
            self.assertEqual(a.read_bytes(),b.read_bytes())
            with ZipFile(a) as z:
                self.assertEqual(z.read('blueprint.json'),SOURCE)
                h=z.read('launch_review.html').decode();self.assertNotIn('<script',h)
                import html
                url=html.unescape(re.search('href="(https://playground.wordpress.net/#[^"]+)',h).group(1))
                self.assertEqual(base64.b64decode(url.partition('#')[2]),SOURCE)
                self.assertEqual(json.loads(z.read('manifest.json'))['margins'],72)

if __name__=='__main__':unittest.main(verbosity=2)
