"""DB2-only tier candidate discovery: 2 seasons qualify, NONE auto-selected."""
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest

from runner import v245_db2_first_tier_discovery as tierdb
from runner import v168_current_season_tier_discovery as physical
from tests.test_v168_current_season_tier_discovery import synthetic,write_csv

BUILD="12.2.0.99999"

def arrange(folder,*,two_seasons=True,omit_4pc=False,bad_mask=False):
    """Only synthetic source identity, never using any tier name seed."""
    root=Path(folder)
    receipt=synthetic(root)
    receipt["build"]=BUILD
    sparse=list(csv.DictReader((root/"ItemSparse.csv").open()))
    items=list(csv.DictReader((root/"Item.csv").open()))
    classes=sorted(physical.FAMILY)
    for row in sparse:
        idx=(number_id-500 if (number_id:=int(row["ItemSet"]))>=500 else -1)
        if 0<=idx<len(classes):
            row["AllowableClass"]=str(1<<(tierdb.CLASS_IDS[classes[idx]]-1))
    setrows=[];bonus=[];specs=[]
    for n,cl in enumerate(classes):
        classid=tierdb.CLASS_IDS[cl]
        for j in (0,1):
            specs.append({"ID":10000+10*n+j,"ClassID":classid})
        for wave in range(2 if two_seasons else 1):
            sid=500+n+100*wave
            iids=[]
            for pos,inv in enumerate((1,3,20,10,7)):
                iid=910000+100*n+pos if wave==0 else 820000+100*n+pos
                iids.append(iid)
                if wave==1:
                    sparse.append({"ID":iid,"Display_lang":"Old-looking "+cl,
                        "InventoryType":str(inv),"ExpansionID":"11",
                        "ItemSet":str(sid),"AllowableClass":str(1<<(classid-1))})
                    items.append({"ID":iid,"ClassID":"4",
                         "SubclassID":str(physical.FAMILY[cl]),
                         "InventoryType":str(inv)})
                elif bad_mask and cl=="druid" and pos==0:
                    for row in sparse:
                        if int(row["ID"])==iid:row["AllowableClass"]="0"
            setrows.append({"ID":sid,"Name_lang":"not for matching "+str(wave)+cl,
                            **{"ItemID_"+str(i):iids[i] if i<5 else 0
                               for i in range(17)}})
            for j in (0,1):
                for th in (2,4):
                    if omit_4pc and wave==0 and cl=="evoker" and th==4:
                        continue
                    bonus.append({"ID":len(bonus)+1,"ItemSetID":sid,
                         "ChrSpecID":10000+10*n+j,"Threshold":th,
                         "SpellID":100000+10*n+th+j})
    write_csv(root/"ItemSparse.csv",list(sparse[0]),sparse)
    write_csv(root/"Item.csv",list(items[0]),items)
    for name in ("ItemSparse","Item"):
        file=root/(name+".csv")
        from hashlib import sha256
        receipt["tables"][name]={"bytes":file.stat().st_size,
                                  "sha256":sha256(file.read_bytes()).hexdigest()}
    (root/"receipt.json").write_text(json.dumps(receipt),encoding="utf8")
    def csv_bytes(values):
        buf=io.StringIO()
        writer=csv.DictWriter(buf,fieldnames=list(values[0]))
        writer.writeheader();writer.writerows(values)
        return buf.getvalue().encode("utf8")
    return {"ItemSet":csv_bytes(setrows),
            "ItemSetSpell":csv_bytes(bonus),
            "ChrSpecialization":csv_bytes(specs)}

