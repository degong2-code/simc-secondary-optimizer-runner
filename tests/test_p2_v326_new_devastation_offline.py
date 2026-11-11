"""v326 real source-first Devastation case and 120 research request guards, Native0."""
from __future__ import annotations
import os
import pathlib
import tempfile
import unittest
from unittest import mock
from integration_probes import p2_v319_new_windwalker_v290_v318_real_once as harness
from integration_probes import p2_v324_balance_new_user_variable_n_real_once as prev
from integration_probes import p2_v326_new_devastation_heldout_N_real_once as study

class V326Devastation(unittest.TestCase):
    def test_new_26_DPS_specialization_default_auto_T(self):
        case,controls=harness.new_user_case(study.CASE,study.SPEC)
        self.assertEqual((case["character_class"],case["character_spec"]),
                         ("evoker","devastation"))
        self.assertEqual(case["character_race"],"dracthyr")
        self.assertIsNone(case["final_T"])
        self.assertIsNone(controls["final_T"])
        self.assertEqual((case["target_ilevel"],case["sockets"]),(334,4))
    def test_35_native_input_exact_two_changes_for_new_N(self):
        source=("evoker=sample\nspec=devastation\n"
                "iterations=35\ngear_crit_rating=80\n"
                "flask=flask_foo\njson2=/old.json\n")
        with tempfile.TemporaryDirectory() as t:
            path=pathlib.Path(t)/"new.json"
            out=prev.update_input(source,96,path,source_iterations=35,
                                   allowed_N=study.N_GRID+(study.HOLDOUT_N,))
            self.assertEqual(out,source.replace("iterations=35","iterations=96")
                             .replace("json2=/old.json","json2="+str(path.resolve())))
            with self.assertRaises(prev.VariableNBlocked):
                prev.update_input(source,35,path,source_iterations=35,
                                   allowed_N=study.N_GRID+(study.HOLDOUT_N,))
    def test_new_campaign_only_not_replay_old_native(self):
        with mock.patch.dict(os.environ,{"P2_V326_NEW_DEVASTATION_ONCE":"0"}):
            with self.assertRaisesRegex(study.V326Blocked,
                                        "NEW_SPECIALIZATION_NATIVE_EXPLICIT"):
                study.main()
        self.assertEqual(study.TOTAL_RESEARCH_NATIVE,120)
        self.assertNotIn(("evoker","devastation"),
                         {("monk","windwalker"),("priest","shadow"),
                          ("druid","balance"),("mage","frost")})
    def test_precommitted_case_stratification_without_holdout_lookahead(self):
        def row(i,phase,vec,dps):
            return {"index":i,"phase":phase,"iterations":35 if phase=="scout" else 320,
                    "target":dict(zip(study.quality.STATS,vec)),
                    "dps_mean":dps,"case_key":"case_%05d"%i,
                    "input_sha256":"0"*64}
        a=[row(i,"scout",(i*10,1000-i*10,1000,900),1000+i) for i in range(56)]
        a+=[row(i,"precision",(j*10,1000-j*10,1000,900),3000+j)
            for i,j in zip(range(56,64),range(8))]
        b=[row(i,"scout",(i*10+1,1000-i*10-1,1000,900),2000+i)
            for i in range(56)]
        b+=[row(i,"precision",(j*10+1,1000-j*10-1,1000,900),4000+j)
            for i,j in zip(range(56,64),range(8))]
        x=study.select_pooled_candidates(a,b)
        self.assertEqual(len(x),12)
        self.assertEqual(len({tuple(v["vector"]) for v in x}),12)
        self.assertTrue(all(sum(v["vector"])==2900 for v in x))
if __name__=="__main__":unittest.main()
