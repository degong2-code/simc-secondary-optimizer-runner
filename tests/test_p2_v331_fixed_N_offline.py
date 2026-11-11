"""v331 fixed N source contract and equal-budget evaluation; Native0."""
import unittest
from pathlib import Path
from integration_probes import p2_v331_unholy_fixed_N_real_once as p
from integration_probes import p2_v319_new_windwalker_v290_v318_real_once as fresh
class FixedN(unittest.TestCase):
    def test_fresh_case_and_grid(self):
        case,controls=fresh.new_user_case(p.CASE,p.SPEC)
        self.assertEqual((case["character_class"],case["character_spec"]),p.SPEC)
        self.assertIsNone(controls["final_T"])
        self.assertEqual(p.NS,(32,35,48,56,64))
        self.assertEqual(set(p.ARM_ORDER),set(p.NS))
    def test_holdout_changes_only_N_and_path(self):
        text="deathknight=test\niterations=56\njson2=/old/result.json\n"
        text+="".join("gear_"+s+"=1\n" for s in p.STATS)
        converted=p.held_input(text,56,Path("/tmp/new.json"))
        self.assertEqual(converted,text.replace("iterations=56","iterations=640").replace("/old/result.json","/tmp/new.json"))
    def test_same_budget_prefix_no_credit_for_unmeasured_candidates(self):
        a=(1,1,1,1);b=(2,1,0,1)
        rows=[{"target":dict(zip(p.STATS,v)),"phase":"scout","iterations":56}
              for v in (a,b)]
        times=[{"invocation_elapsed_seconds":1},{"invocation_elapsed_seconds":2}]
        held={a:{"DPS":99.,"CHMV":a},b:{"DPS":100.,"CHMV":b}}
        r=p.prefix_metrics(rows,times,held,iterations=100)
        self.assertEqual(r["completed_cases"],1)
        self.assertEqual(r["discovery_regret_pct"],1.)
        self.assertEqual(r["near_reference_CHMV_discovered"],0)
        self.assertIsNone(p.prefix_metrics(rows,times,held,wall=.5)["discovery_regret_pct"])
if __name__=="__main__":unittest.main()