class DB2CandidateTest(unittest.TestCase):
    def test_two_complete_rosters_without_names_remain_unselected(self):
        with tempfile.TemporaryDirectory() as d:
            sources=arrange(d)
            doc=tierdb.discover(wago_folder=d,build=BUILD,
                                 expansion_id=11,source_bytes=sources)
            self.assertEqual(doc["candidate_set_count"],26)
            self.assertEqual(set(doc["candidate_counts_by_class"].values()),{2})
            self.assertIsNone(doc["current_season_selection"])
            self.assertFalse(doc["source_season_verified"])
            self.assertFalse(doc["used_prior_tier_names"])
            self.assertFalse(doc["used_prior_tier_ids"])
            self.assertFalse(doc["environment_ready"])
            self.assertTrue(all(len(x["tier_piece_ids"])==5
                                for x in doc["candidates"]))
            self.assertTrue(all(set(next(iter(x["spec_bonus_spells"]
                .values())))=={"2","4"} for x in doc["candidates"]))

    def test_not_every_set_name_or_bonus_is_a_tier(self):
        with tempfile.TemporaryDirectory() as d:
            sources=arrange(d,omit_4pc=True,bad_mask=True)
            doc=tierdb.discover(wago_folder=d,build=BUILD,
                                 expansion_id=11,source_bytes=sources)
            self.assertEqual(doc["candidate_set_count"],24)
            self.assertEqual(doc["candidate_counts_by_class"]["druid"],1)
            self.assertEqual(doc["candidate_counts_by_class"]["evoker"],1)
            self.assertIsNone(doc["current_season_selection"])

    def test_failed_second_http_records_real_attempt_count(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);wago=root/"wago";wago.mkdir()
            sources=arrange(wago)
            stage=root/"stage";stage.mkdir()
            called=[]
            class Response(io.BytesIO):
                status=200
                def __enter__(self):return self
                def __exit__(self,*args):self.close()
            def transport(request,timeout):
                table=request.full_url.split("/db2/")[1].split("/")[0]
                called.append(table)
                if len(called)==2:raise OSError("synthetic HTTP failure")
                return Response(sources[table])
            with self.assertRaisesRegex(tierdb.TierDBBlocked,
                                        "TIER_DB2_DOWNLOAD_FAILED") as ctx:
                tierdb.build_stage(stage_root=stage,wago_folder=wago,
                    build=BUILD,expansion_id=11,
                    wago_receipt_sha256="b"*64,transport=transport)
            self.assertEqual(called,list(tierdb.TABLES)[:2])
            self.assertEqual(ctx.exception.network_calls_attempted,2)

    def test_source_schema_build_and_missing_provenance_block(self):
        with tempfile.TemporaryDirectory() as d:
            sources=arrange(d)
            with self.assertRaisesRegex(tierdb.TierDBBlocked,
                                        "TIER_DB2_SOURCE_COLUMNS_MISSING"):
                tierdb.discover(wago_folder=d,build=BUILD,
                    expansion_id=11,source_bytes={
                    **sources,"ItemSetSpell":b"ID,SpellID\n1,100\n"})
            with self.assertRaisesRegex(tierdb.TierDBBlocked,
                                        "TIER_DB2_PINNED_V161_RECEIPT_REQUIRED"):
                tierdb.discover(wago_folder=d,build="12.3.0.99999",
                    expansion_id=11,source_bytes=sources)

    def test_sealed_download_once_and_second_build_zero_network(self):
        class Response(io.BytesIO):
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):self.close()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);wago=root/"wago";wago.mkdir()
            sources=arrange(wago)
            stage=root/"stage";stage.mkdir()
            calls=[]
            def transport(request,timeout):
                table=request.full_url.split("/db2/")[1].split("/")[0]
                calls.append(table)
                return Response(sources[table])
            args={"stage_root":stage,"wago_folder":wago,
                  "build":BUILD,"expansion_id":11,
                  "wago_receipt_sha256":"a"*64,"transport":transport}
            a=tierdb.build_stage(**args)
            b=tierdb.build_stage(**args)
            self.assertEqual(calls,list(tierdb.TABLES))
            self.assertEqual((a["network_calls_by_stage"],
                              b["network_calls_by_stage"]),(3,0))
            self.assertEqual(a["source_stage"]["status"],"EXECUTED_AND_SEALED")
            self.assertEqual(b["source_stage"]["status"],"REUSED_VERIFIED")
            self.assertEqual(a["candidate_set_count"],26)
            self.assertIsNone(json.loads(Path(a["candidate_path"])
                          .read_text())["current_season_selection"])
            self.assertFalse(a["used_publisher_names"])
            self.assertFalse(a["environment_installed"])
            self.assertFalse(a["source_season_verified"])

if __name__=="__main__":
    unittest.main()
