#!/usr/bin/env python3
"""Read-only first-party archival image byte gate for FV Experience 2.

Default mode is an OFFLINE contract preflight. --network is explicit and
performs three HTTPS GET requests to fixed first-party media URLs only.
Never writes to WordPress. Never treats a rights statement as a transfer test.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import urllib.request
from urllib.parse import urlsplit

LIMIT = 8_000_000
MEDIA = (
    {"wp_id": 473, "name": "NASA Apollo 1 S67-19766", "file": "s67-19766.webp", "bytes": 78346, "mime": "image/webp"},
    {"wp_id": 474, "name": "Franklin Victory Point note 1869 reproduction", "file": "Franklinexpeditionnote.jpg", "bytes": 466043, "mime": "image/jpeg"},
    {"wp_id": 1258, "name": "NYPL Brooklyn rapid transit map 5003296", "file": "edit-017-v02-nypl-5003296-original.jpg", "bytes": 5553669, "mime": "image/jpeg"},
)
BASE = "https://finalvestige.com/wp-content/uploads/2026/08/"

class GateFailure(ValueError):
    pass

def media_url(row):
    return BASE + row["file"]

def validate_location(url, expected):
    p = urlsplit(url)
    if p.scheme != "https" or p.hostname != "finalvestige.com" or p.port not in (None, 443):
        raise GateFailure(f"unexpected host/scheme/port: {url}")
    if p.path != urlsplit(expected).path or p.query or p.fragment or p.username or p.password:
        raise GateFailure(f"unexpected media destination: {url}")

def is_image(data, mime):
    if mime == "image/webp":
        return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    if mime == "image/jpeg":
        return len(data) >= 4 and data[:3] == b"\xff\xd8\xff" and data[-2:] == b"\xff\xd9"
    return False

def inspect(row, opener=None):
    """Requires exact-sized, valid original bytes (not CDN derivatives)."""
    url = media_url(row)
    validate_location(url, url)
    opener = opener or urllib.request.urlopen
    request = urllib.request.Request(url, headers={"User-Agent": "FV-EX2-read-only-media-admission/1.0", "Accept": row["mime"]}, method="GET")
    h = hashlib.sha256()
    buf = bytearray()
    with opener(request, timeout=18) as response:
        validate_location(response.geturl(), url)
        if getattr(response, "status", None) != 200:
            raise GateFailure("expected HTTP 200")
        content_type = response.headers.get("Content-Type", "").split(";",1)[0].lower().strip()
        if content_type != row["mime"]:
            raise GateFailure(f"unexpected Content-Type {content_type}")
        while True:
            chunk = response.read(64_000)
            if not chunk:
                break
            buf.extend(chunk)
            h.update(chunk)
            if len(buf) > LIMIT or len(buf) > row["bytes"]:
                raise GateFailure("too many bytes / unexpected transfer size")
    if len(buf) != row["bytes"]:
        raise GateFailure(f"expected {row['bytes']} bytes, received {len(buf)}")
    if not is_image(buf, row["mime"]):
        raise GateFailure("invalid image magic/trailer")
    return {"wp_id":row["wp_id"],"url":url,"bytes":len(buf),"mime":content_type,"sha256":h.hexdigest(),"transfer":"PASS"}

def run(network=False, opener=None):
    rows=[]
    for record in MEDIA:
        url=media_url(record)
        validate_location(url,url)
        if network:
            try: rows.append(inspect(record,opener))
            except Exception as exc: rows.append({"wp_id":record["wp_id"],"url":url,"transfer":"FAIL","reason":str(exc)})
        else: rows.append({"wp_id":record["wp_id"],"url":url,"wp_reported_bytes":record["bytes"],"mime":record["mime"],"transfer":"NOT_TESTED"})
    return {"scope":"READ_ONLY", "endpoint":"FIRST_PARTY_ORIGINALS_ONLY", "source":"WordPress media IDs 473,474,1258 re-read 2026-11-10", "rights_gate":"SEPARATE", "network_attempted":network,"all_pass": bool(network and all(r["transfer"]=="PASS" for r in rows)), "records":rows}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--network',action='store_true',help='explicitly GET three immutable hard-coded public first-party files')
    p.add_argument('--out',type=pathlib.Path,help='write JSON report to local disk only')
    a=p.parse_args()
    report=run(a.network)
    rendered=json.dumps(report,indent=2,sort_keys=True)
    if a.out: a.out.write_text(rendered+'\n',encoding='utf-8')
    print(rendered)
    if a.network and not report['all_pass']: raise SystemExit(1)
