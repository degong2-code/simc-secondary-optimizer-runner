"""v171 M+ season selection: include all 223 current dungeon candidates."""
import copy,json,os,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v171_current_mplus_inclusive_gear as update
import v167_product_season_gear_adapter as gear

def real_source():
    source=os.environ.get("SIMC_V166_PRODUCT_GEAR_DB")
    folder=os.environ.get("SIMC_V161_SNAPSHOT_DIR")
    if not source or not folder:return None
    return (json.loads(pathlib.Path(source).read_text()),
            pathlib.Path(folder))

class InclusiveSeasonMplus(unittest.TestCase):
    def test_mplus_provenance_and_unsupported_source_are_not_silently_assumed(self):
        with self.assertRaises(update.InclusionBlocked):
            update.build({},pathlib.Path("/not-item.csv"),
                         pathlib.Path("/not-sparse.csv"))
        self.assertEqual(update.MPLUS_BASIS,
                         "SEASON_MPLUS_JOURNAL_CANDIDATE_WORLDSTATE_UNRESOLVED")

    def test_committed_product_metadata_when_regenerated(self):
        data=gear.read()
        self.assertIn(data["item_count"],(288,511))
        if "mplus_season_candidate_inclusion" not in data:
            self.skipTest("actual inclusive DB not yet committed to branch")
        added=data["mplus_season_candidate_inclusion"]
        self.assertEqual(data["item_count"],511)
        self.assertEqual(data["conditional_ids_excluded"],2)
        self.assertEqual(added["added_item_count"],223)
        self.assertEqual(added["added_roles"],{
            "trinket":27,"special_effect_gear_candidate":4,
            "plain_representative_candidate":192})
        self.assertEqual(added["matched_current_season_dungeons"],8)
        self.assertFalse(added["world_state_effectively_resolved"])
        self.assertFalse(added["actual_drop_or_simc_effect_certified"])
        self.assertEqual(sum(map(len,gear.public_options(data)["choices"].values())),
                         63+14+106)
        self.assertTrue({250215,273796,273649}<={
           x["item_id"] for x in data["items"] if x["category"]=="trinket"})
        self.assertEqual(sum(1 for x in data["items"]
            if x.get("season_list_basis")==update.MPLUS_BASIS),223)

    def test_actual_saved_v166_plus_sha_sealed_same_build_db2(self):
        files=real_source()
        if files is None:
            self.skipTest("real saved v166+v161 evidence not provided to offline job")
        source,folder=files
        receipt=json.loads((folder/"receipt.json").read_text())
        output=update.build(source,folder/"Item.csv",
                            folder/"ItemSparse.csv",receipt=receipt)
        self.assertEqual(output["item_count"],511)
        self.assertEqual(output["role_counts"],{
            "trinket":63,"special_effect_gear_candidate":14,
            "plain_representative_candidate":328,
            "selectable_stat_craft":106})
        self.assertEqual(output["conditional_ids_excluded"],2)
        self.assertFalse(output["mplus_season_candidate_inclusion"]
                         ["world_state_effectively_resolved"])
        self.assertEqual(output["new_api_calls"],0)
        self.assertEqual(output["new_native_calls"],0)

    def test_reject_unexpected_expansion_era_assumptions_or_wrong_source(self):
        files=real_source()
        if files is None:
            self.skipTest("real source not supplied")
        source,folder=files
        bad=copy.deepcopy(source)
        bad["conditional_unverified"][0]["source_kinds"]=["unknown"]
        with self.assertRaises(update.InclusionBlocked):
            update.build(bad,folder/"Item.csv",folder/"ItemSparse.csv")
        bad=copy.deepcopy(source)
        bad["season_build"]="12.1.5.fake"
        with self.assertRaises(update.InclusionBlocked):
            update.build(bad,folder/"Item.csv",folder/"ItemSparse.csv")

if __name__=="__main__":unittest.main()
