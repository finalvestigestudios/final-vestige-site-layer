"""Verify outbound related-reading blocks on the five 2026-11-02 posts (public site).
Usage: python verify_outbound.py <slug> [<slug> ...]"""
import re, sys, json, time, collections, urllib.request, urllib.error

def get(u):
    for _ in range(4):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u + ("&" if "?" in u else "?") + "chk=%d" % time.time(), headers={"User-Agent": "Mozilla/5.0"}), timeout=40)
            return r.status, r.geturl(), r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, u, ""
        except Exception:
            time.sleep(2)
    return 0, u, ""

for slug in sys.argv[1:]:
    url = f"https://finalvestige.com/2026/11/02/{slug}/"
    s, _, h = get(url)
    blk = re.search(r'<div class="wp-block-group fv-related-reading.*?</div>', h, re.S)
    hrefs = re.findall(r'href="([^"]+)"', blk.group(0)) if blk else []
    link_status = {u: get(u)[:2] for u in hrefs}
    types = collections.Counter(re.findall(r'"@type":"(Article|FAQPage|BreadcrumbList)"', h))
    ld_ok = True
    for j in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', h, re.S):
        try: json.loads(j)
        except Exception: ld_ok = False
    faq_after_block = bool(blk) and h.find("fv-related-reading") < h.find('"FAQPage"') if '"FAQPage"' in h else None
    print(slug, dict(status=s, blocks=h.count('class="wp-block-group fv-related-reading'), links=len(hrefs),
          links_ok=all(v[0] == 200 and v[1].split('?')[0].rstrip('/') == k.rstrip('/') for k, v in link_status.items()),
          schema=dict(types), jsonld_parses=ld_ok, h1=len(re.findall(r"<h1[\s>]", h)), block_before_faq_jsonld=faq_after_block))
