#!/usr/bin/env python3
"""v069: actual Rogue numeric witnesses -> official G/J/F and fixed-L target.

Uses only actual JSON2 gear static records from the EXACT user-chosen scenario
(16 slots), never a generic Mage offset or an item/proc/APL reimplementation.
Rejects 'unknown' secondary numbers as unallocated, not zero.
A single (optional) Native official-budget candidate verifies FINAL rating
and DPS/SEM with current v064 evaluator; it is NOT an optimizer search.
"""
from __future__ import annotations
import argparse,hashlib,json,math,os,pathlib,subprocess,sys
import v046_static_item_cache as cache
import v055_simc_item_selection as selector
import v061_scenario_contract as contract
import v062_static_budget_bridge as budget
import v063_numeric_injection as numeric
import v064_adaptive_evaluator_port as port
import v065_v015_scheduler_adapter as scheduler
import v068_rogue_user_profile as rogue
import v068_rogue_two_native_probe as probe

SCHEMA="v069_actual_user_rogue_official_GJF_one_candidate_v1"
FIELDS=contract.STATS
TIER=frozenset(rogue.TIER)
SPECIAL=frozenset(rogue.SPECIAL)
CRAFTED=frozenset(rogue.CRAFTED)
TRINKETS=frozenset(rogue.TRINKETS)
class ReconcileBlocked(ValueError):pass
def need(x,reason):
    if not x:raise ReconcileBlocked(reason)
def parse_exact_input(text):
    parsed={}
    for line in text.splitlines():
        k,sep,v=line.partition("=")
        if sep and k in selector.SLOTS:
            need(k not in parsed,"DUPLICATE_SIMC_SLOT:"+k)
            _,opts=cache.parse_encoded(v)
            parsed[k]={"slot":k,"item_id":int(opts["id"]),
                 "ilevel":int(opts["ilevel"]),
                 "options":{key:value for key,value in opts.items()
                            if key not in ("id","ilevel","source")}}
    need(set(parsed)==selector.SLOTS,"ROGUE_INPUT_NOT_16_EQUIPMENT_SLOTS")
    return parsed
