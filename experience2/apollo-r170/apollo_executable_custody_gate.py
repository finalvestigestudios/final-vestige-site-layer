"""R170: source-exact executable/style custody for Apollo offline Gutenberg previews.

R169 locks citations and narrative, but is not an executable-content attestator.
This gate must detect mutations to JS, CSS and DOM executable attributes before
any staging acceptance. It does not execute remote code, write WordPress or deploy.
"""
from __future__ import annotations

import hashlib
import re
from html.parser import HTMLParser
from pathlib import Path
from apollo_source_conversion_gate import verify as verify_editorial, offline_preflight
from stage_patch import START as OLD_JS_START, END as OLD_JS_END
from wp_block_pack import payload as r167_payload
from wp_source_custody_gate import CONTRACT_CSS, R168_TAG

HERE = Path(__file__).resolve().parent
SCRIPT = re.compile(r'<script(?P<attrs>[^>]*)>(?P<body>.*?)</script\s*>', re.I | re.S)
STYLE = re.compile(r'<style(?P<attrs>[^>]*)>(?P<body>.*?)</style\s*>', re.I | re.S)


def sha(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def slices(regex: re.Pattern, value: str) -> list[tuple[str, str]]:
    return [(m.group('attrs'), m.group('body')) for m in regex.finditer(value)]


class SurfaceParser(HTMLParser):
    """Snapshot exploitable HTML surfaces without conflating script text with markup."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.triggers: list[tuple[str, str, str]] = []
        self.structural: list[tuple[str, tuple[tuple[str, str], ...]]] = []

    def handle_starttag(self, tag, attrs):
        pairs = [(str(k).lower(), '' if v is None else str(v)) for k, v in attrs]
        for key, value in pairs:
            if key.startswith('on') and len(key) > 2:
                self.triggers.append((tag, key, value))
        if tag in {'script', 'iframe', 'form', 'object', 'embed', 'base', 'meta', 'link'}:
            self.structural.append((tag, tuple(sorted(pairs))))


def surfaces(value: str) -> SurfaceParser:
    p = SurfaceParser()
    p.feed(value)
    p.close()
    return p


def expected_legacy_script(before: str) -> str:
    start = before.find(OLD_JS_START)
    end = before.find(OLD_JS_END, start + len(OLD_JS_START))
    if start < 0 or end < 0 or before.count(OLD_JS_START) != 1 or before.count(OLD_JS_END) != 1:
        raise ValueError('HOLD: historic legacy script cannot be independently reconstructed')
    return before[:start] + before[end:]


def validate_executable(before: str, after: str) -> dict:
    """Constrain every executable/style byte to the one authorized R167+R168 build.

    This is an independent *post-build verifier*: any arbitrary JS/CSS modification
    that R169's narrative/link custody missed must raise an explicit HOLD.
    """
    verify_editorial(before, after)
    old_scripts, new_scripts = slices(SCRIPT, before), slices(SCRIPT, after)
    old_styles, new_styles = slices(STYLE, before), slices(STYLE, after)
    if len(old_scripts) != 1 or len(new_scripts) != 2:
        raise ValueError('HOLD: unexpected executable script count')
    if len(new_styles) != len(old_styles) + 2:
        raise ValueError('HOLD: unexpected style block count')
    if any(attrs.strip() for attrs, _ in old_scripts + new_scripts):
        raise ValueError('HOLD: external or attributed script prohibited by pinned build')
    if any(attrs.strip() for attrs, _ in old_styles + new_styles):
        raise ValueError('HOLD: attributed style prohibited by pinned build')
    legacy = expected_legacy_script(old_scripts[0][1])
    if new_scripts[0][1] != legacy:
        raise ValueError('HOLD: unauthorized legacy JavaScript drift')
    staged_payload_scripts = slices(SCRIPT, r167_payload())
    if len(staged_payload_scripts) != 1 or new_scripts[1] != staged_payload_scripts[0]:
        raise ValueError('HOLD: injected R167 script bytes are not attested')
    if new_styles[:len(old_styles)] != old_styles:
        raise ValueError('HOLD: original style source drift')
    if new_styles[len(old_styles)] != slices(STYLE, r167_payload())[0]:
        raise ValueError('HOLD: injected R167 CSS not attested')
    if new_styles[-1] != ('', '\n' + CONTRACT_CSS.read_text(encoding='utf-8') + '\n'):
        raise ValueError('HOLD: injected R168 contrast CSS not attested')
    a, b = surfaces(before), surfaces(after)
    if a.triggers != b.triggers:
        raise ValueError('HOLD: inline event handler changed or inserted')
    if a.structural != b.structural[:len(a.structural)]:
        # A script is expected to be inserted at the end, so filter scripts and
        # compare non-script high-risk markup in original document order instead.
        def non_script(items):
            return [x for x in items if x[0] != 'script']
        if non_script(a.structural) != non_script(b.structural):
            raise ValueError('HOLD: form/iframe/embed/base/meta/link surface drift')
    else:
        # The prefix case can still conceal a non-script mutation at the end.
        if [x for x in a.structural if x[0] != 'script'] != [x for x in b.structural if x[0] != 'script']:
            raise ValueError('HOLD: unsupported active markup change')
    # No extra scripts or styles hidden in mixed-case tags or script attr variants.
    for tag, count in (('script',2), ('style',len(new_styles))):
        if len(re.findall(fr'<{tag}\b', after, re.I)) != count:
            raise ValueError('HOLD: unrecognized mixed-case executable/style tag')
    return {
        'gate': 'R170_EXECUTABLE_STYLE_CUSTODY_PASS_OFFLINE_ONLY',
        'original_legacy_script_sha256': sha(old_scripts[0][1]),
        'authorized_legacy_script_sha256': sha(new_scripts[0][1]),
        'r167_script_sha256': sha(new_scripts[1][1]),
        'r167_style_sha256': sha(new_styles[-2][1]),
        'r168_style_sha256': sha(new_styles[-1][1]),
        'original_style_count': len(old_styles),
        'new_script_count': len(new_scripts),
        'new_style_count': len(new_styles),
        'new_dom_event_handlers': 0,
        'new_active_embed_or_form_surfaces': 0,
        'approved_for_publish': False,
        'wordpress_writes': 0,
        'axe': 'NOT_EXECUTED',
        'real_wordpress_browser': 'NOT_EXECUTED',
        'actual_cwv': 'NOT_MEASURED',
        'net_revenue': 'UNKNOWN_NO_RECONCILED_PAID_ORDERS',
    }


def preflight(before: str, witness: dict | None = None):
    from wp_source_custody_gate import WITNESS
    staged, receipt = offline_preflight(before, WITNESS if witness is None else witness)
    receipt['r170'] = validate_executable(before, staged)
    return staged, receipt


if __name__ == '__main__':
    import argparse, json
    cli = argparse.ArgumentParser(description='Offline attested Apollo editor preview; never deploys')
    cli.add_argument('pinned_editor_input', type=Path)
    cli.add_argument('preview_output', type=Path)
    args = cli.parse_args()
    preview, report = preflight(args.pinned_editor_input.read_text(encoding='utf-8'))
    args.preview_output.write_text(preview, encoding='utf-8')
    args.preview_output.with_suffix('.audit.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(json.dumps(report['r170'], sort_keys=True))
