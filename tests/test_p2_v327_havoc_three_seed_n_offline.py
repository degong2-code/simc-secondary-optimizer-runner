"""v327 source-first new Havoc user, original v326 compatibility, Native0."""
from __future__ import annotations
import os,unittest
from unittest import mock
from integration_probes import p2_v319_new_windwalker_v290_v318_real_once as h
from integration_probes import p2_v327_havoc_new_user_three_seed_n_real_once as study

class HavocOffline(unittest.TestCase):
    def test_new_supported_dps_profile_auto_T(self):
        case,ctl=h.new_user_case(study.CASE,study.SPEC)
        self.assertEqual((case["character_class"],case["character_spec"]),
                         ("demonhunter","havoc"))
        self.assertEqual(case["character_race"],"night_elf")
        self.assertIsNone(case["final_T"])
        self.assertIsNone(ctl["final_T"])
        self.assertEqual(case["target_ilevel"],334)
    def test_research_bounded_and_different_new_specialization(self):
        self.assertEqual(study.SCREEN_N,(32,48,64,96))
        self.assertEqual(study.TOTAL_RESEARCH_NATIVE,168)
        self.assertEqual(study.TOTAL_RESEARCH_ITERATIONS,24000)
        self.assertEqual(study.SCREEN_REPS,(0,1,2))
        self.assertNotIn(study.SPEC,{
            ("monk","windwalker"),("priest","shadow"),
            ("druid","balance"),("evoker","devastation")})
    def test_predeclared_current_journal_candidate_pool(self):
        keys=study.quality.STATS
        def make(offset):
            scout=[{"index":i,"phase":"scout","iterations":35,
                    "target":dict(zip(keys,(100+offset+i*5,1000-offset-i*5,1000,900))),
                    "dps_mean":5000.+i,"case_key":f"case_{i:05d}",
                    "input_sha256":"1"*64} for i in range(56)]
            confirm=[dict(scout[i],index=56+i,phase="precision",
                          iterations=320,dps_mean=6000.+i,
                          case_key=f"case_{56+i:05d}") for i in range(8)]
            return scout+confirm
        pool=study.select_fresh_pool(make(0),make(1))
        self.assertEqual(len(pool),12)
        self.assertEqual(len({x["vector"] for x in pool}),12)
        self.assertTrue(all(x["row"]["phase"]=="scout" for x in pool))
        self.assertEqual({sum(x["vector"]) for x in pool},{3000})
    def test_actual_57_7_and_58_6_source_journals_allowed(self):
        keys=study.quality.STATS
        def make(confirmed,offset):
            scouts=64-confirmed
            rows=[{"index":i,"phase":"scout","iterations":35,
                   "target":dict(zip(keys,(100+offset+i*5,1000-offset-i*5,1000,900))),
                   "dps_mean":1000.+i,"case_key":f"case_{i:05d}",
                   "source":"NEW_NATIVE","input_sha256":"1"*64}
                  for i in range(scouts)]
            rows += [dict(rows[j],index=scouts+j,phase="precision",
                          iterations=320,dps_mean=2000.+j,
                          case_key=f"case_{scouts+j:05d}") for j in range(confirmed)]
            return rows
        chosen=study.select_fresh_pool(make(7,0),make(6,1))
        self.assertEqual(len(chosen),12)
        self.assertEqual({sum(x["vector"]) for x in chosen},{3000})
    def test_optin_blocks_all_native(self):
        with mock.patch.dict(os.environ,{"P2_V327_FRESH_HAVOC_N_ONCE":"0"}):
            with self.assertRaisesRegex(study.HavocBlocked,
                                        "EXPLICIT_NATIVE_ONCE"):
                study.main()
    def test_v326_prior_contract_kept(self):
        from integration_probes import p2_v326_new_devastation_heldout_N_real_once as old
        self.assertEqual(old.N_GRID,(24,48,96,192))
        self.assertEqual(old.TOTAL_RESEARCH_NATIVE,120)
if __name__=="__main__":unittest.main()
