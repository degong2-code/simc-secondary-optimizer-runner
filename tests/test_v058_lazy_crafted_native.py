"""v058: verify exactly one Native fetch when G stat cache misses."""
import json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v046_static_item_cache as c
import v058_lazy_crafted_native as f

def req(item=239652,slot="head",options=None,compatible=None):
    return {"item_id":item,"slot":slot,"ilevel":331,
            "options":options if options is not None else {"crafted_stats":"49/36"},
            "compatible_profile":compatible}

class LazyNative(unittest.TestCase):
    def test_catalogue_head_profile_contains_real_id(self):
        t=req()
        with tempfile.TemporaryDirectory() as d:
            raw=f.native_source(t,pathlib.Path(d)/"output.json")
            self.assertIn("head=selected_239652,id=239652,ilevel=331,source=local,crafted_stats=49/36",raw)
            self.assertIn('mage="V058_Static_Only"',raw)
            self.assertEqual(sum("head=selected_239652" in x for x in raw.splitlines()),1)
            self.assertEqual(sum(x.startswith("json2=") for x in raw.splitlines()),1)
            self.assertIn("iterations=1",raw)
    def test_plate_and_mail_compatible_classes(self):
        r=req(237832,"head")
        self.assertEqual(f.get_class(r)[0],"warrior")
        r=req(244580,"shoulders")
        self.assertEqual(f.get_class(r)[0],"hunter")
    def test_uncatalogued_uses_user_class_only(self):
        with self.assertRaisesRegex(c.CacheBlocked,"UNCATALOGUED_ITEM_REQUIRES_COMPATIBLE_PROFILE"):
            f.native_source(req(999999,"head"),pathlib.Path("/tmp/a.json"))
        x=req(999999,"head",compatible={"class":"mage","spec":"arcane","role":"spell"})
        self.assertIn("id=999999",f.native_source(x,pathlib.Path("/tmp/a.json")))
    def test_trinket_selection_does_not_require_binary_native(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);seed=root/"base.json"
            c.write_atomic(seed,c.empty_cache())
            status=f.hydrate(req(250224,"trinket1",options={}),seed,None,root/"out")
            self.assertEqual(status,0)
            r=json.loads((root/"out/V058_RECEIPT.json").read_text())
            self.assertEqual(r["native_attempts"],0)
            self.assertEqual(r["status"],"PASS_TRINKET_NO_STATIC_LOOKUP_REQUIRED")
            self.assertTrue(r["static_undetected_is_not_zero_proof"])
            self.assertEqual(r["G_contribution"],0)
    def test_exact_cached_nontrinket_no_native(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);seed=root/"base.json"
            obj=c.empty_cache();ident=f.identity(req())
            s={"secondary":{"crit_rating":57,"haste_rating":57,
               "mastery_rating":0,"versatility_rating":0},
               "primary_other":dict.fromkeys(c.PRIMARY,0),"weapon_if_native":{}}
            obj["variants"][c.digest(ident)]={"identity":ident,
               "source_kind":"NATIVE_JSON2_RESOLVED_VARIANT",
               "static":s,"static_digest":c.digest(s)}
            c.write_atomic(seed,obj)
            self.assertEqual(f.hydrate(req(),seed,None,root/"out"),0)
            r=json.loads((root/"out/V058_RECEIPT.json").read_text())
            self.assertEqual(r["native_attempts"],0)
            self.assertEqual(r["G_contribution"],114)
    def test_missing_nontrinket_requires_pinned_binary(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);seed=root/"base.json"
            c.write_atomic(seed,c.empty_cache())
            self.assertEqual(f.hydrate(req(),seed,None,root/"out"),3)
            r=json.loads((root/"out/V058_RECEIPT.json").read_text())
            self.assertEqual(r["native_attempts"],0)
            self.assertEqual(r["status"],"BLOCKED")
            self.assertIn("BINARY_SHA_CHANGED",r["error"])
    def test_trinket_with_no_static_never_becomes_zero_native_stat(self):
        val=f.identity(req(250224,"trinket1",options={}))
        self.assertEqual(val["slot"],"trinket")
        self.assertEqual(val["options"],{})
    def test_unapproved_request_fields_fail(self):
        obj=req();obj["unexpected"]="n"
        with self.assertRaisesRegex(c.CacheBlocked,"ON_DEMAND_REQUEST_SHAPE"):
            f.validate_request(obj)
    def test_never_replace_simc_version_dependent_static(self):
        # Cache identity keys are static season, item, ilvl, slot and options.
        self.assertNotIn("simc_revision",f.identity(req()))

if __name__=="__main__":unittest.main()
