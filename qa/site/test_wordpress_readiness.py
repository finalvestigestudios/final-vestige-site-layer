"""Unit tests for the inert, snapshot-only Final Vestige readiness checker."""
import json
import tempfile
import unittest
from pathlib import Path

from wordpress_readiness import blocks, inspect, main


class ReadinessTests(unittest.TestCase):
    def codes(self,snapshot):
        return {x['code'] for x in inspect(snapshot)}

    def test_gutenberg_parser(self):
        markup='<!-- wp:navigation-submenu {"label":"Research","type":"custom","url":"/research/"} --><!-- wp:navigation-link {"label":"Foo","url":"/foo/"} /--><!-- /wp:navigation-submenu -->'
        names=[(closing,name) for closing,name,_,_ in blocks(markup)]
        self.assertEqual(names,[(False,'navigation-submenu'),(False,'navigation-link'),(True,'navigation-submenu')])

    def test_duplicate_jetpack_subscriptions_detected(self):
        markup='<!-- wp:jetpack/subscriptions {"appSource":"one"} /--><!-- wp:jetpack/subscriptions {"appSource":"two"} /-->'
        self.assertIn('DUPLICATE_SUBSCRIBE',self.codes({'navigation_markup':markup}))

    def test_single_subscription_clean(self):
        self.assertNotIn('DUPLICATE_SUBSCRIBE',self.codes({'navigation_markup':'<!-- wp:jetpack/subscriptions {} /-->'}))

    def test_submenu_links_do_not_inflate_root_count(self):
        markup='<!-- wp:navigation-submenu {"label":"Research","url":"/research/"} -->'+'<!-- wp:navigation-link {"label":"Foo","url":"/foo/"} /-->'*20+'<!-- /wp:navigation-submenu -->'
        self.assertNotIn('DENSE_NAVIGATION',self.codes({'navigation_markup':markup}))

    def test_many_root_items_flagged(self):
        markup=''.join(f'<!-- wp:navigation-link {{"label":"{i}","url":"/{i}/"}} /-->' for i in range(12))
        self.assertIn('DENSE_NAVIGATION',self.codes({'navigation_markup':markup}))

    def test_root_duplicate_ignores_querystring(self):
        markup='<!-- wp:navigation-link {"label":"A","url":"https://finalvestige.com/a/?utm=1"} /--><!-- wp:navigation-link {"label":"B","url":"/a/"} /-->'
        self.assertIn('DUPLICATE_ROOT_LINK',self.codes({'navigation_markup':markup}))

    def test_alerts_from_security_backup_and_identity(self):
        codes=self.codes({'navigation_markup':'<!-- wp:navigation-link {"label":"Home","url":"/"} /-->',
                          'settings':{'identity':{'site_icon':0,'site_logo':0}},
                          'monitor':{'monitor_active':False},
                          'backup':{'backups':{'last_attempt_failed':True,'last_attempt_status':'error'}},
                          'scan':{'threats':[{'id':1}]}})
        for code in ('MISSING_SITE_ICON','MISSING_SITE_LOGO_SETTING','MONITOR_DISABLED','BACKUP_FAILED','ACTIVE_THREATS'):
            self.assertIn(code,codes)

    def test_homepage_holding_page_flag(self):
        snap={'navigation_markup':'<!-- wp:navigation-link {"label":"Home","url":"/"} /-->',
              'homepage_html':'<a href="/watch/films/">Our films</a>',
              'landing_pages':{'https://finalvestige.com/watch/films/':'Films will appear here as they are released.'}}
        self.assertIn('FEATURED_HOLDING_PAGE',self.codes(snap))

    def test_cli_exit_code(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'snap.json'
            p.write_text(json.dumps({'navigation_markup':'<!-- wp:jetpack/subscriptions /--><!-- wp:jetpack/subscriptions /-->'}))
            self.assertEqual(main([str(p),'--strict']),1)

if __name__=='__main__':
    unittest.main()
