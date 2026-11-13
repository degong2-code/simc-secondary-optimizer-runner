#!/usr/bin/env python3
"""v106 Windows user-session controller around existing v098 -> v096 -> v094.

No optimizer, native parser, item database or new SimC mechanics. User inputs
only. Session identity is tied to canonical user controls, actual binary SHA,
revision and optional exact static-cache bytes. The SAME key resumes cached
Native calls; changed settings always create a different session.
"""
from __future__ import annotations
import argparse, contextlib, functools, hashlib, json, os, pathlib, re, sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import v098_target_user_scenario_bootstrap as bootstrap
import v108_native_consumable_inputs as consumer
import v206_nonchmv_eagle_selection as nonchmv_enchant
import v213_source_to_catalog as source_catalog_bridge
import v218_v098_profile_stage_adapter as profile_stage

SCHEMA="v106_dps_user_session_v1"
DEFAULT_ROOT=pathlib.Path.home()/"SIMC_Secondary_Optimizer"/"runs"
SUPPORTED=tuple(sorted(set(bootstrap.ARCHETYPES)|bootstrap.PURE_PRODUCT_SPECS))
# User-editable starter talents from the already verified v140 Windows
# source-free inputs; not a runtime dependency on official full SimC profiles.
PURE_STARTERS={
    ("druid","balance"):("night_elf","CYGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWoMbNjxMDwsYmZmZhBjZZmlZYmZswyMLzMGzshhBYstMzgxsNCMBAAAYxMzMzgNDjxAAwMDMA"),
    ("evoker","devastation"):("dracthyr","CsbBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzMDMDzgBmZGjZaYmpZMWmxMzMz8AzMzAmxMGzMLzMDMwYwCsMGN2GQmBBbYGMzghB")}
PURE_TRINKET_IDS=(250215,281215)

# Extended UI selected equipment is a pass-through to v098's exact
# source-backed item/tier/native-L checks, not a second selector.
OPTIONAL_CONTROLS=frozenset(("special_items","embellishments",
                             "consumable_choices","enchant_choices",
                             "runeforge_by_hand","max_single_stat_percent"))
DUAL_FORMS=frozenset(("dual_two_hand","dual_one_hand"))

class SessionBlocked(ValueError):pass
def need(ok,why):
    if not ok:raise SessionBlocked("V106_"+why)
def canonical(obj):
    return json.dumps(obj,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False)
def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_catalog_identity(path,revision,package_manifest_path=None):
    if path is None:
        need(package_manifest_path is None,
             "PACKAGE_MANIFEST_WITHOUT_SOURCE_CATALOG")
        return None
    source_path=pathlib.Path(path).expanduser().resolve()
    need(source_path.is_file() and not source_path.is_symlink(),
         "V213_SOURCE_CATALOG_FILE_INVALID")
    raw=source_path.read_bytes()
    try:
        document=json.loads(raw.decode("utf8"))
        source_catalog_bridge.verify_catalog(document)
    except Exception as exc:
        raise SessionBlocked("V213_SOURCE_CATALOG_INVALID:"+type(exc).__name__) from exc
    # This is the IMMUTABLE static-season source revision, not the actual
    # SimC runtime revision. Session identity separately binds the active
    # revision and executable SHA; do not rebuild unchanged seasonal gear
    # whenever SimC balance/APL is updated.
    need(document.get("schema")==source_catalog_bridge.SCHEMA and
         document.get("native_calls")==0 and
         document.get("network_calls")==0 and
         document.get("automatic_ui_promotion") is False,
         "V213_SOURCE_CATALOG_SESSION_IDENTITY_MISMATCH")
    result={
        "schema":document["schema"],
        "artifact_sha256":sha(raw),
        "manifest_sha256":document["manifest_sha256"],
        "game_build":document["game_build"],
        "simc_revision":document["simc_revision"],
    }
    if package_manifest_path is not None:
        package_path=pathlib.Path(package_manifest_path).expanduser().resolve()
        need(package_path.is_file() and not package_path.is_symlink(),
             "V181_PACKAGE_MANIFEST_FILE_INVALID")
        package_raw=package_path.read_bytes()
        need(0<len(package_raw)<=5_000_000,
             "V181_PACKAGE_MANIFEST_SIZE_INVALID")
        result["package_manifest_sha256"]=sha(package_raw)
    return result
STARTER_CATALOG=(pathlib.Path(__file__).resolve().parents[1]/
    "integration_probes/catalog/v146_character_starter_examples.json")

@functools.lru_cache(maxsize=1)
def starter_examples():
    """Compact user-editable examples; never load source equipment/APL files.

    Original complete SimC fixtures remain required on the legacy execution
    route, not for class/spec/race/talents/trinket INPUT controls.
    """
    doc=json.loads(STARTER_CATALOG.read_text(encoding="utf8"))
    need(type(doc) is dict and
         doc.get("schema")=="v146_user_character_starter_examples_v1" and
         type(doc.get("entries")) is dict,
         "USER_STARTER_CATALOG_SCHEMA")
    records=doc["entries"]
    need(set(records)=={"/".join(key) for key in bootstrap.ARCHETYPES},
         "USER_STARTER_CATALOG_24_SPEC_COVERAGE")
    for key,row in records.items():
        need(type(row) is dict and
             set(row)=={"race","talents","trinket_ids"} and
             type(row["trinket_ids"]) is list and
             len(row["trinket_ids"])==2 and
             all(type(i) is int and i>0 for i in row["trinket_ids"]),
             "USER_STARTER_CATALOG_ENTRY:"+key)
        bootstrap.scenario.text_token(row["race"],"STARTER_RACE")
        bootstrap.scenario.text_token(row["talents"],"STARTER_TALENTS")
    return records

def legacy_fixture_path(key):
    """Readiness locator only. No fixture contents or source metadata load."""
    need(key in bootstrap.ARCHETYPES,"DPS_ARCHETYPE_NOT_READY")
    first=bootstrap.common.metadata.BY_SPEC.get(key)
    if first is not None:
        name=first.source_fixture
    else:
        actor=bootstrap.common.mid2_pins.NEW.get("/".join(key))
        need(actor is not None,"LEGACY_SOURCE_FIXTURE_NOT_REGISTERED")
        name="v132_MID2_"+actor[0]+".simc"
    return bootstrap.FIXTURES/name

