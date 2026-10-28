#!/usr/bin/env python3
"""v106 Windows user-session controller around existing v098 -> v096 -> v094.

No optimizer, native parser, item database or new SimC mechanics. User inputs
only. Session identity is tied to canonical user controls, actual binary SHA,
revision and optional exact static-cache bytes. The SAME key resumes cached
Native calls; changed settings always create a different session.
"""
from __future__ import annotations
import argparse, contextlib, hashlib, json, os, pathlib, re, sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import v098_target_user_scenario_bootstrap as bootstrap
import v108_native_consumable_inputs as consumer

SCHEMA="v106_dps_user_session_v1"
DEFAULT_ROOT=pathlib.Path.home()/"SIMC_Secondary_Optimizer"/"runs"
SUPPORTED=tuple(sorted(bootstrap.ARCHETYPES))
# Extended UI selected equipment is a pass-through to v098's exact
# source-backed item/tier/native-L checks, not a second selector.
OPTIONAL_CONTROLS=frozenset(("special_items","embellishments",
                             "consumable_choices"))
DUAL_FORMS=frozenset(("dual_two_hand","dual_one_hand"))

class SessionBlocked(ValueError):pass
def need(ok,why):
    if not ok:raise SessionBlocked("V106_"+why)
def canonical(obj):
    return json.dumps(obj,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False)
def sha(data):
    return hashlib.sha256(data).hexdigest()
def source_defaults(key):
    need(key in bootstrap.ARCHETYPES,"DPS_ARCHETYPE_NOT_READY")
    name,_,weapon,_=bootstrap.ARCHETYPES[key]
    text=(bootstrap.FIXTURES/name).read_text(encoding="utf8")
    fields={}
    for line in text.splitlines():
        field,sep,val=line.partition("=")
        if sep and field in ("spec","race","talents"):
            need(field not in fields,"SOURCE_DUPLICATE_CHARACTER_FIELD")
            fields[field]=val
    need(set(fields)=={"spec","race","talents"} and fields["spec"]==key[1],
         "SOURCE_CHARACTER_NOT_READY")
    trinkets=[]
    for slot in ("trinket1","trinket2"):
        found=[x for x in text.splitlines() if x.startswith(slot+"=")]
        need(len(found)==1,"SOURCE_TRINKET_NOT_UNIQUE:"+slot)
        m=re.search(r"(?:^|,)id=([1-9][0-9]*)(?:,|$)",found[0])
        need(m is not None,"SOURCE_TRINKET_ID_MISSING:"+slot)
        trinkets.append(int(m.group(1)))
    return {"class":key[0],"spec":key[1],"race":fields["race"],
            "talents":fields["talents"],"trinket_ids":trinkets,
            "weapon_form":weapon,"oil_hands":["main_hand","off_hand"]
             if weapon in DUAL_FORMS else ["main_hand"]}

def validated_selected_gear(entries,group,limit):
    """Validate only user input shape. v098 + SimC own identity and effects."""
    need(type(entries) is list and len(entries)<=limit,
         "SELECTED_GEAR_COUNT_OR_TYPE")
    out=[]
    for item in entries:
        need(type(item) is dict and
             set(item)=={"slot","item_id","options"},
             "SELECTED_GEAR_FIELDS")
        slot=item["slot"]
        need(type(slot) is str and slot in bootstrap.item_mod.SLOTS and
             slot not in ("trinket1","trinket2"),
             "SELECTED_GEAR_NONTRINKET_SLOT_REQUIRED")
        bootstrap.item_mod.checked_id(item["item_id"])
        options=bootstrap.item_mod.checked_options(item["options"])
        if group=="special":
            need(not(set(options)&{"embellishment","crafted_stats"}),
                 "SPECIAL_CANNOT_BE_CRAFTED")
        else:
            need("embellishment" in options and
                 "redirected_base_stats" not in options,
                 "CRAFTED_NEEDS_EMBELLISHMENT_NOT_CATALYST")
        out.append({"slot":slot,"item_id":item["item_id"],
                    "options":options})
    need(len({v["slot"] for v in out})==len(out),
         "DUPLICATE_SELECTED_GEAR_SLOT")
    return out

