#!/usr/bin/env python3
"""R326: read-only Preparedness browser FormData/GET preflight (HARD HOLD).

Compares original, Git-pinned tool body form surfaces with browser-derived form
serialization *shapes*. Never submits, navigates, transmits or reads household
values into reports. No privacy, emergency-safety, QD, or publication approval.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re

from preparedness.tools import r319_three_way_custody_hold as custody
from preparedness.tools import r324_tool_privacy_egress_hold as r324
from preparedness.tools import r325_browser_form_exposure_hold as r325

SCHEMA = 'fv-preparedness-r326-form-serialization-draft-hard-hold-v1'
RELEASE = dict(publication_authorized=False, independent_qd_pass=False,
               emergency_safety_approved=False, child_privacy_approved=False,
               browser_egress_verified=False, paid_conversion_verified=False)


class Surface(HTMLParser):
    """Only inspect markup names; never collect typed or default field values."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.forms = []
        self.fields = []
        self.buttons = []
        self.active = None
        self.privacy_assertions = 0
        self._visible_text = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        a = {str(k).lower(): v for k, v in attrs}
        if tag == 'form':
            if self.active is not None:  # Invalid nested forms: browser repairs tree.
                self.forms[self.active]['nested_form_source'] = True
            self.forms.append(dict(id=a.get('id'), method=(a.get('method') or 'GET').upper(),
                                   action_present=bool(a.get('action')),
                                   handler_present=bool(a.get('onsubmit')),
                                   nested_form_source=False))
            self.active = len(self.forms) - 1
        elif tag in ('input', 'select', 'textarea'):
            typ = 'select' if tag == 'select' else 'textarea' if tag == 'textarea' else (a.get('type') or 'text').lower()
            self.fields.append(dict(form=a.get('form'), inside=self.active, name=a.get('name'),
                                    type=typ, disabled='disabled' in a,
                                    checkbox=(typ in ('checkbox', 'radio')),
                                    checked='checked' in a))
        elif tag == 'button':
            self.buttons.append(dict(form=a.get('form'), inside=self.active,
                                     type=(a.get('type') or 'submit').lower(),
                                     overridden=bool(a.get('formaction') or a.get('formmethod'))))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag.lower() == 'form':
            self.active = None

    def handle_data(self, data):
        # Avoid emitting source content or values, only a count of privacy claims.
        self._visible_text.append(data)

    def finish(self):
        text = ' '.join(self._visible_text).lower()
        self.privacy_assertions = len(re.findall(
            r'not sent anywhere|nothing is sent|sends nothing|not saved in (?:the )?address bar|'
            r'not stored|keeps nothing|nothing you (?:choose|type) is (?:stored|sent)', text))
        self._visible_text.clear()


def inspect(raw: bytes) -> dict:
    if not isinstance(raw, bytes):
        raise TypeError('SOURCE_BYTES_REQUIRED')
    doc = raw.decode('utf-8', 'strict')
    if '\x00' in doc:
        raise ValueError('INVALID_SOURCE_NUL')
    p = Surface()
    p.feed(doc)
    p.close()
    p.finish()
    rows = []
    for index, form in enumerate(p.forms):
        owned = [f for f in p.fields if f['inside'] == index or
                 (form['id'] and f['form'] == form['id'])]
        active = [f for f in owned if f['name'] and not f['disabled']]
        potentially_successful = [f for f in active if f['type'] not in ('button', 'submit', 'reset', 'image', 'file')
                                  and (not f['checkbox'] or f['checked'])]
        buttons = [b for b in p.buttons if b['inside'] == index or
                   (form['id'] and b['form'] == form['id'])]
        flags = set()
        if form['method'] == 'GET':
            flags.add('GET_DEFAULT_OR_EXPLICIT_NAVIGATION_HOLD')
            if potentially_successful:
                flags.add('POTENTIAL_FORMDATA_URL_QUERY_HOLD')
        elif form['method'] in ('POST', 'DIALOG'):
            flags.add('NON_GET_FORM_BEHAVIOR_REVIEW')
        else:
            flags.add('INVALID_FORM_METHOD_BROWSER_NORMALIZATION_REVIEW')
        if form['handler_present']:
            flags.add('INLINE_SUBMIT_HANDLER_NOT_NOJS_GUARD')
        if form['action_present']:
            flags.add('EXPLICIT_ACTION_DESTINATION_REVIEW')
        if form['nested_form_source']:
            flags.add('BROWSER_PARSER_REPAIR_REVIEW')
        if any(b['overridden'] for b in buttons):
            flags.add('BUTTON_OVERRIDE_REVIEW')
        if not buttons and active:
            flags.add('ENTER_IMPLICIT_SUBMISSION_REVIEW')
        rows.append({'index': index, 'method_source': form['method'],
                     'named_active_controls': len(active),
                     'potential_successful_controls': len(potentially_successful),
                     'name_only_witness': sorted(set(f['name'] for f in active)),
                     'flags': sorted(flags)})
    return {'form_count': len(p.forms), 'field_count': len(p.fields),
            'privacy_claim_occurrences': p.privacy_assertions,
            'forms': rows, 'privacy_approved': False}


