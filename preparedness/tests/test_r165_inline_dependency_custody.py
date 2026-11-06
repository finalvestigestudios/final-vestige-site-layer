"""R165 mutation regressions: deliberately synthetic, never a browser or privacy approval."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'tools' / 'r165_inline_dependency_custody.py'
spec = importlib.util.spec_from_file_location('r165_gate', MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def common():
    return ('function paCleanText(x){return x;} function paIsoOrNull(x){return x;} '
            'function paDownloadText(){var blob=new Blob(["X"], {type:"text/plain;charset=utf-8"});'
            'var url=URL.createObjectURL(blob);URL.revokeObjectURL(url);}')


def reunion():
    return ('function rcClean(x){return x;} function rcModel(x,minimal){'
            'minimal ? null : row("If not, meet at", c.meet2);var back = minimal;return x;} '
            'function rcWarnings(){} function rcLooksLikeStreetAddress(){} '
            'function rcLooksLikeGovId(){}')


def template():
    return '<script>{{inline-js:shelter_common.js}}\n{{inline-js:reunion_card.js}}</script>'


class ClosureTests(unittest.TestCase):
    def test_synthetic_closure_expands_only_twice(self):
        output, report = gate.expand_checked(
            template(), {'shelter_common.js':common(), 'reunion_card.js':reunion()})
        self.assertEqual(report['dependency_order'],list(gate.EXPECTED))
        self.assertIn('function rcModel(',output)
        self.assertNotIn('{{inline-js:',output)

    def test_missing_repo_fails_closed(self):
        self.assertEqual(gate.main(['--repo','/no-such-archive-r165']),2)

    def test_git_blob_deterministic(self):
        self.assertEqual(gate.git_blob(b'test'),'30d74d258442c7c65512eafab474568dd706c430')

    def test_model_unavailable_is_not_a_pass(self):
        self.assertEqual(gate.model_smoke({},executable='')['model_smoke'],'NOT_RUN_NODE_MISSING')

    def test_bad_node_fails_closed(self):
        with self.assertRaises(ValueError):
            gate.model_smoke({'shelter_common.js':'broken', 'reunion_card.js':'invalid'},executable='node')


def mutation_test(script_name, inject):
    def run(self):
        scripts={'shelter_common.js':common(), 'reunion_card.js':reunion()}
        scripts[script_name]=inject(scripts[script_name])
        with self.assertRaises(ValueError):
            gate.expand_checked(template(),scripts)
    return run


PAYLOADS = [
 'fetch("/collect")','navigator.sendBeacon("/collect",secret)',
 'new XMLHttpRequest()','new WebSocket("wss://bad")',
 'new EventSource("/events")','localStorage.x=123','sessionStorage["x"]=1',
 'indexedDB.open("x")','document.cookie="abc"',
 'postMessage(data,"*")','new FormData(form)','navigator.serviceWorker.register("/s")',
 'eval(secret)','Function("return 2")()', 'import("https://bad")',
 'element.innerHTML = content','element.outerHTML = content',
 'element.insertAdjacentHTML("beforeend",content)','document.write(content)',
 'window.open("/out")','setAttribute("src","/out")',
 'https://untrusted.test/x','data:text/html;base64,abc','</script><script>evil()</script>',
 '<!-- hidden -->', ']]>', '{{inline-js:evil.js}}',
]
for name in ('shelter_common.js','reunion_card.js'):
    for index, payload in enumerate(PAYLOADS):
        method=f'test_reject_{name.split(".")[0]}_payload_{index:02d}'
        setattr(ClosureTests,method,mutation_test(name,lambda s,payload=payload:s+'\n'+payload))


def template_test(modify):
    def run(self):
        with self.assertRaises(ValueError):
            gate.expand_checked(modify(template()),{'shelter_common.js':common(),'reunion_card.js':reunion()})
    return run


for i, mut in enumerate((
    lambda x:x.replace('{{inline-js:reunion_card.js}}',''),
    lambda x:x.replace('{{inline-js:reunion_card.js}}','{{inline-js:unknown.js}}'),
    lambda x:x.replace('{{inline-js:shelter_common.js}}',''),
    lambda x:x.replace('{{inline-js:reunion_card.js}}','{{inline-js:reunion_card.js}}{{inline-js:reunion_card.js}}'),
    lambda x:x.replace('{{inline-js:shelter_common.js}}\n{{inline-js:reunion_card.js}}',
                       '{{inline-js:reunion_card.js}}\n{{inline-js:shelter_common.js}}'),
    lambda x:x.replace('{{inline-js:reunion_card.js}}','{{inline-js:reunion_card.js}}\n{{inline-js:evil.js}}'),
    lambda x:x.replace('{{inline-js:reunion_card.js}}','{{inline-js:reunion_card.js}}\n{{inline-js:evil-file.js}}'),
    lambda x:x.replace('{{inline-js:reunion_card.js}}','{{inline-js:reunion_card.js}}\n{{inline-js:../private.js}}'),
)):
    setattr(ClosureTests,f'test_reject_template_{i}',template_test(mut))

for i, (script,old) in enumerate((
    ('shelter_common.js','URL.revokeObjectURL(url)'),
    ('shelter_common.js','URL.createObjectURL(blob)'),
    ('shelter_common.js','text/plain;charset=utf-8'),
    ('shelter_common.js','function paCleanText('),
    ('reunion_card.js','function rcModel('),
    ('reunion_card.js','function rcWarnings('),
    ('reunion_card.js','function rcLooksLikeGovId('),
    ('reunion_card.js','var back = minimal'),
)):
    setattr(ClosureTests,f'test_reject_contract_removed_{i}',mutation_test(script,lambda s,old=old:s.replace(old,'REMOVED')))

if __name__=='__main__':unittest.main()
