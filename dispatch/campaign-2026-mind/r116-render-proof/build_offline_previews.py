"""Offline, non-sending previews of the original six Dispatch Markdown manuscripts.

This deliberately does NOT mimic or call Jetpack's real email renderer.
It never contacts a recipient, changes WordPress, or supplies an email send method.
"""
from __future__ import annotations
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json
import re
import sys

PILOT = Path(__file__).resolve().parents[1]
GATE = "HOLD — REVIEW ONLY — NOT A JETPACK EMAIL"
SENDER = "Final Vestige Studios"
POSTAL = "[[VALID_POSTAL_ADDRESS_REQUIRED]]"
OPTOUT = "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"
MERCHANT_TOKENS = ("[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]", "[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]")
LINK = re.compile(r"\[([^\]]+)\]\((https://[^\s)]+)\)")


def inline_html(s: str) -> str:
    """Escape raw copy first; reinsert HTTPS-only links from literal markdown."""
    out, cursor = [], 0
    for match in LINK.finditer(s):
        out.append(escape(s[cursor:match.start()]))
        label, url = match.groups()
        parts = urlparse(url)
        if parts.scheme != "https" or parts.hostname != "finalvestige.com":
            out.append(escape(label + " [external link withheld in offline preview]"))
        else:
            out.append('<a href="' + escape(url, quote=True) + '" style="color:#C7A66C;text-decoration:underline">' + escape(label) + '</a>')
        cursor = match.end()
    out.append(escape(s[cursor:]))
    result = ''.join(out)
    result = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", result)
    result = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", result)
    return result


def sections(md: str) -> list[str]:
    # Body lies between the two horizontal rules, not the review metadata/footer.
    chunks = md.split('\n---\n')
    if len(chunks) != 3:
        raise ValueError('Expected exact 3-part manuscript structure')
    return [line for line in chunks[1].splitlines() if line.strip()]


def body_html(lines: list[str]) -> str:
    blocks, bullets = [], []
    def flush():
        if bullets:
            blocks.append('<ul style="padding-left:22px;margin:18px 0">'+''.join('<li style="padding:4px 0">'+inline_html(x)+'</li>' for x in bullets)+'</ul>')
            bullets.clear()
    for line in lines:
        if line.startswith('- '):
            bullets.append(line[2:]);continue
        flush()
        text = line.strip()
        blocks.append('<p style="margin:0 0 18px;line-height:1.7">'+inline_html(text)+'</p>')
    flush()
    return '\n'.join(blocks)


def preview_html(subject: str, preheader: str, lines: list[str], issue_number: int) -> str:
    commercial = issue_number in (3, 5)
    banner = 'COMMERCIAL DRAFT — MERCHANT PERMISSION NOT VERIFIED' if commercial else 'EDITORIAL DRAFT — NOT RELEASED'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(subject)} | Offline QA</title></head>
