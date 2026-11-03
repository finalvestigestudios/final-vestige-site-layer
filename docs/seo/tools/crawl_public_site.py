import json, re, sys, time, hashlib, urllib.request, urllib.error, html, subprocess
UA = "Mozilla/5.0 (compatible; FVSEOAudit/1.0)"
def get(url, tries=5):
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40)
            return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After", "5")) + 1); continue
            return e.code, ""
        except Exception as e:
            time.sleep(2)
    return 0, ""
urls = []
for kind in ("pages", "posts"):
    p = 1
    while True:
        s, b = get(f"https://finalvestige.com/wp-json/wp/v2/{kind}?per_page=100&page={p}&_fields=id,link,type,modified")
        if s != 200: break
        d = json.loads(b)
        for x in d: urls.append((x["type"], x["id"], x["link"], x["modified"]))
        if len(d) < 100: break
        p += 1
print("urls", len(urls), file=sys.stderr)
out = []
for typ, id_, link, mod in urls:
    s, h = get(link)
    time.sleep(0.4)
    def m(rx, flags=re.S | re.I):
        mm = re.search(rx, h, flags); return html.unescape(mm.group(1).strip()) if mm else None
    title = m(r"<title[^>]*>(.*?)</title>")
    desc = m(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>')
    canon = m(r'<link\s+rel=["\']canonical["\']\s+href=["\'](.*?)["\']')
    ogt = m(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']')
    ogd = m(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']')
    robots = m(r'<meta\s+name=["\']robots["\']\s+content=["\'](.*?)["\']')
    ld = re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', h, re.S | re.I)
    types = []
    for j in ld:
        try:
            o = json.loads(j)
            for n in (o.get("@graph", [o]) if isinstance(o, dict) else o):
                t = n.get("@type"); types.append(t if isinstance(t, str) else "/".join(t or []))
        except Exception: types.append("PARSE_ERROR")
    h1 = len(re.findall(r"<h1[\s>]", h, re.I))
    main = re.search(r"<main.*?</main>", h, re.S | re.I)
    body = main.group(0) if main else h
    links = re.findall(r'<a\s[^>]*href=["\'](.*?)["\']', body, re.I)
    internal = [l for l in links if l.startswith("https://finalvestige.com") or l.startswith("/")]
    out.append(dict(type=typ, id=id_, url=link, status=s, modified=mod, title=title, desc=desc, desc_len=len(desc) if desc else 0,
        title_len=len(title) if title else 0, canonical=canon, og_title=ogt, og_desc=ogd, robots=robots, jsonld=types, h1=h1,
        internal_links=len(internal), internal_targets=sorted(set(internal)), html_sha1=hashlib.sha1(h.encode()).hexdigest()))
json.dump(out, open(sys.argv[1], "w"), indent=1)
print("done", len(out), file=sys.stderr)
