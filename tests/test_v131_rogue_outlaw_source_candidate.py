"""v131: official MID2 Rogue Outlaw pinned source, newly source-connected.

Checks source completeness and validates exact existing Rogue tier compatibility.
No simulation, no cache mutation; Native acceptance still pending.
"""
from __future__ import annotations
import hashlib,pathlib,sys,unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v055_simc_item_selection as items
import v104_shared_pinned_rogue_shaman_composer as existing
import v127_dps_source_metadata as registry
import v129_common_source_fields as fields

PROFILE=ROOT/"integration_probes"/"fixtures"/"v131_upstream_mid2_rogue_outlaw_reference.simc"
BLOB="738f7fe64c1d75159b86ecc2e8064dc29c69c203"
UPSTREAM_COMMIT="426ad85ecb1c5d9a1af166931478dabf29b42fdd"

class OutlawStagedSource(unittest.TestCase):
    @staticmethod
    def need(ok,why):
        if not ok:raise ValueError(why)

    def test_exact_official_source_blob_and_full_apl(self):
        raw=PROFILE.read_bytes()
        self.assertEqual(hashlib.sha1(
            b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw
        ).hexdigest(),BLOB)
        text=raw.decode("utf8")
        values=fields.settings(text,("spec","race","role","talents",
                                      "flask","food","potion"))
        self.assertEqual(values["spec"],"outlaw")
        self.assertEqual(values["race"],"dwarf")
        self.assertEqual(values["role"],"attack")
        self.assertTrue(values["talents"].startswith("CQQ"))
        self.assertEqual(values["flask"],"flask_of_the_shattered_sun_2")
        self.assertIn('rogue="MID2_Rogue_Outlaw"',text)
        actions=fields.matching_lines(text,"actions")
        self.assertGreaterEqual(len(actions),15)
        self.assertEqual(sum(x.startswith("actions=") for x in actions),1)

    def test_source_exact_tier_and_weapon_identity_for_next_spec(self):
        raw=PROFILE.read_text(encoding="utf8")
        ids,mods=fields.equipment(raw,items.SLOTS,need=self.need,
            duplicate_prefix="OUTLAW_DUPLICATE_SLOT:",
            missing_id_prefix="OUTLAW_ITEM_MISSING:",include_gem_enchant=True)
        self.assertEqual(set(ids),set(items.SLOTS))
        self.assertEqual({slot:ids[slot] for slot in
                          ("head","shoulders","chest","hands","legs")},
                         existing.TIERS["rogue"])
        self.assertEqual(ids["main_hand"],268209)
        self.assertEqual(ids["off_hand"],275070)
        self.assertEqual(mods["head"]["gem_id"],"240967")
        self.assertEqual(len(mods["neck"]["gem_id"].split("/")),2)
        self.assertEqual(ids["trinket1"],270175)
        self.assertEqual(ids["trinket2"],270173)

    def test_new_spec_uses_same_registry_without_new_optimizer(self):
        record=registry.get(("rogue","outlaw"))
        self.assertEqual(record.source_git_blob,BLOB)
        self.assertEqual(record.weapon_form,"dual_one_hand")
        self.assertEqual(record.fifth_replacement(),("chest",271513,251159))
        self.assertEqual(record.flask_vector()["crit_rating"],165)
        self.assertIn(("rogue","subtlety"),registry.BY_SPEC)
        self.assertNotIn(("priest","shadow"),registry.BY_SPEC)

if __name__=="__main__":
    unittest.main()
