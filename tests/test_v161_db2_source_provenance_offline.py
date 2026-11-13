"""A6: existing 10-table v161 -> v217 -> v163 provenance with no network.

The real KR 70783 source receipt is a separate historical Actions observation.
This test uses explicitly synthetic CSV bytes to exercise hashes, identity,
build separation and cache tampering; it does not assert current-season data.
"""
from __future__ import annotations

import hashlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock
from urllib.parse import parse_qs,urlsplit

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v161_wago_db2_snapshot as collector
import v163_zero_seed_db2_join as join
import v217_stage_execution_engine as stages

BUILD="13.0.0.88888"

class Response(io.BytesIO):
    status=200
    def __enter__(self):return self
    def __exit__(self,*args):self.close()

class TenTableProvenance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.folder=self.root/"wago"
        self.folder.mkdir()
        self.calls=[]
        self.rows={
            table:("ID,Name\n1,"+table+"\n").encode("utf8")
            for table in collector.TABLES}

    def fetch(self,req,timeout):
        url=urlsplit(req.full_url)
        table=url.path.split("/")[-2]
        self.assertEqual(url.scheme,"https")
        self.assertEqual(url.hostname,"wago.tools")
        self.assertEqual(url.path,"/db2/"+table+"/csv")
        self.assertEqual(parse_qs(url.query),{
            "build":[BUILD],"locale":["enUS"]})
        self.assertEqual(timeout,90)
        self.assertEqual(req.get_header("Accept"),"text/csv")
        self.assertIn(table,collector.TABLES)
        self.calls.append(table)
        return Response(self.rows[table])

    def test_exact_ten_table_receipt_and_standalone_full_hash(self):
        src=collector.snapshot(self.folder,build=BUILD,fetch=self.fetch,
                               make_archive=False)
        self.assertEqual(tuple(self.calls),collector.TABLES)
        self.assertEqual(set(src["tables"]),set(join.TABLES))
        self.assertEqual(src["build"],BUILD)
        self.assertEqual(src["locale"],"enUS")
        self.assertEqual(src["status"],"ALL_CSV_DOWNLOADED_NOT_YET_INTERPRETED")
        self.assertEqual(src["simc_native_calls"],0)
        self.assertFalse(src["legacy_item_ids_imported"])
        self.assertEqual(src["total_csv_bytes"],sum(map(len,self.rows.values())))
        self.assertFalse((self.folder/"db2-snapshot.zip").exists())
        for table,meta in src["tables"].items():
            self.assertEqual(meta["bytes"],len(self.rows[table]))
            self.assertEqual(meta["sha256"],
                             hashlib.sha256(self.rows[table]).hexdigest())
            self.assertIn("build="+BUILD,meta["source_url"])
            self.assertIn("locale=enUS",meta["source_url"])
        self.assertEqual(join.verify_snapshot(self.folder,BUILD)["tables"],
                         src["tables"])

    def test_exact_build_size_sha_and_locale_mismatch_fail_closed(self):
        collector.snapshot(self.folder,build=BUILD,fetch=self.fetch,
                           make_archive=False)
        with self.assertRaisesRegex(join.JoinBlocked,"PINNED_RECEIPT_MISMATCH"):
            join.verify_snapshot(self.folder,"13.0.0.99999")
        first=collector.TABLES[0]
        path=self.folder/(first+".csv")
        original=path.read_bytes()
        path.write_bytes(original[:-1]+b"X")  # same size, different SHA
        with self.assertRaisesRegex(join.JoinBlocked,
                                    "CSV_SHA_MISMATCH_"+first):
            join.verify_snapshot(self.folder,BUILD)
        path.write_bytes(original[:-3])
        with self.assertRaisesRegex(join.JoinBlocked,
                                    "CSV_SIZE_MISMATCH_"+first):
            join.verify_snapshot(self.folder,BUILD)
        path.write_bytes(original)
        receipt=self.folder/"receipt.json"
        doc=json.loads(receipt.read_text("utf8"))
        doc["locale"]="koKR"
        receipt.write_text(json.dumps(doc),encoding="utf8")
        with self.assertRaisesRegex(join.JoinBlocked,"PINNED_RECEIPT_MISMATCH"):
            join.verify_snapshot(self.folder,BUILD)

    def test_v217_sealed_reuse_tamper_rejects_and_trusted_identity(self):
        outputs={"receipt":"wago/receipt.json"}
        outputs.update({name:"wago/"+name+".csv"
                        for name in collector.TABLES})
        inputs={"game_build":BUILD,"locale":"enUS",
                "tables":list(collector.TABLES),
                "source":"https://wago.tools/db2",
                "code_sha256":"a"*64}
        def acquire():
            return collector.snapshot(self.folder,build=BUILD,fetch=self.fetch,
                                      make_archive=False)
        def validate(_paths):
            doc=json.loads((self.folder/"receipt.json").read_text("utf8"))
            return (doc["build"]==BUILD and doc["locale"]=="enUS" and
                    set(doc["tables"])==set(collector.TABLES) and
                    doc["total_csv_bytes"]==sum(
                        row["bytes"] for row in doc["tables"].values()) and
                    all((self.folder/(t+".csv")).stat().st_size==
                        doc["tables"][t]["bytes"]
                        for t in collector.TABLES))
        first=stages.execute_stage(
            root=self.root,stage_id="fresh-wago-db2",
            stage_version="v161-normal-collector-1",inputs=inputs,
            outputs=outputs,execute=acquire,validate=validate)
        self.assertEqual(first["status"],"EXECUTED_AND_SEALED")
        self.assertEqual(first["output_count"],len(collector.TABLES)+1)
        self.assertEqual(len(self.calls),len(collector.TABLES))
        seal=json.loads((self.root/".stage_receipts/fresh-wago-db2.json")
                        .read_text("utf8"))
        source=json.loads((self.folder/"receipt.json").read_text("utf8"))
        trusted={}
        for table in collector.TABLES:
            sealed=seal["outputs"][table]
            origin=source["tables"][table]
            self.assertEqual(sealed["sha256"],origin["sha256"])
            self.assertEqual(sealed["size"],origin["bytes"])
            trusted[table]={"sha256":sealed["sha256"],
                            "bytes":sealed["size"]}
        self.assertEqual(join.verify_snapshot(
            self.folder,BUILD,verified_tables=trusted)["build"],BUILD)
        # No extra source fetch on a properly sealed second Build.
        second=stages.execute_stage(
            root=self.root,stage_id="fresh-wago-db2",
            stage_version="v161-normal-collector-1",inputs=inputs,
            outputs=outputs,execute=lambda: self.fail("REUSE_MUST_NOT_FETCH"),
            validate=validate)
        self.assertEqual(second["status"],"REUSED_VERIFIED")
        self.assertEqual(second["receipt_writes"],0)
        self.assertEqual(first["receipt_sha256"],second["receipt_sha256"])
        self.assertEqual(len(self.calls),10)
        # An unchanged-build stage must refuse a different code/build identity.
        with self.assertRaisesRegex(
                stages.StageExecutionBlocked,"STAGE_INPUT_FINGERPRINT_MISMATCH"):
            stages.execute_stage(
                root=self.root,stage_id="fresh-wago-db2",
                stage_version="v161-normal-collector-1",
                inputs={**inputs,"game_build":"13.0.0.99999"},
                outputs=outputs,execute=lambda: self.fail("MUST_NOT_FETCH"))
        # Even same-size edits are detected by v217 before the trusted
        # v163 shortcut can be legitimately used in the normal product.
        table=collector.TABLES[-1]
        path=self.folder/(table+".csv")
        data=path.read_bytes()
        path.write_bytes(data[:-1]+b"X")
        with self.assertRaisesRegex(
                stages.StageExecutionBlocked,"STAGE_OUTPUT_HASH_MISMATCH"):
            stages.verify_stage(root=self.root,stage_id="fresh-wago-db2",
                                stage_version="v161-normal-collector-1",
                                inputs=inputs,outputs=outputs)
        self.assertEqual(len(self.calls),10)

    def test_download_size_limit_does_not_create_complete_receipt(self):
        with mock.patch.object(collector,"MAX_PER",8):
            with self.assertRaisesRegex(ValueError,
                                        "CSV_DOWNLOAD_LIMIT_EXCEEDED"):
                collector.snapshot(self.folder,build=BUILD,fetch=self.fetch,
                                   make_archive=False)
        self.assertFalse((self.folder/"receipt.json").exists())

if __name__=="__main__":
    unittest.main()
