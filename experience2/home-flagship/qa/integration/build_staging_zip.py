#!/usr/bin/env python3
"""Package an unpublished WordPress capability-gated Experience 2.0 preview ZIP.

Requires exact code-checkout assets. Neither activates nor installs WordPress.
Refuses to build if local design-source contract fails, avoiding silent partial
bundles or unreviewed executable dependencies.
"""
from __future__ import annotations
import argparse,hashlib,json,io,zipfile,re
from pathlib import Path
from check_contract import scan,ASSETS

PREFIX="fv-ex2-staging-preview"

def build(source:Path,tool_dir:Path,target:Path,expected_sha:str):
    checks,observations,errors=scan(source)
    if errors:raise ValueError("Contract failed; not packaging: "+"; ".join(errors))
    php=(tool_dir/"fv-ex2-preview.php").read_bytes()
    if re.search(rb"add_action\s*\(\s*['\"]wp_ajax_nopriv_", php):
        raise ValueError("Preview plugin must never register a public Ajax endpoint")
    if b"FV_EX2_ALLOW_PREVIEW" not in php or b"fv_ex2_preview_authorized" not in php:
        raise ValueError("No explicit staging capability gate")
    manifest={
        "status":"UNPUBLISHED_STAGING_ONLY_DO_NOT_ACTIVATE_ON_PRODUCTION",
        "source_expected_git_head":expected_sha,
        "note":"Source SHA provided by caller; asset hashes are derived from local bytes, not GitHub attestation.",
        "wordpress_preview": "[fv_ex2_homepage_preview] (requires staging+editor+FV_EX2_ALLOW_PREVIEW true)",
        "source_sha256":observations["asset_sha256"],
        "php_sha256":hashlib.sha256(php).hexdigest(),
        "no_side_effects": "No WordPress posts, pages, menus, themes, settings, subscribers, or public home routes changed.",
        "holds": ["Not production-approved; no independently green CI", "Actual WordPress staging, theme behavior and axe/screenreader not tested", "Photograph/media source-rights clearance incomplete", "Full native WordPress layout integration is NOT achieved by iframe preview"]
    }
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as out:
        out.writestr(f"{PREFIX}/fv-ex2-preview.php",php)
        for name in ASSETS:
            data=(source/name).read_bytes()
            ext=".txt" if name=="index.html" else ""
            out.writestr(f"{PREFIX}/assets/{name}{ext}",data)
        out.writestr(f"{PREFIX}/STAGING_MANIFEST.json",json.dumps(manifest,indent=2)+"\n")
        out.writestr(f"{PREFIX}/INSTALLATION_HOLD.txt", "UNPUBLISHED STAGING ONLY. No permission to install/deploy/change WordPress.\nRequires a separate private staging site and founder approval; never install on production.\nConfirm wp-config: define('WP_ENVIRONMENT_TYPE','staging') AND define('FV_EX2_ALLOW_PREVIEW',true).\nAuthorize shortcode to an editor only, on a private unpublished staging draft; do not add to live home.\nFull WordPress compatibility, photo rights, accessibility and Lighthouse audits remain open.\n")
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--out',type=Path,required=True);p.add_argument('--expected-head',required=True);args=p.parse_args()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    m=build(args.root,Path(__file__).resolve().parent,args.out,args.expected_head)
    print(json.dumps({"artifact":str(args.out),"bytes":args.out.stat().st_size,"files":len(ASSETS)+3,"asset_sha256":m['source_sha256']},indent=2))
