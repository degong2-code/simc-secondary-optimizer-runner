"""P3-BV: no-network exact gem enchant source join and one-stage cache."""
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runner import v266_gem_enchant_raw_stat_source as source
from runner import v268_gem_enchant_existing_source_stage as adapter


BUILD="12.1.5.70575"


def joined(*,game_build=BUILD):
    rows=[
        (2001,11,501),(2002,12,502),
        (2003,13,503),(2004,14,504)]
    return {
        "schema":source.GEM_SOURCE_SCHEMA,
        "status":source.GEM_SOURCE_STATUS,
        "game_build":game_build,
        "simc_generated_gem_source_build":game_build,
        "simc_revision":"b"*40,
        "v213_manifest_sha256":"c"*64,
        "exact_link_count":len(rows),
        "joins":[{"item_id":itemid,"gem_property_id":property_id,
                  "enchant_id":enchant_id,
                  "color_mask":(1 if itemid==2003 else 2),
                  "minimum_ilevel":(345 if itemid==2003 else 300),
                  "expansion_id":12,
                  "socket_eligibility":"NOT_YET_VERIFIED",
                  "status":"EXACT_DB2_ITEMSPARSE_GEM_PROPERTY_RELATION",
                  "ui_selectable":False}
                 for itemid,property_id,enchant_id in rows],
    }


def enchant_csv():
    header=list(source.COLUMNS)
    buf=io.StringIO()
    writer=csv.DictWriter(buf,fieldnames=header,lineterminator="\n")
    writer.writeheader()
    def row(iid,kind,arg,points,scaling=0):
        v={column:"0" for column in header}
        v.update(ID=str(iid),Effect_0=str(kind),
                 EffectArg_0=str(arg),EffectPointsMin_0=str(points),
                 EffectScalingPoints_0=str(scaling))
        writer.writerow(v)
    row(501,5,32,25,0)  # static crit raw points only
    row(502,5,36,40,1.5)  # stat but scaled, must remain pending
    row(503,3,123,0,0)   # spell effect not a plain stat
    # 504 deliberately missing: absence is not proof of zero stat.
    row(9000,5,40,999,0) # irrelevant other enchant ignored
    return buf.getvalue().encode("utf8")


