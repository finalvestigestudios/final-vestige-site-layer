#!/usr/bin/env python3
"""Offline, read-only WordPress Playground launcher for a PRIVATE GitHub Blueprint.
This does not run or certify WordPress, does not write to the live CMS.
"""
import argparse
import base64
import hashlib
import html
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

BLOB = "455c6cccbf8a00e6ecc4c2524775010d7ee1762c"
ASSEMBLER = "75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f"
CHAPTERS = ("fv-hf-title", "fv-hf-chronicle", "fv-hf-evidence", "fv-hf-inquiry",
            "fv-hf-method-title", "fv-hf-observer", "fv-hf-mind-title")


def validate(raw):
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob != BLOB:
        raise ValueError("Exact GitHub Blueprint blob mismatch; refuse to package")
    obj = json.loads(raw)
    steps = obj.get("steps", [])
    if [s.get("step") for s in steps] != ["installTheme", "mkdir", "writeFile", "runPHP", "runPHP"]:
        raise ValueError("Unexpected WordPress installation steps")
    theme = steps[0]["themeData"]
    if (theme.get("resource"), theme.get("path"), theme.get("ref")) != ("git:directory", "assembler", ASSEMBLER):
        raise ValueError("Theme is not exact pinned Assembler")
    if steps[2].get("path") != "/wordpress/wp-content/mu-plugins/fv-ex2-playground-review.php":
        raise ValueError("Plugin path mismatch")
    php = steps[2]["data"]
    if (php.count('class="fv-margin-strip__item"') != 72 or
        php.count('href="https://finalvestige.com/focus/"') != 5 or
        any(php.count('id="' + id + '"') != 1 for id in CHAPTERS)):
        raise ValueError("72 records, five Focus links or seven chapters changed")
    if "fv_ex2_playground_review_only" not in php or "NOT LIVE" not in php:
        raise ValueError("Review-only safety fence missing")
    if "FV_EX2_WORDPRESS_IMPORT_ADMISSION_PASS" not in steps[4]["code"]:
        raise ValueError("WordPress integration gate missing")
    return blob


def package(blueprint, output):
    raw = Path(blueprint).read_bytes()
    blob = validate(raw)
    fragment = base64.b64encode(raw).decode("ascii")
    link = "https://playground.wordpress.net/#" + fragment
    # The link sends no Blueprint in an HTTP request; its URL fragment is
    # processed by Playground's own browser code. No secrets may be included.
    page = ('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>FV Private Playground Review</title><style>
:root{color-scheme:dark;background:#0b0e0e;color:#f3ecdf;font:17px/1.6 system-ui,sans-serif}*{box-sizing:border-box}body{margin:0;padding:1rem;min-height:100vh;display:grid;place-items:center}main{width:min(100%,680px);padding:clamp(1rem,5vw,3rem);min-width:0;overflow-wrap:anywhere;border:1px solid #675741;background:#13201f}h1{font:normal clamp(2rem,5vw,3rem)/1.15 Georgia,serif}a{display:inline-block;min-height:44px;max-width:100%;background:#d4ad73;color:#12110f;padding:.9rem 1.1rem;font-weight:bold;overflow-wrap:anywhere}a:focus-visible{outline:3px solid white;outline-offset:4px}small{color:#ccbda7}</style><body><main><h1>Final Vestige: Unpublished Archive</h1><p>Local, source-pinned, seven-chapter WordPress Playground review using Assembler. No subscriber, account or private database imports.</p><p><a href="''' + html.escape(link, quote=True) + '''" target="_blank" rel="noreferrer noopener">Open isolated Playground review ↗</a></p><p><strong>Review only.</strong> Verify actual WordPress startup, 72 historical records, image transfers, keyboard and no-JS, axe accessibility, measured Lighthouse, and Focus CTA. No production edits or release approval.</p><small>Git blob: ''' + blob + '''. This launcher has no scripts or analytics; the Blueprint source remains in your browser's URL fragment.</small></main></body></html>''').encode()
    manifest = dict(blob_sha1=blob, blueprint_sha256=hashlib.sha256(raw).hexdigest(),
                    assembler_commit=ASSEMBLER, chapters=7, margins=72, focus_links=5,
                    wordpress_boot="NOT_TESTED", rights="NOT_CERTIFIED", wcag="NOT_TESTED",
                    revenue="NOT_VERIFIED")
    items = {"blueprint.json":raw,"launch_review.html":page,
             "manifest.json":(json.dumps(manifest,indent=2)+"\n").encode()}
    with ZipFile(output,"w") as z:
        for name,content in items.items():
            info=ZipInfo(name,(2026,11,6,12,0,0));info.compress_type=ZIP_DEFLATED
            z.writestr(info,content)
    print(json.dumps(dict(output=str(output),size=Path(output).stat().st_size,**manifest),indent=2))


if __name__ == "__main__":
    p=argparse.ArgumentParser();p.add_argument("--blueprint",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();package(a.blueprint,a.output)
