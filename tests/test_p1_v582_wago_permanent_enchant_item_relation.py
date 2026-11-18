"""Offline v582 source-join contract: no Wago network or SimC Native."""
import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "integration_probes/p1_v582_wago_permanent_enchant_item_relation_once.py"
spec = importlib.util.spec_from_file_location("p1_v582_probe", SCRIPT)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def write_csv(root, name, columns, rows):
    with (root / (name + ".csv")).open("w", encoding="utf8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)


class PermanentEnchantSameBuildJoin(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.root = root
        write_csv(root, "Item", ["ID", "ClassID", "SubclassID"], [
            {"ID":244014,"ClassID":8,"SubclassID":0}, {"ID":244015,"ClassID":8,"SubclassID":0},
            {"ID":244016,"ClassID":8,"SubclassID":0}, {"ID":700,"ClassID":3,"SubclassID":0}])
        write_csv(root, "ItemSparse", ["ID","ExpansionID","Display_lang"], [
            {"ID":244014,"ExpansionID":11,"Display_lang":"Ring enchant"},
            {"ID":244015,"ExpansionID":10,"Display_lang":"Wrong expansion"},
            {"ID":244016,"ExpansionID":11,"Display_lang":"Other enchant"},
            {"ID":700,"ExpansionID":11,"Display_lang":"Not a scroll"}])
        write_csv(root, "ItemXItemEffect", ["ItemID","ItemEffectID"], [
            {"ItemID":244014,"ItemEffectID":100},
            {"ItemID":244015,"ItemEffectID":101},
            {"ItemID":244016,"ItemEffectID":102},
            {"ItemID":700,"ItemEffectID":103}])
        write_csv(root, "ItemEffect", ["ID","SpellID","TriggerType"], [
            {"ID":100,"SpellID":777,"TriggerType":5},
            {"ID":101,"SpellID":778,"TriggerType":0},
            {"ID":102,"SpellID":779,"TriggerType":0},
            {"ID":103,"SpellID":780,"TriggerType":0}])
        write_csv(root, "SpellEffect", [
            "SpellID","Effect","EffectIndex","EffectMiscValue_0","DifficultyID"], [
            {"SpellID":777,"Effect":53,"EffectIndex":0,"EffectMiscValue_0":8025,"DifficultyID":0},
            {"SpellID":778,"Effect":53,"EffectIndex":0,"EffectMiscValue_0":8025,"DifficultyID":0},
            {"SpellID":779,"Effect":54,"EffectIndex":0,"EffectMiscValue_0":8039,"DifficultyID":0},
            {"SpellID":780,"Effect":53,"EffectIndex":0,"EffectMiscValue_0":8025,"DifficultyID":0}])
        self.simc = {
            8025:[{"token":"enchant_ring__silvermoons_alacrity","quality_rank":2}],
            8039:[{"token":"enchant_weapon__acuity_of_the_rendorei","quality_rank":2}]}
        self.highest = [{"enchant_id":8025},{"enchant_id":8039}]

    def tearDown(self):
        self.temp.cleanup()

    def test_exact_item_expansion_and_spell_effect_53(self):
        result = probe.wago_join(self.root,self.simc,self.highest,11)
        self.assertEqual(result["highest_simc_candidate_count"],2)
        self.assertEqual(result["highest_source_rank_linked"],1)
        self.assertEqual(result["highest_source_rank_unlinked_ids"],[8039])
        self.assertEqual(result["matched_physical_item_ids"],1)
        self.assertEqual(result["matches"][0]["wago_items"][0]["item_id"],244014)
        self.assertEqual(result["matches"][0]["wago_items"][0]["apply_spell_id"],777)
        self.assertEqual(result["other_wago_permanent_enchant_ids_not_in_simc_token_source"],[])

    def test_not_confuse_real_expansion_with_wrong_expansion(self):
        write_csv(self.root,"ItemSparse",["ID","ExpansionID","Display_lang"],[
            {"ID":244014,"ExpansionID":10,"Display_lang":"Wrong expansion"},
            {"ID":244015,"ExpansionID":11,"Display_lang":"Current expansion"},
            {"ID":244016,"ExpansionID":11,"Display_lang":"Other enchant"}])
        result=probe.wago_join(self.root,self.simc,self.highest,11)
        self.assertEqual(result["matched_physical_item_ids"],1)
        self.assertEqual(result["matches"][0]["wago_items"][0]["item_id"],244015)

    def test_unchanged_simc_id_not_sufficient(self):
        write_csv(self.root,"SpellEffect",
                  ["SpellID","Effect","EffectIndex","EffectMiscValue_0","DifficultyID"],[
            {"SpellID":777,"Effect":54,"EffectIndex":0,"EffectMiscValue_0":8025,"DifficultyID":0},
            {"SpellID":778,"Effect":53,"EffectIndex":0,"EffectMiscValue_0":123456,"DifficultyID":0},
            {"SpellID":779,"Effect":53,"EffectIndex":0,"EffectMiscValue_0":123456,"DifficultyID":0}])
        result=probe.wago_join(self.root,self.simc,self.highest,11)
        self.assertEqual(result["highest_source_rank_linked"],0)
        self.assertEqual(result["highest_source_rank_unlinked_ids"],[8025,8039])
        self.assertIn(123456,result["other_wago_permanent_enchant_ids_not_in_simc_token_source"])


if __name__=="__main__":
    unittest.main()
