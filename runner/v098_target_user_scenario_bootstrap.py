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
import v101_common_representative_equipment as common
import v091_weapon_oil_external_adapter as oil_mod
import v096_unified_product_entry as entry
import v108_native_consumable_inputs as consumer
import v122_common_profile_format as profile_format
import v139_pure_target_profile_composer as pure
import v169_source_first_representative_stage as source_first
import v202_one_enchant_admission as verified_enchant
import v206_nonchmv_eagle_selection as nonchmv_enchant

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


def _current_season_profile_supplier_coverage(season_override, selected_key):
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
    need(supplied == expected,
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

def build(user,folder,binary,revision,static_cache_path=None,
          imported_profile_text=None,*,ordinary_variant=None,pure_stage=False,
          independent_334=False,independent_target_level=False,
          source_first_stage=False,current_season_product=False,
          static_special_probe_only=False,source_catalog_path=None):
    """Return an already validated internal manifest and v096 plan; no Native."""
    base_accepted=(FIELDS,FIELDS|{IMPORT_FIELD},FIELDS|{CONSUME_FIELD},
                   FIELDS|{IMPORT_FIELD,CONSUME_FIELD})
    # Existing Linux-pinned fixed-E pilot and one source-classified nonCHMV
    # user choice are separate; never combine them in one stage.
    accepted=(base_accepted+
              tuple(x|{ENCHANT_FIELD} for x in base_accepted)+
              tuple(x|{SEASON_ENCHANT_FIELD} for x in base_accepted))
    need(type(user) is dict and set(user) in accepted
         and user.get("schema")==SCHEMA,"USER_SCENARIO_FIELDS")
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
    # Source-independent P1 production specs compile from the season catalog.
    # Existing 24 source-backed default paths remain unchanged; explicit
    # pure_stage=True preserves the older v140 witness-only pilot contract.
    season_override=None
    profile_supplier_coverage=None
    if source_first_stage or current_season_product:
        season_override=source_first.season_scope()
        if current_season_product:
            profile_supplier_coverage=_current_season_profile_supplier_coverage(
                season_override,"/".join(key))
    if pure_stage or source_free:
        need(ordinary_variant is None and
             (ilvl==334 or independent_target_level or current_season_product),
             "PURE_STAGE_TARGET_OR_VARIANT_NOT_READY")
        base_profile,cfg,rows,groups,weapon_layout,F,tier_data,fifth_data=(
            pure.v098_inputs(ch,user["trinkets"],target_ilevel=ilvl,
                             combat=combat,
                             level_preview=(independent_target_level or
                                            (current_season_product and ilvl!=334)),
                             season_override=season_override))
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
    if pure_stage or source_free:
        restored_tier_slots,catalyst_origin_rows=common.apply_user_equipment(
            key,rows,groups,user,ilvl,need,
            tier_override=tier_data,fifth_override=fifth_data,
            flexible_current_tier=current_season_product)
    else:
        restored_tier_slots,catalyst_origin_rows=common.apply_user_equipment(
            key,rows,groups,user,ilvl,need)
    # 240967 requires four distinct ordinary Midnight gem colors for its
    # crit-effectiveness bonus. These are real SimC gem IDs, not locked CHMV.
    # Existing 240983 profiles and already-four-color source rows stay intact.
    choice=user.get(CONSUME_FIELD) or {}
    gem_choice=choice.get("diamond_id") or int(
        rows["head"]["options"].get("gem_id","0"))
    common.ensure_representative_gem_colors(rows,gem_choice,need)
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
    selected=consumer.apply(profile,cfg,rows,
                            user.get(CONSUME_FIELD))
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

def run(user_path,folder,binary,revision,static_cache_path=None,
        execute=False,cache_only=False,*,ordinary_variant=None,pure_stage=False,
        physical_acceptance_root=None,open_folder=True,independent_334=False,
        independent_target_level=False,source_first_stage=False,
        current_season_product=False,source_catalog_path=None):
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
                   source_catalog_path=source_catalog_path)
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
