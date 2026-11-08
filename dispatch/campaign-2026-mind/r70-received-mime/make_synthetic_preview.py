#!/usr/bin/env python3
"""Produce real previewable HTML/plaintext and redacted JSON from SYNTHETIC MIME only.

No network, no actual recipient, no private input, no .eml output, no sending.
The result always says HOLD_UNSENT and is not a native Jetpack inbox preview.
"""
from email.message import EmailMessage
import importlib.util
import json
from pathlib import Path
import argparse

HERE = Path(__file__).resolve().parent

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

inspector = load("fv_r70_local_inspector", "inspect_received_eml.py")
renderer = load("fv_r70_local_renderer", "render_report.py")

FAKE_POSTAL = "P.O. Box 123, Example City, CA 90000"
FAKE_SUBJECT = "A source is not a verdict — SYNTHETIC REVIEW"
ISSUE = "03"

def generate(directory: Path):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    m = EmailMessage()
    m["From"] = "Synthetic Final Vestige <donotreply@wordpress.com>"
    m["To"] = "nobody@example.invalid"
    m["Subject"] = FAKE_SUBJECT
    m["List-Unsubscribe"] = "<https://optout.example.invalid/u/FAKE_NOOP>"
    m["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    disclosure = "Final Vestige may earn a commission if you buy through a linked, separately verified buyer guide."
    intro = ("This fictional format test is not a real commercial offer, proof of product results,"
             " confirmation of permission, or a preview of an actual WordPress message.")
    m.set_content(disclosure + "\n\n" + intro + "\n\nUnsubscribe: https://optout.example.invalid/u/FAKE_NOOP\n" + FAKE_POSTAL)
    html = (
        '<!doctype html><html lang="en"><body><main><h1>' + FAKE_SUBJECT + '</h1><p>' +
        disclosure + '</p><p>' + intro + '</p><p><a href="https://optout.example.invalid/u/FAKE_NOOP">'
        'Unsubscribe</a></p><p>' + FAKE_POSTAL + '</p></main></body></html>'
    )
    m.add_alternative(html, subtype="html")
    report = inspector.audit_bytes(m.as_bytes(), edition=ISSUE,
                                   expected_subject=FAKE_SUBJECT,
                                   publisher_postal_address=FAKE_POSTAL)
    # Only redacted schema can be persisted; raw MIME is in-memory and discarded.
    assert report["release_status"] == "HOLD_UNSENT" and report["send_allowed"] is False
    outputs = {
        "json": directory / "synthetic-redacted-report.json",
        "html": directory / "synthetic-review.html",
        "text": directory / "synthetic-review.txt",
    }
    outputs["json"].write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs["html"].write_text(renderer.html_report(report), encoding="utf-8")
    outputs["text"].write_text(renderer.text_report(report), encoding="utf-8")
    return outputs

def main(argv=None):
    p = argparse.ArgumentParser(description="Make local SYNTHETIC only hold previews; never a real email")
    p.add_argument("--out-dir", required=True, type=Path)
    a = p.parse_args(argv)
    try:
        files = generate(a.out_dir)
    except (OSError, ValueError):
        print("SYNTHETIC_PREVIEW_FAILED")
        return 2
    # Deliberately no personal paths emitted.
    print("CREATED_SYNTHETIC_HOLD_ONLY HTML/TEXT/JSON: " +
          ", ".join(v.name for v in files.values()))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
