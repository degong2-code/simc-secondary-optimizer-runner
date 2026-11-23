"""Focused first-user visible-oil contract, no Windows setup or Native.

This protects v690 against clicking the intentionally hidden oil checkbox.
Full real-browser/season/DPS evidence belongs to the existing one-shot job.
"""
from __future__ import annotations

import pathlib
import re
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]


class FirstUserOilVisibleContractTests(unittest.TestCase):
    def test_oil_is_user_visible_select_not_hidden_checkbox(self):
        markup=(ROOT/"runner/webui/index.html").read_text("utf8")
        select=re.search(
            r'<select\s+id="optimizer-oil-use-mode"[^>]*>'
            r'([\s\S]*?)</select>',markup)
        self.assertIsNotNone(select)
        self.assertRegex(select.group(1),r'<option\s+value="off">미사용</option>')
        self.assertRegex(markup,
                         r'<input\s+id="optimizer-oil-enabled"[^>]*\shidden\b')

    def test_real_ui_change_is_wired_to_original_oil_logic(self):
        js=(ROOT/"runner/webui/app.js").read_text("utf8")
        self.assertIn(
            '$("optimizer-oil-use-mode").addEventListener("change",()=>{',
            js)
        self.assertIn(
            '$("optimizer-oil-enabled").checked=selection==="use";',js)
        self.assertIn("withBusy(applyOilUseToggle);",js)

    def test_first_user_driver_selects_visible_off_and_checks_mirror(self):
        script=(ROOT/"integration_probes/"
                "p1_v690_one_zip_first_user_zero_history_once.py").read_text(
                    "utf8")
        self.assertIn('Select(oil_mode).select_by_value("off")',script)
        self.assertIn('wait_idle(driver,60)',script)
        self.assertIn('visible_oil_after_attempt',script)
        self.assertIn(
            'e.web_environment_scope?.environment_ready===true',script)
        self.assertIn(
            'e.web_environment_scope?.environment_installed===true',script)
        self.assertIn('oil_mode.is_displayed() and oil_mode.is_enabled()',script)
        # JS uses an explicit line break before .checked. Whitespace is
        # not a behavioral change; inspect the exact target expression.
        self.assertRegex(
            script,
            r"document\.getElementById\('optimizer-oil-enabled'\)\s*"
            r"\.checked")
        self.assertIn('record["last_completed_stage"]="VISIBLE_OIL_OFF_APPLIED"',
                      script)
        self.assertNotIn("clickable(driver,oil)",script)


if __name__=="__main__":
    unittest.main()
