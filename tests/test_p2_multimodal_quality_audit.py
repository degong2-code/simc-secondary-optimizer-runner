"""Optional P2 synthetic proposal-policy audit; NOT product Native evidence.

Run manually when considering exploration schedule changes:
    PYTHONPATH=runner:integration_probes:. python -m unittest -v tests.test_p2_multimodal_quality_audit

Intentionally excluded from always-on focused CI; identical candidate call
count is not a guarantee of identical total iterations/CPU. No SimC invoked.
"""
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v290_multiscale_adaptive_policy as p


class MultimodalAudit(unittest.TestCase):
    B=3107
    lo=(50,0,0,0)
    hi=(1553,1553,1553,1553)

    def test_multimodal_equal_budget_non_native_strategy_audit(self):
        """Compare proposal schedules only; never interpret oracle as SimC.

        Two genuinely distinct strategies receive identical CHMV bounds and
        equal case budgets. A second schedule occasionally requests an extra
        existing global maximin candidate; it is NOT a proposed product policy.
        Neither observations nor SEM in this synthetic audit are Native data.
        """
        import json
        import math
        cap=112
        desired=min(64,max(8,math.ceil(2*math.sqrt(cap))))
        a=(736,900,736,735)
        b=(245,1450,795,617)
        c=(1430,305,700,672)
        d=(50,1553,1503,1)
        e=(1090,1250,400,367)
        f=(350,650,1200,907)
        cases={
            "single_smooth":((a,190000.,.007),),
            "separated_interior":((a,188000.,.009),
                                  (b,192000.,.032)),
            "separated_boundary":((a,188000.,.009),
                                  (d,193000.,.028)),
            "three_disjoint":((a,188000.,.009),
                               (b,192000.,.032),
                               (c,191500.,.030)),
            "off_axis_narrow":((a,188000.,.008),
                                (e,194000.,.055)),
            "off_axis_broad":((a,189000.,.008),
                               (f,192000.,.015)),
        }
        def run(peaks,extra_global_every):
            rows=[]
            unique=set()
            global_proposals=0
            requested_iterations=0
            best=-float("inf")
            best_vector=None
            for i in range(cap):
                proposal=p.next_plan(
                    rows,total=self.B,lower=self.lo,upper=self.hi,
                    native_calls_used=i,max_native_calls=cap,
                    scout_iterations=35,confirmation_iterations=320,
                    max_iterations=320)
                self.assertEqual(proposal["status"],"NEXT_NATIVE_PROPOSED")
                q=proposal["next_request"]
                vector=tuple(q["target"][s] for s in p.STATS)
                decision=proposal["decision"]
                if (extra_global_every and len(unique)>=desired
                        and (i+1)%extra_global_every==0
                        and q["phase"]=="scout"):
                    alternate=p._unobserved_global_maximin(
                        self.B,self.lo,self.hi,desired,unique)
                    if alternate is not None:
                        vector=alternate
                        q={"phase":"scout","iterations":35,
                           "target":p.legacy.to_target(vector)}
                        decision="AUDIT_ONLY_EXTRA_GLOBAL"
                self.assertTrue(p.legacy.eligible(
                    vector,self.B,self.lo,self.hi))
                self.assertFalse(vector in unique and q["phase"]=="scout")
                if ("GLOBAL" in decision):
                    global_proposals+=1
                # Oracle is a geometric *synthetic* max of smooth separated
                # peaks, not predicted or simulated DPS.
                value=max(height-penalty*p._distance(vector,peak)**2
                          for peak,height,penalty in peaks)
                if value>best:
                    best,best_vector=value,vector
                unique.add(vector)
                requested_iterations+=q["iterations"]
                rows.append({"target":q["target"],
                             "iterations":q["iterations"],
                             "dps_mean":value,
                             "dps_sem":500. if q["phase"]=="scout" else 150.})
            return {"calls":len(rows),"unique":len(unique),
                    "requested_iterations":requested_iterations,
                    "extra_or_regular_global_proposals":global_proposals,
                    "best_oracle_value":round(best,3),
                    "oracle_regret":round(max(height for _,height,_ in peaks)-best,3),
                    "best_target":best_vector,
                    "nearest_known_peak":min(
                        p._distance(best_vector,peak) for peak,_,_ in peaks)}
        for name,peaks in cases.items():
            with self.subTest(synthetic_shape=name):
                self.assertTrue(all(
                    sum(peak)==self.B and
                    p.legacy.eligible(peak,self.B,self.lo,self.hi)
                    for peak,_,_ in peaks))
                existing=run(peaks,None)
                exploratory=run(peaks,9)
                self.assertEqual(existing["calls"],cap)
                self.assertEqual(exploratory["calls"],cap)
                self.assertGreater(exploratory["extra_or_regular_global_proposals"],
                                   existing["extra_or_regular_global_proposals"])
                print("P2_SYNTHETIC_MULTIMODAL_AUDIT "+
                      json.dumps({"shape":name,"existing":existing,
                                  "audit_more_global":exploratory},
                                 sort_keys=True),flush=True)


if __name__=="__main__":
    unittest.main()
