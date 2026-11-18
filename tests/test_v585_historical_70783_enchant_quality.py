"""Pinned 70783 *historical* source-only enchant-rank regression; zero network/Native.

A tiny excerpt from the exact original pinned SimC generated tables; only
source-evidence regression (no runtime IDs, UI registration or quality gate).
The eight families' Wago membership is a separately cited original Action.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runner"))
import v211_enchant_source_effect_classification as classify


FIXTURE=Path(__file__).resolve().parent/"fixtures"/(
    "p1_v585_70783_linked_enchant_quality_pinned_source_excerpt.json")
STATIC_TYPES={"ITEM_ENCHANTMENT_STAT":5,"ITEM_ENCHANTMENT_RESISTANCE":4}


class HistoricalPinnedSourceQuality(unittest.TestCase):
    def test_70783_exact_original_eight_families_raw_components_not_admission(self):
        data=json.loads(FIXTURE.read_text("utf8"))
        self.assertEqual(data["game_build"],"12.1.5.70783")
        self.assertEqual(len(data["simc_revision"]),40)
        raw_permanent="\n".join(data["permanent_enchant_rows"])+"\n"
        source=classify.parse_permanent(raw_permanent)
        ids=set(source)
        self.assertEqual(len(ids),16)
        dbc=classify.parse_dbc_rows(
            "\n".join(data["spell_item_enchantment_rows"])+"\n",ids)
        self.assertEqual(set(dbc),ids)
        family_by_key={}
        for rows in source.values():
            for row in rows:
                key=(row["token"],row["item_class"],
                     row["inventory_type_mask"],row["item_subclass_mask"])
                family_by_key.setdefault(key,[]).append(row)
        self.assertEqual(len(family_by_key),8)
        seen=set()
        observed=[]
        for family in family_by_key.values():
            self.assertEqual(len(family),2)
            ranks=sorted(x["quality_rank"] for x in family)
            self.assertEqual(ranks,[1,2])
            top=max(family,key=lambda r:r["quality_rank"])
            seen.add(top["enchant_id"])
            ordered=sorted(family,key=lambda x:-x["quality_rank"])
            comparison=classify.source_rank_component_comparison(
                ordered,dbc,top["enchant_id"],STATIC_TYPES)
            self.assertFalse(comparison["quality_noninferiority_runtime_verified"])
            self.assertFalse(comparison["same_effect_and_use_conditions_verified"])
            self.assertFalse(comparison["ui_selectable"])
            self.assertFalse(comparison["policy_A_product_input_verified"])
            self.assertFalse(comparison["source_id_spell_identical"])
            self.assertTrue(comparison["simc_spell_value_may_override_raw_coefficient"])
            self.assertEqual(comparison["stat_value_precedence_source"],
                "SIMC_ENCHANT_SPELL_AVERAGE_FIRST_THEN_DBC_COEFFICIENT_FALLBACK")
            observed.append((top["enchant_id"],comparison))
        self.assertEqual(seen,set(data["high_rank_enchant_ids"]))
        raw_static={eid for eid,row in observed if row[
            "source_raw_amount_and_coefficient_nondecreasing"]}
        self.assertEqual(raw_static,{7935,7939,8159,8161,8163})
        self.assertEqual(sum(row["source_strictly_stronger_raw_component"]
                             for _,row in observed),5)
        self.assertEqual(sum(row["status"]==
            "SOURCE_COMPONENT_KIND_OR_SPELL_DRIVER_NEEDS_REVIEW"
            for _,row in observed),3)
        self.assertEqual(sum(row["source_same_scaling_and_use_conditions"]
                             for _,row in observed),8)
        # 5 static families are PRIMARY/HP/ARMOR, NOT CHMV E.
        stat_props={32,36,49,40}
        for eid,comparison in observed:
            for source_rank in comparison["by_source_rank"]:
                for comp in source_rank["components"]:
                    self.assertFalse(comp["enchant_type_id"]==5 and
                                     comp["stat_or_spell_id"] in stat_props,
                                     "unexpected fixed CHMV source in "+str(eid))

    def test_driver_id_or_conditions_changed_cannot_source_approve(self):
        data=json.loads(FIXTURE.read_text("utf8"))
        source=classify.parse_permanent(
            "\n".join(data["permanent_enchant_rows"])+"\n")
        dbc=classify.parse_dbc_rows(
            "\n".join(data["spell_item_enchantment_rows"])+"\n",set(source))
        upper=[x for group in source.values() for x in group
               if x["enchant_id"] in (7938,7939)]
        upper.sort(key=lambda x:-x["quality_rank"])
        # SimC 7939/7938 share identical static component stat kinds.
        self.assertTrue(classify.source_rank_component_comparison(
            upper,dbc,7939,STATIC_TYPES)[
            "source_raw_amount_and_coefficient_nondecreasing"])
        changed={k:{**v,"ench_coeff":list(v["ench_coeff"])}
                 for k,v in dbc.items()}
        changed[7939]["ench_coeff"][0]=0.1
        self.assertFalse(classify.source_rank_component_comparison(
            upper,changed,7939,STATIC_TYPES)[
            "source_raw_amount_and_coefficient_nondecreasing"])
        changed2={k:dict(v) for k,v in dbc.items()}
        changed2[7939]["min_ilevel"]=130
        result=classify.source_rank_component_comparison(
            upper,changed2,7939,STATIC_TYPES)
        self.assertEqual(result["status"],
                         "SOURCE_USE_OR_SCALING_SCOPE_DIFFERS")
        self.assertFalse(result["ui_selectable"])


if __name__=="__main__":
    unittest.main()
