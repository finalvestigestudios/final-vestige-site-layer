#!/usr/bin/env python3
"""Build the isolated, local-only WordPress release candidate for the flagship homepage.

Inputs (all committed):
  ../index.html + css/js            the seven-chapter Experience 2.0 flagship (PR #550)
  snapshot/page6-live-frontend-body.html   public rendered body of live page 6 (read-only snapshot)
  parity/                           public-safe Assembler header/footer/page template parity

Output directory (never inside the git checkout):
  plugin/fv-flagship-candidate/     enqueues the flagship CSS/JS on the front page only
  page-content.html                 the composed page body (this is the proposed production body)
  stage-manifest.json               sha256 of every produced byte

Composition rule: the live page keeps EVERYTHING it has today (72 Margins strip, Focus CTA,
Jetpack subscription, journal links, schema) except the old "Studios hero" section, which the
seven-chapter flagship replaces. The flagship drops its own studio banner, masthead and footer
because the Assembler header/footer already render around post-content, and its <main> becomes
a <div> because the page template already provides the single <main> landmark.
"""
import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FLAG = HERE.parent
SITE_CSS = ["site-parity.css", "live-block-support.css"]  # production emits these inline in <head>
FLAG_CSS = ["flagship.css", "chronicle.css", "chronicle-lens.css", "inquiry.css",
            "observer-lab.css", "reading-trail.css", "wp-integration.css"]  # shipped as ONE bundle
ASSETS_JS = ["flagship.js", "observer-lab.js", "chronicle-lens.js", "reading-trail.js"]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def extract(pattern, text, what):
    m = re.search(pattern, text, re.S)
    if not m:
        raise SystemExit(f"index.html no longer contains expected {what}")
    return m


def flagship_fragment(index_html: str) -> str:
    skip = extract(r'<a class="fv-hf__skip"[^>]*>.*?</a>', index_html, "skip link").group(0)
    nav = extract(r'<nav class="fv-hf__chapter-nav".*?</nav>', index_html, "chapter nav").group(0)
    main = extract(r'<main>(.*?)</main>', index_html, "main landmark").group(1)
    return (
        '<div class="fv-hf fv-hf--wp alignfull" data-fv-home-flagship>\n'
        '  <div class="fv-hf__canvas">\n'
        f'    {skip}\n{nav}\n    <div class="fv-hf__main">{main}</div>\n'
        '  </div>\n</div>\n'
    )


def compose(page6: str, fragment: str) -> str:
    a = page6.index('<section class="fv-studios-hero"')
    b = page6.index('<section class="fv-focus-cta"')
    before, after = page6[:a], page6[b:]
    if "fv-margin-strip" not in before or "fv-focus-cta" not in after:
        raise SystemExit("snapshot layout changed; re-review the composition")
    blk = lambda s: f"<!-- wp:html -->\n{s.strip()}\n<!-- /wp:html -->\n\n"
    return blk(before) + blk(fragment) + blk(after)


