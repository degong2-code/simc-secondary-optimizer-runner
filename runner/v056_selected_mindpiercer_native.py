#!/usr/bin/env python3
"""v056: One limited actual SimC run with Mindpiercer's Sigil selected.

Only prove that selector passes its ID into an otherwise intact representative
profile and the pinned SimC accepts/executes that input. NEVER inspect effects,
proc uptimes or gear JSON2 static availability as an eligibility condition.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,subprocess,sys
import pilot
import v055_simc_item_selection as selector

BINARY_SHA="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"
def launch(binary,out):
    out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"v056_one_native_selection_acceptance_v1","status":"BLOCKED",
             "native_calls":0,"max_calls":1,
             "static_chmv_record_required":False,
             "simc_owns_all_effects":True,
             "product_code_integrated":False,"official_policy_promoted":False}
    try:
        if not binary.is_file() or hashlib.sha256(binary.read_bytes()).hexdigest()!=BINARY_SHA:
            raise ValueError("SIMC_BINARY_SHA_CHANGED")
        raw,proof=pilot.source()
        altered,plan=selector.apply_selection(raw,[
            {"slot":"trinket1","item_id":250224,"ilevel":334,"options":{}}])
        inp=out/"selected.simc"
        result=(out/"selected.json").resolve()
        lines=[]
        for line in altered.splitlines():
            if line.startswith("iterations="):line="iterations=1"
            elif line.startswith("max_time="):line="max_time=2"
            lines.append(line)
        lines.append("json2="+str(result))
        inp.write_text("\n".join(lines)+"\n",encoding="utf-8")
        receipt["input_sha256"]=hashlib.sha256(inp.read_bytes()).hexdigest()
        receipt["selected_item_id"]=250224
        receipt["selected_slot"]="trinket1"
        receipt["native_calls"]=1
        process=subprocess.run([str(binary),str(inp)],cwd=binary.parent,stdin=subprocess.DEVNULL,
                               capture_output=True,timeout=90)
        (out/"stdout.txt").write_bytes(process.stdout)
        (out/"stderr.txt").write_bytes(process.stderr)
        receipt["simc_exit_code"]=process.returncode
        if process.returncode!=0 or not result.is_file():
            raise ValueError("SIMC_EXECUTION_NOT_ACCEPTED")
        report=json.loads(result.read_text(encoding="utf8"))
        if report.get("report_version")!="2.0.0" or len(report.get("sim",{}).get("players",[]))!=1:
            raise ValueError("SIMC_JSON2_MISSING_PLAYER")
        receipt["native_json_sha256"]=hashlib.sha256(result.read_bytes()).hexdigest()
        receipt["json2_gear_trinket1_record_present"]="trinket1" in report["sim"]["players"][0].get("gear",{})
        receipt["json2_trinket_gear_record_is_not_a_selection_gate"]=True
        receipt["status"]="PASS_SIMC_EXECUTED_WITH_USER_SELECTED_250224_NO_EFFECT_GATE"
    except Exception as exc:
        receipt["error"]=type(exc).__name__+":"+str(exc)
    (out/"V056_RECEIPT.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("V056",receipt["status"],"native_calls",receipt["native_calls"],flush=True)
    return 0 if receipt["status"].startswith("PASS") else 3

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--binary",type=pathlib.Path,required=True)
    ap.add_argument("--out",type=pathlib.Path,required=True)
    a=ap.parse_args()
    sys.exit(launch(a.binary.resolve(),a.out.resolve()))
