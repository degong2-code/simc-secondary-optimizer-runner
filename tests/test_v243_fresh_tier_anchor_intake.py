"""Synthetic current-publication tier title to exact 13x5 DB2 provenance."""
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from runner import v243_fresh_tier_anchor_intake as v
from runner import v168_current_season_tier_discovery as tier
from tests.test_v168_current_season_tier_discovery import synthetic

BUILD="12.2.0.99999"
def fixture():
    names={cl:("Echo of Calamity" if cl=="evoker" else
               "New "+cl+" Regalia") for cl in tier.FAMILY}
    html=("<h1>Tier sets Midnight Season 2</h1>"+"".join(
        "<p>"+v.ALIASES[cl]+"</p><div>"+names[cl]+"</div>"
        for cl in sorted(names))).encode()
    out=io.StringIO()
    writer=csv.DictWriter(out,fieldnames=("ID","Name_lang"))
    writer.writeheader()
    for idx,cl in enumerate(sorted(names)):
        writer.writerow({"ID":500+idx,"Name_lang":names[cl]})
    return html,out.getvalue().encode()

class FreshTierInputTest(unittest.TestCase):
    def test_public_titles_find_exact_itemsets_and_v168_physical_pieces(self):
        html,raw=fixture()
        anchor=v.parse_anchor(publisher_raw=html,itemset_raw=raw,
            build=BUILD,expansion_id=11,mplus_zone="Mythic+ Season 2")
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            synthetic(root)
            result=tier.discover(anchor,root/"ItemSparse.csv",
                                 root/"Item.csv")
            self.assertEqual(result["class_count"],13)
            self.assertEqual(result["item_count"],65)
            self.assertTrue(result["evidence"][
                "verified_new_season_itemset_name_match"])
            self.assertEqual(anchor["classes"]["evoker"],"Echo of Calamity")
            self.assertFalse(result["production_profile_promoted"])
    def test_stale_publisher_and_ambiguous_set_block(self):
        html,raw=fixture()
        with self.assertRaisesRegex(v.TierSourceBlocked,
                                    "TIER_PUBLISHER_SEASON_MISMATCH"):
            v.parse_anchor(publisher_raw=html.replace(b"Season 2",b"Season 1"),
                itemset_raw=raw,build=BUILD,expansion_id=11,
                mplus_zone="Mythic+ Season 2")
        with self.assertRaisesRegex(v.TierSourceBlocked,
                                    "TIER_PUBLISHER_CLASS_ITEMSET_NOT_UNIQUE"):
            v.parse_anchor(publisher_raw=html,itemset_raw=raw+
                b'99999,Echo of Calamity\n',build=BUILD,expansion_id=11,
                mplus_zone="Mythic+ Season 2")
    def test_live_source_stage_reuses_without_second_network_request(self):
        html,raw=fixture()
        requests=[]
        class Response(io.BytesIO):
            status=200
            def __enter__(self):return self
            def __exit__(self,*unused):self.close()
        def transport(req,timeout):
            requests.append(req.full_url)
            return Response(html if req.full_url==v.SOURCE_URL else raw)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            stage=root/"stage";stage.mkdir()
            wago=root/"wago";wago.mkdir()
            synthetic(wago)
            args=dict(stage_root=stage,wago_folder=wago,build=BUILD,
                expansion_id=11,mplus_zone="Mythic+ Season 2",
                wago_receipt_sha256="f"*64,transport=transport)
            first=v.build_from_public_source(**args)
            second=v.build_from_public_source(**args)
            self.assertEqual(len(requests),2)
            self.assertEqual(first["source_stage"]["status"],
                             "EXECUTED_AND_SEALED")
            self.assertEqual(second["source_stage"]["status"],
                             "REUSED_VERIFIED")
            self.assertEqual(second["network_calls_by_stage"],0)
            self.assertFalse(first["environment_ready"])
            self.assertTrue(Path(first["tier_candidate_path"]).is_file())
if __name__=="__main__":
    unittest.main()
