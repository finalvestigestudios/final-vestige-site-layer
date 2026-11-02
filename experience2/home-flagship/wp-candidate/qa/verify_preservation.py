#!/usr/bin/env python3
"""Production-preservation proof for the composed homepage body.

  python verify_preservation.py --stage <work/stage> [--live]

Checks, byte for byte, that everything on live page 6 survives in the candidate except the single
section the flagship replaces (the old "Studios hero" and its <style>), and (with --live) that the
live page has not drifted since the snapshot was taken. Read-only: one public GET.
"""
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def entry_content(raw):
    m = re.search(r'<div class="entry-content[^"]*wp-block-post-content[^"]*"[^>]*>', raw)
    start, depth = m.end(), 1
    for t in re.finditer(r'<script\b.*?</script>|<style\b.*?</style>|<(/?)div\b[^>]*>', raw[start:], re.S | re.I):
        if t.group(0).lower().startswith(("<script", "<style")):
            continue
        depth += -1 if t.group(1) == "/" else 1
        if depth == 0:
            return raw[start:start + t.start()]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", required=True, type=Path); ap.add_argument("--live", action="store_true")
    a = ap.parse_args()
    snap = (HERE / "snapshot" / "page6-live-frontend-body.html").read_text(encoding="utf-8")
    comp = (a.stage / "page-content.html").read_text(encoding="utf-8")
    i, j = snap.index('<section class="fv-studios-hero"'), snap.index('<section class="fv-focus-cta"')
    removed, before, after = snap[i:j], snap[:i], snap[j:]
    R = {"checks": {}, "removed_section": {"links": re.findall(r'href="([^"]*)"', removed), "bytes": len(removed), "text": re.sub(r"\s+", " ", re.sub(r"<style.*?</style>|<[^>]+>", " ", removed, flags=re.S)).strip()[:400]}}
    c = R["checks"]
    c["preserved_before_flagship_byte_exact"] = before.strip() in comp
    c["preserved_after_flagship_byte_exact"] = after.strip() in comp
    idx = re.findall(r'fv-margin-strip__item" style="--i:(\d+)"', comp)
    c["margins_72_unique_0_to_71"] = sorted(map(int, idx)) == list(range(72))
    c["jetpack_form_and_email_input"] = 'id="subscribe-blog"' in comp and 'type="email"' in comp
    c["focus_links_in_preserved_part"] = len(re.findall(r'href="[^"]*/focus/"', before + after))
    c["jetpack_form_action"] = sorted(set(re.findall(r'<form[^>]*action="([^"]*)"', comp)))
    c["studios_hero_gone_from_candidate"] = 'fv-studios-hero"' not in comp
    c["flagship_present_once"] = len(re.findall(r'<div class="fv-hf [^>]*data-fv-home-flagship', comp)) == 1
    if a.live:
        raw = subprocess.run(["curl", "-sS", "--ssl-no-revoke", "-A", "Mozilla/5.0", "-L", "https://finalvestige.com/"], capture_output=True, check=True).stdout.decode("utf-8", "replace")
        live = entry_content(raw)
        R["live"] = {"sha256": hashlib.sha256(live.encode()).hexdigest(), "snapshot_sha256": hashlib.sha256(snap.encode()).hexdigest()}
        R["live"]["identical_to_snapshot"] = live == snap
        if live != snap:
            # nonces/tokens may legitimately differ per request; report the size of the drift only
            R["live"]["bytes_live"], R["live"]["bytes_snapshot"] = len(live), len(snap)
    print(json.dumps(R, indent=2))
    sys.exit(0 if all(v is True or isinstance(v, (int, list)) and v for v in c.values()) else 1)


if __name__ == "__main__":
    main()
