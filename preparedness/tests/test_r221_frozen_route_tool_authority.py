"""R221 35-route and six-tool mutation regressions; synthetic, no archive writes."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / 'tools' / 'r221_frozen_route_tool_authority.py'
spec = importlib.util.spec_from_file_location('r221_frozen_route_tool_authority', MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def synthetic_roster():
    return [dict(n=n, slug=f'article-{n}', section='start-here', track='modern',
                 route=f'/preparedness/start-here/article-{n}/') for n in range(1, 36)]


class RouteTests(unittest.TestCase):
    def setUp(self):
        self.roster = synthetic_roster()
        self.routes = {a['slug']: a['route'] for a in self.roster}
        self.routes.update({name: f'/preparedness/field-tools/{name}/' for name in gate.FROZEN_TOOLS})

        class Library:
            def __init__(self, routes):
                self.routes = routes
                self.articles = {slug: {} for slug in routes}
            def url_path(self, slug):
                return self.routes[slug]
        self.lib = Library(self.routes)

    def test_valid_frozen_routes(self):
        gate.verify_routes(self.roster, self.lib)

    def test_missing_tool(self):
        self.lib.articles.pop('water-planner')
        with self.assertRaisesRegex(ValueError, '41 exact'):
            gate.verify_routes(self.roster, self.lib)

    def test_extra_tool(self):
        self.lib.articles['mystery-tool'] = {}
        with self.assertRaisesRegex(ValueError, '41 exact'):
            gate.verify_routes(self.roster, self.lib)

    def test_duplicate_tool_route(self):
        names = list(gate.FROZEN_TOOLS)
        self.lib.routes[names[0]] = self.lib.routes[names[1]]
        with self.assertRaisesRegex(ValueError, 'canonical route'):
            gate.verify_routes(self.roster, self.lib)


def article_route_mutation(n):
    def test(self):
        slug = f'article-{n}'
        self.lib.routes[slug] = f'/dangerous/hijacked/{slug}/'
        with self.assertRaisesRegex(ValueError, 'canonical route'):
            gate.verify_routes(self.roster, self.lib)
    return test


def tool_route_mutation(slug):
    def test(self):
        self.lib.routes[slug] = f'/preparedness/other/{slug}/'
        with self.assertRaisesRegex(ValueError, 'canonical route'):
            gate.verify_routes(self.roster, self.lib)
    return test


for _n in range(1, 36):
    setattr(RouteTests, f'test_article_{_n:02}_hijacked_from_mutable_taxonomy', article_route_mutation(_n))
for _slug in gate.FROZEN_TOOLS:
    setattr(RouteTests, 'test_tool_' + _slug.replace('-', '_') + '_hijacked', tool_route_mutation(_slug))


class SourceAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='fv-r221-synthetic-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'content' / 'tools').mkdir(parents=True)
        self.roster = synthetic_roster()
        taxonomy = {'base_path': '/preparedness/', 'slate': [
            {k: a[k] for k in ('n', 'slug', 'section', 'track')} for a in self.roster]}
        tax_bytes = json.dumps(taxonomy).encode()
        (self.root / 'taxonomy.json').write_bytes(tax_bytes)
        self.oid = gate.git_blob(tax_bytes)
        self.pins = {}
        for slug in gate.FROZEN_TOOLS:
            body = f'<h2>Original body of {slug}</h2>'.encode()
            meta = json.dumps({'slug': slug, 'kind': 'tool', 'section': 'field-tools',
                               'track': 'modern', 'status': {'publish': 'draft'}}).encode()
            (self.root / 'content' / 'tools' / (slug + '.body.html')).write_bytes(body)
            (self.root / 'content' / 'tools' / (slug + '.meta.json')).write_bytes(meta)
            self.pins[slug] = (gate.git_blob(body), gate.git_blob(meta))
        from contextlib import ExitStack
        self.stack = ExitStack()
        self.stack.enter_context(patch.object(gate, 'TAXONOMY_OID', self.oid))
        self.stack.enter_context(patch.object(gate, 'FROZEN_TOOLS', self.pins))
        self.addCleanup(self.stack.close)

    def read(self, root, relative):
        path = root / relative
        if path.is_symlink():
            raise ValueError('symlink source')
        return path.read_bytes()

    def check(self):
        return gate.verify_authorities(self.root, self.roster, self.read)

    def test_valid_all_six_tools(self):
        self.assertEqual(self.check()['tool_inputs_pinned'], 12)

    def test_taxonomy_base_path_hijack(self):
        p = self.root / 'taxonomy.json'
        p.write_text(p.read_text().replace('/preparedness/', '/hijack/'))
        with self.assertRaisesRegex(ValueError, 'taxonomy authority'):
            self.check()

    def test_taxonomy_slugs_modified_even_with_rehashed_pin(self):
        p = self.root / 'taxonomy.json'
        p.write_text(p.read_text().replace('article-4', 'article-fake'))
        with patch.object(gate, 'TAXONOMY_OID', gate.git_blob(p.read_bytes())):
            with self.assertRaisesRegex(ValueError, 'taxonomy/frozen'):
                self.check()

    def test_extra_tool_input(self):
        (self.root / 'content' / 'tools' / 'bogus.meta.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'tool inputs'):
            self.check()

    def test_missing_tool_input(self):
        (self.root / 'content' / 'tools' / 'kit-builder.meta.json').unlink()
        with self.assertRaisesRegex(ValueError, 'tool inputs'):
            self.check()

    def test_symlinked_tool_dir(self):
        (self.root / 'content' / 'tools').rename(self.root / 'realdir')
        (self.root / 'content' / 'tools').symlink_to(self.root / 'realdir', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlinked tool'):
            self.check()

    def test_duplicate_json_metadata(self):
        p = self.root / 'content' / 'tools' / 'water-planner.meta.json'
        p.write_text('{"slug":"water-planner","slug":"injected"}')
        pins = dict(self.pins)
        pins['water-planner'] = (pins['water-planner'][0], gate.git_blob(p.read_bytes()))
        with patch.object(gate, 'FROZEN_TOOLS', pins):
            with self.assertRaisesRegex(ValueError, 'duplicate JSON'):
                self.check()


def mutated_tool_input(slug, extension):
    def test(self):
        p = self.root / 'content' / 'tools' / (slug + '.' + extension)
        p.write_bytes(p.read_bytes() + b' INJECTED')
        with self.assertRaisesRegex(ValueError, 'provenance mismatch'):
            self.check()
    return test


for _slug in gate.FROZEN_TOOLS:
    for _ext in ('body.html', 'meta.json'):
        setattr(SourceAuthorityTests, 'test_mutated_' + _slug.replace('-', '_') + '_' + _ext.replace('.', '_'),
                mutated_tool_input(_slug, _ext))


if __name__ == '__main__':
    unittest.main()
