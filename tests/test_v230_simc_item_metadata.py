"""v230 raw generated SimC item metadata parsing; no historical DB or Native."""
from __future__ import annotations
import copy
import json
import pathlib
import tempfile
import unittest

from runner import v229_simc_only_source_seed as seed
from runner import v230_simc_item_metadata as item
from tests.test_v229_simc_only_source_seed import raw_sources,BUILD,REVISION,OLD


def synthetic_item_data(build=BUILD):
    rows=[]
    for iid,slot,cl,sub,primary,setid in [
        (9001,1,4,4,4,1234),(9002,3,4,4,4,1234),
        (9003,10,4,4,4,1234),(9004,7,4,4,4,1234),
        (9005,5,4,4,4,1234),(9010,17,2,8,4,0),
        (9011,9,4,4,4,0),(9012,11,4,0,0,0),
    ]:
        stats="&__item_stats_data[0]" if primary else "0"
        stat_count=1 if primary else 0
        fields=[f'"simc_item_{iid}"',str(iid),"0","0","0","335",
                "80","0","0","4",str(slot),str(cl),str(sub),
                "0","0.0","0.0","0.0",stats,str(stat_count),
                "0x2","0x0","{ 0, 0, 0 }","0","0",str(setid),
                "0","0","0"]
        assert len(fields)==28
        rows.append("  { "+", ".join(fields)+" },")
    return ("static const dbc_item_data_t::stats_t __item_stats_data[1] = {\n"
            "  { 4, 100, 0.0 },\n"
            "};\n"
            "// Items, ilevel 1-1000, wow build "+build+"\n\n"
            "static const std::array<dbc_item_data_t, 8> __item_data_chunk0 { {\n"
            +"\n".join(rows)+"\n"
            "} };\n"
            "static const std::array<util::span<const dbc_item_data_t>, 1> __item_data { {\n"
            "  __item_data_chunk0,\n"
            "} };\n").encode()


class SimCExactItemMetadataTests(unittest.TestCase):
    def test_exact_two_ids_and_generated_stat_codes(self):
        result=item.parse_exact(
            synthetic_item_data(),build=BUILD,item_ids=[9001,9010])
        self.assertEqual(result["requested_item_count"],2)
        self.assertEqual(result["full_generated_item_rows_scanned"],8)
        self.assertEqual(result["items"][0]["inventory_type"],1)
        self.assertEqual(result["items"][0]["item_set_id"],1234)
        self.assertEqual(result["items"][0]["stat_modifier_codes"],[4])
        self.assertEqual(result["items"][1]["class_id"],2)
        self.assertEqual(result["items"][1]["subclass_id"],8)
        self.assertEqual(result["G"],None)
        self.assertEqual(result["native_calls"],0)

    def test_nontier_ordinary_not_inferred_from_item_id(self):
        result=item.parse_exact(
            synthetic_item_data(),build=BUILD,item_ids=[9011,9012])
        self.assertEqual(result["items"][0]["item_set_id"],0)
        self.assertEqual(result["items"][1]["stat_modifier_codes"],[])
        self.assertFalse(result["environment_ready"])

    def test_build_wrong_stale_or_missing_id_block(self):
        with self.assertRaisesRegex(item.ItemMetadataBlocked,
                                    "GENERATED_BUILD_MISMATCH"):
            item.parse_exact(synthetic_item_data(OLD),build=BUILD,
                             item_ids=[9001])
        with self.assertRaisesRegex(item.ItemMetadataBlocked,
                                    "INCOMPLETE_OR_REQUEST_MISSING"):
            item.parse_exact(synthetic_item_data(),build=BUILD,
                             item_ids=[987654])
        with self.assertRaisesRegex(item.ItemMetadataBlocked,
                                    "EXACT_ITEM_REQUEST_IDS_INVALID"):
            item.parse_exact(synthetic_item_data(),build=BUILD,
                             item_ids=[9001,9001])

    def test_item_stat_pointer_and_chunk_count_must_be_exact(self):
        raw=synthetic_item_data().replace(
            b"&__item_stats_data[0]",b"&__item_stats_data[4]",1)
        with self.assertRaisesRegex(item.ItemMetadataBlocked,
                                    "STAT_POINTER_OUTSIDE"):
            item.parse_exact(raw,build=BUILD,item_ids=[9001])
        raw=synthetic_item_data().replace(
            b"dbc_item_data_t, 8",b"dbc_item_data_t, 7")
        with self.assertRaisesRegex(item.ItemMetadataBlocked,
                                    "CHUNK_DECLARED_COUNT_DRIFT"):
            item.parse_exact(raw,build=BUILD,item_ids=[9001])

    def test_cpp_commas_in_name_and_socket_array_not_separator(self):
        raw=synthetic_item_data().replace(
            b'simc_item_9001',b'simc_item_comma, and space')
        result=item.parse_exact(raw,build=BUILD,item_ids=[9001])
        self.assertEqual(result["items"][0]["name"],
                         "simc_item_comma, and space")
        self.assertEqual(result["items"][0]["allowed_class_mask"],2)

    def test_generated_stat_suffix_blank_and_comment_are_accepted(self):
        raw=synthetic_item_data().replace(
            b"  { 4, 100, 0.0 },",
            b"  // Source generator note\n\n  { 4, 100, 0.0f }, // multiplier")
        result=item.parse_exact(raw,build=BUILD,item_ids=[9001])
        self.assertEqual(result["items"][0]["stat_modifier_codes"],[4])

    def test_bad_generated_fields_even_unrequested_item_blocks(self):
        raw=synthetic_item_data().replace(
            b'simc_item_9012",',b'simc_item_9012", broken,',1)
        with self.assertRaisesRegex(item.ItemMetadataBlocked,
                                    "FIELD_COUNT"):
            item.parse_exact(raw,build=BUILD,item_ids=[9001])

    def test_seed_receipt_and_source_hash_required_without_old_data(self):
        src=raw_sources()
        src["item_data.inc"]=synthetic_item_data()
        original=seed.inventory(
            src,simc_revision=REVISION,expected_build=BUILD,
            previous_game_build=OLD,
            expected_git_blob={k:seed.git_blob(v) for k,v in src.items()})
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            for name,content in src.items():
                (root/name).write_bytes(content)
            (root/seed.RECEIPT).write_text(json.dumps(original))
            ok=item.from_seed(directory=root,item_ids=[9001])
            self.assertEqual(ok["simc_revision"],REVISION)
            self.assertEqual(ok["requested_item_count"],1)
            self.assertEqual(ok["source_receipt_sha256"],
                             original["receipt_sha256"])
            # Corrupt exact source even when semantically identical.
            (root/"item_data.inc").write_bytes(
                synthetic_item_data()+b"\n")
            with self.assertRaisesRegex(item.ItemMetadataBlocked,
                                        "BYTES_NOT_IN_PINNED_SEED"):
                item.from_seed(directory=root,item_ids=[9001])

    def test_item_data_not_requested_from_v229_blocks(self):
        src=raw_sources()
        r=seed.inventory(
            src,simc_revision=REVISION,expected_build=BUILD,
            previous_game_build=OLD,
            expected_git_blob={k:seed.git_blob(v) for k,v in src.items()})
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            (root/seed.RECEIPT).write_text(json.dumps(r))
            with self.assertRaisesRegex(item.ItemMetadataBlocked,
                                        "ITEM_DATA_NOT_FETCHED_OPT_IN_REQUIRED"):
                item.from_seed(directory=root,item_ids=[9001])


if __name__=="__main__":
    unittest.main()
