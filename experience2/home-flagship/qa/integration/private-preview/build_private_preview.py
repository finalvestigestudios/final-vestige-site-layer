#!/usr/bin/env python3
"""Build a non-public, source-integrity-checked WordPress staging ZIP.

The old v0.1 builder placed index.html.txt and JS/CSS in web-readable
wp-content/plugins/.../assets/. This replacement embeds all exact source files
in a PHP-only payload (executable guarded PHP, never a public .txt/.js/.css).
Requires the existing Experience 2.0 source contract; rejects missing/extra
executables and does no network I/O, CMS writes, installs or publications.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import re
from pathlib import Path
import zipfile

PREFIX="fv-ex2-private-preview"


def php_payload(files: dict[str,bytes]) -> bytes:
    """PHP file is inert on anonymous direct GET (ABSPATH is not set)."""
    def php_literal(x: str) -> str:
        # only hashes, enumerated filenames and base64 reach this function
        assert re.fullmatch(r"[a-zA-Z0-9_.\-/+=]+", x), x[:50]
        return "'" + x + "'"
    hashes={k:hashlib.sha256(v).hexdigest() for k,v in files.items()}
    sha_rows=",\n".join(f"    {php_literal(k)} => {php_literal(v)}" for k,v in hashes.items())
    data_rows=",\n".join(f"    {php_literal(k)} => {php_literal(base64.b64encode(v).decode('ascii'))}" for k,v in files.items())
    return ("<?php\nif (!defined('ABSPATH')) { http_response_code(403); exit; }\n"
            "return [\n 'sha256' => [\n"+sha_rows+"\n ],\n 'data' => [\n"+data_rows+"\n ],\n];\n").encode("ascii")


def create(root:Path, plugin:Path, output:Path, expected_head:str, check_contract_module):
    checks, observations, errors = check_contract_module.scan(root)
    if errors: raise ValueError("Canonical source contract failed: " + "; ".join(errors))
    assets=check_contract_module.ASSETS
    if len(assets)!=len(set(assets)): raise ValueError("Duplicate asset names")
    files={name:(root/name).read_bytes() for name in assets}
    php=plugin.read_bytes()
    if not php.lstrip().startswith(b"<?php") or b"FV_EX2_ALLOW_PREVIEW" not in php:
        raise ValueError("Missing opt-in plugin guard")
    if re.search(rb"add_action\s*\(\s*['\"]wp_ajax_nopriv_",php):
        raise ValueError("Refusing public AJAX endpoint")
    if b"fv_ex2_private_compose" not in php or b"hash_equals" not in php or b"random_bytes" not in php:
        raise ValueError("Missing source-integrity or nonce-locked CSP")
    if not re.fullmatch(r"[0-9a-f]{40}",expected_head):
        raise ValueError("Expected Git head must be a 40-digit SHA, not a branch/ref")
    source_hash={name:hashlib.sha256(data).hexdigest() for name,data in files.items()}
    payload=php_payload(files)
    manifest={
        "release_status":"HOLD_UNPUBLISHED_STAGING_ONLY",
        "expected_git_head_given_by_caller":expected_head,
        "source_hashes":source_hash,
        "plugin_sha256":hashlib.sha256(php).hexdigest(),
        "payload_sha256":hashlib.sha256(payload).hexdigest(),
        "payload_in_php_executable_only":True,
        "included_files":["fv-ex2-private-preview.php","fv-ex2-private-payload.php"],
        "prohibited_files":["assets/index.html.txt", "assets/index.html", "assets/flagship.js", "assets/flagship.css"],
        "limitations":["No actual WordPress deployment or Staging install", "No independent WordPress/browser/assistive technology production certification", "Archived media rights unresolved", "GitHub CI/QD release gates still hold"]
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.writestr(f"{PREFIX}/fv-ex2-private-preview.php",php)
        z.writestr(f"{PREFIX}/fv-ex2-private-payload.php",payload)
        # These metadata artifacts disclose hashes but no unpublished HTML / CSS / JS.
        z.writestr(f"{PREFIX}/STAGING_MANIFEST.json",json.dumps(manifest,indent=2)+"\n")
        z.writestr(f"{PREFIX}/INSTALLATION_HOLD.txt",
            "UNPUBLISHED STAGING ONLY — DO NOT INSTALL OR ACTIVATE ON finalvestige.com.\n"
            "Install only on a separately approved private WordPress staging environment.\n"
            "Define('FV_EX2_ALLOW_PREVIEW',true) and WP_ENVIRONMENT_TYPE=staging,\n"
            "use the private [fv_ex2_homepage_preview_private] shortcode as an editor.\n"
            "Before release: independent CI/QD, WCAG 2.2 AA, photo rights, live CWV.\n"
            "All original source files are only embedded in guarded .php; no public assets.\n")
    return manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--expected-head',required=True)
    p.add_argument('--contract-dir',type=Path,required=True)
    args=p.parse_args()
    import sys
    sys.path.insert(0,str(args.contract_dir))
    import check_contract
    plugin=Path(__file__).with_name('fv-ex2-private-preview.php')
    report=create(args.root,plugin,args.out,args.expected_head,check_contract)
    print(json.dumps({"passed":True,"artifact":str(args.out),"bytes":args.out.stat().st_size,"asset_count":len(report['source_hashes']),"payload_sha256":report['payload_sha256']},indent=2))

if __name__=='__main__':main()
