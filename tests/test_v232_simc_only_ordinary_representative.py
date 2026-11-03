"""v232 SimC-only 13-slot provisional representative; no existing season DB."""
from __future__ import annotations

import copy
import json
import pathlib
import tempfile
import unittest

from runner import v229_simc_only_source_seed as seed
from runner import v230_simc_item_metadata as item_parser
from runner import v231_simc_tier_item_join as tier_join
from runner import v232_simc_only_ordinary_representative as builder
from tests.test_v229_simc_only_source_seed import BUILD,OLD,REVISION
from tests.test_v231_simc_tier_item_join import raw_fixture


def item_row(iid,inv,cls,sub,primary=4,quality=4,base=335,mask="0x2"):
    count=1 if primary else 0
    ptr="&__item_stats_data[0]" if primary else "0"
    fields=[f'"rep_{iid}"',str(iid),"0","0","0",str(base),
            "80","0","0",str(quality),str(inv),str(cls),str(sub),
            "0","0.0","0.0","0.0",ptr,str(count),
            mask,"0x0","{ 0, 0, 0 }","0","0","0","0","0","0"]
    assert len(fields)==28
    return "  { "+", ".join(fields)+" },\n"


def make_fixture(*,omit=None,wrong_weapon=False,quality_error=False,
                 warrior=False):
    src=raw_fixture(set_class=1 if warrior else 2)
    extra=[
        item_row(9020,5,4,4),  # source-only plain chest
        item_row(9021,6,4,4),  # belt
        item_row(9022,8,4,4),  # boots
        item_row(9023,2,4,0,primary=0), # necklace
        item_row(9024,16,4,0,primary=0),# cloak
        item_row(9025,11,4,0,primary=0),# second ring
        item_row(9026,5,4,2),  # wrong leather, must not select
        item_row(9027,8,4,4,quality=2), # wrong quality
        item_row(9028,9,4,4,base=700),# remote base ilevel
        item_row(9029,8,4,4,mask="0x4"), # wrong class
    ]
    if warrior:
        extra.append(item_row(9031,17,2,8))  # Titan's Grip second 2H
    if omit is not None:
        extra=[r for r in extra if f"rep_{omit}" not in r]
    raw=src["item_data.inc"].decode("utf8")
    if wrong_weapon:
        raw=raw.replace('"simc_item_9010", 9010,', '"simc_item_9010", 9010,')
        raw=raw.replace('"simc_item_9010", 9010, 0, 0, 0, 335, 80, 0, 0, 4, 17, 2, 8, 0, 0.0, 0.0, 0.0, &__item_stats_data[0], 1, 0x2',
                        '"simc_item_9010", 9010, 0, 0, 0, 335, 80, 0, 0, 4, 17, 2, 18, 0, 0.0, 0.0, 0.0, &__item_stats_data[0], 1, 0x2')
    if quality_error:
        raw=raw.replace('"simc_item_9001", 9001, 0, 0, 0, 335, 80, 0, 0, 4,',
                        '"simc_item_9001", 9001, 0, 0, 0, 335, 80, 0, 0, 3,')
    raw=raw.replace("dbc_item_data_t, 8>",f"dbc_item_data_t, {8+len(extra)}>")
    raw=raw.replace("} };\nstatic const std::array<util::span",
                    "".join(extra)+"} };\nstatic const std::array<util::span")
    if warrior:
        # Warrior class bit 0 (paladin class bit 1) for all selected gear.
        raw=raw.replace("0x2", "0x1")
    src["item_data.inc"]=raw.encode()
    return src


class SourceOnlyRepresentativeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=pathlib.Path(self.temp.name)
        self.seed_files(make_fixture())

    def seed_files(self,files,cls="paladin",spec="retribution"):
        for filename,raw in files.items():
            (self.folder/filename).write_bytes(raw)
        receipt=seed.inventory(
            files,simc_revision=REVISION,expected_build=BUILD,
            previous_game_build=OLD,
            expected_git_blob={k:seed.git_blob(v) for k,v in files.items()})
        (self.folder/seed.RECEIPT).write_text(
            json.dumps(receipt),encoding="utf8")
        self.tier=tier_join.select(
            seed_directory=self.folder,cls=cls,
            spec=spec,set_option="season_token_test")

    def plan(self,target=335):
        return builder.find_candidate(
            seed_directory=self.folder,tier_candidate=self.tier,
            target_ilevel=target)

    def test_one_spec_exact_physical_source_13_slots(self):
        row=self.plan()
        ids=row["selected_G_slot_ids"]
        self.assertEqual(len(ids),13)
        self.assertEqual(ids["chest"],9020)
        self.assertEqual(ids["wrists"],9011)
        self.assertEqual(ids["waist"],9021)
        self.assertEqual(ids["feet"],9022)
        self.assertEqual(ids["neck"],9023)
        self.assertEqual(ids["back"],9024)
        self.assertEqual({ids["finger1"],ids["finger2"]},{9012,9025})
        self.assertEqual(ids["main_hand"],9010)
        self.assertEqual(ids["head"],9001)
        self.assertEqual(ids["shoulders"],9002)
        self.assertEqual(ids["hands"],9003)
        self.assertEqual(ids["legs"],9004)
        self.assertEqual(row["character"]["weapon_form"],"single_two_hand")
        self.assertTrue(row["item_effects_absence_not_proven"])
        self.assertFalse(row["generic_G_physical_conditions_verified"])
        self.assertFalse(row["generic_G_current_season_membership_required"])
        self.assertFalse(row["tier_set_current_season_authenticated"])
        self.assertIsNone(row["G"])
        self.assertIsNone(row["B"])
        self.assertIsNone(row["T"])
        self.assertFalse(row["environment_ready"])
        self.assertEqual(row["native_calls"],0)
        self.assertEqual(row["cache_mutations"],0)

    def test_warrior_fury_titans_grip_requires_two_real_distinct_2h_items(self):
        self.seed_files(make_fixture(warrior=True),
                        cls="warrior",spec="fury")
        result=self.plan()
        self.assertEqual(result["character"]["weapon_form"],"dual_two_hand")
        self.assertEqual(len(result["selected_G_slot_ids"]),14)
        self.assertEqual(
            {result["selected_G_slot_ids"]["main_hand"],
             result["selected_G_slot_ids"]["off_hand"]},
            {9010,9031})
        self.assertIsNone(result["G"])
        self.assertFalse(result["environment_ready"])

    def test_opt_in_wago_db2_season_candidates_override_unscaled_level_heuristic(self):
        from runner import v167_product_season_gear_adapter as provider
        from runner import v233_source_only_G_probe_profile as compiler
        allowed={
            9020:(5,4,4), 9028:(9,4,4), 9021:(6,4,4),
            9022:(8,4,4), 9023:(2,4,0),9024:(16,4,0),
            9012:(11,4,0),9025:(11,4,0),9010:(17,2,8)}
        rows=[{
            "item_id":iid,"name":f"season_{iid}",
            "category":"plain_representative_candidate",
            "inventory_type":inv,"class_id":kind,"subclass_id":sub,
            "allowed_class_mask":2,
            "source_kinds":["raid_journal"],"item_set_id":0}
            for iid,(inv,kind,sub) in sorted(allowed.items())]
        season={
            "schema":provider.SCHEMA,
            "status":"CURRENT_SEASON_CANDIDATE_SELECTION_ONLY",
            "no_old_catalog_seed":True,
            "season_build":BUILD,
            "item_count":len(rows),
            "role_counts":{"plain_representative_candidate":len(rows)},
            "items":rows,
            "not_certified":{"tier_four_set":True,"simc_item_effects":True},
            "new_native_calls":0,"new_api_calls":0}
        baseline=self.plan()
        self.assertEqual(baseline["selected_G_slot_ids"]["wrists"],9011)
        preferred=builder.find_candidate(
            seed_directory=self.folder,tier_candidate=self.tier,
            target_ilevel=335,season_gear_db=season)
        self.assertEqual(preferred["selected_G_slot_ids"]["wrists"],9028)
        self.assertEqual(preferred["selected_G_slot_ids"]["main_hand"],9010)
        self.assertEqual(preferred["season_candidate_provider"],
                         "EXPLICIT_SAME_BUILD_WAGO_DB2_V167_CANDIDATES")
        self.assertEqual(preferred["selected_gear_season_source_kinds"]["wrists"],
                         ["raid_journal"])
        self.assertIsNone(preferred["G"])
        self.assertTrue(preferred["generic_G_physical_conditions_verified"])
        self.assertTrue(preferred["generic_G_plain_item_effect_relation_checked"])
        self.assertFalse(preferred["generic_G_current_season_membership_required"])
        self.assertFalse(preferred["environment_ready"])
        self.assertTrue(preferred["same_season_membership_not_proven"])
        text,receipt=compiler.build(
            source_directory=self.folder,tier_candidate=self.tier,
            representative_candidate=preferred,race="human",
            level=90,season_gear_db=season)
        self.assertIn("wrists=simc_source_9028,id=9028",text)
        self.assertEqual(receipt["native_calls"],0)
        self.assertTrue(receipt["generic_G_physical_conditions_verified"])
        self.assertFalse(receipt["generic_G_current_season_membership_required"])
        with self.assertRaisesRegex(compiler.ProbeBlocked,
                                    "REPLAY_DRIFT"):
            compiler.build(
                source_directory=self.folder,tier_candidate=self.tier,
                representative_candidate=preferred,race="human",level=90)
        wrong=dict(season,season_build="12.0.0.11111")
        with self.assertRaisesRegex(
                builder.SourceRepresentativeBlocked,
                "BUILD_OR_PROVENANCE_MISMATCH"):
            builder.find_candidate(
                seed_directory=self.folder,tier_candidate=self.tier,
                target_ilevel=335,season_gear_db=wrong)

    def test_selected_sources_prefer_explicit_db2_season_and_keep_unknowns_pending(self):
        from runner import v167_product_season_gear_adapter as provider
        eligible = {
            9020:(5,4,4),9021:(6,4,4),9022:(8,4,4),
            9023:(2,4,0),9024:(16,4,0),9012:(11,4,0),
            9025:(11,4,0),9010:(17,2,8),
            9011:(9,4,4),9028:(9,4,4)}
        rows=[]
        for iid,(inv,cls,sub) in sorted(eligible.items()):
            if iid==9028:
                evidence=[{"source":"mplus_journal",
                    "season_evidence":"DB2_DISPLAY_SEASON_MATCH",
                    "display_season_id":37,
                    "world_state_expression_id":0,
                    "journal_encounter_id":14,"journal_instance_id":2}]
            elif iid==9011:
                evidence=[{"source":"localbots_delve_pool"}]
            elif iid==9022:
                evidence=[{"source":"mplus_journal",
                    "season_evidence":"UNKNOWN_WORLD_STATE_EXPRESSION",
                    "display_season_id":37,
                    "world_state_expression_id":55,
                    "journal_encounter_id":14,"journal_instance_id":2}]
            else:
                evidence=[{"source":"raid_journal",
                    "season_evidence":"UNKNOWN_UNSCOPED_JOURNAL",
                    "display_season_id":0,
                    "world_state_expression_id":0,
                    "journal_encounter_id":7,"journal_instance_id":1}]
            rows.append({"item_id":iid,"name":f"season_{iid}",
                "category":"plain_representative_candidate",
                "inventory_type":inv,"class_id":cls,"subclass_id":sub,
                "allowed_class_mask":2,"item_set_id":0,
                "source_kinds":[evidence[0]["source"]],
                "source_evidence":evidence})
        season={"schema":provider.SCHEMA,
            "status":"CURRENT_SEASON_CANDIDATE_SELECTION_ONLY",
            "no_old_catalog_seed":True,"season_build":BUILD,
            "db2_display_season_id":37,
            "item_count":len(rows),
            "role_counts":{"plain_representative_candidate":len(rows)},
            "items":rows,
            "not_certified":{"tier_four_set":True,"simc_item_effects":True},
            "new_native_calls":0,"new_api_calls":0}
        picked=builder.find_candidate(
            seed_directory=self.folder,tier_candidate=self.tier,
            target_ilevel=334,season_gear_db=season)
        self.assertEqual(picked["selected_G_slot_ids"]["wrists"],9028)
        self.assertEqual(picked["selected_non_tier_explicit_db2_match_count"],1)
        self.assertEqual(picked["selected_ordinary_source_provenance"][
            "wrists"]["status"],
            "DB2_DISPLAY_SEASON_EXPLICIT_WSE_ZERO_CANDIDATE")
        self.assertIn("feet",picked[
            "selected_non_tier_season_condition_pending_slots"])
        self.assertEqual(picked["selected_ordinary_source_provenance"][
            "feet"]["status"],"WORLD_STATE_EXPRESSION_PENDING")
        self.assertEqual(picked["selected_ordinary_source_provenance"][
            "chest"]["status"],"RAID_JOURNAL_SEASON_UNSCOPED_OR_UNKNOWN")
        self.assertFalse(picked["selected_ordinary_source_provenance"][
            "wrists"]["season_membership_authenticated"])
        self.assertTrue(picked["tier_active_season_membership_not_authenticated"])
        self.assertTrue(picked["selected_G_source_candidate_not_approved"])
        # Unscoped raid, Localbots and WSE!=0 do not invalidate the
        # ordinary physical G budget if the category/primary is correct.
        self.assertTrue(picked["generic_G_physical_conditions_verified"])
        self.assertFalse(picked["generic_G_current_season_membership_required"])
        self.assertIsNone(picked["G"])
        self.assertFalse(picked["environment_ready"])

    def test_conditional_mplus_worldstate_physical_fallback_no_G(self):
        from runner import v167_product_season_gear_adapter as provider
        from runner import v233_source_only_G_probe_profile as compiler
        eligible={
            9020:(5,4,4),9021:(6,4,4),9011:(9,4,4),
            9023:(2,4,0),9024:(16,4,0),
            9012:(11,4,0),9025:(11,4,0),
            9010:(17,2,8)}
        rows=[{"item_id":iid,"name":f"season_{iid}",
               "category":"plain_representative_candidate",
               "inventory_type":inv,"class_id":cls,"subclass_id":sub,
               "allowed_class_mask":2,"source_kinds":["raid_journal"],
               "item_set_id":0}
              for iid,(inv,cls,sub) in sorted(eligible.items())]
        conditional={"item_id":9022,"name":"pending_foot",
               "category":"plain_representative_candidate",
               "inventory_type":8,"class_id":4,"subclass_id":4,
               "allowed_class_mask":2,"item_set_id":0,
               "provisional_mplus_world_state_only":True,
               "season_membership_verified":False,"ui_selectable":False,
               "source_kinds":["mplus_journal"],
               "source_evidence":[{
                   "source":"mplus_journal",
                   "season_evidence":"UNKNOWN_WORLD_STATE_EXPRESSION",
                   "display_season_id":37,"world_state_expression_id":441,
                   "journal_encounter_id":30,"journal_instance_id":20}]}
        db={"schema":provider.SCHEMA,
            "status":"CURRENT_SEASON_CANDIDATE_SELECTION_ONLY",
            "no_old_catalog_seed":True,"season_build":BUILD,
            "db2_display_season_id":37,"item_count":len(rows),
            "role_counts":{"plain_representative_candidate":len(rows)},
            "items":rows,
            "internal_conditional_mplus_plain_candidates":[conditional],
            "internal_conditional_mplus_plain_count":1,
            "not_certified":{"tier_four_set":True,"simc_item_effects":True},
            "new_native_calls":0,"new_api_calls":0}
        picked=builder.find_candidate(
            seed_directory=self.folder,tier_candidate=self.tier,
            target_ilevel=334,season_gear_db=db)
        self.assertEqual(picked["selected_G_slot_ids"]["feet"],9022)
        self.assertIn("feet",picked[
            "selected_non_tier_season_condition_pending_slots"])
        detail=picked["selected_ordinary_source_provenance"]["feet"]
        self.assertEqual(detail["world_state_expression_ids"],[441])
        self.assertTrue(detail["same_display_season_worldstate_pending"])
        self.assertFalse(detail["G_source_approved"])
        self.assertTrue(picked["generic_G_physical_conditions_verified"])
        self.assertIsNone(picked["G"])
        self.assertFalse(picked["environment_ready"])
        text,receipt=compiler.build(
            source_directory=self.folder,tier_candidate=self.tier,
            representative_candidate=picked,race="human",
            level=90,season_gear_db=db)
        self.assertIn("feet=simc_source_9022,id=9022",text)
        self.assertEqual(receipt["native_calls"],0)

    def test_selected_plain_armor_wrong_primary_blocks_g_not_season(self):
        # Same slot, class, quality and base ilvl are insufficient when a
        # plate chest has NO valid main-stat row for this specialization.
        files=make_fixture()
        raw=files["item_data.inc"]
        before=b'"rep_9020", 9020, 0, 0, 0, 335, 80, 0, 0, 4, 5, 4, 4, 0, 0.0, 0.0, 0.0, &__item_stats_data[0], 1, 0x2'
        after=b'"rep_9020", 9020, 0, 0, 0, 335, 80, 0, 0, 4, 5, 4, 4, 0, 0.0, 0.0, 0.0, 0, 0, 0x2'
        self.assertIn(before,raw)
        files["item_data.inc"]=raw.replace(before,after,1)
        self.seed_files(files)
        with self.assertRaisesRegex(builder.SourceRepresentativeBlocked,
                                    "ORDINARY_PRIMARY_STAT_NOT_COMPATIBLE:chest"):
            self.plan()

    def test_different_target_ilevel_does_not_infer_scaling(self):
        first=self.plan(target=335)
        next=self.plan(target=336)
        self.assertEqual(first["selected_G_slot_ids"],next[
            "selected_G_slot_ids"])
        self.assertNotEqual(first["receipt_sha256"],next["receipt_sha256"])
        self.assertIsNone(next["G"])
        self.assertTrue(next["source_item_level_window"][
            "not_an_ilevel_scaling_rule"])

    def test_single_full_pass_reuses_v230_source_reader(self):
        data=(self.folder/"item_data.inc").read_bytes()
        result=item_parser.parse_exact(
            data,build=BUILD,
            candidate_filter=lambda fields:fields[1] in ("9001","9020"),
            candidate_limit=3)
        self.assertEqual({r["item_id"] for r in result["items"]},
                         {9001,9020})
        self.assertEqual(result["selection_mode"],"SOURCE_CANDIDATE_UNAPPROVED")
        with self.assertRaisesRegex(item_parser.ItemMetadataBlocked,
                                    "SOURCE_CANDIDATE_LIMIT_REACHED"):
            item_parser.parse_exact(
                data,build=BUILD,
                candidate_filter=lambda fields:fields[1] in ("9001","9020"),
                candidate_limit=1)

    def test_missing_required_ordinary_fails_not_filled_from_old_db(self):
        self.seed_files(make_fixture(omit=9021))
        with self.assertRaisesRegex(
                builder.SourceRepresentativeBlocked,
                "ORDINARY_SLOT_WITHOUT_SIMC_CANDIDATE:waist"):
            self.plan()

    def test_wrong_weapon_primary_or_subclass_blocks(self):
        self.seed_files(make_fixture(wrong_weapon=True))
        with self.assertRaisesRegex(
                builder.SourceRepresentativeBlocked,
                "WEAPON_FORM_SOURCE_CANDIDATE_MISSING"):
            self.plan()

    def test_mismatched_tier_ilevel_or_quality_fail_closed(self):
        edited=copy.deepcopy(self.tier)
        edited["tier_unscaled_ilevel_by_slot"]["head"]=444
        edited["receipt_sha256"]=seed.digest(seed.canonical(
            {k:v for k,v in edited.items() if k!="receipt_sha256"}
            ).encode())
        with self.assertRaisesRegex(
                builder.SourceRepresentativeBlocked,
                "TIER_PHYSICAL_SOURCE_ROW_CHANGED"):
            builder.find_candidate(seed_directory=self.folder,
                tier_candidate=edited,target_ilevel=335)
        self.seed_files(make_fixture(quality_error=True))
        with self.assertRaisesRegex(
                builder.SourceRepresentativeBlocked,
                "TIER_LEVEL_OR_QUALITY_NOT_SOURCE_BOUND"):
            self.plan()

    def test_corrupted_raw_simc_bytes_rejected_not_cache_fallback(self):
        file=self.folder/"item_data.inc"
        file.write_bytes(file.read_bytes()+b"\n")
        with self.assertRaisesRegex(
                builder.SourceRepresentativeBlocked,
                "ITEM_DATA_SOURCE_BYTES_DRIFT"):
            self.plan()

    def test_no_trinkets_special_gear_or_legacy_storage(self):
        row=self.plan()
        self.assertTrue(set(row["selected_G_slot_ids"]).isdisjoint(
            {"trinket1","trinket2"}))
        self.assertFalse((self.folder/"data").exists())
        self.assertFalse((self.folder/"integration_probes").exists())
        self.assertEqual(row,self.plan())

    def test_target_validity_and_receipt_tamper(self):
        with self.assertRaisesRegex(
                builder.SourceRepresentativeBlocked,
                "TARGET_LEVEL_OR_SEARCH_WINDOW_INVALID"):
            self.plan(target=0)
        invalid=copy.deepcopy(self.tier)
        invalid["set_id"]=555555
        with self.assertRaisesRegex(
                builder.SourceRepresentativeBlocked,
                "UNPROMOTED_V231_SOURCE_TIER_REQUIRED"):
            builder.find_candidate(seed_directory=self.folder,
                tier_candidate=invalid,target_ilevel=335)

    def test_cli_writes_one_source_candidate_without_native(self):
        tier_file=self.folder/"tier_candidate.json"
        tier_file.write_text(json.dumps(self.tier),encoding="utf8")
        out=self.folder/"one_spec.json"
        self.assertEqual(builder.main([
            "--seed-dir",str(self.folder),"--tier-candidate",str(tier_file),
            "--target-ilevel","335","--out",str(out)]),0)
        record=json.loads(out.read_text(encoding="utf8"))
        self.assertEqual(record["native_calls"],0)
        self.assertEqual(record["selected_G_slot_ids"],self.plan()[
            "selected_G_slot_ids"])


if __name__=="__main__":
    unittest.main()
