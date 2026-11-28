"""P3-BV: no-network exact gem enchant source join and one-stage cache."""
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runner import v266_gem_enchant_raw_stat_source as source
from runner import v268_gem_enchant_existing_source_stage as adapter


BUILD="12.1.5.70575"


def joined(*,game_build=BUILD):
    rows=[
        (2001,11,501),(2002,12,502),
        (2003,13,503),(2004,14,504)]
    return {
        "schema":source.GEM_SOURCE_SCHEMA,
        "status":source.GEM_SOURCE_STATUS,
        "game_build":game_build,
        "simc_generated_gem_source_build":game_build,
        "simc_revision":"b"*40,
        "v213_manifest_sha256":"c"*64,
        "exact_link_count":len(rows),
        "joins":[{"item_id":itemid,"gem_property_id":property_id,
                  "enchant_id":enchant_id,
                  "color_mask":(1 if itemid==2003 else 2),
                  "minimum_ilevel":(345 if itemid==2003 else 300),
                  "expansion_id":12,
                  "socket_eligibility":"NOT_YET_VERIFIED",
                  "status":"EXACT_DB2_ITEMSPARSE_GEM_PROPERTY_RELATION",
                  "ui_selectable":False}
                 for itemid,property_id,enchant_id in rows],
    }


def enchant_csv():
    header=list(source.COLUMNS)
    buf=io.StringIO()
    writer=csv.DictWriter(buf,fieldnames=header,lineterminator="\n")
    writer.writeheader()
    def row(iid,kind,arg,points,scaling=0):
        v={column:"0" for column in header}
        v.update(ID=str(iid),Effect_0=str(kind),
                 EffectArg_0=str(arg),EffectPointsMin_0=str(points),
                 EffectScalingPoints_0=str(scaling))
        writer.writerow(v)
    row(501,5,32,25,0)  # static crit raw points only
    row(502,5,36,40,1.5)  # stat but scaled, must remain pending
    row(503,3,123,0,0)   # spell effect not a plain stat
    # 504 deliberately missing: absence is not proof of zero stat.
    row(9000,5,40,999,0) # irrelevant other enchant ignored
    return buf.getvalue().encode("utf8")