def chromium_preflight(raw: bytes, *, executable='/usr/bin/chromium', timeout_ms=4000) -> dict:
    """Browser-computed sanitized FormData shapes under JS-off/CSP; NO submission.

    Scripts in the source cannot run. DOM is populated with synthetic markers
    before serialization, avoiding collection of any authentic field values.
    Browser output contains only field *names* and numeric counts.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {'state': 'BROWSER_UNAVAILABLE_HARD_HOLD', 'browser_egress_verified': False}
    try:
        markup = raw.decode('utf-8', 'strict')
    except (UnicodeError, AttributeError):
        return {'state': 'INVALID_INPUT_HARD_HOLD', 'browser_egress_verified': False}
    observations = []
    try:
        with sync_playwright() as pw:
            for enabled in (False, True):
                browser = pw.chromium.launch(headless=True, executable_path=executable,
                                             args=['--no-sandbox'])
                try:
                    ctx = browser.new_context(java_script_enabled=enabled,
                                              accept_downloads=False)
                    page = ctx.new_page()
                    page.route('**/*', lambda route: route.abort())
                    csp = ('<meta http-equiv="Content-Security-Policy" '
                           'content="default-src \'none\'; script-src \'none\'; '
                           'connect-src \'none\'; form-action \'none\'; base-uri \'none\'">')
                    page.set_content(csp + markup, wait_until='domcontentloaded',
                                     timeout=timeout_ms)
                    forms = page.locator('form').evaluate_all('''forms => forms.map((f) => {
                        // Replace values with synthetic test-only data. No user data is read.
                        for (const el of Array.from(f.elements)) {
                            if ('value' in el && el.type !== 'file' &&
                                el.type !== 'submit' && el.type !== 'image') {
                                try { el.value = 'R326_SYNTHETIC'; } catch (_) {}
                            }
                        }
                        const fd = new FormData(f);
                        return {
                          method: f.method.toUpperCase(),
                          named: Array.from(f.elements).filter(el => el.name && !el.disabled).length,
                          successful: Array.from(fd.keys()).length,
                          field_names: Array.from(new Set(fd.keys())).sort(),
                          submit_buttons: Array.from(f.elements).filter(
                            el => (el.tagName === 'BUTTON' && el.type === 'submit') ||
                             (el.tagName === 'INPUT' && el.type === 'submit')).length
                        };
                    })''')
                    observations.append({'javascript_enabled': enabled, 'forms': forms})
                    ctx.close()
                finally:
                    browser.close()
    except Exception as error:
        return {'state': 'BROWSER_ERROR_HARD_HOLD',
                'error_class': type(error).__name__,
                'browser_egress_verified': False,
                'observations': observations}
    return {'state': 'OFFLINE_DOM_FORMDATA_SHAPE_ONLY_HARD_HOLD',
            'observations': observations, 'navigation_attempted': False,
            'network_submission_attempted': False,
            'browser_egress_verified': False}


def audit(loader, *, browser=False) -> dict:
    entries, errors = [], []
    for slug in sorted(r324.PINS):
        path = f'preparedness/content/tools/{slug}.body.html'
        try:
            raw = loader(path)
            if custody.blob(raw) != r324.PINS[slug]:
                raise ValueError('PIN_MISMATCH')
            entry = {'slug': slug, 'blob_sha': r324.PINS[slug], **inspect(raw)}
            if browser:
                entry['offline_browser'] = chromium_preflight(raw)
            entries.append(entry)
        except (ValueError, TypeError, UnicodeError, OSError) as error:
            errors.append(f'{slug}:{type(error).__name__}')
    return {'schema': SCHEMA,
            'state': 'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors': sorted(set(errors)), 'tool_count': len(entries),
            'entries': entries, 'release': RELEASE.copy()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument('--browser', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        mp = root / custody.MANIFEST_PATH
        if mp.is_symlink():
            raise OSError('SYMLINKED_MANIFEST')
        manifest = json.loads(mp.read_text(encoding='utf-8'))
        if custody.validate_manifest(manifest, root)['errors']:
            raise ValueError('INVALID_MANIFEST')
        output = audit(lambda path: custody.safe_bytes(root, path),
                       browser=args.browser)
    except (OSError, ValueError, UnicodeError, KeyError, TypeError):
        output = {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD',
                  'errors': ['AUTHENTIC_REPOSITORY_UNAVAILABLE_OR_INVALID'],
                  'entries': [], 'release': RELEASE.copy()}
    print(json.dumps(output, sort_keys=True, indent=2))
    return 2 if output['state'] == 'DRAFT_HARD_HOLD' else 1


if __name__ == '__main__':
    raise SystemExit(main())
