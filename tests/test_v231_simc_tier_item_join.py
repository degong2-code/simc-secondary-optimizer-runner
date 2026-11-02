"""v231 source-only SimC set candidate + exact item metadata, one DPS spec."""
from __future__ import annotations
import json
import pathlib
import tempfile
import unittest

from runner import v229_simc_only_source_seed as seed
from runner import v231_simc_tier_item_join as join
from tests.test_v229_simc_only_source_seed import (
    raw_sources,BUILD,OLD,REVISION)
from tests.test_v230_simc_item_metadata import synthetic_item_data


def raw_fixture(*, set_class=2, wrong_mask=False, wrong_slot=False,
                old_set=False, missing_bonus=False):
    files=raw_sources()
    text=files["item_set_bonus.inc"].decode()
    text=text.replace(
        '"SYN1", 3, 1234, 2, 1, 71',
        f'"SYN1", 3, 1234, 2, {set_class}, 71')
    text=text.replace(
        '"SYN1", 3, 1234, 4, 1, 72',
        f'"SYN1", 3, 1234, 4, {set_class}, 72')
    if missing_bonus:
        text=text.replace('"SYN1", 3, 1234, 4', '"SYN1", 3, 1234, 2')
    files["item_set_bonus.inc"]=text.encode()
    data=synthetic_item_data()
    if wrong_mask:
        data=data.replace(b"0x2",b"0x4",1)
    if wrong_slot:
        data=data.replace(b'simc_item_9003", 9003, 0, 0, 0, 335, 80, 0, 0, 4, 10',
                          b'simc_item_9003", 9003, 0, 0, 0, 335, 80, 0, 0, 4, 5')
    files["item_data.inc"]=data
    return files


class TierJoinTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=pathlib.Path(self.temp.name)
        self.set_files(raw_fixture())

    def set_files(self,files):
        self.files=files
        for name,payload in files.items():
            (self.root/name).write_bytes(payload)
        receipt=seed.inventory(
            files,simc_revision=REVISION,expected_build=BUILD,
            previous_game_build=OLD,
            expected_git_blob={k:seed.git_blob(v) for k,v in files.items()})
        (self.root/seed.RECEIPT).write_text(
            json.dumps(receipt,sort_keys=True),encoding="utf8")
        self.receipt=receipt

    def plan(self,cls="paladin",spec="retribution",token="season_token_test"):
        return join.select(seed_directory=self.root,
                           cls=cls,spec=spec,set_option=token)

    def test_five_piece_paladin_source_only_exact_slots(self):
        result=self.plan()
        self.assertEqual(result["class"],"paladin")
        self.assertEqual(result["class_mask"],2)
        self.assertEqual(result["set_id"],1234)
        self.assertEqual(result["tier_piece_ids"],{
            "head":9001,"shoulders":9002,"chest":9005,
            "hands":9003,"legs":9004})
        self.assertEqual(result["four_piece_slots"],
                         ["head","shoulders","hands","legs"])
        self.assertEqual(result["tier_bonus_sizes"],[2,4])
        self.assertEqual(result["game_build"],BUILD)
        self.assertEqual(result["native_calls"],0)
        self.assertIsNone(result["G"])
        self.assertIsNone(result["B"])
        self.assertIsNone(result["T"])
        self.assertFalse(result["environment_ready"])
        self.assertEqual(result["season_set_option_source_authentication"],
                         "NOT_PROVED_BY_SIMC_TABLE_ALONE")
        self.assertEqual(result["receipt_sha256"],seed.digest(
            seed.canonical({k:v for k,v in result.items()
                            if k!="receipt_sha256"}).encode()))

    def test_set_is_not_guessed_from_ilevel_or_high_id(self):
        with self.assertRaisesRegex(join.TierCandidateBlocked,
                                    "SET_OPTION_MISSING_OR_AMBIGUOUS"):
            self.plan(token="not_known_season")
        with self.assertRaisesRegex(join.TierCandidateBlocked,
                                    "NOT_AN_EXACT_5PC_2PC_4PC_SET"):
            self.plan(token="separate_option")

    def test_wrong_physical_slot_and_class_mask_blocked(self):
        self.set_files(raw_fixture(wrong_slot=True))
        with self.assertRaisesRegex(join.TierCandidateBlocked,
                                    "TIER_PHYSICAL_ARMOR_CLASS_SLOT_OR_SET"):
            self.plan()
        self.set_files(raw_fixture(wrong_mask=True))
        with self.assertRaisesRegex(join.TierCandidateBlocked,
                                    "TIER_PHYSICAL_ARMOR_CLASS_SLOT_OR_SET"):
            self.plan()

    def test_non_dps_or_wrong_class_set_rejected(self):
        with self.assertRaisesRegex(join.TierCandidateBlocked,
                                    "26_DPS_SPEC_REQUIRED"):
            self.plan(spec="holy")
        self.set_files(raw_fixture(set_class=1))
        with self.assertRaisesRegex(join.TierCandidateBlocked,
                                    "SET_OPTION_MISSING_OR_AMBIGUOUS"):
            self.plan()

    def test_missing_4pc_bonus_cannot_complete_tier(self):
        self.set_files(raw_fixture(missing_bonus=True))
        with self.assertRaisesRegex(join.TierCandidateBlocked,
                                    "NOT_AN_EXACT_5PC_2PC_4PC_SET"):
            self.plan()

    def test_mutated_set_source_fails_before_tier_selection(self):
        p=self.root/"item_set_bonus.inc"
        p.write_bytes(p.read_bytes()+b"\n")
        with self.assertRaisesRegex(join.TierCandidateBlocked,
                                    "SET_BYTES_NOT_MATCH_PINNED"):
            self.plan()

    def test_candidate_selection_is_deterministic_and_no_old_sources(self):
        self.assertEqual(self.plan(),self.plan())
        self.assertFalse((self.root/"data").exists())
        self.assertFalse((self.root/"integration_probes").exists())


if __name__=="__main__":
    unittest.main()