def source_defaults(key):
    need(key in SUPPORTED,"DPS_ARCHETYPE_NOT_READY")
    spec=bootstrap.pure.contracts.lookup(*key)
    need(spec is not None,"STABLE_USER_SPEC_CONTRACT_MISSING")
    if key in bootstrap.PURE_PRODUCT_SPECS:
        race,talents=PURE_STARTERS[key]
        trinkets=list(PURE_TRINKET_IDS)
        oil=[]
    else:
        row=starter_examples()["/".join(key)]
        race,talents,trinkets=row["race"],row["talents"],list(row["trinket_ids"])
        oil=(["main_hand","off_hand"]
             if spec["weapon_form"] in DUAL_FORMS else ["main_hand"])
    return {"class":key[0],"spec":key[1],"race":race,
            "talents":talents,"trinket_ids":trinkets,
            "weapon_form":spec["weapon_form"],"oil_hands":oil}

def validated_selected_gear(entries,group,limit):
    """Validate only user input shape. v098 + SimC own identity and effects."""
    need(type(entries) is list and len(entries)<=limit,
         "SELECTED_GEAR_COUNT_OR_TYPE")
    out=[]
    for item in entries:
        need(type(item) is dict and
             set(item)=={"slot","item_id","options"},
             "SELECTED_GEAR_FIELDS")
        slot=item["slot"]
        need(type(slot) is str and slot in bootstrap.item_mod.SLOTS and
             slot not in ("trinket1","trinket2"),
             "SELECTED_GEAR_NONTRINKET_SLOT_REQUIRED")
        bootstrap.item_mod.checked_id(item["item_id"])
        options=bootstrap.item_mod.checked_options(item["options"])
        if group=="special":
            need(not(set(options)&{"embellishment","crafted_stats"}),
                 "SPECIAL_CANNOT_BE_CRAFTED")
        else:
            need("embellishment" in options and
                 "redirected_base_stats" not in options,
                 "CRAFTED_NEEDS_EMBELLISHMENT_NOT_CATALYST")
        out.append({"slot":slot,"item_id":item["item_id"],
                    "options":options})
    need(len({v["slot"] for v in out})==len(out),
         "DUPLICATE_SELECTED_GEAR_SLOT")
    return out

def selected_rows_from_form(special_rows,crafted_rows):
    """Thin form-data serializer: only ID/slot/SimC-native option tokens.

    Empty rows are ignored. Partial rows fail before any Native request.
    Original item effects and crafted stat mechanics stay in SimC, not here.
    """
    need(type(special_rows) is list and len(special_rows)<=2
         and type(crafted_rows) is list and len(crafted_rows)<=2,
         "ADVANCED_FORM_MAX_TWO_ROWS_PER_GROUP")
    converted={}
    layouts=(
        ("special_items",special_rows,("bonus_id","redirected_base_stats")),
        ("embellishments",crafted_rows,
         ("crafted_stats","embellishment","bonus_id")))
    for group,rows,option_keys in layouts:
        result=[]
        for raw in rows:
            need(type(raw) is dict
                 and set(raw)=={"slot","item_id"}|set(option_keys),
                 "ADVANCED_FORM_FIELDS")
            text={k:str(v).strip() for k,v in raw.items()}
            if not any(text.values()):continue
            need(text["slot"] and text["item_id"] and
                 text["item_id"].isdigit(),
                 "ADVANCED_FORM_SLOT_AND_ITEM_REQUIRED")
            result.append({
                "slot":text["slot"],"item_id":int(text["item_id"]),
                "options":{k:text[k] for k in option_keys if text[k]}})
        converted[group]=result
    return converted

def user_scenario(controls):
    """Only approved v098 user fields; do not expose manifest/filler/seed."""
    required={"class","spec","ilevel","final_T",
              "trinket_ids","oil_hands","targets","duration_seconds",
              "raid_buffs"}
    need(type(controls) is dict and
         required<=set(controls)<=required|OPTIONAL_CONTROLS|{"race","talents"},
         "USER_INPUT_FIELDS")
    key=(controls["class"],controls["spec"])
    need(key in SUPPORTED,"DPS_ARCHETYPE_NOT_READY")
    # Empty or omitted character choices have explicit, deterministic
    # defaults; saved sessions always bind the EFFECTIVE race/talents.
    # Do not import gear, flask, enchants or oils from a SimC sample.
    raw_race=controls.get("race")
    raw_talents=controls.get("talents")
    need(raw_race is None or type(raw_race) is str,
         "USER_RACE_TYPE_INVALID")
    need(raw_talents is None or type(raw_talents) is str,
         "USER_TALENTS_TYPE_INVALID")
    race=(raw_race.strip() if raw_race else "") or "dwarf"
    talents=(raw_talents.strip() if raw_talents else "")
    if not talents:
        talents=source_defaults(key)["talents"]
    # Dwarves cannot be druids, demon hunters or evokers. Do not silently
    # replace the user's requested dwarf default with another race.
    need(not (race=="dwarf" and key[0] in
              ("druid","demonhunter","evoker")),
         "DWARF_NOT_AVAILABLE_FOR_CLASS_SELECT_RACE")
    contract=bootstrap.pure.contracts.lookup(*key)
    need(contract is not None and
         (contract["allowed_races"] is None or
          race in contract["allowed_races"]),
         "RACE_NOT_SUPPORTED_BY_SPECIALIZATION")
    bootstrap.scenario.text_token(race,"USER_RACE")
    bootstrap.scenario.text_token(talents,"USER_TALENTS")
    ilvl=controls["ilevel"];final=controls["final_T"]
    stat_cap=controls.get("max_single_stat_percent")
    need(stat_cap is None or (type(stat_cap) is int and
         25<=stat_cap<=100),"USER_MAX_SINGLE_STAT_PERCENT_25_TO_100")
    need(type(ilvl) is int and 266<=ilvl<=344,"ILVL_OUT_OF_REFERENCE")
    need(final is None or type(final) is int and 1<=final<=100000,
         "USER_FINAL_T_INVALID")
    trinkets=controls["trinket_ids"]
    need(type(trinkets) is list and len(trinkets)==2
         and all(type(i) is int and i>0 for i in trinkets),
         "TWO_REAL_TRINKET_IDS_REQUIRED")
    # Input validation is source-free for all 26 contracts. Execution of an
    # unpromoted legacy spec STILL uses its old source-backed route.
    weapons=bootstrap.pure.contracts.lookup(*key)["weapon_form"]
    hands=controls["oil_hands"]
    need(type(hands) is list and len(hands)==len(set(hands))
         and set(hands)<={"main_hand","off_hand"} and
         (weapons in DUAL_FORMS or "off_hand" not in hands),
         "OIL_HANDS_INCOMPATIBLE_WITH_SOURCE_WEAPON_FORM")
    targets=controls["targets"];duration=controls["duration_seconds"]
    need(type(targets) is int and 1<=targets<=40 and
         type(duration) is int and 1<=duration<=3600 and
         type(controls["raid_buffs"]) is bool,
         "COMBAT_USER_SETTING_INVALID")
    specials=validated_selected_gear(
        controls.get("special_items",[]),"special",8)
    crafted=validated_selected_gear(
        controls.get("embellishments",[]),"crafted",2)
    choice=controls.get("consumable_choices")
    if choice is not None:
        need(type(choice) is dict and
             set(choice)==consumer.CHOICE_FIELDS,
             "CONSUMABLE_CHOICES_FIELDS")
        need(all(type(choice[k]) is str for k in
                 ("flask","food","potion","augmentation")) and
             type(choice["diamond_id"]) is int and
             type(choice["omnium_talents"]) is str,
             "CONSUMABLE_CHOICES_TYPES")
    occupied=[r["slot"] for r in specials+crafted]
    need(len(occupied)==len(set(occupied)),
         "SELECTED_SPECIAL_AND_CRAFTED_SLOT_CONFLICT")
    output={"schema":bootstrap.SCHEMA,
            "character":{"class":key[0],"spec":key[1],
                         "race":race,"talents":talents},
            "target":{"ilevel":ilvl,"final_T":final},
            "trinkets":[{"slot":slot,"item_id":id_,"options":{}}
                for slot,id_ in zip(("trinket1","trinket2"),trinkets)],
            "special_items":specials,"embellishments":crafted,
            "oil_hands":list(hands),
            "combat":{"targets":targets,"duration_seconds":duration,
                      "raid_buffs":controls["raid_buffs"]}}
    if choice is not None:output["consumable_choices"]=dict(choice)
    if stat_cap is not None:output["max_single_stat_percent"]=stat_cap
    if "enchant_choices" in controls:
        nonchmv_enchant.check_choice(controls["enchant_choices"])
        output[nonchmv_enchant.FIELD]=dict(controls["enchant_choices"])
    if "runeforge_by_hand" in controls:
        output["runeforge_by_hand"]=bootstrap.runeforge_mod.check_input(
            selection=controls["runeforge_by_hand"],class_name=key[0],
            weapon_form=weapons,need=need)
    return output

