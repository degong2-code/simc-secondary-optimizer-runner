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


def make_fixture(*,omit=None,wrong_weapon=False,quality_error=False):
    src=raw_fixture()
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
    src["item_data.inc"]=raw.encode()
    return src


class SourceOnlyRepresentativeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=pathlib.Path(self.temp.name)
        self.seed_files(make_fixture())

    def seed_files(self,files):
        for filename,raw in files.items():
            (self.folder/filename).write_bytes(raw)
        receipt=seed.inventory(
            files,simc_revision=REVISION,expected_build=BUILD,
            previous_game_build=OLD,
            expected_git_blob={k:seed.git_blob(v) for k,v in files.items()})
        (self.folder/seed.RECEIPT).write_text(
            json.dumps(receipt),encoding="utf8")
        self.tier=tier_join.select(
            seed_directory=self.folder,cls="paladin",
            spec="retribution",set_option="season_token_test")

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
        self.assertFalse(row["tier_set_current_season_authenticated"])
        self.assertIsNone(row["G"])
        self.assertIsNone(row["B"])
        self.assertIsNone(row["T"])
        self.assertFalse(row["environment_ready"])
        self.assertEqual(row["native_calls"],0)
        self.assertEqual(row["cache_mutations"],0)

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
