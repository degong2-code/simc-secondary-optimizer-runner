#!/usr/bin/env python3
"""v186: four bounded corrected-weapon physical Native probes; NO optimizer.

Reuse v145 physical CLI/receipts with current-season v169->v098 source-first
profile. 26-wide static tests already passed; only four distinct weapon forms
are newly exercised. Every original SimC JSON2 and error stays in out/.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v145_targeted_pure_physical_native as physical
import v106_user_session_controller as sessions
import v169_source_first_representative_stage as stage

SCHEMA="v186_four_corrected_primary_weapon_physical_native_v1"
REV="7bc10711b5"
SHA="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"
# Distinct physical forms: strength dual-1H, agility dual daggers,
# agility dual maces, agility two-hand staff. Frost mage already v185 PASS.
CASES={
 "deathknight/frost":{"main_hand":(158373,"strength"),"off_hand":(251195,"strength")},
 "rogue/assassination":{"main_hand":(159136,"agility"),"off_hand":(193756,"agility")},
 "shaman/enhancement":{"main_hand":(159645,"agility"),"off_hand":(193767,"agility")},
 "druid/feral":{"main_hand":(251192,"agility")}
}
def need(v,why):
    if not v:raise RuntimeError("V186_"+why)
def persist(path,r):
    path.write_text(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf8")
def run(binary,out,*,execute=False):
    binary=pathlib.Path(binary).resolve()
    need(binary.is_file() and hashlib.sha256(binary.read_bytes()).hexdigest()==SHA,
         "SIMC_EXACT_SHA")
    out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    report={"schema":SCHEMA,"status":"STARTED","new_native_reserved":0,
            "new_native_confirmed":0,"cases":[],"max_total_native":4}
    p=out/"V186_FOUR_WEAPON_NATIVE_SUMMARY.json"
    persist(p,report)
    catalog=stage.build_all(stage.gear.read(),stage.load_tier())["specializations"]
    for key,hands in CASES.items():
        row={"spec":key,"status":"PREPARING","expected":hands}
        report["cases"].append(row);persist(p,report)
        try:
            need(set(catalog[key]["weapons"])==set(hands),"SLOT_FORM_MISMATCH")
            need(all(catalog[key]["weapons"][hand]==item_id
                     for hand,(item_id,_) in hands.items()),"SELECTED_ID_DRIFT")
            cl,spec=key.split("/")
            controls=sessions.standard_controls((cl,spec));controls["oil_hands"]=[]
            user=sessions.user_scenario(controls)
            prior=physical.run(user,binary,out,REV,iterations=35,
                               max_new=0,source_first_stage=True)
            need(prior["new_native_calls"]==0,"PREFLIGHT_CALLED_NATIVE")
            row["prefight"]=prior["status"]
            if execute:
                report["new_native_reserved"]+=1;persist(p,report)
                actual=physical.run(user,binary,out,REV,iterations=35,
                                    max_new=1,source_first_stage=True)
            else: actual=prior
            row.update({"status":actual["status"],"receipt":actual["receipt"],
                        "raw_log":actual["raw_log"],
                        "output_dir":actual["output_dir"],
                        "native_new":actual["new_native_calls"]})
            report["new_native_confirmed"]+=actual["new_native_calls"]
            if execute:
                need(actual["status"] in ("PASS_PHYSICAL_SIMC",
                                         "CACHED_VERIFIED_PHYSICAL_SIMC"),
                     "NATIVE_NOT_PASS_"+key)
                doc=json.loads((pathlib.Path(actual["output_dir"])/"physical.json").read_text())
                need(doc.get("report_version")=="2.0.0","JSON2_REPORT_VERSION")
                players=doc.get("sim",{}).get("players",[])
                need(len(players)==1,"JSON2_PLAYER_COUNT")
                items=players[0].get("gear",{})
                need(type(items) is dict,"GEAR_MISSING")
                row["gear"]={}
                for hand,(wanted,primary) in hands.items():
                    item=items.get(hand,{})
                    encoded=str(item.get("encoded_item",""))
                    need(",id="+str(wanted)+"," in encoded+",",
                         "JSON2_WEAPON_ID_"+key+"_"+hand)
                    need(item.get(primary,0)>0,"JSON2_PRIMARY_MISSING_"+key+"_"+hand)
                    for other in {"agility","strength","intellect"}-{primary}:
                        need(item.get(other,0)==0,"JSON2_WRONG_PRIMARY_"+key+"_"+hand)
                    row["gear"][hand]={"id":wanted,primary:item[primary]}
                row["json2_sha256"]=hashlib.sha256(
                     (pathlib.Path(actual["output_dir"])/"physical.json").read_bytes()).hexdigest()
                need(len([x for x in items if x in
                          ("head","shoulders","chest","hands","legs")])==5,
                     "TIER_ARMOR_SLOTS_MISSING")
                row["status"]="PASS_CORRECT_PRIMARY_PHYSICAL_NATIVE"
        except Exception as ex:
            row["status"]="BLOCKED_OR_NATIVE_FAILED"
            row["error"]=type(ex).__name__+":"+str(ex)
            row["traceback"]=traceback.format_exc(limit=4)
        persist(p,report)
    report["status"]=("PASS_FOUR_NEW_CORRECTED_PHYSICAL_NATIVE" if
        execute and report["new_native_confirmed"]==4 and
        all(x["status"]=="PASS_CORRECT_PRIMARY_PHYSICAL_NATIVE"
            for x in report["cases"]) else
        ("PREFLIGHT_ONLY" if not execute and
         all(x["status"] in ("PREPARED_NO_NATIVE","CACHED_VERIFIED_PHYSICAL_SIMC")
             for x in report["cases"]) else "FINISHED_WITH_BLOCKERS"))
    persist(p,report)
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--simc",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    try:
        result=run(a.simc,a.out,execute=a.execute)
        for row in result["cases"]:
            print("V186_SPEC",row["spec"],row["status"],
                  row.get("gear",""),row.get("error",""),flush=True)
        print("V186_FINAL",result["status"],
              "NEW_NATIVE",result["new_native_confirmed"],flush=True)
        return 0 if result["status"] in ("PREFLIGHT_ONLY",
                    "PASS_FOUR_NEW_CORRECTED_PHYSICAL_NATIVE") else 3
    except Exception as ex:
        print("V186_FATAL",str(ex),file=sys.stderr,flush=True)
        return 3
if __name__=="__main__":raise SystemExit(main())
