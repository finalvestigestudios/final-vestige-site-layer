"""Shared test support. Builds once per process; provides stub media so browser tests never depend on NASA being up."""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
from pathlib import Path

EX2 = Path(__file__).resolve().parent.parent
TOOLS = EX2 / "tools"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(EX2 / "atlas" / "tools"))

import fvx_lib as lib  # noqa: E402

DIST = EX2 / "dist"
PLUGIN = EX2 / "wp-plugin" / "final-vestige-experience-2"
VIEWPORTS = [(360, 800), (390, 844), (768, 1024), (1024, 800), (1440, 900), (1920, 1080)]
PAGES = {"flagship": "apollo-1/index.html", "desk": "research-desk/index.html", "atlas": "atlas/index.html", "gallery": "design-system/index.html"}

_built = False


def build() -> None:
    global _built
    if _built:
        return
    proc = subprocess.run([sys.executable, str(TOOLS / "build_all.py")], capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError("build failed:\n" + proc.stdout + proc.stderr)
    _built = True


def find_php() -> str:
    exe = os.environ.get("FVX_PHP")
    if exe:
        return exe
    from shutil import which
    found = which("php")
    if not found:
        raise RuntimeError("php not found on PATH (set FVX_PHP). PHP tests cannot be skipped.")
    return found


def _ratio_table() -> dict[str, float]:
    data = lib.load_apollo1()
    table: dict[str, float] = {}
    for rec in data["records"]:
        img = rec["image"]
        ratio = img["height"] / img["width"]
        table[img["src"]] = ratio
        for v in img["variants"]:
            table[v["url"]] = ratio
    return table


def install_media_stubs(context) -> None:
    """Answer image requests to the real media hosts with correctly-proportioned local JPEGs."""
    from PIL import Image
    ratios = _ratio_table()

    def handle(route):
        url = route.request.url
        ratio = ratios.get(url, 0.75)
        buf = io.BytesIO()
        Image.new("RGB", (320, max(1, round(320 * ratio))), (92, 86, 74)).save(buf, "JPEG", quality=60)
        route.fulfill(status=200, content_type="image/jpeg", body=buf.getvalue())

    context.route("https://images-assets.nasa.gov/**", handle)
    context.route("https://finalvestige.com/wp-content/**", handle)
