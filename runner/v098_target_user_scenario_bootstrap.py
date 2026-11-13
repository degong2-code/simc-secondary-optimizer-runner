#!/usr/bin/env python3
"""v098 target-level USER inputs -> internally generated v096 source-locked manifest.

Bounded source-backed archetypes: Fury, Frost Mage, Retribution, Beast Mastery,
Subtlety Rogue, and Elemental Shaman.
Not a new item DB, equipment optimizer, SimC effect evaluator or general class
coverage claim. Planning invokes ZERO Native SimC calls.
"""
from __future__ import annotations
import argparse,copy,functools,hashlib,json,pathlib,sys
import v046_static_item_cache as cache_mod
import v055_simc_item_selection as item_mod
import v061_scenario_contract as scenario
import v065_v015_scheduler_adapter as scheduler
import v062_static_budget_bridge as static_budget
import v101_common_representative_equipment as common
import v091_weapon_oil_external_adapter as oil_mod
import v096_unified_product_entry as entry
import v108_native_consumable_inputs as consumer
import v122_common_profile_format as profile_format
import v139_pure_target_profile_composer as pure
import v169_source_first_representative_stage as source_first
import v213_source_to_catalog as original_catalog
import v202_one_enchant_admission as verified_enchant
import v206_nonchmv_eagle_selection as nonchmv_enchant
import v212_environment_manifest as installed_manifest
import v222_season_budget_contract as budget_contract
import v432_selected_4pc_budget_bridge as selected_budget
import v294_dk_runeforge_selection as runeforge_mod

SCHEMA="v098_target_ilevel_user_scenario_v1"
FIELDS={"schema","character","target","trinkets","special_items",
        "embellishments","oil_hands","combat"}
# Backward-compatible public source metadata; ownership moved to v101.
ARCHETYPES=common.ARCHETYPES
# Two source-independent specs now have real Windows adaptive Native 6/6
# receipts each. Do not infer readiness for arbitrary catalog additions.
PURE_PRODUCT_SPECS=frozenset((("druid","balance"),("evoker","devastation")))
FIXTURES=common.FIXTURES
IMPORT_FIELD="import_simc_profile"
CONSUME_FIELD="consumable_choices"
ENCHANT_FIELD="verified_enchant"
SEASON_ENCHANT_FIELD=nonchmv_enchant.FIELD
RUNEFORGE_FIELD="runeforge_by_hand"
STAT_CAP_FIELD="max_single_stat_percent"
TIER_FIVE=common.TIER_FIVE
FIFTH_TIER=common.FIFTH_TIER

@functools.lru_cache(maxsize=1)
def _profile_supplier_registry():
    # Resolve all 26 user-input routes once per process. Contract discovery
    # only: no Native, no network, and no legacy profile text read.
    import v106_user_session_controller as sessions
    contracts=tuple(sorted(source_first.contracts.CONTRACTS))
    legacy=tuple(sorted("/".join(x) for x in ARCHETYPES))
    independent=tuple(sorted("/".join(x) for x in PURE_PRODUCT_SPECS))
    supported=tuple(sorted("/".join(x) for x in sessions.SUPPORTED))
    starters=tuple(sorted(
        set(sessions.starter_examples()) |
        {"/".join(x) for x in sessions.PURE_STARTERS}))
    season_catalog=tuple(sorted(pure.catalog()["specializations"]))
    gear_raw=source_first.gear.DEFAULT.read_bytes()
    tier_raw=source_first.TIER_PATH.read_bytes()
    budget_raw=source_first.BUDGET_PATH.read_bytes()
    gear_doc=json.loads(gear_raw.decode("utf8"))
    tier_doc=json.loads(tier_raw.decode("utf8"))
    digest=lambda raw:hashlib.sha256(raw).hexdigest()
    code_hashes={
        "contracts":digest(pathlib.Path(source_first.contracts.__file__).read_bytes()),
        "profile_composer":digest(pathlib.Path(pure.__file__).read_bytes()),
        "user_session":digest(pathlib.Path(sessions.__file__).read_bytes()),
        "season_stage":digest(pathlib.Path(source_first.__file__).read_bytes()),
    }
    return {"contracts":contracts,"legacy_source_backed":legacy,
            "source_independent":independent,"user_input":supported,
            "starter_defaults":starters,"season_catalog":season_catalog,
            "season_build":gear_doc["season_build"],
            "tier_build":tier_doc["retail_build"],
            "source_input_sha256":{
                "gear":digest(gear_raw),"tier":digest(tier_raw),
                "budget":digest(budget_raw)},
            "supplier_code_sha256":code_hashes}


def _current_season_profile_supplier_coverage(season_override, selected_key, *,
                                              one_spec_only=False):
    need(type(season_override) is dict and
         type(season_override.get("specializations")) is dict,
         "CURRENT_SEASON_PROFILE_SUPPLIER_CATALOG_MISSING")
    registry=_profile_supplier_registry()
    expected=registry["contracts"]
    supplied=tuple(sorted(season_override["specializations"]))
    need(set(registry["legacy_source_backed"]) |
         set(registry["source_independent"]) == set(expected) and
         set(registry["legacy_source_backed"]).isdisjoint(
             registry["source_independent"]),
         "PROFILE_SUPPLIER_LEGACY_AND_PURE_COVERAGE_DRIFT")
    for name in ("user_input","starter_defaults","season_catalog"):
        need(registry[name] == expected,
             "PROFILE_SUPPLIER_REGISTRY_DRIFT:"+name)
    need((supplied == (selected_key,) if one_spec_only else
          supplied == expected),
         "CURRENT_SEASON_PROFILE_SUPPLIER_SET_DRIFT")
    need(selected_key in supplied,
         "SELECTED_SPEC_HAS_NO_CURRENT_SEASON_PROFILE_SUPPLIER")
    need(registry["season_build"]==registry["tier_build"],
         "PROFILE_SUPPLIER_GEAR_TIER_BUILD_MISMATCH")
    return {
        "schema":"v215_profile_supplier_coverage_v1",
        "status":"CURRENT_SEASON_PLAN_SUPPLIERS_26_OF_26",
        "supported_specializations":list(expected),
        "contract_count":len(registry["contracts"]),
        "legacy_source_backed_count":len(registry["legacy_source_backed"]),
        "source_independent_count":len(registry["source_independent"]),
        "user_input_default_count":len(registry["user_input"]),
        "starter_default_count":len(registry["starter_defaults"]),
        "season_catalog_count":len(registry["season_catalog"]),
        "current_season_profile_supplier_count":len(supplied),
        "selected_specialization":selected_key,
        "selected_specialization_plan_supplier":True,
        "season_build":registry["season_build"],
        "source_input_sha256":registry["source_input_sha256"],
        "supplier_code_sha256":registry["supplier_code_sha256"],
        # Supplier/plan coverage is not full adaptive DPS acceptance.
        "all_specs_ready":False,
        "adaptive_native_evidence_complete":False,
        "native_calls":0,
        "network_calls":0,
    }


def reconcile_four_tier(key,rows,groups,taken,ilevel):
    return common.reconcile_four_tier(key,rows,groups,taken,ilevel,need)

def character_from_uploaded_simc(text):
    """Only four character fields are imported; ALL worn-gear rows are ignored.

    Duplicate/ambiguous SimC character assignments fail closed. This is a
    narrow selector, not a generic SimC parser or profile-equipment import.
    """
    need(type(text) is str and bool(text.strip()),"SIMC_IMPORT_TEXT_REQUIRED")
    found={name:[] for name in ("spec","race","talents")}
    classes=[]
    for line in text.splitlines():
        line=line.strip()
        if not line or line.startswith("#") or "=" not in line:continue
        key,_,value=line.partition("=")
        if key in scenario.CLASSES:
            need(bool(value.strip()),"SIMC_IMPORT_EMPTY_CLASS_DECLARATION")
            classes.append(key)
        if key in found:found[key].append(value)
    need(len(classes)==1 and all(len(found[k])==1 for k in found),
         "SIMC_IMPORT_CHARACTER_INCOMPLETE_OR_AMBIGUOUS")
    for name,rows in found.items():
        scenario.text_token(rows[0],"IMPORTED_"+name.upper())
    return {"class":classes[0],"spec":found["spec"][0],
            "race":found["race"][0],"talents":found["talents"][0]}

class UserScenarioBlocked(ValueError):pass
def need(ok,why):
    if not ok:raise UserScenarioBlocked(why)
def canonical(obj):
    return json.dumps(obj,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False)
def put_once(path,content):
    data=content.encode("utf8") if isinstance(content,str) else content
    if path.exists():
        need(path.read_bytes()==data,"EXISTING_BOOTSTRAP_FILE_CHANGED:"+path.name)
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)

def replace_assignments(profile,settings,slots):
    result=[];seen=set();gear=set()
    for line in profile.splitlines():
        key,sep,_=line.partition("=")
        if sep and key in item_mod.SLOTS:
            need(key not in gear,"TEMPLATE_DUPLICATE_SLOT:"+key)
            gear.add(key)
            continue
        if sep and key in settings:
            need(key not in seen,"TEMPLATE_DUPLICATE_SETTING:"+key)
            seen.add(key)
            result.append(key+"="+settings[key])
            continue
        result.append(line)
    need(gear==set(slots),"TEMPLATE_GEAR_SLOT_DRIFT")
    need({"spec","race","talents","role","fight_style","desired_targets",
          "max_time","optimal_raid"}<=seen,"TEMPLATE_REQUIRED_SETTINGS_MISSING")
    for slot,row in slots.items():
        result.append(item_mod.equipment_line(slot,row["item_id"],
                      row["ilevel"],row["options"]))
    return "\n".join(result).rstrip()+"\n"

def preserve_existing_v104_gear_order(key,rows,folder):
    """Read-only replay compatibility for a previously sealed v104 plan.

    Earlier v104 used tuple(set_of_slots); separately spawned Python workers
    could emit the SAME item lines in a different order. The existing profile
    is never edited or trusted as replacement content: only slot order is
    recovered, and put_once still requires the complete bytes to match.
    """
    if key not in (("rogue","subtlety"),("shaman","elemental")):
        return rows
    prior=folder/"profile.simc"
    if not prior.is_file():
        return rows
    order=[]
    for line in prior.read_text(encoding="utf8").splitlines():
        slot,sep,_=line.partition("=")
        if sep and slot in item_mod.SLOTS:
            order.append(slot)
    need(len(order)==len(rows) and set(order)==set(rows),
         "EXISTING_BOOTSTRAP_GEAR_SLOT_ORDER_INVALID")
    return {slot:rows[slot] for slot in order}

