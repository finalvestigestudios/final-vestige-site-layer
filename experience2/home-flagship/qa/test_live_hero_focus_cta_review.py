"""Synthetic adversarial fixtures only; separately inspect actual authenticated Page 6."""
import unittest
from live_hero_focus_cta_review import OLD,NEW,CHAPTERS,propose,digest

def fixture():
    return (''.join('<span class="fv-margin-strip__item">%d</span>'%i for i in range(72))+
            ''.join('<a href="#fv-hf-%s">%s</a>'%(x,x) for x in CHAPTERS)+OLD+
            '<img src="s67-19766.webp"><img src="Franklinexpeditionnote.jpg">'+
            '<img src="nypl-5003296-original.jpg"><img src="focus.webp">'+
            '<a href="https://finalvestige.com/focus/">One</a>'*2+
            '<a href="/focus/">Two</a>'*2+'<script>const untouched=1</script><!-- wp:html -->').encode()

class HeroExperiment(unittest.TestCase):
    def good(self,s):return propose(s,digest(s))
    def test_atomic_and_counts(self):
        s=fixture();n,r=self.good(s)
        self.assertEqual(n,s.replace(OLD.encode(),NEW.encode()))
        self.assertEqual((r['before']['focus'],r['after']['focus']),(4,5))
        self.assertEqual(r['release'],'HOLD')
    def test_sha_pin(self):
        with self.assertRaisesRegex(ValueError,'unpinned'):propose(fixture())
    def test_source_modified(self):
        s=fixture();
        with self.assertRaisesRegex(ValueError,'unpinned'):propose(s+b' ',digest(s))
    def test_bad_hero(self):
        for s in (fixture().replace(OLD.encode(),b''),fixture()+OLD.encode(),fixture().replace(OLD.encode(),NEW.encode())):
            with self.subTest(s=s[-30:]),self.assertRaisesRegex(ValueError,'hero action'):self.good(s)
    def test_margins_drift(self):
        s=fixture().replace(b'<span class="fv-margin-strip__item">0</span>',b'')
        with self.assertRaisesRegex(ValueError,'structure'):self.good(s)
    def test_chapters_drift(self):
        s=fixture().replace(b'href="#fv-hf-observer"',b'href="#missing"')
        with self.assertRaisesRegex(ValueError,'structure'):self.good(s)
    def test_archive_drift(self):
        s=fixture().replace(b'Franklinexpeditionnote.jpg',b'other.jpg')
        with self.assertRaisesRegex(ValueError,'structure'):self.good(s)
    def test_focus_count_drift(self):
        s=fixture()+b'<a href="/focus/">Extra</a>'
        with self.assertRaisesRegex(ValueError,'structure'):self.good(s)
    def test_no_new_external_domains(self):
        s=fixture();n,_=self.good(s)
        self.assertNotIn(b'awin1.com',n);self.assertNotIn(b'utm_campaign',n)

if __name__=='__main__':unittest.main()
