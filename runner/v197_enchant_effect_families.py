#!/usr/bin/env python3
"""v197: one source-indexed, same-effect grouping for Midnight ring enchants.

Strong-vs-ordinary is an advisory item-effect comparison, not proof of exact
Native static CHMV or permission to turn on a user equipment enchant.
Different effects stay separate (e.g. crit rating != crit effectiveness).
Source-based quality rank was already reduced by v191; DO NOT conflate the
two independent dimensions 'item rank' and 'effect magnitude'.
"""
from __future__ import annotations

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

def decorate(enchant_rows):
    if type(enchant_rows) is not list:
        raise ValueError("ENCHANT_ROWS_INVALID")
    result=[];observed=set()
    for row in enchant_rows:
        token=row.get("token")
        if type(token) is not str or "__" not in token:
            raise ValueError("ENCHANT_TOKEN_INVALID")
        prefix,name=token.split("__",1)
        if token in observed:raise ValueError("ENCHANT_TOKEN_DUPLICATE")
        observed.add(token)
        data=dict(row)
        data["display_name"]="Enchant "+prefix.replace("enchant_","").title()+
            " — "+name.replace("_"," ").title()
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
        result.append(data)
    observed_ring={x.split("__",1)[1] for x in observed
                   if x.startswith("enchant_ring__")}
    if observed_ring!=set(RING_EFFECTS):
        raise ValueError("RING_SOURCE_EFFECT_FAMILIES_INCOMPLETE")
    return result
