"""v652: environment input layout and existing SimC control wiring.

No live SimC/HTTP/DB2. The current product DOM and JavaScript are the
contract, not a mock design playground. Tests are independent of screenshots.
"""
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/"runner"/"webui"


class IDReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
        self.labels=[]
    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if "id" in values:
            self.ids.append(values["id"])
        if tag=="label" and "for" in values:
            self.labels.append(values["for"])


class EnvironmentGridV652(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(WEB/"index.html").read_text(encoding="utf8")
        cls.css=(WEB/"styles.css").read_text(encoding="utf8")
        cls.js=(WEB/"app.js").read_text(encoding="utf8")

    def test_actual_user_controls_are_unique_and_in_requested_rows(self):
        parser=IDReader();parser.feed(self.html)
        self.assertEqual(len(parser.ids),len(set(parser.ids)))
        self.assertTrue(set(parser.labels).issubset(set(parser.ids)))
        start=self.html.index('<div class="env-input-grid"')
        end=self.html.index('<div class="env-bottom-row"',start)
        env=self.html[start:end]
        slots=["targets","duration","season-target-socket-count",
               "optimizer-oil-use-mode","food","season-verified-flask",
               "potion","augmentation","omnium"]
        positions=[env.index('id="'+i+'"') for i in slots]
        self.assertEqual(positions,sorted(positions))
        self.assertEqual(env.count('class="env-grid-cell"'),8)
        self.assertIn('class="env-grid-cell env-omnium"',env)
        for name in slots:
            self.assertEqual(parser.ids.count(name),1)
        self.assertIn('<select id="optimizer-oil-use-mode"',env)
        self.assertIn('<option value="use">사용</option>',env)
        self.assertIn('<option value="off">미사용</option>',env)
        self.assertIn('id="optimizer-oil-enabled" type="checkbox" checked hidden',env)
        self.assertIn('<select id="season-verified-flask"',env)
        self.assertIn('<select id="augmentation"',env)
        self.assertIn('id="env-flask-summary" hidden',env)
        self.assertIn('id="season-verified-flask-status" hidden',env)
        self.assertEqual(self.html.count('id="raid_buffs"'),1)
        self.assertEqual(self.html.count('id="user-variant-prepare-btn"'),1)

    def test_enchant_order_and_compatibility_slot(self):
        start=self.html.index('<div class="env-enchant-grid"')
        end=self.html.index('</div>\n</details>',start)
        block=self.html[start:end]
        ids=["env-enchant-weapon","env-enchant-offhand",
             "season_enchant_finger1","season_enchant_finger2",
             "env-enchant-chest","env-enchant-legs",
             "env-enchant-helm","env-enchant-shoulders",
             "env-enchant-back","env-enchant-boots",
             "env-enchant-waist","env-enchant-hands",
             "env-enchant-wrists","env-enchant-neck",
             "season_enchant_other"]
        positions=[block.index('id="'+i+'"') for i in ids]
        self.assertEqual(positions,sorted(positions))
        self.assertEqual(block.count('class="field env-enchant-cell env-enchant-wide"'),2)
        self.assertIn('id="season_enchant_other"',block)
        self.assertIn('class="field env-enchant-cell" hidden',block)
        # Native slot semantics: main/off hand remain distinct, never alias.
        self.assertIn('for="env-enchant-weapon">무기(주무기)</label>',block)
        self.assertIn('for="env-enchant-offhand">보조무기</label>',block)
        self.assertIn('for="env-enchant-boots">발</label>',block)

    def test_uniform_control_styles_and_mobile_two_columns(self):
        css=self.css
        self.assertIn('v652 — Unified four-column input controls',css)
        self.assertIn('grid-template-columns:repeat(4,minmax(0,1fr))',css)
        self.assertIn('grid-template-rows:18px 36px',css)
        self.assertIn('grid-column:span 2',css)
        self.assertIn('@media(max-width:880px)',css)
        self.assertIn('@media(max-width:480px)',css)
        self.assertIn('grid-template-columns:repeat(2,minmax(0,1fr))',css)
        # v653 inherits the original class/spec input visual language,
        # not v652's introduced visible outlines or shaded wrapper card.
        self.assertIn('v653 — the class/spec selects are the visual authority',css)
        self.assertIn('border:1px solid transparent!important;border-radius:5px!important',css)
        self.assertIn('background:#2C2B30!important;',css)
        self.assertIn('height:33px!important;min-height:33px!important',css)
        self.assertIn('grid-template-rows:18px 33px',css)
        self.assertIn('#season-target-socket-count{',css)
        self.assertIn('width:100%!important;min-width:0!important;max-width:100%!important',css)
        self.assertIn('background:transparent;border:0;',css)
        self.assertIn('background:#493c29!important',css)
        self.assertIn('#user-variant-prepare-btn',css)
        self.assertIn('#optimizer-oil-enabled[hidden]{display:none!important}',css)
        self.assertNotIn('border:1px solid #444045!important',css)
        self.assertNotIn('background:#2b2926;border:1px solid #484039',css)

    def test_v653_equal_size_four_cells_and_original_control_look(self):
        css=self.css
        # Must match the same 33px, borderless controls as the class/spec
        # fields. This test guards the regression shown in the user's image.
        self.assertIn('border:1px solid transparent!important;border-radius:5px!important',css)
        self.assertIn('background:#2C2B30!important;',css)
        self.assertIn('height:33px!important;min-height:33px!important',css)
        self.assertIn('grid-template-columns:repeat(4,minmax(0,1fr))',css)
        self.assertIn('#optimizer-form .conditions-panel #season-gem-layout,',css)
        self.assertIn('#optimizer-form .conditions-panel #season-gem-layout>.field{',css)
        self.assertIn('justify-self:stretch;align-self:end',css)
        self.assertIn('background:transparent;border:0;',css)
        self.assertNotIn('background:var(--input);border:1px solid #444045!important',css)
        self.assertNotIn('border-left:3px solid #bb9450;border-radius:8px',css)

    def test_actual_oil_sync_uses_existing_boolean_not_new_budget(self):
        self.assertIn('function applyOilUseToggle()',self.js)
        self.assertIn('withBusy(applyOilUseToggle)',self.js)
        self.assertIn('"optimizer-oil-use-mode","optimizer-oil-loadout"',self.js)
        self.assertIn('$("optimizer-oil-use-mode").disabled=busy||active;',self.js)
        self.assertIn('box.checked=oilUseIntent;',self.js)
        self.assertIn('selector.value=oilUseIntent?"use":"off";',self.js)
        self.assertIn('$("optimizer-oil-enabled").checked=selection==="use";',self.js)
        self.assertIn('"season-verified-flask"',self.js)
        self.assertIn('"augmentation"',self.js)

    def test_oil_dropdown_sync_executes_actual_js(self):
        node=shutil.which("node")
        if not node:self.skipTest("Node.js unavailable")
        code=r"""
const assert=require('node:assert/strict'),fs=require('fs');
const js=fs.readFileSync(process.argv[1],'utf8');
const begin=js.indexOf('function syncOilUseToggle(){');
const end=js.indexOf('\nfunction tryApplyDefaultOil()',begin);
assert(begin>=0 && end>begin);
const nodes={
  'optimizer-oil-enabled':{checked:false},
  'optimizer-oil-use-mode':{value:'off'},
  'optimizer-oil-toggle-status':{textContent:''}
};
const make=(intent,verified)=>Function('$','oilUseIntent',
  'selectedFullVerifiedOil','oilNeedsOffhand',
  js.slice(begin,end)+'\nreturn syncOilUseToggle;')(
  id=>nodes[id],intent,()=>verified,()=>false);
make(true,{installed_manifest_sha256:'x'})();
assert.equal(nodes['optimizer-oil-enabled'].checked,true);
assert.equal(nodes['optimizer-oil-use-mode'].value,'use');
assert.equal(nodes['optimizer-oil-toggle-status'].textContent,'주무기 적용');
make(false,null)();
assert.equal(nodes['optimizer-oil-enabled'].checked,false);
assert.equal(nodes['optimizer-oil-use-mode'].value,'off');
assert.equal(nodes['optimizer-oil-toggle-status'].textContent,'미사용');
console.log('V652_EXACT_OIL_SELECT_BOOL_SYNC_PASS');
"""
        completed=subprocess.run(
            [node,"-e",code,str(WEB/"app.js")],
            capture_output=True,text=True,encoding="utf8",errors="replace",
            timeout=20,cwd=ROOT)
        self.assertEqual(completed.returncode,0,completed.stderr)
        self.assertIn('V652_EXACT_OIL_SELECT_BOOL_SYNC_PASS',completed.stdout)


if __name__=="__main__":
    unittest.main()
