#!/usr/bin/env python3
"""v197: one source-indexed, same-effect grouping for Midnight ring enchants.

Strong-vs-ordinary is an advisory item-effect comparison, not proof of exact
Native static CHMV or permission to turn on a user equipment enchant.
Different effects stay separate (e.g. crit rating != crit effectiveness).
Source-based quality rank was already reduced by v191; DO NOT conflate the
two independent dimensions 'item rank' and 'effect magnitude'.
"""
from __future__ import annotations
import json
from pathlib import Path

# Two independently documented ring families have improved variants in
# the *same* chosen rating type. This does not certify SimC's numeric stat
# projection inside gear_* overrides. Current game database has all nine.
RING_EFFECTS={
 "amani_mastery":("mastery_rating","regular"),
 "zuljins_mastery":("mastery_rating","stronger"),
 "thalassian_haste":("haste_rating","regular"),
 "silvermoons_alacrity":("haste_rating","stronger"),
 "thalassian_versatility":("versatility_rating","regular"),
 "silvermoons_tenacity":("versatility_rating","stronger"),
 "natures_wrath":("crit_rating","regular"),
 "natures_fury":("crit_rating","stronger"),
 "eyes_of_the_eagle":("crit_effectiveness","distinct"),
}
SOURCE_REFERENCES=(
    "https://www.wow-professions.com/midnight/enchanting-specialization-guide-and-builds",
    "https://www.wowhead.com/spell=1236088/enchant-ring-silvermoons-alacrity",
    "https://www.wowhead.com/spell=1236074/enchant-ring-natures-fury",
    "https://www.wowhead.com/spell=1236060/enchant-ring-zuljins-mastery",
    "https://www.wowhead.com/spell=1236089/enchant-ring-silvermoons-tenacity",
)
EFFECT_NAMES={
 "crit_rating":"치명타 rating 증가",
 "haste_rating":"가속 rating 증가",
 "mastery_rating":"특화 rating 증가",
 "versatility_rating":"유연성 rating 증가",
 "crit_effectiveness":"치명타 효과 강화 (치명타 rating 증가와 별개)",
}
SOURCE_CLASSIFICATION_PATH=(
    Path(__file__).resolve().parents[1]/
    "data/current_season_enchant_effect_classification.json")
SOURCE_CLASSIFICATION_SCHEMA="v211_current_season_enchant_effect_classification_v1"
SOURCE_SIMC_COMMIT="710c2408bfd3ae4df71b8cd55cdf01f63fd6c926"
SOURCE_FILE_PINS={
 "data_enums.hh":(75791,"23e5af4d5c407aef6092225030019757c9fa3354",
                  "25a88c629f3d4ebb4ac966f3927307b28f756cf9cef9482dc77a79b197873ea4"),
 "enchants.cpp":(19322,"4876fc816c275844ad6da9be3ca026cdb4a52090",
                 "e4b4cb85c4f74896f3a330d3932aaa5e32b67a1ab7f48d0fd8b9f0fa2fb92ff0"),
 "permanent_enchant.inc":(86347,"2321ad985ab4ee960a5a3a80d41b25db9fb2b8af",
                          "1d836f16acfa812c9fe39fe30185910595c6b813c9e8c2c87691bc2c47fd586a"),
 "spell_item_enchantment.inc":(1093702,"7262db77d57d3c041a561de4d3d404431685a7ff",
                               "dad56ceec265431ea9abbca80f6ce426bf316ac3d0ba12dce80ed6d28701f080"),
 "spelltext_data.inc":(3971792,"0197c596fd5dfddbe04a1d7284ec9025d51d3bf3",
                       "f4f124ff41b13f18512c7b10ef56b9a5f744150938b3d37b9528ed4d51d09f23"),
 "unique_gear_midnight.cpp":(243844,"9bb01bff903f22c3332f9cb6464ed72c0cae27ea",
                             "80393730af429f225610a0c65399c65289117eccc9faaaa63ba685a72e0d4987")
}
SIMC_ITEM_ENCHANT_PIPELINE={
 "static_stat_path":"ITEM_ENCHANTMENT_STAT",
 "spell_effect_path":"ITEM_ENCHANTMENT_EQUIP_SPELL",
 "passive_spell_path":"passive_enchant",
 "owner":"SIMC","source_file":"engine/item/enchants.cpp"
}