def prepare(witness_root,binary_sha):
    need(binary_sha==probe.BIN_SHA,"PINNED_NATIVE_BINARY_CHANGED")
    witnesses=[]
    cache_in=cache.empty_cache()
    for n in range(2):
        case=pathlib.Path(witness_root)/("case_%02d"%n)
        inputfile=case/"input.simc"
        nativefile=case/"result.json"
        raw=inputfile.read_bytes()
        payload=nativefile.read_bytes()
        reference=raw.decode("utf8")
        doc=json.loads(payload)
        player=(doc.get("sim") or {}).get("players") or []
        need(doc.get("report_version")=="2.0.0" and len(player)==1,
             "WITNESS_JSON2_INVALID")
        need(player[0].get("race")=="void_elf" and
             player[0].get("talents")==rogue.USER_TALENTS and
             player[0].get("specialization")=="Subtlety Rogue" and
             "spec=subtlety" in reference.splitlines(),
             "USER_SPEC_RACE_TALENT_NOT_NATIVE_MATCHED")
        statgear=player[0].get("gear") or {}
        need(set(statgear)==selector.SLOTS,"WITNESS_GEAR_MISSING_SLOTS")
        for slot,info in statgear.items():
            # A positive unknown in a crafted piece is NOT proven CHMV=0;
            # further exact Native variant resolution is required.
            need(info.get("unknown",0)==0,
                 "NATIVE_STATIC_UNALLOCATED_UNKNOWN:"+slot+
                 "="+str(info.get("unknown")))
        rows=cache.native_records(payload,artifact_id="V069_ROGUE_ACTUAL_NATIVE")
        cache.merge_native(cache_in,rows)
        witnesses.append({"input":reference,"native":doc,"raw_native_json":payload,
                          "input_sha256":hashlib.sha256(raw).hexdigest(),
                          "result_sha256":hashlib.sha256(payload).hexdigest()})
    calibration=numeric.calibrate(witnesses)
    need(calibration["native_revision"]=="7bc10711b5",
         "PINNED_REAL_SIMC_REVISION_CHANGED")
    reference=witnesses[0]["input"]
    entities=parse_exact_input(reference)
    for group,ids in ((TIER,rogue.TIER),(SPECIAL,rogue.SPECIAL),
                      (TRINKETS,rogue.TRINKETS)):
        for slot in group:
            need(entities[slot]["item_id"]==ids[slot],"SELECTED_USER_ITEM_DRIFT:"+slot)
    for slot in CRAFTED:
        need(entities[slot]["item_id"]==rogue.CRAFTED[slot][0] and
             entities[slot]["options"]["embellishment"]==rogue.CRAFTED[slot][1],
             "CRAFTED_EFFECT_OR_ID_CHANGED:"+slot)
    need(sum(1 for slot,row in entities.items()
              if "embellishment" in row["options"])==2,
         "USER_TWO_EMBELLISHMENTS_MISSING")
    parsed={}
    for l in reference.splitlines():
        if "=" in l and not l.startswith("#"):
            k,v=l.split("=",1);parsed[k]=v
    need(parsed.get("omnium_talents","").split("/")[-2]==rogue.OMNIUM_FOURTH,
         "USER_OMNIUM_MASTERY_NOT_SERVED")
    need(parsed.get("temporary_enchant")==rogue.EXISTING_DEFAULTS[
           "temporary_enchant"],"TWO_WEAPON_TEMPS_NOT_PRESERVED")
    normalized=contract.normalize({
      "schema":contract.SCHEMA,
      "character":{"class":"rogue","spec":"subtlety","race":"void_elf",
                   "talents":rogue.USER_TALENTS,"role":"attack"},
      "source":{"kind":"user_supplied","profile_sha256":hashlib.sha256(
                 reference.encode("utf8")).hexdigest()},
      "target":{"mode":"derived_ilevel","ilevel":334,
                "manual_total":None,"manual_total_scope":None},
      "equipment":{"tier":[entities[s] for s in sorted(TIER)],
                   "special":[entities[s] for s in sorted(SPECIAL)],
                   "crafted":[entities[s] for s in sorted(CRAFTED)],
                   "trinkets":[entities[s] for s in sorted(TRINKETS)]},
      "consumables":{"gem_budget_J":138,"flask_budget_F":165,
            "special_gem_id":rogue.SPECIAL_GEM_B,
            "flask":rogue.EXISTING_DEFAULTS["flask"],
            "food":rogue.EXISTING_DEFAULTS["food"],
            "potion":rogue.EXISTING_DEFAULTS["potion"],
            "weapon_temporary":"thalassian_phoenix_oil_2",
            "weapon_temporary_fixed_rating":{k:0 for k in FIELDS}},
      "combat":{"fight_style":"Patchwerk","targets":1,"duration_seconds":300,
           "vary_combat_length_pct":0,"raid_buffs":True,
           "bloodlust":"simc_default","external_buffs":[],"events":[]},
      "constraints":{"min_fraction":{k:0. for k in FIELDS},
                     "max_fraction":{k:0.5 for k in FIELDS},
                     "minimum_rating":{k:0 for k in FIELDS}},
      "runtime":{"scout_iterations":35,"confirm_iterations":120,
                 "max_native_calls":4,"threads":1,
                 "resume":True,"seed":None}})
    filler=[row for slot,row in entities.items() if
            slot not in TIER|SPECIAL|CRAFTED|TRINKETS]
    built=budget.compile_static_budget(normalized,filler,cache_in)
    need(not built["missing_nontrinket_static"] and
         not built["missing_special_fixed_static"] and
         built["G_if_complete"] is not None,"NATIVE_EXACT_G_INCOMPLETE")
    need(built["budget"]["official_formula"]=="T=G+J+F" and
         built["budget"]["oil_stays_OUTSIDE_T"] is True,
         "OFFICIAL_BUDGET_POLICY_DRIFT")
    total=built["budget"]["T_official"]
    lower=built["effective_floor_if_possible"]
    need(total==built["G_if_complete"]+138+165,"T_GJF_MISMATCH")
    need(sum(lower.values())<=total,"FLOOR_EXCEEDS_OFFICIAL_TOTAL")
    # Balanced initial official rating, not a searched optimum.
    vals=dict(lower)
    remaining=total-sum(vals.values())
    each,remainder=divmod(remaining,4)
    for i,k in enumerate(FIELDS):vals[k]+=each+int(i<remainder)
    need(sum(vals.values())==total,"INITIAL_T_ALLOCATION")
    # Enforce 50% upper caps without altering policy; fall back to a
    # simple capacity-constrained integer distributor if necessary.
    maxes={k:int(math.floor(total*0.5+1e-9)) for k in FIELDS}
    overflow=0
    for k in FIELDS:
        if vals[k]>maxes[k]:
            overflow+=vals[k]-maxes[k];vals[k]=maxes[k]
    for k in FIELDS:
        take=min(overflow,maxes[k]-vals[k])
        vals[k]+=take;overflow-=take
    need(overflow==0,"OFFICIAL_T_CAP_UNFEASIBLE")
    numeric.check_target(normalized,built,vals)
    return {"normalized":normalized,"budget":built,"calibration":calibration,
            "reference":reference,"witnesses":witnesses,
            "initial_target":vals,"native_static_cache":cache_in}
