#!/usr/bin/env python3
"""Prepare (and optionally launch) the isolated local WordPress that renders the candidate.

  python run_stage.py --work <dir outside repo> --assembler-zip <official zip> [--launch] [--port 9400]

Needs Node >= 20 and network access for `npx @wp-playground/cli` (free, no account). Nothing is
sent to, or imported from, finalvestige.com / WordPress.com. The Assembler ZIP is the unmodified
official archive; only its top-level folder is renamed assembler-wpcom/ -> assembler/.
"""
import argparse
import json
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PG_VERSION = "3.1.61"

SEED_PHP = r"""<?php
require_once '/wordpress/wp-load.php';
$host = strtolower((string) parse_url(home_url('/'), PHP_URL_HOST));
if (wp_get_environment_type() !== 'local' || !in_array($host, ['127.0.0.1', 'localhost'], true)) {
    throw new RuntimeException('REFUSED: not local loopback');
}
// Local throwaway admin: without unfiltered_html, KSES silently rewrites the markup on insert.
wp_set_current_user(1);
if (!current_user_can('unfiltered_html')) { throw new RuntimeException('admin lacks unfiltered_html'); }
$body = file_get_contents('/wordpress/wp-content/uploads/fv-ex2-stage/page-content.html');
if (!$body || strlen($body) < 50000) { throw new RuntimeException('page content missing'); }
// Production's homepage is page ID 6 and many live CSS rules are keyed to .page-id-6.
// The local copy takes the same ID so those selectors apply exactly as they do in production.
if (get_post(6)) { throw new RuntimeException('local post ID 6 already in use'); }
$id = wp_insert_post(wp_slash([
    'post_type' => 'page', 'post_status' => 'publish', 'post_title' => 'Final Vestige Studios',
    'post_name' => 'fv-flagship-candidate', 'post_content' => $body, 'comment_status' => 'closed',
    'import_id' => 6,
]), true);
if (!is_wp_error($id) && (int) $id !== 6) { throw new RuntimeException('page did not take ID 6: ' . $id); }
if (is_wp_error($id)) { throw new RuntimeException($id->get_error_message()); }
if (get_post_field('post_content', $id) !== $body) { throw new RuntimeException('READBACK MISMATCH'); }
update_option('show_on_front', 'page');
update_option('page_on_front', $id);
update_option('blogname', 'Final Vestige Studios');
update_option('permalink_structure', '/%postname%/');
flush_rewrite_rules();
echo 'seeded page ' . $id . ' bytes=' . strlen($body);
"""


def blueprint():
    return {
        "$schema": "https://playground.wordpress.net/blueprint-schema.json",
        "landingPage": "/",
        "preferredVersions": {"php": "8.3", "wp": "latest"},
        "steps": [
            {"step": "defineWpConfigConsts", "consts": {
                "WP_ENVIRONMENT_TYPE": "local", "WP_DEBUG": True, "WP_DEBUG_DISPLAY": False,
                "WP_DEBUG_LOG": True}},
            {"step": "activateTheme", "themeFolderName": "assembler"},
            {"step": "activatePlugin", "pluginPath": "fv-flagship-candidate/fv-flagship-candidate.php"},
            {"step": "runPHP", "code": SEED_PHP},
            {"step": "runPHP", "code": "<?php require_once '/wordpress/wp-load.php'; wp_set_current_user(1); "
                                       "require '/wordpress/wp-content/uploads/fv-ex2-parity/apply_local_parity.php';"},
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, type=Path)
    ap.add_argument("--assembler-zip", required=True, type=Path)
    ap.add_argument("--port", type=int, default=9400)
    ap.add_argument("--launch", action="store_true")
    ap.add_argument("--delivery", choices=["plugin", "inline"], default="plugin")
    ap.add_argument("--minify", default="", help="esbuild binary path to minify the flagship CSS/JS")
    ap.add_argument("--cli", default="", help="path to cli.js of an installed @wp-playground/cli")
    a = ap.parse_args()
    work = a.work.resolve()
    if work.is_relative_to(HERE.parent.parent.parent):
        sys.exit("work dir must be outside the checkout")
    stage = work / "stage"
    subprocess.run([sys.executable, str(HERE / "build_candidate.py"), "--out", str(stage), "--delivery", a.delivery] + (["--minify", a.minify] if a.minify else []), check=True)

    theme = work / "theme"
    theme.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(a.assembler_zip) as z:
        for m in z.infolist():
            if m.is_dir() or not m.filename.startswith("assembler-wpcom/"):
                continue
            dest = theme / "assembler" / m.filename[len("assembler-wpcom/"):]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(z.read(m))
    (work / "blueprint.json").write_text(json.dumps(blueprint(), indent=2), encoding="utf-8")

    mounts = [
        (theme / "assembler", "/wordpress/wp-content/themes/assembler"),
        (stage / "plugin" / "fv-flagship-candidate", "/wordpress/wp-content/plugins/fv-flagship-candidate"),
        (HERE / "parity", "/wordpress/wp-content/uploads/fv-ex2-parity"),
        (stage, "/wordpress/wp-content/uploads/fv-ex2-stage"),
    ]
    argv = (["node", a.cli] if a.cli else ["npx", "--yes", f"@wp-playground/cli@{PG_VERSION}"]) + [
        "server", f"--port={a.port}", f"--blueprint={work / 'blueprint.json'}"]
    # --mount-dir takes host and VFS paths as separate args, so Windows drive letters work.
    for src, dst in mounts:
        argv += ["--mount-dir", str(src), dst]
    (work / "launch-argv.json").write_text(json.dumps(argv, indent=2), encoding="utf-8")
    print(json.dumps(argv))
    if a.launch:
        subprocess.run(argv, check=True)


if __name__ == "__main__":
    main()
