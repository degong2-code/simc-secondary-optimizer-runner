"""P3-GT: reuse sealed v280 Item->Spell source without J admission."""
import json,pathlib,sys,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"runner"))
import v216_environment_build_coordinator as v

class SocketSourceFromExistingV280(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        (self.root/"source").mkdir()
        self.candidate=self.root/"source"/"v280_socket_source.json"
        self.build="12.1.5.70783"
        self.data={
            "schema":v.consumable_item_candidates.SCHEMA,
            "source":{"wago_snapshot_build":self.build},
            "item_use_spell_join":{
                "schema":v.item_spell_bridge.SCHEMA,
                "game_build":self.build,"source_only":True},
            "automatic_ui_promotion":False,
            "items":[
                {"item_id":275707,"name_enUS":"Miasmic Jewelbinder",
                 "expansion_id":12,
                 "item_effect_source":{
                    "status":"EXACT_DB2_ITEM_TO_ON_USE_SPELL_SOURCE_ONLY",
                    "on_use_spell_ids":[1297709]}},
                {"item_id":111111,"name_enUS":"Radiant Jewelbinder",
                 "expansion_id":12,
                 "item_effect_source":{
                    "status":"EXACT_DB2_ITEM_TO_ON_USE_SPELL_SOURCE_ONLY",
                    "on_use_spell_ids":[111000]}},
                {"item_id":275701,"name_enUS":"Other Potion",
                 "expansion_id":12,
                 "item_effect_source":{
                    "status":"EXACT_DB2_ITEM_TO_ON_USE_SPELL_SOURCE_ONLY",
                    "on_use_spell_ids":[1297709]}}]}
        self.collected={
            "expected_game_build":self.build,
            "fresh_consumable_item_spell_source":{
                "status":"ITEM_USE_SPELL_SOURCE_JOINED_UNADMITTED",
                "candidate_path":str(self.candidate),
                "source_stage":{"status":"EXECUTED_AND_SEALED",
                                "receipt_sha256":"b"*64}}}
        self.compiled={"stage_root":str(self.root)}
    def write(self):
        self.candidate.write_text(json.dumps(self.data),encoding="utf8")
    def test_existing_join_returns_both_season_candidates_without_guessing(self):
        self.write()
        out=v._existing_v280_season_socket_item_source(
            self.collected,self.compiled)
        self.assertEqual(out["candidate_count"],2)
        self.assertEqual([x["physical_item_id"] for x in
                          out["physical_candidates_unadmitted"]],
                         [111111,275707])
        self.assertTrue(out["same_build_source"])
        self.assertFalse(out["slot_application_verified"])
        self.assertFalse(out["j_budget_admitted"])
        self.assertEqual(out["new_native_calls"],0)
        self.assertEqual(out["network_calls"],0)
        self.assertEqual(out["source_sha256"],
                         v.digest(self.candidate.read_bytes()))
    def test_pending_stage_requires_no_reads(self):
        out=v._existing_v280_season_socket_item_source(
            {"expected_game_build":self.build},self.compiled)
        self.assertEqual(out["candidate_count"],0)
        self.assertFalse(out["same_build_source"])
    def test_season_drift_is_not_a_source(self):
        self.data["item_use_spell_join"]["game_build"]="12.1.5.70575"
        self.write()
        with self.assertRaisesRegex(
                v.EnvironmentBuildBlocked,
                "V216_SOCKET_V280_SAME_BUILD_ITEM_JOIN_DRIFT"):
            v._existing_v280_season_socket_item_source(
                self.collected,self.compiled)
    def test_unmatched_item_is_not_mechanism_proof(self):
        self.data["items"]=[self.data["items"][-1]]
        self.write()
        out=v._existing_v280_season_socket_item_source(
            self.collected,self.compiled)
        self.assertEqual(out["status"],
                         "NO_MATCH_IN_EXISTING_V280_CONSUMABLE_SCOPE")
        self.assertFalse(out["slot_application_verified"])
    def test_source_outside_sealed_workspace_rejected(self):
        self.write()
        other=self.root.parent/"outside-socket-source.json"
        # No extra fixture is required: a nonexistent external path is blocked.
        self.collected["fresh_consumable_item_spell_source"][
            "candidate_path"]=str(other)
        with self.assertRaisesRegex(
                v.EnvironmentBuildBlocked,
                "V216_SOCKET_V280_SEALED_CANDIDATE_REQUIRED"):
            v._existing_v280_season_socket_item_source(
                self.collected,self.compiled)
if __name__=="__main__":
    unittest.main()