def selected_rows_from_form(special_rows,crafted_rows):
    """Thin form-data serializer: only ID/slot/SimC-native option tokens.

    Empty rows are ignored. Partial rows fail before any Native request.
    Original item effects and crafted stat mechanics stay in SimC, not here.
    """
    need(type(special_rows) is list and len(special_rows)<=2
         and type(crafted_rows) is list and len(crafted_rows)<=2,
         "ADVANCED_FORM_MAX_TWO_ROWS_PER_GROUP")
    converted={}
    layouts=(
        ("special_items",special_rows,("bonus_id","redirected_base_stats")),
        ("embellishments",crafted_rows,
         ("crafted_stats","embellishment","bonus_id")))
    for group,rows,option_keys in layouts:
        result=[]
        for raw in rows:
            need(type(raw) is dict
                 and set(raw)=={"slot","item_id"}|set(option_keys),
                 "ADVANCED_FORM_FIELDS")
            text={k:str(v).strip() for k,v in raw.items()}
            if not any(text.values()):continue
            need(text["slot"] and text["item_id"] and
                 text["item_id"].isdigit(),
                 "ADVANCED_FORM_SLOT_AND_ITEM_REQUIRED")
            result.append({
                "slot":text["slot"],"item_id":int(text["item_id"]),
                "options":{k:text[k] for k in option_keys if text[k]}})
        converted[group]=result
    return converted

def user_scenario(controls):
    """Only approved v098 user fields; do not expose manifest/filler/seed."""
    required={"class","spec","race","talents","ilevel","final_T",
              "trinket_ids","oil_hands","targets","duration_seconds",
              "raid_buffs"}
    need(type(controls) is dict and
         required<=set(controls)<=required|OPTIONAL_CONTROLS,
         "USER_INPUT_FIELDS")
    key=(controls["class"],controls["spec"])
    need(key in bootstrap.ARCHETYPES,"DPS_ARCHETYPE_NOT_READY")
    for x in ("race","talents"):
        bootstrap.scenario.text_token(controls[x],"USER_"+x.upper())
    ilvl=controls["ilevel"];final=controls["final_T"]
    need(type(ilvl) is int and 266<=ilvl<=344,"ILVL_OUT_OF_REFERENCE")
    need(final is None or type(final) is int and 1<=final<=100000,
         "USER_FINAL_T_INVALID")
    trinkets=controls["trinket_ids"]
    need(type(trinkets) is list and len(trinkets)==2
         and all(type(i) is int and i>0 for i in trinkets),
         "TWO_REAL_TRINKET_IDS_REQUIRED")
    weapons=bootstrap.ARCHETYPES[key][2]
    hands=controls["oil_hands"]
    need(type(hands) is list and len(hands)==len(set(hands))
         and set(hands)<={"main_hand","off_hand"} and
         (weapons in DUAL_FORMS or "off_hand" not in hands),
         "OIL_HANDS_INCOMPATIBLE_WITH_SOURCE_WEAPON_FORM")
    targets=controls["targets"];duration=controls["duration_seconds"]
    need(type(targets) is int and 1<=targets<=40 and
         type(duration) is int and 1<=duration<=3600 and
         type(controls["raid_buffs"]) is bool,
         "COMBAT_USER_SETTING_INVALID")
    specials=validated_selected_gear(
        controls.get("special_items",[]),"special",8)
    crafted=validated_selected_gear(
        controls.get("embellishments",[]),"crafted",2)
    choice=controls.get("consumable_choices")
    if choice is not None:
        need(type(choice) is dict and
             set(choice)==consumer.CHOICE_FIELDS,
             "CONSUMABLE_CHOICES_FIELDS")
        need(all(type(choice[k]) is str for k in
                 ("flask","food","potion","augmentation")) and
             type(choice["diamond_id"]) is int and
             type(choice["omnium_talents"]) is str,
             "CONSUMABLE_CHOICES_TYPES")
    occupied=[r["slot"] for r in specials+crafted]
    need(len(occupied)==len(set(occupied)),
         "SELECTED_SPECIAL_AND_CRAFTED_SLOT_CONFLICT")
    output={"schema":bootstrap.SCHEMA,
            "character":{k:controls[k] for k in
                         ("class","spec","race","talents")},
            "target":{"ilevel":ilvl,"final_T":final},
            "trinkets":[{"slot":slot,"item_id":id_,"options":{}}
                for slot,id_ in zip(("trinket1","trinket2"),trinkets)],
            "special_items":specials,"embellishments":crafted,
            "oil_hands":list(hands),
            "combat":{"targets":targets,"duration_seconds":duration,
                      "raid_buffs":controls["raid_buffs"]}}
    if choice is not None:output["consumable_choices"]=dict(choice)
    return output

