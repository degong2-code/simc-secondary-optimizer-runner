#!/usr/bin/env python3
"""v182: bounded SIX one-shot physical SimC checks: 4 Omnium row4, 2 armor linings.
Existing v098 new-season profile generator and v140 physical serializer, no new solver.
"""
from __future__ import annotations
import hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v106_user_session_controller as sessions
import v098_target_user_scenario_bootstrap as bootstrap
import v140_pure_profile_physical_native_smoke as physical
import v145_targeted_pure_physical_native as report
REV="7bc10711b5"
SHA="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"
CASES=(("rune_crit","row4_crit",None),("rune_haste","row4_haste",None),
       ("rune_mastery","row4_mastery",None),("rune_vers","row4_vers",None),
       ("craft_arcanoweave",None,"arcanoweave_lining"),
       ("craft_sunfire",None,"sunfire_silk_lining"))
def main():
    binary=ROOT/".simc-cache/v035/simc"
    if not binary.is_file() or hashlib.sha256(binary.read_bytes()).hexdigest()!=SHA:
        raise RuntimeError("V182_PINNED_SIMC_MISSING_OR_SHA_MISMATCH")
    out=ROOT/"out"/"v182"
    out.mkdir(parents=True,exist_ok=True)
    results=[]
    for name,choice,lining in CASES:
        folder=out/name
        controls=sessions.standard_controls(("mage","frost"))
        controls["oil_hands"]=[]
        if choice:controls["consumable_choices"]["omnium_talents"]=choice
        if lining:controls["embellishments"]=[{"slot":"back","item_id":239656,
           "options":{"crafted_stats":"32/36","embellishment":lining}}]
        user=sessions.user_scenario(controls)
        row={"name":name,"status":"PREPARED","native_attempted":False}
        results.append(row)
        try:
            prepared=bootstrap.build(user,folder,binary,REV,current_season_product=True)
            assert prepared["native_calls"]==0
            native=folder/"physical.json"
            source=physical.physical_input((folder/"profile.simc").read_text("utf8"),native,35)
            simc_input=folder/"physical.simc"
            simc_input.write_text(source,encoding="utf8",newline="\n")
            with (folder/"simc_stdout.log").open("wb") as log:
                r=subprocess.run([str(binary),str(simc_input)],cwd=folder,
                                stdout=log,stderr=subprocess.STDOUT,timeout=180,check=False)
            row["native_attempted"]=True
            row["native_exit"]=r.returncode
            if r.returncode:raise RuntimeError("SIMC_NATIVE_EXIT_"+str(r.returncode))
            summary=report.summary_from_json2(native.read_bytes(),REV)
            row.update({"status":"PASS_ONE_REAL_SIMC","dps":summary["json2"]["dps_mean"],
                   "sha256":hashlib.sha256(native.read_bytes()).hexdigest(),
                   "scope":"physical profile acceptance only, NOT 95% optimizer or proc proof"})
        except Exception as ex:
            row["status"]="FAIL_REAL_SIMC_OR_PROFILE"
            row["error"]=type(ex).__name__+":"+str(ex)
            if folder.joinpath("simc_stdout.log").is_file():
                row["simc_error_tail"]=folder.joinpath("simc_stdout.log").read_text("utf8",errors="replace")[-2400:]
        finally:
            (out/"V182_OMNIUM_AND_CRAFT_NATIVE_SUMMARY.json").write_text(
                json.dumps({"cases":results,"passed":sum(r["status"]=="PASS_ONE_REAL_SIMC" for r in results),
                     "max_native":6,"no_global_optimality_claim":True},indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    for row in results:print("V182_PROBE",row["name"],row["status"],row.get("error",""),flush=True)
    return 0 if all(r["status"]=="PASS_ONE_REAL_SIMC" for r in results) else 3
if __name__=="__main__":raise SystemExit(main())
