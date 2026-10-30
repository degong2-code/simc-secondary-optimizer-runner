#!/usr/bin/env python3
"""v198: bounded, on-demand two-input Native enchant static-rating comparison.

Reads an EXISTING v098/v106 stage/profile.simc with representative equipment.
No new character/item DB queries, no optimization, no baseline mutation.
Exactly one gear slot's enchant differs; v140 removes gear_* overrides to
observe SimC's physical gear. Two CLI Native JSON2 calls max, cached by
source profile+SimC binary+enchant identity; previously created bytes sealed.
This is *not* proc/effect-certification or a new engine.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,re,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"integration_probes"),str(ROOT/"runner")]
import v140_pure_profile_physical_native_smoke as physical

SCHEMA="v198_native_two_profile_enchant_rating_v1"
STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")
ALLOWED={"finger1","finger2","head","shoulders","chest","feet"}
class ProbeBlocked(ValueError):pass
def need(ok,code):
    if not ok:raise ProbeBlocked(code)
def sha(data):return hashlib.sha256(data).hexdigest()
def file_sha(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),
                                  ensure_ascii=False).encode("utf8")
def put_once(path,raw):
    path=pathlib.Path(path)
    if path.is_file():
        need(path.read_bytes()==raw,"EXISTING_NATIVE_PROOF_INPUT_DRIFT")
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(raw)
def swap_slot_enchant(source,slot,enchant_id):
    """Two profiles differ in one enchant_id field and nothing else."""
    need(slot in ALLOWED,"PROBE_SLOT_NOT_APPROVED")
    need(type(enchant_id) is int and 1<=enchant_id<=999999,
         "ENCHANT_ID_INVALID")
    lines=source.splitlines()
    index=[i for i,line in enumerate(lines) if line.startswith(slot+"=")]
    need(len(index)==1,"EXACT_ONE_GEAR_SLOT_REQUIRED")
    original=lines[index[0]]
    need("source=local" in original and ",id=" in original,
         "PHYSICAL_SIMC_GEAR_ROW_REQUIRED")
    parts=[x for x in original.split(",") if not
           x.startswith(("enchant=","enchant_id="))]
    # Exact bare vs selected enchant input; other options order unmodified.
    bare=list(lines);bare[index[0]]=",".join(parts)
    applied=list(lines);applied[index[0]]=",".join(parts+[f"enchant_id={enchant_id}"])
    need(sum(a!=b for a,b in zip(bare,applied))==1,"ONLY_ONE_ITEM_ROW_MAY_CHANGE")
    return "\n".join(bare)+"\n","\n".join(applied)+"\n"

def parse_native(raw,revision,slot):
    obj=json.loads(raw)
    need(obj.get("report_version")=="2.0.0" and
         str(obj.get("git_revision","")).startswith(revision[:7]),
         "SIMC_JSON2_REVISION_OR_REPORT_INVALID")
    players=(obj.get("sim") or {}).get("players") or []
    need(len(players)==1,"SIMC_SINGLE_PLAYER_REQUIRED")
    gear=players[0].get("gear") or {}
    need(slot in gear,"SIMC_GEAR_SLOT_MISSING")
    stats={s:gear[slot].get(s,0) for s in STATS}
    need(all(type(v) in (int,float) and v>=0 and float(v).is_integer()
             for v in stats.values()),
         "SIMC_GEAR_SLOT_STATIC_RATING_NOT_INTEGER")
    # Permanent enchants may NOT be item-local JSON2 gear[slot] fields.
    # The actual precombat character total in collected_data.buffed_stats
    # includes the enchant: v199 Native 8025 observed haste 1004 -> 1034
    # although gear.finger1.haste_rating stayed unchanged.
    rated=((players[0].get("collected_data") or {}).get("buffed_stats") or
           {}).get("stats") or {}
    need(all(k in rated and type(rated[k]) in (int,float) and
             float(rated[k]).is_integer() and rated[k]>=0 for k in STATS),
         "SIMC_CHARACTER_BUFFED_RATING_MISSING")
    return {"gear":gear,
            "slot_stats":{k:int(v) for k,v in stats.items()},
            "character_stats":{k:int(rated[k]) for k in STATS},
            "encoded_item":gear[slot].get("encoded_item",""),
            "simc_revision":obj["git_revision"]}

def compare_native(before,after,slot,enchant_id,revision):
    p=parse_native(before,revision,slot);q=parse_native(after,revision,slot)
    need(f"enchant_id={enchant_id}" in q["encoded_item"],
         "TARGET_ENCHANT_NOT_OBSERVED_IN_JSON2")
    # Non-target items must remain exactly equal; only selected one changed.
    for k in p["gear"]:
        if k!=slot:
            need(p["gear"][k]==q["gear"].get(k),
                 "OTHER_NATIVE_GEAR_CHANGED:"+k)
    need(set(p["gear"])==set(q["gear"]),"GEAR_SLOT_SET_CHANGED")
    for k in ("id","ilevel"):
        pat=re.compile(r"(?:^|,)"+k+r"=([^,]+)")
        x=pat.search(p["encoded_item"]);y=pat.search(q["encoded_item"])
        need(x is not None and y is not None and x.group(1)==y.group(1),
             "BASE_ITEM_ID_OR_ILVL_CHANGED")
    delta={k:q["character_stats"][k]-p["character_stats"][k]
           for k in STATS}
    gear_delta={k:q["slot_stats"][k]-p["slot_stats"][k] for k in STATS}
    need(all(v>=0 for v in delta.values()),
         "ENCHANT_NEGATIVE_CHARACTER_RATING_DELTA")
    need(all(v>=0 for v in gear_delta.values()),
         "ENCHANT_NEGATIVE_GEAR_SLOT_RATING_DELTA")
    return {"enchant_id":enchant_id,"slot":slot,"static_secondary":delta,
            "observed_character_rating_before":p["character_stats"],
            "observed_character_rating_after":q["character_stats"],
            "observed_item_slot_rating_delta":gear_delta,
            "rating_source":"sim.players[0].collected_data.buffed_stats.stats",
            "classification":"POSITIVE_PRECOMBAT_SECONDARY_RATING_OBSERVED"
                if sum(delta.values())>0 else
                "NO_PRECOMBAT_SECONDARY_RATING_DELTA_OBSERVED",
            "source_revision":q["simc_revision"]}

def run(profile,binary,revision,slot,enchant_id,out,*,iterations=35,max_new=2,
        timeout=180):
    need(type(iterations) is int and 1<=iterations<=35,"ITERATIONS_BOUNDED")
    need(type(max_new) is int and max_new in (0,1,2),"MAX_NEW_0_1_2")
    need(type(timeout) is int and 30<=timeout<=900,"NATIVE_TIMEOUT_BOUNDED")
    need(type(revision) is str and re.fullmatch("[a-f0-9]{7,40}",revision),
         "SIMC_REVISION_HEX_REQUIRED")
    source=pathlib.Path(profile).resolve().read_text("utf8")
    exe=pathlib.Path(binary).resolve()
    need(exe.is_file(),"SIMC_EXE_MISSING")
    need(not any(x.startswith("import=") for x in source.splitlines()),
         "IMPORTED_CURRENT_EQUIPMENT_PROFILE_REFUSED")
    plain,enchanted=swap_slot_enchant(source,slot,enchant_id)
    identity={"base_sha256":sha(source.encode("utf8")),
              "simc_bin_sha256":file_sha(exe),
              "revision":revision,"slot":slot,"enchant_id":enchant_id,
              "iterations":iterations}
    folder=pathlib.Path(out).resolve()/sha(canonical(identity))[:24]
    folder.mkdir(parents=True,exist_ok=True)
    for name,variant in (("before",plain),("after",enchanted)):
        inp=physical.physical_input(variant,folder/(name+".json"),iterations)
        put_once(folder/(name+".simc"),inp.encode("utf8"))
    calls=0
    for name in ("before","after"):
        target=folder/(name+".json")
        if target.is_file():continue
        need(calls<max_new,"NATIVE_CALL_CAP_REACHED")
        # Append instead of truncating previous failure diagnostics on retry.
        with (folder/(name+".log")).open("ab") as log:
            log.write(b"\n=== V198 NEW EXACT-SAME-IDENTITY NATIVE ATTEMPT ===\n")
            try:
                r=subprocess.run([str(exe),str(folder/(name+".simc"))],
                       cwd=folder,stdout=log,stderr=subprocess.STDOUT,
                       timeout=timeout,check=False)
            except subprocess.TimeoutExpired as exc:
                raise ProbeBlocked("SIMC_TIMEOUT:"+name) from exc
        need(r.returncode==0 and target.is_file(),
             "SIMC_NATIVE_FAILED:"+name)
        calls+=1
    b=(folder/"before.json").read_bytes()
    a=(folder/"after.json").read_bytes()
    diff=compare_native(b,a,slot,enchant_id,revision)
    proof={
        "schema":SCHEMA,"identity":identity,
        "status":"NATIVE_TWO_INPUT_COMPARISON_COMPLETED",
        "native_new_calls":calls,"max_native_calls":2,
        "source_profile_unchanged":True,
        "base_input_sha256":sha((folder/"before.simc").read_bytes()),
        "enchant_input_sha256":sha((folder/"after.simc").read_bytes()),
        "before_native_sha256":sha(b),"after_native_sha256":sha(a),
        "comparison":diff,
        "budget_E_input_allowed_automatically":False,
        "reason":"MATCHED_NATIVE_RATING_DELTA_REQUIRES_COMPANION_RECEIPT_REVIEW"}
    receipt=folder/"receipt.json"
    if receipt.is_file():
        sealed=json.loads(receipt.read_text("utf8"))
        same={k:v for k,v in proof.items() if k!="native_new_calls"}
        prior={k:v for k,v in sealed.items() if k!="native_new_calls"}
        need(prior==same,"IMMUTABLE_NATIVE_COMPARISON_RECEIPT_CHANGED")
    else:
        put_once(receipt,canonical(proof)+b"\n")
        sealed=proof
    print(json.dumps({"status":proof["status"],"new_native_this_request":calls,
                      "E":diff["static_secondary"],"folder":str(folder)},
                     ensure_ascii=False))
    return {**sealed,"native_new_calls_this_request":calls}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("profile","binary","revision","slot","out"):
        p.add_argument("--"+key,required=True)
    p.add_argument("--enchant-id",required=True,type=int)
    p.add_argument("--iterations",type=int,default=35)
    p.add_argument("--max-new",type=int,default=2)
    a=p.parse_args()
    try:
        run(a.profile,a.binary,a.revision,a.slot,a.enchant_id,a.out,
            iterations=a.iterations,max_new=a.max_new)
    except (ProbeBlocked,OSError,ValueError,KeyError) as exc:
        print("V198_BLOCKED",str(exc),file=sys.stderr)
        return 3
    return 0
if __name__=="__main__":raise SystemExit(main())
