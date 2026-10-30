import json
import tempfile
import unittest
from pathlib import Path
from retired_navigation_guard import canonical, find_links, analyze, proposed_remove, main


def link(label, url):
    return '<!-- wp:navigation-link ' + json.dumps({'label': label, 'type':'custom', 'url':url}, separators=(',', ':')) + ' /-->'


class RetiredNavigationTests(unittest.TestCase):
    def setUp(self):
        self.raw = link('Home', 'https://finalvestige.com/') + '\n' + link('Water Resilience Field Manual', 'https://finalvestige.com/collection/water-resilience-field-manual/') + '\n' + link('Free Focus Fieldbook', 'https://finalvestige.com/focus/')
        self.inventory = [{'id': 6, 'link': 'https://finalvestige.com/', 'status':'publish'},
                          {'id': 85, 'link': 'https://finalvestige.com/collection/water-resilience-field-manual/', 'status':'draft'},
                          {'id': 1579, 'link': 'https://finalvestige.com/focus/', 'status':'publish'}]

    def test_detects_draft_destination(self):
        r = analyze(self.raw, self.inventory)
        self.assertEqual(len(r['findings']), 1)
        self.assertEqual(r['findings'][0]['destination_id'], 85)

    def test_does_not_flag_published_focus(self):
        self.assertTrue(all(x['destination_id'] != 1579 for x in analyze(self.raw, self.inventory)['findings']))

    def test_remove_only_requested_link(self):
        next_raw = proposed_remove(self.raw, '/collection/water-resilience-field-manual/')
        self.assertIn('Free Focus Fieldbook', next_raw)
        self.assertIn('Home', next_raw)
        self.assertNotIn('Water Resilience', next_raw)
        self.assertEqual(len(find_links(next_raw)), 2)

    def test_fail_closed_when_missing(self):
        with self.assertRaises(ValueError): proposed_remove(self.raw, '/missing/')

    def test_fail_closed_when_duplicate(self):
        with self.assertRaises(ValueError): proposed_remove(self.raw + '\n' + link('Duplicate', '/collection/water-resilience-field-manual/'), '/collection/water-resilience-field-manual/')

    def test_ignores_external_mail_and_fragment(self):
        self.assertIsNone(canonical('https://another-site.com/anything'))
        self.assertIsNone(canonical('mailto:hello@example.com'))
        self.assertIsNone(canonical('#section'))

    def test_same_site_www_query_normalized(self):
        self.assertEqual(canonical('https://www.finalvestige.com/focus/?x=2#top'), '/focus')

    def test_invalid_json_ignored(self):
        self.assertEqual(find_links('<!-- wp:navigation-link {wrong} /-->'), [])

    def test_draft_to_publish_rechecks_clean(self):
        item = [dict(i) for i in self.inventory]
        item[1]['status'] = 'publish'
        self.assertEqual(analyze(self.raw, item)['findings'], [])

    def test_cli_creates_proposal_without_overwriting(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'snapshot.json'
            source.write_text(json.dumps({'navigation_markup':self.raw,'inventory':self.inventory}), encoding='utf-8')
            proposal = root / 'proposed.html'
            self.assertEqual(main([str(source), '--propose-remove', '/collection/water-resilience-field-manual/', '--output', str(proposal)]), 1)
            self.assertTrue(proposal.exists())
            self.assertNotIn('Water Resilience', proposal.read_text())
            with self.assertRaises(SystemExit):
                main([str(source), '--propose-remove', '/collection/water-resilience-field-manual/', '--output', str(proposal)])

if __name__ == '__main__': unittest.main()
