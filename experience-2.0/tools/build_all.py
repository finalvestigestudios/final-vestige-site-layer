#!/usr/bin/env python3
"""Build every Experience 2.0 artifact.

Outputs
  experience-2.0/dist/                       preview site (gitignored)
  experience-2.0/wp-plugin/.../assets|templates   committed plugin payload; `--check` fails if it is stale
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import fvx_lib as lib  # noqa: E402
from render_apollo_page import manifest as page_manifest, render_blocks  # noqa: E402
from render_atlas import render_atlas  # noqa: E402
from render_desk import render_desk  # noqa: E402
from render_flagship import render_flagship  # noqa: E402
from render_gallery import render_gallery  # noqa: E402

DIST = lib.EX2 / "dist"
PLUGIN = lib.EX2 / "wp-plugin" / "final-vestige-experience-2"
PAGE_BLOCKS = lib.EX2 / "page-blocks"  # plugin-free: one core/html block per page, committed so its hash is reviewable


def outputs() -> dict[Path, str]:
    data = lib.load_apollo1()
    css, js = lib.bundle_css(), lib.bundle_js()
    desk_fragment = render_desk(data, lib.INSTANCE_PLACEHOLDER, fragment=True)
    atlas_fragment, _ = render_atlas(fragment=True)
    shell = lambda title, desc, body, depth: lib.page_shell(  # noqa: E731
        title=title, description=desc, body=body, css_href="../" * depth + "assets/fv-ex2.css", js_src="../" * depth + "assets/fv-ex2.js")
    atlas_body, atlas_report = render_atlas()
    files: dict[Path, str] = {
        DIST / "assets" / "fv-ex2.css": css,
        DIST / "assets" / "fv-ex2.js": js,
        DIST / "apollo-1" / "index.html": shell(
            "The Hatch Opened Inward - The Evidence Unfolds", "Six sourced records from the Apollo 204 Review Board and NASA's archive.",
            render_flagship(data, desk_url="../research-desk/index.html", atlas_url="../atlas/index.html"), 1),
        DIST / "research-desk" / "index.html": shell(
            "Research Desk - Apollo 1", "Source records, evidence limitations and claim crosswalk for the Apollo 1 investigation.",
            render_desk(data, "apollo1"), 1),
        DIST / "atlas" / "index.html": shell(
            "Evidence Atlas - catalogue", "Published Final Vestige investigations. Map pins appear only after verified geography.", atlas_body, 1),
        DIST / "design-system" / "index.html": shell(
            "Experience 2.0 design system gallery", "Component gallery for the Final Vestige Experience 2.0 design system.", render_gallery(data), 1),
        PLUGIN / "assets" / "fv-ex2.css": css,
        PLUGIN / "assets" / "fv-ex2.js": js,
        PLUGIN / "templates" / "research-desk.html": desk_fragment + "\n",
        PLUGIN / "templates" / "atlas.html": atlas_fragment + "\n",
    }
    manifest = lib.bundle_manifest(css, js, {
        "templates": {
            "research-desk": {"sha256": __import__("hashlib").sha256(files[PLUGIN / "templates" / "research-desk.html"].encode()).hexdigest()},
            "atlas": {"sha256": __import__("hashlib").sha256(files[PLUGIN / "templates" / "atlas.html"].encode()).hexdigest()},
        },
        "data_sources": {"apollo1": __import__("hashlib").sha256((lib.DATA / "apollo1.json").read_bytes()).hexdigest()},
    })
    files[PLUGIN / "assets" / "manifest.json"] = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    blocks = render_blocks()
    for name, markup in blocks:
        files[PAGE_BLOCKS / "apollo1-investigation" / f"{name}.block.html"] = markup
    files[PAGE_BLOCKS / "manifest.json"] = json.dumps({"apollo1-investigation": page_manifest(blocks)}, indent=2, sort_keys=True) + chr(10)
    files[DIST / "atlas-report.json"] = json.dumps(atlas_report, indent=2, sort_keys=True) + "\n"
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if committed plugin payload differs from a fresh build")
    args = ap.parse_args()
    files = outputs()
    if args.check:
        stale = [str(p.relative_to(lib.EX2)) for p, text in files.items()
                 if (PLUGIN in p.parents or PAGE_BLOCKS in p.parents) and (not p.exists() or p.read_text(encoding="utf-8") != text)]
        if stale:
            print("STALE plugin payload (run tools/build_all.py):", *stale, sep="\n  ")
            return 1
        print("OK: committed plugin payload matches a fresh build")
        return 0
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    print(f"built {len(files)} files; css={len(files[DIST / 'assets' / 'fv-ex2.css'].encode())}B js={len(files[DIST / 'assets' / 'fv-ex2.js'].encode())}B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