def standard_controls(key=("paladin","retribution")):
    d=source_defaults(key)
    return {k:v for k,v in d.items()
            if k in ("class","spec","race","talents","oil_hands")} | {
            "ilevel":334,"final_T":None,"max_single_stat_percent":60,
            "trinket_ids":d["trinket_ids"],
            "targets":1,"duration_seconds":300,"raid_buffs":True,
            "special_items":[],"embellishments":[],
            "consumable_choices":{
                "flask":"source_default","food":"source_default",
                "potion":"source_default","augmentation":"source_default",
                "diamond_id":0,"omnium_talents":"source_default"}}

def session_key(user,binary,revision,static_cache=None,*,ordinary_variant=None,
                independent_334=False,independent_target_level=False,
                current_season_product=False,source_catalog_path=None,
                package_manifest_path=None,
                 fresh_installed_manifest_sha256=None):
    binary=pathlib.Path(binary).expanduser().resolve()
    need(binary.is_file(),"SIMC_BINARY_NOT_FOUND")
    need(type(revision) is str and re.fullmatch(r"[0-9a-fA-F]{7,40}",revision),
         "SIMC_REVISION_MUST_BE_VERIFIED_HEX")
    cache_path=(pathlib.Path(static_cache).expanduser().resolve()
                if static_cache else None)
    need(cache_path is None or cache_path.is_file(),"STATIC_CACHE_NOT_FOUND")
    # Specials require an exact Native static L variant in the selected
    # cache. Don't invite an expensive Native job then invent/zero missing L.
    need(not user.get("special_items") or cache_path is not None,
         "SPECIAL_EQUIPMENT_REQUIRES_EXACT_STATIC_CACHE")
    need(type(current_season_product) is bool,
         "CURRENT_SEASON_PRODUCT_MODE_BOOL_REQUIRED")
    need(source_catalog_path is None or current_season_product,
         "V213_SOURCE_CATALOG_ONLY_CURRENT_SEASON_PRODUCT")
    need(package_manifest_path is None or source_catalog_path is not None,
         "V181_PACKAGE_MANIFEST_WITHOUT_V213_SOURCE")
    need(fresh_installed_manifest_sha256 is None or (
          current_season_product and source_catalog_path is not None and
          type(fresh_installed_manifest_sha256) is str and
          re.fullmatch(r"[0-9a-f]{64}",fresh_installed_manifest_sha256)),
          "FRESH_V212_INSTALL_IDENTITY_INVALID")
    need(not current_season_product or (
         not independent_334 and not independent_target_level and
         ordinary_variant is None and
         type(user) is dict and type(user.get("character")) is dict and
         type(user.get("target")) is dict and
         (user["character"].get("class"),user["character"].get("spec")) in SUPPORTED and
         type(user["target"].get("ilevel")) is int and
         266<=user["target"]["ilevel"]<=344),
         "CURRENT_SEASON_PRODUCT_SCOPE_TARGET_RANGE")
    need(type(independent_334) is bool,"INDEPENDENT_334_MODE_BOOL_REQUIRED")
    need(type(independent_target_level) is bool,"INDEPENDENT_TARGET_LEVEL_MODE_BOOL_REQUIRED")
    need(not (independent_334 and independent_target_level),"ONLY_ONE_INDEPENDENT_PROFILE_MODE")
    if independent_334:
        ch=user.get("character") if type(user) is dict else None
        target=user.get("target") if type(user) is dict else None
        need(type(ch) is dict and type(target) is dict and
             (ch.get("class"),ch.get("spec")) in bootstrap.ARCHETYPES and
             target.get("ilevel")==334 and ordinary_variant is None,
             "INDEPENDENT_334_USER_SCOPE_NOT_SUPPORTED")
    if independent_target_level:
        ch=user.get("character") if type(user) is dict else None
        target=user.get("target") if type(user) is dict else None
        need(type(ch) is dict and type(target) is dict and
             (ch.get("class"),ch.get("spec")) in SUPPORTED and
             type(target.get("ilevel")) is int and
             266<=target["ilevel"]<=344 and target["ilevel"]!=334 and
             ordinary_variant is None,
             "INDEPENDENT_NON334_USER_SCOPE_NOT_SUPPORTED")
    if ordinary_variant is not None:
        # Developer-only representative experiment. A profile identity change
        # MUST produce a different durable session, never reuse old DPS JSON2.
        need(type(ordinary_variant) is str
             and ordinary_variant in bootstrap.common.ORDINARY_VARIANTS,
             "ORDINARY_VARIANT_NOT_PINNED")
        variant=bootstrap.common.ORDINARY_VARIANTS[ordinary_variant]
        character=user.get("character") if type(user) is dict else None
        target=user.get("target") if type(user) is dict else None
        need(type(character) is dict and type(target) is dict
             and (character.get("class"),character.get("spec"))==variant["key"]
             and target.get("ilevel")==334,
             "ORDINARY_VARIANT_CHARACTER_OR_LEVEL_MISMATCH")
        need(all(r.get("slot")!=variant["slot"] for group in
                 ("special_items","embellishments")
                 for r in user.get(group,[])),
             "ORDINARY_VARIANT_CONFLICTS_WITH_SELECTED_GEAR")
    identity={"schema":SCHEMA,"user":user,
              "simc_binary_sha256":sha(binary.read_bytes()),
              "simc_revision":revision,
              "static_cache_sha256":sha(cache_path.read_bytes()) if cache_path else None}
    if ordinary_variant is not None:
        identity["ordinary_variant"]=ordinary_variant
    if independent_334:
        identity["independent_334"]=True
    if independent_target_level:
        identity["independent_target_level"]=True
    if current_season_product:
        # These additions affect opt-in sessions only. Old session identity
        # bytes are IDENTICAL to existing v106 across all prior modes.
        stage=bootstrap.source_first
        identity["current_season_product"]="v177_source_first_26_dps_v1"
        # A code-only weapon rule change alters the generated profile even
        # when the 511/65 season catalog byte SHA stays exactly the same.
        # Make NEW corrected user sessions disjoint from pre-v184 Native.
        identity["current_season_weapon_selection_policy"]=stage.WEAPON_SELECTION_POLICY
        # Only an occupied tier-functional slot can change its 4-of-5
        # physical layout. Preserve good v185 baseline and neck/ring/back
        # selected-gear Native caches when their equipment is unchanged.
        if any(row["slot"] in bootstrap.common.TIER_FIVE
               for group in ("special_items","embellishments")
               for row in user.get(group,[])):
            identity["current_season_tier_layout_policy"]=bootstrap.common.CURRENT_SEASON_TIER_LAYOUT_POLICY
        identity["current_season_gear_sha256"]=sha(stage.gear.DEFAULT.read_bytes())
        identity["current_season_tier_sha256"]=sha(stage.TIER_PATH.read_bytes())
        identity["current_season_budget_sha256"]=sha(stage.BUDGET_PATH.read_bytes())
        identity["source_first_base_catalog_sha256"]=sha(
            bootstrap.pure.DEFAULT_CATALOG.read_bytes())
        source_identity=source_catalog_identity(
            source_catalog_path,revision,package_manifest_path)
        if source_identity is not None:
            identity["current_season_source_catalog"]=source_identity
        if fresh_installed_manifest_sha256 is not None:
            identity["fresh_v212_installed_manifest_sha256"]=(
                fresh_installed_manifest_sha256)
    identity["profile_stage"]=profile_stage.session_identity(
        user,independent_334=independent_334,
        independent_target_level=independent_target_level,
        current_season_product=current_season_product,
        source_catalog_path=source_catalog_path)
    return sha(canonical(identity).encode("utf8"))[:20],identity


