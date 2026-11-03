#!/usr/bin/env python3
"""Bounded four-case SimC socket parser contrast; not game eligibility proof."""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re
import subprocess

STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")
GEM_ID=240906
SOCKET=re.compile(r"bonus_id=\{\s*(\d+)\s*\}.*socket=\{\s*1\s*\}")

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def require(ok,code):
    if not ok: raise RuntimeError("V270_"+code)

def bare_slot(lines,slot):
    matching=[i for i,line in enumerate(lines) if line.startswith(slot+"=")]
    require(len(matching)==1,"EXACT_ONE_"+slot)
    i=matching[0]
    tokens=lines[i].split(",")
    require(any(t.startswith("id=") for t in tokens),"ITEM_ID_REQUIRED")
    kept=[t for t in tokens if not t.startswith(
        ("bonus_id=","gem_id=","gem_bonus_id=","ilevel="))]
    return i,",".join(kept+["ilevel=334"])

def run(binary,profile,out,name):
    inp=out/(name+".simc")
    dst=out/(name+".json")
    log=out/(name+".log")
    raw=(profile.rstrip()+"\niterations=1\nthreads=1\n"
         "max_time=15\nvary_combat_length=0\n"
         "calculate_scale_factors=0\njson2="+str(dst)+"\n").encode("utf8")
    inp.write_bytes(raw)
    row={"case":name,"profile_sha256":digest(raw)}
    with log.open("wb") as writer:
        try:
            done=subprocess.run([str(binary),str(inp)],cwd=out,
                stdout=writer,stderr=subprocess.STDOUT,timeout=150)
        except subprocess.TimeoutExpired:
            return {**row,"status":"SIMC_TIMEOUT"}
    row["returncode"]=done.returncode
    row["native_json2_exists"]=dst.exists()
    if done.returncode!=0 or not dst.exists():
        return {**row,"status":"SIMC_REJECTED_OR_FAILED",
                "log_excerpt":log.read_text("utf8",errors="replace")[-1400:]}
    payload=dst.read_bytes()
    row["native_json2_sha256"]=digest(payload)
    try:
        doc=json.loads(payload)
        players=doc["sim"]["players"]
        require(len(players)==1,"SINGLE_PLAYER_REQUIRED")
        p=players[0]
        gear=p["gear"]
        rated=p["collected_data"]["buffed_stats"]["stats"]
        row.update(status="NATIVE_JSON2_OBSERVED",
            chest_encoded=gear["chest"]["encoded_item"],
            shoulders_encoded=gear["shoulders"]["encoded_item"],
            chest_json_keys=sorted(gear["chest"]),
            buffed_rating={k:rated.get(k) for k in STATS},
            native_revision=doc.get("git_revision"))
    except (ValueError,KeyError,TypeError,IndexError,RuntimeError) as exc:
        row.update(status="JSON2_UNEXPECTED",error=str(exc))
    return row

def main():
    parser=argparse.ArgumentParser()
    for k in ("binary","profile","revision","out"):
        parser.add_argument("--"+k,required=True)
    args=parser.parse_args()
    exe=pathlib.Path(args.binary).resolve()
    original=pathlib.Path(args.profile).read_text("utf8")
    out=pathlib.Path(args.out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    require(exe.is_file(),"EXACT_BINARY_REQUIRED")
    lines=original.splitlines()
    chestidx,chest=bare_slot(lines,"chest")
    shoulderidx,shoulders=bare_slot(lines,"shoulders")
    basis=list(lines)
    basis[chestidx]=chest
    basis[shoulderidx]=shoulders
    # Read the installed SimC binary's real DBC once; no guessed bonus ID.
    dump=subprocess.run([str(exe),"display_build=0","show_bonus_ids=1"],
        cwd=out,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
        timeout=120,check=False)
    require(dump.returncode==0,"SIMC_BONUS_DUMP_FAILED")
    found=[]
    for line in dump.stdout.decode("utf8",errors="replace").splitlines():
        m=SOCKET.search(line)
        if m:
            id=int(m.group(1))
            noise=sum(key in line for key in (
                "ilevel_adjust=","stats={","effects={",
                "recursive_bonus_ids=","crafting_quality="))
            found.append((noise,abs(14000-id),-id,id,line[:260]))
    require(found,"NO_SINGLE_SOCKET_BONUS_IN_SIMC_DBC")
    found.sort()
    bonus=found[0][3]
    def variant(name,slot=None,with_bonus=False):
        now=list(basis)
        if slot:
            idx,plain=(chestidx,chest) if slot=="chest" else (
                shoulderidx,shoulders)
            now[idx]=(plain+(f",bonus_id={bonus}" if with_bonus else "")
                      +f",gem_id={GEM_ID}")
        return run(exe,"\n".join(now),out,name)
    cases={}
    for name,slot,extra in (
        ("bare_chest_without_gem",None,False),
        ("chest_gem_without_socket","chest",False),
        ("chest_gem_with_socket_bonus","chest",True),
        ("shoulders_gem_with_socket_bonus","shoulders",True)):
        cases[name]=variant(name,slot,extra)
    reference=cases["bare_chest_without_gem"].get("buffed_rating")
    if reference:
        for case in cases.values():
            current=case.get("buffed_rating")
            if current:
                case["delta_rating_from_baseline"]={
                    k:round(current[k]-reference[k],4)
                    if isinstance(current[k],(int,float))
                    and isinstance(reference[k],(int,float)) else None
                    for k in STATS}
    receipt={
        "schema":"v270_one_pinned_simc_socket_parser_contrast_v1",
        "simc_binary_sha256":digest(exe.read_bytes()),
        "source_profile_sha256":digest(original.encode("utf8")),
        "source_revision_requested":args.revision,
        "gem_id":GEM_ID,"socket_bonus_id_from_native_dbc":bonus,
        "socket_bonus_raw_row":found[0][4],
        "one_socket_ids_found_in_native_dbc":len(found),
        "native_attempts":4,
        "show_bonus_ids_invocations":1,
        "game_equipment_upgrade_permission_not_proven":True,
        "cases":cases,
    }
    receiptpath=out/"V270_SOCKET_NATIVE_CONTRAST_RECEIPT.json"
    receiptpath.write_text(json.dumps(receipt,indent=2,sort_keys=True,
                                ensure_ascii=False)+"\n",encoding="utf8")
    print("V270_SOCKET_PROBE",json.dumps({
        "socket_bonus_id":bonus,
        "cases":{k:{"status":v.get("status"),
                    "delta":v.get("delta_rating_from_baseline"),
                    "returncode":v.get("returncode")}
            for k,v in cases.items()},
        "receipt":str(receiptpath)
    },ensure_ascii=False))
    require(reference is not None,"BASELINE_SIMC_NATIVE_FAILED")

if __name__=="__main__":
    main()