<body style="margin:0;background:#090A0A;color:#F4EFE6;font-family:Arial,Helvetica,sans-serif;font-size:16px;overflow-wrap:anywhere;word-break:break-word">
<div role="note" style="background:#42260C;color:#FFEECC;text-align:center;padding:16px;font-weight:bold">{escape(GATE)}<br>{escape(banner)}</div>
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="width:100%;background:#090A0A"><tr><td align="center" style="padding:20px 12px"><table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="width:100%;max-width:640px;table-layout:fixed"><tr><td style="overflow-wrap:anywhere;word-break:break-word;padding:28px 18px;border:1px solid #514939;background:#121313;color:#F4EFE6">
<p style="font-size:13px;letter-spacing:.1em;color:#C7A66C">FINAL VESTIGE STUDIOS · THE DISPATCH</p><h1 style="font-size:30px;line-height:1.2">{escape(subject)}</h1><p style="color:#DDC8A2">Preheader candidate (not verified in Jetpack): {escape(preheader)}</p>
{body_html(lines)}
<div style="border-top:1px solid #726147;padding-top:18px;margin-top:24px;font-size:13px;line-height:1.7;color:#DDC8A2"><strong>Compliance holds:</strong><br>Sender: {escape(SENDER)}<br>Publisher postal address: {escape(POSTAL)}<br>Functional unsubscribe: {escape(OPTOUT)}<br>These are placeholders, NOT an actual Jetpack footer. Merchant authorization, real transport and recipient eligibility are NOT verified.</div>
</td></tr></table></td></tr></table></body></html>'''


def build(out_dir: Path) -> dict:
    manifest = json.loads((PILOT/'manifest.json').read_text(encoding='utf-8'))
    entries = manifest['issues']
    if len(entries)!=6 or [e['kind'] for e in entries].count('editorial')!=4:
        raise ValueError('The 4:2 launch allocation must be preserved')
    if manifest['status'] != 'DRAFT_UNSENT_NO_SCHEDULING':
        raise ValueError('Master campaign is not in explicitly unsent state')
    if any(e['merchant_affiliate_url'] is not None or e['publish_state']!='hold' for e in entries):
        raise ValueError('At least one merchant URL or issue state has been activated')
    out_dir.mkdir(parents=True,exist_ok=True)
    report={'source_commit':'d57ccdba3aee8f065e143e101c2945f4f3d01647','transport':'OFFLINE_SIMULATION_NOT_WORDPRESS','send_capability':False,'release_status':'HOLD','issues':[]}
    for e in entries:
        md=(PILOT/'issues'/f"{e['number']:02d}-{e['slug']}.md").read_text(encoding='utf-8')
        if ('**Subject:** '+e['subject']) not in md or ('**Preheader:** '+e['preheader']) not in md:
            raise ValueError(f"Issue {e['number']} manifest copy mismatch")
        if any(token not in md for token in (POSTAL,OPTOUT)) or 'UNSENT DRAFT' not in md:
            raise ValueError(f"Issue {e['number']} safety hold missing")
        if e['kind'] == 'commercial-review-pending':
            if not any(t in md for t in MERCHANT_TOKENS) or '**Commercial disclosure:**' not in md:
                raise ValueError('Commercial draft lacks placeholder/disclosure')
        lines=sections(md)
        html=preview_html(e['subject'],e['preheader'],lines,e['number'])
        plaintext='\n'.join([GATE, e['subject'], 'Preheader candidate: '+e['preheader'], '','\n'.join(lines), '', 'POSTAL HOLD: '+POSTAL,'UNSUBSCRIBE HOLD: '+OPTOUT,'NOT DELIVERED · NOT WORDPRESS RENDER'])
        (out_dir/f"{e['number']:02d}.html").write_text(html,encoding='utf-8')
        (out_dir/f"{e['number']:02d}.txt").write_text(plaintext,encoding='utf-8')
        report['issues'].append({'number':e['number'],'kind':e['kind'],'subject':e['subject'],'preheader_characters':len(e['preheader']),'subject_characters':len(e['subject']),'live_cta_in_source':e['editorial_cta'].startswith('https://'),'merchant_permission':'UNVERIFIED' if e['number'] in (3,5) else 'NOT_APPLICABLE','jetpack_received_preview':'NOT_OBTAINED','release':'HOLD'})
    (out_dir/'audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    links=''.join('<li><a href="%02d.html">Issue %02d — %s</a> · <a href="%02d.txt">plaintext</a></li>'%(e['number'],e['number'],escape(e['subject']),e['number']) for e in entries)
    (out_dir/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Dispatch offline reviewer — HOLD</title><body><h1>Offline campaign reviewer — never a live email</h1><p>All six drafts remain unsent and unapproved. These previews simulate the original source, NOT WordPress excerpt delivery or legal footer.</p><ul>'+links+'</ul></body></html>',encoding='utf-8')
    return report


if __name__=='__main__':
    destination=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent/'output'
    print(json.dumps(build(destination),indent=2))
