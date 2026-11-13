"""A7: normal v216 Build seals public source reconciliation automatically.

Two executions, one synthetic source acquisition; second must use both
v254 and v405 v217 sealed cache, without HTTP/Native or selecting IDs by AI.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v216_environment_build_coordinator as build


class Body(io.BytesIO):
    status=200
    def __enter__(self):return self
    def __exit__(self,*args):self.close()

def write(path,fields,rows):
    with path.open("w",encoding="utf8",newline="") as stream:
        w=csv.DictWriter(stream,fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

def origin(kind,season,wse):
    return {
        "source":kind,
        "season_evidence":("DB2_DISPLAY_SEASON_MATCH" if season==83
                           else "UNKNOWN_UNSCOPED_JOURNAL" if season==0
                           else "UNKNOWN_OTHER_DISPLAY_SEASON"),
        "display_season_id":season,
        "world_state_expression_id":wse,
        "journal_encounter_id":221,"journal_instance_id":222,
        **({"challenge_mode_id":223} if kind=="mplus_journal" else {})}

class A7NormalBuildSourceConsumer(unittest.TestCase):
    def test_first_stage_seals_and_second_reuses_without_extra_fetch(self):
        game_build="13.0.0.88888"
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            wago=root/"raw";wago.mkdir()
            stage_root=root/"stages";stage_root.mkdir()
            current=[
                {"item_id":110,"name":"Active trinket","slot":12,
                 "acquisition_sources":[origin("raid_journal",0,881)]},
                {"item_id":111,"name":"Physical wrist","slot":9,
                 "acquisition_sources":[origin("mplus_journal",83,991)]},
                {"item_id":112,"name":"Previous-season trinket","slot":12,
                 "acquisition_sources":[origin("mplus_journal",82,0)]},
            ]
            v163={
                "schema":"v163_zero_seed_db2_join_v1",
                "source_provider":"WAGO_TOOLS_PINNED_DB2_WCL_LIVE",
                "build":game_build,"old_item_catalog_imported":False,
                "full_season_completeness_confirmed":False,
                "db2_expansion_id":27,"db2_display_season_id":83,
                "items":current}
            candidate=root/"v163_join.json"
            candidate.write_text(json.dumps(v163),encoding="utf8")
            write(wago/"ItemSparse.csv",[
                "ID","Display_lang","InventoryType","ExpansionID",
                "ItemSet","OverallQualityID","AllowableClass",
                "StatModifier_bonusStat_0"],[
                {"ID":x["item_id"],"Display_lang":x["name"],
                 "InventoryType":x["slot"],"ExpansionID":27,
                 "ItemSet":0,"OverallQualityID":4,"AllowableClass":-1,
                 "StatModifier_bonusStat_0":5} for x in current])
            write(wago/"Item.csv",[
                "ID","ClassID","SubclassID","InventoryType"],[
                {"ID":x["item_id"],"ClassID":4,"SubclassID":1,
                 "InventoryType":x["slot"]} for x in current])
            effect=b"ItemID,ItemEffectID\n110,8765\n"
            calls=[]
            def transport(req,timeout):
                calls.append(req.full_url)
                self.assertIn("build="+game_build,req.full_url)
                return Body(effect)
            linked={
                "candidate_path":str(candidate),
                "stage":{"receipt_sha256":"a"*64}}
            first=build._fresh_ordinary_gear_source_stage(
                stage_root=stage_root,wago_folder=wago,
                build=game_build,linked=linked,transport=transport)
            self.assertEqual(len(calls),1)
            self.assertEqual(first["network_calls_by_stage"],1)
            self.assertEqual(first["status"],
                             "FRESH_GEAR_PLAIN_CANDIDATES_SOURCE_ONLY")
            proof=first["a7_auto_source_choice_provenance"]
            self.assertTrue(proof["candidate_provenance_verified"],first)
            self.assertFalse(proof["final_user_e2e_verified"])
            self.assertEqual(proof["additional_network_calls"],0)
            self.assertEqual(proof["native_calls"],0)
            self.assertEqual(proof["source_stage"]["status"],
                             "EXECUTED_AND_SEALED")
            body=json.loads(pathlib.Path(proof["receipt_path"]).read_text())
            self.assertEqual(body["public_candidate_count"],1)
            self.assertEqual(body["public_role_counts"]["trinket"],1)
            self.assertFalse(body["item_eligibility_requires_wse"])
            self.assertEqual(body["game_build"],game_build)
            self.assertEqual(body["original_v163_sha256"],
                             hashlib.sha256(candidate.read_bytes()).hexdigest())
            # The adapter's public options are source-derived; the previous
            # season item is never promoted and ordinary gear is internal.
            try:
                import v167_product_season_gear_adapter as adapter
                doc=json.loads(pathlib.Path(first["candidate_path"]).read_text())
                opts=adapter.public_options(doc)["choices"]
                self.assertEqual([x["item_id"] for x in opts["trinket"]],[110])
            except Exception:
                raise
            def no_fetch(req,timeout):
                self.fail("SEALED_REPEAT_MUST_NOT_FETCH")
            second=build._fresh_ordinary_gear_source_stage(
                stage_root=stage_root,wago_folder=wago,
                build=game_build,linked=linked,transport=no_fetch)
            self.assertEqual(second["network_calls_by_stage"],0)
            self.assertEqual(second["source_stage"]["status"],"REUSED_VERIFIED")
            reuse=second["a7_auto_source_choice_provenance"]
            self.assertTrue(reuse["candidate_provenance_verified"])
            self.assertEqual(reuse["source_stage"]["status"],"REUSED_VERIFIED")
            self.assertEqual(reuse["source_stage"]["receipt_sha256"],
                             proof["source_stage"]["receipt_sha256"])
            self.assertEqual(len(calls),1)

if __name__=="__main__":
    unittest.main()
