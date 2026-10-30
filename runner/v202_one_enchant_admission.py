#!/usr/bin/env python3
"""v202 one exact Native-evidenced enchant E for opt-in developer sessions.

Not a new effect/proc evaluator or general-purpose item authorization. This
pin is deliberately Linux binary + Frost-334 + identical ring item + exact
enchant. Windows and every other enchant stay unpromoted until their scope
has equivalent Native evidence. Existing normal user controls are unchanged.
"""
from __future__ import annotations
import hashlib,json,pathlib,re
import v197_verified_effect_budget as fixed

DEFAULT=pathlib.Path(__file__).resolve().parents[1]/"data/v202_verified_enchant_8025_source.json"
CHOICE={"finger1":8025}
# Full source profile SHA of the completed v203 six-Native Frost334 sample,
# after exactly one oil application. Character/talents/trinkets/consumables/
# fight conditions/other gear must be byte-identical in this developer pilot.
# Do not extrapolate one Native ring effect to arbitrary user loadouts.
EXACT_SOURCE_PROFILE_SHA256="8305a811137db6f557f8076dfa44a4a1a359111d60bb7452225e1573bf72a401"
SCHEMA="v202_one_exact_enchant_source_evidence_v1"
# SHA-confirmed v200/v201 raw Native JSON2, not just four plausible hex strings.
EXPECTED_NATIVE_JSON_SHA={
    "v200_before_native_sha256": "6fdbb14ec3404ab59dc95d3078c58811d0323810e74cc8cf2b647cd7e27557d5",
    "v200_after_native_sha256": "63d47320423ff75969d7d4c2302ced854d6ceb0dfba254572e4cc2d91cd08e2d",
    "v201_before_native_sha256": "29228e6fb402952f90a4b62a9bcd193133eb5386f7469ab01c28dd6b37e04973",
    "v201_after_native_sha256": "2f25c842207dd67aa9c02345798d24468649c895c12fb45a8bf6d5f1ef1112d0"
}
class EnchantAdmissionBlocked(ValueError):pass
def need(ok,code):
    if not ok:raise EnchantAdmissionBlocked(code)
def read():
    raw=DEFAULT.read_bytes()
    data=json.loads(raw)
    need(data.get("schema")==SCHEMA and
         data.get("status")=="VERIFIED_IN_TWO_NATIVE_PAIR_PROFILES_NOT_UI_PROMOTED"
         and data.get("slot")=="finger1" and data.get("enchant_id")==8025
         and data.get("ring_item_id")==158366 and data.get("source_ilvl")==334
         and data.get("source_spec")=="mage/frost"
         and data.get("revision")=="710c2408bfd3ae4df71b8cd55cdf01f63fd6c926"
         and data.get("linux_binary_sha256")==
             "f105b8a34fd911c340e735f0440e0d1eadf0d0dbc25f18923c048810cf69095d"
         and data.get("static_enchant_E")==
             {"crit_rating":0,"haste_rating":30,"mastery_rating":0,"versatility_rating":0}
         and data.get("v200_reconcile_run")==41076597270
         and data.get("v201_gear_override_native_run")==41078102843
         and data.get("v201_same_override_rating_delta")==
             {"crit_rating":0,"haste_rating":0,"mastery_rating":0,"versatility_rating":0}
         and data.get("product_ui_selectable") is False,
         "PINNED_NATIVE_ENCHANT_EVIDENCE_DRIFT")
    need(all(data.get(k)==v for k,v in EXPECTED_NATIVE_JSON_SHA.items())
         and data.get("v199_artifact_id")==12986044543
         and data.get("v200_artifact_id")==12987312399
         and data.get("v201_artifact_id")==12988042331,
         "PINNED_NATIVE_EVIDENCE_BYTES_OR_ARTIFACT_DRIFT")
    return data,hashlib.sha256(raw).hexdigest()
def reject_selected_L_overlap(user,need_user):
    """E is already inside G; one selected special/crafted slot must not lock it twice."""
    need_user(type(user) is dict and
              not any(r.get("slot")=="finger1"
                      for group in ("special_items","embellishments")
                      for r in user.get(group,[])),
              "V203_ENCHANT_E_OVERLAPS_SELECTED_L_OR_CRAFTED_SLOT")

def apply_verified_ring(rows,user_choice,key,ilevel,need_user):
    """Mutate only one generated internal representative item option."""
    need_user(type(user_choice) is dict and user_choice==CHOICE,
              "V202_ONE_PINNED_DEVELOPER_ENCHANT_CHOICE_ONLY")
    need_user(key==("mage","frost") and ilevel==334,
              "V202_ONLY_NATIVE_WITNESSED_MAGE_FROST_334")
    r=rows.get("finger1")
    need_user(type(r) is dict and r.get("item_id")==158366 and
              r.get("ilevel")==334 and type(r.get("options")) is dict,
              "V202_PINNED_FINGER1_GEAR_ITEM_NOT_PRESENT")
    opts=r["options"]
    need_user("enchant" not in opts and
              "enchant_id" not in opts,
              "V202_WOULD_OVERWRITE_PREEXISTING_ENCHANT")
    # Fail before mutating source gear when the Native proof is absent,
    # stale or tampered. Keep caller data untouched on failed admission.
    verified,_=read()
    opts["enchant_id"]="8025"
    return dict(verified["static_enchant_E"])
def admit(manifest_choice,profile,normalized,binary_sha,revision):
    need(type(manifest_choice) is dict and manifest_choice==CHOICE,
         "V202_DEVELOPER_ONLY_EXACT_CHOICE")
    data,digest=read()
    ch=normalized["scenario"]["character"]
    need((ch["class"],ch["spec"])==("mage","frost") and
         normalized["scenario"]["target"]["ilevel"]==334,
         "V202_SOURCE_SPEC_OR_ILVL_NOT_EVIDENCED")
    need(binary_sha==data["linux_binary_sha256"] and
         type(revision) is str and len(revision)>=7 and
         data["revision"].startswith(revision),
         "V202_ONLY_PINNED_LINUX_SIMC_BINARY_AND_REVISION")
    need(type(profile) is str and
         hashlib.sha256(profile.encode("utf8")).hexdigest()==EXACT_SOURCE_PROFILE_SHA256,
         "V203_FULL_PROFILE_TALENTS_CONSUMABLES_GEAR_COMBAT_SHA_NOT_EVIDENCED")
    ring=[s.partition("=")[2] for s in profile.splitlines()
          if s.startswith("finger1=")]
    need(len(ring)==1,"V202_EXACT_ONE_FINGER1_ROW")
    parts=ring[0].split(",")
    need(sum(x=="id=158366" for x in parts)==1
         and sum(x=="ilevel=334" for x in parts)==1
         and sum(x=="enchant_id=8025" for x in parts)==1
         and not any(x.startswith("enchant=") for x in parts),
         "V202_PINNED_ITEM_ENCHANT_ID_ILVL_NOT_IN_PROFILE")
    E=fixed.vector(data["static_enchant_E"],"VERIFIED_ENCHANT_E")
    return {"schema":SCHEMA,"choice":dict(CHOICE),"fixed_E":E,
            "evidence_sha256":digest,"v200_run":data["v200_reconcile_run"],
            "v201_run":data["v201_gear_override_native_run"],
            "gear_override_does_not_add_E_twice":True}