def standard_controls(key=("paladin","retribution")):
    d=source_defaults(key)
    return {k:v for k,v in d.items()
            if k in ("class","spec","race","talents","oil_hands")} | {
            "ilevel":334,"final_T":None,"trinket_ids":d["trinket_ids"],
            "targets":1,"duration_seconds":300,"raid_buffs":True,
            "special_items":[],"embellishments":[],
            "consumable_choices":{
                "flask":"source_default","food":"source_default",
                "potion":"source_default","augmentation":"source_default",
                "diamond_id":0,"omnium_talents":"source_default"}}

def session_key(user,binary,revision,static_cache=None,*,ordinary_variant=None):
    binary=pathlib.Path(binary).expanduser().resolve()
    need(binary.is_file(),"SIMC_BINARY_NOT_FOUND")
    need(type(revision) is str and re.fullmatch(r"[0-9a-fA-F]{7,40}",revision),
         "SIMC_REVISION_MUST_BE_VERIFIED_HEX")
    cache_path=(pathlib.Path(static_cache).expanduser().resolve()
                if static_cache else None)
    need(cache_path is None or cache_path.is_file(),"STATIC_CACHE_NOT_FOUND")
    # Specials require an exact Native static L variant in the selected
    # cache. Don't invite an expensive Native job then invent/zero missing L.
    need(not user.get("special_items") or cache_path is not None,
         "SPECIAL_EQUIPMENT_REQUIRES_EXACT_STATIC_CACHE")
    if ordinary_variant is not None:
        # Developer-only representative experiment. A profile identity change
        # MUST produce a different durable session, never reuse old DPS JSON2.
        need(type(ordinary_variant) is str
             and ordinary_variant in bootstrap.common.ORDINARY_VARIANTS,
             "ORDINARY_VARIANT_NOT_PINNED")
        variant=bootstrap.common.ORDINARY_VARIANTS[ordinary_variant]
        character=user.get("character") if type(user) is dict else None
        target=user.get("target") if type(user) is dict else None
        need(type(character) is dict and type(target) is dict
             and (character.get("class"),character.get("spec"))==variant["key"]
             and target.get("ilevel")==334,
             "ORDINARY_VARIANT_CHARACTER_OR_LEVEL_MISMATCH")
        need(all(r.get("slot")!=variant["slot"] for group in
                 ("special_items","embellishments")
                 for r in user.get(group,[])),
             "ORDINARY_VARIANT_CONFLICTS_WITH_SELECTED_GEAR")
    identity={"schema":SCHEMA,"user":user,
              "simc_binary_sha256":sha(binary.read_bytes()),
              "simc_revision":revision,
              "static_cache_sha256":sha(cache_path.read_bytes()) if cache_path else None}
    if ordinary_variant is not None:
        identity["ordinary_variant"]=ordinary_variant
    return sha(canonical(identity).encode("utf8"))[:20],identity

def session_path(user,root,binary,revision,static_cache=None,*,
                 ordinary_variant=None):
    key,identity=session_key(user,binary,revision,static_cache,
                             ordinary_variant=ordinary_variant)
    return pathlib.Path(root).expanduser().resolve()/key,identity

def store_session(user,root,binary,revision,static_cache=None,*,
                  ordinary_variant=None):
    folder,identity=session_path(user,root,binary,revision,static_cache,
                                 ordinary_variant=ordinary_variant)
    folder.mkdir(parents=True,exist_ok=True)
    target=folder/"user.json"
    raw=canonical(user)+"\n"
    need(not target.exists() or target.read_text(encoding="utf8")==raw,
         "EXISTING_SESSION_USER_INPUT_CHANGED")
    if not target.exists():target.write_text(raw,encoding="utf8")
    lock=folder/"V106_SESSION_IDENTITY.json"
    seal=canonical(identity)+"\n"
    need(not lock.exists() or lock.read_text(encoding="utf8")==seal,
         "SESSION_IDENTITY_DRIFT")
    if not lock.exists():lock.write_text(seal,encoding="utf8")
    return folder

