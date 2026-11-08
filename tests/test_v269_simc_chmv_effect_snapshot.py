import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runner"))
import v269_simc_chmv_effect_snapshot as v

PROFILE = '''paladin="sample"
spec=retribution
head=sample,id=12345,ilevel=334
main_hand=sword,id=23456,ilevel=334
actions.precombat=flask
actions.precombat+=/food
actions.precombat+=/snapshot_stats
actions=auto_attack
flask=old_flask
food=old_food
'''

def report(options, crit=2500, haste=1300, mastery=1100, vers=700, rev="a"*10):
    return json.dumps({"git_revision": rev, "sim": {"players": [{
        "name": "sample", "flask": options.get("flask", "disabled"),
        "food": options.get("food", "disabled"),
        "temporary_enchant": options.get("temporary_enchant", "disabled"),
        "collected_data": {"buffed_stats": {"stats": {
            "crit_rating": crit, "haste_rating": haste,
            "mastery_rating": mastery, "versatility_rating": vers
        }}}
    }]}}).encode()

class NativeSnapshotTests(unittest.TestCase):
    def test_same_profile_before_after_flask_rating_and_metadata(self):
        prep=v.prepare(profile=PROFILE, kind="flask",token="flask_of_the_magisters_2")
        for key in v.CONSUMABLES:
            self.assertEqual(prep["baseline_profile"].count(key+"="),1)
        self.assertIn("food=disabled",prep["active_profile"])
        self.assertIn("flask=flask_of_the_magisters_2",prep["active_profile"])
        result=v.compare(
            baseline_json2=report({}),
            active_json2=report({"flask":"flask_of_the_magisters_2"},crit=2608),
            prepared=prep,binary_sha256="c"*64,simc_revision="a"*40)
        self.assertEqual(result["static_CHMV_candidate"],{
            "crit_rating":108,"haste_rating":0,"mastery_rating":0,"versatility_rating":0})
        self.assertEqual(result["status"],"OBSERVED_INTEGER_STATIC_CHMV_SNAPSHOT_DELTA")
        self.assertIsNone(result["F"])
        self.assertFalse(result["environment_ready"])

    def test_food_and_oil_are_measured_not_double_accounted(self):
        food=v.prepare(profile=PROFILE,kind="food",token="silvermoon_parade")
        out=v.compare(baseline_json2=report({}),active_json2=report(
            {"food":"silvermoon_parade"},haste=1400),
            prepared=food,binary_sha256="b"*64,simc_revision="a"*40)
        self.assertEqual(out["static_CHMV_candidate"]["haste_rating"],100)
        self.assertTrue(out["budget_ownership_not_assigned_here"])
        oil=v.prepare(profile=PROFILE,kind="temporary_enchant",
                      token="main_hand:thalassian_phoenix_oil_2")
        actual=v.compare(baseline_json2=report({}),active_json2=report(
            {"temporary_enchant":"main_hand:thalassian_phoenix_oil_2"},
            crit=2516,haste=1316),prepared=oil,binary_sha256="b"*64,
            simc_revision="a"*40)
        self.assertEqual(actual["static_CHMV_candidate"]["crit_rating"],16)
        self.assertIsNone(actual["O"])

    def test_empty_or_misordered_snapshot_cannot_certify_zero(self):
        with self.assertRaisesRegex(v.SnapshotBlocked,"MUST_PRECEDE"):
            v.prepare(profile=PROFILE.replace(
                "actions.precombat=flask\nactions.precombat+=/food\nactions.precombat+=/snapshot_stats",
                "actions.precombat=food\nactions.precombat+=/snapshot_stats\nactions.precombat+=/flask"),
                kind="flask",token="new_flask")
        p=v.prepare(profile=PROFILE,kind="flask",token="new_flask")
        with self.assertRaisesRegex(v.SnapshotBlocked,"OPTION_DRIFT"):
            v.compare(baseline_json2=report({}),active_json2=report({}),
                      prepared=p,binary_sha256="b"*64,simc_revision="a"*40)
        with self.assertRaisesRegex(v.SnapshotBlocked,"REVISION_DRIFT"):
            v.compare(baseline_json2=report({},rev="9"*10),
                      active_json2=report({"flask":"new_flask"}),
                      prepared=p,binary_sha256="b"*64,simc_revision="a"*40)
        observed=v.compare(
            baseline_json2=report({},crit=0,haste=0,mastery=0,vers=0),
            active_json2=report({"flask":"new_flask"},
                                crit=0,haste=165,mastery=0,vers=0),
            prepared=p,binary_sha256="b"*64,simc_revision="a"*40)
        self.assertEqual(observed["static_CHMV_candidate"],{
            "crit_rating":0,"haste_rating":165,
            "mastery_rating":0,"versatility_rating":0})
        missing=json.loads(report({}))
        missing["sim"]["players"][0]["collected_data"]["buffed_stats"]["stats"]={}
        with self.assertRaisesRegex(v.SnapshotBlocked,"SNAPSHOT_EMPTY"):
            v.compare(baseline_json2=json.dumps(missing).encode("utf8"),
                      active_json2=report({"flask":"new_flask"}),
                      prepared=p,binary_sha256="b"*64,simc_revision="a"*40)

    def test_noninteger_negative_or_zero_delta_not_declared_fixed(self):
        p=v.prepare(profile=PROFILE,kind="flask",token="new_flask")
        for ct in [2500, 2500.75, 2498]:
            with self.subTest(ct=ct):
                out=v.compare(baseline_json2=report({}),
                              active_json2=report({"flask":"new_flask"},crit=ct),
                              prepared=p,binary_sha256="b"*64,simc_revision="a"*40)
                self.assertIsNone(out["static_CHMV_candidate"])
                self.assertEqual(out["status"],
                    "NO_CLEAN_STATIC_CHMV_DELTA_CONDITIONAL_EFFECT_PENDING")

    def test_oil_gear_override_is_not_suitable_for_measurement(self):
        with self.assertRaisesRegex(v.SnapshotBlocked,"OIL_BASELINE"):
            v.prepare(profile=PROFILE+"gear_crit_rating=100\n",
                      kind="temporary_enchant",token="main_hand:abc")
        with self.assertRaisesRegex(v.SnapshotBlocked,"OFF_HAND_ITEM_REQUIRED"):
            v.prepare(profile=PROFILE,kind="temporary_enchant",
                      token="main_hand:abc/off_hand:abc")


    def test_p3_he_one_ordinary_gem_simc_numeric_owner_and_no_auto_admit(self):
        profile=("paladin=sample\n"
                 "head=sample,id=12345,ilevel=334,source=local\n"
                 "chest=sample2,id=23456,ilevel=334,source=local\n")
        prep=v.prepare_ordinary_gem(
            profile=profile,slot="head",ordinary_gem_id=240906)
        self.assertEqual(prep["active_profile"].replace(
            ",gem_id=240906","",1),profile)
        def gem_report(which,crit=100,haste=200,mastery=300,vers=400):
            first="sample,id=12345,ilevel=334,source=local"
            if which=="active":
                first="sample,id=12345,ilevel=334,gem_id=240906,source=local"
            return json.dumps({"git_revision":"a"*10,"sim":{"players":[{
                "name":"sample",
                "gear":{
                    "head":{"encoded_item":first},
                    "chest":{"encoded_item":
                        "sample2,id=23456,ilevel=334,source=local"}},
                "collected_data":{"buffed_stats":{"stats":{
                    "crit_rating":crit,"haste_rating":haste,
                    "mastery_rating":mastery,"versatility_rating":vers
                }}}}]}}).encode()
        baseline=gem_report("baseline")
        active=gem_report("active",crit=116,haste=207)
        result=v.compare_ordinary_gem(
            prepared=prep,baseline_json2=baseline,active_json2=active,
            binary_sha256="c"*64,simc_revision="a"*40)
        self.assertEqual(result["status"],
                         "SIMC_ORDINARY_GEM_TWO_STAT_OBSERVED_UNADMITTED")
        self.assertEqual(result["simc_effective_two_stat_rating_unadmitted"],23)
        self.assertEqual(result["simc_effective_two_stat_vector_unadmitted"],{
            "crit_rating":16,"haste_rating":7,
            "mastery_rating":0,"versatility_rating":0})
        self.assertIsNone(result["official_J"])
        self.assertFalse(result["same_effect_highest_quality_verified_here"])
        with self.assertRaisesRegex(v.SnapshotBlocked,"GEAR_ITEM_DRIFT"):
            v.compare_ordinary_gem(
                prepared=prep,baseline_json2=baseline,
                active_json2=gem_report("baseline",crit=116,haste=207),
                binary_sha256="c"*64,simc_revision="a"*40)
        with self.assertRaisesRegex(v.SnapshotBlocked,"UNCONFOUNDED"):
            v.prepare_ordinary_gem(
                profile=profile+"gear_crit_rating=100\n",
                slot="head",ordinary_gem_id=240906)
        with self.assertRaisesRegex(v.SnapshotBlocked,"UNCONFOUNDED"):
            v.prepare_ordinary_gem(
                profile=profile+"profileset.variant=copy\n",
                slot="head",ordinary_gem_id=240906)
        wrong=v.compare_ordinary_gem(
            prepared=prep,baseline_json2=baseline,
            active_json2=gem_report("active",crit=116),
            binary_sha256="c"*64,simc_revision="a"*40)
        self.assertEqual(wrong["status"],
                         "SIMC_ORDINARY_GEM_EFFECTIVE_RATING_PENDING")
        self.assertIsNone(wrong["simc_effective_two_stat_rating_unadmitted"])

if __name__ == "__main__": unittest.main()
