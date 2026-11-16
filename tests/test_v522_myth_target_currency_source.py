"""Offline v522 same-build CurrencyTypes / active raid target contract.

Synthetic DB2 data is NOT real 70783 Wago testimony or a new-season
ilvl approval. Native 0; source HTTP injected; original ten-table receipt
identities and existing artifact bytes remain unchanged.
"""
from __future__ import annotations
import hashlib,json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v161_wago_db2_snapshot as wago
import v522_myth_target_currency_source as target

BUILD="12.1.5.70783"
SCOPE={"source_basis":"LIVE_WCL_ACTIVE_ZONES_AND_SAME_BUILD_DB2",
       "db2_display_season_id":37,"raid_zone":"The Venomous Abyss"}
CSV=("ID,Name_lang,Description_lang\n"
     '5001,Myth Oldcrest,"Used to upgrade Myth equipment in Midnight Season 1 up to item levels 290-300. Earned from Mythic The Voidspire."\n'
     '3441,Myth Mistcrest,"Used to upgrade Myth equipment in Midnight Season 2 up to item levels 321-334. Earned from Mythic The Venomous Abyss."\n'
     '3446,Myth Mistcrest,"Used to upgrade Myth equipment in Midnight Season 2 up to item levels 321-334. When used for crafting, sets the item level to 318-331. Earned from Mythic The Venomous Abyss."\n'
     '3445,Hero Mistcrest,"Used to upgrade Hero equipment in Midnight Season 2 up to item levels 308-321. Earned from Mythic The Venomous Abyss."\n').encode()

class Response:
    status=200
    def __init__(self,data):self.data=data
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,n):data,self.data=self.data[:n],self.data[n:];return data

