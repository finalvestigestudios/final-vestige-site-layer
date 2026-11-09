"""Mutation controls for EX2 below-fold image policy; no live network."""
import unittest
from verify_belowfold_media import validate

NAV=('fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title')
PHOTO='https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp'
FRANKLIN='https://finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg'
NYPL='https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg'

def fixture():
    return ('<html><main data-fv-home-flagship><section id="fv-hf-title"></section>'
            '<section id="fv-hf-chronicle"></section>'
            '<section id="fv-hf-evidence">'
            f'<img src="{PHOTO}" alt="Apollo 1 astronauts Grissom White and Chaffee" width="1041" height="810" loading="lazy" decoding="async" data-fv-archive-img>'
            f'<img src="{FRANKLIN}" alt="Note" width="960" height="1526" loading="lazy">'
            f'<img src="{NYPL}" alt="Map" width="1024" height="692" loading="lazy">'
            '</section>' + ''.join(f'<a href="#{id}">Chapter</a>' for id in NAV)
            + '<a href="https://finalvestige.com/focus/">Fieldbook</a></main></html>')

class ImagePriorityTests(unittest.TestCase):
    def test_control_pass(self):self.assertEqual(validate(fixture()),[])
    def test_eager_rejected(self):self.assertTrue(validate(fixture().replace('loading="lazy"','loading="eager"',1)))
    def test_high_priority_rejected(self):self.assertTrue(validate(fixture().replace('decoding="async"','fetchpriority="high" decoding="async"',1)))
    def test_duplicate_photo_rejected(self):self.assertTrue(validate(fixture().replace('</section>','<img src="'+PHOTO+'"></section>',1)))
    def test_missing_note_rejected(self):self.assertTrue(validate(fixture().replace(FRANKLIN,'example.invalid')))
    def test_missing_map_rejected(self):self.assertTrue(validate(fixture().replace(NYPL,'example.invalid')))
    def test_missing_alt_rejected(self):self.assertTrue(validate(fixture().replace('alt="Apollo 1 astronauts Grissom White and Chaffee"','')))
    def test_chapter_link_rejected(self):self.assertTrue(validate(fixture().replace('href="#fv-hf-inquiry"','href="#absent"')))
    def test_missing_focus_rejected(self):self.assertTrue(validate(fixture().replace('https://finalvestige.com/focus/','about:blank')))
    def test_missing_root_rejected(self):self.assertTrue(validate(fixture().replace('data-fv-home-flagship','data-test')))
    def test_second_image_lost_lazy_rejected(self):self.assertTrue(validate(fixture().replace('height="1526" loading="lazy"','height="1526" loading="eager"')))
    def test_first_image_lost_geometry_rejected(self):self.assertTrue(validate(fixture().replace('width="1041"','width="100"')))

if __name__=='__main__':unittest.main()