def paths(folder):
    folder=pathlib.Path(folder)
    out=folder/"generated"/"simc_results"
    return {"cancel":folder/"generated"/"CANCEL",
            "progress":out/"V094_PROGRESS.json",
            "native_result":out/"V094_RESULT.json",
            "final":folder/"V106_USER_RESULT.json",
            "state":folder/"V106_WORKER_STATE.json",
            "log":folder/"V106_WORKER.log"}

def request_cancel(folder):
    p=paths(folder)["cancel"]
    p.parent.mkdir(parents=True,exist_ok=True)
    p.touch(exist_ok=True)
    return p

def clear_cancel(folder):
    p=paths(folder)["cancel"]
    if p.exists():p.unlink()

def progress(folder):
    p=paths(folder)
    x={"status":"NOT_STARTED","progress_percent":0.0,
       "completed_jobs":0,"planned_jobs":6,
       "cache_hits":0,"native_attempts":0}
    if p["progress"].is_file():
        report=json.loads(p["progress"].read_text(encoding="utf8"))
        x.update({"status":report["status"],
                  "progress_percent":report.get("progress_percent",0.0),
                  "completed_jobs":report.get("completed_jobs",0),
                  "planned_jobs":report.get("planned_jobs",6),
                  "cache_hits":report.get("cache_verified_hits",0),
                  "native_attempts":report.get("new_native_attempts",0),
                  "error":report.get("error")})
    if p["state"].is_file():
        x["worker"]=json.loads(p["state"].read_text(encoding="utf8"))
    return x

def format_result(data):
    """No recomputation of DPS or stats: render v096's 95%-only user result."""
    need(type(data) is dict and data.get("status","").startswith("PASS")
         and type(data.get("user_result")) is dict,
         "REAL_NATIVE_USER_RESULT_REQUIRED")
    r=data["user_result"];first=r["observed_first_choice"]
    names={"crit_rating":"치명","haste_rating":"가속",
           "mastery_rating":"특화","versatility_rating":"유연"}
    need(r["confidence_level"]==0.95 and
         r["global_optimum_proven"] is False,"ONLY_95_ALLOWED")
    ratings=first["absolute_rating_T"]
    ratio=first["percent_of_final_T"]
    need(all(k in ratings and k in ratio for k in names),
         "FOUR_ABSOLUTE_RATINGS_AND_PERCENT_REQUIRED")
    lines=["관측 1순위 · 전역 최적해 입증 아님",
           "최종 CHMV T = "+str(r["final_T"])+" (B="+str(r["base_B"])
           +", 고정 기름 O="+str(sum(r["fixed_O"].values()))+")",
           " / ".join(names[k]+" "+str(ratings[k])+
                      " ("+format(ratio[k],".2f")+"%)"
                      for k in names),
           "관측 DPS: "+format(first["observed_dps_mean"],",.1f")+
           "   SimC SEM: "+format(first["simc_sem"],",.2f"),
           "선택된 확인 후보 2개의 95% 방향 지지: "+
           ("예" if r["confirmation_pair_direction_supported_at_95"] else "미확정"),
           "실질적 근접 대안 관측: "+str(len(r["material_near_alternatives"]))+
           "개 (미관측은 존재하지 않는다는 뜻 아님)"]
    for i,v in enumerate(r["material_near_alternatives"],1):
        lines.append("대안 "+str(i)+": "+
            " / ".join(names[k]+" "+str(v["absolute_rating_T"][k])
                       for k in names)+" | DPS "+
            format(v["observed_dps_mean"],",.1f")+" | "+
            str(v["pairwise_95_label"]))
    return "\n".join(lines)