class GemEnchantmentSourceReuseTests(unittest.TestCase):
    def test_raw_static_points_are_not_approved_J_or_highest_quality(self):
        result=source.preview(
            gem_join=joined(),raw_enchant_csv=enchant_csv(),
            expected_game_build=BUILD)
        self.assertEqual(result["raw_static_candidate_count"],1)
        self.assertEqual(result["unresolved_count"],3)
        self.assertIsNone(result["J"])
        self.assertFalse(result["highest_quality_selection_verified"])
        self.assertFalse(result["environment_ready"])
        self.assertEqual(result["native_calls"],0)
        by_id={r["item_id"]:r for r in result["records"]}
        self.assertEqual(by_id[2001]["raw_static_points_candidate"],{
            "crit_rating":25,"haste_rating":0,"mastery_rating":0,
            "versatility_rating":0})
        self.assertEqual(by_id[2002]["effect_classification"],
            "NONSTATIC_SCALED_OR_NON_CHMV_EFFECT_PENDING")
        self.assertEqual(by_id[2003]["effect_classification"],
            "NONSTATIC_SCALED_OR_NON_CHMV_EFFECT_PENDING")
        self.assertEqual(by_id[2004]["effect_classification"],
            "ENCHANT_ID_MISSING_FROM_SAME_BUILD_CSV")
        self.assertTrue(all(not row["ui_selectable"]
                            and not row["J_rating_verified"]
                            for row in result["records"]))

    def test_same_build_source_and_scaling_schema_must_be_explicit(self):
        with self.assertRaisesRegex(source.EnchantSourceBlocked,
                                    "EXACT_SAME_BUILD"):
            source.preview(gem_join=joined(game_build="12.1.5.70574"),
                           raw_enchant_csv=enchant_csv(),
                           expected_game_build=BUILD)
        data=enchant_csv().replace(b"EffectScalingPoints_0",
                                  b"UnknownScaling_0",1)
        with self.assertRaisesRegex(source.EnchantSourceBlocked,
                                    "STATIC_COLUMNS_MISSING"):
            source.preview(gem_join=joined(),raw_enchant_csv=data,
                           expected_game_build=BUILD)

    def test_selected_gem_change_reuses_verified_full_join_once(self):
        """One CSV parse per unchanged source, not per user gem selection."""
        raw=enchant_csv()
        class FakeResponse:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,size=-1):return raw
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            adapter.collect(stage_root=root,build=BUILD,
                transport=lambda request,timeout:FakeResponse())
            source_path=root/"v221.json"
            source_path.write_text(json.dumps(joined()),encoding="utf8")
            original=adapter.join.preview
            with patch.object(adapter.join,"preview",wraps=original) as parse:
                first=adapter.view(stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2001],
                    selected_source_gem_item_ids=[2001,2002])
                second=adapter.view(stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2002,2003],
                    selected_source_gem_item_ids=[2002,2003])
                self.assertEqual(parse.call_count,1)
                receipts=list((root/".stage_receipts").glob(
                    "fresh-v266-gem-enchant-join-*.json"))
                self.assertEqual(len(receipts),1)
                self.assertEqual(json.loads(receipts[0].read_text("utf8"))[
                    "status"],"COMPLETE")
                self.assertEqual(first[
                    "selected_gem_raw_points_by_id_unadmitted"],{"2001":25})
                self.assertEqual(second[
                    "selected_gem_unresolved_item_ids"],[2002,2003])
                self.assertTrue(second[
                    "selected_gem_v221_same_build_items_all_present"])
                # Mandatory special gem is projected from the SAME cached
                # join; its nonstatic effect is NOT a proved zero J.
                unknown_special=adapter.view(
                    stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2001],
                    selected_source_gem_item_ids=[2001,2003],
                    selected_special_gem_item_id=2003)
                self.assertEqual(parse.call_count,1)
                unknown=unknown_special[
                    "selected_special_gem_raw_effect_unadmitted"]
                self.assertEqual(unknown["item_id"],2003)
                self.assertIsNone(unknown[
                    "raw_static_CHMV_total_candidate_unadmitted"])
                self.assertTrue(unknown[
                    "missing_or_nonstatic_never_assumed_zero"])
                observed_special=adapter.view(
                    stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2003],
                    selected_source_gem_item_ids=[2001,2003],
                    selected_special_gem_item_id=2001)
                self.assertEqual(parse.call_count,1)
                static=observed_special[
                    "selected_special_gem_raw_effect_unadmitted"]
                self.assertEqual(static[
                    "raw_static_CHMV_total_candidate_unadmitted"],25)
                self.assertEqual(static[
                    "raw_static_CHMV_vector_candidate_unadmitted"][
                    "crit_rating"],25)
                self.assertFalse(static["J_budget_attribution_verified"])
                with self.assertRaisesRegex(ValueError,
                        "V268_SPECIAL_GEM_MUST_BE_SOURCE_BOUND_AND_DISTINCT"):
                    adapter.view(
                        stage_root=root,v221_candidate_path=source_path,
                        build=BUILD,selected_gem_item_ids=[2001],
                        selected_source_gem_item_ids=[2001,2003],
                        selected_special_gem_item_id=2001)
                self.assertFalse(second["environment_ready"])
                self.assertFalse(second["highest_quality_J_verified"])
                # A new v221 artifact identity MUST miss the old cache.
                modified=joined()
                modified["source_annotation"]="changed_original_bytes"
                source_path.write_text(json.dumps(modified),encoding="utf8")
                third=adapter.view(stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2001])
                self.assertEqual(parse.call_count,2)
                self.assertEqual(len(list((root/".stage_receipts").glob(
                    "fresh-v266-gem-enchant-join-*.json"))),2)
                # The original exact bytes should hit their previous receipt.
                source_path.write_text(json.dumps(joined()),encoding="utf8")
                fourth=adapter.view(stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2001])
                self.assertEqual(parse.call_count,2)
                self.assertEqual(len(list((root/".stage_receipts").glob(
                    "fresh-v266-gem-enchant-join-*.json"))),2)
                # Even a known-good cache cannot hide a modified CSV.
                csvpath=root/adapter.OUTPUTS["csv"]
                csvpath.write_bytes(raw+b"\n")
                drift=adapter.view(stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2001])
                self.assertEqual(drift["status"],"GEM_ENCHANT_LOCAL_JOIN_PENDING")
                self.assertEqual(drift["reason"],"V268_SEALED_CSV_BYTES_CHANGED")
                self.assertEqual(parse.call_count,2)
                # A tampered cached join is rejected by the existing v217
                # output hash, never used as a fresh product J or UI choice.
                csvpath.write_bytes(raw)
                joined_outputs=list((root/"fresh_source").glob(
                    "v266_exact_gem_enchant_join_*.json"))
                self.assertEqual(len(joined_outputs),2)
                for original_json in joined_outputs:
                    original_json.write_text("{}\n",encoding="utf8")
                invalid=adapter.view(
                    stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2001])
                self.assertEqual(invalid["status"],"GEM_ENCHANT_LOCAL_JOIN_PENDING")
                self.assertIn("STAGE_OUTPUT_HASH_MISMATCH",invalid["reason"])

    def test_single_fetch_replays_local_and_rejects_changed_csv(self):
        raw=enchant_csv()
        calls=[]
        class FakeResponse:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,size=-1):return raw
        def fetch(request,timeout):
            calls.append((request.full_url,timeout))
            return FakeResponse()
        def fail(request,timeout):
            raise AssertionError("a cached CSV must never refetch")
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            first=adapter.collect(stage_root=root,build=BUILD,
                                  transport=fetch)
            second=adapter.collect(stage_root=root,build=BUILD,
                                   transport=fail)
            self.assertEqual((first["network_calls_by_stage"],
                              second["network_calls_by_stage"]),(1,0))
            self.assertEqual(len(calls),1)
            self.assertIn("SpellItemEnchantment",calls[0][0])
            self.assertEqual(second["status"],"GEM_ENCHANT_CSV_SOURCE_SEALED")
            p=root/"v221.json"
            p.write_text(json.dumps(joined()),encoding="utf8")
            status=adapter.view(stage_root=root,v221_candidate_path=p,
                                build=BUILD,
                                selected_gem_item_ids=[2001,2001,2002,2004])
            self.assertEqual(status["selected_gem_raw_points_by_id_unadmitted"],
                             {"2001":25})
            self.assertEqual(
                status["selected_gem_raw_CHMV_vectors_by_id_unadmitted"],
                {"2001":{"crit_rating":25,"haste_rating":0,
                         "mastery_rating":0,"versatility_rating":0}})
            self.assertEqual(status["selected_gem_unresolved_item_ids"],
                             [2002,2004])
            self.assertFalse(status["selected_gem_all_raw_points_known"])
            self.assertTrue(status["selected_gem_raw_points_not_native_verified"])
            only=adapter.view(stage_root=root,v221_candidate_path=p,
                              build=BUILD,selected_gem_item_ids=[2001]*6)
            self.assertTrue(only["selected_gem_all_raw_points_known"])
            self.assertEqual(only["selected_gem_raw_points_by_id_unadmitted"],
                             {"2001":25})
            source_bound=adapter.view(
                stage_root=root,v221_candidate_path=p,build=BUILD,
                selected_gem_item_ids=[2001]*2,
                selected_source_gem_item_ids=[2001,2003])
            self.assertEqual(source_bound[
                "selected_gem_v221_item_ids_unadmitted"],[2001,2003])
            self.assertTrue(source_bound[
                "selected_gem_v221_same_build_items_all_present"])
            self.assertTrue(source_bound["selected_gem_v221_source_only"])
            self.assertTrue(source_bound[
                "selected_gem_v221_source_properties_complete"])
            props=source_bound["selected_gem_v221_source_properties_unadmitted"]
            self.assertEqual([p["item_id"] for p in props],[2001,2003])
            self.assertEqual(props[1]["minimum_ilevel"],345)
            self.assertEqual(props[1]["color_mask"],1)
            self.assertEqual(props[1]["gem_property_id"],13)
            self.assertEqual(len(props),2)
            # 2003 has non-static effects: source ID exists but its
            # SimC effect, specialness and rating remain unverified.
            self.assertEqual(source_bound[
                "selected_gem_raw_points_by_id_unadmitted"],{"2001":25})
            missing=adapter.view(
                stage_root=root,v221_candidate_path=p,build=BUILD,
                selected_source_gem_item_ids=[2001,999999])
            self.assertFalse(missing[
                "selected_gem_v221_same_build_items_all_present"])
            self.assertEqual(missing["selected_gem_v221_missing_item_ids"],
                             [999999])
            self.assertFalse(missing[
                "selected_gem_v221_source_properties_complete"])
            self.assertEqual(len(missing[
                "selected_gem_v221_source_properties_unadmitted"]),1)
            self.assertIsNone(only["J"])
            self.assertEqual(status["raw_static_candidate_count"],1)
            self.assertEqual(status["unresolved_enchant_count"],3)
            self.assertIsNone(status["J"])
            self.assertFalse(status["highest_quality_J_verified"])
            self.assertEqual(status["network_calls"],0)
            csvpath=root/adapter.OUTPUTS["csv"]
            csvpath.write_bytes(raw+b"\n")
            drift=adapter.view(stage_root=root,v221_candidate_path=p,
                               build=BUILD)
            self.assertEqual(drift["status"],"GEM_ENCHANT_LOCAL_JOIN_PENDING")
            self.assertEqual(drift["reason"],"V268_SEALED_CSV_BYTES_CHANGED")


if __name__=="__main__":
    unittest.main()