PLUGIN_PHP = r"""<?php
/**
 * Plugin Name: FV Flagship Candidate (local review only)
 * Description: Enqueues the seven-chapter flagship CSS/JS on the front page. Local staging only.
 * Version: 0.1.0
 */
if (!defined('ABSPATH')) { exit; }
// Local review safety: the preserved Jetpack form posts to wordpress.com/email-subscriptions
// (the real production list). Refuse any cross-origin form submission from this copy.
add_action('send_headers', function () {
    header("Content-Security-Policy: form-action 'self'");
});
add_action('wp_enqueue_scripts', function () {
    if (!is_front_page()) { return; }
    $base = plugin_dir_url(__FILE__) . 'assets/';
    $dir  = plugin_dir_path(__FILE__) . 'assets/';
    // Production prints the site-wide CSS inline (global styles); do the same so the stage does
    // not add stylesheet round trips that the real site does not have.
    wp_register_style('fv-hf-site', false);
    wp_enqueue_style('fv-hf-site');
    wp_add_inline_style('fv-hf-site', file_get_contents($dir . 'site-parity.css') . "
" . file_get_contents($dir . 'live-block-support.css'));
    wp_enqueue_style('fv-hf-bundle', $base . 'flagship.bundle.css', ['fv-hf-site'], filemtime($dir . 'flagship.bundle.css'));
    foreach (%JS% as $f) {
        wp_enqueue_script('fv-hf-' . basename($f, '.js'), $base . $f, [], filemtime($dir . $f), ['strategy' => 'defer', 'in_footer' => true]);
    }
});
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--delivery", choices=["plugin", "inline"], default="plugin",
                    help="plugin: flagship CSS/JS enqueued by a plugin; inline: CSS/JS ship inside the page block itself (no plugin)")
    ap.add_argument("--minify", metavar="ESBUILD_BIN", help="path to an esbuild binary/cmd; minifies the flagship CSS bundle and JS (visual/behavioural parity is re-tested by qa/run_wp_qa.py)")
    ap.add_argument("--page6", type=Path, default=HERE / "snapshot" / "page6-live-frontend-body.html")
    a = ap.parse_args()
    out = a.out.resolve()
    if FLAG in out.parents or out == FLAG:
        sys.exit("output must live outside the checkout")
    index = (FLAG / "index.html").read_text(encoding="utf-8")
    page6 = a.page6.read_text(encoding="utf-8")
    fragment = flagship_fragment(index)
    parts = []
    for f in FLAG_CSS:
        src = (FLAG / f) if (FLAG / f).exists() else (HERE / f)
        parts.append("/* ==== " + f + " ==== */" + chr(10) + src.read_text(encoding="utf-8").rstrip() + chr(10))
    css_bundle = "".join(parts)
    if a.minify:
        import subprocess
        mini = lambda text, loader: subprocess.run([a.minify, "--minify", "--loader=" + loader, "--legal-comments=none"], input=text.encode("utf-8"), capture_output=True, check=True).stdout.decode("utf-8")
        css_bundle = mini(css_bundle, "css")
    inline_block = ""
    if a.delivery == "inline":
        read_js = (lambda f: mini((FLAG / f).read_text(encoding="utf-8"), "js")) if a.minify else (lambda f: (FLAG / f).read_text(encoding="utf-8").rstrip())
        js = "".join("<script>" + chr(10) + read_js(f).rstrip() + chr(10) + "</script>" + chr(10) for f in ASSETS_JS)
        if "</script" in "".join((FLAG / f).read_text(encoding="utf-8") for f in ASSETS_JS).lower():
            raise SystemExit("a JS asset contains </script; cannot inline")
        inline_block = "<style>" + chr(10) + css_bundle + "</style>" + chr(10) + js
        # Visitors view-source: drop internal authoring comments (CSS /* */ and HTML <!-- -->) from the
        # shipped block. wp:html markers are added later and are unaffected.
        css_only = css_bundle
        stripped = re.sub(r"/\*.*?\*/", "", css_only, flags=re.S)
        inline_block = inline_block.replace(css_only, stripped, 1)
        fragment = re.sub(r"<!--.*?-->", "", fragment, flags=re.S)
        fragment = fragment + inline_block
    body = compose(page6, fragment)

    plug = out / "plugin" / "fv-flagship-candidate"
    if out.exists():
        shutil.rmtree(out)
    (plug / "assets").mkdir(parents=True)
    # Live site-wide CSS (dark body, link/selection rules, header/footer chrome) as captured in the
    # public-safe parity file. WordPress drops styles.css from a seeded wp_global_styles record
    # (KSES/edit_css), so ship the identical bytes as a plain stylesheet for the local review.
    parity = json.loads((HERE / "parity" / "assembler-public-safe.json").read_text(encoding="utf-8"))
    (plug / "assets" / "site-parity.css").write_text(parity["global_styles"]["styles"]["css"], encoding="utf-8")
    shutil.copyfile(HERE / "snapshot" / "live-block-support.css", plug / "assets" / "live-block-support.css")
    for f in ASSETS_JS:
        shutil.copyfile(FLAG / f, plug / "assets" / f)
    bundle = css_bundle
    (plug / "assets" / "flagship.bundle.css").write_text(bundle, encoding="utf-8")
    php = PLUGIN_PHP.replace("%JS%", json.dumps([] if a.delivery == "inline" else ASSETS_JS).replace('"', "'"))
    if a.delivery == "inline":
        php = php.replace("    wp_enqueue_style('fv-hf-bundle'", "    // inline delivery: flagship CSS/JS live inside the page block" + chr(10) + "    // wp_enqueue_style('fv-hf-bundle'")
    (plug / "fv-flagship-candidate.php").write_text(php, encoding="utf-8")
    (out / "page-content.html").write_text(body, encoding="utf-8")
    if a.delivery == "inline":
        blk = "<!-- wp:html -->" + chr(10) + (fragment).strip() + chr(10) + "<!-- /wp:html -->" + chr(10)
        (out / "production-replacement-block.html").write_text(blk, encoding="utf-8")

    manifest = {"schema": "fv-flagship-candidate-stage-v1", "local_only": True,
                "files": {str(p.relative_to(out)).replace("\\", "/"): sha(p.read_bytes())
                          for p in sorted(out.rglob("*")) if p.is_file()},
                "page6_snapshot_sha256": sha(page6.encode("utf-8")),
                "index_html_sha256": sha(index.encode("utf-8"))}
    (out / "stage-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"page_bytes": len(body), "files": len(manifest["files"])}))


if __name__ == "__main__":
    main()
