"""P3-HAJ: source-locked 70783 local web real Native single-shot guard."""
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]

class WebRealOnceGuard(unittest.TestCase):
    def test_opt_in_scope_and_real_web_bridge(self):
        w=(ROOT/".github/workflows/p3_fz_reuse_exact_simc_live_t1.yml").read_text()
        p=(ROOT/"integration_probes/p3_fr_zero_base_t1_acceptance.py").read_text()
        q=(ROOT/"integration_probes/p3_haj_real_local_web_native_e2e.py").read_text()
        for k in ("[p3-haj-web-native-once]",
                  "p3_haj_real_web_native_once_20261109.json",
                  "P3_T1_WEB_LONGRUN_ONCE",
                  '"adaptive_dps_native_max":4',
                  '"cache_only_new_native_calls":0',
                  "requirements-web-test.txt"):
            self.assertIn(k,w)
        for k in ("if web_longrun:","web_e2e.execute(",
                  "P3_HAJ_EXCLUSIVE_REAL_WEB_DPS_REQUIRED"):
            self.assertIn(k,p)
        for k in ("v213_source_to_catalog","/api/v1/longrun/prepare",
                  "/longrun/resume","/longrun/cancel",
                  "/longrun/cache-only","/longrun/result",
                  "all(v*2<total for v in vector.values())",
                  "real_browser_click_tested"):
            self.assertIn(k,q)
        # Ret web once must not inherit Enh specialization or v291 probe mode.
        for key in ("P3_T1_SPEC_CLASS:", "P3_T1_SPEC_NAME:",
                    "P3_T1_FULL_CONSUMABLES_ONCE:",
                    "P3_T1_V291_LONGRUN_NATIVE_ONCE:"):
            line=next(x for x in w.splitlines() if x.strip().startswith(key))
            self.assertNotIn("p3-haj-web-native-once",line)
        for key in ("P3_T1_EXISTING_SPECIAL_GEM_ID:",
                    "P3_T1_DPS_E2E_ONCE:",
                    "P3_T1_WEB_LONGRUN_ONCE:"):
            line=next(x for x in w.splitlines() if x.strip().startswith(key))
            self.assertIn("p3-haj-web-native-once",line)
        compile(p,"p3_fr_zero_base_t1_acceptance.py","exec")
        compile(q,"p3_haj_real_local_web_native_e2e.py","exec")


    def test_one_selected_oil_uses_original_build_flags_and_web_session(self):
        # The same T1 compiler, v216 installer and v113 user API serve O0
        # and positive O. Do not add a second O calculator or trust HTTP O.
        from integration_probes import p3_fr_zero_base_t1_acceptance as once
        exact={"main_hand":243734}
        source=once.selected_t1_source_inputs(
            exact_flask_item_id=241324,existing_special_gem_id=240967,
            selected_oil_item_ids_by_hand=exact)
        self.assertEqual(source["selected_budget_items"]["oil_item_ids_by_hand"],
                         exact)
        flags=once.t1_native_source_controls(
            selected_F=241324,f_only=False,binary_available=True,
            selected_oil_items=exact)
        self.assertTrue(flags["auto_native_O_requested"])
        self.assertTrue(flags["auto_native_F_requested"])
        self.assertFalse(once.t1_native_source_controls(
            selected_F=241324,f_only=False,binary_available=True
        )["auto_native_O_requested"])
        self.assertEqual(once.selected_t1_source_inputs(
            exact_flask_item_id=241324,existing_special_gem_id=240967
        )["selected_budget_items"]["oil_item_ids_by_hand"],{})
        probe=(ROOT/"integration_probes/p3_haj_real_local_web_native_e2e.py").read_text()
        self.assertIn('args["selected_oil_item_ids_by_hand"]=selected_oils',probe)
        self.assertIn('app.state.jobs.persist_verified_fresh_profile()',probe)
        self.assertIn('"P1_O_WEB_FINAL_B_T_ACCOUNTING_DRIFT"',probe)
        self.assertNotIn('"static_CHMV_vector": {"crit_rating":16',probe)

    def test_manual_t_test_reuses_real_api_and_new_executable_sha(self):
        workflow=(ROOT/".github/workflows/p3_har_manual_t_native_once.yml").read_text()
        probe=(ROOT/"integration_probes/p3_haj_real_local_web_native_e2e.py").read_text()
        launcher=(ROOT/"integration_probes/p3_fr_zero_base_t1_acceptance.py").read_text()
        self.assertIn("P3_HAR_USER_MANUAL_FINAL_T: '3500'",workflow)
        self.assertIn("SIMC_PINNED_BINARY_SHA256=$SHA",workflow)
        self.assertIn("P3_HAR_NEW_BINARY_SHA",workflow)
        self.assertIn("manual_final_T=user_manual_T",launcher)
        self.assertIn('"/api/v1/sessions/"+prepared["session_id"]+"/inputs"',probe)
        self.assertIn('checked["user"]["target"]["final_T"]==manual_final_T',probe)
        self.assertNotIn('prepared["plan"]["final_T"]',probe)
        compile(probe,"p3_haj_real_local_web_native_e2e.py","exec")
        compile(launcher,"p3_fr_zero_base_t1_acceptance.py","exec")


if __name__=="__main__":
    unittest.main()