def preview_selected_fresh_session_identity(user,binary,revision,static_cache,*,
        selected_source,source_catalog_path,installed_manifest_sha256,
        package_manifest_path=None):
    """v435 B8 exact *future* session/cache key; no folder/Native/admission.

    Reuse the existing v106 binary/revision/user/cache/season identity, then
    add the final v434 profile + typed B/T/L/O physical/source digest. Old
    v106 keys are not changed and this preview never calls store_session().
    """
    proof=selected_source
    need(type(proof) is dict and
         proof.get("schema")==
             "v433_v098_selected_user_physical_budget_preflight_v1"
         and proof.get("status")==
             "B8_SELECTED_V096_COMPLETE_PROFILE_BUDGET_NOT_ADMITTED"
         and proof.get("native_execution_authorized") is False
         and proof.get("runtime_manifest_created") is False
         and type(proof.get("final_source_identity")) is dict
         and type(proof.get("v096_selected_source_only_preflight")) is dict
         and type(proof.get("budget_preflight")) is dict
         and type(proof.get("bound_source_identity")) is dict
         and type(proof.get("profile_simc")) is str,
         "B8_SELECTED_V434_SOURCE_ONLY_IDENTITY_REQUIRED")
    final=proof["final_source_identity"]
    bound=proof["bound_source_identity"]
    budget=proof["budget_preflight"]
    verified=proof["v096_selected_source_only_preflight"]
    need(final.get("schema")==
             "v434_b8_selected_full_native_profile_source_binding_v1"
         and proof.get("final_source_identity_sha256")==
             sha(canonical(final).encode("utf8"))
         and proof.get("bound_source_identity_sha256")==
             sha(canonical(bound).encode("utf8"))
         and verified.get("schema")==
             "v434_v096_selected_fresh_nonadmitted_preflight_v1"
         and verified.get("status")==
             "B8_V096_SOURCE_ONLY_PROFILE_AND_STATIC_BOUNDS_VALIDATED"
         and verified.get("native_execution_authorized") is False
         and verified.get("runtime_manifest_created") is False
         and final.get("verified_v096_preflight_sha256")==
             sha(canonical(verified).encode("utf8"))
         and final.get("v433_preconsumable_source_sha256")==
             proof["bound_source_identity_sha256"]
         and final.get("final_profile_sha256")==
             proof.get("source_profile_sha256")==
             sha(proof["profile_simc"].encode("utf8"))
         and final.get("final_scenario_digest")==
             proof.get("v096_typed_input_unadmitted",{}).get(
                 "scenario_digest")==verified.get("scenario_digest")
         and final.get("installed_v212_manifest_sha256")==
             installed_manifest_sha256==
             verified.get("installed_v212_manifest_sha256")==
             bound.get("installed_v212_manifest_sha256")
         and final.get("selected_budget_identity_sha256")==
             verified.get("selected_budget_identity_sha256")==
             budget.get("selected_budget_identity_sha256"),
         "B8_SELECTED_V434_FINAL_PROFILE_OR_SOURCE_SHA_DRIFT")
    need(type(user) is dict and
         bool(user.get("special_items") or user.get("embellishments")) and
         type(user.get("target")) is dict and
         user["target"].get("ilevel")==budget.get("target_ilevel") and
         (user["target"].get("final_T") is None or
          user["target"]["final_T"]==budget.get("final_T")) and
         budget.get("manual_final_T_authoritative")==
             (user["target"].get("final_T") is not None),
         "B8_SELECTED_USER_TARGET_NOT_BOUND_TO_V434")
    equipment=proof.get("selected_equipment")
    need(type(equipment) is dict,"B8_SELECTED_EQUIPMENT_REQUIRED")
    rows=[r for group in ("tier","special","crafted","trinkets")
          for r in equipment.get(group,[]) if type(r) is dict]
    actual={r.get("slot"):r.get("item_id") for r in rows}
    need(len(actual)==len(rows) and
         all(type(x) is dict and actual.get(x.get("slot"))==
             x.get("item_id") for group in ("special_items","embellishments")
             for x in user.get(group,[])),
         "B8_SELECTED_USER_ITEM_ID_NOT_PHYSICALLY_BOUND")
    # A digest field copied from a prior result is not the runtime source.
    # Re-normalize the actual typed scenario and verify the full v061
    # digest before its iterations or combat settings enter the cache key.
    typed=proof.get("v096_typed_input_unadmitted")
    need(type(typed) is dict and type(typed.get("scenario")) is dict,
         "B8_SELECTED_TYPED_SCENARIO_MISSING")
    normalized=bootstrap.scenario.normalize(typed["scenario"])
    need(normalized["scenario_digest"]==
             verified.get("scenario_digest")==
             typed.get("scenario_digest") and
         normalized["scenario"]["target"]["manual_total"]==
             budget.get("base_B") and
         normalized["budget"]["external_temporary_rating"]==
             budget.get("fixed_O") and
         normalized["scenario"]["equipment"]==
             proof.get("selected_equipment") and
         proof.get("scenario_source_only",{}).get("runtime")==
             normalized["scenario"]["runtime"],
         "B8_SELECTED_TYPED_SCENARIO_OR_PREVIEW_CACHE_DRIFT")
    settings=normalized["scenario"]["runtime"]
    need(type(settings) is dict and
         all(type(settings.get(k)) is int and settings[k]>0
             for k in ("scout_iterations","confirm_iterations","threads"))
         and settings["confirm_iterations"]>=settings["scout_iterations"],
         "B8_SELECTED_ITERATION_IDENTITY_MISSING")
    base_key,base_identity=session_key(
        user,binary,revision,static_cache,
        current_season_product=True,source_catalog_path=source_catalog_path,
        package_manifest_path=package_manifest_path,
        fresh_installed_manifest_sha256=installed_manifest_sha256)
    need(base_identity["static_cache_sha256"]==
             bound.get("static_cache_content_sha256")==
             verified.get("static_cache_content_sha256")
         and base_identity.get("fresh_v212_installed_manifest_sha256")==
             installed_manifest_sha256,
         "B8_SELECTED_STATIC_CACHE_FILE_OR_INSTALLED_IDENTITY_DRIFT")
    payload={
        "schema":"v435_selected_fresh_session_key_preview_v1",
        "v106_original_session_identity_sha256":
            sha(canonical(base_identity).encode("utf8")),
        "v434_final_source_identity_sha256":
            proof["final_source_identity_sha256"],
        "v434_source_profile_sha256":
            proof["source_profile_sha256"],
        "v434_scenario_digest":verified["scenario_digest"],
        "selected_budget_identity_sha256":
            budget["selected_budget_identity_sha256"],
        "selected_static_cache_content_sha256":
            base_identity["static_cache_sha256"],
        "installed_v212_manifest_sha256":installed_manifest_sha256,
        "iterations_identity":{
            k:settings[k] for k in
            ("scout_iterations","confirm_iterations","threads")},
        "native_binary_sha256":base_identity["simc_binary_sha256"],
        "simc_revision":revision,
    }
    # The complete v106 identity (rather than a detached payload-only SHA)
    # is sealable in V106_SESSION_IDENTITY.json and readable by the worker.
    # Legacy non-selected session keys are left untouched.
    full_session_identity={**base_identity,
                           "v435_selected_source_identity":payload}
    final_sha=sha(canonical(full_session_identity).encode("utf8"))
    need(final_sha[:20]!=base_key,
         "B8_SELECTED_SESSION_KEY_COLLIDES_WITH_LEGACY")
    return {"schema":payload["schema"],
            "status":"B8_SELECTED_SESSION_KEY_SOURCE_ONLY_NOT_ADMITTED",
            "session_key_preview":final_sha[:20],
            "identity_sha256":final_sha,
            "identity_components":payload,
            "full_session_identity":full_session_identity,
            "old_v106_session_key_not_reused":True,
            "native_execution_authorized":False,
            "session_folder_created":False,
            "runtime_manifest_created":False,
            "cache_mutations":0,"new_native_calls":0}