class Source(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=pathlib.Path(self.temp.name)
        self.receipt=self.folder/"receipt.json"
        self.receipt.write_text(json.dumps({
            "schema":"v161_wago_zero_seed_csv_snapshot_v1",
            "build":BUILD,"locale":"enUS",
            "tables":{table:{} for table in wago.TABLES}}))
        self.original=self.receipt.read_bytes()

    def get(self,data=CSV):
        calls=[]
        def fetch(req,timeout):
            calls.append(req.full_url)
            return Response(data)
        return fetch,calls

    def test_current_raid_currency_upper_limit_not_max_raid_drop_or_crafting(self):
        fetch,calls=self.get()
        receipt=target.collect(self.folder,BUILD,fetch=fetch)
        self.assertEqual(receipt["network_calls_now"],1)
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0],target.url(BUILD))
        reused=target.collect(self.folder,BUILD,
                fetch=lambda *_a,**_kw:self.fail("DUPLICATE_HTTP"))
        self.assertEqual(reused["network_calls_now"],0)
        self.assertEqual(self.receipt.read_bytes(),self.original)
        self.assertEqual(len(wago.TABLES),10)
        proof=target.myth_target_candidate(
            self.folder,BUILD,active_season_scope=SCOPE)
        self.assertEqual(proof["target_ilevel"],334)
        self.assertEqual(proof["myth_range_low"],321)
        self.assertIsNone(proof["currency_id"])
        self.assertEqual(proof["currency_ids"],[3441,3446])
        self.assertEqual(proof["candidate_count"],2)
        self.assertEqual(proof["distinct_season_myth_range_count"],1)
        self.assertTrue(proof["duplicate_myth_ranges_deduplicated"])
        self.assertFalse(proof["environment_ready"])
        self.assertFalse(proof["needs_user_target_ilevel"])

    def test_new_season_number_is_read_from_new_source_not_assumed_334(self):
        other=CSV.replace(b"Midnight Season 2",b"Other Expansion Season 4")
        other=other.replace(b"321-334",b"352-365")
        other=other.replace(b"The Venomous Abyss",b"New Raid")
        fetch,_=self.get(other)
        target.collect(self.folder,BUILD,fetch=fetch)
        proof=target.myth_target_candidate(
            self.folder,BUILD,active_season_scope={**SCOPE,
                "raid_zone":"New Raid"})
        self.assertEqual(proof["target_ilevel"],365)
        self.assertEqual(proof["season_label"],"Other Expansion Season 4")

    def test_absent_matching_active_raid_needs_user_level(self):
        target.collect(self.folder,BUILD,fetch=self.get()[0])
        proof=target.myth_target_candidate(
            self.folder,BUILD,active_season_scope={**SCOPE,
                "raid_zone":"Unrelated Raid"})
        self.assertTrue(proof["needs_user_target_ilevel"])
        self.assertIsNone(proof["target_ilevel"])

    def test_ambiguous_myth_currencies_never_choose_highest(self):
        other=CSV+(
            '3447,Myth Other,"Used to upgrade Myth equipment in Midnight Season 2 '
            'up to item levels 325-345. Mythic The Venomous Abyss."\n').encode()
        target.collect(self.folder,BUILD,fetch=self.get(other)[0])
        proof=target.myth_target_candidate(
            self.folder,BUILD,active_season_scope=SCOPE)
        self.assertEqual(proof["candidate_count"],3)
        self.assertEqual(proof["distinct_season_myth_range_count"],2)
        self.assertTrue(proof["needs_user_target_ilevel"])
        self.assertIsNone(proof["target_ilevel"])

    def test_same_bound_but_different_season_label_is_not_mistaken_for_one_season(self):
        # Even two matching raid names cannot fuse different season identities.
        other=CSV+(
            '3448,Myth Previous,"Used to upgrade Myth equipment in Midnight '
            'Season 1 up to item levels 321-334. Mythic The Venomous Abyss."\\n').encode()
        target.collect(self.folder,BUILD,fetch=self.get(other)[0])
        result=target.myth_target_candidate(
            self.folder,BUILD,active_season_scope=SCOPE)
        self.assertEqual(result["distinct_season_myth_range_count"],2)
        self.assertTrue(result["needs_user_target_ilevel"])
        self.assertIsNone(result["target_ilevel"])

    def test_build_sha_active_join_and_csv_header_fail_closed(self):
        target.collect(self.folder,BUILD,fetch=self.get()[0])
        with self.assertRaisesRegex(target.TargetSourceBlocked,
                                    "TARGET_ORIGINAL_V161_BUILD_OR_TABLES_MISMATCH"):
            target.myth_target_candidate(
                self.folder,"13.0.0.99999",active_season_scope=SCOPE)
        for scope in ({**SCOPE,"source_basis":"USER_SUPPLIED"},
                      {**SCOPE,"db2_display_season_id":0}):
            with self.assertRaisesRegex(target.TargetSourceBlocked,
                                        "TARGET_ACTIVE_SEASON_RAID_JOIN_REQUIRED"):
                target.myth_target_candidate(
                    self.folder,BUILD,active_season_scope=scope)
        csv_path=self.folder/target.FILE
        csv_path.write_bytes(csv_path.read_bytes().replace(b"321-334",b"321-344"))
        with self.assertRaisesRegex(target.TargetSourceBlocked,
                                    "TARGET_CURRENCY_SOURCE_SHA_OR_BUILD_MISMATCH"):
            target.myth_target_candidate(
                self.folder,BUILD,active_season_scope=SCOPE)

    def test_bad_csv_and_partial_download_do_not_create_authority(self):
        # An HTTP 200 HTML/error body cannot poison the immutable
        # optional season cache; the same build may retry a valid CSV.
        for bad,code in ((b"<!DOCTYPE html>",
                          "TARGET_CURRENCY_DOWNLOAD_COLUMNS_INVALID"),
                         (b"\\xff\\xfeinvalid",
                          "TARGET_CURRENCY_DOWNLOAD_COLUMNS_INVALID")):
            with self.subTest(bad=bad),self.assertRaisesRegex(
                    target.TargetSourceBlocked,code):
                target.collect(self.folder,BUILD,fetch=self.get(bad)[0])
            self.assertFalse((self.folder/target.FILE).exists())
            self.assertFalse((self.folder/target.RECEIPT).exists())
        target.collect(self.folder,BUILD,fetch=self.get()[0])
        self.assertEqual(target.myth_target_candidate(
            self.folder,BUILD,active_season_scope=SCOPE)["target_ilevel"],334)
        # Existing valid, sealed source is immutable and SHA-enforced.
        with self.assertRaisesRegex(target.TargetSourceBlocked,
                                    "TARGET_CURRENCY_SOURCE_SHA_OR_BUILD_MISMATCH"):
            (self.folder/target.FILE).write_bytes(b"tampered")
            target.collect(self.folder,BUILD,fetch=self.get()[0])

if __name__=="__main__":
    unittest.main()
