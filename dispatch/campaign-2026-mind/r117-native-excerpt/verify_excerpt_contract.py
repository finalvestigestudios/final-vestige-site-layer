"""Non-sending, no-network release guard and offline reviewer for proposed Jetpack Post Excerpts.

NOT a Jetpack email renderer. It has no SMTP, WordPress or subscriber functionality.
"""
import argparse
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
COMMERCIAL = (3, 5)
HOLD = 'HOLD_UNSENT'


def audit(doc):
    problems = []
    if doc.get('release') != HOLD or doc.get('transport') != 'JETPACK_NEW_POST_EXCERPT_DRAFT_ONLY':
        problems.append('Release/transport status must remain a draft HOLD')
    rules = doc.get('rules', {})
    if rules.get('do_not_publish') is not True:
        problems.append('do_not_publish must be true')
    for key in ('email_new_posts_by_default', 'actual_footer_verified',
                'actual_received_email_verified', 'merchant_email_permission_verified',
                'legal_postal_address_verified', 'unsubscribe_working_verified'):
        if rules.get(key) is not False:
            problems.append(key + ' must remain unverified/false')
    if rules.get('email_content_format') != 'excerpt':
        problems.append('WordPress excerpt setting mismatch')
    issues = doc.get('issues', [])
    if len(issues) != 6 or [x.get('number') for x in issues] != list(range(1, 7)):
        problems.append('Expected exactly issues 1–6 in fixed order')
    if sum(x.get('kind') == 'editorial' for x in issues) != 4 or sum(x.get('kind') == 'commercial-review-pending' for x in issues) != 2:
        problems.append('The founder-approved 4:2 draft allocation must be preserved')
    for issue in issues:
        n = issue.get('number')
        body = issue.get('excerpt', '')
        if not isinstance(body, str) or not 95 <= len(body) <= 320:
            problems.append(f'{n}: explicit excerpt must be 95–320 characters')
            continue
        if '\n' in body or '[[' in body or '<' in body or ']]' in body:
            problems.append(f'{n}: excerpt contains unsafe formatting or placeholder')
        if re.search(r'https?://|utm_|affiliate_id|[\w.+-]+@[\w-]+\.', body, re.I):
            problems.append(f'{n}: URL, tracking or personal identifier forbidden in excerpt')
        if any(x in body.lower() for x in ('guaranteed', 'cure', 'clinically proven', 'get rich', '100%')):
            problems.append(f'{n}: unsubstantiated benefit language')
        if not str(issue.get('eligibility', '')).startswith('HOLD_'):
            problems.append(f'{n}: cannot mark issue eligible to send')
        if n in COMMERCIAL:
            if issue.get('kind') != 'commercial-review-pending':
                problems.append(f'{n}: offer edition must remain commercial')
            if 'Final Vestige may earn a commission' not in body:
                problems.append(f'{n}: near-offer disclosure absent from visible excerpt')
            if not str(issue.get('in_post_destination', '')).startswith('[[APPROVED_'):
                problems.append(f'{n}: first-party offer guide is not approved/live')
        elif issue.get('kind') != 'editorial':
            problems.append(f'{n}: cannot be marked promotional')
        if n == 4 and issue.get('editorial_title_qa') != 'BLOCK_UNSOURCED_FOURTEEN_SECONDS':
            problems.append('Apollo 1 timing subject not cleared')
        if n == 6 and not str(issue.get('in_post_destination','')).startswith('[[DIRECT_FIELD_BOOK'):
            problems.append('Issue 06 direct PDF requires independent retrieval QA')
    if len(doc.get('official_sources', [])) < 5:
        problems.append('Official-source ledger incomplete')
    return problems


def render(doc):
    rows = []
    for issue in doc['issues']:
        n = issue['number']
        rows.append('<article class="card"><p class="eyebrow">ISSUE %02d · %s · UNSENT</p>' %
                    (n, html.escape(issue['kind'])))
        rows.append('<h2>%s</h2>' % html.escape(issue.get('suggested_replacement_subject', issue['canonical_subject'])))
        rows.append('<p>%s</p>' % html.escape(issue['excerpt']))
        rows.append('<p class="cta" role="note">NATIVE-POST CONTINUATION ONLY — disabled; no link supplied.</p>')
        rows.append('<p class="hold">%s</p></article>' % html.escape(issue['eligibility']))
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" '
            'content="width=device-width,initial-scale=1"><title>Dispatch proposed Jetpack excerpts — HOLD</title>'
            '<style>*{box-sizing:border-box}body{background:#0b0d0e;color:#f6f0e7;margin:0;'
            'font:17px/1.7 system-ui,sans-serif;overflow-wrap:anywhere}main{max-width:1040px;'
            'padding:24px 18px;margin:auto}h1,h2{font-family:Georgia,serif;line-height:1.25}h2{font-size:1.55rem}'
            '.intro{border-left:4px solid #c7a66c;padding-left:16px}.grid{display:grid;'
            'grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:20px;margin-top:28px}'
            '.card{background:#171b1c;padding:20px;border:1px solid #77654d;min-width:0}'
            '.eyebrow{font-size:.75rem;letter-spacing:.08em;color:#f0d09b}.cta{border:1px dashed #c7a66c;'
            'padding:10px;color:#eddeb9}.hold{font-size:.75rem;color:#ffcb9a}a:focus-visible{outline:3px solid white}'
            '</style></head><body><main><h1>Dispatch · excerpt-readiness preview</h1>'
            '<p class="intro">OFFLINE STATIC QA ONLY. These are proposed WordPress Post Excerpt fields, '
            'not the actual rendered email. No affiliate links, subscriber data, checkout actions, '
            'or working CTA. Every issue remains blocked.</p><div class="grid">'+''.join(rows)+'</div>'
            '<p>Native emails can be triggered by new posts only after the founder separately approves publication '
            'and the individual email-send toggle. Current default is OFF; leave it OFF. Confirm '
            'publisher postal address, actual unsubscribe and actual Jetpack preview before any send.</p>'
            '</main></body></html>')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', default=str(ROOT / 'excerpt_contract.json'))
    p.add_argument('--preview', help='Optional offline HTML output')
    a = p.parse_args()
    doc = json.loads(pathlib.Path(a.input).read_text(encoding='utf-8'))
    problems = audit(doc)
    if problems:
        for problem in problems:
            print('FAIL: '+problem)
        raise SystemExit(1)
    if a.preview:
        pathlib.Path(a.preview).write_text(render(doc), encoding='utf-8')
    print('PASS: 6 explicit excerpts, 4 editorial/2 commercial, all HOLD, no live CTA or send capability')


if __name__ == '__main__':
    main()
