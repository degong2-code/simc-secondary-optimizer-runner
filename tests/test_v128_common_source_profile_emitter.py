"""v128 common source emitter parity: six source-backed profiles, Native 0.

The shadow serializer below mirrors the exact *pre-v128* generation behavior
in v082/v083/v084/v104, so same-fixture/cwd/profile bytes, config, tiers and
metadata must remain precisely unchanged. No real SimC binary is invoked.
"""
from __future__ import annotations
import pathlib,sys,tempfile,unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v055_simc_item_selection as items
import v101_common_representative_equipment as common
import v127_dps_source_metadata as metadata
import v128_common_source_profile_emitter as emitter

def prior_serializer(source,overrides,rows,slot_order,*,
                     blank_before_overrides,need=None,
                     check_duplicate_overrides=False):
    """Independent reference for the legacy v082/083/084 and v104 loops."""
    result=[]
    seen=set()
    for line in source.splitlines():
        if line.startswith("# Gear Summary"):
            break
        key,sep,_=line.partition("=")
        if blank_before_overrides:
            if (sep and not line.startswith("#") and
                (key in overrides or key in slot_order or
                 key=="temporary_enchant")):
                continue
        else:
            if sep and (key in slot_order or key=="temporary_enchant"):
                continue
            if sep and key in overrides:
                if check_duplicate_overrides:
                    need(key not in seen,"DUPLICATE_SOURCE_OVERRIDE:"+key)
                    seen.add(key)
                continue
        result.append(line)
    if blank_before_overrides:
        result.append("")
    result.extend(k+"="+v for k,v in overrides.items())
    result.extend(items.equipment_line(k,rows[k]["item_id"],334,
                  rows[k]["options"]) for k in slot_order)
    return "\n".join(result).rstrip()+"\n"

class SharedSourceEmission(unittest.TestCase):
    @staticmethod
    def need(ok,why):
        if not ok:raise ValueError(why)

    def test_all_six_source_factories_match_legacy_profiles_byte_for_byte(self):
        self.assertTrue(metadata.validate())
        for item in metadata.SOURCE_BACKED:
            with self.subTest(spec=item.key),tempfile.TemporaryDirectory() as td:
                folder=pathlib.Path(td)
                # Both calls receive the SAME path: initial_native/json2 paths
                # are absolute for three old factories.
                with mock.patch.object(emitter,"emit",side_effect=prior_serializer):
                    old=common.source_backed_gear(
                        item.key,folder,334,self.need)
                new=common.source_backed_gear(
                    item.key,folder,334,self.need)
                self.assertEqual(new,old)
                text,cfg,rows,groups,form,F=new
                self.assertIn("actions=",text)
                self.assertEqual(form,item.weapon_form)
                self.assertEqual(F,item.flask_vector())
                self.assertTrue(set(groups).issubset(rows))
                self.assertEqual(sum(kind=="tier" for kind in groups.values()),4)
                self.assertEqual(cfg["source"]["profile_sha256"],
                    __import__("hashlib").sha256(text.encode("utf8")).hexdigest())
                self.assertFalse((folder/"initial_native").exists())
                self.assertFalse((folder/"simc_results").exists())

    def test_two_legacy_layouts_preserve_apl_and_replace_runtime_and_equipment(self):
        source=('rogue="original"\n'
                'spec=subtlety\n'
                'actions=/stealth\n'
                'actions+=/shadowstrike\n'
                'race=dwarf\n'
                'race=dwarf\n'
                'temporary_enchant=123\n'
                'head=original,id=123\n'
                '# Gear Summary\n'
                'ignore=anything\n')
        rows={"head":{"slot":"head","item_id":271510,"ilevel":334,
                      "options":{"gem_id":"240967"}}}
        overrides={"race":"human","iterations":"35","json2":"output.json"}
        for blank in (False,True):
            with self.subTest(blank=blank):
                shared=emitter.emit(
                    source,overrides,rows,("head",),
                    blank_before_overrides=blank)
                previous=prior_serializer(
                    source,overrides,rows,("head",),
                    blank_before_overrides=blank)
                self.assertEqual(shared,previous)
                self.assertEqual(shared.count("actions+=/shadowstrike"),1)
                self.assertNotIn("temporary_enchant",shared)
                self.assertEqual(shared.count("head=selected_271510"),1)
                self.assertEqual(shared.count("json2=output.json"),1)
                self.assertNotIn("ignore=anything",shared)

    def test_shared_v104_duplicate_source_override_fails_closed(self):
        source=("rogue=x\niterations=35\niterations=30\nhead=a,id=1\n")
        rows={"head":{"slot":"head","item_id":271510,"ilevel":334,
                      "options":{}}}
        with self.assertRaisesRegex(ValueError,"DUPLICATE_SOURCE_OVERRIDE:iterations"):
            emitter.emit(source,{"iterations":"35"},rows,("head",),
                 blank_before_overrides=False,need=self.need,
                 check_duplicate_overrides=True)

    def test_missing_equipment_or_invalid_metadata_cannot_serialize(self):
        with self.assertRaisesRegex(emitter.SourceEmissionBlocked,
                                    "INVALID_SOURCE_EMISSION_CONTRACT"):
            emitter.emit("mage=x\n",{"iterations":"35"},{},
                         ("main_hand",),blank_before_overrides=True)

if __name__=="__main__":
    unittest.main()
