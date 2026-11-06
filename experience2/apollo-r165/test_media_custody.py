"""Deterministic actual Chromium synthetic srcset QA (not WordPress evidence)."""
from __future__ import annotations
import json
import random
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from urllib.parse import urlparse

from media_custody_witness import witness

SITE = "https://finalvestige.com"
FILES = ["apollo1-nasa-s66-58038.jpg", "apollo1-nasa-s67-15717.jpg", "apollo1-nasa-ksc-20170124-three-part-hatch.jpg"]
NASA = ["https://www.nasa.gov/image-detail/amf-s66-58038/", "https://www.nasa.gov/image-detail/amf-s67-15717/", "https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129"]


def png(seed):
    """Nontrivial deterministic 480x320 PNG; no paid or downloaded images."""
    rng = random.Random(seed)
    pixels = b"".join(b"\0" + rng.randbytes(480 * 3) for _ in range(320))
    def chunk(t, payload):
        return struct.pack(">I", len(payload)) + t + payload + struct.pack(">I", zlib.crc32(t + payload) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB",480,320,8,2,0,0,0)) + chunk(b"IDAT", zlib.compress(pixels, 9)) + chunk(b"IEND",b"")


def fixture():
    figures = []
    for i, (file, record) in enumerate(zip(FILES, NASA)):
        origin = f"{SITE}/wp-content/uploads/2026/11/{file}"
        proxy = f"https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/11/{file}?resize=1200,800"
        figures.append(f'<figure data-fvx-chrono-photo="{i}"><img alt="An archival NASA context photograph dated in the historical caption" src="{origin}" srcset="{origin} 240w, {proxy} 1200w" sizes="(max-width: 600px) 85vw, 700px"><figcaption><a href="{record}">NASA original record</a></figcaption></figure>')
    controls = ''.join(f'<button type="button" onclick="show({i})">View {i+1}</button>' for i in range(3))
    return f'''<!doctype html><html><head><style>
      body{{margin:0;background:#13110e;color:#f4eee2;font:18px Arial}}
      [data-fvx-chrono-gallery]{{width:min(94%,960px);margin:2rem auto}}
      figure{{margin:0}} img{{display:block;width:min(100%,700px);height:auto}}
      button{{min-height:44px;margin:.4rem;color:white;background:#38332b;border:1px solid #dac18a}}
      figcaption{{padding:1rem}} a{{color:#f0d9b4}}
    </style></head><body><main><h1>Apollo 1 | Historical media custody</h1>
    <section data-fvx-chrono-gallery><div class="fvx-archive-choice">{controls}</div>
    {''.join(figures)}</section></main><script>
    function show(i){{document.querySelectorAll('[data-fvx-chrono-photo]').forEach((f,j)=>f.hidden=i!==j);}}
    show(0);
    </script></body></html>'''


class MediaWitness(unittest.TestCase):
    def run_case(self, fail_cdn=False):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fixture.html"
            path.write_text(fixture())
            pngs = [png(401+i) for i in range(3)]
            def route(r):
                u = r.request.url
                i = next((i for i, file in enumerate(FILES) if file in u), None)
                if i is None:
                    r.fulfill(status=404, body=b"not found", content_type="text/plain")
                elif fail_cdn and urlparse(u).hostname == "i0.wp.com":
                    r.fulfill(status=503, body=b"proxy failure", content_type="text/plain")
                else:
                    r.fulfill(status=200, body=pngs[i], content_type="image/png")
            return witness(f"{SITE}/apollo-evidence-atlas/", Path(temp)/"out", fixture=path, intercept=route)

    def test_success_selected_current_src_is_cdn_and_body_is_measured(self):
        r=self.run_case()
        self.assertEqual((r["passed_checks"],r["total_checks"]),(r["total_checks"],r["total_checks"]))
        self.assertEqual(r["result"],"HOLD_OFFLINE_FIXTURE_ONLY")
        for row in r["widths"].values():
            self.assertEqual(len(row["images"]),3)
            for image in row["images"]:
                self.assertEqual(image["current_src_host"],"i0.wp.com")
                self.assertTrue(image["srcset_selected"])
                self.assertGreater(image["transferred_bytes"],512)
                self.assertEqual(image["http_status"],200)
                self.assertEqual(len(image["sha256_response_body"]),64)

    def test_proxied_candidate_breakage_is_not_mistaken_for_origin_success(self):
        r=self.run_case(fail_cdn=True)
        self.assertLess(r["passed_checks"],r["total_checks"])
        self.assertEqual(r["result"],"HOLD_OFFLINE_FIXTURE_FAIL")
        self.assertTrue(any(not im["checks"]["response_2xx"] for row in r["widths"].values() for im in row["images"]))

if __name__ == '__main__':
    unittest.main(verbosity=2)
