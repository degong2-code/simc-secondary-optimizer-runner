#!/usr/bin/env python3
"""v045 bounded SimC-first gear inventory and CHMV candidate.

Full slot/name/ID/options/static-stat audit against already-pinned Native
JSON2. Hand-authored JSON is a *hint*, never authority for stat totals.
The oil-inclusive 3185 trial is not an amendment to v1.0 T=G+J+F.
SimC remains the authority for effects and DPS; this code never models procs.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,re,subprocess,sys

import pilot
import v039_venomkeeper_bare_probe as bare
import v041_catalyst_gem_proc_probe as v041
import v044_static_budget_attribution as v044

SCHEMA="v045_simc_first_budget_oil_floor_v2"
STATS=v044.STATS
OIL=(16,16,0,0)
FLASK=(0,165,0,0) # pinned haste-flask trial only
TEST_TARGET=(600,1140,1115,330) # 3185, trial, not optimizer recommendation
CHECK_OPTIONS=("id","ilevel","gem_id","bonus_id","redirected_base_stats",
               "crafted_stats","embellishment","enchant","enchant_id")
class Blocked(ValueError): pass
def need(ok,reason):
    if not ok:raise Blocked(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def parse_slots(source):
    items={}
    for raw in source.splitlines():
        if raw.startswith('#') or '=' not in raw:continue
        name,item=raw.split('=',1)
        if name in v044.SLOTS:
            need(name not in items,"DUPLICATE_SLOT:"+name)
            items[name]=item
    need(set(items)==set(v044.SLOTS),"PROFILE_SLOTS_MISSING")
    return items
def parts(s):
    need(isinstance(s,str) and s,"ENCODED_ITEM_EMPTY")
    seq=s.split(',');name=seq[0];options={}
    need(bool(name),"ITEM_NAME_ABSENT")
    for token in seq[1:]:
        need('=' in token,"ITEM_OPTION_MALFORMED")
        key,value=token.split('=',1)
        need(key not in options,"DUPLICATE_ITEM_OPTION:"+key)
        options[key]=value
    return name,options

def audit_inventory(source_bytes,native_bytes,hint_bytes=None):
    """Every slot matched from the original SimC request vs genuine JSON2."""
    native=v044.analyze(source_bytes,native_bytes) # pinned v042 byte identities
    profile=parse_slots(source_bytes.decode("utf-8"))
    doc=json.loads(native_bytes)
    gear=doc["sim"]["players"][0]["gear"]
    hints=None
    if hint_bytes is not None:
        hints=json.loads(hint_bytes)
        need(hints.get('schema')=='v045_pinned_v042_static_334_v1',
             "HINT_SCHEMA_CHANGED")
        need(hints.get('native_json2_sha256')==v044.NATIVE_SHA,
             "HINT_REFERENCE_DRIFT")
        need(set(hints.get('item_ids',{}))==set(gear),"HINT_SLOT_SET_DRIFT")
    audited=[];static_total=[0,0,0,0];fixed_mastery=0
    for slot in v044.SLOTS:
        input_name,a=parts(profile[slot])
        native_name,b=parts(gear[slot]['encoded_item'])
        need(input_name==native_name,"SIMC_NAME_MISMATCH:"+slot)
        for field in CHECK_OPTIONS:
            need(a.get(field)==b.get(field),"SIMC_OPTION_MISMATCH:"+slot+":"+field)
        need(gear[slot].get('ilevel')==334 and a.get("ilevel")=="334",
             "ILEVEL_CHANGED:"+slot)
        need(str(gear[slot].get("name"))==native_name,
             "NATIVE_ITEM_NAME_FIELD_DRIFT:"+slot)
        need(a.get('id') and a['id'].isdigit(),"INVALID_ITEM_ID:"+slot)
        if hints:
            need(hints['item_ids'][slot]==int(a['id']),"HINT_ITEM_ID_MISMATCH:"+slot)
        vector=[gear[slot].get(s,0) for s in STATS]
        need(all(type(x) is int and x>=0 for x in vector),
             "NATIVE_STATIC_RATING_INVALID:"+slot)
        if slot not in v044.TRINKETS:
            for i,v in enumerate(vector):static_total[i]+=v
        if slot=="head":
            need(vector==[0,0,201,0],"HEAD_FIXED_MASTERY_CHANGED")
            fixed_mastery=201
        audited.append({"slot":slot,"native_item_name":native_name,"native_item_id":int(a["id"]),
            "ilevel":334,"native_static_rating":dict(zip(STATS,vector)),
            "input_and_native_options_match":True,
            "native_options":{k:b[k] for k in CHECK_OPTIONS if k in b},
            "external_name_canonicality_verified":False})
    G=sum(static_total)
    need(G==native['static_nontrinket_gear_sum_all_stats'],"NATIVE_G_RECOUNT_DRIFT")
    need(G==2850,"PINNED_V042_G_CHANGED")
    return {"schema":SCHEMA,"status":"PASS_ALL_15_SIMC_SLOTS_VS_INPUT",
        "test_success":True,"source_kind":"ACTUAL_PINNED_SIMC_JSON2_NOT_USER_ITEM_JSON",
        "json_item_hints_used_for_identity_only":hints is not None,
        "native_source_sha256":v044.NATIVE_SHA,
        "input_source_sha256":v044.INPUT_SHA,
        "slots_checked":len(audited),"items":audited,
        "native_G":G,"native_G_vector":dict(zip(STATS,static_total)),
        "native_external_trinket_static":native["trinket_gear_secondary_external"],
        "special_fixed_mastery_floor":fixed_mastery,
        "known_flask_input_to_native_offset":native["final_minus_gear_override"],
        "known_flask_offset_not_generalized":True,
        "items_are_pinned_trial_not_live_user_selection":True,
        "unverified_real_catalyst_bonus":True,
        "product_code_integrated":False,"official_policy_promoted":False}

def make_plan(inventory,target=TEST_TARGET,include_oil_trial=True):
    need(inventory.get("status")=="PASS_ALL_15_SIMC_SLOTS_VS_INPUT",
         "SIMC_INVENTORY_REQUIRED")
    G=inventory["native_G"];J=138;F=165
    need(G==2850,"PINNED_G_CHANGED")
    v1_total=G+J+F
    oil_total=sum(OIL)
    trial_total=v1_total+(oil_total if include_oil_trial else 0)
    need(type(target) is tuple and len(target)==4 and
         all(type(n) is int and n>=0 for n in target),"TARGET_SHAPE")
    need(sum(target)==trial_total,"CHMV_TOTAL_MISMATCH")
    cap=trial_total//2
    # Oil + selected special fixed stat must remain INSIDE the candidate.
    locked=(OIL[0],OIL[1],inventory["special_fixed_mastery_floor"],0)
    require_floors=tuple(max(locked[i],FLASK[i]) for i in range(4))
    need(all(require_floors[i]<=target[i]<=cap for i in range(4)),
         "CANDIDATE_FIXED_FLOOR_OR_CAP_BREACH")
    override=tuple(target[i]-FLASK[i] for i in range(4))
    need(all(x>=0 for x in override),"NEGATIVE_OVERRIDE")
    need(sum(override)==trial_total-F,"OVERRIDE_ALREADY_HAS_FLASK")
    return {"schema":SCHEMA,"status":"PASS_BOUNDED_INPUT_PLAN_NOT_POLICY",
        "G":G,"J":J,"F":F,"v1_0_official_T":v1_total,
        "oil_trial_rating":dict(zip(STATS,OIL)),
        "oil_inclusion_is_bounded_unpromoted_scenario":include_oil_trial,
        "bounded_trial_T":trial_total,
        "required_static_floor":dict(zip(STATS,locked)),
        "candidate":dict(zip(STATS,target)),
        "gear_override":dict(zip(STATS,override)),
        "expected_flask_delta":dict(zip(STATS,FLASK)),
        "oil_subtraction_already_accounted_once":include_oil_trial,
        "product_code_integrated":False,"official_policy_promoted":False,
        "user_item_selection_attested":False,
        "actual_scenario_DPS_comparison_authorized":False}

def build_profile(reference,result,case):
    # Single controlled change: original v041 effect/gem/tier preserved;
    # change only the four gear_* override lines.
    src=v041.build_source(reference,result)
    lines=src.splitlines()
    for stat,n in case["gear_override"].items():
        key="gear_"+stat+"="
        found=[i for i,s in enumerate(lines) if s.startswith(key)]
        need(len(found)==1,"GEAR_OVERRIDE_NOT_UNIQUE:"+stat)
        lines[found[0]]=key+str(n)
    need(sum(x.startswith("json2=") for x in lines)==1,"JSON2_NOT_UNIQUE")
    return "\n".join(lines)+"\n"

def audit_result(native_bytes,plan,inventory):
    base=v041.audit_native(native_bytes)
    doc=json.loads(native_bytes);p=doc["sim"]["players"][0]
    actual={}
    for stat in STATS:
        value=p["collected_data"]["buffed_stats"]["stats"].get(stat)
        need(type(value) in (float,int) and abs(value-round(value))<1e-8,
             "INVALID_FINAL_RATING:"+stat)
        actual[stat]=int(round(value))
    need(actual==plan["candidate"],"FINAL_CHMV_NOT_TARGET")
    need(sum(actual.values())==plan["bounded_trial_T"],"FINAL_TOTAL_MISMATCH")
    prior={x["slot"]:(x["native_item_id"],x["native_static_rating"],x["native_options"],x["native_item_name"]) for x in inventory["items"]}
    need(set(prior)==set(p["gear"]),"SLOTS_CHANGED")
    for slot,record in p["gear"].items():
        name,opts=parts(record["encoded_item"])
        id_,stats,options,oldname=prior[slot]
        need(int(opts.get("id","0"))==id_ and record.get("ilevel")==334
             and name==oldname,"NATIVE_GEAR_ID_DRIFT:"+slot)
        need({s:record.get(s,0) for s in STATS}==stats,
             "NATIVE_GEAR_STATS_DRIFT:"+slot)
        need({k:opts[k] for k in CHECK_OPTIONS if k in opts}==options,
             "NATIVE_GEAR_EFFECT_OPTIONS_DRIFT:"+slot)
    need(p.get("flask")=="flask_of_the_blood_knights_2"
         and p.get("temporary_enchant")=="main_hand:thalassian_phoenix_oil_2",
         "CONSUMABLE_CHANGED")
    return {"status":"PASS_PINNED_3185_FINAL_CHMV_ONE_NATIVE_ONLY",
        "actual_final_chmv":actual,"native_json2_sha256":sha(native_bytes),
        "native_sample_count":base["sample_count"],"all_15_gear_slots_preserved":True,
        "oil_effect_already_proven_real_game":False,
        "DPS_optimization_proven":False,
        "product_code_integrated":False,"official_policy_promoted":False}

def run(binary,evidence_dir,output,mode):
    output.mkdir(parents=True,exist_ok=True)
    receipt={"schema":SCHEMA,"status":"BLOCKED","test_success":False,
       "product_code_integrated":False,"official_policy_promoted":False,
       "native_max_calls":1 if mode=="native" else 0,
       "native_calls_attempted":0,
       "product_admission":"BLOCKED_NOT_GENERALIZED_AND_V016_LINEAGE_UNVERIFIED"}
    try:
        source=(evidence_dir/v044.SOURCE).read_bytes()
        native=(evidence_dir/v044.NATIVE).read_bytes()
        hints=pathlib.Path(__file__).resolve().parents[1]/"integration_probes/evidence/v045_v042_native_static_334.json"
        inventory=audit_inventory(source,native,hints.read_bytes())
        receipt["inventory"]=inventory
        plan=make_plan(inventory)
        receipt["plan"]=plan
        (output/"V045_INVENTORY.json").write_text(json.dumps(inventory,indent=2)+"\n")
        if mode=="native":
            need(binary is not None and binary.is_file() and
                 sha(binary.read_bytes())==v041.prior.BIN_SHA,
                 "PINNED_BINARY_CHANGED")
            old,_=pilot.source()
            bare.verify_preconditions(old,binary)
            result=(output/"result.json").resolve()
            inputpath=(output/"input.simc").resolve()
            inp=build_profile(old,result,plan)
            inputpath.write_text(inp)
            # Head +14 others must not change relative to pinned Native.
            source_slots=parse_slots(inp)
            for item in inventory['items']:
                name,parts_in=parts(source_slots[item['slot']])
                need(name==item['native_item_name'] and
                     parts_in.get('id')==str(item['native_item_id']) and
                     {k:parts_in[k] for k in CHECK_OPTIONS if k in parts_in}
                       ==item['native_options'],
                     "INPUT_SLOT_CHANGED:"+item['slot'])
            receipt["input_sha256"]=sha(inputpath.read_bytes())
            receipt["native_calls_attempted"]=1
            (output/"V045_PROGRESS.json").write_text(json.dumps(receipt,indent=2)+"\n")
            process=subprocess.run([str(binary),str(inputpath)],
                cwd=binary.parent,stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=100)
            (output/"stdout.txt").write_bytes(process.stdout)
            (output/"stderr.txt").write_bytes(process.stderr)
            need(process.returncode==0,"SIMC_EXIT_"+str(process.returncode))
            need(result.is_file(),"MISSING_NATIVE_OUTPUT")
            receipt["native"]=audit_result(result.read_bytes(),plan,inventory)
            receipt["status"]="PASS_ONE_BOUNDED_NATIVE_OIL_FLOOR_NOT_POLICY"
        else:
            receipt["status"]="PASS_OFFLINE_NATIVE_INVENTORY_AND_PLAN_ONLY"
        receipt["test_success"]=True
    except Exception as exc:
        receipt["error_code"]=type(exc).__name__+":"+str(exc)
    (output/"V045_RECEIPT.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print("V045",receipt["status"],"native_attempts",receipt["native_calls_attempted"],flush=True)
    return 0 if receipt["test_success"] else 3

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--evidence-dir",type=pathlib.Path,required=True)
    ap.add_argument("--output",type=pathlib.Path,required=True)
    ap.add_argument("--binary",type=pathlib.Path)
    ap.add_argument("--mode",choices=("offline","native"),default="offline")
    x=ap.parse_args()
    return run(x.binary.resolve() if x.binary else None,
               x.evidence_dir.resolve(),x.output.resolve(),x.mode)
if __name__=="__main__":sys.exit(main())