class GemEnchantmentSourceReuseTests(unittest.TestCase):
    def test_raw_static_points_are_not_approved_J_or_highest_quality(self):
        result=source.preview(
            gem_join=joined(),raw_enchant_csv=enchant_csv(),
            expected_game_build=BUILD)
        self.assertEqual(result["raw_static_candidate_count"],1)
        self.assertEqual(result["unresolved_count"],3)
        self.assertIsNone(result["J"])
        self.assertFalse(result["highest_quality_selection_verified"])
        self.assertFalse(result["environment_ready"])
        self.assertEqual(result["native_calls"],0)
        by_id={r["item_id"]:r for r in result["records"]}
        self.assertEqual(by_id[2001]["raw_static_points_candidate"],{
            "crit_rating":25,"haste_rating":0,"mastery_rating":0,
            "versatility_rating":0})
        self.assertEqual(by_id[2002]["effect_classification"],
            "NONSTATIC_SCALED_OR_NON_CHMV_EFFECT_PENDING")
        self.assertEqual(by_id[2003]["effect_classification"],
            "NONSTATIC_SCALED_OR_NON_CHMV_EFFECT_PENDING")
        self.assertEqual(by_id[2004]["effect_classification"],
            "ENCHANT_ID_MISSING_FROM_SAME_BUILD_CSV")
        self.assertTrue(all(not row["ui_selectable"]
                            and not row["J_rating_verified"]
                            for row in result["records"]))

    def test_p3_fm_four_nominal_stat_types_from_one_sealed_join(self):
        # A special is already chosen. No effect/role proof or Native call.
        links=joined()
        links["joins"]=[]
        header=list(source.COLUMNS)
        buf=io.StringIO()
        writer=csv.DictWriter(buf,fieldnames=header,lineterminator="\n")
        writer.writeheader()
        for i,stat_code in enumerate((0,32,36,49,40,32,32,32,32,32)):
            item=2100+i
            links["joins"].append({
                "item_id":item,"gem_property_id":11+i,
                "enchant_id":600+i,"color_mask":2,
                "minimum_ilevel":14277 if i in (5,8) else 0,"expansion_id":12,
                "socket_eligibility":"NOT_YET_VERIFIED",
                "status":"EXACT_DB2_ITEMSPARSE_GEM_PROPERTY_RELATION",
                "ui_selectable":False})
            row={key:"0" for key in header}
            row.update(ID=str(600+i),
                       Effect_0="5",
                       EffectArg_0=str(32 if i==0 else stat_code),
                       EffectPointsMin_0=str(200 if i==0 else 20+i*5),
                       EffectScalingPoints_0="0")
            if i>=2:
                # Each ordinary is a 2-stat gem: +dominant/+7.
                # One equal +50/+50 example must remain unassigned.
                row.update(Effect_1="5",
                           EffectArg_1=str(
                               {2:32,3:40,4:36,5:49,6:36,
                                7:36,8:36,9:36}[i]),
                           EffectPointsMin_1=str(50 if i==6 else 7),
                           EffectScalingPoints_1="0")
            if i>=7:
                row.update(EffectScalingPoints_0="0.5",
                           EffectScalingPoints_1="0.2")
                if i==9:
                    row.update(Effect_1="3")
            writer.writerow(row)
        links["exact_link_count"]=len(links["joins"])
        raw=buf.getvalue().encode("utf8")
        class FakeResponse:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,size=-1):return raw
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            collected=adapter.collect(stage_root=root,build=BUILD,
                transport=lambda req,timeout:FakeResponse())
            self.assertEqual(collected["status"],"GEM_ENCHANT_CSV_SOURCE_SEALED")
            path=root/"v221.json"
            path.write_text(json.dumps(links),encoding="utf8")
            first=adapter.view(
                stage_root=root,v221_candidate_path=path,build=BUILD,
                selected_source_gem_item_ids=[2100],
                excluded_ordinary_item_id=2100)
            self.assertTrue(first[
                "four_stat_ordinary_source_complete_unadmitted"])
            self.assertEqual({
                k:v["item_id"] for k,v in first[
                    "four_stat_ordinary_best_observed_unadmitted"].items()},
                {"crit_rating":2105,"haste_rating":2102,
                 "mastery_rating":2103,"versatility_rating":2104})
            # Full CHMV, including secondary +7, belongs to J rather than
            # treating these four legitimate ordinary gems as missing.
            self.assertEqual(first[
                "four_stat_ordinary_best_observed_unadmitted"],{
                    "crit_rating":{"item_id":2105,"raw_nominal_points":52},
                    "haste_rating":{"item_id":2102,"raw_nominal_points":37},
                    "mastery_rating":{"item_id":2103,"raw_nominal_points":42},
                    "versatility_rating":{"item_id":2104,"raw_nominal_points":47}})
            scoped=adapter.view(
                stage_root=root,v221_candidate_path=path,build=BUILD,
                target_ilevel=334,selected_gem_item_ids=[2105])
            self.assertTrue(scoped["four_stat_ordinary_source_complete_unadmitted"])
            self.assertEqual(scoped[
                "ordinary_two_CHMV_scaled_shape_candidate_ids_source_only"],[2107,2108])
            self.assertEqual(scoped["four_stat_ordinary_best_observed_unadmitted"],
                             first["four_stat_ordinary_best_observed_unadmitted"])
            self.assertEqual(scoped["selected_gem_raw_points_by_id_unadmitted"],
                             {"2105":52})
            boundary=adapter.view(stage_root=root,v221_candidate_path=path,
                                  build=BUILD,target_ilevel=340)
            self.assertEqual(boundary["four_stat_ordinary_best_observed_unadmitted"],
                             first["four_stat_ordinary_best_observed_unadmitted"])
            self.assertEqual(boundary[
                "ordinary_two_CHMV_scaled_shape_candidate_ids_source_only"],[2107,2108])
            for invalid in (2105,2107):
                role=adapter.view(stage_root=root,v221_candidate_path=path,
                    build=BUILD,selected_source_gem_item_ids=[invalid],
                    excluded_ordinary_item_id=invalid,target_ilevel=340)
                self.assertTrue(role[
                    "selected_special_gem_two_CHMV_accounting_pending_source_only"])
            # A missing or non-CHMV shape is not a positive role proof.
            self.assertFalse(first[
                "selected_special_gem_two_CHMV_accounting_pending_source_only"])
            # A one-stat source cannot silently become a zero-CHMV special.
            self.assertTrue(first[
                "selected_special_gem_positive_CHMV_accounting_pending_source_only"])
            chosen=adapter.view(
                stage_root=root,v221_candidate_path=path,build=BUILD,
                selected_gem_item_ids=[2102,2103,2104,2105],
                selected_source_gem_item_ids=[
                    2100,2102,2103,2104,2105],
                excluded_ordinary_item_id=2100)
            self.assertEqual(
                chosen["selected_gem_raw_points_by_id_unadmitted"],
                {"2102":37,"2103":42,"2104":47,"2105":52})
            self.assertEqual(sum(chosen[
                "selected_gem_raw_points_by_id_unadmitted"].values()),178)
            self.assertTrue(chosen["selected_gem_all_raw_points_known"])
            self.assertTrue(chosen[
                "selected_ordinary_gem_two_stat_budget_eligible_unadmitted"])
            single=adapter.view(
                stage_root=root,v221_candidate_path=path,build=BUILD,
                selected_gem_item_ids=[2101],
                selected_source_gem_item_ids=[2101])
            self.assertTrue(single["selected_gem_all_raw_points_known"])
            self.assertFalse(single[
                "selected_ordinary_gem_two_stat_budget_eligible_unadmitted"])
            self.assertEqual(single[
                "selected_one_stat_gem_activation_only_item_ids"],[2101])
            self.assertEqual(single[
                "selected_gem_raw_points_by_id_unadmitted"],{"2101":25})
            self.assertIsNone(single["J"])
            self.assertIsNone(chosen["J"])
            self.assertFalse(chosen["environment_ready"])
            self.assertNotIn(2106,[d["item_id"] for d in first[
                "four_stat_ordinary_best_observed_unadmitted"].values()])
            self.assertFalse(first[
                "four_stat_effect_or_special_role_reverified"])
            self.assertIsNone(first["selected_special_gem_raw_effect_unadmitted"])
            # A single-stat gem never qualifies for the nominal J default,
            # even if it has a much larger observed stat amount.
            unexcluded=adapter.view(
                stage_root=root,v221_candidate_path=path,build=BUILD)
            self.assertEqual(unexcluded[
                "four_stat_ordinary_best_observed_unadmitted"][
                    "crit_rating"]["item_id"],2105)
            self.assertNotIn(2100,[x["item_id"] for x in unexcluded[
                "four_stat_ordinary_best_observed_unadmitted"].values()])
            with self.assertRaisesRegex(
                    ValueError,"ORDINARY_EXCLUSION_SOURCE_BOUND_ID_REQUIRED"):
                adapter.view(stage_root=root,v221_candidate_path=path,
                             build=BUILD,excluded_ordinary_item_id=2100)
            self.assertIsNone(first["J"])
            self.assertFalse(first["environment_ready"])
            self.assertEqual(first["native_calls"],0)
            self.assertEqual(first["network_calls"],0)

    def test_v819_primary_role_and_mixed_CHMV_source_remain_separate(self):
        # Source fixtures, not current-season real gem measurements.
        links=joined()
        records=list(csv.DictReader(io.StringIO(enchant_csv().decode("utf8"))))
        by_id={int(row["ID"]):row for row in records}
        by_id[501].update(Effect_0="5",EffectArg_0="71",
                          EffectPointsMin_0="0",EffectScalingPoints_0="0.5")
        by_id[502].update(Effect_1="5",EffectArg_1="4",
                          EffectPointsMin_1="10",EffectScalingPoints_1="0")
        by_id[503].update(Effect_1="5",EffectArg_1="7",
                          EffectPointsMin_1="12",EffectScalingPoints_1="0")
        buf=io.StringIO()
        writer=csv.DictWriter(buf,fieldnames=list(source.COLUMNS),lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
        raw=buf.getvalue().encode("utf8")
        class FakeResponse:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,size=-1):return raw
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            adapter.collect(stage_root=root,build=BUILD,
                transport=lambda req,timeout:FakeResponse())
            path=root/"v221.json"
            path.write_text(json.dumps(links),encoding="utf8")
            with patch.object(adapter.join,"preview",wraps=adapter.join.preview) as parse:
                for item,primary,positive in ((2001,True,False),(2002,True,True),
                                               (2003,False,False),(2004,False,False)):
                    result=adapter.view(stage_root=root,v221_candidate_path=path,
                        build=BUILD,selected_source_gem_item_ids=[item],
                        selected_special_gem_item_id=item)
                    self.assertEqual(result["primary_attribute_special_gem_ids_source_only"],
                                     [2001,2002])
                    self.assertEqual(result[
                        "selected_special_gem_primary_role_observed_source_only"],primary)
                    self.assertEqual(result[
                        "selected_special_gem_positive_CHMV_accounting_pending_source_only"],positive)
                    effect=result["selected_special_gem_raw_effect_unadmitted"]
                    self.assertIsNone(effect["raw_static_CHMV_total_candidate_unadmitted"])
                    self.assertFalse(effect["J_budget_attribution_verified"])
                    self.assertFalse(result["environment_ready"])
                    self.assertIsNone(result["J"])
                    self.assertEqual(result["native_calls"],0)
                    self.assertEqual(result["network_calls"],0)
                self.assertEqual(parse.call_count,1)

    def test_v822_actual_v821_special_rank_source_projection(self):
        from runner import v211_enchant_source_effect_classification as classifier
        import copy
        path=Path(__file__).resolve().parents[1]/"docs/development/research_receipts/p1_v821_70961_primary_gem_enchant_compact.json"
        doc=json.loads(path.read_text("utf8"))
        self.assertEqual(doc["status"],"PASS_EXACT_PINNED_SPECIAL_GEM_ENCHANT_ROWS_NOT_ADMITTED")
        rows=doc["candidate_rows"]
        result=classifier.primary_gem_quality_projection(rows)
        self.assertEqual(result["preferred_rank_item_ids_source_only"],
                         [240967,240969,240971,240983])
        self.assertEqual(result["lower_rank_item_ids_source_only"],
                         [240966,240968,240970,240982])
        self.assertEqual(result["unranked_distinct_item_ids"],[241142,241143,241144])
        direct=result["direct_static_CHMV_source_by_item_id"]
        self.assertEqual({int(i) for i,r in direct.items()
                          if r["direct_static_CHMV_vector_source_only"] is not None},
                         {240970,240971,240982,240983})
        pair=json.loads((path.parent/"p1_v826_70961_special_gem_native_pair_compact.json").read_text("utf8"))
        self.assertEqual(pair["status"],"PASS_ACTUAL_SPECIAL_GEM_PROFILE_PAIR_NOT_ADMITTED")
        self.assertEqual(pair["game_build"],doc["game_build"])
        self.assertEqual(pair["simc_revision"],doc["simc_revision"])
        self.assertEqual(pair["native_calls"],2)
        self.assertEqual(direct["240983"]["direct_static_CHMV_vector_source_only"],
                         pair["buffed_CHMV_delta_observed"])
        self.assertIsNone(pair["head_static_CHMV_after"]["mastery_rating"])
        self.assertIsNone(direct["240967"]["direct_static_CHMV_vector_source_only"])
        self.assertFalse(direct["240983"]["effective_runtime_CHMV_verified"])
        mixed=copy.deepcopy(rows)
        mixed[7]["enchant_source_row"]["ench_type"][1]=5
        mixed[7]["enchant_source_row"]["ench_prop"][1]=32
        mixed[7]["enchant_source_row"]["ench_coeff"][1]=0.1
        self.assertIsNone(classifier.primary_gem_quality_projection(mixed)[
            "direct_static_CHMV_source_by_item_id"]["240983"][
                "direct_static_CHMV_vector_source_only"])
        self.assertFalse(result["resolved_numeric_noninferiority_verified"])
        self.assertFalse(result["user_selectable"])
        for key,value in (("ench_prop",[71,999,0]),("min_ilevel",81),
                          ("ench_coeff",[0.1,0,0])):
            altered=copy.deepcopy(rows)
            altered[1]["enchant_source_row"][key]=value
            rejected=classifier.primary_gem_quality_projection(altered)
            self.assertNotIn(240967,rejected["preferred_rank_item_ids_source_only"])
            self.assertTrue({240966,240967}<=set(
                rejected["comparison_pending_item_ids"]))
        drift=copy.deepcopy(rows)
        drift[1]["enchant_source_row"]["id_gem"]=1
        with self.assertRaises(classifier.SourceBlocked):
            classifier.primary_gem_quality_projection(drift)

    def test_v828_original_J_owner_consumes_exact_special_direct_zero(self):
        from runner import v211_enchant_source_effect_classification as classifier
        from runner import v216_environment_build_coordinator as engine
        import copy
        path=Path(__file__).resolve().parents[1]/"docs/development/research_receipts/p1_v821_70961_primary_gem_enchant_compact.json"
        doc=json.loads(path.read_text("utf8"))
        projected=classifier.primary_gem_quality_projection(doc["candidate_rows"])
        build=doc["game_build"]; rev=doc["simc_revision"]
        rank={**projected,"status":"PRIMARY_GEM_RANK_SOURCE_PROJECTED_UNADMITTED",
              "game_build":build,"simc_revision":rev,
              "v221_stage_receipt_sha256":"a"*64,"enchant_source_sha256":"b"*64}
        ids=[11,12,13,14]
        pre={"schema":engine.FRESH_SOURCE_PREFLIGHT_SCHEMA,"environment_ready":False,
             "game_build":build,"simc_revision":rev,
             "source_catalog_manifest_sha256":"c"*64,
             "physical_gem_layout_unadmitted":{"special_gem_id":240983,
                 "ordinary_gem_ids":ids}}
        numeric={"J":{"rating":92,"special_gem_item_id":240983,
             "ordinary_gem_item_ids":ids,
             "per_item_nominal_rating":{str(i):23 for i in ids},
             "v221_stage_receipt_sha256":"a"*64,"source_identity_sha256":"d"*64}}
        quality={"J":{"ordinary_gem_item_ids":ids,
             "v221_stage_receipt_sha256":"a"*64,"v230_stage_receipt_sha256":"e"*64,
             "real_socket_proof_required":True,
             "same_enchant_quality_groups_source_only":[
                 {"observed_item_ids":[i],"comparable_effect_source_only":True,
                  "best_discovered_effect_item_id_source_only":i} for i in ids]}}
        staged={"status":"FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED",
                "stage_status":"REUSED_VERIFIED","stage_receipt_sha256":"f"*64}
        # Synthetic physically supported five-socket case, not actual
        # 70961 representative installation; the source gem rows are real.
        socket={"status":"J_INTRINSIC_COUNTS_BOUND_SOURCE_ONLY",
                "additional_socket_proof_required_by_slot":{},
                "observed_J_unadmitted":92,"v232_stage_receipt_sha256":"1"*64,
                "selected_socket_counts":{"head":1,"neck":2,"finger1":1,"finger2":1}}
        comp={"simc_revision":rev,"primary_gem_rank_source_unadmitted":rank,
              "selected_J_intrinsic_socket_origin_unadmitted":socket}
        def bind(i):
            comp["selected_special_gem_direct_CHMV_source_only"]={
                **rank["direct_static_CHMV_source_by_item_id"][str(i)],
                **{k:rank[k] for k in ("game_build","simc_revision",
                    "v221_stage_receipt_sha256","enchant_source_sha256")},
                "ordinary_J_includes_selected_special":False}
            pre["physical_gem_layout_unadmitted"]["special_gem_id"]=i
            numeric["J"]["special_gem_item_id"]=i
        def admit():
            return engine._fresh_source_owner_original_J_F_components(
                preflight=pre,compilation=comp,staged=staged,
                owner_numeric=numeric,quality_scope=quality,effect_observations=[])
        bind(240983)
        self.assertEqual(admit()["J"]["rating"],92)
        proof=admit()["J"]["source_sha256"]
        bind(240971)
        self.assertNotEqual(admit()["J"]["source_sha256"],proof)
        bind(240967)
        self.assertNotIn("J",admit())
        bind(240983)
        for key,value in (("game_build","12.1.5.0"),("enchant_source_sha256","0"*64),
                          ("direct_static_CHMV_vector_source_only",None),
                          ("item_id",240971)):
            with self.subTest(field=key):
                original=copy.deepcopy(comp["selected_special_gem_direct_CHMV_source_only"])
                comp["selected_special_gem_direct_CHMV_source_only"][key]=value
                self.assertNotIn("J",admit())
                comp["selected_special_gem_direct_CHMV_source_only"]=original
        # The existing additional-socket gate must still reject reachable
        # bonus candidates without actual physical applicability.
        socket["status"]="J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING"
        socket["additional_socket_proof_required_by_slot"]={"head":1}
        self.assertNotIn("J",admit())

    def test_v833_linked_special_pair_preserves_ordinary_gems_and_measures_CHMV(self):
        from runner import v216_environment_build_coordinator as engine
        from runner import v211_enchant_source_effect_classification as classifier
        doc=json.loads((Path(__file__).resolve().parents[1]/
            "docs/development/research_receipts/p1_v821_70961_primary_gem_enchant_compact.json").read_text("utf8"))
        rank=classifier.primary_gem_quality_projection(doc["candidate_rows"])
        self.assertEqual(rank["direct_static_CHMV_source_by_item_id"]["240967"][
            "linked_equip_spell_ids_source_only"],[1258209])
        self.assertIsNone(rank["direct_static_CHMV_source_by_item_id"]["240967"][
            "direct_static_CHMV_vector_source_only"])
        layout={"socket_counts":{"finger1":2,"neck":3},"special_slot":"finger1",
                "special_gem_id":240967,"ordinary_gem_ids":[11,12,13,14]}
        b,a,ordinary=engine._linked_special_gem_pair_profiles(
            "finger1=item,id=1,ilevel=334,bonus_id=3\nneck=item,id=2,ilevel=334\n",layout)
        self.assertEqual(a.replace("240967/",""),b)
        self.assertEqual(ordinary,{"finger1":[11],"neck":[12,13,14]})
        rev=doc["simc_revision"];stats={s:100 for s in engine.season_budget_contract.STATS}
        def raw(profile,delta=0):
            gear={line.split("=",1)[0]:{"encoded_item":line.split("=",1)[1]}
                  for line in profile.splitlines()}
            return json.dumps({"git_revision":rev,"sim":{"players":[{
                "name":"test","gear":gear,"collected_data":{"buffed_stats":{
                    "stats":{**stats,"crit_rating":100+delta}}}}]}}).encode()
        proof=engine._compare_linked_special_gem_static(baseline=raw(b),active=raw(a),
            layout=layout,ordinary_by_slot=ordinary,revision=rev)
        self.assertTrue(proof["static_CHMV_zero"])
        self.assertFalse(engine._compare_linked_special_gem_static(baseline=raw(b),
            active=raw(a,1),layout=layout,ordinary_by_slot=ordinary,revision=rev)["static_CHMV_zero"])
        with self.assertRaises(ValueError):
            engine._compare_linked_special_gem_static(baseline=raw(b),
                active=raw(a.replace("12/13/14","12/13/15")),layout=layout,
                ordinary_by_slot=ordinary,revision=rev)

    def test_v830_actual_bonus_proof_consumed_by_original_J_and_profile(self):
        from runner import v216_environment_build_coordinator as engine
        from runner import v211_enchant_source_effect_classification as classifier
        from runner import v212_environment_manifest as manifest
        from runner import v096_unified_product_entry as entry
        import copy
        root=Path(__file__).resolve().parents[1]/"docs/development/research_receipts"
        actual=json.loads((root/"p1_v829_70961_selected_socket_bonus_compact.json").read_text("utf8"))
        doc=json.loads((root/"p1_v821_70961_primary_gem_enchant_compact.json").read_text("utf8"))
        layout=actual["layout"]; proof=actual["selected_socket_bonus_native"]
        build=actual["game_build"];rev=actual["simc_revision"]
        ids=layout["ordinary_gem_ids"]; special=layout["special_gem_id"]
        rank={**classifier.primary_gem_quality_projection(doc["candidate_rows"]),
              "status":"PRIMARY_GEM_RANK_SOURCE_PROJECTED_UNADMITTED",
              "game_build":build,"simc_revision":rev,
              "v221_stage_receipt_sha256":"a"*64,"enchant_source_sha256":"b"*64}
        source_doc=json.loads((root/"p1_v825_70961_selected_socket_bonus_compact.json").read_text("utf8"))
        rows=source_doc["selected_rows"]
        source={"status":"SAME_BUILD_SELECTED_SOCKET_BONUS_SOURCE_ONLY",
                "game_build":build,"simc_revision":rev,
                "review_receipt_sha256":proof["source_review_sha256"],
                "v232_stage_receipt_sha256":proof["v232_stage_receipt_sha256"],
                "intrinsic_socket_counts_by_slot":{r["slot"]:r["intrinsic_socket_count"] for r in rows},
                "selected_rows":rows}
        pre={"schema":engine.FRESH_SOURCE_PREFLIGHT_SCHEMA,"environment_ready":False,
             "game_build":build,"simc_revision":rev,"source_catalog_manifest_sha256":"c"*64,
             "physical_gem_layout_unadmitted":layout,
             "v277_native_G_preprofile_unadmitted":{"game_build":build,"simc_revision":rev,
                 "target_ilevel":334,"native_json2_sha256":proof["original_G_native_sha256"]}}
        j={"rating":92,"ordinary_gem_item_ids":ids,"special_gem_item_id":special,
           "per_item_nominal_rating":{str(i):23 for i in ids},
           "v221_stage_receipt_sha256":"a"*64,"source_identity_sha256":"d"*64}
        quality={"J":{"ordinary_gem_item_ids":ids,"v221_stage_receipt_sha256":"a"*64,
             "v230_stage_receipt_sha256":"e"*64,"real_socket_proof_required":True,
             "same_enchant_quality_groups_source_only":[]}}
        staged={"status":"FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED",
                "stage_status":"REUSED_VERIFIED","stage_receipt_sha256":"f"*64}
        socket={"status":"J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING",
                "selected_socket_counts":layout["socket_counts"],
                "additional_socket_proof_required_by_slot":{s:1 for s in layout["socket_counts"]},
                "observed_J_unadmitted":92,"v232_stage_receipt_sha256":proof["v232_stage_receipt_sha256"]}
        selected={**rank["direct_static_CHMV_source_by_item_id"][str(special)],
                  **{k:rank[k] for k in ("game_build","simc_revision","v221_stage_receipt_sha256","enchant_source_sha256")},
                  "ordinary_J_includes_selected_special":False}
        comp={"simc_revision":rev,"physical_gem_layout_unadmitted":layout,
              "primary_gem_rank_source_unadmitted":rank,
              "selected_special_gem_direct_CHMV_source_only":selected,
              "selected_J_intrinsic_socket_origin_unadmitted":socket,
              "selected_socket_bonus_native":proof,
              "selected_representative_socket_bonus_source_only":source}
        def admit():
            return engine._fresh_source_owner_original_J_F_components(
                preflight=pre,compilation=comp,staged=staged,owner_numeric={"J":j},
                quality_scope=quality,effect_observations=[])
        scope=admit()["J"]["exact_representative_socket_source"]
        self.assertTrue(manifest.verify_exact_J_socket_source(scope,game_build=build,
            simc_revision=rev,target_ilevel=334,J=92))
        doc={"official_J_physical_socket_source":scope}
        ordinary=iter(ids)
        lines=[]
        for slot,n in sorted(scope["socket_counts"].items()):
            gems=[special] if slot==scope["special_slot"] else []
            gems.extend(next(ordinary) for _ in range(n-len(gems)))
            lines.append(slot+"=item,id="+str(scope["physical_item_ids_by_slot"][slot])+
                ",ilevel=334,bonus_id="+str(scope["source_socket_bonus_by_slot"][slot]["bonus_id"])+
                ",gem_id="+"/".join(map(str,gems)))
        profile="\n".join(lines)
        entry._assert_installed_J_socket_profile(doc=doc,profile=profile)
        for broken in (profile.replace("bonus_id=13668","bonus_id=13695",1),
                       profile.replace("ilevel=334","ilevel=330",1),
                       profile.replace("gem_id="+str(special),"gem_id=1",1)):
            with self.assertRaises(ValueError):
                entry._assert_installed_J_socket_profile(doc=doc,profile=broken)
        for key,value in (("active_native_sha256","bad"),("original_G_native_sha256","0"*64),
                          ("bonus_plan",{}),("game_build","12.1.5.0")):
            comp["selected_socket_bonus_native"]={**proof,key:value}
            self.assertNotIn("J",admit())
        comp["selected_socket_bonus_native"]=proof
        rank["preferred_rank_item_ids_source_only"]=[]
        self.assertNotIn("J",admit())

    def test_same_build_source_and_scaling_schema_must_be_explicit(self):
        with self.assertRaisesRegex(source.EnchantSourceBlocked,
                                    "EXACT_SAME_BUILD"):
            source.preview(gem_join=joined(game_build="12.1.5.70574"),
                           raw_enchant_csv=enchant_csv(),
                           expected_game_build=BUILD)
        data=enchant_csv().replace(b"EffectScalingPoints_0",
                                  b"UnknownScaling_0",1)
        with self.assertRaisesRegex(source.EnchantSourceBlocked,
                                    "STATIC_COLUMNS_MISSING"):
            source.preview(gem_join=joined(),raw_enchant_csv=data,
                           expected_game_build=BUILD)

    def test_selected_gem_change_reuses_verified_full_join_once(self):
        """One CSV parse per unchanged source, not per user gem selection."""
        raw=enchant_csv()
        class FakeResponse:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,size=-1):return raw
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            adapter.collect(stage_root=root,build=BUILD,
                transport=lambda request,timeout:FakeResponse())
            source_path=root/"v221.json"
            source_path.write_text(json.dumps(joined()),encoding="utf8")
            original=adapter.join.preview
            with patch.object(adapter.join,"preview",wraps=original) as parse:
                first=adapter.view(stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2001],
                    selected_source_gem_item_ids=[2001,2002])
                second=adapter.view(stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2002,2003],
                    selected_source_gem_item_ids=[2002,2003])
                self.assertEqual(parse.call_count,1)
                receipts=list((root/".stage_receipts").glob(
                    "fresh-v266-gem-enchant-join-*.json"))
                self.assertEqual(len(receipts),1)
                self.assertEqual(json.loads(receipts[0].read_text("utf8"))[
                    "status"],"COMPLETE")
                self.assertEqual(first[
                    "selected_gem_raw_points_by_id_unadmitted"],{"2001":25})
                self.assertEqual(second[
                    "selected_gem_unresolved_item_ids"],[2002,2003])
                self.assertTrue(second[
                    "selected_gem_v221_same_build_items_all_present"])
                # Mandatory special gem is projected from the SAME cached
                # join; its nonstatic effect is NOT a proved zero J.
                unknown_special=adapter.view(
                    stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2001],
                    selected_source_gem_item_ids=[2001,2003],
                    selected_special_gem_item_id=2003)
                self.assertEqual(parse.call_count,1)
                unknown=unknown_special[
                    "selected_special_gem_raw_effect_unadmitted"]
                self.assertEqual(unknown["item_id"],2003)
                self.assertIsNone(unknown[
                    "raw_static_CHMV_total_candidate_unadmitted"])
                self.assertTrue(unknown[
                    "missing_or_nonstatic_never_assumed_zero"])
                observed_special=adapter.view(
                    stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2003],
                    selected_source_gem_item_ids=[2001,2003],
                    selected_special_gem_item_id=2001)
                self.assertEqual(parse.call_count,1)
                static=observed_special[
                    "selected_special_gem_raw_effect_unadmitted"]
                self.assertEqual(static[
                    "raw_static_CHMV_total_candidate_unadmitted"],25)
                self.assertEqual(static[
                    "raw_static_CHMV_vector_candidate_unadmitted"][
                    "crit_rating"],25)
                self.assertFalse(static["J_budget_attribution_verified"])
                self.assertTrue(observed_special[
                    "selected_special_gem_positive_CHMV_accounting_pending_source_only"])
                self.assertFalse(unknown_special[
                    "selected_special_gem_positive_CHMV_accounting_pending_source_only"])
                self.assertIsNone(unknown["raw_static_CHMV_total_candidate_unadmitted"])
                with self.assertRaisesRegex(ValueError,
                        "V268_SPECIAL_GEM_MUST_BE_SOURCE_BOUND_AND_DISTINCT"):
                    adapter.view(
                        stage_root=root,v221_candidate_path=source_path,
                        build=BUILD,selected_gem_item_ids=[2001],
                        selected_source_gem_item_ids=[2001,2003],
                        selected_special_gem_item_id=2001)
                self.assertFalse(second["environment_ready"])
                # Unscoped legacy gem layouts remain ordinary-only previews:
                # the new source-bound special argument is not mandatory.
                legacy=adapter.view(
                    stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2001])
                self.assertEqual(parse.call_count,1)
                self.assertIsNone(legacy[
                    "selected_special_gem_raw_effect_unadmitted"])
                self.assertEqual(legacy[
                    "selected_gem_raw_points_by_id_unadmitted"],{"2001":25})
                self.assertFalse(second["highest_quality_J_verified"])
                # A new v221 artifact identity MUST miss the old cache.
                modified=joined()
                modified["source_annotation"]="changed_original_bytes"
                source_path.write_text(json.dumps(modified),encoding="utf8")
                third=adapter.view(stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2001])
                self.assertEqual(parse.call_count,2)
                self.assertEqual(len(list((root/".stage_receipts").glob(
                    "fresh-v266-gem-enchant-join-*.json"))),2)
                # The original exact bytes should hit their previous receipt.
                source_path.write_text(json.dumps(joined()),encoding="utf8")
                fourth=adapter.view(stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2001])
                self.assertEqual(parse.call_count,2)
                self.assertEqual(len(list((root/".stage_receipts").glob(
                    "fresh-v266-gem-enchant-join-*.json"))),2)
                # Even a known-good cache cannot hide a modified CSV.
                csvpath=root/adapter.OUTPUTS["csv"]
                csvpath.write_bytes(raw+b"\n")
                drift=adapter.view(stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2001])
                self.assertEqual(drift["status"],"GEM_ENCHANT_LOCAL_JOIN_PENDING")
                self.assertEqual(drift["reason"],"V268_SEALED_CSV_BYTES_CHANGED")
                self.assertEqual(parse.call_count,2)
                # A tampered cached join is rejected by the existing v217
                # output hash, never used as a fresh product J or UI choice.
                csvpath.write_bytes(raw)
                joined_outputs=list((root/"fresh_source").glob(
                    "v266_exact_gem_enchant_join_*.json"))
                self.assertEqual(len(joined_outputs),2)
                for original_json in joined_outputs:
                    original_json.write_text("{}\n",encoding="utf8")
                invalid=adapter.view(
                    stage_root=root,v221_candidate_path=source_path,
                    build=BUILD,selected_gem_item_ids=[2001])
                self.assertEqual(invalid["status"],"GEM_ENCHANT_LOCAL_JOIN_PENDING")
                self.assertIn("STAGE_OUTPUT_HASH_MISMATCH",invalid["reason"])

    def test_single_fetch_replays_local_and_rejects_changed_csv(self):
        raw=enchant_csv()
        calls=[]
        class FakeResponse:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,size=-1):return raw
        def fetch(request,timeout):
            calls.append((request.full_url,timeout))
            return FakeResponse()
        def fail(request,timeout):
            raise AssertionError("a cached CSV must never refetch")
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            first=adapter.collect(stage_root=root,build=BUILD,
                                  transport=fetch)
            second=adapter.collect(stage_root=root,build=BUILD,
                                   transport=fail)
            self.assertEqual((first["network_calls_by_stage"],
                              second["network_calls_by_stage"]),(1,0))
            self.assertEqual(len(calls),1)
            self.assertIn("SpellItemEnchantment",calls[0][0])
            self.assertEqual(second["status"],"GEM_ENCHANT_CSV_SOURCE_SEALED")
            p=root/"v221.json"
            p.write_text(json.dumps(joined()),encoding="utf8")
            status=adapter.view(stage_root=root,v221_candidate_path=p,
                                build=BUILD,
                                selected_gem_item_ids=[2001,2001,2002,2004])
            self.assertEqual(status["selected_gem_raw_points_by_id_unadmitted"],
                             {"2001":25})
            self.assertEqual(
                status["selected_gem_raw_CHMV_vectors_by_id_unadmitted"],
                {"2001":{"crit_rating":25,"haste_rating":0,
                         "mastery_rating":0,"versatility_rating":0}})
            self.assertEqual(status["selected_gem_unresolved_item_ids"],
                             [2002,2004])
            self.assertFalse(status["selected_gem_all_raw_points_known"])
            self.assertTrue(status["selected_gem_raw_points_not_native_verified"])
            only=adapter.view(stage_root=root,v221_candidate_path=p,
                              build=BUILD,selected_gem_item_ids=[2001]*6)
            self.assertTrue(only["selected_gem_all_raw_points_known"])
            self.assertEqual(only["selected_gem_raw_points_by_id_unadmitted"],
                             {"2001":25})
            source_bound=adapter.view(
                stage_root=root,v221_candidate_path=p,build=BUILD,
                selected_gem_item_ids=[2001]*2,
                selected_source_gem_item_ids=[2001,2003])
            self.assertEqual(source_bound[
                "selected_gem_v221_item_ids_unadmitted"],[2001,2003])
            self.assertTrue(source_bound[
                "selected_gem_v221_same_build_items_all_present"])
            self.assertTrue(source_bound["selected_gem_v221_source_only"])
            self.assertTrue(source_bound[
                "selected_gem_v221_source_properties_complete"])
            props=source_bound["selected_gem_v221_source_properties_unadmitted"]
            self.assertEqual([p["item_id"] for p in props],[2001,2003])
            self.assertEqual(props[1]["minimum_ilevel"],345)
            self.assertEqual(props[1]["color_mask"],1)
            self.assertEqual(props[1]["gem_property_id"],13)
            self.assertEqual(len(props),2)
            # 2003 has non-static effects: source ID exists but its
            # SimC effect, specialness and rating remain unverified.
            self.assertEqual(source_bound[
                "selected_gem_raw_points_by_id_unadmitted"],{"2001":25})
            missing=adapter.view(
                stage_root=root,v221_candidate_path=p,build=BUILD,
                selected_source_gem_item_ids=[2001,999999])
            self.assertFalse(missing[
                "selected_gem_v221_same_build_items_all_present"])
            self.assertEqual(missing["selected_gem_v221_missing_item_ids"],
                             [999999])
            self.assertFalse(missing[
                "selected_gem_v221_source_properties_complete"])
            self.assertEqual(len(missing[
                "selected_gem_v221_source_properties_unadmitted"]),1)
            self.assertIsNone(only["J"])
            self.assertEqual(status["raw_static_candidate_count"],1)
            self.assertEqual(status["unresolved_enchant_count"],3)
            self.assertIsNone(status["J"])
            self.assertFalse(status["highest_quality_J_verified"])
            self.assertEqual(status["network_calls"],0)
            csvpath=root/adapter.OUTPUTS["csv"]
            csvpath.write_bytes(raw+b"\n")
            drift=adapter.view(stage_root=root,v221_candidate_path=p,
                               build=BUILD)
            self.assertEqual(drift["status"],"GEM_ENCHANT_LOCAL_JOIN_PENDING")
            self.assertEqual(drift["reason"],"V268_SEALED_CSV_BYTES_CHANGED")


if __name__=="__main__":
    unittest.main()
