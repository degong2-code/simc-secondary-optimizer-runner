"""Source SHA is checked at acquisition; downstream reuse needs no rehash.

These tests use the real v217 stage and v163 snapshot contract, with tiny
synthetic CSVs. They do not establish any season, item or CHMV eligibility.
"""
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v163_zero_seed_db2_join as season
import v217_stage_execution_engine as stages


class VerifiedWagoSourceSealTests(unittest.TestCase):
    def test_upstream_stage_checks_bytes_and_downstream_reuses_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            snapshot=root/"wago"
            snapshot.mkdir()
            build="12.1.5.70575"
            records={name:("ID\\n1\\n").encode("utf8")
                     for name in season.TABLES}
            table_info={name:{"sha256":hashlib.sha256(raw).hexdigest(),
                              "bytes":len(raw)}
                        for name,raw in records.items()}
            source_receipt={"build":build,"locale":"enUS",
                            "tables":table_info}
            outputs={"receipt":"wago/receipt.json"}
            outputs.update({name:"wago/"+name+".csv" for name in season.TABLES})
            def execute():
                for name,raw in records.items():
                    (snapshot/(name+".csv")).write_bytes(raw)
                (snapshot/"receipt.json").write_text(
                    json.dumps(source_receipt),encoding="utf8")
            args=dict(root=root,stage_id="synthetic-wago",
                      stage_version="1",inputs={"build":build},
                      outputs=outputs)
            staged=stages.execute_stage(**args,execute=execute)
            self.assertEqual(staged["status"],"EXECUTED_AND_SEALED")
            sealed=json.loads((root/".stage_receipts"/
                               "synthetic-wago.json").read_text("utf8"))
            verified={name:{"sha256":sealed["outputs"][name]["sha256"],
                            "bytes":sealed["outputs"][name]["size"]}
                      for name in season.TABLES}
            # The second stage call already hashes the source and confirms
            # that the cached receipt still corresponds to physical bytes.
            self.assertEqual(stages.verify_stage(**args)["status"],
                             "REUSED_VERIFIED")
            with mock.patch.object(season.hashlib,"sha256",
                                   side_effect=AssertionError("duplicate SHA")):
                receipt=season.verify_snapshot(
                    snapshot,build,verified_tables=verified)
            self.assertEqual(receipt["tables"],table_info)
            wrong=json.loads(json.dumps(verified))
            wrong["Item"]["sha256"]="f"*64
            with self.assertRaisesRegex(season.JoinBlocked,
                                         "V217_VERIFIED_TABLE_PROVENANCE"):
                season.verify_snapshot(snapshot,build,verified_tables=wrong)
            # Identical file length is NOT a cache hit after tampering:
            # v217 rejects the changed bytes before passing any seal along.
            (snapshot/"Item.csv").write_bytes(b"ID\\n2\\n")
            with self.assertRaisesRegex(stages.StageExecutionBlocked,
                                         "STAGE_OUTPUT_HASH_MISMATCH"):
                stages.verify_stage(**args)


if __name__=="__main__":
    unittest.main()
