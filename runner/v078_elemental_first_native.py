#!/usr/bin/env python3
"""v078: first cross-class real Native bootstrap using pinned upstream Elemental.

Uses upstream SimC APL without rewriting actions, exact source-backed item IDs
and v077 raw witness input builder. This is a bounded 2-witness calibration and
native static-readiness proof, not a 320-iteration optimizer or effect gate.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,re,subprocess,sys
import v046_static_item_cache as static_cache
import v055_simc_item_selection as items
import v061_scenario_contract as scenario
import v062_static_budget_bridge as budgets
import v063_numeric_injection as numeric
import v066_profile_neutral_preflight as preflight
import v077_generic_profile_bootstrap_readiness as first_use
import v068_rogue_two_native_probe as native_pin
import v065_original_scheduler_native_bridge as durable

SCHEMA="v078_elemental_cross_class_first_real_native_v1"
UPSTREAM_BLOB="c92d111e37bd684647e4637dcfef3ccb92864cde"
ITERATIONS=35
MAX_NATIVE=2
SLOTS=("head","neck","shoulders","back","chest","wrists","hands","waist",
       "legs","feet","finger1","finger2","trinket1","trinket2","main_hand","off_hand")
# Item IDs from pinned upstream Elemental Shaman profile; single head
# replacement 271441 is from official MID2 BM Hunter profile, same mail
# armor family, avoiding a fifth Shaman tier piece. These are a test fixture,
# not user gear recommendations or a complete season item catalog.
HEAD_SOURCE="MID2_Hunter_Beast_Mastery.simc"
HEAD_ID=271441
TIER_SLOTS=("shoulders","chest","hands","legs")
CRAFTED_SLOTS=("wrists","feet")
TRINKET_SLOTS=("trinket1","trinket2")
INITIAL_RAW=(700,700,700,700)
GEMMED={"head":"240983","neck":"240906/240906",
        "wrists":"240906","waist":"240906",
        "finger1":"240906","finger2":"240906"}
CRAFTED={"wrists":"36/49","feet":"36/49"}

class Blocked(ValueError): pass
def need(x,reason):
    if not x:raise Blocked(reason)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(pathlib.Path(path).read_text(encoding="utf8"))

def extract(upstream):
    """Use original item IDs, not a fabricated equipment DB."""
    pos={}
    for line in upstream.splitlines():
        if line.startswith("# Gear Summary"):break
        k,sep,val=line.partition("=")
        if sep and k in SLOTS:
            need(k not in pos,"SOURCE_DUPLICATE_SLOT:"+k)
            match=re.search(r"(?:^|,)id=(\d+)(?:,|$)",val)
            need(match is not None,"UPSTREAM_ID_MISSING:"+k)
            pos[k]=int(match.group(1))
    need(set(pos)==set(SLOTS),"UPSTREAM_SIXTEEN_EQUIPMENT_ROWS_REQUIRED")
    original=dict(pos)
    pos["head"]=HEAD_ID
    return pos,original

def entry(slot,item_id):
    opts={}
    if slot in GEMMED:opts["gem_id"]=GEMMED[slot]
    if slot in CRAFTED:opts["crafted_stats"]=CRAFTED[slot]
    return {"slot":slot,"item_id":item_id,"ilevel":334,"options":opts}

def spec_profile(upstream,out):
    need('shaman="MID2_Shaman_Elemental_Farseer"' in upstream
         and "spec=elemental" in upstream
         and "race=tauren" in upstream
         and upstream.count("actions.precombat=")==1
         and upstream.count("actions=")==1,
         "PINNED_UPSTREAM_SHAMAN_PROFILE_DRIFT")
    ids,original=extract(upstream)
    gear={s:entry(s,ids[s]) for s in SLOTS}
    char={"class":"shaman","spec":"elemental","race":"orc",
          "role":"spell"}
    talents=[line.split("=",1)[1] for line in upstream.splitlines()
             if line.startswith("talents=")]
    need(len(talents)==1,"UPSTREAM_TALENTS_COUNT")
    char["talents"]=talents[0]
    # Derive from exact pinned APL and replace only canonical named settings
    # and fixture gear. Missing redirected/bonus source tokens are intentionally
    # not silently claimed preserved: this is an explicitly normalized
    # representative 334 TEST fixture with independently stated ID/options.
    canonical={"race":"orc","fight_style":"Patchwerk","desired_targets":"1",
      "max_time":"300","vary_combat_length":"0","fixed_time":"1",
      "optimal_raid":"1","threads":"1","iterations":str(ITERATIONS),
      "json2":str((pathlib.Path(out)/"reference.json").resolve()),
      "temporary_enchant":None}
    canonical.update({"gear_"+k:str(v) for k,v in
       zip(scenario.STATS,INITIAL_RAW)})
    source=[]
    for line in upstream.splitlines():
        if line.startswith("# Gear Summary"):break
        k,sep,_=line.partition("=")
        if sep and not line.startswith("#") and (k in SLOTS or k in canonical):
            continue
        source.append(line)
    source.extend("")
    source.extend(k+"="+v for k,v in canonical.items() if v is not None)
    source.extend(items.equipment_line(x,gear[x]["item_id"],334,gear[x]["options"])
                  for x in SLOTS)
    reference="\n".join(source).rstrip()+"\n"
    before=[line for line in upstream.splitlines() if line.startswith("actions")]
    after=[line for line in reference.splitlines() if line.startswith("actions")]
    need(before==after,"UPSTREAM_ACTION_LINES_CHANGED")
    scenario_doc={
      "schema":scenario.SCHEMA,"character":char,
      "source":{"kind":"user_supplied","profile_sha256":sha(reference.encode("utf8"))},
      "target":{"mode":"derived_ilevel","ilevel":334,
                "manual_total":None,"manual_total_scope":None},
      "equipment":{
        "tier":[gear[k] for k in TIER_SLOTS],
        "special":[],
        "crafted":[gear[k] for k in CRAFTED_SLOTS],
        "trinkets":[gear[k] for k in TRINKET_SLOTS]},
      "consumables":{
        "gem_budget_J":138,"flask_budget_F":165,
        "special_gem_id":240983,
        "flask":"flask_of_the_shattered_sun_2",
        "food":"harandar_celebration",
        "potion":"lights_potential_2",
        "weapon_temporary":None,
        "weapon_temporary_fixed_rating":{k:0 for k in scenario.STATS}},
      "combat":{"fight_style":"Patchwerk","targets":1,"duration_seconds":300,
         "vary_combat_length_pct":0.0,"raid_buffs":True,
         "bloodlust":"on_pull","external_buffs":[],"events":[]},
      "constraints":{
        "min_fraction":{k:0 for k in scenario.STATS},
        "max_fraction":{k:1 for k in scenario.STATS},
        "minimum_rating":{k:0 for k in scenario.STATS}},
      "runtime":{"scout_iterations":35,"confirm_iterations":320,
        "max_native_calls":4,"threads":1,"resume":True,"seed":1}}
    filler=[gear[k] for k in SLOTS if k not in
            set(TIER_SLOTS)|set(CRAFTED_SLOTS)|set(TRINKET_SLOTS)]
    scenario.normalize(scenario_doc)
    return reference,scenario_doc,filler,{"upstream_original_gear":original,
       "selected_representative_gear":ids,
       "single_head_replacement_external_source":HEAD_SOURCE,
       "original_apl_action_lines_preserved":len(before),
       "upstream_non_id_bonuses_replaced_with_explicit_fixture_options":True,
       "target_ilvl":334,"archetype":"mail_onehand_shield_orc_elemental"}

def run(upstream_file,out,binary=None,cache_only=False):
    out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
    report=out/"V078_RECEIPT.json"
    result={"schema":SCHEMA,"status":"BLOCKED_OR_PARTIAL",
      "native_attempts_total":0,"new_native_this_invocation":0,
      "new_native_cap":MAX_NATIVE,"no_effect_certification":True,
      "global_optimum_proven":False}
    try:
        source=pathlib.Path(upstream_file).read_text(encoding="utf8")
        reference,contract_doc,fillers,origin=spec_profile(source,out)
        inputs=first_use.paired_input(reference,out/"native",ITERATIONS,50)
        planned=first_use.prepare(contract_doc,fillers,
              static_cache.empty_cache(),reference,out/"native")
        need(planned["status"]=="BLOCKED_EXACT_NATIVE_STATIC_VARIANTS_MISSING",
             "FIRST_USE_STATIC_CACHE_NOT_EMPTY_UNEXPECTEDLY")
        result.update({"status":"PASS_NEW_CLASS_TWO_WITNESS_INPUT_PLAN_ONLY",
             "source_upstream_sha256":sha(source.encode("utf8")),
             "origin":origin,"character":contract_doc["character"],
             "scenario_profile_sha256":sha(reference.encode("utf8")),
             "first_use_readiness_before_native":planned["status"],
             "previous_native_static_unknown_is_not_zero":True,
             "witness_input_sha256":[i["input_sha256"] for i in inputs],
             "official_budget_formula":"T=G+J+F",
             "new_profile_numeric_offset_unknown_before_native":True})
        if binary is not None:
            binary=pathlib.Path(binary).resolve()
            need(binary.is_file() and sha(binary.read_bytes())==native_pin.BIN_SHA,
                 "SIMC_NATIVE_BINARY_SHA_CHANGED")
            seal=out/"V078_IDENTITY.json"
            identity={"schema":SCHEMA,
                      "upstream_sha256":sha(source.encode("utf8")),
                      "source_sha256":sha(reference.encode("utf8")),
                      "binary_sha256":native_pin.BIN_SHA,
                      "witness_input_sha256":result["witness_input_sha256"]}
            if seal.exists():
                need(load(seal)==identity,"RESUME_PROFILE_SOURCE_DRIFT")
            else:
                need(not any((out/"native"/("case_%02d"%i)/"result.json").exists()
                             for i in range(MAX_NATIVE)),
                     "UNSEALED_RESULT_PRESENT")
                durable.write_atomic(seal,identity)
            progress_path=out/"V078_PROGRESS.json"
            progress={"schema":SCHEMA,"witness_input_sha256":identity["witness_input_sha256"],
                  "native_attempts":0,"status":"READY"}
            if progress_path.exists():
                old=load(progress_path)
                need(old.get("schema")==progress["schema"] and
                     old.get("witness_input_sha256")==progress["witness_input_sha256"]
                     and type(old.get("native_attempts")) is int and
                     0<=old["native_attempts"]<=MAX_NATIVE,
                     "RESUME_ATTEMPT_LEDGER_DRIFT")
                progress["native_attempts"]=old["native_attempts"]
            else:
                durable.write_atomic(progress_path,progress)
            evidence=[]
            for i,case in enumerate(inputs):
                folder=out/"native"/("case_%02d"%i)
                folder.mkdir(parents=True,exist_ok=True)
                simc_input=folder/"input.simc"
                native_result=folder/"result.json"
                receipt_path=folder/"native_receipt.json"
                if simc_input.exists():
                    need(simc_input.read_bytes()==case["input"].encode("utf8"),
                         "CASE_INPUT_MODIFIED")
                else:
                    need(not native_result.exists() and not receipt_path.exists(),
                         "RESULT_WITHOUT_INPUT")
                    simc_input.write_text(case["input"],encoding="utf8")
                if native_result.exists() or receipt_path.exists():
                    need(native_result.is_file() and receipt_path.is_file(),
                         "PARTIAL_NATIVE_CASE_NOT_REUSED")
                    raw=native_result.read_bytes()
                    old=load(receipt_path)
                    need(old.get("input_sha256")==case["input_sha256"] and
                         old.get("json2_sha256")==sha(raw) and
                         old.get("simc_binary_sha256")==native_pin.BIN_SHA,
                         "CACHED_NATIVE_SHA_DRIFT")
                    new=False
                else:
                    need(not cache_only,"CACHE_ONLY_REFUSES_NEW_NATIVE")
                    need(progress["native_attempts"]<MAX_NATIVE,
                         "NATIVE_TWO_WITNESS_CAP_EXCEEDED")
                    progress["native_attempts"]+=1
                    progress["status"]="ATTEMPT_STARTED"
                    durable.write_atomic(progress_path,progress)
                    result["new_native_this_invocation"]+=1
                    process=subprocess.run([str(binary),str(simc_input.resolve())],
                         cwd=binary.parent,stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=240)
                    (folder/"stdout.txt").write_bytes(process.stdout)
                    (folder/"stderr.txt").write_bytes(process.stderr)
                    need(process.returncode==0,
                         "SIMC_NATIVE_EXIT_"+str(process.returncode)+
                         "_SEE_ORIGINAL_STDERR")
                    need(native_result.exists(),"SIMC_JSON2_NOT_CREATED")
                    raw=native_result.read_bytes()
                    old={"input_sha256":case["input_sha256"],"json2_sha256":sha(raw),
                         "simc_binary_sha256":native_pin.BIN_SHA}
                    durable.write_atomic(receipt_path,old)
                    new=True
                doc=json.loads(raw)
                observed=numeric.from_native(case["input"],doc)
                need(doc.get("report_version")=="2.0.0" and
                     len((doc.get("sim") or {}).get("players") or [])==1,
                     "FIRST_NEW_SPEC_JSON2_INVALID")
                player=doc["sim"]["players"][0]
                dps=(player.get("collected_data") or {}).get("dps") or {}
                need(type(dps.get("mean")) in (int,float) and
                     type(dps.get("mean_std_dev")) in (int,float) and
                     type(dps.get("count")) is int and dps["count"]>=20,
                     "NEW_SPEC_JSON2_DPS_SEM_ABSENT")
                evidence.append({"input":case["input"],"native":doc,
                    "raw_native_json":raw,
                    "input_sha256":case["input_sha256"],
                    "native_json_sha256":sha(raw)})
                result["completed_witnesses"]=len(evidence)
                result["status"]="PARTIAL_FIRST_NEW_SPEC_NATIVE"
                durable.write_atomic(report,result)
            cal=numeric.calibrate(evidence)
            local_cache=static_cache.empty_cache()
            for i,record in enumerate(evidence):
                raw=record["raw_native_json"]
                records=static_cache.native_records(raw,
                         artifact_id="V078_ELEMENTAL_NATIVE_%02d"%i)
                static_cache.merge_native(local_cache,records)
            stat=budgets.compile_static_budget(
                     scenario.normalize(contract_doc),fillers,local_cache)
            ready=first_use.prepare(contract_doc,fillers,local_cache,
                          reference,out/"native")
            result.update({"status":"PASS_TWO_ELEMENTAL_NATIVE_NUMERIC_WITNESSES",
               "new_profile_calibration":cal,
               "first_use_readiness_after_native":ready["status"],
               "full_static_G_if_native":stat["G_if_complete"],
               "full_official_T_if_native":stat["budget"]["T_official"],
               "missing_nontrinket_native_static":stat["missing_nontrinket_static"],
               "actual_native_witnesses":[{"input_sha256":e["input_sha256"],
                   "json2_sha256":e["native_json_sha256"],
                   "dps":e["native"]["sim"]["players"][0]["collected_data"]["dps"]["mean"],
                   "sem":e["native"]["sim"]["players"][0]["collected_data"]["dps"]["mean_std_dev"]}
                   for e in evidence],
               "native_attempts_total":progress["native_attempts"],
               "original_v015_v016_merged":False,
               "trinket_static_missing_never_assumed_zero":True})
            durable.write_atomic(out/"V078_STATIC_CACHE.json",local_cache)
            durable.write_atomic(out/"V078_SCENARIO.json",contract_doc)
            durable.write_atomic(out/"V078_FILLER.json",fillers)
            (out/"V078_REFERENCE.simc").write_text(reference,encoding="utf8")
            if ready["status"]=="READY_FOR_TWO_NATIVE_CALIBRATION_WITNESSES":
                # The two bootstrap witnesses are valid measured offset
                # data, but the generic v066 requires their absolute output
                # target to sum to official T. Probe-only raw sum is not
                # automatically an official bounded candidate.
                total=stat["budget"]["T_official"]
                observed_totals=[sum(numeric.read_rating(
                    x["native"]["sim"]["players"][0]).values()) for x in evidence]
                result["native_abs_rating_totals"]=observed_totals
                result["v066_official_witness_admissible"]=all(
                       x==total for x in observed_totals)
                if result["v066_official_witness_admissible"]:
                    # Reuse exact actual witnesses with the approved
                    # generic v066, NEVER manufacture a synthetic observation.
                    prepared=preflight.prepare(contract_doc,fillers,local_cache,
                             reference,evidence,native_pin.BIN_SHA)
                    result["v066_generic_preflight_status"]=prepared["summary"]["status"]
                else:
                    result["v066_generic_preflight_status"]=(
                       "NOT_YET_OFFICIAL_T_WITNESSES_REQUIRE_ADDITIONAL_BOUNDED_REAL_NATIVE")
            else:
                result["v066_generic_preflight_status"]="BLOCKED_MISSING_EXACT_STATIC"
            result["new_native_this_invocation"]=(
                 result["new_native_this_invocation"])
        else:
            result["not_run"]="TWO_PROPOSED_CASES_NO_NATIVE"
    except Exception as exc:
        result["status"]="BLOCKED_OR_PARTIAL"
        result["error"]=type(exc).__name__+":"+str(exc)
    durable.write_atomic(report,result)
    print("V078",result["status"],"new_native",
          result["new_native_this_invocation"],"error",result.get("error"),flush=True)
    return 0 if result["status"].startswith("PASS") else 3

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    p.add_argument("--binary",type=pathlib.Path)
    p.add_argument("--cache-only",action="store_true")
    a=p.parse_args(argv)
    return run(a.upstream,a.out,a.binary,a.cache_only)

if __name__=="__main__":
    sys.exit(main())