def store_selected_fresh_session(user,root,binary,revision,static_cache, *,
                                 selected_source,source_catalog_path,
                                 installed_manifest_sha256):
    """Store only the separately keyed source-backed selected session.

    No Native and no V094/old-session migration. v096 replays the original
    v191/v232/v432/v217/v212 sources after the stage writes a manifest.
    """
    proof=preview_selected_fresh_session_identity(
        user,binary,revision,static_cache,
        selected_source=selected_source,
        source_catalog_path=source_catalog_path,
        installed_manifest_sha256=installed_manifest_sha256)
    identity=proof["full_session_identity"]
    key=proof["session_key_preview"]
    need(sha(canonical(identity).encode("utf8"))[:20]==key,
         "B8_SELECTED_FULL_SESSION_SHA_OR_KEY_DRIFT")
    folder=pathlib.Path(root).expanduser().resolve()/key
    need(not folder.is_symlink(),"B8_SELECTED_SESSION_FOLDER_SYMLINK")
    user_bytes=canonical(user)+"\n"
    identity_bytes=canonical(identity)+"\n"
    for name,expected in (("user.json",user_bytes),
                          ("V106_SESSION_IDENTITY.json",identity_bytes)):
        target=folder/name
        need(not target.is_symlink() and
             (not target.exists() or
              target.is_file() and target.read_text("utf8")==expected),
             "B8_SELECTED_EXISTING_SEALED_SESSION_CHANGED:"+name)
    folder.mkdir(parents=True,exist_ok=True)
    for name,expected in (("user.json",user_bytes),
                          ("V106_SESSION_IDENTITY.json",identity_bytes)):
        target=folder/name
        if not target.exists():
            target.write_text(expected,encoding="utf8")
    return folder


def session_path(user,root,binary,revision,static_cache=None,*,
                 ordinary_variant=None,independent_334=False,independent_target_level=False,
                 current_season_product=False,source_catalog_path=None,
                 package_manifest_path=None,
                 fresh_installed_manifest_sha256=None):
    key,identity=session_key(user,binary,revision,static_cache,
                             ordinary_variant=ordinary_variant,
                             independent_334=independent_334,
                             independent_target_level=independent_target_level,
                             current_season_product=current_season_product,
                             source_catalog_path=source_catalog_path,
                             package_manifest_path=package_manifest_path,
                              fresh_installed_manifest_sha256=fresh_installed_manifest_sha256)
    return pathlib.Path(root).expanduser().resolve()/key,identity

