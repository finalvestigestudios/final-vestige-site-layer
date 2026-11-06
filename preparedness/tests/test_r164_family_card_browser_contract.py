"""Synthetic-only security/UX mutation tests; NOT real browser, privacy or safety approval."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('r164_contract', ROOT / 'tools' / 'r164_family_card_browser_contract.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def fixture():
    fields = ''.join(
        '<label for="%s">Label</label><input id="%s" type="%s" %s>' % (
            fid, fid, kind, ('maxlength="%d" autocomplete="off"' % maxlen) if maxlen is not None else '')
        for fid, (kind, maxlen) in gate.FIELDS.items())
    return ("<section>A printed card can be lost. Do not put a child's full name on it. "
            "Every field is optional. Choose the minimal version.</section>" +
            '<form id="rc" onsubmit="return false"><p id="rc-help">Help</p>' +
            '<label for="rc-minimal">Minimal</label><input id="rc-minimal" type="checkbox">' +
            '<label for="rc-copies">Copies</label><select id="rc-copies"><option>1</option></select>' + fields +
            '<button id="rc-print" type="button" hidden>Print</button>' +
            '<button id="rc-reset" type="button" hidden>Clear</button></form>' +
            ''.join('<p id="%s"></p>' % x for x in ('rc-meet1-h','rc-schoolPlan-h','rc-pickup-h','rc-access-h')) +
            '<p id="rc-warn" aria-live="polite"></p><div id="rc-live" hidden>' +
            '<div id="rc-preview"></div><div id="rc-sheet"></div></div>' +
            '<noscript>Blank paper card</noscript><noscript>Print by hand</noscript>' +
            '<p>{{cite:shelter-cdc-reunification}}{{cite:shelter-ncmec-hotline}}</p>' +
            '<script>{{inline-js:shelter_common.js}}{{inline-js:reunion_card.js}}' +
            'document.createTextNode(r.v);e.textContent = text;form.reset(); render();window.print();</script>')


class ContractTest(unittest.TestCase):
    def test_valid_fixture_remains_hard_hold(self):
        r = gate.check_html(fixture())
        self.assertEqual((r['state'], r['controls_checked']), ('DRAFT_HARD_HOLD', 17))
        for f in ('script_runtime_inspected','network_privacy_verified','browser_print_verified',
                  'mobile_a11y_verified','independent_safety_review','publication_authorized','paid_offer_verified'):
            self.assertFalse(r[f])

    def test_cli_missing_checkout_fails_closed(self):
        self.assertEqual(gate.main(['--repo','/unavailable/r164']), 2)


def make_test(mutate):
    def run(self):
        with self.assertRaises(ValueError):
            gate.check_html(mutate(fixture()))
    return run


CASES = {}
for fid, (kind, lim) in gate.FIELDS.items():
    CASES['missing_field_'+fid] = lambda s, fid=fid: s.replace('id="'+fid+'"', 'id="removed"', 1)
    CASES['missing_label_'+fid] = lambda s, fid=fid: s.replace('for="'+fid+'"', 'for="removed"', 1)
    if lim is not None:
        old = 'id="'+fid+'" type="'+kind+'" maxlength="'+str(lim)+'"'
        CASES['long_field_'+fid] = lambda s, old=old, lim=lim: s.replace(old, old.replace('maxlength="'+str(lim)+'"','maxlength="1000"'), 1)
for i, expression in enumerate((
    'fetch("/collect")', 'sendBeacon("/data",payload)', 'new XMLHttpRequest()',
    'new WebSocket("wss://x")', 'new EventSource("/events")', 'localStorage.x=1',
    'sessionStorage.x=1', 'indexedDB.open("x")', 'document.cookie="x"',
    'window.location = "/collect"', 'document.location = "/collect"',
    'postMessage(value,"*")', 'new FormData(form)',
    'navigator.serviceWorker.register("/x")', 'eval(value)', 'element.innerHTML = value',
    'element.outerHTML = value', 'element.insertAdjacentHTML("beforeend",value)',
    'document.write(value)', 'new Image().src="/pixel"', '$.ajax({url:"/x"})',
    '$.post("/x")', '$.get("/x")')):
    CASES['script_exfil_'+str(i)] = lambda s, expression=expression: s.replace('</script>', expression+'</script>', 1)
for i, tag in enumerate((
    '<iframe src="https://x"></iframe>', '<object data="x"></object>',
    '<embed src="https://x">', '<base href="https://x">',
    '<meta http-equiv="refresh" content="x">', '<input type="hidden" name="x">',
    '<a href="/ok" ping="https://x">See</a>', '<div contenteditable="true">Edit</div>',
    '<img src="/pixel">', '<style>@import url(https://x)</style>',
    '<script src="https://x"></script>', '<p>Data are never stored</p>',
    '<p>guaranteed private</p>', '<button type="submit">Send</button>',
    '<div onmouseover="send()">Hover</div>', '<div id="rc-preview">Duplicate</div>',
    '<script>{{inline-js:untrusted.js}}</script>')):
    CASES['injected_markup_'+str(i)] = lambda s, tag=tag: s.replace('</section>', tag+'</section>', 1)
for i, (old, new) in enumerate((
    ('onsubmit="return false"','onsubmit="return true"'),
    ('id="rc-print" type="button"','id="rc-print" type="submit"'),
    ('id="rc-reset" type="button"','id="rc-reset" type="submit"'),
    ('id="rc-warn" aria-live="polite"','id="rc-warn" aria-live="off"'),
    ('id="rc-live" hidden','id="rc-live"'),
    ('rc-print" type="button" hidden','rc-print" type="button"'),
    ('rc-reset" type="button" hidden','rc-reset" type="button"'),
    ('{{cite:shelter-ncmec-hotline}}','{{cite:wrong}}'),
    ('{{inline-js:reunion_card.js}}','{{inline-js:rogue.js}}'),
    ('document.createTextNode(r.v)','document.createElement(r.v)'),
    ('form.reset(); render();','form.reset();'),
    ('window.print();','alert("print")'),
    ("Do not put a child's full name", "Put a child's full name"),
    ('id="rc" onsubmit','id="rc" id="duplicate" onsubmit'),
    ('id="rc-hhName"','id="rc-hhName" name="secret"'),
    ('id="rc-hhPhone"','id="rc-hhPhone" value="prefilled"'),
    ('id="rc-meet1"','id="rc-meet1" form="other"'))):
    CASES['tamper_'+str(i)] = lambda s, old=old, new=new: s.replace(old,new)
for name, mutate in CASES.items():
    setattr(ContractTest, 'test_reject_'+name.replace('-', '_'), make_test(mutate))

if __name__ == '__main__':
    unittest.main()
