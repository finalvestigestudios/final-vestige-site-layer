"""R474 isolated adversarial custody tests. All assertions are structural, NOT safety review."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools/r474_child_card_scope_gate.py"
spec = importlib.util.spec_from_file_location("r474_child_card", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
MANIFEST = json.loads((Path(__file__).resolve().parents[1] /
                      "reviews/r474_child_card_scope_manifest.json").read_text())


def setup():
    a = {"n": 15, "slug": gate.ARTICLE, "status":{"publish":"draft"},
         "safety_review":{"state":"pending","reviewer":None,"date":None},
         "source_use":{k:"older documented scope" for k in gate.REQUIRED_OLD_IDS}}
    t = copy.deepcopy(a);t["n"]=104;t["slug"]=gate.TOOL
    article = ("<strong>Keep it on paper, too.</strong> This is our caution, not an agency's. "
               "{{link:family-reunification-card|fold-over wallet card}} "
               "{{cite:shelter-cdc-reunification}} {{cite:shelter-ready-plan-form}}")
    tool = ("A printed card can be lost. Do not put a child's full name, "
            "a medical diagnosis or a password on it. "
            "First names or nicknames and phone numbers are usually enough. "
            "minimal version. School, childcare and care (left off the minimal version). "
            "{{cite:shelter-cdc-reunification}}")
    return [article, a, tool, t, copy.deepcopy(MANIFEST)]