def one_candidate(prepared,out,binary=None,cache_only=False):
    out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
    bundle=prepared
    report={"schema":SCHEMA,"status":"BLOCKED","new_native_calls":0,
       "official_policy":"T=G+J+F","global_optimum_proven":False,
       "source_v015_v016_original_tests_not_rerun":True,
       "independent_proc_gate":False}
    path=out/"V069_RECEIPT.json"
    try:
        budgeted=bundle["budget"]
        target=bundle["initial_target"]
        report.update({"status":"OFFICIAL_TARGET_READY_NO_NATIVE_YET",
          "G":budgeted["G_if_complete"],
          "J":budgeted["budget"]["J"],"F":budgeted["budget"]["F"],
          "T_official":budgeted["budget"]["T_official"],
          "fixed_special_L":budgeted["locked_L_when_all_specials_observed"],
          "user_exact_two_embellishments":True,
          "gear_rows_gem_enchant_attribution_flagged":
               len(budgeted["budget"]["ambiguous_gem_enchant_gear_rows"]),
          "native_json2_numeric_offset":bundle["calibration"][
             "net_input_to_json2_rating_offset"],
          "external_oil_not_added_to_T":True,
          "external_oil_numeric_rating_unattributed":True,
          "candidate_target":target})
        request=port.make_request(bundle["normalized"],budgeted,
             bundle["calibration"],bundle["reference"],probe.BIN_SHA,target,35,
             out/"result.json")
        (out/"input.simc").write_text(request["input"],encoding="utf8")
        report["candidate_case_key"]=request["case_key"]
        if binary is None:
            report["status"]="PASS_OFFICIAL_TARGET_PLANNED_ZERO_NATIVE"
        else:
            binary=pathlib.Path(binary)
            need(binary.is_file() and hashlib.sha256(binary.read_bytes()).hexdigest()==probe.BIN_SHA,
                 "PINNED_NATIVE_BINARY_HASH_CHANGED")
            if (out/"result.json").exists():
                need(cache_only,"EXISTING_NATIVE_UNATTESTED_USE_CACHE_ONLY")
                data=(out/"result.json").read_bytes()
                # No blind "cache ok"; numerical validation runs below.
                doc=json.loads(data)
            else:
                need(not cache_only,"CACHE_ONLY_WITH_NO_NATIVE_RESULT")
                report["new_native_calls"]=1
                probe.write(path,report)
                p=subprocess.run([str(binary.resolve()),str((out/"input.simc").resolve())],
                    cwd=binary.resolve().parent,stdin=subprocess.DEVNULL,
                    capture_output=True,timeout=240)
                (out/"stdout.txt").write_bytes(p.stdout)
                (out/"stderr.txt").write_bytes(p.stderr)
                need(p.returncode==0,"SIMC_NATIVE_RETURN_"+str(p.returncode)+
                     "_SEE_STDERR_UNMODIFIED")
                need((out/"result.json").is_file(),
                     "NATIVE_JSON2_FILE_NOT_CREATED")
                data=(out/"result.json").read_bytes();doc=json.loads(data)
            observed=port.ingest_native(request,doc,bundle["calibration"],data)
            report["result"]={k:observed[k] for k in ("status","target","rating_actual",
                                        "dps_mean","dps_sem","dps_samples",
                                        "native_json_sha256")}
            report["status"]="PASS_ONE_ROGUE_OFFICIAL_T_NATIVE_DPS_RATING" 
    except Exception as exc:
        report["status"]="BLOCKED_OR_PARTIAL"
        report["error"]=type(exc).__name__+":"+str(exc)
    probe.write(path,report)
    return 0 if report["status"].startswith("PASS") else 3
def main(argv=None):
    cli=argparse.ArgumentParser()
    cli.add_argument("--witness-root",required=True,type=pathlib.Path)
    cli.add_argument("--out",required=True,type=pathlib.Path)
    cli.add_argument("--binary",type=pathlib.Path)
    cli.add_argument("--cache-only",action="store_true")
    a=cli.parse_args(argv)
    a.out.mkdir(parents=True,exist_ok=True)
    try:
        ctx=prepare(a.witness_root,probe.BIN_SHA)
    except Exception as e:
        report={"schema":SCHEMA,"status":"BLOCKED_STATIC_OR_WITNESS",
          "new_native_calls":0,
          "error":type(e).__name__+":"+str(e)}
        probe.write(a.out/"V069_RECEIPT.json",report)
        print("V069",report["status"],report["error"])
        return 3
    status=one_candidate(ctx,a.out,a.binary,a.cache_only)
    r=json.loads((a.out/"V069_RECEIPT.json").read_text())
    print("V069",r["status"],"new_native",r["new_native_calls"])
    return status
if __name__=="__main__":
    sys.exit(main())