def read_source_classification(path=SOURCE_CLASSIFICATION_PATH):
    """Read compact source classification; never turns source facts into E proof."""
    path=Path(path)
    if not path.is_file():
        return None
    doc=json.loads(path.read_text("utf8"))
    if (doc.get("schema")!=SOURCE_CLASSIFICATION_SCHEMA or
        doc.get("status")!="SOURCE_CLASSIFIED_NOT_GENERAL_NATIVE_ACCEPTANCE_OR_UI_PROMOTION" or
        doc.get("simc_commit")!=SOURCE_SIMC_COMMIT or
        doc.get("season_game_build")!="12.1.5.70575" or
        doc.get("counts")!={"total":38,"static_chmv_rating":8,
          "static_nonchmv_only_or_mixed":19,"spell_effects":15,
          "native_E_measured":2,"user_selectable_existing_scope":1,
          "developer_only_exact_scope":1,"locked":36} or
        doc.get("candidate_source_artifact_id")!=12961140046 or
        doc.get("simc_item_enchant_pipeline")!=SIMC_ITEM_ENCHANT_PIPELINE or
        type(doc.get("source_files")) is not dict or
        set(doc["source_files"])!=set(SOURCE_FILE_PINS) or
        any((doc["source_files"][k].get("size_bytes"),
             doc["source_files"][k].get("git_blob_sha1"),
             doc["source_files"][k].get("sha256"))!=SOURCE_FILE_PINS[k]
            for k in SOURCE_FILE_PINS) or
        doc.get("native_calls")!=0 or doc.get("automatic_ui_promotion") is not False or
        doc.get("simc_effect_reimplemented") is not False):
        raise ValueError("V211_SOURCE_CLASSIFICATION_PROVENANCE_INVALID")
    rows=doc.get("rows")
    if type(rows) is not list or len(rows)!=38:
        raise ValueError("V211_SOURCE_CLASSIFICATION_ROW_COUNT_INVALID")
    result={}
    for row in rows:
        if (type(row) is not dict or type(row.get("token")) is not str or
            type(row.get("enchant_id")) is not int or row["token"] in result or
            type(row.get("static_components")) is not list or
            type(row.get("driver_spell_ids")) is not list or
            type(row.get("simc_custom_handlers")) is not list or
            row.get("simc_effect_owner")!="SIMC" or
            row.get("simc_effect_reimplemented") is not False):
            raise ValueError("V211_SOURCE_CLASSIFICATION_ROW_INVALID")
        result[row["token"]]=row
    if (sum(bool(x["static_chmv_rating_present"]) for x in rows)!=8 or
        sum(x["selection_status"]=="EXISTING_EAGLE_ONE_SCOPE_USER_CHOICE"
            for x in rows)!=1 or
        sum(x["selection_status"]=="DEVELOPER_ONLY_EXACT_SCOPE"
            for x in rows)!=1 or
        sum(bool(x["driver_spell_ids"]) for x in rows)!=15):
        raise ValueError("V211_SOURCE_CLASSIFICATION_SCOPE_DRIFT")
    by_id={x["enchant_id"]:x for x in rows}
    zero={"crit_rating":0,"haste_rating":0,"mastery_rating":0,"versatility_rating":0}
    if (by_id.get(7967,{}).get("native_E_status")!=
        "MEASURED_ZERO_ONE_WINDOWS_PALADIN_334_PROFILE" or
        by_id.get(7967,{}).get("native_E")!=zero or
        by_id.get(7967,{}).get("selection_status")!=
        "EXISTING_EAGLE_ONE_SCOPE_USER_CHOICE" or
        by_id.get(8025,{}).get("native_E_status")!=
        "MEASURED_ONE_LINUX_FROST_334_PROFILE" or
        by_id.get(8025,{}).get("native_E")!={"crit_rating":0,"haste_rating":30,
            "mastery_rating":0,"versatility_rating":0} or
        by_id.get(8025,{}).get("selection_status")!="DEVELOPER_ONLY_EXACT_SCOPE"):
        raise ValueError("V211_SOURCE_NATIVE_E_SCOPE_OR_SELECTION_DRIFT")
    if any(x["dynamic_chmv_proc_present"] for x in rows
           if x["static_chmv_rating_present"]):
        raise ValueError("V211_STATIC_RING_RATING_MISLABELED_AS_DYNAMIC_PROC")
    return result

def compact_classification_rows(rows):
    """Normalize full v211 compiler rows to the existing v197 read model."""
    if type(rows) is not list:
        raise ValueError("V211_CLASSIFICATION_ROWS_INVALID")
    result={}
    for row in rows:
        token=row.get("token") if type(row) is dict else None
        eid=row.get("enchant_id") if type(row) is dict else None
        if type(token) is not str or type(eid) is not int or token in result:
            raise ValueError("V211_CLASSIFICATION_ROW_IDENTITY_INVALID")
        native=row.get("native_E_evidence",{})
        if type(native) is not dict:
            raise ValueError("V211_CLASSIFICATION_NATIVE_E_INVALID")
        spells=row.get("spell_effects",[])
        static=row.get("static_components",[])
        if type(spells) is not list or type(static) is not list:
            raise ValueError("V211_CLASSIFICATION_COMPONENTS_INVALID")
        result[token]={
          "token":token,"enchant_id":eid,
          "static_components":[x.get("item_mod") for x in static
                               if type(x) is dict and x.get("item_mod")],
          "driver_spell_ids":[x.get("driver_spell_id") for x in spells
                              if type(x) is dict and
                              type(x.get("driver_spell_id")) is int],
          "simc_custom_handlers":list(row.get("simc_custom_handlers",[])),
          "simc_effect_owner":row.get("simc_effect_owner"),
          "simc_effect_reimplemented":row.get("simc_effect_reimplemented"),
          "static_chmv_rating_present":row.get("static_chmv_rating_present_in_dbc"),
          "static_chmv_stats":list(row.get("static_chmv_stats",[])),
          "dynamic_chmv_proc_present":row.get("dynamic_chmv_proc_present_in_spell_text"),
          "dynamic_chmv_proc_roles":list(row.get("dynamic_chmv_proc_roles",[])),
          "native_E_status":native.get("status"),
          "native_E":native.get("static_E"),
          "selection_status":row.get("selection_status"),
          "effect_family":row.get("effect_family"),
          "effect_summary":row.get("effect_summary")
        }
    if len(result)!=38:
        raise ValueError("V211_CLASSIFICATION_ROW_COUNT_INVALID")
    return result