def store_session(user,root,binary,revision,static_cache=None,*,
                  ordinary_variant=None,independent_334=False,independent_target_level=False,
                  current_season_product=False,source_catalog_path=None,
                  package_manifest_path=None,
                 fresh_installed_manifest_sha256=None):
    folder,identity=session_path(user,root,binary,revision,static_cache,
                                 ordinary_variant=ordinary_variant,
                                 independent_334=independent_334,
                                 independent_target_level=independent_target_level,
                                 current_season_product=current_season_product,
                                 source_catalog_path=source_catalog_path,
                                 package_manifest_path=package_manifest_path,
                                  fresh_installed_manifest_sha256=fresh_installed_manifest_sha256)
    folder.mkdir(parents=True,exist_ok=True)
    target=folder/"user.json"
    raw=canonical(user)+"\n"
    need(not target.exists() or target.read_text(encoding="utf8")==raw,
         "EXISTING_SESSION_USER_INPUT_CHANGED")
    if not target.exists():target.write_text(raw,encoding="utf8")
    lock=folder/"V106_SESSION_IDENTITY.json"
    seal=canonical(identity)+"\n"
    need(not lock.exists() or lock.read_text(encoding="utf8")==seal,
         "SESSION_IDENTITY_DRIFT")
    if not lock.exists():lock.write_text(seal,encoding="utf8")
    return folder

def paths(folder):
    folder=pathlib.Path(folder)
    out=folder/"generated"/"simc_results"
    return {"cancel":folder/"generated"/"CANCEL",
            "progress":out/"V094_PROGRESS.json",
            "native_result":out/"V094_RESULT.json",
            "final":folder/"V106_USER_RESULT.json",
            "state":folder/"V106_WORKER_STATE.json",
            "log":folder/"V106_WORKER.log"}

def request_cancel(folder):
    p=paths(folder)["cancel"]
    p.parent.mkdir(parents=True,exist_ok=True)
    p.touch(exist_ok=True)
    return p

def clear_cancel(folder):
    p=paths(folder)["cancel"]
    if p.exists():p.unlink()

def progress(folder):
    p=paths(folder)
    x={"status":"NOT_STARTED","progress_percent":0.0,
       "completed_jobs":0,"planned_jobs":6,
       "cache_hits":0,"native_attempts":0}
    if p["progress"].is_file():
        report=json.loads(p["progress"].read_text(encoding="utf8"))
        x.update({"status":report["status"],
                  "progress_percent":report.get("progress_percent",0.0),
                  "completed_jobs":report.get("completed_jobs",0),
                  "planned_jobs":report.get("planned_jobs",6),
                  "cache_hits":report.get("cache_verified_hits",0),
                  "native_attempts":report.get("new_native_attempts",0),
                  "error":report.get("error")})
    if p["state"].is_file():
        x["worker"]=json.loads(p["state"].read_text(encoding="utf8"))
    return x

def format_result(data):
    """No recomputation of DPS or stats: render v096's 95%-only user result."""
    need(type(data) is dict and data.get("status","").startswith("PASS")
         and type(data.get("user_result")) is dict,
         "REAL_NATIVE_USER_RESULT_REQUIRED")
    r=data["user_result"];first=r["observed_first_choice"]
    names={"crit_rating":"치명","haste_rating":"가속",
           "mastery_rating":"특화","versatility_rating":"유연"}
    need(r["confidence_level"]==0.95 and
         r["global_optimum_proven"] is False,"ONLY_95_ALLOWED")
    ratings=first["absolute_rating_T"]
    ratio=first["percent_of_final_T"]
    need(all(k in ratings and k in ratio for k in names),
         "FOUR_ABSOLUTE_RATINGS_AND_PERCENT_REQUIRED")
    lines=["관측 1순위 · 전역 최적해 입증 아님",
           "최종 CHMV T = "+str(r["final_T"])+" (B="+str(r["base_B"])
           +", 고정 기름 O="+str(sum(r["fixed_O"].values()))+")",
           " / ".join(names[k]+" "+str(ratings[k])+
                      " ("+format(ratio[k],".2f")+"%)"
                      for k in names),
           "관측 DPS: "+format(first["observed_dps_mean"],",.1f")+
           "   SimC SEM: "+format(first["simc_sem"],",.2f"),
           "선택된 확인 후보 2개의 95% 방향 지지: "+
           ("예" if r["confirmation_pair_direction_supported_at_95"] else "미확정"),
           "실질적 근접 대안 관측: "+str(len(r["material_near_alternatives"]))+
           "개 (미관측은 존재하지 않는다는 뜻 아님)"]
    for i,v in enumerate(r["material_near_alternatives"],1):
        lines.append("대안 "+str(i)+": "+
            " / ".join(names[k]+" "+str(v["absolute_rating_T"][k])
                       for k in names)+" | DPS "+
            format(v["observed_dps_mean"],",.1f")+" | "+
            str(v["pairwise_95_label"]))
    return "\n".join(lines)