def initial_seeds(B,lower,upper):
    """Only two feasible deterministic start vectors for existing scheduler."""
    need(type(B) is int and all(type(n) is int for n in lower+upper),
         "BAD_SEED_BOUNDS")
    need(sum(lower)<=B<=sum(upper),"B_SEED_UNFEASIBLE")
    def fill(order):
        a=list(lower);left=B-sum(a)
        while left:
            moved=False
            for k in order:
                if left and a[k]<upper[k]:
                    a[k]+=1;left-=1;moved=True
            need(moved,"SEED_CAP_EXHAUSTED")
        return tuple(a)
    first=fill((0,1,2,3))
    # Start meaningfully apart where allowed (about 10% of B moved).
    # This is only seed diversification, NOT a new search/optimizer.
    second=first
    desired=max(1,(B+9)//10)
    for i in range(4):
        if second!=first:break
        for j in range(4):
            if i==j:continue
            transferable=min(desired,first[i]-lower[i],upper[j]-first[j])
            if transferable>0:
                a=list(first);a[i]-=transferable;a[j]+=transferable
                second=tuple(a)
                break
    need(first!=second and all(scheduler.eligible(x,B,lower,upper)
                             for x in (first,second)),
         "TWO_DISTINCT_ELIGIBLE_SEEDS_UNAVAILABLE")
    return [dict(zip(scenario.STATS,v)) for v in (first,second)]


def _v191_raw_gear_tier_link(bundle, originals, revision):
    """Read-only original v191/v213 gear/tier SHA binding for source preview.

    The source compiler already sealed these original bytes. This verifies
    that the replaceable v098 documents are precisely those same raw inputs.
    It never grants environment READY, policy A, or Native admission.
    """
    need(type(originals) is dict and
         set(originals)=={"catalog","gear","tier"},
         "SEASON_V191_ORIGINAL_SOURCE_PATHS_REQUIRED")
    files={}; raw={}
    for name in ("catalog","gear","tier"):
        value=originals[name]
        need(isinstance(value,(str,pathlib.Path)),
             "SEASON_V191_ORIGINAL_SOURCE_PATH_INVALID")
        path=pathlib.Path(value).expanduser()
        need(path.is_file() and not path.is_symlink() and
             0<path.stat().st_size<=12_000_000,
             "SEASON_V191_ORIGINAL_SOURCE_UNSAFE_OR_MISSING")
        files[name]=path.resolve()
    root=files["catalog"].parent.parent
    need(files["catalog"].parent.name=="fresh_source" and
         files["catalog"].name=="v213_candidate_catalog.json" and
         all(files[k].is_relative_to(root) for k in ("gear","tier")),
         "SEASON_V191_SOURCES_OUTSIDE_ORIGINAL_STAGE")
    try:
        for name,path in files.items():
            raw[name]=path.read_bytes()
        catalog=json.loads(raw["catalog"])
        original_catalog.verify_catalog(catalog)
        expected=catalog["source_provenance"]["v191"]["sha256_by_input"]
        need(type(expected) is dict and expected.get("budget") is None,
             "SEASON_V191_FRESH_BUDGET_SOURCE_REQUIRED")
        need(catalog["game_build"]==bundle["gear"]["season_build"]==
             bundle["tier"]["retail_build"] and
             catalog["simc_revision"]==revision,
             "SEASON_V191_ORIGINAL_BUILD_OR_REVISION_DRIFT")
        sha={}
        for name in ("gear","tier"):
            sha[name]=hashlib.sha256(raw[name]).hexdigest()
            need(sha[name]==expected.get(name) and
                 json.loads(raw[name])==bundle[name],
                 "SEASON_V191_"+name.upper()+"_RAW_SHA_OR_BYTES_DRIFT")
    except (OSError,ValueError,KeyError,TypeError,
            original_catalog.CatalogBlocked) as exc:
        if isinstance(exc,UserScenarioBlocked):
            raise
        raise UserScenarioBlocked(
            "SEASON_V191_ORIGINAL_SOURCE_NOT_VERIFIED") from exc
    return {"schema":"v098_v191_original_gear_tier_link_v1",
            "status":"ORIGINAL_GEAR_TIER_RAW_SHA_LINKED_PREVIEW_ONLY",
            "source_catalog_artifact_sha256":hashlib.sha256(
                raw["catalog"]).hexdigest(),
            "source_catalog_manifest_sha256":catalog["manifest_sha256"],
            "raw_source_sha256":sha,
            "environment_ready":False,"native_authorized":False}




def _selected_season_profile_budget_preflight(*, user, profile, cfg, rows,
                                              groups, catalyst, baseline_rows,
                                              candidate, class_tier_five, original_v191_link,
                                              installed_path, cache_path):
    """Bind actual v101 overlaid user profile to v432 G/L: NO session/Native.

    This is deliberately separate from v096. Existing v212 installed G is a
    representative reference, not the selected user G. A v432 delta cannot
    be silently passed to the old unselected v096 source admission contract.
    """
    need(type(candidate) is dict and
         type(candidate.get("selected_G_slot_ids")) is dict and
         type(original_v191_link) is dict and
         type(baseline_rows) is dict,
         "B8_SELECTED_PROFILE_ORIGINAL_V232_V191_SOURCES_REQUIRED")
    cache_file=pathlib.Path(cache_path).expanduser()
    need(cache_file.is_file() and not cache_file.is_symlink() and
         0<cache_file.stat().st_size<=25_000_000,
         "B8_SELECTED_STATIC_CACHE_SOURCE_FILE_REQUIRED")
    raw=cache_file.read_bytes()
    need(0<len(raw)<=25_000_000,
         "B8_SELECTED_STATIC_CACHE_SOURCE_BYTES_INVALID")
    try:
        cached=json.loads(raw)
        cache_mod.check_cache(cached)
    except (ValueError,TypeError,KeyError,UnicodeError) as exc:
        raise UserScenarioBlocked(
            "B8_SELECTED_EXACT_STATIC_CACHE_INVALID:"+type(exc).__name__) from exc
    # Same-season v046 static entries are independent of the SimC revision.
    # A different cache season needs an explicit verified owner migration;
    # never assume its identically named item IDs are equivalent.
    need(cached["season"]==cache_mod.SEASON,
         "B8_SELECTED_CACHE_SEASON_NOT_VERIFIED_FOR_CURRENT_BUILD")
    install=pathlib.Path(installed_path).expanduser()
    need(install.is_file() and not install.is_symlink(),
         "B8_SELECTED_VERIFIED_INSTALL_FILE_REQUIRED")
    doc,_=installed_manifest.read_json(install)
    installed_manifest.verify_fresh_installed_environment(doc)
    need(doc["game_build"]==candidate.get("game_build") and
         doc["target_ilevel"]==user["target"]["ilevel"] and
         doc["simc_revision"]==candidate.get("simc_revision"),
         "B8_SELECTED_INSTALLED_BUILD_REVISION_OR_ILEVEL_DRIFT")
    selected_equipment,_=common.physical_gear_groups(
        rows,groups,catalyst)
    need(cfg.get("equipment")==selected_equipment and
         cfg.get("source",{}).get("profile_sha256")==
             hashlib.sha256(profile.encode("utf8")).hexdigest(),
         "B8_SELECTED_PHYSICAL_PROFILE_EQUIPMENT_OR_SHA_DRIFT")
    try:
        proof=selected_budget.reconcile(
            baseline_rows=baseline_rows,
            final_rows=rows,final_groups=groups,user=user,
            class_tier_five=class_tier_five,
            baseline_slot_ids=candidate["selected_G_slot_ids"],
            installed_document=doc,
            original_v191_link=original_v191_link,
            native_cache=cached,
            expected_cache_season=cache_mod.SEASON)
    except selected_budget.SelectedBudgetBlocked as exc:
        raise UserScenarioBlocked(
            "B8_SELECTED_G_L_PREFLIGHT_BLOCKED:"+str(exc)) from exc
    profile_sha=cfg["source"]["profile_sha256"]
    budget_identity=proof.get("selected_budget_identity_sha256")
    bound={
        "schema":"v433_b8_selected_profile_budget_source_binding_v1",
        "installed_v212_manifest_sha256":doc["manifest_sha256"],
        "original_v191_raw_gear_tier_sha256":
            original_v191_link["raw_source_sha256"],
        "selected_v232_receipt_sha256":candidate["receipt_sha256"],
        "selected_profile_sha256":profile_sha,
        "static_cache_content_sha256":hashlib.sha256(raw).hexdigest(),
        "selected_budget_identity_sha256":budget_identity,
        "physical_equipment_sha256":hashlib.sha256(
            canonical(selected_equipment).encode("utf8")).hexdigest(),
    }
    bind_sha=hashlib.sha256(canonical(bound).encode("utf8")).hexdigest()
    return {
        "schema":"v433_v098_selected_user_physical_budget_preflight_v1",
        "status":("B8_SELECTED_PROFILE_STATIC_VARIANTS_PENDING_NO_NATIVE"
                  if proof["missing_exact_native_variants"] else
                  "B8_SELECTED_PROFILE_BUDGET_RECONCILED_NOT_ADMITTED"),
        "source_profile_sha256":profile_sha,
        "profile_simc":profile,
        "scenario_source_only":cfg,
        "selected_equipment":selected_equipment,
        "budget_preflight":proof,
        "bound_source_identity":bound,
        "bound_source_identity_sha256":bind_sha,
        "runtime_manifest_created":False,
        "native_execution_authorized":False,
        "environment_ready_for_selected_user":False,
        "user_session_created":False,
        "static_cache_modified":False,
        "native_calls":0,
        "network_calls":0,
    }


def _verified_one_spec_G_profile_scope(*, source_bundle, candidate,
                                      selected_key, target_ilevel, source_revision):
    """Build the selected v139 physical profile from ORIGINAL v232 G items.

    The actual v216/v217/v212 READY path is required by the calling
    v098 writer. Do not use v169's unrelated all-26 plain-neck selection,
    copy historical gear, infer same-season membership or redo Native G.
    """
    import v232_simc_only_ordinary_representative as physical
    need(type(candidate) is dict and
         candidate.get("schema")==physical.SCHEMA and
         candidate.get("status")==
             "SIMC_SOURCE_PHYSICAL_CANDIDATE_NOT_ACTUAL_SEASON_PROOF" and
         candidate.get("receipt_sha256")==physical.seed.digest(
             physical.seed.canonical({
                 k:v for k,v in candidate.items()
                 if k!="receipt_sha256"}).encode("utf8")) and
         type(candidate.get("selected_G_slot_ids")) is dict,
         "FRESH_V232_ORIGINAL_G_PROFILE_SOURCE_RECEIPT_INVALID")
    cls,spec=selected_key
    key=cls+"/"+spec
    gear=source_bundle["gear"]
    tier=source_bundle["tier"]
    need(candidate.get("game_build")==gear["season_build"]==
             tier["retail_build"] and
         candidate.get("simc_revision")==source_revision and
         candidate.get("target_ilevel")==target_ilevel and
         candidate.get("character",{}).get("class")==cls and
         candidate.get("character",{}).get("spec")==spec,
         "FRESH_V232_SELECTED_G_BUILD_SPEC_OR_ILEVEL_DRIFT")
    tier_ids=tier["classes"][cls]["pieces"]
    four=source_first.FOUR
    selected={**{slot:tier_ids[slot] for slot in four},
              **candidate["selected_ordinary"],
              **candidate["selected_common"],
              **candidate["selected_weapons"]}
    need(selected==candidate["selected_G_slot_ids"] and
         set(candidate["selected_common"])==set(source_first.COMMON) and
         set(candidate["selected_ordinary"])==set(source_first.ORDINARY),
         "FRESH_V232_USER_PHYSICAL_G_SLOT_DRIFT")
    config=source_bundle["settings"]
    original=pure.validate_season(config)
    scope={name:copy.deepcopy(original[name]) for name in
           ("schema","season","target_ilevel","character_level",
            "gems","default_consumables")}
    if original.get("simc_item_db_source") is not None:
        scope["simc_item_db_source"]=original["simc_item_db_source"]
    scope["common_gear"]=dict(candidate["selected_common"])
    scope["specializations"]={key:{
        "tier_ids":dict(tier_ids),
        "four_tier_slots":list(four),
        "ordinary":dict(candidate["selected_ordinary"]),
        "weapons":dict(candidate["selected_weapons"])}}
    need(scope["target_ilevel"]==target_ilevel,
         "FRESH_V232_PROFILE_SETTINGS_TARGET_DRIFT")
    pure.validate_season(scope)
    return scope



def season_profile_source_only(*, profile, cfg, weapon_layout, user,
                               season_profile_inputs, season_build,
                               simc_revision, fillers=None):
    """Season-neutral v098 profile composition from v216 numeric preview.

    This route reuses v108 J/F and v091 O serializers. It is purposely
    not executable: v216 source-only ratings and the pinned gear supplier
    cannot be promoted into the old v096/v094 runtime or Policy A.
    """
    need(type(season_profile_inputs) is dict and
         set(season_profile_inputs)=={
             "schema","v216_numeric_preview","flask","oil_by_hand"}
         and season_profile_inputs["schema"]==
             "v098_internal_season_profile_inputs_v1",
         "SEASON_PROFILE_INPUT_SCHEMA_REQUIRED")
    v216=season_profile_inputs["v216_numeric_preview"]
    need(type(v216) is dict and v216.get("schema")==(
             "v216_zero_history_selected_v222_numeric_preview_v1")
         and v216.get("status")==(
             "SELECTED_GJFO_V222_ARITHMETIC_PREVIEW_UNADMITTED")
         and v216.get("numeric_preview_only") is True
         and v216.get("source_authenticated") is False
         and v216.get("environment_ready") is False
         and type(v216.get("calculation")) is dict,
         "SEASON_PROFILE_REQUIRES_UNADMITTED_V216_PREVIEW")
    budget=v216["calculation"]
    selected=v216.get("selected_physical_items")
    need(type(selected) is dict and type(user) is dict
         and type(season_build) is str
         and budget.get("game_build")==season_build
         and budget.get("simc_revision")==simc_revision
         and budget.get("target_ilevel")==user["target"]["ilevel"]
         and budget.get("numeric_preview_only") is True
         and budget.get("source_authentication_performed_here") is False
         and type(budget.get("J")) is int
         and type(budget.get("F")) is int,
         "SEASON_PROFILE_GEAR_BUILD_OR_BUDGET_DRIFT")
    flask=season_profile_inputs["flask"]
    need(type(flask) is dict and
         set(flask)=={"physical_item_id","simc_input_token",
                      "static_CHMV_vector"}
         and flask.get("physical_item_id")==selected.get("flask_item_id"),
         "SEASON_PROFILE_FLASK_ITEM_ID_DRIFT")
    # v096/v094 require the exact per-stat F vector, not just scalar F.
    # Reuse original v278 Native baseline/active static CHMV observations.
    native_flask_vector=scenario.vector(
        flask["static_CHMV_vector"],"SEASON_SELECTED_FLASK_NATIVE_F")
    need(sum(native_flask_vector.values())==budget["F"],
         "SEASON_PROFILE_FLASK_NATIVE_VECTOR_SUM_DRIFT")
    by_hand=season_profile_inputs["oil_by_hand"]
    need(type(by_hand) is dict
         and type(selected.get("oil_item_ids_by_hand")) is dict
         and set(by_hand)==set(selected["oil_item_ids_by_hand"])
         and sorted(by_hand)==sorted(user["oil_hands"])
         and all(type(row) is dict and
                 row.get("physical_item_id")==
                     selected["oil_item_ids_by_hand"][hand]
                 for hand,row in by_hand.items()),
         "SEASON_PROFILE_OIL_PHYSICAL_ITEMS_OR_HANDS_DRIFT")
    if user["target"]["final_T"] is not None:
        need(budget.get("final_T")==user["target"]["final_T"]
             and budget.get("manual_final_T_authoritative") is True,
             "SEASON_PROFILE_MANUAL_FINAL_T_DRIFT")
    else:
        need(budget.get("manual_final_T_authoritative") is False,
             "SEASON_PROFILE_AUTO_TARGET_DRIFT")
    fixed_o=budget.get("fixed_O")
    need(type(fixed_o) is dict and
         type(budget.get("base_B")) is int
         and type(budget.get("final_T")) is int
         and budget["base_B"]+sum(fixed_o.values())==
             budget["final_T"],
         "SEASON_PROFILE_B_PLUS_O_DRIFT")
    consumed=consumer.season_static_consumables_source_only(
        profile,cfg,gem_budget_J=budget["J"],
        flask_budget_F=budget["F"],
        flask_item_id=flask["physical_item_id"],
        flask_simc_token=flask["simc_input_token"])
    configured=oil_mod.configure(
        consumed["profile"],consumed["scenario"],
        weapon_layout,user["oil_hands"],
        season_oil_by_hand={
            hand:{"physical_item_id":row["physical_item_id"],
                  "simc_input_token":row["simc_input_token"],
                  "static_CHMV_vector":row["static_CHMV_vector"]}
            for hand,row in by_hand.items()})
    need(configured["declared_O"]==fixed_o
         and configured["scenario"]["consumables"]["gem_budget_J"]==
             budget["J"]
         and configured["scenario"]["consumables"]["flask_budget_F"]==
             budget["F"]
         and configured["applied_hands"]==[
             hand for hand in ("main_hand","off_hand") if hand in by_hand],
         "SEASON_PROFILE_FIXED_J_F_O_OR_SERIALIZATION_DRIFT")
    # v061's legacy "T" is officially the free B and explicitly EXCLUDES
    # external O. Bind original v222 B as a typed manual_total regardless of
    # whether the user selected an automatic ilevel target or manual final T.
    # This is a scenario draft ONLY: no v089 old-season 79x2 reference and
    # no new session/Native/cache are permitted from unadmitted source data.
    typed=copy.deepcopy(configured["scenario"])
    typed["target"]={
        "mode":"manual_total","ilevel":budget["target_ilevel"],
        "manual_total":budget["base_B"],
        "manual_total_scope":scenario.MANUAL_TOTAL_SCOPE}
    typed_plan=scenario.normalize(typed)
    need(typed_plan["budget"]["T"]==budget["base_B"]
         and typed_plan["budget"]["J"]==budget["J"]
         and typed_plan["budget"]["F"]==budget["F"]
         and typed_plan["budget"]["external_temporary_rating"]==fixed_o
         and typed_plan["scenario"]["source"]["profile_sha256"]==
             configured["profile_sha256"]
         and typed_plan["scenario"]["equipment"]==
             scenario.normalize(configured["scenario"])["scenario"]["equipment"],
         "SEASON_PROFILE_TYPED_BASE_B_OR_SOURCE_DRIFT")
    # Reuse the actual v062 static-L budget and v065 feasibility floors
    # with the typed B and exact F/O vectors. This is the same deterministic
    # seed planning policy the existing runnable v098/v096 path uses; a
    # source-only plan is NEVER a Native or Policy A authorization.
    seed_plan=None
    if fillers is not None:
        need(type(fillers) is list,
             "SEASON_PROFILE_EXACT_FILLERS_REQUIRED")
        compiled=static_budget.compile_static_budget(
            typed_plan,fillers,cache_mod.empty_cache())
        feasible=scheduler.budget_with_fixed_components(
            typed_plan,compiled,native_flask_vector,fixed_o)
        planned_B,lower,upper=scheduler.bounds(typed_plan,feasible)
        need(planned_B==budget["base_B"],
             "SEASON_PROFILE_ADAPTIVE_BASE_B_DRIFT")
        seeds=initial_seeds(planned_B,lower,upper)
        seed_plan={
            "schema":"v098_v065_unadmitted_seed_plan_v1",
            "status":"EXISTING_ADAPTIVE_SEEDS_SOURCE_ONLY",
            "seed_targets_B":seeds,
            "base_B":planned_B,
            "lower_B":dict(zip(scenario.STATS,lower)),
            "upper_B":dict(zip(scenario.STATS,upper)),
            "source_profile_sha256":configured["profile_sha256"],
            "scenario_digest":typed_plan["scenario_digest"],
            "runtime_native_authorized":False}
    typed_input={
        "schema":"v098_unadmitted_v096_typed_input_v1",
        "scenario":typed_plan["scenario"],
        "scenario_digest":typed_plan["scenario_digest"],
        "base_B":budget["base_B"],"final_T":budget["final_T"],
        "fixed_O":dict(fixed_o),"flask_F":dict(native_flask_vector),
        "source_profile_sha256":configured["profile_sha256"],
        "adaptive_seed_plan_unadmitted":seed_plan,
        "source_status":"UNADMITTED_NUMERIC_PREVIEW_ONLY",
        "runtime_manifest_created":False,
        "native_execution_authorized":False}
    return {
        "schema":"v098_source_only_season_profile_plan_v1",
        "status":"SEASON_PROFILE_COMPOSED_NOT_ADMITTED_NO_NATIVE",
        "profile_simc":configured["profile"],
        "scenario":configured["scenario"],
        "source_profile_sha256":configured["profile_sha256"],
        "v096_typed_input_unadmitted":typed_input,
        "budget_preview_unadmitted":budget,
        "same_season_build":season_build,
        "official_B_T_formula":"B=G+J+F;T=B+O",
        "user_does_not_choose_all_gear":True,
        "source_data_never_promoted_to_runtime":True,
        "source_authentication_performed_here":False,
        "policy_A_options_registered":False,
        "environment_ready":False,"user_session_created":False,
        "adaptive_v094_started":False,
        "new_native_calls":0,"network_calls":0}



def _materialize_admitted_season_v096(*, source_only,season_profile_inputs,
                                     season_environment_receipt_path,folder,
                                     binary,revision,static_cache_path,
                                     weapon_layout,fillers,user,ilevel,rows,key,
                                     fresh_installed_environment_path=None,
                                     original_v191_link=None,
                                     exploration_policy=None):
    """Reuse the ORIGINAL v096 manifest+durable v094 route for an admitted season.

    A non-admitted v216 numeric draft can never reach this writer. The
    existing v216/v223 receipt and original v096's own source checks remain
    authoritative. No new season quality, proc or item-effect certification.
    """
    need(type(source_only) is dict and
         source_only.get("status")==(
             "SEASON_PROFILE_COMPOSED_NOT_ADMITTED_NO_NATIVE")
         and type(source_only.get("v096_typed_input_unadmitted")) is dict
         and static_cache_path is None,
         "SEASON_WRITER_PLAIN_SOURCE_ONLY_PROFILE_REQUIRED")
    draft=source_only["v096_typed_input_unadmitted"]
    seed=draft.get("adaptive_seed_plan_unadmitted")
    need(type(seed) is dict and seed.get("schema")==(
             "v098_v065_unadmitted_seed_plan_v1")
         and seed.get("runtime_native_authorized") is False
         and len(seed.get("seed_targets_B",[]))==2,
         "SEASON_WRITER_ORIGINAL_SEED_PLAN_REQUIRED")
    receipt_path=pathlib.Path(
        fresh_installed_environment_path if
        fresh_installed_environment_path is not None else
        season_environment_receipt_path).resolve()
    need(receipt_path.is_file() and not receipt_path.is_symlink(),
         "SEASON_WRITER_INSTALLED_RECEIPT_REQUIRED")
    if fresh_installed_environment_path is None:
        import v216_environment_build_coordinator as existing_environment
        original_receipt=existing_environment.read_receipt(receipt_path)
        source_sha=original_receipt["receipt_sha256"]
        manifest_source={
            "schema":entry.SEASON_SCHEMA,
            "environment_receipt_path":str(receipt_path),
            "environment_receipt_sha256":source_sha,
            "oil_by_hand":copy.deepcopy(
                season_profile_inputs["oil_by_hand"])}
        source=entry._admitted_season_source(
            manifest_path=folder/"manifest.json",season=manifest_source,
            revision=revision,user_scenario=draft["scenario"],
            flask_F=draft["flask_F"],oil_hands=user["oil_hands"])
        source_field=entry.SEASON_FIELD
    else:
        import v212_environment_manifest as installed_manifest
        doc,_=installed_manifest.read_json(receipt_path)
        installed_manifest.verify_fresh_installed_environment(doc)
        need(type(original_v191_link) is dict and
             original_v191_link.get("source_catalog_artifact_sha256")==
                 doc["source_catalog_artifact_sha256"] and
             original_v191_link.get("source_catalog_manifest_sha256")==
                 doc["source_catalog_manifest_sha256"] and
             doc["target_ilevel"]==ilevel,
             "FRESH_SEASON_V191_GEAR_TIER_AND_INSTALLED_CATALOG_DRIFT")
        source_sha=doc["manifest_sha256"]
        manifest_source={
            "schema":entry.FRESH_SEASON_SCHEMA,
            "installed_environment_path":str(receipt_path),
            "installed_manifest_sha256":source_sha,
            "oil_by_hand":copy.deepcopy(
                season_profile_inputs["oil_by_hand"]),
            **({"user_final_T":user["target"]["final_T"]}
               if user["target"]["final_T"] is not None else {})}
        source=entry._admitted_fresh_season_source(
            manifest_path=folder/"manifest.json",season=manifest_source,
            revision=revision,user_scenario=draft["scenario"],
            flask_F=draft["flask_F"],oil_hands=user["oil_hands"],
            profile=source_only["profile_simc"])
        source_field=entry.FRESH_SEASON_FIELD
    # Original v096 source and all v217/v212 seals are checked before
    # writing mutable user session files or planning Native execution.
    approved=source["season_budget"]
    draft_budget=source_only["budget_preview_unadmitted"]
    need(all(draft_budget.get(k)==approved.get(k)
             for k in ("game_build","simc_revision",
                       "source_catalog_manifest_sha256",
                       "source_catalog_artifact_sha256",
                       "target_ilevel","base_B","final_T",
                       "J","F","fixed_O"))
         and draft["base_B"]==approved["base_B"]
         and draft["final_T"]==approved["final_T"]
         and draft["fixed_O"]==approved["fixed_O"]
         and source_only["same_season_build"]==
             approved["game_build"]
         and draft["source_profile_sha256"]==
             source_only["source_profile_sha256"]
         and seed["base_B"]==draft["base_B"],
         "SEASON_WRITER_V216_V098_SOURCE_ACCOUNTING_DRIFT")
    manifest={"schema":entry.SCHEMA,
              "profile_simc":"profile.simc",
              "scenario_json":"scenario.json",
              "fillers_json":"fillers.json",
              "static_cache_json":None,
              "weapon_layout":weapon_layout,
              "oil_hands":user["oil_hands"],
              "flask_F":draft["flask_F"],
              "seed_targets_B":seed["seed_targets_B"],
              "native_binary":str(binary),
              "native_revision":revision,
              "output_dir":"simc_results",
              "scouts":1,"material_scouts":1,
              "native_limit":6,"step":100,
              "cancel_file":"CANCEL",
              source_field:manifest_source,
              **({entry.EXPLORATION_FIELD:exploration_policy}
                 if exploration_policy is not None else {})}
    files={
        "profile.simc":source_only["profile_simc"],
        "scenario.json":canonical(draft["scenario"])+"\n",
        "fillers.json":canonical(fillers)+"\n",
        "manifest.json":canonical(manifest)+"\n"}
    # Precheck ALL existing bytes before writing any new file. The original
    # V094_SESSION_IDENTITY is never replaced, even if B/T happen to match.
    for name,content in files.items():
        dest=folder/name
        need(not dest.is_symlink() and
             (not dest.exists() or
              dest.is_file() and dest.read_bytes()==content.encode("utf8")),
             "SEASON_WRITER_EXISTING_SESSION_SOURCE_CHANGED:"+name)
    for name,content in files.items():
        put_once(folder/name,content)
    plan=entry.run_manifest(folder/"manifest.json",plan_only=True)
    need(plan.get("budget_source")==(
             "ADMITTED_FRESH_SEASON_GJFO_V212_V217" if
             fresh_installed_environment_path is not None else
             "ADMITTED_SEASON_GJFO_V216_V223")
         and plan["base_B"]==draft["base_B"]
         and plan["final_T"]==draft["final_T"]
         and plan["fixed_O"]==draft["fixed_O"]
         and plan.get("season_source_receipt_sha256")==
             source_sha
         and plan["item_slots"]==len(rows),
         "SEASON_WRITER_V096_ORIGINAL_PLAN_DRIFT")
    return {
        "schema":SCHEMA,
        "status":"READY_SOURCE_BOUND_SEASON_MANIFEST_ZERO_NATIVE",
        "generated_manifest":str(folder/"manifest.json"),
        "output_dir":str(folder/"simc_results"),
        "plan":plan,
        "season_environment_receipt_sha256":source_sha,
        **({"original_v191_gear_tier_source_unadmitted":original_v191_link}
           if original_v191_link is not None else {}),
        "user_does_not_supply_full_gear_or_simc_profile":True,
        "season_source_not_full_policy_A_option_coverage":True,
        "fresh_v212_installed_proof_reused":
            fresh_installed_environment_path is not None,
        "existing_v096_v094_execution_reused":True,
        "native_calls":0,
        "source_authentication_created_here":False}


def build(user,folder,binary,revision,static_cache_path=None,
          imported_profile_text=None,*,ordinary_variant=None,pure_stage=False,
          independent_334=False,independent_target_level=False,
          source_first_stage=False,current_season_product=False,
          static_special_probe_only=False,source_catalog_path=None,
          season_profile_inputs=None,season_environment_receipt_path=None,
          season_source_bundle=None,season_original_source_paths=None,
          season_socket_plan=None,fresh_installed_environment_path=None,
          season_physical_one_spec_candidate=None,
          season_selected_static_cache_path=None,
          exploration_policy=None):
    """Return an already validated internal manifest and v096 plan; no Native."""
    base_accepted=(FIELDS,FIELDS|{IMPORT_FIELD},FIELDS|{CONSUME_FIELD},
                   FIELDS|{IMPORT_FIELD,CONSUME_FIELD})
    # Existing Linux-pinned fixed-E pilot and one source-classified nonCHMV
    # user choice are separate; never combine them in one stage.
    accepted=(base_accepted+
              tuple(x|{ENCHANT_FIELD} for x in base_accepted)+
              tuple(x|{SEASON_ENCHANT_FIELD} for x in base_accepted))
    accepted=accepted+tuple(x|{RUNEFORGE_FIELD} for x in accepted)
    accepted=accepted+tuple(x|{STAT_CAP_FIELD} for x in accepted)
    need(type(user) is dict and set(user) in accepted
         and user.get("schema")==SCHEMA,"USER_SCENARIO_FIELDS")
    if STAT_CAP_FIELD in user:
        need(type(user[STAT_CAP_FIELD]) is int and
             25<=user[STAT_CAP_FIELD]<=100,
             "MAX_SINGLE_STAT_PERCENT_25_TO_100")
    using_import=IMPORT_FIELD in user
    if using_import:
        need(type(user[IMPORT_FIELD]) is str and bool(user[IMPORT_FIELD].strip()),
             "SIMC_IMPORT_PATH_REQUIRED")
        need(user["character"] is None,"SIMC_IMPORT_AND_MANUAL_CHARACTER_AMBIGUOUS")
        ch=character_from_uploaded_simc(imported_profile_text)
    else:
        need(imported_profile_text is None,"UNREQUESTED_IMPORTED_PROFILE")
        ch=user["character"]
    need(type(ch) is dict and set(ch)=={"class","spec","race","talents"},
         "USER_CHARACTER_FIELDS")
    key=(ch["class"],ch["spec"])
    tgt=user["target"]
    need(type(tgt) is dict and set(tgt)=={"ilevel","final_T"},
         "USER_TARGET_FIELDS")
    ilvl=tgt["ilevel"];final_T=tgt["final_T"]
    # Explicit v106 session identity selects the independently compiled 24-DPS
    # production route at ilvl 334 only. Historic v147/v145 probes remain
    # unpromoted and their unchanged pure_stage semantics are preserved.
    need(type(source_first_stage) is bool,"SOURCE_FIRST_STAGE_BOOL_REQUIRED")
    need(season_source_bundle is None or
         (season_profile_inputs is not None
          and current_season_product
          and type(season_source_bundle) is dict
          and set(season_source_bundle)=={
             "schema","gear","tier","budget","settings"}
          and season_source_bundle["schema"]==
             "v098_internal_season_source_bundle_v1"),
         "SEASON_SOURCE_BUNDLE_INTERNAL_PREVIEW_ONLY")
    need(season_original_source_paths is None or
         season_source_bundle is not None,
         "SEASON_V191_ORIGINALS_REQUIRE_SOURCE_BUNDLE")
    # v271 plan is an INTERNAL source-only preview, never a public
    # socket selector or runnable admission bypass.
    need(season_socket_plan is None or
         (type(season_socket_plan) is dict and
          season_source_bundle is not None and
          season_profile_inputs is not None and
          season_environment_receipt_path is None),
         "SEASON_V271_SOCKET_PLAN_SOURCE_ONLY_REQUIRED")
    # v216/v223 verifies previous-season installed source links; the
    # replaceable season bundle has not yet been joined to those exact
    # raw source bytes. A same build label is never sufficient for Native.
    need(season_source_bundle is None or
         season_environment_receipt_path is None,
         "SEASON_SOURCE_BUNDLE_ORIGINAL_GEAR_TIER_SHA_ADMISSION_PENDING")
    need(fresh_installed_environment_path is None or (
         season_source_bundle is not None and
         season_original_source_paths is not None and
         season_profile_inputs is not None and
         season_environment_receipt_path is None and
         current_season_product and static_cache_path is None),
         "FRESH_SEASON_INSTALLED_REQUIRES_ORIGINAL_SOURCE_LINKS")
    need(season_physical_one_spec_candidate is None or (
         fresh_installed_environment_path is not None and
         type(season_physical_one_spec_candidate) is dict and
         season_source_bundle is not None and
         season_original_source_paths is not None),
         "FRESH_V232_ONE_SPEC_ONLY_WITH_VERIFIED_INSTALLED_SOURCE")
    need(season_environment_receipt_path is None or
         (season_profile_inputs is not None
          and static_cache_path is None),
         "SEASON_WRITER_INTERNAL_SOURCE_AND_NO_STATIC_CACHE_REQUIRED")
    selected_season_items=bool(user["special_items"] or user["embellishments"])
    # B8 selected profile is intentionally NON-executable. Do not weaken
    # the ordinary v212/v096 user session or accept uninstalled v216 previews.
    need(season_selected_static_cache_path is None or (
         season_profile_inputs is not None and selected_season_items
         and fresh_installed_environment_path is not None
         and season_physical_one_spec_candidate is not None
         and season_original_source_paths is not None),
         "B8_SELECTED_INTERNAL_CACHE_ONLY_WITH_VERIFIED_V232_INSTALL")
    need(season_profile_inputs is None or
         (type(season_profile_inputs) is dict and current_season_product
          and not source_first_stage and not pure_stage
          and not static_special_probe_only
          and ENCHANT_FIELD not in user
          and SEASON_ENCHANT_FIELD not in user
          and (not selected_season_items or
               season_selected_static_cache_path is not None)),
         "SEASON_PROFILE_INTERNAL_SOURCE_ONLY_MODE_REQUIRED")
    # Search policy is an explicitly new session opt-in, never inherited from
    # an old sealed manifest or a source-only budget preview.
    need(exploration_policy is None or
         (exploration_policy=="axis_coverage_v1" and
          fresh_installed_environment_path is not None),
         "ADAPTIVE_EXPLORATION_REQUIRES_NEW_INSTALLED_SESSION")
    need(type(current_season_product) is bool,"CURRENT_SEASON_PRODUCT_BOOL_REQUIRED")
    # Separate opt-in product session: NO physical-proof-only stage seal.
    # v176 physically accepted all 26 source-first archetypes. Different
    # user-selected talents/trinkets are evaluated by actual SimC at runtime.
    need(not (current_season_product and source_first_stage),
         "SOURCE_FIRST_STAGE_AND_PRODUCT_ARE_EXCLUSIVE")
    need(not current_season_product or
         (not pure_stage and not independent_334 and
          not independent_target_level and ordinary_variant is None and
          type(ilvl) is int and 266<=ilvl<=344 and
          key in (set(ARCHETYPES)|PURE_PRODUCT_SPECS)),
         "CURRENT_SEASON_PRODUCT_SCOPE_TARGET_RANGE")
    # Developer-only v171+v168 representative equipment. Never activate in
    # ordinary web/v106 sessions or reuse existing v098 production receipts.
    need(not source_first_stage or
         (pure_stage and not independent_334 and
          not independent_target_level and ordinary_variant is None and
          ilvl==334),
         "SOURCE_FIRST_STAGE_ONLY_334_PURE_PLAN")
    need(type(independent_334) is bool,"INDEPENDENT_334_MODE_BOOL_REQUIRED")
    need(type(independent_target_level) is bool,
         "INDEPENDENT_TARGET_LEVEL_MODE_BOOL_REQUIRED")
    need(not (independent_334 and independent_target_level),
         "ONLY_ONE_INDEPENDENT_PROFILE_MODE")
    need(not independent_334 or
         (key in ARCHETYPES and ilvl==334 and ordinary_variant is None and
          not pure_stage),
         "INDEPENDENT_334_USER_SCOPE_NOT_SUPPORTED")
    need(not independent_target_level or
         (key in (set(ARCHETYPES)|PURE_PRODUCT_SPECS) and
          type(ilvl) is int and 266<=ilvl<=344 and ilvl!=334 and
          ordinary_variant is None and not pure_stage),
         "INDEPENDENT_NON334_USER_SCOPE_NOT_SUPPORTED")
    source_free=((key in PURE_PRODUCT_SPECS or independent_334 or
                  independent_target_level or current_season_product) and
                 "/".join(key) in pure.catalog()["specializations"])
    need(key in ARCHETYPES or source_free,
         "REPRESENTATIVE_ARCHETYPE_NOT_READY:"+"/".join(key))
    for name in ("race","talents"):
        scenario.text_token(ch[name],"USER_"+name.upper())
    need(type(ilvl) is int and 266<=ilvl<=344,
         "TARGET_ILVL_OUTSIDE_VERIFIED_REFERENCE")
    need(final_T is None or
         (type(final_T) is int and 1<=final_T<=100000),"MANUAL_FINAL_T_INVALID")
    combat=user["combat"]
    need(type(combat) is dict and set(combat)==
         {"targets","duration_seconds","raid_buffs"},"USER_COMBAT_FIELDS")
    need(type(combat["targets"]) is int and 1<=combat["targets"]<=40
         and type(combat["duration_seconds"]) is int
         and 1<=combat["duration_seconds"]<=3600
         and type(combat["raid_buffs"]) is bool,"USER_COMBAT_INVALID")
    need(type(user["oil_hands"]) is list,"USER_OIL_HANDS_LIST")
    need(type(user["trinkets"]) is list and len(user["trinkets"])==2,
         "TWO_USER_TRINKETS_REQUIRED")
    need(type(user["special_items"]) is list and len(user["special_items"])<=8
         and type(user["embellishments"]) is list
         and len(user["embellishments"])<=2,"USER_SELECTED_GEAR_LISTS")
    if ENCHANT_FIELD in user:
        verified_enchant.reject_selected_L_overlap(user,need)
    folder=pathlib.Path(folder).resolve()
    binary=pathlib.Path(binary).resolve()
    need(binary.is_file(),"SIMC_BINARY_NOT_PRESENT")
    need(type(revision) is str and len(revision)>=7,"SIMC_REVISION_REQUIRED")
    linked_originals=(_v191_raw_gear_tier_link(
        season_source_bundle,season_original_source_paths,revision)
        if season_original_source_paths is not None else None)
    # Source-independent P1 production specs compile from the season catalog.
    # Existing 24 source-backed default paths remain unchanged; explicit
    # pure_stage=True preserves the older v140 witness-only pilot contract.
    season_override=None
    profile_supplier_coverage=None
    if source_first_stage or current_season_product:
        if season_source_bundle is None:
            season_override=source_first.season_scope()
            actual_season_build=_profile_supplier_registry()["season_build"]
        else:
            season_override=(
                _verified_one_spec_G_profile_scope(
                    source_bundle=season_source_bundle,
                    candidate=season_physical_one_spec_candidate,
                    selected_key=key,target_ilevel=ilvl,
                    source_revision=season_profile_inputs[
                        "v216_numeric_preview"]["calculation"]["simc_revision"])
                if season_physical_one_spec_candidate is not None else
                source_first.season_scope(
                    db=season_source_bundle["gear"],
                    tier=season_source_bundle["tier"],
                    settings=season_source_bundle["settings"],
                    budget=season_source_bundle["budget"]))
            actual_season_build=season_source_bundle["gear"]["season_build"]
            observed=season_profile_inputs["v216_numeric_preview"]
            candidate=observed.get("calculation")
            need(type(candidate) is dict
                 and candidate.get("game_build")==actual_season_build
                 and candidate.get("target_ilevel")==ilvl,
                 "SEASON_SOURCE_BUNDLE_V216_BUILD_OR_TARGET_DRIFT")
            # v222 is the single authority for season J/F arithmetic. A
            # replaceable profile/settings file cannot silently overwrite
            # source-observed rating, even in a non-executable preview.
            need(candidate.get("J")==season_source_bundle["budget"][
                     "ordinary_gem"]["total_J"] and
                 candidate.get("F")==season_source_bundle["budget"][
                     "flasks"]["total_F"],
                 "SEASON_SOURCE_BUNDLE_V222_J_F_RATING_DRIFT")
        if current_season_product:
            profile_supplier_coverage=_current_season_profile_supplier_coverage(
                season_override,"/".join(key),
                one_spec_only=season_physical_one_spec_candidate is not None)
            if season_source_bundle is not None:
                profile_supplier_coverage={
                    **profile_supplier_coverage,
                    "season_build":actual_season_build,
                    "source_input_sha256":{
                        name:hashlib.sha256(canonical(
                            season_source_bundle[name]).encode("utf8")).hexdigest()
                        for name in ("gear","tier","budget","settings")},
                    "season_catalog_source_only":True,
                    "native_evidence_not_promoted":True}
    if pure_stage or source_free:
        need(ordinary_variant is None and
             (ilvl==334 or independent_target_level or current_season_product),
             "PURE_STAGE_TARGET_OR_VARIANT_NOT_READY")
        base_profile,cfg,rows,groups,weapon_layout,F,tier_data,fifth_data=(
            pure.v098_inputs(ch,user["trinkets"],target_ilevel=ilvl,
                             combat=combat,
                             level_preview=(independent_target_level or
                                            (current_season_product and ilvl!=334)),
                             season_override=season_override,
                             source_only_season_consumables=(
                                 season_profile_inputs is not None),
                             socket_plan=season_socket_plan))
    elif ordinary_variant is None:
        # Preserve the historical exact call shape and all default receipts.
        base_profile,cfg,rows,groups,weapon_layout,F=common.source_backed_gear(
            key,folder,ilvl,need)
    else:
        need(ordinary_variant in common.ORDINARY_VARIANTS,
             "REPRESENTATIVE_ORDINARY_VARIANT_NOT_PINNED")
        slot=common.ORDINARY_VARIANTS[ordinary_variant]["slot"]
        need(not any(r["slot"]==slot for r in
                     user["special_items"]+user["embellishments"]),
             "ORDINARY_VARIANT_CONFLICTS_WITH_USER_SELECTED_ITEM")
        base_profile,cfg,rows,groups,weapon_layout,F=common.source_backed_gear(
            key,folder,ilvl,need,ordinary_variant=ordinary_variant)
    if STAT_CAP_FIELD in user:
        # New product sessions use the explicit user cap on FINAL T.
        # The old per-stat B max_fraction template remains for sealed legacy
        # sessions only, and must not silently override a new 60% selection.
        # The user cap is separately bound into the scenario SHA and caches.
        cfg["constraints"]["max_single_stat_percent"]=user[STAT_CAP_FIELD]
        cfg["constraints"]["max_fraction"]={stat:1.0 for stat in scenario.STATS}
    if season_physical_one_spec_candidate is not None:
        # The tested G must correspond to exactly the representative item
        # IDs serialized into this user profile before adding two trinkets.
        observed={slot:rows[slot]["item_id"] for slot in
                  season_physical_one_spec_candidate["selected_G_slot_ids"]}
        need(observed==season_physical_one_spec_candidate[
                "selected_G_slot_ids"],
             "FRESH_V232_NATIVE_G_PHYSICAL_PROFILE_ITEMS_CHANGED")
    if season_socket_plan is not None:
        # Reuse v271's physical compositor above; compare the ACTUAL rows
        # with the original v216/v222 item-ID basis before any profile
        # serialization. Recoloring must never silently change J ownership.
        slot_counts=season_socket_plan["socket_counts"]
        actually_ordinary=[]
        actual_special=None
        for slot in sorted(slot_counts):
            need(slot in rows,"SEASON_V271_SOCKET_SLOT_NOT_IN_REPRESENTATIVE")
            value=rows[slot]["options"].get("gem_id","")
            tokens=[] if not value else value.split("/")
            need(len(tokens)==slot_counts[slot] and
                 all(part.isdigit() for part in tokens),
                 "SEASON_V271_PHYSICAL_SOCKET_COUNT_DRIFT")
            if slot==season_socket_plan["special_slot"]:
                actual_special=int(tokens[0])
                tokens=tokens[1:]
            actually_ordinary.extend(int(v) for v in tokens)
        need(actual_special==season_socket_plan["special_gem_id"] and
             actually_ordinary==season_socket_plan["ordinary_gem_ids"],
             "SEASON_V271_PHYSICAL_GEM_IDS_CHANGED_AFTER_J")
    original_selected_baseline_rows=(copy.deepcopy(rows)
        if season_selected_static_cache_path is not None else None)
    if pure_stage or source_free:
        restored_tier_slots,catalyst_origin_rows=common.apply_user_equipment(
            key,rows,groups,user,ilvl,need,
            tier_override=tier_data,fifth_override=fifth_data,
            flexible_current_tier=current_season_product,
            season_source_gear=(season_source_bundle["gear"]
                                if season_source_bundle is not None else None),
            season_source_tier=(season_source_bundle["tier"]
                                if season_source_bundle is not None else None))
    else:
        restored_tier_slots,catalyst_origin_rows=common.apply_user_equipment(
            key,rows,groups,user,ilvl,need)
    # DK user rune is permanent enchant_id, not temporary oil O.
    # The profile and durable cache identity change only for explicit choice.
    admitted_dk_ids=runeforge_mod.RUNE_IDS  # unchanged older sessions only
    if RUNEFORGE_FIELD in user and fresh_installed_environment_path is not None:
        # New/future-season DK selections must use the current verified
        # v212 registry, never the old static fallback list.
        fresh_path=pathlib.Path(fresh_installed_environment_path).resolve()
        need(fresh_path.is_file() and not fresh_path.is_symlink(),
             "FRESH_DK_INSTALLED_SOURCE_FILE_REQUIRED")
        dk_install,_=installed_manifest.read_json(fresh_path)
        installed_manifest.verify_fresh_installed_environment(dk_install)
        dk_source=dk_install.get("verified_DK_runeforges")
        need(type(dk_source) is dict and
             dk_install["game_build"]==actual_season_build and
             dk_install["target_ilevel"]==ilvl,
             "FRESH_DK_RUNEFORGE_SOURCE_NOT_INSTALLED")
        admitted_dk_ids={row["enchant_id"] for row in dk_source["items"]}
    runeforge_mod.apply(rows=rows,selection=user.get(RUNEFORGE_FIELD),
                        class_name=key[0],weapon_form=weapon_layout,need=need,
                        admitted_ids=admitted_dk_ids)
    # 240967 requires four distinct ordinary Midnight gem colors for its
    # crit-effectiveness bonus. These are real SimC gem IDs, not locked CHMV.
    # Existing 240983 profiles and already-four-color source rows stay intact.
    choice=user.get(CONSUME_FIELD) or {}
    gem_choice=choice.get("diamond_id") or int(
        rows["head"]["options"].get("gem_id","0"))
    if season_profile_inputs is None:
        common.ensure_representative_gem_colors(rows,gem_choice,need)
    else:
        # Socket legality is owned by the actual season source and v271.
        # Do not require historical Midnight-specific four-color diamonds
        # merely to compile a NON-executable source-only preview.
        default_choice=user.get(CONSUME_FIELD)
        # The v218 bridge maps selected food/potion/augmentation to the
        # exact settings used by the v139/SimC profile composer. They must
        # not be silently ignored or assumed to match the old season.
        # The verified v212 flask/gem budget and optional season module
        # remain independent and are not overridden here.
        if season_source_bundle is None:
            # Keep historical unadmitted source-only previews strict: they
            # have no verified selected seasonal settings to bind against.
            need(default_choice is None or (
                 type(default_choice) is dict and
                 set(default_choice)==consumer.CHOICE_FIELDS and
                 all(default_choice[k]=="source_default" for k in
                     ("flask","food","potion","augmentation",
                      "omnium_talents")) and
                 default_choice["diamond_id"]==0),
                 "SEASON_PROFILE_NONDEFAULT_CONSUMABLES_NOT_SOURCE_BOUND")
        else:
            bound=season_source_bundle["settings"]["default_consumables"]
            need(default_choice is None or (
                 type(default_choice) is dict and
                 set(default_choice)==consumer.CHOICE_FIELDS and
                 default_choice["flask"]=="source_default" and
                 default_choice["diamond_id"]==0 and
                 default_choice["omnium_talents"]=="source_default" and
                 all(default_choice[k]=="source_default" or
                     bound[k]==default_choice[k] for k in
                     ("food","potion","augmentation"))),
                 "SEASON_PROFILE_SELECTED_CONSUMABLES_NOT_SOURCE_BOUND")
    selected_nonchmv=None
    if SEASON_ENCHANT_FIELD in user:
        selected_nonchmv=nonchmv_enchant.apply(
            rows,user[SEASON_ENCHANT_FIELD],user,
            current_season_product=current_season_product,need_user=need,
            catalog_path=source_catalog_path)
    selected_fixed_E=None
    if ENCHANT_FIELD in user:
        # The same selected ring cannot be counted both as the exact
        # special-item L slot and a separate enchant E contribution.
        verified_enchant.reject_selected_L_overlap(user,need)
        # Internal exact-evidence path only. Normal v106/web controls
        # continue to reject this developer-only field.
        selected_fixed_E=verified_enchant.apply_verified_ring(
            rows,user[ENCHANT_FIELD],key,ilvl,need)
    # New plans use ONE common slot order for all archetypes. Existing sealed
    # sessions replay the old order exactly, avoiding a forced recalculation.
    legacy=profile_format.existing_profile_uses_legacy_format(
        folder/"profile.simc")
    rows=preserve_existing_v104_gear_order(key,rows,folder)
    rows=profile_format.order_rows(rows,legacy=legacy)
    cfg["equipment"],fillers=common.physical_gear_groups(
        rows,groups,catalyst_origin_rows)
    cfg["character"].update({"race":ch["race"],"talents":ch["talents"]})
    cfg["target"]={"mode":"derived_ilevel","ilevel":ilvl,
                   "manual_total":None,"manual_total_scope":None}
    cfg["combat"].update(combat)
    cfg["runtime"]["max_native_calls"]=6
    settings={"race":ch["race"],"talents":ch["talents"],
              "spec":ch["spec"],"role":cfg["character"]["role"],
              "fight_style":cfg["combat"]["fight_style"],
              "desired_targets":str(combat["targets"]),
              "max_time":str(combat["duration_seconds"]),
              "optimal_raid":"1" if combat["raid_buffs"] else "0"}
    profile=replace_assignments(base_profile,settings,rows)
    # Profile-native consumables and primary-only diamond are applied to
    # existing full source-backed gear BEFORE oil recalculates SHA and B/O.
    if season_profile_inputs is None:
        selected=consumer.apply(profile,cfg,rows,
                                user.get(CONSUME_FIELD))
    else:
        # The ordinary legacy v108.apply requires J=138/F=165; bypass that
        # *only* for the internal source-only season preview. The actual
        # v108 season serializer below writes independently observed J/F.
        selected={"profile":profile,"scenario":cfg,
                  "selected":None}
    profile=consumer.set_head_gem(selected["profile"],rows["head"])
    # This runtime serializer is now shared by all current archetypes;
    # per-spec producer APL/items are data inputs, never output-format forks.
    profile=profile_format.finalize(profile,legacy=legacy)
    cfg=selected["scenario"]
    cfg["equipment"],fillers=common.physical_gear_groups(
        rows,groups,catalyst_origin_rows)
    cfg["source"]={"kind":"user_supplied",
                   "profile_sha256":hashlib.sha256(profile.encode("utf8")).hexdigest()}
    scenario.normalize(cfg)
    if season_selected_static_cache_path is not None:
        return _selected_season_profile_budget_preflight(
            user=user,profile=profile,cfg=cfg,rows=rows,
            groups=groups,catalyst=catalyst_origin_rows,
            baseline_rows=original_selected_baseline_rows,
            candidate=season_physical_one_spec_candidate,
            class_tier_five=tier_data,
            original_v191_link=linked_originals,
            installed_path=fresh_installed_environment_path,
            cache_path=season_selected_static_cache_path)
    if season_profile_inputs is not None:
        source_only=season_profile_source_only(
            profile=profile,cfg=cfg,weapon_layout=weapon_layout,user=user,
            season_profile_inputs=season_profile_inputs,
            season_build=actual_season_build,
            simc_revision=revision,fillers=fillers)
        if linked_originals is not None:
            source_only["original_v191_gear_tier_source_unadmitted"]=linked_originals
        if season_socket_plan is not None:
            source_only["v271_variable_socket_layout_unadmitted"]={
                "socket_counts":dict(season_socket_plan["socket_counts"]),
                "special_slot":season_socket_plan["special_slot"],
                "special_gem_id":season_socket_plan["special_gem_id"],
                "ordinary_gem_ids":list(season_socket_plan["ordinary_gem_ids"]),
                "game_socket_legality_verified_here":False,
                "new_native_calls":0}
        if (season_environment_receipt_path is None and
                fresh_installed_environment_path is None):
            # Unadmitted observations never write a runnable manifest.
            return source_only
        return _materialize_admitted_season_v096(
            source_only=source_only,
            season_profile_inputs=season_profile_inputs,
            season_environment_receipt_path=season_environment_receipt_path,
            folder=folder,binary=binary,revision=revision,
            static_cache_path=static_cache_path,weapon_layout=weapon_layout,
            fillers=fillers,user=user,ilevel=ilvl,rows=rows,key=key,
            fresh_installed_environment_path=fresh_installed_environment_path,
            original_v191_link=linked_originals,
            exploration_policy=exploration_policy)
    if static_special_probe_only:
        # v208 internal on-demand static-L source, never a product plan.
        # Reuses exactly the real user/gear/consumables profile composition
        # above, before v062 rejects a cache-missing selected L. Nothing is
        # written, no SimC is executed, and no optimizer or result is seeded.
        need(current_season_product and bool(user["special_items"])
             and static_cache_path is None,
             "STATIC_SPECIAL_PROBE_ONLY_EXACT_CURRENT_USER")
        oil=oil_mod.configure(profile,cfg,weapon_layout,user["oil_hands"])
        chosen_slots=({r["slot"] for r in cfg["equipment"]["special"]} |
                      set(cfg["equipment"].get("catalyst_special_tier_slots",[])))
        need(chosen_slots and
             chosen_slots=={r["slot"] for r in user["special_items"]},
             "STATIC_SPECIAL_PROBE_SLOTS_NOT_SOURCE_BOUND")
        return {"schema":"v208_exact_current_special_static_source_v1",
                "profile":oil["profile"],
                "special_rows":[copy.deepcopy(rows[s]) for s in sorted(chosen_slots)],
                "source_profile_sha256":hashlib.sha256(
                    oil["profile"].encode("utf8")).hexdigest(),
                "native_calls":0,"no_optimization_or_budget_produced":True}
    static=(cache_mod.empty_cache() if static_cache_path is None
            else cache_mod.load(pathlib.Path(static_cache_path)))
    prepared=oil_mod.prepare(profile,cfg,fillers,static,weapon_layout,
                             user["oil_hands"],manual_final_T=final_T,
                             verified_enchant_E=selected_fixed_E)
    normalized=prepared["prepared"]["scenario"]
    budget=prepared["prepared"]["static_budget"]
    # Shared floor B >= F-O, with selected exact L protected.
    # Candidate seeds must be viable BEFORE a Native call is even planned.
    if ENCHANT_FIELD in user:
        # E is fixed within effective G: auto reference B includes the
        # selected incremental rating, manual final T stays authoritative.
        e_vector=selected_fixed_E
        feasible=scheduler.budget_with_fixed_components(
            normalized,budget,F,prepared["oil"]["declared_O"],
            fixed_enchant_E=e_vector)
    else:
        feasible=scheduler.budget_with_fixed_components(
            normalized,budget,F,prepared["oil"]["declared_O"])
    B,lo,hi=scheduler.bounds(normalized,feasible)
    seeds=initial_seeds(B,lo,hi)
    # The tightened F/O feasibility floor must NOT reseed an already sealed
    # session. Reconstruct the two known deterministic seed policies rather
    # than trusting arbitrary mutable manifest contents: pre-v124 L-only and
    # current unified L/F/O. Admit the old pair only if both remain feasible.
    prior_manifest=folder/"manifest.json"
    if prior_manifest.is_file():
        old=json.loads(prior_manifest.read_text(encoding="utf8"))
        sealed=old.get("seed_targets_B")
        # If any Native run has started, its durable session identity is the
        # stronger immutable witness for the ORIGINAL pair, not merely the
        # current manifest bytes. A changed-but-recognized manifest cannot
        # repoint completed Native receipts to other seeds.
        native_seal=folder/"simc_results"/"V094_SESSION_IDENTITY.json"
        if native_seal.is_file():
            native_identity=json.loads(native_seal.read_text(encoding="utf8"))
            need(native_identity.get("seed_base_targets")==sealed,
                 "EXISTING_MANIFEST_SEEDS_DISAGREE_WITH_NATIVE_IDENTITY")
        old_B,old_lo,old_hi=scheduler.bounds(normalized,budget)
        need(old_B==B,"EXISTING_SESSION_SEED_TOTAL_DRIFT")
        pre_v124_seeds=initial_seeds(old_B,old_lo,old_hi)
        if sealed==seeds:
            pass
        elif sealed==pre_v124_seeds:
            need(all(scheduler.eligible(
                 tuple(v[k] for k in scenario.STATS),B,lo,hi)
                 for v in sealed),
                 "EXISTING_SESSION_SEEDS_BELOW_FIXED_COMPONENT_FLOOR")
            seeds=pre_v124_seeds
        else:
            need(False,"EXISTING_SESSION_SEEDS_UNRECOGNIZED_OR_CHANGED")
    manifest={"schema":entry.SCHEMA,
              "profile_simc":"profile.simc","scenario_json":"scenario.json",
              "fillers_json":"fillers.json",
              "static_cache_json":str(pathlib.Path(static_cache_path).resolve())
                                  if static_cache_path else None,
              "weapon_layout":weapon_layout,"oil_hands":user["oil_hands"],
              "flask_F":F,"seed_targets_B":seeds,"native_binary":str(binary),
              "native_revision":revision,"output_dir":"simc_results",
              "scouts":1,"material_scouts":1,"native_limit":6,
              "step":100,"cancel_file":"CANCEL"}
    if final_T is not None:manifest["manual_final_T"]=final_T
    if ENCHANT_FIELD in user:
        manifest[entry.NATIVE_ENCHANT_FIELD]=dict(user[ENCHANT_FIELD])
    if SEASON_ENCHANT_FIELD in user:
        manifest[entry.NONCHMV_ENCHANT_FIELD]=dict(user[SEASON_ENCHANT_FIELD])
    if pure_stage:manifest[entry.STAGE_FIELD]=True
    put_once(folder/"profile.simc",profile)
    put_once(folder/"scenario.json",canonical(cfg)+"\n")
    put_once(folder/"fillers.json",canonical(fillers)+"\n")
    put_once(folder/"manifest.json",canonical(manifest)+"\n")
    plan=entry.run_manifest(folder/"manifest.json",plan_only=True)
    need(plan["base_B"]==B and plan["item_slots"]==len(rows),
         "BOOTSTRAP_TO_V096_BUDGET_OR_SLOT_DRIFT")
    return {"schema":SCHEMA,
            **({"selected_nonchmv_enchant":selected_nonchmv}
               if selected_nonchmv is not None else {}),
            "status":("STAGED_INTERNAL_MANIFEST_NATIVE_NOT_AUTHORIZED"
                      if pure_stage else "READY_INTERNAL_MANIFEST_ZERO_NATIVE"),
            **({"pure_source_independent_stage":True,
                "physical_socket_weapon_native_verified":False,
                "user_optimizer_ready":False}
               if pure_stage else {}),
            "user_does_not_supply_full_gear_or_simc_profile":True,
            "source_independent_334_user_session":bool(independent_334),
            "source_independent_non334_user_session":bool(independent_target_level),
            "non334_physical_simc_not_yet_observed":bool(independent_target_level or
                    (current_season_product and ilvl!=334)),
            "template_archetype":"/".join(key),"target_ilevel":ilvl,
            "generated_manifest":str(folder/"manifest.json"),
            "output_dir":str(folder/"simc_results"),"plan":plan,
            "native_calls":0,"supported_archetypes_now":len(ARCHETYPES),
            **({"current_season_supported_specializations":
                    profile_supplier_coverage["current_season_profile_supplier_count"],
                "profile_supplier_coverage":profile_supplier_coverage}
               if profile_supplier_coverage is not None else {}),
            "armor_family":common.CLASS_ARMOR[key[0]],
            "ordinary_armor_seed_slots_available":list(
                common.available_ordinary_seed_slots(
                    common.CLASS_ARMOR[key[0]])),
            "ordinary_armor_seed_pool_partial_not_full_set":True,
            "weapon_form":weapon_layout,
            "catalyst_origin_items":catalyst_origin_rows,
            "restored_tier_slots":restored_tier_slots,
            "effective_four_tier_slots":sorted(
                 slot for slot,g in groups.items() if g=="tier"),
            "all_specs_ready":False,
            "consumables_selected":selected["selected"],
            "gem_secondary_budget_J_fixed_138":True,
            "flask_F_fixed_165":True,
            "omnium_folio_user_input_ready":False,
            **({"internal_ordinary_variant":ordinary_variant}
               if ordinary_variant is not None else {}),
            **({"source_first_stage":True,
                "new_season_equipment_not_native_accepted":True,
                "v098_user_default_unchanged":True}
               if source_first_stage else {}),
            **({"current_season_product":True,
                "v176_base_physical_26_of_26_verified":ilvl==334,
                "current_user_selected_options_verified_only_by_native":True,
                "default_legacy_sessions_unchanged":True}
               if current_season_product else {})}

def _season_settings_from_v216(*, compilation, numeric_inputs,
                                controls=None, need):
    """Compose observed gem/J/F settings without optional user-input gates.

    P3-BN: SimC owns compiled default level (no level=). The existing
    optional food/potion/augmentation settings are disabled when unselected;
    Omnium is a separate OFF-by-default module, not a budget prerequisite.
    Exact season-specific options remain unadmitted until normal Policy A.
    """
    need(controls is None or
         (type(controls) is dict and
          set(controls)<={"food","potion","augmentation","omnium_talents"}),
         "SEASON_SETTINGS_ONLY_OPTIONAL_CONSUMABLE_AND_MODULE_FIELDS")
    optional={} if controls is None else controls
    choices={}
    for name in ("food","potion","augmentation"):
        token=optional.get(name,"disabled")
        need(type(token) is str and 1<=len(token)<=90 and
             token!="source_default" and token[0].isalpha() and
             token[0].islower() and
             all(char in "abcdefghijklmnopqrstuvwxyz0123456789_"
                 for char in token),
             "SEASON_SETTINGS_EXACT_OPTIONAL_SIMC_TOKEN_REQUIRED:"+name)
        choices[name]=token
    folio=optional.get("omnium_talents")
    need(folio is None or
         (type(folio) is str and 1<=len(folio)<=500 and
          folio!="source_default" and
          all(char in "0123456789:/"
              for char in folio)),
         "SEASON_SETTINGS_OPTIONAL_OMNIUM_TOKEN_INVALID")
    layout=compilation.get("physical_gem_layout_unadmitted")
    gem=compilation.get("physical_gem_J_arithmetic_unadmitted")
    missing=[]
    if type(layout) is not dict or type(gem) is not dict:
        missing.append("V271_SELECTED_PHYSICAL_GEM_LAYOUT_AND_J_PENDING")
    if missing:
        return {"status":"SEASON_SETTINGS_SOURCE_PENDING",
                "missing":missing,"settings":None}
    need(layout.get("schema")=="v271_user_socket_gem_layout_stage_v1"
         and layout.get("status")==
             "PHYSICAL_GEMS_STAGED_SOURCE_AND_SOCKET_PROOFS_PENDING"
         and gem.get("status")=="PHYSICAL_GEM_J_ARITHMETIC_UNADMITTED"
         and gem.get("physical_gem_item_ids")==layout.get("ordinary_gem_ids")
         and gem.get("J_candidate_unadmitted")==
             numeric_inputs["v216_numeric_preview"]["calculation"]["J"],
         "SEASON_SETTINGS_V271_V222_PHYSICAL_J_DRIFT")
    ordinary=layout["ordinary_gem_ids"]
    counts=layout.get("socket_counts")
    special=layout.get("special_gem_id")
    where=layout.get("special_slot")
    # A future-season gem item must first match the ORIGINAL sealed v221
    # same-build ItemSparse→GemProperty FK. This is not certification of
    # special class, effective J, highest quality or game socket legality.
    source_ids=layout.get("source_observed_gem_item_ids")
    source_relation=compilation.get(
        "selected_v221_gem_item_relation_unadmitted")
    if source_ids is not None:
        if (type(source_ids) is not list or
                type(source_relation) is not dict or
                source_relation.get("same_build_gem_item_join_only") is not True or
                source_relation.get("selected_item_ids")!=source_ids or
                source_relation.get("special_gem_item_id")!=special or
                type(source_relation.get("v221_stage_receipt_sha256")) is not str):
            return {"status":"SEASON_SETTINGS_SOURCE_PENDING",
                    "missing":["V221_SELECTED_SPECIAL_GEM_SOURCE_LINK_PENDING"],
                    "settings":None}
    # Same-build item property metadata is reusable season input, but it
    # does not prove special-effect role, highest quality or legal sockets.
    property_rows=(source_relation.get(
        "selected_gem_property_records_unadmitted")
        if type(source_relation) is dict else None)
    if property_rows is not None:
        if (type(property_rows) is not list or
                [row.get("item_id") for row in property_rows
                 if type(row) is dict]!=source_ids or
                any(type(row) is not dict or
                    set(row)!={"item_id","gem_property_id","enchant_id",
                               "color_mask","minimum_ilevel","expansion_id"}
                    or any(type(v) is not int or v<0
                           for v in row.values())
                    for row in property_rows)):
            return {"status":"SEASON_SETTINGS_SOURCE_PENDING",
                    "missing":["V221_GEM_SOURCE_PROPERTY_INPUT_DRIFT"],
                    "settings":None}
    # Reuse v230's existing exact-item crafting-quality source observation.
    # An item rank does not establish identical effect/applicability or best
    # available quality; such conclusions remain owned by Policy A evidence.
    selected_quality=(source_relation.get(
        "selected_simc_gem_quality_source_unadmitted")
        if type(source_relation) is dict else None)
    if selected_quality is not None and selected_quality.get(
            "quality_source_authenticated") is True:
        if (selected_quality.get("game_build")!=
                numeric_inputs["v216_numeric_preview"]["calculation"]["game_build"]
                or selected_quality.get("selected_item_ids")!=source_ids):
            return {"status":"SEASON_SETTINGS_SOURCE_PENDING",
                    "missing":["V230_SELECTED_GEM_QUALITY_SCOPE_DRIFT"],
                    "settings":None}
    # v271/v139 already support variable N and a non-head special slot.
    # Unsupported source IDs remain pending rather than being invented.
    with_special=special is not None
    if (type(counts) is not dict or type(ordinary) is not list or
        (with_special and
         (type(special) is not int or special<=0 or
          type(where) is not str or counts.get(where,0)<1)) or
        (not with_special and (where is not None or
                               len(set(ordinary[:4]))!=4)) or
        sum(counts.values())!=len(ordinary)+int(with_special) or
        not (1 if with_special else 4)<=sum(counts.values())<=64):
        return {"status":"SEASON_SETTINGS_SOURCE_PENDING",
                "missing":["V271_PHYSICAL_SOCKET_PLAN_SOURCE_PENDING"],
                "settings":None}
    if special not in (240983,240967) and source_ids is None:
        return {"status":"SEASON_SETTINGS_SOURCE_PENDING",
                "missing":["V271_NEW_SPECIAL_GEM_SAME_BUILD_ID_PENDING"],
                "settings":None}
    allowed={"head","neck","shoulders","back","chest","wrists","hands",
             "waist","legs","feet","finger1","finger2","main_hand","off_hand"}
    need(all(type(k) is str and k in allowed and
             type(v) is int and 0<=v<=16 for k,v in counts.items()) and
         all(type(item) is int and item>0 for item in ordinary),
         "SEASON_SETTINGS_V271_SOCKET_ROWS_INVALID")
    source_gems={}
    consumed=iter(ordinary)
    for slot in sorted(counts):
        item_ids=[special] if with_special and slot==where else []
        item_ids.extend(next(consumed) for _ in
                        range(counts[slot]-
                              (1 if with_special and slot==where else 0)))
        if item_ids:
            source_gems[slot]="/".join(map(str,item_ids))
    flask=numeric_inputs["flask"]
    vector=scenario.vector(flask["static_CHMV_vector"],
                           "SEASON_SETTINGS_NATIVE_FLASK_VECTOR")
    chosen=[k for k,v in vector.items() if v>0]
    calc=numeric_inputs["v216_numeric_preview"]["calculation"]
    need(sum(vector.values())==calc["F"],
         "SEASON_SETTINGS_FLASK_NATIVE_V222_DRIFT")
    if len(chosen)!=1:
        return {"status":"SEASON_SETTINGS_SOURCE_PENDING",
                "missing":["V139_MULTI_STAT_FLASK_SOURCE_COMPOSER_PENDING"],
                "settings":None}
    build=calc["game_build"]
    settings={
        "schema":"v144_representative_season_items_v1",
        "season":"source_build_"+build.replace(".","_"),
        "target_ilevel":calc["target_ilevel"],
        "character_level":None,
        "common_gear":{},"specializations":{},
        "simc_item_db_source":"local",
        "gems":source_gems,
        "default_consumables":{
            "flask":flask["simc_input_token"],
            "food":choices["food"],
            "potion":choices["potion"],
            "augmentation":choices["augmentation"],
            "omnium_talents":folio,
            "gem_budget_J":calc["J"],
            "flask_budget_F":calc["F"],
            "flask_fixed_stat":chosen[0]}}
    pure.validate_season(settings)
    # Old 6+head shape keeps its exact existing serialization. All other
    # source-observed layouts use the existing v271 opt-in compositor.
    fixed=(source_ids is None and where=="head"
           and counts.get("head")==1 and
           len(ordinary)==6 and sum(counts.values())==7)
    socket_plan=(None if fixed else {
        "socket_counts":dict(counts),
        "special_gem_id":special,"special_slot":where,
        "ordinary_gem_ids":list(ordinary),
        **({"source_observed_gem_item_ids":list(source_ids)}
           if source_ids is not None else {})})
    return {"status":"SEASON_SETTINGS_PHYSICAL_GEMS_FLASK_COMPOSED_UNADMITTED",
            "missing":[],"settings":settings,
            "v271_socket_plan_unadmitted":socket_plan,
            "physical_gem_ids_reused":True,
            "selected_native_flask_reused":True,
            "selected_v221_gem_property_inputs_unadmitted":(
                [dict(row) for row in property_rows]
                if property_rows is not None else None),
            "selected_v230_gem_item_quality_unadmitted":(
                [dict(row) for row in selected_quality[
                    "selected_item_quality_unadmitted"]]
                if type(selected_quality) is dict and
                selected_quality.get("quality_source_authenticated") is True
                else None),
            "gem_policy_A_source_and_quality_unadmitted":(
                source_relation.get(
                    "gem_policy_A_source_and_quality_unadmitted")
                if type(source_relation) is dict else None),
            "gem_highest_quality_verified_here":False,
            "source_minimum_ilevel_for_selected_gems_observed_only":(
                all(row["minimum_ilevel"]<=calc["target_ilevel"]
                    for row in property_rows)
                if property_rows is not None else None),
            "game_socket_legality_authenticated_here":False,
            "controls_admitted_or_default_quality_verified_here":False,
            "optional_consumables_default_disabled_if_unselected":True,
            "simc_compiled_default_level_used":True}


def _choose_user_specific_fresh_G_source(candidate, *, user, calculation):
    """A one-spec measured physical G reference cannot be copied to another spec.

    Keep the same-build reference budget for normal-target B/T. For a different
    class/spec, route profile composition through the source-backed 26-spec
    v169 gear/tier selection. Neither route makes a new G-Native claim.
    """
    import v232_simc_only_ordinary_representative as physical
    import v229_simc_only_source_seed as source_seed
    need(type(candidate) is dict and
         candidate.get("schema")==physical.SCHEMA and
         candidate.get("status")==
             "SIMC_SOURCE_PHYSICAL_CANDIDATE_NOT_ACTUAL_SEASON_PROOF"
         and candidate.get("receipt_sha256")==source_seed.digest(
             source_seed.canonical({k:v for k,v in candidate.items()
                                    if k!="receipt_sha256"}).encode("utf8"))
         and candidate.get("game_build")==calculation["game_build"]
         and candidate.get("simc_revision")==calculation["simc_revision"]
         and candidate.get("target_ilevel")==calculation["target_ilevel"]
         and type(candidate.get("character")) is dict
         and type(candidate.get("selected_G_slot_ids")) is dict,
         "FRESH_V232_REFERENCE_SOURCE_HASH_OR_SCOPE_DRIFT")
    need(type(user) is dict and type(user.get("character")) is dict,
         "FRESH_V232_USER_CHARACTER_MISSING")
    measured=(candidate["character"].get("class"),
              candidate["character"].get("spec"))
    selected=(user["character"].get("class"),
              user["character"].get("spec"))
    need(selected in set(ARCHETYPES)|PURE_PRODUCT_SPECS,
         "FRESH_V232_USER_SPEC_UNSUPPORTED")
    if measured==selected:
        return candidate,False
    return None,True


def _select_v216_source_only_user_spec(candidate, *, user,
                                      environment_result, calculation):
    """Select ONE user-spec source from the SAME pinned v216 Build, Native0.

    v216's G/B/T remains a general reference; candidate gear for each
    actual DPS spec comes from the same pinned SimC item data/tier and Wago
    files. No 26-spec all-or-nothing catalog, no historical gear fallback,
    no copied static rating certification for the user's spec.
    """
    import v216_environment_build_coordinator as builder
    source=environment_result
    need(type(source) is dict and
         type(source.get("source_compilation")) is dict,
         "FRESH_SELECTED_SPEC_SOURCE_CONTEXT_MISSING")
    root=pathlib.Path(source["source_compilation"]["stage_root"]).resolve()
    need(root.is_dir() and not root.is_symlink(),
         "FRESH_SELECTED_SPEC_STAGE_ROOT_MISSING")
    gear=source.get("fresh_ordinary_gear")
    tier=source.get("fresh_tier_simc_candidate_bridge")
    full=source.get("fresh_lazy_full_pinned_simc_item_source")
    need(all(type(x) is dict for x in (gear,tier,full)) and
         all(type(x.get("candidate_path")) is str and x.get("candidate_path")
             for x in (gear,tier)) and
         type(full.get("source_dir")) is str and full["source_dir"],
         "FRESH_SELECTED_SPEC_PINNED_SOURCE_NOT_RETAINED")
    seed=pathlib.Path(full["source_dir"]).resolve()
    paths=(pathlib.Path(gear["candidate_path"]).resolve(),
           pathlib.Path(tier["candidate_path"]).resolve(),seed)
    need(all(x.is_relative_to(root) and x.exists() and not x.is_symlink()
             for x in paths) and seed.is_dir() and
         (seed/"item_data.inc").is_file() and
         not (seed/"item_data.inc").is_symlink(),
         "FRESH_SELECTED_SPEC_SOURCE_OUTSIDE_PINNED_STAGE")
    request={"class":user["character"]["class"],
             "spec":user["character"]["spec"],
             "target_ilevel":calculation["target_ilevel"]}
    result=builder._one_spec_ordinary_simc_stage(
        stage_root=root,build=calculation["game_build"],
        fresh_gear=gear,tier_bridge=tier,seed_directory=seed,
        request=request)
    need(result.get("status")==
             "FRESH_ONE_SPEC_SIMC_G_SOURCE_CANDIDATE_PENDING_NATIVE" and
         result.get("native_calls")==0 and
         type(result.get("candidate_path")) is str,
         "FRESH_SELECTED_SPEC_SOURCE_ONLY_NOT_READY:"+str(result.get("reason")))
    path=pathlib.Path(result["candidate_path"]).resolve()
    need(path.is_relative_to(root) and path.is_file() and
         not path.is_symlink() and 0<path.stat().st_size<=12_000_000,
         "FRESH_SELECTED_SPEC_SOURCE_CANDIDATE_PATH_INVALID")
    try:
        chosen=json.loads(path.read_text(encoding="utf8"))
    except (OSError,ValueError,UnicodeError) as exc:
        raise UserScenarioBlocked(
            "FRESH_SELECTED_SPEC_SOURCE_CANDIDATE_JSON_INVALID") from exc
    # Reuse the existing original per-spec SHA, build, revision and
    # exact selected physical-slot validation (in v098.build).
    need(chosen.get("game_build")==calculation["game_build"] and
         chosen.get("simc_revision")==calculation["simc_revision"] and
         chosen.get("target_ilevel")==calculation["target_ilevel"] and
         (chosen.get("character",{}).get("class"),
          chosen.get("character",{}).get("spec"))==
         (request["class"],request["spec"]),
         "FRESH_SELECTED_SPEC_NEW_SOURCE_IDENTITY_DRIFT")
    return chosen


def preview_from_environment_build(user,folder,binary,revision,*,
                                   environment_result,season_settings=None,
                                   season_controls=None,
                                   selected_static_cache_path=None,
                                   exploration_policy=None):
    """Normal v216 source → v098 preview without manual gear/tier/J/F bundling.

    The v216 zero-history Build already compiles v191/v213 gear/tier and
    calculates selected exact G/J/F/O with original v222. Keep those single
    sources; require separate season-native profile settings until a verified
    automatic settings producer exists. No session, Native, Policy A or READY.
    """
    need(type(environment_result) is dict and
         environment_result.get("normal_build_entry") is True and
         type(environment_result.get("zero_history_build")) is dict and
         environment_result["zero_history_build"].get("environment_ready")
             in (False,True),
         "SEASON_V216_NORMAL_BUILD_UNADMITTED_RESULT_REQUIRED")
    compilation=environment_result.get("source_compilation")
    need(type(compilation) is dict,
         "SEASON_V216_ORIGINAL_SOURCE_COMPILATION_REQUIRED")
    installed_path=None
    if environment_result["zero_history_build"]["environment_ready"] is True:
        installed=compilation.get("verified_environment_install")
        need(type(installed) is dict
             and installed.get("environment_ready") is True
             and installed.get("environment_installed") is True
             and installed.get("status")==
                 "FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY"
             and type(installed.get("stage_output_path")) is str,
             "SEASON_V216_READY_WITHOUT_ORIGINAL_FRESH_INSTALL")
        installed_path=installed["stage_output_path"]
    selected_items=bool(user["special_items"] or user["embellishments"])
    if selected_items and (installed_path is None or
                           selected_static_cache_path is None):
        return {
            "schema":"v433_v098_selected_user_physical_budget_preflight_v1",
            "status":"B8_SELECTED_VERIFIED_INSTALL_OR_EXACT_CACHE_PENDING",
            "missing":([
                "B8_SELECTED_FRESH_V212_INSTALLED_SOURCE_REQUIRED"
                ] if installed_path is None else [])+([
                "B8_SELECTED_EXACT_V046_CACHE_REQUIRED"
                ] if selected_static_cache_path is None else []),
            "user_session_created":False,
            "native_calls":0,"network_calls":0,
            "native_execution_authorized":False,
        }
    originals=compilation.get("v191_original_gear_tier_source_paths")
    inputs=compilation.get("v098_source_only_profile_inputs_unadmitted")
    missing=[]
    if compilation.get("status")!="FRESH_V191_V211_V213_COMPILED_UNADMITTED":
        missing.append("ORIGINAL_V191_V213_COMPILATION_PENDING")
    if originals is None:
        missing.append("ORIGINAL_V191_GEAR_TIER_PATHS_PENDING")
    if inputs is None:
        missing.append("SELECTED_V222_GJFO_PROFILE_INPUTS_PENDING")
    need(season_settings is None or season_controls is None,
         "SEASON_SETTINGS_AMBIGUOUS_EXPLICIT_AND_DERIVED")
    derived_settings=None
    if season_settings is None and inputs is not None:
        derived_settings=_season_settings_from_v216(
            compilation=compilation,numeric_inputs=inputs,
            controls=season_controls,need=need)
        if derived_settings["settings"] is not None:
            season_settings=derived_settings["settings"]
        else:
            missing.extend(derived_settings["missing"])
    elif season_settings is None:
        missing.append("SEASON_SPECIFIC_GEM_AND_CONSUMABLE_SETTINGS_PENDING")
    if missing:
        return {"schema":"v098_v216_auto_source_preview_bridge_v1",
                "status":"V216_TO_V098_SOURCE_PROFILE_PENDING",
                "missing":sorted(set(missing)),
                "environment_ready":False,"native_calls":0,
                "network_calls":0,"user_session_created":False}
    need(type(originals) is dict and
         set(originals)=={"catalog","gear","tier"} and
         originals["catalog"]==compilation.get("source_catalog_path") and
         type(inputs) is dict and
         inputs.get("schema")=="v098_internal_season_profile_inputs_v1" and
         type(inputs.get("v216_numeric_preview")) is dict,
         "SEASON_V216_SOURCE_PATHS_OR_INPUTS_DRIFT")
    # Signed v212 environment remains immutable; only the user session
    # retargets B/T. Original v096 checks source-owner proofs once more.
    if installed_path is not None and user["target"]["final_T"] is not None:
        original=inputs["v216_numeric_preview"]["calculation"]
        p=pathlib.Path(installed_path)
        need(p.is_file() and not p.is_symlink(),
             "FRESH_USER_T_INSTALLED_PATH_INVALID")
        doc,_=installed_manifest.read_json(p)
        installed_manifest.verify_fresh_installed_environment(doc)
        need(doc["manifest_sha256"]==compilation[
                 "verified_environment_install"]["manifest_sha256"] and
             original["base_B"]==doc["official_B"] and
             original["final_T"]==doc["official_T"] and
             original["J"]==doc["official_J"] and
             original["F"]==doc["official_F"] and
             original["fixed_O"]==doc["official_O"] and
             original["source_catalog_manifest_sha256"]==
                 doc["source_catalog_manifest_sha256"] and
             original["source_catalog_artifact_sha256"]==
                 doc["source_catalog_artifact_sha256"],
             "FRESH_USER_T_ORIGINAL_SOURCE_DRIFT")
        try:
            adjusted=budget_contract.retarget_verified_install(
                document=doc,manual_final_T=user["target"]["final_T"])
        except budget_contract.SeasonBudgetBlocked as exc:
            raise UserScenarioBlocked(
                "FRESH_USER_T_FIXED_BUDGET_INVALID:"+str(exc)) from exc
        inputs=copy.deepcopy(inputs)
        inputs["v216_numeric_preview"]["calculation"].update({
            "base_B":adjusted["base_B"],
            "final_T":adjusted["final_T"],
            "manual_final_T_authoritative":True})
    numeric=inputs["v216_numeric_preview"]
    calc=numeric.get("calculation")
    need(numeric.get("schema")==
             "v216_zero_history_selected_v222_numeric_preview_v1" and
         numeric.get("status")==
             "SELECTED_GJFO_V222_ARITHMETIC_PREVIEW_UNADMITTED" and
         numeric.get("numeric_preview_only") is True and
         numeric.get("environment_ready") is False and
         type(calc) is dict and calc.get("numeric_preview_only") is True and
         calc.get("simc_revision")==compilation.get("simc_revision") and
         type(calc.get("J")) is int and calc["J"]>0 and
         type(calc.get("F")) is int and calc["F"]>0,
         "SEASON_V216_NUMERIC_GJFO_SOURCE_NOT_RECONCILED")
    need(type(season_settings) is dict and
         type(season_settings.get("default_consumables")) is dict and
         season_settings["default_consumables"].get("gem_budget_J")==calc["J"] and
         season_settings["default_consumables"].get("flask_budget_F")==calc["F"],
         "SEASON_V216_SETTINGS_J_F_DRIFT")
    # Read the ORIGINAL same-build files selected by v274. v098.build will
    # immediately recheck their v191 raw SHA / actual v213 manifest identity,
    # so a forged season label or file edit cannot become a runnable manifest.
    docs={}
    for name in ("gear","tier"):
        path=pathlib.Path(originals[name]).expanduser()
        need(path.is_file() and not path.is_symlink() and
             0<path.stat().st_size<=12_000_000,
             "SEASON_V216_ORIGINAL_GEAR_TIER_FILE_MISSING")
        try:
            docs[name]=json.loads(path.read_text(encoding="utf8"))
        except (OSError,ValueError,UnicodeError) as exc:
            raise UserScenarioBlocked(
                "SEASON_V216_ORIGINAL_GEAR_TIER_JSON_INVALID") from exc
    need(docs["gear"].get("season_build")==calc.get("game_build") and
         docs["tier"].get("retail_build")==calc.get("game_build") and
         type(user) is dict and type(user.get("target")) is dict and
         user["target"].get("ilevel")==calc.get("target_ilevel"),
         "SEASON_V216_GEAR_TIER_BUILD_OR_USER_TARGET_DRIFT")
    # v169 requires only these measured numeric components from v222; do
    # not manufacture legacy J138/F165, high-quality approval or oil values.
    budget={"schema":"v165_current_season_chmv_consumables_v1",
            "retail_build":calc["game_build"],
            "ordinary_gem":{"total_J":calc["J"]},
            "flasks":{"total_F":calc["F"]}}
    bundle={"schema":"v098_internal_season_source_bundle_v1",
            **docs,"budget":budget,"settings":copy.deepcopy(season_settings)}
    one_spec_candidate=None
    if installed_path is not None:
        source=environment_result.get("fresh_one_spec_simc_representative")
        root=pathlib.Path(compilation["stage_root"]).resolve()
        need(type(source) is dict and
             type(source.get("candidate_path")) is str,
             "FRESH_V232_INSTALLED_G_ORIGINAL_CANDIDATE_PATH_MISSING")
        path=pathlib.Path(source["candidate_path"]).expanduser()
        need(path.is_file() and not path.is_symlink()
             and path.resolve().is_relative_to(root)
             and 0<path.stat().st_size<=12_000_000,
             "FRESH_V232_INSTALLED_G_CANDIDATE_OUTSIDE_ORIGINAL_STAGE")
        try:
            one_spec_candidate=json.loads(path.read_text("utf8"))
        except (OSError,ValueError,UnicodeError) as exc:
            raise UserScenarioBlocked(
                "FRESH_V232_INSTALLED_G_ORIGINAL_JSON_INVALID") from exc
        one_spec_candidate,other_spec_general_source=(
            _choose_user_specific_fresh_G_source(
                one_spec_candidate,user=user,calculation=calc))
        if other_spec_general_source:
            one_spec_candidate=_select_v216_source_only_user_spec(
                one_spec_candidate,user=user,
                environment_result=environment_result,calculation=calc)
    else:
        other_spec_general_source=False
    result=build(user,folder,binary,revision,
                 current_season_product=True,
                 season_source_bundle=bundle,
                 season_original_source_paths=originals,
                 season_profile_inputs=inputs,
                 season_socket_plan=(derived_settings.get(
                     "v271_socket_plan_unadmitted")
                     if derived_settings is not None else None),
                 fresh_installed_environment_path=installed_path,
                 season_physical_one_spec_candidate=one_spec_candidate,
                 season_selected_static_cache_path=(
                     selected_static_cache_path if selected_items else None),
                 exploration_policy=exploration_policy)
    proof=result["original_v191_gear_tier_source_unadmitted"]
    need(proof["source_catalog_artifact_sha256"]==
             calc.get("source_catalog_artifact_sha256") and
         proof["source_catalog_manifest_sha256"]==
             calc.get("source_catalog_manifest_sha256"),
         "SEASON_V216_GJFO_SOURCE_CATALOG_SHA_DRIFT")
    return {**result,
            "v216_to_v098_auto_source_linked_preview":True,
            "fresh_installed_v212_source_reused":installed_path is not None,
            "fresh_general_G_reference_used_for_other_spec":
                other_spec_general_source,
            "fresh_selected_spec_exact_native_G_not_claimed":
                other_spec_general_source,
            "user_dps_executed":False,
            "season_settings_source_admitted_here":False,
            "verified_user_default_options_registered":False,
            "season_settings_physical_gem_flask_assembled_unadmitted":
                derived_settings is not None,
            "existing_v271_variable_socket_connected_unadmitted":
                derived_settings is not None and
                derived_settings.get("v271_socket_plan_unadmitted") is not None,
            "optional_omnium_module_active_in_profile":
                season_settings["default_consumables"]["omnium_talents"]
                is not None,
            "v216_preflight_sha256":compilation.get("preflight_sha256")}



def run_from_verified_environment_build(user,folder,binary,revision,*,
                                        environment_result,
                                        season_controls=None,
                                        exploration_policy=None,
                                        execute=False,cache_only=False,
                                        open_folder=False):
    """One already-built season -> original v098/v096/v094, no extra G/F Native.

    The original v216/v217/v212 install is checked by v096 before the
    manifest is materialized. Only execution (not planning) invokes SimC.
    No synthetic source-only preview may authorize an adaptive run.
    """
    result=preview_from_environment_build(
        user,folder,binary,revision,environment_result=environment_result,
        season_controls=season_controls,
        exploration_policy=exploration_policy)
    if not execute:
        return result
    need(result.get("status")=="READY_SOURCE_BOUND_SEASON_MANIFEST_ZERO_NATIVE"
         and result.get("fresh_v212_installed_proof_reused") is True
         and type(result.get("generated_manifest")) is str,
         "FRESH_SEASON_INSTALLED_NATIVE_SOURCE_NOT_READY")
    actual=entry.run_manifest(
        result["generated_manifest"],cache_only=cache_only,
        open_folder=open_folder)
    return {"input_preparation":result,"native_result":actual}


def run(user_path,folder,binary,revision,static_cache_path=None,
        execute=False,cache_only=False,*,ordinary_variant=None,pure_stage=False,
        physical_acceptance_root=None,open_folder=True,independent_334=False,
        independent_target_level=False,source_first_stage=False,
        current_season_product=False,source_catalog_path=None,
        season_profile_inputs=None,season_environment_receipt_path=None,
        season_source_bundle=None,season_original_source_paths=None):
    # An exact v140 (historical 2 specs) or v145 (single preview profile)
    # physical Native receipt authorizes ONLY its identical internal profile.
    # v096 verifies original JSON2 bytes before any adaptive Native call.
    need(not (source_first_stage and execute),
         "SOURCE_FIRST_STAGE_NATIVE_NOT_AUTHORIZED")
    need(not (pure_stage and execute and physical_acceptance_root is None),
         "PURE_STAGE_NATIVE_NOT_AUTHORIZED")
    need(pure_stage or physical_acceptance_root is None,
         "PURE_PHYSICAL_ACCEPTANCE_NOT_FOR_SOURCE_PROFILES")
    path=pathlib.Path(user_path).resolve()
    user=json.loads(path.read_text(encoding="utf8"))
    imported=None
    if type(user) is dict and IMPORT_FIELD in user:
        relative=pathlib.Path(user[IMPORT_FIELD]).expanduser()
        resolved=(relative if relative.is_absolute() else path.parent/relative).resolve()
        need(resolved.is_file(),"SIMC_IMPORT_NOT_FOUND")
        imported=resolved.read_text(encoding="utf8")
    prepared=build(user,folder,binary,revision,static_cache_path,
                   imported_profile_text=imported,
                   ordinary_variant=ordinary_variant,pure_stage=pure_stage,
                   independent_334=independent_334,
                   independent_target_level=independent_target_level,
                   source_first_stage=source_first_stage,
                   current_season_product=current_season_product,
                   source_catalog_path=source_catalog_path,
                   season_profile_inputs=season_profile_inputs,
                   season_environment_receipt_path=
                       season_environment_receipt_path,
                   season_source_bundle=season_source_bundle,
                   season_original_source_paths=season_original_source_paths)
    if not execute:return prepared
    if pure_stage:
        actual=entry.run_manifest(prepared["generated_manifest"],
            cache_only=cache_only,
            physical_acceptance_root=physical_acceptance_root,
            open_folder=open_folder)
    else:
        actual=entry.run_manifest(prepared["generated_manifest"],cache_only=cache_only)
    return {"input_preparation":prepared,"native_result":actual}

def main(argv=None):
    p=argparse.ArgumentParser(description="Target user inputs -> internal representative SimC -> v096")
    p.add_argument("--input",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    p.add_argument("--binary",required=True,type=pathlib.Path)
    p.add_argument("--revision",required=True)
    p.add_argument("--static-cache",type=pathlib.Path)
    p.add_argument("--execute",action="store_true")
    p.add_argument("--pure-stage",action="store_true",
                   help="Internal source-independent stage; execute requires exact v140/v145 physical Native receipt")
    p.add_argument("--source-first-stage",action="store_true",
                   help="Internal only: use current v171 gear + v168 tier in existing v098 plan. Requires --pure-stage, never executes Native")
    p.add_argument("--physical-acceptance-root",type=pathlib.Path,
                   help="Internal v140 root (two historical specs), or exact v145 per-user physical output folder")
    p.add_argument("--cache-only",action="store_true")
    p.add_argument("--source-to-catalog",type=pathlib.Path,
                   help="Optional exact v213 source-to-catalog artifact for current-season approval")
    p.add_argument("--ordinary-variant",
                   choices=sorted(common.ORDINARY_VARIANTS),
                   help="Internal source-pinned representative test only; default unchanged")
    a=p.parse_args(argv)
    try:
        result=run(a.input,a.out,a.binary,a.revision,a.static_cache,
                   execute=a.execute,cache_only=a.cache_only,
                   ordinary_variant=a.ordinary_variant,pure_stage=a.pure_stage,
                   source_first_stage=a.source_first_stage,
                   physical_acceptance_root=a.physical_acceptance_root,
                   source_catalog_path=a.source_to_catalog)
        print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
        return 0
    except Exception as e:
        print("V098_BLOCKED:",type(e).__name__,str(e),file=sys.stderr)
        return 3
if __name__=="__main__":sys.exit(main())
