"""R184 build and PHP adapter contracts. Requires PHP CLI + beautifulsoup4/tinycss2 for build."""
import tempfile, subprocess, sys, json, shutil, unittest
from pathlib import Path
from bs4 import BeautifulSoup
P = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P))
from build_wp_atlas import build, digest

class AtlasAdapterContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = build()
        cls.f = P / "dist/templates/atlas-fragment.html"
        cls.c = P / "dist/assets/atlas-scoped.css"
        cls.php = P / "dist/fv-ex2-apollo-r184.php"
        cls.s = BeautifulSoup(cls.f.read_text(), "html.parser")

    def test_checksum_and_reproducible_build(self):
        a = (digest(self.f.read_bytes()), digest(self.c.read_bytes()))
        self.assertEqual(a, (self.manifest["fragment_sha256"], self.manifest["css_sha256"]))
        build()
        self.assertEqual(a, (digest(self.f.read_bytes()), digest(self.c.read_bytes())))

    def test_no_second_main_or_duplicate_ids(self):
        self.assertIsNone(self.s.find("main"))
        self.assertIsNone(self.s.find("body"))
        self.assertEqual(len(self.s.select("article.fv-apollo-atlas")),1)
        ids = [el["id"] for el in self.s.select("[id]")]
        self.assertEqual(len(set(ids)), len(ids))
        for a in self.s.select("a[href^='#']"):
            self.assertIn(a["href"][1:], ids)

    def test_meaningful_no_js_evidence(self):
        self.assertEqual(len(self.s.select(".rail li")),4)
        self.assertEqual(len(self.s.select(".plate")),4)
        self.assertEqual(len(self.s.select(".source-card")),4)
        self.assertEqual(len(self.s.select("details summary")),8)
        self.assertIn("not conclusively", self.s.get_text(" ",strip=True))
        self.assertNotIn("NASA approved", self.s.get_text(" ",strip=True))
        self.assertFalse(self.s.select("script,iframe,img,form,video,[data-lat],[data-map-pin]"))

    def test_one_contextual_read_action(self):
        links = [a.get("href") for a in self.s.select("a.cta")]
        self.assertEqual(links, ["https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"])
        self.assertFalse(self.s.select('a[href*="payhip"],a[href*="awin1"]'))

    def test_all_css_scoped(self):
        css=self.c.read_text()
        self.assertNotIn("\nbody{",css)
        self.assertNotIn("\nhtml{",css)
        self.assertNotIn(":root{",css)
        self.assertIn(".fv-apollo-atlas .plate",css)

    def test_php_lints(self):
        res = subprocess.run(["php","-l",str(self.php)],capture_output=True,text=True,check=True)
        self.assertIn("No syntax errors",res.stdout)

    def test_php_runtime_fail_open(self):
        bootstrap = """<?php
        define('ABSPATH','/fakewp/');
        function add_shortcode($key,$callback){$GLOBALS['shortcode']=$callback;}
        function plugin_dir_path($p){return dirname($p).'/';}
        function plugins_url($path,$file){return 'https://staging.invalid/'.$path;}
        function wp_register_style($key,$src,$deps,$v){$GLOBALS['registered']=$key;}
        function wp_enqueue_style($key){$GLOBALS['enqueued']=$key;}
        require $argv[1];
        echo json_encode(array('html'=>fv_ex2_r184_render(),'enqueue'=>$GLOBALS['enqueued']??null));
        """
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)/"plugin"
            shutil.copytree(P/"dist",target)
            test = Path(d)/"run.php"
            test.write_text(bootstrap)
            def invoke():
                p=subprocess.run(["php",str(test),str(target/"fv-ex2-apollo-r184.php")],
                    capture_output=True,text=True,check=True)
                return json.loads(p.stdout)
            ok=invoke()
            self.assertEqual(ok["enqueue"],"fv-apollo-r184")
            self.assertIn("What the records support",ok["html"])
            (target/"assets/atlas-scoped.css").write_text("tampered")
            failed=invoke()
            self.assertIsNone(failed["enqueue"])
            self.assertIn("temporarily unavailable",failed["html"])

if __name__=="__main__":
    unittest.main()
