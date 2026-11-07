"""Archival network evidence: exact Blueprint sources and hostile URL controls.

Offline unit tests are not proof of a WordPress image transfer.
"""
import json
from html.parser import HTMLParser
from pathlib import Path
import unittest
from verify_archival_provenance import classify_source, verify_receipt, MEDIA, ORIGIN, BASE


class MediaContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bp=json.loads(Path(__file__).with_name("FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json").read_text())
        cls.php=bp["steps"][2]["data"]

    def test_two_approved_images_no_nypl_and_cdn_disclosed(self):
        class Images(HTMLParser):
            def __init__(self):
                super().__init__()
                self.images=[]
            def handle_starttag(self, tag, attrs):
                if tag == "img":
                    data=dict(attrs)
                    if "data-fv-archive-img" in data:
                        self.images.append(data)
        p=Images()
        p.feed(self.php)
        images=p.images
        self.assertEqual(len(images),2)
        self.assertNotIn("edit-017-v02-nypl",self.php)
        for i,img in enumerate(images):
            src=img["src"]
            self.assertTrue(img.get("alt"))
            original=classify_source(src,src,i)
            self.assertTrue(original["first_party"])
            self.assertEqual(original["media_id"],MEDIA[i]["id"])
            srcset=img.get("srcset","")
            self.assertTrue(srcset)
            for entry in srcset.split(", "):
                candidate=entry.split(" ")[0]
                selected=classify_source(src,candidate,i)
                self.assertFalse(selected["first_party"])
                self.assertEqual(selected["host"],"i0.wp.com")

    def test_reject_unapproved_exfiltration_and_malformed_derivatives(self):
        origin=f'https://{ORIGIN}{BASE}{MEDIA[0]["file"]}'
        bad=[
            "https://evil.example/a.webp",
            "https://i0.wp.com.evil.example/finalvestige.com"+BASE+"s67-19766.webp?fit=300%2C233&ssl=1",
            "http://i0.wp.com/finalvestige.com"+BASE+"s67-19766.webp?fit=300%2C233&ssl=1",
            "https://i0.wp.com/finalvestige.com"+BASE+"s67-19766.webp?fit=300%2C233&ssl=1&utm_campaign=secret",
            "https://i0.wp.com/finalvestige.com"+BASE+"s67-19766.webp?fit=333%2C333&ssl=1",
            "https://i0.wp.com/finalvestige.com"+BASE+"s67-19766.webp?fit=300%2C233&ssl=0",
            "https://i0.wp.com/finalvestige.com"+BASE+"s67-19766.webp?fit=300%2C233&ssl=1#junk",
            "https://i0.wp.com/finalvestige.com"+BASE+"s67-19766.webp?fit=300%2C233&ssl=1&fit=768%2C598",
            "https://finalvestige.com.evil.example"+BASE+"s67-19766.webp",
            "https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl.jpg?fit=300%2C233&ssl=1",
        ]
        for selected in bad:
            with self.subTest(selected=selected),self.assertRaises(ValueError):
                classify_source(origin,selected,0)
        with self.assertRaises(ValueError):
            classify_source("https://attacker.example/"+MEDIA[0]["file"],origin,0)

    def test_crossed_media_identity_rejected(self):
        a="https://finalvestige.com"+BASE+MEDIA[0]["file"]
        b="https://finalvestige.com"+BASE+MEDIA[1]["file"]
        with self.assertRaises(ValueError): classify_source(a,a,1)
        with self.assertRaises(ValueError): classify_source(b,b,0)

    def test_real_network_receipt_required_and_negative_cases(self):
        a="https://finalvestige.com"+BASE+MEDIA[0]["file"]
        src=classify_source(a,a,0)
        receipt={"format":"WEBP","width":1041,"height":810,"bytes":78346,"sha256":"a"*64}
        self.assertEqual(verify_receipt(src,receipt,200,"image/webp")["transfer_bytes"],78346)
        for status,kind,data in [
            (404,"image/webp",receipt),(200,"text/html",receipt),
            (200,"image/jpeg",receipt),(200,"image/webp",{**receipt,"width":1}),
            (200,"image/webp",{**receipt,"sha256":""}),
            (200,"image/webp",{**receipt,"bytes":0}),
        ]:
            with self.subTest(status=status,kind=kind,data=data),self.assertRaises(ValueError):
                verify_receipt(src,data,status,kind)


if __name__=="__main__":
    unittest.main(verbosity=2)
