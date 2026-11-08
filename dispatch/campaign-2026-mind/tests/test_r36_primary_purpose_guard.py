"""Adversarial R36 all-six legal primary purpose preflight tests."""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('fv_r36', ROOT / 'r36-primary-purpose' / 'primary_purpose_guard.py')
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)


def fixture():
    manifest = {'status': 'DRAFT_UNSENT_NO_SCHEDULING',
                'mix': {'editorial': 4, 'commercial_review_pending': 2}, 'issues': []}
    texts = {}
    for n in range(1, 7):
        kind = 'commercial-review-pending' if n in (3, 5) else 'editorial'
        cta = G.GUIDES[n] if n in G.OFFER else 'https://finalvestige.com/editorial-' + str(n) + '/'
        manifest['issues'].append({'number': n, 'subject': f'Subject {n}', 'preheader': f'Preview {n}',
                                   'kind': kind, 'editorial_cta': cta,
                                   'publish_state': 'hold', 'merchant_affiliate_url': None})
        disclosure = '**Commercial disclosure:** If you buy through the guide, Final Vestige may earn a commission.\n' if n in G.OFFER else ''
        texts[n] = (f'> **STATUS: UNSENT DRAFT — DO NOT PUBLISH OR EMAIL**\n'
                    f'**Subject:** Subject {n}\n**Preheader:** Preview {n}\n'
                    f'**Content type:** {kind}\nSource context.\n{disclosure}Read {cta}\n'
                    f'**Pre-send compliance block — remove/replace ONLY after legal and rendered-email QA.**\n'
                    f'Sender Final Vestige Studios. Address: {G.POSTAL} Unsubscribe: {G.OPT_OUT}')
    return manifest, texts


class R36PrimaryPurpose(unittest.TestCase):
    def test_valid_draft_is_still_six_held_editions(self):
        m, t = fixture()
        r = G.inspect(m, t)
        self.assertTrue(r['structural_integrity'], r)
        self.assertEqual([x['edition'] for x in r['editions']], [1, 2, 3, 4, 5, 6])
        self.assertFalse(r['email_sending_capability'])
        self.assertTrue(all(not x['send_authorized'] for x in r['editions']))

    def test_actual_github_campaign_integrity(self):
        r = G.read_campaign(ROOT)
        self.assertTrue(r['structural_integrity'], r)
        self.assertTrue(all(x['received_jetpack_email_verified'] is False for x in r['editions']))

    def test_editorial_not_automatically_exempt(self):
        m, t = fixture()
        r = G.inspect(m, t)
        self.assertEqual([x['edition'] for x in r['editions'] if x['editorial_allocation']=='editorial'], [1,2,4,6])
        self.assertTrue(all(x['conservative_postal_and_unsubscribe_proof_required'] for x in r['editions']))
        self.assertTrue(all(x['can_spam_primary_purpose'].startswith('UNDETERMINED') for x in r['editions']))

    def test_commercial_permission_and_guides_remain_held(self):
        m, t = fixture()
        r = G.inspect(m, t)
        self.assertEqual([x['edition'] for x in r['editions'] if x['merchant_email_permission_verified'] is False], [3,5])
        self.assertTrue(all(x['release'] == 'HOLD_MERCHANT_AND_UNSENT' for x in r['editions'] if x['edition'] in (3,5)))

    def test_campaign_status_edit_rejected(self):
        m,t=fixture(); m['status']='SEND_READY'
        self.assertFalse(G.inspect(m,t)['structural_integrity'])

    def test_four_two_change_rejected(self):
        m,t=fixture(); m['mix']['editorial']=5
        self.assertFalse(G.inspect(m,t)['structural_integrity'])

    def test_merchant_url_activation_rejected(self):
        m,t=fixture(); m['issues'][2]['merchant_affiliate_url']='https://zen12.com/?aff=unsafe'
        self.assertFalse(G.inspect(m,t)['structural_integrity'])

    def test_undisclosed_offer_rejected(self):
        m,t=fixture(); t[3]=t[3].replace('may earn a commission','has some involvement')
        self.assertFalse(G.inspect(m,t)['structural_integrity'])

    def test_disclosure_after_guide_rejected(self):
        m,t=fixture()
        sentence='**Commercial disclosure:** If you buy through the guide, Final Vestige may earn a commission.\n'
        t[5]=t[5].replace(sentence,'')+'\n'+sentence
        self.assertFalse(G.inspect(m,t)['structural_integrity'])

    def test_premature_publication_rejected(self):
        m,t=fixture(); m['issues'][0]['publish_state']='publish'
        self.assertFalse(G.inspect(m,t)['structural_integrity'])


def mutation(n, field):
    def run(self):
        m,t=fixture()
        if field == 'postal': t[n]=t[n].replace(G.POSTAL,'')
        elif field == 'unsubscribe': t[n]=t[n].replace(G.OPT_OUT,'')
        elif field == 'subject': t[n]=t[n].replace(f'Subject {n}', 'Guaranteed transformation')
        elif field == 'preheader': t[n]=t[n].replace(f'Preview {n}', 'Buy now')
        elif field == 'type': t[n]=t[n].replace('**Content type:**', '**Wrong type:**')
        elif field == 'warning': t[n]=t[n].replace('STATUS: UNSENT DRAFT — DO NOT PUBLISH OR EMAIL', 'READY TO SEND')
        elif field == 'footer': t[n]=t[n].replace('Pre-send compliance block', 'Ordinary text')
        result=G.inspect(m,t)
        self.assertFalse(result['structural_integrity'], (n, field, result))
        self.assertTrue(all(not x['send_authorized'] for x in result['editions']))
    return run


for edition in range(1, 7):
    for bad_field in ('postal','unsubscribe','subject','preheader','type','warning','footer'):
        setattr(R36PrimaryPurpose, f'test_malicious_{bad_field}_issue_{edition}', mutation(edition,bad_field))


if __name__ == '__main__':
    unittest.main()
