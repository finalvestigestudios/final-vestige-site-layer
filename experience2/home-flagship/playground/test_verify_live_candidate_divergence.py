import unittest
from verify_live_candidate_divergence import scan,evaluate,sha_blob,ANCHORS

class ReadOnlyDriftTests(unittest.TestCase):
    def markup(self,nypl=False,early=False):
        nodes=''.join('<div id="%s"></div>'%a for a in ANCHORS)
        records='<span class="fv-margin-strip__item"></span>'*72
        margins='<div class="fv-margin-strip fv-margin-strip--rotator">'+records+'</div>'
        hero='<div data-fv-home-flagship>'+nodes+'</div>'
        imgs='<img src="https://finalvestige.com/s67-19766.webp"><img src="https://finalvestige.com/Franklinexpeditionnote.jpg">'
        if nypl: imgs+='<img src="https://i0.wp.com/finalvestige.com/edit-017-v02-nypl-5003296-original.jpg?fit=1024%2C692&amp;ssl=1">'
        return (margins+hero if early else hero+margins)+imgs+'<a href="https://finalvestige.com/focus/">Focus</a>'
    def test_detect_margin_order(self):
        self.assertTrue(scan(self.markup(early=True))['margin_before_hero'])
        self.assertFalse(scan(self.markup())['margin_before_hero'])
    def test_approved_image_vs_rights_pending_image(self):
        a=scan(self.markup(nypl=True));b=scan(self.markup());self.assertEqual(a['images_total'],3)
        self.assertEqual(b['images_total'],2);self.assertEqual(a['image_media']['edit-017-v02-nypl-5003296-original.jpg'],1)
        self.assertEqual(b['image_media']['edit-017-v02-nypl-5003296-original.jpg'],0)
    def test_same_chapters_do_not_make_live_identical(self):
        live=scan(self.markup(nypl=True,early=True));candidate=scan(self.markup());a=evaluate(live,candidate)
        self.assertTrue(a['live_seven_chapter_core']);self.assertTrue(a['candidate_seven_chapter_core'])
        self.assertEqual(a['gate'],'RELEASE_HOLD_LIVE_CANDIDATE_DIFFER')
    def test_missing_chapter_fails_core(self):
        live=scan(self.markup().replace('fv-hf-observer','not-a-chapter'))
        self.assertFalse(evaluate(live,scan(self.markup()))['live_seven_chapter_core'])
    def test_entities_preserve_media_domain(self):
        u=scan('<img src="https://i0.wp.com/finalvestige.com/s67-19766.webp?fit=300%2C233&amp;ssl=1">')
        self.assertEqual(u['image_cdn'],1);self.assertEqual(u['image_src_hosts'],['i0.wp.com'])
    def test_git_blob_hash_is_content_sensitive(self):
        self.assertNotEqual(sha_blob(b'abc'),sha_blob(b'abd'))

if __name__=='__main__':unittest.main()
