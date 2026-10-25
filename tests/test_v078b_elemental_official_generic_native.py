"""v078b offline official target, historical proof and Native bounding rules."""
import pathlib,sys,tempfile,unittest,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v078b_elemental_official_generic_native as gate
import v061_scenario_contract as scenario

class V078BOfficialGenericSmoke(unittest.TestCase):
    def test_two_official_targets_preserve_total_and_100_transfer(self):
        static={"effective_floor_if_possible":{k:0 for k in scenario.STATS}}
        x,y=gate.targets(2948,static)
        self.assertEqual(sum(x.values()),2948)
        self.assertEqual(sum(y.values()),2948)
        self.assertEqual(x["crit_rating"]-y["crit_rating"],100)
        self.assertEqual(y["haste_rating"]-x["haste_rating"],100)
    def test_fixed_floor_blocks_ineligible_official_candidates(self):
        stats={"effective_floor_if_possible":dict.fromkeys(scenario.STATS,0)}
        stats["effective_floor_if_possible"]["crit_rating"]=700
        with self.assertRaisesRegex(gate.Blocked,"BELOW_FLOOR"):
            gate.targets(2948,stats)
    def test_witness_paths_require_actual_existing_artifact(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            rc=gate.run(root/"missing_parent",root/"out")
            self.assertEqual(rc,3)
            receipt=json.loads((root/"out"/"V078B_RECEIPT.json").read_text())
            self.assertEqual(receipt["status"],"BLOCKED_OR_PARTIAL")
            self.assertEqual(receipt["new_native_this_invocation"],0)
    def test_bounded_three_new_native(self):
        self.assertEqual(gate.NATIVE_CAP,3)
        self.assertEqual(gate.ITERATIONS,35)

if __name__=="__main__":unittest.main()
