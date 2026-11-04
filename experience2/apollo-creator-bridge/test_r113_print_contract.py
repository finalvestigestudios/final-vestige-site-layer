"""R113 exact-source print fidelity contracts. Not browser/WordPress acceptance."""
from pathlib import Path
from html.parser import HTMLParser
import unittest
ROOT=Path(__file__).resolve().parent
HTML=(ROOT/"landing-preview.html").read_text(encoding="utf-8")
RUN=(ROOT/"qa_r113_print.py").read_text(encoding="utf-8")
class Parse(HTMLParser):
    def __init__(self):super().__init__();self.nodes=[]
    def handle_starttag(self,t,attrs):self.nodes.append((t,dict(attrs)))
class R113(unittest.TestCase):
    def test_print_has_full_evidence(self):
        self.assertIn(".plate[hidden]{display:block!important}",HTML)
        self.assertIn(".table-scroll{overflow:visible!important",HTML)
        self.assertIn("min-width:0!important;table-layout:fixed",HTML)
        self.assertIn("all four findings",HTML)
    def test_sources_and_commerce(self):
        p=Parse();p.feed(HTML)
        self.assertEqual(sum("data-fv-claim" in x for _,x in p.nodes),4)
        self.assertEqual(sum("data-fv-photo-record" in x for _,x in p.nodes),6)
        self.assertEqual(sum(x.get("id","").startswith("photo-source-") for _,x in p.nodes),6)
        self.assertEqual(sum("data-fv-primary-cta" in x for _,x in p.nodes),1)
        self.assertFalse(any(t=="form" for t,_ in p.nodes))
        self.assertFalse(any("payhip" in x.get("href","").lower() for _,x in p.nodes))
    def test_browser_runner_contract(self):
        self.assertIn("page.set_content(body",RUN)
        self.assertIn("page.emulate_media(media='print')",RUN)
        self.assertIn("page.keyboard.press('Enter')",RUN)
        self.assertIn("reduced_motion='reduce'",RUN)
        self.assertIn("len(record['performance'])==6",RUN)
        self.assertIn("record['complete']=True",RUN)
if __name__=="__main__":unittest.main()