def decorate(enchant_rows, source_classification_rows=None):
    if type(enchant_rows) is not list:
        raise ValueError("ENCHANT_ROWS_INVALID")
    source_rows=(read_source_classification() if source_classification_rows is None
                 else compact_classification_rows(source_classification_rows))
    result=[];observed=set()
    for row in enchant_rows:
        token=row.get("token")
        if type(token) is not str or "__" not in token:
            raise ValueError("ENCHANT_TOKEN_INVALID")
        prefix,name=token.split("__",1)
        if token in observed:raise ValueError("ENCHANT_TOKEN_DUPLICATE")
        observed.add(token)
        data=dict(row)
        data["display_name"]=("Enchant "+prefix.replace("enchant_","").title()+
                              " — "+name.replace("_"," ").title())
        data["effect_family"]="UNRESOLVED_FROM_CURRENT_SIMC_GENERATED_ROW"
        data["effect_description"]="효과 종류·정적 rating은 추가 원본 연결 필요"
        data["superseded_by_stronger_same_effect"]=False
        data["preferred_if_same_effect_source"]="UNKNOWN_NOT_DEDUPED"
        data["simc_static_rating_verified"]=False
        if prefix=="enchant_ring":
            if name not in RING_EFFECTS:
                raise ValueError("CURRENT_SEASON_RING_EFFECT_FAMILY_UNEXPECTED")
            family,strength=RING_EFFECTS[name]
            data["effect_family"]=family
            data["effect_description"]=EFFECT_NAMES[family]
            data["superseded_by_stronger_same_effect"]=strength=="regular"
            data["preferred_if_same_effect_source"]=(
                "STRONGER_VARIANT_REPORTED" if strength=="stronger" else
                "DISTINCT_EFFECT_NO_DOMINANCE" if strength=="distinct" else
                "WEAKER_VARIANT_REPORTED")
        if source_rows is not None and "enchant_id" in row:
            source=source_rows.get(token)
            if source is None or source["enchant_id"]!=row.get("enchant_id"):
                raise ValueError("V211_ENCHANT_SOURCE_CLASSIFICATION_IDENTITY_MISMATCH")
            data["source_effect_classification"]=dict(source)
            data["source_effect_classification_status"]=(
                "PINNED_SIMC_DBC_SPELLTEXT_AND_HANDLER_SOURCE_CLASSIFIED")
            data["source_effect_family"]=source["effect_family"]
            data["source_effect_description"]=source["effect_summary"]
            data["source_static_chmv_rating_present"]=source["static_chmv_rating_present"]
            data["source_static_chmv_stats"]=list(source["static_chmv_stats"])
            data["source_dynamic_chmv_proc_roles"]=list(source["dynamic_chmv_proc_roles"])
            data["source_native_E_status"]=source["native_E_status"]
            data["source_native_E_one_scope"]=(
                dict(source["native_E"]) if source["native_E"] is not None else None)
            data["source_simc_custom_handlers"]=list(source["simc_custom_handlers"])
            data["source_driver_spell_ids"]=list(source["driver_spell_ids"])
            # Source classification is not itself an exact Native acceptance.
            data["simc_static_rating_verified"]=False
            if prefix!="enchant_ring":
                data["effect_family"]=source["effect_family"]
                data["effect_description"]=source["effect_summary"]
        elif source_rows is None:
            data["source_effect_classification_status"]="SOURCE_MANIFEST_UNAVAILABLE"
        else:
            data["source_effect_classification_status"]="SOURCE_IDENTITY_NOT_SUPPLIED_FOR_PARTIAL_TEST_ROW"
        result.append(data)
    observed_ring={x.split("__",1)[1] for x in observed
                   if x.startswith("enchant_ring__")}
    if observed_ring!=set(RING_EFFECTS):
        raise ValueError("RING_SOURCE_EFFECT_FAMILIES_INCOMPLETE")
    return result
