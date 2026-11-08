#!/usr/bin/env python3
"""Apollo R209 source-controlled staging builder; never writes WordPress."""
from __future__ import annotations
import hashlib,json,os,re,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BASE=Path(os.environ.get("FV_APOLLO_R208_DIST",str(ROOT.parent/"apollo-r208"/"dist")))
DIST=ROOT/"dist"
PARENT_MANIFEST_SHA="b9f41a76d03e524b96ea5384bafc9dc591e1a35af78287fcaf8b42e07c02a219"
REQUIRED=("templates/atlas-fragment.html","assets/atlas-scoped.css","assets/campaign-handoff.js","fv-ex2-apollo-r208.php")

def digest(x):return hashlib.sha256(x).hexdigest()

def build():
    parent_file=BASE/"manifest.json"
    if not parent_file.is_file() or digest(parent_file.read_bytes())!=PARENT_MANIFEST_SHA:
        raise ValueError("R208 staging snapshot missing/changed; no output permitted")
    parent=json.loads(parent_file.read_text(encoding="utf8"))
    if parent.get("source_chain_verified") is not False:
        raise ValueError("Unexpected upstream ancestry claim; independent review required")
    for name in REQUIRED:
        file=BASE/name
        if not file.is_file() or digest(file.read_bytes())!=parent["files"][name]:
            raise ValueError("R208 file custody mismatch: "+name)
    lesson=(ROOT/"lesson.html").read_text(encoding="utf8")
    extra_css=(ROOT/"lesson.css").read_text(encoding="utf8")
    if lesson.count('id="fv-apollo-source-test"')!=1 or lesson.count("<details")!=1:
        raise ValueError("Unexpected source lesson structure")
    html=(BASE/REQUIRED[0]).read_text(encoding="utf8")
    marker='<section class="fv-apollo-reading-lab"'
    if html.count(marker)!=1 or "fv-apollo-source-test" in html or html.count('class="cta"')!=1:
        raise ValueError("Unsafe insertion point or primary CTA mismatch")
    html=html.replace(marker,lesson+marker,1)
    css=(BASE/REQUIRED[1]).read_text(encoding="utf8")+"\n"+extra_css
    js=(BASE/REQUIRED[2]).read_bytes()
    assets={"templates/atlas-fragment.html":html.encode("utf8"),
            "assets/atlas-scoped.css":css.encode("utf8"),
            "assets/campaign-handoff.js":js}
    php=(BASE/REQUIRED[3]).read_text(encoding="utf8").replace("r208","r209").replace("R208","R209")
    for path in ("templates/atlas-fragment.html","assets/atlas-scoped.css"):
        php=php.replace(parent["files"][path],digest(assets[path]))
    php=php.replace("'dddb5a73a58d'","'"+digest(assets["assets/atlas-scoped.css"])[:12]+"'")
    assets["fv-ex2-apollo-r209.php"]=php.encode("utf8")
    if DIST.exists():shutil.rmtree(DIST)
    for path,data in assets.items():
        output=DIST/path;output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(data)
    for path in ("commercial-offer-gate.json","conversion-validation.json","source-records.json","custody-ledger.json"):
        (DIST/path).write_bytes((BASE/path).read_bytes())
    shim=(BASE/"wp-render-shim-r208.php").read_text(encoding="utf8").replace("r208","r209").replace("R208","R209")
    (DIST/"wp-render-shim-r209.php").write_text(shim,encoding="utf8")
    manifest={"release":"r209","baseline_manifest_sha256":PARENT_MANIFEST_SHA,
              "files":{k:digest(v) for k,v in sorted(assets.items())},
              "upstream_R198_reconciled":False,"installed_WordPress_accepted":False,
              "media_commercial_rights_cleared":False,"approved_purchase_offer":False,
              "source_records":["Apollo 204 Review Board","S67-21294"],"geo_pins":[],
              "editorial_cta":"free original investigation",
              "release_gate":"STAGING HOLD: canonical ancestry, WP, axe, screen readers, CI, founder approval"}
    (DIST/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf8")
    return manifest

if __name__=="__main__":print(json.dumps(build(),indent=2,sort_keys=True))
