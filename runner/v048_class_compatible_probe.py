#!/usr/bin/env python3
"""v048 small class-compatible Native static equipment diagnostics.

Eight 1-iteration trials MAX, no DPS optimization, no item recommendation.
Test only local item lookup in correct armor/weapon classes to explain
v047's uniform 14-level failures. Save stdout/stderr for accountability.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,subprocess,sys
import v046_static_item_cache as cache

EXPECTED_BIN="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"
TRIALS=[
    {"item_id":268229,"name":"plate_head_warrior","class":"warrior","spec":"arms","slot":"head"},
    {"item_id":281239,"name":"new_plate_head_warrior","class":"warrior","spec":"arms","slot":"head"},
    {"item_id":268219,"name":"leather_head_druid","class":"druid","spec":"balance","slot":"head"},
    {"item_id":268230,"name":"mail_head_hunter","class":"hunter","spec":"marksmanship","slot":"head"},
    {"item_id":268207,"name":"bow_hunter","class":"hunter","spec":"marksmanship","slot":"main_hand"},
    {"item_id":250224,"name":"trinket_warrior1","class":"warrior","spec":"arms","slot":"trinket1"},
    {"item_id":250244,"name":"trinket_warrior2","class":"warrior","spec":"arms","slot":"trinket1"},
    {"item_id":268229,"name":"plate_head_mage_control","class":"mage","spec":"arcane","slot":"head"}
]
def profile(t,output):
    parts=[
        t["class"]+'="V048Probe"',
        'spec='+t["spec"],'level=90','race=dwarf','role=attack',
        t["slot"]+'=v048_probe,id='+str(t["item_id"])+',ilevel=334,source=local',
        'item_db_source=local','fight_style=Patchwerk','iterations=1',
        'threads=1','fixed_time=1','max_time=2','vary_combat_length=0',
        'optimal_raid=0','calculate_scale_factors=0',
        'actions=wait,sec=1','json2='+str(output.resolve())
    ]
    return '\n'.join(parts)+'\n'
def run(binary,out):
    out.mkdir(parents=True,exist_ok=True)
    doc={"schema":"v048_cross_class_native_static_probe_v1",
         "status":"BLOCKED","cases":[],"native_calls_attempted":0,
         "maximum_native_calls":len(TRIALS),"product_code_integrated":False,
         "official_policy_promoted":False}
    try:
        if not binary.is_file() or hashlib.sha256(binary.read_bytes()).hexdigest()!=EXPECTED_BIN:
            raise ValueError("PINNED_BIN_CHANGED")
        for t in TRIALS:
            sub=out/t["name"];sub.mkdir(exist_ok=True)
            inp=sub/"input.simc";output=sub/"result.json"
            inp.write_text(profile(t,output),encoding='utf-8')
            doc["native_calls_attempted"]+=1
            step={"name":t["name"],"item_id":t["item_id"],
                  "class":t["class"],"slot":t["slot"],"status":"BLOCKED"}
            try:
                r=subprocess.run([str(binary),str(inp)],cwd=binary.parent,
                    stdin=subprocess.DEVNULL,capture_output=True,timeout=35)
                (sub/"stdout.txt").write_bytes(r.stdout[:16000])
                (sub/"stderr.txt").write_bytes(r.stderr[:16000])
                step["exit_code"]=r.returncode
                if r.returncode!=0 or not output.is_file():raise ValueError("NATIVE_PROCESS_FAILURE")
                records=cache.native_records(output.read_bytes(),artifact_id="V048_CROSS_CLASS_DIAGNOSTIC")
                chosen=[a for a in records if a["observed_slot"]==t["slot"] and
                        a["identity"]["item_id"]==t["item_id"]]
                if len(chosen)!=1:raise ValueError("EXPECTED_GEAR_ABSENT")
                step["secondary"]=chosen[0]["static"]["secondary"]
                step["itemlevel"]=chosen[0]["identity"]["ilevel"]
                step["status"]="PASS_NATIVE_STATIC_LOOKUP_ONLY"
            except Exception as exc:
                step["error"]=type(exc).__name__+":"+str(exc)
            doc["cases"].append(step)
            (out/"V048_PROGRESS.json").write_text(json.dumps(doc,indent=2)+"\n")
        doc["status"]="COMPLETED_WITH_CASE_RESULTS"
    except Exception as exc:
        doc["error"]=type(exc).__name__+":"+str(exc)
    (out/"V048_RECEIPT.json").write_text(json.dumps(doc,indent=2)+"\n")
    print("V048",doc["status"],"attempted",doc["native_calls_attempted"],
          "passed",sum(x["status"].startswith("PASS") for x in doc["cases"]))
    return 0 if doc["status"]=="COMPLETED_WITH_CASE_RESULTS" else 3

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--binary",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    a=p.parse_args()
    sys.exit(run(a.binary.resolve(),a.out.resolve()))
