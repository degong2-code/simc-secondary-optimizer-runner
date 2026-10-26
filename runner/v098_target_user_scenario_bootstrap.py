#!/usr/bin/env python3
"""v098 target-level USER inputs -> internally generated v096 source-locked manifest.

Bounded source-backed archetypes: Fury, Frost Mage, Retribution, Beast Mastery.
Not a new item DB, equipment optimizer, SimC effect evaluator or general class
coverage claim. Planning invokes ZERO Native SimC calls.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,pathlib,sys
import v046_static_item_cache as cache_mod
import v055_simc_item_selection as item_mod
import v061_scenario_contract as scenario
import v065_v015_scheduler_adapter as scheduler
import v101_common_representative_equipment as common
import v091_weapon_oil_external_adapter as oil_mod
import v096_unified_product_entry as entry

SCHEMA="v098_target_ilevel_user_scenario_v1"
FIELDS={"schema","character","target","trinkets","special_items",
        "embellishments","oil_hands","combat"}
# Backward-compatible public source metadata; ownership moved to v101.
ARCHETYPES=common.ARCHETYPES
FIXTURES=common.FIXTURES
IMPORT_FIELD="import_simc_profile"
TIER_FIVE=common.TIER_FIVE
FIFTH_TIER=common.FIFTH_TIER

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
          imported_profile_text=None):
    """Return an already validated internal manifest and v096 plan; no Native."""
    need(type(user) is dict and set(user) in (FIELDS,FIELDS|{IMPORT_FIELD})
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
    need(key in ARCHETYPES,"REPRESENTATIVE_ARCHETYPE_NOT_READY:"+"/".join(key))
    for name in ("race","talents"):
        scenario.text_token(ch[name],"USER_"+name.upper())
    tgt=user["target"]
    need(type(tgt) is dict and set(tgt)=={"ilevel","final_T"},
         "USER_TARGET_FIELDS")
    ilvl=tgt["ilevel"];final_T=tgt["final_T"]
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
    folder=pathlib.Path(folder).resolve()
    binary=pathlib.Path(binary).resolve()
    need(binary.is_file(),"SIMC_BINARY_NOT_PRESENT")
    need(type(revision) is str and len(revision)>=7,"SIMC_REVISION_REQUIRED")
    # SimC APL and original item IDs stay in pinned source factory; v101 owns
    # the material/weapon/tier representative gear assembly thereafter.
    base_profile,cfg,rows,groups,weapon_layout,F=common.source_backed_gear(
        key,folder,ilvl,need)
    restored_tier_slots,catalyst_origin_rows=common.apply_user_equipment(
        key,rows,groups,user,ilvl,need)
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
    cfg["source"]={"kind":"user_supplied",
                   "profile_sha256":hashlib.sha256(profile.encode("utf8")).hexdigest()}
    scenario.normalize(cfg)
    static=(cache_mod.empty_cache() if static_cache_path is None
            else cache_mod.load(pathlib.Path(static_cache_path)))
    prepared=oil_mod.prepare(profile,cfg,fillers,static,weapon_layout,
                             user["oil_hands"],manual_final_T=final_T)
    normalized=prepared["prepared"]["scenario"]
    budget=prepared["prepared"]["static_budget"]
    B,lo,hi=scheduler.bounds(normalized,budget)
    seeds=initial_seeds(B,lo,hi)
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
    put_once(folder/"profile.simc",profile)
    put_once(folder/"scenario.json",canonical(cfg)+"\n")
    put_once(folder/"fillers.json",canonical(fillers)+"\n")
    put_once(folder/"manifest.json",canonical(manifest)+"\n")
    plan=entry.run_manifest(folder/"manifest.json",plan_only=True)
    need(plan["base_B"]==B and plan["item_slots"]==len(rows),
         "BOOTSTRAP_TO_V096_BUDGET_OR_SLOT_DRIFT")
    return {"schema":SCHEMA,"status":"READY_INTERNAL_MANIFEST_ZERO_NATIVE",
            "user_does_not_supply_full_gear_or_simc_profile":True,
            "template_archetype":"/".join(key),"target_ilevel":ilvl,
            "generated_manifest":str(folder/"manifest.json"),
            "output_dir":str(folder/"simc_results"),"plan":plan,
            "native_calls":0,"supported_archetypes_now":len(ARCHETYPES),
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
            "all_specs_ready":False}

def run(user_path,folder,binary,revision,static_cache_path=None,
        execute=False,cache_only=False):
    path=pathlib.Path(user_path).resolve()
    user=json.loads(path.read_text(encoding="utf8"))
    imported=None
    if type(user) is dict and IMPORT_FIELD in user:
        relative=pathlib.Path(user[IMPORT_FIELD]).expanduser()
        resolved=(relative if relative.is_absolute() else path.parent/relative).resolve()
        need(resolved.is_file(),"SIMC_IMPORT_NOT_FOUND")
        imported=resolved.read_text(encoding="utf8")
    prepared=build(user,folder,binary,revision,static_cache_path,
                   imported_profile_text=imported)
    if not execute:return prepared
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
    p.add_argument("--cache-only",action="store_true")
    a=p.parse_args(argv)
    try:
        result=run(a.input,a.out,a.binary,a.revision,a.static_cache,
                   execute=a.execute,cache_only=a.cache_only)
        print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
        return 0
    except Exception as e:
        print("V098_BLOCKED:",type(e).__name__,str(e),file=sys.stderr)
        return 3
if __name__=="__main__":sys.exit(main())
