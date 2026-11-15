"""Fail-closed, non-sending RFC 5322 review artefacts for the PR #175 originals.

Never imports SMTP/requests. Outputs .eml, .html, .txt for offline inspection only.
All rendered content comes from immutable input Markdown; no newsletter sends or writes.
Run: python dispatch/r367/build_review_mime.py <path-to-campaign-root> <output-dir>
"""
from __future__ import annotations

import email.policy
from email.message import EmailMessage
from html import escape
from pathlib import Path
import json
import re
import sys

try:
    import mistune
except ImportError:
    mistune = None

EXPECTED = (
    (1, "01-the-mind-is-not-a-camera.md", "editorial"),
    (2, "02-before-hypnosis-had-a-name.md", "editorial"),
    (3, "03-the-twelve-minute-question.md", "commercial-review-pending"),
    (4, "04-the-hatch-and-the-spark.md", "editorial"),
    (5, "05-before-you-press-play.md", "commercial-review-pending"),
    (6, "06-the-evidence-log.md", "editorial"),
)
DISABLED = {
    3: "[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]",
    5: "[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]",
}
LEGAL = ("[[VALID_POSTAL_ADDRESS_REQUIRED]]", "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]")
REVIEW_BANNER = "REVIEW ONLY — NOT A JETPACK EMAIL — DO NOT SEND"


def parse_source(source: str, num: int, kind: str) -> dict:
    assert f"ISSUE {num:02d}" in source[:180], "Unexpected source edition"
    subject = re.search(r"\*\*Subject:\*\* ([^\n]+)", source)
    preheader = re.search(r"\*\*Preheader:\*\* ([^\n]+)", source)
    content_type = re.search(r"\*\*Content type:\*\* ([^\n]+)", source)
    assert subject and preheader and content_type, "Missing original header"
    assert content_type.group(1).strip() == kind, "Campaign class drift"
    assert "STATUS: UNSENT DRAFT" in source and "---\n" in source, "Hold/source marker absent"
    assert all(x in source for x in LEGAL), "Missing legal blocking tokens"
    if num in DISABLED:
        assert DISABLED[num] in source, "Merchant CTA unexpectedly activated"
        assert "**Commercial disclosure:**" in source, "Merchant disclosure absent"
    if "[http" in source:
        raise AssertionError("Raw link substitution detected")
    subject = subject.group(1).strip()
    preheader = preheader.group(1).strip()
    assert 12 <= len(subject) <= 85 and len(preheader) <= 170, "Subject/preheader bounds"
    assert not any(c in subject + preheader for c in "\r\n"), "Header injection"
    body = source.split("\n---\n", 1)[1].strip()
    return dict(number=num, kind=kind, subject=subject, preheader=preheader, body=body)


def build_review(issue: dict):
    """Use an explicit no-recipient multipart/alternative artefact, never a deliverable message."""
    num = issue["number"]
    body = issue["body"]
    escaped = escape(body)
    # Deliberately preserve all original body text; no template substitution or sendable footer.
    if mistune is not None:
        rendered = mistune.create_markdown(escape=True)(body)
        # Mistune renders raw Markdown links with ordinary external links; never auto-links tokens.
    else:
        rendered = "<pre style='white-space:pre-wrap'>" + escaped + "</pre>"
    assert "<script" not in rendered.lower() and "<form" not in rendered.lower()
    for token in LEGAL + tuple(DISABLED.values()):
        if token in body:
            assert escape(token) in rendered or token in rendered, "Unsafe token rewrite"
    html = ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>REVIEW ONLY: " + escape(issue["subject"]) + "</title></head>"
            "<body style='margin:0;background:#f7f3e9;color:#202020;font:16px/1.6 Arial,sans-serif'>"
            "<table role='presentation' width='100%' cellpadding='0' cellspacing='0'><tr><td align='center' style='padding:18px 10px'>"
            "<table role='presentation' width='600' cellpadding='0' cellspacing='0' style='max-width:600px;width:100%;background:#fff'>"
            "<tr><td style='padding:24px'>"
            "<p style='font-weight:700;color:#831d1d'>" + REVIEW_BANNER + "</p>"
            "<h1 style='font-size:26px;line-height:1.25'>" + escape(issue["subject"]) + "</h1>"
            "<p style='color:#504b45'>" + escape(issue["preheader"]) + "</p>"
            "<div style='overflow-wrap:anywhere'>" + rendered + "</div>"
            "<p style='border-top:2px solid #831d1d;padding-top:12px;color:#831d1d;font-weight:bold'>"
            "NO SEND: address, unsubscribe, consent, actual Jetpack render, founder approval and applicable merchant rights UNVERIFIED.</p>"
            "</td></tr></table></td></tr></table></body></html>"
    )
    plain = f"{REVIEW_BANNER}\nSubject: {issue['subject']}\nPreheader: {issue['preheader']}\n\n" + body + (
        "\n\nNO SEND: legal footer, opt-out, verified audience, native render, founder approval and commercial rights not cleared.\n"
    )
    msg = EmailMessage(policy=email.policy.SMTP)
    msg["Subject"] = "[REVIEW ONLY / UNSENDABLE] " + issue["subject"]
    msg["X-FV-Review-Only"] = "yes"
    msg["X-FV-Release-Gate"] = "HOLD_UNSENT"
    msg["X-FV-Merchant-Gate"] = "HOLD_MERCHANT" if num in DISABLED else "N_A"
    # No To, From, CC, BCC or Date; these cannot be mistaken for a delivered message.
    msg.set_content(plain, charset="utf-8")
    msg.add_alternative(html, subtype="html", charset="utf-8")
    assert msg.is_multipart() and not any(k in msg for k in ("To", "From", "Cc", "Bcc"))
    return html, plain, msg.as_bytes()


def generate(campaign_root: Path, output_dir: Path) -> list[dict]:
    manifest = json.loads((campaign_root / "manifest.json").read_text(encoding="utf-8"))
    assert len(manifest.get("issues", [])) == 6, "Non-canonical issue count"
    assert sum(1 for _, _, kind in EXPECTED if kind == "commercial-review-pending") == 2
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = []
    for n, fname, kind in EXPECTED:
        source = (campaign_root / "issues" / fname).read_text(encoding="utf-8")
        issue = parse_source(source, n, kind)
        html, plain, mime = build_review(issue)
        stem = f"issue-{n:02d}"
        (output_dir / f"{stem}.html").write_text(html, encoding="utf-8")
        (output_dir / f"{stem}.txt").write_text(plain, encoding="utf-8")
        (output_dir / f"{stem}.eml").write_bytes(mime)
        summary.append({"issue": n, "subject": issue["subject"], "kind": kind,
                        "mime_bytes":len(mime), "release":"HOLD_UNSENT",
                        "merchant":"HOLD_MERCHANT" if n in DISABLED else "N/A"})
    (output_dir / "manifest-review.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: build_review_mime.py <campaign-root> <offline-output>")
    print(json.dumps(generate(Path(sys.argv[1]), Path(sys.argv[2])), indent=2))
