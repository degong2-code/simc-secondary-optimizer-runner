"""v168 source-first 5pc tier identity from NEW season anchors and DB2 only."""
import csv,hashlib,json,os,tempfile
from pathlib import Path
import unittest
from runner import v168_current_season_tier_discovery as tier

def anchors():
    return {
      "schema":tier.SOURCE_SCHEMA, "season":"midnight_s2",
      "policy":"SOURCE_FIRST_SAME_BUILD_MATCH_CLASS_NAME_AND_ITEMSET_NOT_OLD_PROFILE_IDS",
      "retail_build":"12.1.5.70575","expansion_id":11,
      "source_url":"https://guildloot.de/en/set/retail/",
      "native_item_set_effect_certified":False,
      "classes":{cl:"Independent "+cl for cl in tier.FAMILY}
    }

def write_csv(path,fields,records):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader();w.writerows(records)
def synthetic(folder):
    sparse=[];items=[]
    slots=[(1,"head"),(3,"shoulders"),(20,"chest"),(10,"hands"),(7,"legs")]
    for n,(cl,sub) in enumerate(sorted(tier.FAMILY.items())):
        for pos,(inv,slot) in enumerate(slots):
            iid=910000+100*n+pos
            row={"ID":iid,"Display_lang":"Independent "+cl+" "+slot,
                 "InventoryType":inv,"ExpansionID":11,"ItemSet":500+n,
                 "AllowableClass":2**n}
            sparse.append(row)
            items.append({"ID":iid,"ClassID":4,"SubclassID":sub,
                          "InventoryType":inv})
    write_csv(folder/"ItemSparse.csv",list(sparse[0]),sparse)
    write_csv(folder/"Item.csv",list(items[0]),items)
    receipt={"build":"12.1.5.70575","locale":"enUS","tables":{}}
    for name in ("ItemSparse","Item"):
        p=folder/(name+".csv")
        receipt["tables"][name]={"bytes":p.stat().st_size,
            "sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
    return receipt

class TierIdentity(unittest.TestCase):
    def test_independent_13_class_exact5_and_masks(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);receipt=synthetic(root)
            out=tier.discover(anchors(),root/"ItemSparse.csv",
                              root/"Item.csv",receipt=receipt)
        self.assertEqual(out["class_count"],13)
        self.assertEqual(out["item_count"],65)
        self.assertEqual(out["classes"]["paladin"]["allowed_class_mask"]&(out["classes"]["paladin"]["allowed_class_mask"]-1),0)
        self.assertEqual(set(out["classes"]["druid"]["pieces"]),set(tier.SLOTS))
        self.assertFalse(out["production_profile_promoted"])
        self.assertEqual(out["native_calls"],0)

    def test_source_build_digest_mismatch_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);receipt=synthetic(root)
            receipt["build"]="12.1.5.70576"
            with self.assertRaises(tier.TierBlocked):
                tier.discover(anchors(),root/"ItemSparse.csv",root/"Item.csv",receipt=receipt)
            receipt["build"]="12.1.5.70575"
            receipt["tables"]["ItemSparse"]["sha256"]="0"*64
            with self.assertRaises(tier.TierBlocked):
                tier.discover(anchors(),root/"ItemSparse.csv",root/"Item.csv",receipt=receipt)

    def test_ambiguous_external_name_does_not_guess_set(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);synthetic(root)
            a=anchors()
            a["classes"]["mage"]="Independent"  # matches 13 sets
            with self.assertRaises(tier.TierBlocked):
                tier.discover(a,root/"ItemSparse.csv",root/"Item.csv")

    def test_wrong_family_and_missing_fifth_block(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);synthetic(root)
            rows=list(csv.DictReader((root/"Item.csv").open()))
            rows[0]["SubclassID"]="4" if rows[0]["SubclassID"]!="4" else "1"
            write_csv(root/"Item.csv",list(rows[0]),rows)
            with self.assertRaises(tier.TierBlocked):
                tier.discover(anchors(),root/"ItemSparse.csv",root/"Item.csv")
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);synthetic(root)
            rows=list(csv.DictReader((root/"ItemSparse.csv").open()))
            rows.pop(0)
            write_csv(root/"ItemSparse.csv",list(rows[0]),rows)
            with self.assertRaises(tier.TierBlocked):
                tier.discover(anchors(),root/"ItemSparse.csv",root/"Item.csv")

    def test_real_v161_pinned_snapshot_when_available(self):
        path=os.environ.get("SIMC_V161_SNAPSHOT_DIR")
        if not path:self.skipTest("pinned v161 source not mounted")
        root=Path(path)
        current=json.loads((Path(__file__).resolve().parents[1]/
                            "data/current_season_tier_source_anchors.json").read_text())
        result=tier.discover(current,root/"ItemSparse.csv",root/"Item.csv",
                             receipt=json.loads((root/"receipt.json").read_text()))
        self.assertEqual((result["class_count"],result["item_count"]),(13,65))
        self.assertEqual(len({x["item_set_id"] for x in result["classes"].values()}),13)
        self.assertFalse(result["simc_tier_bonus_mechanics_verified"])

if __name__=="__main__":unittest.main()