@contextlib.contextmanager
def worker_lock(folder):
    """OS-owned lock: concurrent workers refuse, crash auto-unlocks.

    File remains for inspection; we lock the descriptor, not its existence.
    Windows msvcrt byte lock and Unix flock both release on process exit.
    """
    target=pathlib.Path(folder)/"V106_WORKER.lock"
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("a+b") as fd:
        fd.seek(0,2)
        if fd.tell()==0:fd.write(b"1");fd.flush()
        fd.seek(0)
        try:
            if os.name=="nt":
                import msvcrt
                msvcrt.locking(fd.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(fd.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as e:
            raise SessionBlocked("V106_SAME_SESSION_ALREADY_RUNNING") from e
        try:
            yield
        finally:
            fd.seek(0)
            if os.name=="nt":
                msvcrt.locking(fd.fileno(),msvcrt.LK_UNLCK,1)
            else:
                fcntl.flock(fd.fileno(),fcntl.LOCK_UN)

CACHE_PROOF_SCHEMA="v112_completed_user_cache_replay_v1"

def native_json2_hashes(folder):
    """Six real Native JSON2 outputs, already guarded by v064 disk receipts.

    Do not parse effects or trust naked JSON without a companion Native
    receipt; actual byte/identity checks are performed by cache_only replay.
    """
    cases=pathlib.Path(folder)/"generated"/"simc_results"
    out={}
    for file in sorted(cases.rglob("result.json")):
        need((file.parent/"native_receipt.json").is_file(),
             "CACHE_ONLY_NATIVE_RECEIPT_MISSING")
        out[str(file.relative_to(cases)).replace("\\","/")]=sha(file.read_bytes())
    need(len(out)==6,"CACHE_ONLY_REQUIRES_SIX_JSON2_RESULTS")
    return out

def cache_only_preflight(folder):
    """Fail BEFORE touching v094 progress if any Native case is missing."""
    p=paths(folder)
    need(p["final"].is_file() and p["native_result"].is_file()
         and p["progress"].is_file(),
         "CACHE_ONLY_REQUIRES_COMPLETED_REAL_SESSION")
    final=json.loads(p["final"].read_text("utf8"))
    progress=json.loads(p["progress"].read_text("utf8"))
    report=json.loads(p["native_result"].read_text("utf8"))
    need(final["status"].startswith("PASS") and
         report["status"].startswith("PASS") and
         progress["status"].startswith("PASS") and
         progress["completed_jobs"]==6 and
         progress["new_native_attempts"]==6 and
         final["native_calls_cumulative"]==6,
         "CACHE_ONLY_REQUIRES_SIX_COMPLETED_NATIVE")
    need(final["user_result"]["confidence_level"]==0.95
         and final["user_result"]["global_optimum_proven"] is False,
         "CACHE_ONLY_95_RESULT_REQUIRED")
    return {"result":final,"progress":progress,
            "native_sha256":native_json2_hashes(folder)}

def print_user_result(message):
    """Windows cp1252 console fallback: preserve UTF-8 bytes for GUI logs."""
    try:
        print(message,flush=True)
    except UnicodeEncodeError:
        binary=getattr(sys.stdout,"buffer",None)
        if binary is not None:
            binary.write((message+"\n").encode("utf-8"))
            binary.flush()
        else:
            print(message.encode("ascii","backslashreplace").decode("ascii"),
                  flush=True)

def worker(folder,binary,revision,static_cache=None,cache_only=False):
    """Exclusive child process. GUI owns launch/cancel, existing runner owns DPS."""
    folder=pathlib.Path(folder).resolve()
    try:
        with worker_lock(folder):
            return _worker_locked(folder,binary,revision,static_cache,cache_only)
    except SessionBlocked as e:
        print("V106_BLOCKED:",str(e),file=sys.stderr,flush=True)
        return 3

def _worker_locked(folder,binary,revision,static_cache,cache_only):
    p=paths(folder)
    def write_state(status,reason=None):
        data={"schema":SCHEMA,"status":status}
        if reason:data["reason"]=reason
        p["state"].write_text(canonical(data)+"\n",encoding="utf8")
    try:
        need((folder/"user.json").is_file() and
             (folder/"V106_SESSION_IDENTITY.json").is_file(),
             "STORED_USER_SESSION_REQUIRED")
        user=json.loads((folder/"user.json").read_text(encoding="utf8"))
        identity=json.loads((folder/"V106_SESSION_IDENTITY.json").read_text(encoding="utf8"))
        variant=identity.get("ordinary_variant")
        actual_key,now=session_key(user,binary,revision,static_cache,
                                   ordinary_variant=variant)
        need(actual_key==folder.name and identity==now,
             "SESSION_BINARY_REVISION_OR_CACHE_DRIFT")
        cached_before=cache_only_preflight(folder) if cache_only else None
        write_state("RUNNING_CACHE_ONLY" if cache_only else "RUNNING")
        if variant is None:
            # Preserve historical worker call shape and sealed default input.
            result=bootstrap.run(folder/"user.json",folder/"generated",
                 binary,revision,static_cache,execute=True,cache_only=cache_only)
        else:
            result=bootstrap.run(folder/"user.json",folder/"generated",
                 binary,revision,static_cache,execute=True,cache_only=cache_only,
                 ordinary_variant=variant)
        actual=result["native_result"]
        need(actual["status"].startswith("PASS"),"NATIVE_NOT_PASSED")
        if cache_only:
            need(actual["cache_hits_this_run"]==6 and
                 actual["native_calls_cumulative"]==6,
                 "CACHE_ONLY_SIX_OF_SIX_NOT_VERIFIED")
            need(actual["user_result"]==cached_before["result"]["user_result"],
                 "CACHE_ONLY_DPS_SEM_OR_95_RESULT_DRIFT")
            after=cache_only_preflight(folder)
            need(after["native_sha256"]==cached_before["native_sha256"]
                 and after["progress"]["new_native_attempts"]==
                     cached_before["progress"]["new_native_attempts"],
                 "CACHE_ONLY_NATIVE_BYTES_OR_ATTEMPTS_DRIFT")
        # Do not rewrite result for an unrelated cache identity.
        # Cache-only replay changes cache_hit counters, not the observed
        # Native bytes or 95% user result. Compare the durable semantic
        # result and then refresh the presentation atomically.
        if p["final"].is_file():
            old=json.loads(p["final"].read_text("utf8"))
            need(old["user_result"]==actual["user_result"] and
                 old["base_B"]==actual["base_B"] and
                 old["final_T"]==actual["final_T"] and
                 old["result_path"]==actual["result_path"],
                 "CACHED_USER_RESULT_SEMANTICS_CHANGED")
        stage=p["final"].with_suffix(".tmp")
        stage.write_text(canonical(actual)+"\n",encoding="utf8")
        stage.replace(p["final"])
        if cache_only:
            proof={"schema":CACHE_PROOF_SCHEMA,
                   "status":"PASS_SIX_VERIFIED_CACHE_RESULTS_ZERO_NEW_NATIVE",
                   "cache_hits_this_run":actual["cache_hits_this_run"],
                   "native_calls_cumulative":actual["native_calls_cumulative"],
                   "additional_native_calls":0,
                   "native_json2_sha256":cached_before["native_sha256"],
                   "final_T":actual["final_T"],
                   "observed_dps_mean":
                     actual["user_result"]["observed_first_choice"]["observed_dps_mean"],
                   "observed_sem":
                     actual["user_result"]["observed_first_choice"]["simc_sem"],
                   "confidence_level":0.95,"global_optimum_proven":False}
            proof_file=folder/"V112_CACHE_REPLAY_RECEIPT.json"
            tmp=proof_file.with_suffix(".tmp")
            tmp.write_text(canonical(proof)+"\n",encoding="utf8")
            tmp.replace(proof_file)
        write_state("PASS_CACHE_ONLY" if cache_only else "PASS")
        if cache_only:
            print_user_result("검증된 캐시 6/6 · 추가 Native 0회")
        print_user_result(format_result(actual))
        print_user_result("RESULT_DIR: "+str(folder))
        if os.name=="nt":
            try:os.startfile(str(folder))
            except Exception:pass
        return 0
    except Exception as exc:
        write_state("BLOCKED_OR_PARTIAL",type(exc).__name__+":"+str(exc))
        print("V106_BLOCKED:",type(exc).__name__,str(exc),file=sys.stderr,
              flush=True)
        print("RESULT_DIR:",str(folder),file=sys.stderr,flush=True)
        return 3

def main(argv=None):
    p=argparse.ArgumentParser(description="GUI-independent user Native worker")
    p.add_argument("--session",type=pathlib.Path,required=True)
    p.add_argument("--binary",type=pathlib.Path,required=True)
    p.add_argument("--revision",required=True)
    p.add_argument("--static-cache",type=pathlib.Path)
    p.add_argument("--cache-only",action="store_true")
    a=p.parse_args(argv)
    return worker(a.session,a.binary,a.revision,a.static_cache,a.cache_only)
if __name__=="__main__":sys.exit(main())
