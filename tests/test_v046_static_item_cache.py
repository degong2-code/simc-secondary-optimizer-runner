"""v046: version-stable season static cache, fail-closed manual changes."""
import copy,json,hashlib,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v046_static_item_cache as v

def make_doc(rev="7bc10711b5",item_id=271874,stat=201,option="bonus_id=13846",
             slot="head",ilevel=334):
    tail=(","+option if option else "")
    return json.dumps({"report_version":"2.0.0","git_revision":rev,"sim":{"players":[{
      "gear":{slot:{"encoded_item":"some_item,id="+str(item_id)+",ilevel="+str(ilevel)+tail+",source=local",
      "ilevel":ilevel,"mastery_rating":stat,"intellect":189,"stamina":3910}}
    }]}}).encode()

def record(payload=None):
    return v.native_records(payload or make_doc())

class V046CacheTest(unittest.TestCase):
    def test_native_cache_identity_no_simc_version(self):
        a=record()[0];b=record(make_doc(rev="1234567890"))[0]
        self.assertEqual(a["identity"],b["identity"])
        self.assertEqual(a["static"],b["static"])
        cache=v.empty_cache()
        self.assertEqual(v.merge_native(cache,[a])["added_variants"],1)
        self.assertEqual(v.merge_native(cache,[b])["reused_variants"],1)
        self.assertEqual(len(cache["variants"]),1)
        self.assertEqual(next(iter(cache["variants"].values()))["metadata"]["native_revision"],"7bc10711b5")
    def test_different_season_separate(self):
        old=record()[0]
        cache=v.empty_cache("next_season")
        with self.assertRaisesRegex(v.CacheBlocked,"ITEM_SEASON_MISMATCH"):
            v.merge_native(cache,[old])
        self.assertEqual(cache["variants"],{})
    def test_changed_stat_requires_manual_correction(self):
        cache=v.empty_cache()
        v.merge_native(cache,record())
        before=v.canonical(cache)
        with self.assertRaisesRegex(v.CacheBlocked,"STATIC_CONFLICT_MANUAL_REVIEW_REQUIRED"):
            v.merge_native(cache,record(make_doc(stat=202,rev="9999999")))
        self.assertEqual(v.canonical(cache),before)
    def test_variant_options_keyed(self):
        cache=v.empty_cache()
        z=record(make_doc(option="bonus_id=13847"))
        v.merge_native(cache,record()+z)
        self.assertEqual(len(cache["variants"]),2)
    def test_item_name_is_not_stat_cache_key(self):
        a=record()[0]
        b=copy.deepcopy(a);b["item_name_observed"]="renamed_alias"
        self.assertEqual(v.digest(a["identity"]),v.digest(b["identity"]))
    def test_gems_enchants_crafted_do_not_overwrite_bare(self):
        a=record(make_doc(option="crafted_stats=49/36,gem_id=240967"))
        self.assertTrue(a[0]["modifiers_present"])
        self.assertFalse(a[0]["bare_item_stats_independently_attested"])
        self.assertNotEqual(a[0]["identity"],record(make_doc(option=""))[0]["identity"])
    def test_catalog_only_does_not_fabricate_stats(self):
        c=v.empty_cache()
        src={"items":[{"item_id":281235,"name_en":"Voidweaver's Leggings","slot":"LEGS_CLOTH",
                        "category":"SPECIAL_EFFECT_ARMOR"}]}
        report=v.merge_catalog(c,v.catalog_rows(json.dumps(src).encode()))
        self.assertEqual(report["stats_populated_by_catalog"],0)
        self.assertEqual(c["variants"],{})
        self.assertFalse(c["catalog"]["281235"]["stats_verified"])
    def test_same_id_different_sources_keep_provenance(self):
        c=v.empty_cache()
        j={"items":{"raid:123":{"item_id":123,"name":"Item","slot":"HEAD"},
                    "mplus:123":{"item_id":123,"name":"Item","slot":"HEAD"}}}
        res=v.merge_catalog(c,v.catalog_rows(json.dumps(j).encode()))
        self.assertEqual(res["new_ids"],1)
        self.assertEqual(len(c["catalog"]["123"]["provenance"]),2)
    def test_atomic_persistence_and_hash(self):
        c=v.empty_cache();v.merge_native(c,record())
        with tempfile.TemporaryDirectory() as t:
            path=pathlib.Path(t)/"cache.json"
            v.write_atomic(path,c)
            d=v.load(path)
            self.assertEqual(d["variants"],c["variants"])
            d["variants"][next(iter(d["variants"]))]["static"]["secondary"]["mastery_rating"]+=1
            path.write_text(json.dumps(d))
            with self.assertRaisesRegex(v.CacheBlocked,"CACHE_STATIC_TAMPER"):
                v.load(path)
    def test_manual_correction_requires_explicit_hash_and_reason(self):
        c=v.empty_cache();v.merge_native(c,record())
        e=next(iter(c["variants"].values()))
        obj={"identity":e["identity"],"new_static":copy.deepcopy(e["static"]),
             "expected_static_digest":e["static_digest"],
             "reason":"User specifically requested correction after verified source comparison.",
             "user_requested":True}
        obj["new_static"]["secondary"]["mastery_rating"]=202
        bad=copy.deepcopy(obj);bad["user_requested"]=False
        with self.assertRaisesRegex(v.CacheBlocked,"EXPLICIT_CORRECTION_REQUIRED"):
            v.request_correction(c,bad)
        r=v.request_correction(c,obj)
        self.assertEqual(r["status"],"EXPLICIT_CORRECTION_APPLIED")
        self.assertEqual(len(c["correction_history"]),1)
        with self.assertRaisesRegex(v.CacheBlocked,"CORRECTION_STALE_EXPECTED_DIGEST"):
            v.request_correction(c,obj)
    def test_selected_gear_sum_no_stat_generation(self):
        cache=v.empty_cache()
        v.merge_native(cache,record())
        key=next(iter(cache["variants"].values()))["identity"]
        d=v.selected_gear_sum(cache,[key])
        self.assertEqual(d["G_native_static_including_selected_modifiers"],201)
        self.assertEqual(d["T_v1_policy_arithmetic"],504)
        self.assertTrue(d["requires_reconciliation_if_gems_oils_present"])
    def test_unclassified_nontrinket_is_not_zero_chmv(self):
        d=json.loads(make_doc(item_id=271441,option="gem_id=240983"))
        head=d["sim"]["players"][0]["gear"]["head"]
        head.pop("mastery_rating")
        head["unknown"]=251
        with self.assertRaisesRegex(v.CacheBlocked,
                    "UNCLASSIFIED_NONTRINKET_STATIC_STATS_EXACT_VARIANT_REQUIRED:head:271441"):
            v.native_records(json.dumps(d).encode())

    def test_unclassified_trinket_still_does_not_block(self):
        d=json.loads(make_doc(item_id=281215,option="",slot="trinket1"))
        trinket=d["sim"]["players"][0]["gear"]["trinket1"]
        trinket.pop("mastery_rating")
        trinket["unknown"]=251
        rows=v.native_records(json.dumps(d).encode())
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["static"]["secondary"]["crit_rating"],0)

    def test_trinket_static_is_external(self):
        cache=v.empty_cache()
        a=record(make_doc(item_id=270164,stat=225,option="",slot="trinket1"))
        v.merge_native(cache,a)
        d=v.selected_gear_sum(cache,[a[0]["identity"]])
        self.assertEqual(d["G_native_static_including_selected_modifiers"],0)
        self.assertEqual(d["trinket_external_vector"]["mastery_rating"],225)
    def test_corrupt_native_version_refused(self):
        d=json.loads(make_doc());d["git_revision"]="not_a_sha"
        with self.assertRaisesRegex(v.CacheBlocked,"NATIVE_REVISION_MISSING"):
            v.native_records(json.dumps(d).encode())
    def test_duplicate_option_refused(self):
        with self.assertRaisesRegex(v.CacheBlocked,"DUPLICATE_OR_BAD_ITEM_OPTION"):
            v.parse_encoded("x,id=1,id=2,ilevel=334")
    def test_missing_native_is_never_zero_stat(self):
        c=v.empty_cache()
        identity={"season":v.SEASON,"item_id":1234,"ilevel":334,"slot":"head","options":{}}
        with self.assertRaisesRegex(v.CacheBlocked,"CACHE_MISS_NOT_ZERO"):
            v.selected_gear_sum(c,[identity])
    def test_v1_vs_oil_policy_no_fabrication(self):
        self.assertFalse(any("oil" in k.lower() for k in v.empty_cache()))
        self.assertEqual(v.STATS,("crit_rating","haste_rating","mastery_rating","versatility_rating"))
    def test_native_zip_path_traversal_rejected(self):
        import zipfile
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/"native.zip"
            with zipfile.ZipFile(p,"w") as z:z.writestr("../evil.json",make_doc())
            with self.assertRaisesRegex(v.CacheBlocked,"ZIP_MEMBER_INVALID"):
                v.get_native_input(p,"../evil.json")
    def test_new_build_not_recompute_cache(self):
        c=v.empty_cache()
        self.assertEqual(v.merge_native(c,record())["added_variants"],1)
        before=v.canonical(c)
        self.assertEqual(v.merge_native(c,record())["reused_variants"],1)
        self.assertEqual(v.canonical(c),before)

if __name__=="__main__":unittest.main()