@contextlib.contextmanager
def worker_lock(folder):
    """OS-owned lock: concurrent workers refuse, crash auto-unlocks.

    File remains for inspection; we lock the descriptor, not its existence.
    Windows msvcrt byte lock and Unix flock both release on process exit.
    """
    target=pathlib.Path(folder)/"V106_WORKER.lock"
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("a+b") as fd:
        fd.seek(0,2)
        if fd.tell()==0:fd.write(b"1");fd.flush()
        fd.seek(0)
        try:
            if os.name=="nt":
                import msvcrt
                msvcrt.locking(fd.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(fd.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as e:
            raise SessionBlocked("V106_SAME_SESSION_ALREADY_RUNNING") from e
        try:
            yield
        finally:
            fd.seek(0)
            if os.name=="nt":
                msvcrt.locking(fd.fileno(),msvcrt.LK_UNLCK,1)
            else:
                fcntl.flock(fd.fileno(),fcntl.LOCK_UN)

CACHE_PROOF_SCHEMA="v112_completed_user_cache_replay_v1"

def native_json2_hashes(folder):
    """Six real Native JSON2 outputs, already guarded by v064 disk receipts.

    Do not parse effects or trust naked JSON without a companion Native
    receipt; actual byte/identity checks are performed by cache_only replay.
    """
    cases=pathlib.Path(folder)/"generated"/"simc_results"
    out={}
    for file in sorted(cases.rglob("result.json")):
        need((file.parent/"native_receipt.json").is_file(),
             "CACHE_ONLY_NATIVE_RECEIPT_MISSING")
        out[str(file.relative_to(cases)).replace("\\","/")]=sha(file.read_bytes())
    need(len(out)==6,"CACHE_ONLY_REQUIRES_SIX_JSON2_RESULTS")
    return out

def cache_only_preflight(folder):
    """Fail BEFORE touching v094 progress if any Native case is missing."""
    p=paths(folder)
    need(p["final"].is_file() and p["native_result"].is_file()
         and p["progress"].is_file(),
         "CACHE_ONLY_REQUIRES_COMPLETED_REAL_SESSION")
    final=json.loads(p["final"].read_text("utf8"))
    progress=json.loads(p["progress"].read_text("utf8"))
    report=json.loads(p["native_result"].read_text("utf8"))
    need(final["status"].startswith("PASS") and
         report["status"].startswith("PASS") and
         progress["status"].startswith("PASS") and
         progress["completed_jobs"]==6 and
         progress["new_native_attempts"]==6 and
         final["native_calls_cumulative"]==6,
         "CACHE_ONLY_REQUIRES_SIX_COMPLETED_NATIVE")
    need(final["user_result"]["confidence_level"]==0.95
         and final["user_result"]["global_optimum_proven"] is False,
         "CACHE_ONLY_95_RESULT_REQUIRED")
    return {"result":final,"progress":progress,
            "native_sha256":native_json2_hashes(folder)}

def print_user_result(message):
    """Windows cp1252 console fallback: preserve UTF-8 bytes for GUI logs."""
    try:
        print(message,flush=True)
    except UnicodeEncodeError:
        binary=getattr(sys.stdout,"buffer",None)
        if binary is not None:
            binary.write((message+"\n").encode("utf-8"))
            binary.flush()
        else:
            print(message.encode("ascii","backslashreplace").decode("ascii"),
                  flush=True)

def worker(folder,binary,revision,static_cache=None,cache_only=False):
    """Exclusive child process. GUI owns launch/cancel, existing runner owns DPS."""
    folder=pathlib.Path(folder).resolve()
    try:
        with worker_lock(folder):
            return _worker_locked(folder,binary,revision,static_cache,cache_only)
    except SessionBlocked as e:
        print("V106_BLOCKED:",str(e),file=sys.stderr,flush=True)
        return 3

def _installed_source_paths(identity):
    """Locate packaged source used when this session was planned.

    No network, no artifact refresh. The exact SHA is checked by session_key.
    Product sessions never fall back to an arbitrary or missing source file.
    """
    if "current_season_source_catalog" not in identity:
        return None,None
    root=pathlib.Path(__file__).resolve().parents[1]
    source=root/"data"/"current_season_source_to_catalog.json"
    bound=identity["current_season_source_catalog"]
    need(type(bound) is dict,"V213_SESSION_SOURCE_IDENTITY_INVALID")
    package=(root/"V181_PACKAGE_MANIFEST.json"
             if bound.get("package_manifest_sha256") else None)
    return source,package


def _worker_locked(folder,binary,revision,static_cache,cache_only):
    p=paths(folder)
    def write_state(status,reason=None):
        data={"schema":SCHEMA,"status":status}
        if reason:data["reason"]=reason
        p["state"].write_text(canonical(data)+"\n",encoding="utf8")
    try:
        need((folder/"user.json").is_file() and
             (folder/"V106_SESSION_IDENTITY.json").is_file(),
             "STORED_USER_SESSION_REQUIRED")
        user=json.loads((folder/"user.json").read_text(encoding="utf8"))
        identity=json.loads((folder/"V106_SESSION_IDENTITY.json").read_text(encoding="utf8"))
        variant=identity.get("ordinary_variant")
        independent=identity.get("independent_334",False)
        independent_level=identity.get("independent_target_level",False)
        current_season=bool(identity.get("current_season_product",False))
        # Existing pre-v184 sessions are read-only evidence after the
        # representative weapons change. Do not recompute or overwrite their
        # physical.simc/JSON2, or replay their old DPS as a corrected profile.
        if current_season:
            need(identity.get("current_season_weapon_selection_policy")==
                 bootstrap.source_first.WEAPON_SELECTION_POLICY,
                 "OLD_WEAPON_POLICY_SESSION_START_NEW_CORRECTED_SESSION")
            if any(row["slot"] in bootstrap.common.TIER_FIVE
                   for group in ("special_items","embellishments")
                   for row in user.get(group,[])):
                need(identity.get("current_season_tier_layout_policy")==
                     bootstrap.common.CURRENT_SEASON_TIER_LAYOUT_POLICY,
                     "OLD_TIER_LAYOUT_SESSION_START_NEW_CORRECTED_SESSION")
        selected_fresh=type(identity.get(
            "v435_selected_source_identity")) is dict
        if selected_fresh:
            need(identity.get("schema")==SCHEMA and
                 identity.get("user")==user and
                 sha(canonical(identity).encode("utf8"))[:20]==folder.name and
                 identity.get("simc_binary_sha256")==
                     sha(pathlib.Path(binary).read_bytes()) and
                 identity.get("simc_revision")==revision and
                 isinstance(static_cache,(str,pathlib.Path)) and
                 pathlib.Path(static_cache).is_file() and
                 identity.get("static_cache_sha256")==
                     sha(pathlib.Path(static_cache).read_bytes()),
                 "B8_SELECTED_WORKER_SESSION_BINARY_CACHE_OR_USER_DRIFT")
            selected_manifest=folder/"generated"/"manifest.json"
            need(selected_manifest.is_file() and
                 not selected_manifest.is_symlink(),
                 "B8_SELECTED_WORKER_REPLAY_MANIFEST_REQUIRED")
            requested=json.loads(selected_manifest.read_text("utf8"))
            need(requested.get("installed_selected_fresh_v212_source",{}).
                     get("selected_v435_identity_sha256")==
                 sha(canonical(identity).encode("utf8")),
                 "B8_SELECTED_WORKER_V435_SOURCE_IDENTITY_MISMATCH")
            source_path,package_path=None,None
            actual_key,now=folder.name,identity
        else:
            source_path,package_path=_installed_source_paths(identity)
            actual_key,now=session_key(user,binary,revision,static_cache,
                                   ordinary_variant=variant,
                                   independent_334=independent,
                                   independent_target_level=independent_level,
                                   current_season_product=current_season,
                                   source_catalog_path=source_path,
                                   package_manifest_path=package_path)
        need(actual_key==folder.name and identity==now,
             "SESSION_BINARY_REVISION_OR_CACHE_DRIFT")
        # The child worker must independently verify the exact profile.
        # Parent-side /start validation cannot close the spawn-to-run gap.
        stage_receipt=(folder/"generated"/".stage_receipts"/
                       "v098_target_profile.json")
        use_prepared=stage_receipt.is_file()
        if selected_fresh:
            # New selected route has an independently revalidated v096
            # source replay instead of the old v218 legacy stage receipt.
            use_prepared=True
        if source_path is not None:
            need(use_prepared,"V217_PRODUCT_PROFILE_STAGE_RECEIPT_MISSING")
        if use_prepared and not selected_fresh:
            need("profile_stage" in identity,"V217_STAGE_IDENTITY_MISSING")
            profile_stage.verify_existing(folder,identity)
        cached_before=cache_only_preflight(folder) if cache_only else None
        write_state("RUNNING_CACHE_ONLY" if cache_only else "RUNNING")
        if use_prepared:
            # Reuse the exact Stage-sealed profile/manifest, and hand it
            # straight to the EXISTING bounded SimC optimizer. Do not call
            # v098.build again or generate a second physical profile.
            actual=bootstrap.entry.run_manifest(
                folder/"generated"/"manifest.json",cache_only=cache_only)
            result={"native_result":actual}
        elif variant is None:
            # Preserve historical worker call shape for pre-stage sessions.
            if current_season:
                result=bootstrap.run(folder/"user.json",folder/"generated",
                     binary,revision,static_cache,execute=True,
                     cache_only=cache_only,current_season_product=True)
            elif independent_level:
                result=bootstrap.run(folder/"user.json",folder/"generated",
                     binary,revision,static_cache,execute=True,
                     cache_only=cache_only,independent_target_level=True)
            elif independent:
                result=bootstrap.run(folder/"user.json",folder/"generated",
                     binary,revision,static_cache,execute=True,
                     cache_only=cache_only,independent_334=True)
            else:
                result=bootstrap.run(folder/"user.json",folder/"generated",
                     binary,revision,static_cache,execute=True,cache_only=cache_only)
        else:
            result=bootstrap.run(folder/"user.json",folder/"generated",
                 binary,revision,static_cache,execute=True,cache_only=cache_only,
                 ordinary_variant=variant)
        actual=result["native_result"]
        need(actual["status"].startswith("PASS"),"NATIVE_NOT_PASSED")
        if cache_only:
            need(actual["cache_hits_this_run"]==6 and
                 actual["native_calls_cumulative"]==6,
                 "CACHE_ONLY_SIX_OF_SIX_NOT_VERIFIED")
            need(actual["user_result"]==cached_before["result"]["user_result"],
                 "CACHE_ONLY_DPS_SEM_OR_95_RESULT_DRIFT")
            after=cache_only_preflight(folder)
            need(after["native_sha256"]==cached_before["native_sha256"]
                 and after["progress"]["new_native_attempts"]==
                     cached_before["progress"]["new_native_attempts"],
                 "CACHE_ONLY_NATIVE_BYTES_OR_ATTEMPTS_DRIFT")
        # Do not rewrite result for an unrelated cache identity.
        # Cache-only replay changes cache_hit counters, not the observed
        # Native bytes or 95% user result. Compare the durable semantic
        # result and then refresh the presentation atomically.
        if p["final"].is_file():
            old=json.loads(p["final"].read_text("utf8"))
            need(old["user_result"]==actual["user_result"] and
                 old["base_B"]==actual["base_B"] and
                 old["final_T"]==actual["final_T"] and
                 old["result_path"]==actual["result_path"],
                 "CACHED_USER_RESULT_SEMANTICS_CHANGED")
        stage=p["final"].with_suffix(".tmp")
        stage.write_text(canonical(actual)+"\n",encoding="utf8")
        stage.replace(p["final"])
        if cache_only:
            proof={"schema":CACHE_PROOF_SCHEMA,
                   "status":"PASS_SIX_VERIFIED_CACHE_RESULTS_ZERO_NEW_NATIVE",
                   "cache_hits_this_run":actual["cache_hits_this_run"],
                   "native_calls_cumulative":actual["native_calls_cumulative"],
                   "additional_native_calls":0,
                   "native_json2_sha256":cached_before["native_sha256"],
                   "final_T":actual["final_T"],
                   "observed_dps_mean":
                     actual["user_result"]["observed_first_choice"]["observed_dps_mean"],
                   "observed_sem":
                     actual["user_result"]["observed_first_choice"]["simc_sem"],
                   "confidence_level":0.95,"global_optimum_proven":False}
            proof_file=folder/"V112_CACHE_REPLAY_RECEIPT.json"
            tmp=proof_file.with_suffix(".tmp")
            tmp.write_text(canonical(proof)+"\n",encoding="utf8")
            tmp.replace(proof_file)
        write_state("PASS_CACHE_ONLY" if cache_only else "PASS")
        if cache_only:
            print_user_result("검증된 캐시 6/6 · 추가 Native 0회")
        print_user_result(format_result(actual))
        print_user_result("RESULT_DIR: "+str(folder))
        if os.name=="nt":
            try:os.startfile(str(folder))
            except Exception:pass
        return 0
    except Exception as exc:
        # Distinguish an intentional stop between candidate Native runs from
        # an actual failure. Only the two existing bounded-runner cancellation
        # exception types with the EXACT marker qualify, and only while the
        # local cancel flag still exists. Never convert arbitrary errors to
        # success or alter Native/cache receipts.
        cancelled=(not cache_only and p["cancel"].is_file()
                   and type(exc) in (bootstrap.entry.durable.DurableBlocked,
                                     bootstrap.entry.durable.engine.PipelineBlocked)
                   and str(exc)=="USER_CANCEL_FILE_PRESENT")
        if cancelled:
            write_state("CANCELLED_PARTIAL","USER_CANCEL_FILE_PRESENT")
            print("V106_CANCELLED: USER_CANCEL_FILE_PRESENT",file=sys.stderr,
                  flush=True)
        else:
            write_state("BLOCKED_OR_PARTIAL",type(exc).__name__+":"+str(exc))
            print("V106_BLOCKED:",type(exc).__name__,str(exc),file=sys.stderr,
                  flush=True)
        print("RESULT_DIR:",str(folder),file=sys.stderr,flush=True)
        return 3

def main(argv=None):
    p=argparse.ArgumentParser(description="GUI-independent user Native worker")
    p.add_argument("--session",type=pathlib.Path,required=True)
    p.add_argument("--binary",type=pathlib.Path,required=True)
    p.add_argument("--revision",required=True)
    p.add_argument("--static-cache",type=pathlib.Path)
    p.add_argument("--cache-only",action="store_true")
    a=p.parse_args(argv)
    return worker(a.session,a.binary,a.revision,a.static_cache,a.cache_only)
if __name__=="__main__":sys.exit(main())
