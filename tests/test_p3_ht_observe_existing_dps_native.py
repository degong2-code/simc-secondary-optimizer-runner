"""P3-HT diagnostic extraction is offline and does not call SimC."""
import hashlib,json,pathlib,sys,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from integration_probes import p3_ht_observe_existing_dps_native as audit

class ExistingNativeAudit(unittest.TestCase):
    def test_phase_map_and_compact_actual_raid_and_tier_rows(self):
        self.assertEqual(set(audit.PHASE_FOLDERS),
                         {"SEED_00","SEED_01","SCOUT_00","MATERIAL_00",
                          "CONFIRM_00","CONFIRM_01"})
        actor={"stats":[{"name":"fire_nova","num_executes":{"mean":7}}],
               "buffs":[{"name":"short_circuit","start_count":4}],
               "procs":[{"name":"Other Proc","trigger_count":10}]}
        found=audit._interesting_action_rows(actor)
        self.assertEqual(found["stats"][0]["name"],"fire_nova")
        self.assertEqual(found["buffs"][0]["name"],"short_circuit")
        self.assertEqual(found["procs"],[])
    def test_one_case_verifies_raw_simc_native_hash_before_observing(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)
            source=b"shaman=test\\noptimal_raid=1\\n"
            doc={"sim":{"options":{"optimal_raid":1,"iterations":35},
                        "overrides":{"battle_shout":1},
                        "players":[{"name":"x","specialization":"enhancement",
                            "race":"dwarf","level":90,"talents":"test",
                            "collected_data":{"buffed_stats":{"attribute":{"agility":2222}}},
                            "gear":{"head":{"name":"test","agiint":100}},
                            "buffs_constant":[{"name":"battle_shout","uptime":100}],
                            "stats":[{"name":"voltaic_blaze","num_executes":{"mean":3}}]}]}}
            native=json.dumps(doc).encode()
            (p/"input.simc").write_bytes(source)
            (p/"result.json").write_bytes(native)
            row={"phase":"SEED_00","dps_mean":1.0,
                 "dps_sem":0.1,"samples":35,
                 "input_sha256":hashlib.sha256(source).hexdigest(),
                 "native_sha256":hashlib.sha256(native).hexdigest()}
            brief,src,raw=audit._one_case(p,row)
            self.assertEqual((src,raw),(source,native))
            self.assertEqual(brief["primary_attributes"]["agility"],2222)
            self.assertEqual(brief["gear_primary_rating_sum"],100)
            self.assertEqual(brief["raid_optimal_setting"],1)
            self.assertEqual(brief["tier_relevant_actual_actions"]["stats"][0]["name"],
                             "voltaic_blaze")
            row["native_sha256"]="0"*64
            with self.assertRaisesRegex(audit.AuditBlocked,"SHA_MISMATCH"):
                audit._one_case(p,row)
if __name__=="__main__":
    unittest.main()
