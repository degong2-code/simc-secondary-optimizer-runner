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
            for x in rows)!=1):
        raise ValueError("V211_SOURCE_CLASSIFICATION_SCOPE_DRIFT")
    return result

def decorate(enchant_rows):
    if type(enchant_rows) is not list:
        raise ValueError("ENCHANT_ROWS_INVALID")
    source_rows=read_source_classification()
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
        if source_rows is not None:
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
        else:
            data["source_effect_classification_status"]="SOURCE_MANIFEST_UNAVAILABLE"
        result.append(data)
    observed_ring={x.split("__",1)[1] for x in observed
                   if x.startswith("enchant_ring__")}
    if observed_ring!=set(RING_EFFECTS):
        raise ValueError("RING_SOURCE_EFFECT_FAMILIES_INCOMPLETE")
    return result
