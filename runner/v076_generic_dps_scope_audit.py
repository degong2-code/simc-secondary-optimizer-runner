#!/usr/bin/env python3
"""v076: reproducible, READ-ONLY source-contract audit and six-case DPS test design.

The audit confirms source structure and test coverage categories, never native
SimC success, legal character combinations, item availability or any proc.
No effect gates, independent APLs, new optimization search, or SimC calls.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA = "v076_dps_generic_engine_scope_audit_v1"
CORE = {
    "scenario": "runner/v061_scenario_contract.py",
    "budget": "runner/v062_static_budget_bridge.py",
    "injection": "runner/v063_numeric_injection.py",
    "evaluation": "runner/v064_adaptive_evaluator_port.py",
    "scheduler": "runner/v065_v015_scheduler_adapter.py",
    "native_executor": "runner/v065_original_scheduler_native_bridge.py",
    "preflight": "runner/v066_profile_neutral_preflight.py",
    "generic_route": "runner/v067_generic_adaptive_native_route.py",
}
ACCEPTANCE_FIXTURE = "runner/v068_rogue_user_profile.py"
# One test per structural category; never present an unverified proposed
# profile as a SimC-accepted character or real item/gear fixture.
SIX_CASES = (
    ("rogue","subtlety","void_elf","leather","one_hand_dual","agility","attack","historical_native"),
    ("mage","arcane","human","cloth","one_hand_frill","intellect","spell","historical_native_limited"),
    ("shaman","elemental","orc","mail","one_hand_shield","intellect","spell","planned_no_native"),
    ("hunter","beast_mastery","troll","mail","ranged","agility","attack","planned_no_native"),
    ("warrior","fury","dwarf","plate","two_hand_dual","strength","attack","planned_no_native"),
    ("paladin","retribution","blood_elf","plate","two_hand_single","strength","attack","planned_no_native"),
)
ARMOR={"cloth","leather","mail","plate"}
WEAPONS={"one_hand_dual","one_hand_frill","one_hand_shield",
         "ranged","two_hand_dual","two_hand_single"}
STATS={"agility","strength","intellect"}
ROLES={"attack","spell"}
REQUIRED_FUNCTIONS = {
    "scenario":{"normalize","equipment","entry"},
    "budget":{"compile_static_budget","get_native_secondary"},
    "injection":{"calibrate","input_parts","read_rating"},
    "evaluation":{"make_request","ingest_native","verify_disk_cache"},
    "scheduler":{"initial_state","next_scout","accept_scout"},
    "native_executor":{"execute_one"},
    "preflight":{"prepare","load_witnesses"},
    "generic_route":{"route"},
}
GENERIC_BOUNDARY_MODULES={"scenario","budget","injection","evaluation",
                          "scheduler","native_executor","preflight","generic_route"}
ISOLATED_FIXTURES = {"v068_rogue_user_profile","v068_rogue_two_native_probe",
     "v069_rogue_official_budget_native","v071_rogue_adaptive_first_scout",
     "v072_rogue_high_iteration_confirm","v073_rogue_material_adaptive_scout",
     "v074_rogue_selected_D_high_confirmation","v075_rogue_coarse_continuation"}

def require(value, reason):
    if not value:
        raise ValueError(reason)

def read_asts(root):
    result={}
    for label,rel in {**CORE,"user_rogue_fixture":ACCEPTANCE_FIXTURE}.items():
        path=root/rel
        data=path.read_bytes()
        tree=ast.parse(data.decode("utf8"),filename=rel)
        imports=set()
        functions=set()
        for node in ast.walk(tree):
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                functions.add(node.name)
            elif isinstance(node,ast.Import):
                imports.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node,ast.ImportFrom):
                if node.module:imports.add(node.module.split(".")[0])
        result[label]={"path":rel,"sha256":hashlib.sha256(data).hexdigest(),
                       "functions":functions,"imports":imports,"source":data.decode("utf8")}
    return result

def audit(root=ROOT):
    d=read_asts(root)
    # This does not pretend that a class-neutral source implies Native support.
    for name,funcs in REQUIRED_FUNCTIONS.items():
        require(funcs <= d[name]["functions"],
                "CORE_FUNCTION_MISSING:"+name+":"+repr(funcs-d[name]["functions"]))
    for name in GENERIC_BOUNDARY_MODULES:
        direct=d[name]["imports"] & ISOLATED_FIXTURES
        require(not direct,"GENERIC_IMPORTS_USER_FIXTURE:"+name+":"+repr(direct))
    preflight=d["preflight"]["source"]
    route=d["generic_route"]["source"]
    scenario=d["scenario"]["source"]
    static=d["budget"]["source"]
    require("TWO_PROFILE_SCOPED_NATIVE_WITNESSES_REQUIRED" in preflight,
            "TWO_WITNESS_PREFLIGHT_NOT_FOUND")
    require("reference" in preflight and "fillers" in preflight and
            "static_records" in preflight,"PREPARED_INPUT_BOUNDARY_DRIFT")
    require("preflight.load_witnesses" in route and
            "preflight.prepare" in route,"GENERIC_ROUTE_WITNESS_BOUNDARY_DRIFT")
    require('"tank"' in scenario and '"heal"' in scenario,
            "OFFICIAL_ROLE_SET_CHANGED_WITHOUT_APPROVAL")
    require("missing_nontrinket_static" in static and
            "UNREPORTED_UNKNOWN_NOT_ZERO" in static and
            "oil_stays_OUTSIDE_T" in static,
            "OFFICIAL_STATIC_CONTRACT_DRIFT")
    assert_matrix()
    receipts=[
      {"name":k,"path":v["path"],"sha256":v["sha256"],
       "declared_functions":sorted(v["functions"])}
      for k,v in d.items()]
    rows=[{"class":cl,"spec":sp,"race":ra,"armor":ar,"weapon_form":we,
           "primary":pr,"scenario_role":ro,"evidence":ev,
           "race_class_pair_native_verified_in_this_stage":False,
           "exact_equipment_ids_ready_in_this_stage":False}
          for cl,sp,ra,ar,we,pr,ro,ev in SIX_CASES]
    # THESE ARE OBSERVED SOURCE-BOUNDARY GAPS, not a PASS for coverage.
    gaps=[
      {"id":"GENERIC_PROFILE_PRODUCER_NOT_IN_V067",
       "severity":"P1_BLOCKS_ZERO_MANUAL_SETUP",
       "evidence":"v067.route requires caller-provided --profile, --filler, --static-cache, --witness-root",
       "resolution":"build or adapt representative profile producer with per-case exact IDs; do not construct fake SimC acceptances"},
      {"id":"EXACT_ITEM_VARIANTS_REQUIRED_PER_PROFILE",
       "severity":"P1_BLOCKS_NATIVE_DERIVED_G",
       "evidence":"v066.prepare stops on missing exact non-trinket Native static variants",
       "resolution":"reuse same-season exact cache, lazily resolve only actual missing variants"},
      {"id":"NUMERIC_CALIBRATION_BOOTSTRAP_REQUIRES_TWO_REAL_WITNESSES",
       "severity":"P1_BLOCKS_FIRST_GENERIC_NATIVE",
       "evidence":"v066.prepare requires two prior profile-scoped Native witnesses before v067.route",
       "resolution":"add bounded 2-witness Native bootstrap for a NEW profile; never reuse Rogue/Mage numeric offsets"},
      {"id":"WEAPON_FORM_NOT_EXPLICIT_IN_V061_OR_V062",
       "severity":"P2_COVERAGE_NOT_PROVEN",
       "evidence":"generic static budget binds slot/id/ilevel/options, not 1h/2h/shield/frill/ranged type",
       "resolution":"use actual SimC-valid representative profiles and input-level slot/item identity; avoid new effect-certification gates"},
      {"id":"CLASS_SPEC_RACE_ELIGIBILITY_NOT_NATIVE_ATTESTED",
       "severity":"P2_TEST_DATA_REQUIRED",
       "evidence":"v061 checks class whitelist but spec and race tokens are not a class/race compatibility database",
       "resolution":"obtain exact SimC-valid six-case inputs before claiming archetype native PASS"},
      {"id":"DPS_ONLY_USER_REQUEST_CONFLICTS_WITH_APPROVED_ROLE_SCOPE",
       "severity":"APPROVAL_BOUNDARY",
       "evidence":"Developer Notes v1.2 includes tank/heal; current v061 role set includes both",
       "resolution":"restrict THIS test matrix to DPS; do not change product source/role contract without authorized decision"},
    ]
    return {"schema":SCHEMA,
            "status":"PASS_READ_ONLY_SOURCE_AUDIT_WITH_OPEN_GENERIC_GAPS",
            "meaning":"source structure verified; generic Native acceptance NOT proven",
            "new_native_calls":0,
            "source_snapshots":receipts,
            "matrix":rows,
            "matrix_cover":{
              "armors":sorted({r["armor"] for r in rows}),
              "weapon_forms":sorted({r["weapon_form"] for r in rows}),
              "primary_stats":sorted({r["primary"] for r in rows}),
              "unique_races":len({r["race"] for r in rows}),
              "cases":len(rows),"new_profile_native_tests_completed":0},
            "open_gaps":gaps,
            "formula":"T=G+J+F","oil_added_to_T":False,
            "core_native_dps_calls":0,
            "test_scope":"DPS representative scenarios only; existing approved role set unchanged",
            "original_v015_v016_merged":False,
            "work_os_modified":False,
            "global_optimum_proven":False}

def assert_matrix():
    require(len(SIX_CASES)==6,"SIX_COVERAGE_CASES_REQUIRED")
    require(len({x[2] for x in SIX_CASES})==6,"RACES_NOT_DIVERSE")
    require({x[3] for x in SIX_CASES}==ARMOR,"ARMOR_MISSING")
    require({x[4] for x in SIX_CASES}==WEAPONS,"WEAPON_FORM_MISSING")
    require({x[5] for x in SIX_CASES}==STATS,"PRIMARY_STAT_MISSING")
    require({x[6] for x in SIX_CASES}<=ROLES,"NON_DPS_ROLE_IN_MATRIX")
    require(len({(x[0],x[1]) for x in SIX_CASES})==6,"SPEC_DUPLICATED")

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args(argv)
    result=audit(ROOT)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,
                  indent=2)+"\n",encoding="utf8")
    print("V076",result["status"],"cases",len(result["matrix"]),
          "gaps",len(result["open_gaps"]),"new_native",0)
    return 0

if __name__=="__main__":
    sys.exit(main())
