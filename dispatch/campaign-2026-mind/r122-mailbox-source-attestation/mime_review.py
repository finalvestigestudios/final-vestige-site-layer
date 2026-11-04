"""Non-sending RFC822 fixtures with SOURCE-HASH verification for Dispatch.

This module has no SMTP, network, subscriber, or WordPress write capability.
Never use its .eml products as mail campaign inputs.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
AUDIT_REL = Path('r121-canonical-acceptance/audit.json')
RENDER_REL = Path('r116-render-proof/build_offline_previews.py')
NOTICE = 'OFFLINE QA ONLY - NEVER SEND - NOT WORDPRESS RENDERED'


def blob_sha(data: bytes) -> str:
    """Git SHA-1 blob: includes the content length header, not just data SHA-1."""
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def audit_sources(campaign: Path, snapshot: str = 'stacked') -> dict:
    if snapshot not in ('master', 'stacked'):
        raise ValueError('Snapshot must be explicitly master or stacked')
    audit = json.loads((campaign / AUDIT_REL).read_text(encoding='utf-8'))
    manifest = json.loads((campaign / 'manifest.json').read_text(encoding='utf-8'))
    if len(audit['rows']) != 6 or len(manifest['issues']) != 6:
        raise ValueError('Campaign must have exactly six issues')
    if manifest['status'] != 'DRAFT_UNSENT_NO_SCHEDULING':
        raise ValueError('Sending state is not an unsent draft')
    kinds = [e['kind'] for e in manifest['issues']]
    if kinds.count('editorial') != 4 or kinds.count('commercial-review-pending') != 2:
        raise ValueError('4 editorial / 2 commercial allocation changed')
    if any(e['merchant_affiliate_url'] is not None or e['publish_state'] != 'hold' for e in manifest['issues']):
        raise ValueError('Merchant link or publication state active')
    result = []
    for row, entry in zip(audit['rows'], manifest['issues']):
        if row['issue'] != entry['number']:
            raise ValueError('Source and manifest issue order disagree')
        name = Path(row['path']).name
        source = campaign / 'issues' / name
        actual = blob_sha(source.read_bytes())
        expected = row['original_blob' if snapshot == 'master' else 'stacked_blob']
        if actual != expected:
            raise ValueError(f'Issue {entry["number"]:02d} is not the declared {snapshot} revision')
        if entry['subject'] != row['original_subject' if snapshot == 'master' else 'stacked_subject'] or entry['preheader'] != row['original_preheader' if snapshot == 'master' else 'stacked_preheader']:
            raise ValueError('Manifest does not match attested subject/preheader')
        body = source.read_text(encoding='utf-8')
        if '**Subject:** '+entry['subject'] not in body or '**Preheader:** '+entry['preheader'] not in body:
            raise ValueError('Manuscript does not match attested subject/preheader')
        result.append({'issue':entry['number'],'git_blob':actual,'subject':entry['subject'],'kind':entry['kind']})
    return {'snapshot':snapshot,'commit_claim':audit[snapshot]['sha'],'status':'HOLD_UNSENT','sources':result}


def eml_fixture(issue: int, subject: str, plain: str, html: str) -> bytes:
    if not plain.strip() or '<html' not in html.lower():
        raise ValueError('Missing valid body variants')
    msg = EmailMessage(policy=policy.SMTP)
    msg['From'] = 'Final Vestige QA Fixture <offline@finalvestige.invalid>'
    msg['Subject'] = f'[UNSENT FIXTURE] {subject}'
    msg['X-FV-Review-Only'] = 'TRUE'
    msg['X-FV-Automated-Sending-Allowed'] = 'FALSE'
    msg['Message-ID'] = f'<dispatch-{issue:02d}-unsent@finalvestige.invalid>'
    msg.set_content(NOTICE + '\n\n' + plain)
    msg.add_alternative('<div role="note"><strong>'+NOTICE+'</strong></div>\n'+html, subtype='html')
    encoded = msg.as_bytes()
    parsed = BytesParser(policy=policy.default).parsebytes(encoded)
    if not parsed.is_multipart() or len(list(parsed.iter_attachments())):
        raise ValueError('Unexpected MIME structure')
    if any(k in parsed for k in ('To','Cc','Bcc','List-Unsubscribe','Return-Path')):
        raise ValueError('Not safe as an inert mailbox specimen')
    variants = list(parsed.iter_parts())
    if [v.get_content_type() for v in variants] != ['text/plain','text/html']:
        raise ValueError('Missing plaintext/HTML alternative')
    if any(NOTICE not in v.get_content() for v in variants):
        raise ValueError('Unsent notice must appear in both bodies')
    return encoded


def build(campaign: Path, destination: Path, snapshot: str = 'stacked') -> dict:
    proof = audit_sources(campaign, snapshot)
    renderer = campaign / RENDER_REL
    spec = importlib.util.spec_from_file_location('offline_dispatch_renderer', renderer)
    if not spec or not spec.loader:
        raise ValueError('Offline renderer unavailable')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    render_path = destination / 'rendered_html_plain'
    render_report = mod.build(render_path)
    # R116 hard-codes its source_commit to master even on stacked branches.
    # This is NOT reliable provenance. The independently checked blob SHAs above are.
    proof['legacy_renderer_claim'] = render_report.get('source_commit')
    proof['legacy_renderer_claim_is_proof'] = False
    proof['jetpack_received_email'] = False
    proof['welcome_received'] = False
    proof['actual_unsubscribe_and_postal_footer'] = False
    proof['affiliate_email_permission_verified'] = False
    proof['send_authorized'] = False
    proof['fixtures'] = []
    destination.mkdir(parents=True, exist_ok=True)
    for row in proof['sources']:
        number = row['issue']
        plain = (render_path / f'{number:02d}.txt').read_text(encoding='utf-8')
        html = (render_path / f'{number:02d}.html').read_text(encoding='utf-8')
        mime = eml_fixture(number, row['subject'], plain, html)
        name = f'{number:02d}-INERT-UNSENT.eml'
        (destination / name).write_bytes(mime)
        proof['fixtures'].append({'issue':number,'filename':name,'sha256':hashlib.sha256(mime).hexdigest(),
                                  'text_plain':True,'text_html':True,'actual_jetpack_email':False})
    (destination / 'proof.json').write_text(json.dumps(proof,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return proof


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--campaign',type=Path,default=CAMPAIGN)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--snapshot',choices=['master','stacked'],required=True)
    args=p.parse_args()
    print(json.dumps(build(args.campaign,args.out,args.snapshot),indent=2))
