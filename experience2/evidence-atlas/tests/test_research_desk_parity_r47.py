"""R47 source-link parity contract with synthetic inputs; real R38 requires --ledger."""
import sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE/'tests'))
import build_atlas
from check_research_desk_parity_r47 import verify_ledger


def synthetic_ledger():
    custody=build_atlas.validate_custody()
    return '<section data-fvx-ledger>'+''.join(
        '<article data-fvx-record id="fv-ex2-ledger-apollo1-record-'+r['id']+'">'
        '<div class="fv-ex2-ledger__recordid">NASA '+r['catalog']+' · NASA</div>'
        '<a href="'+r['photo_url']+'">NASA archive record</a>'
        '<details data-fvx-photo-record="'+r['id']+'"><summary>Provenance</summary></details>'
        '</article>' for r in custody['records'])+'</section>'

class ConcordanceR47(unittest.TestCase):
    def test_six_verified_sources(self):
        r=verify_ledger(synthetic_ledger())
        self.assertEqual(r['identity_and_photo_url_parity'],'PASS')
        self.assertEqual(r['historical_claim_parity'],'NOT_ASSESSED')
        self.assertEqual(len(r['records']),6)
    def test_wrong_url_rejected(self):
        self.assertRaises(ValueError,verify_ledger,synthetic_ledger().replace('www.nasa.gov/image-detail/apollo-1-crew-honored/','www.nasa.gov/image-detail/wrong/'))
    def test_wrong_photo_id_rejected(self):
        self.assertRaises(ValueError,verify_ledger,synthetic_ledger().replace('data-fvx-photo-record="03"','data-fvx-photo-record="99"'))
    def test_missing_card_rejected(self):
        self.assertRaises(ValueError,verify_ledger,synthetic_ledger().split('<article')[0]+'</section>')

if __name__=='__main__':unittest.main()
