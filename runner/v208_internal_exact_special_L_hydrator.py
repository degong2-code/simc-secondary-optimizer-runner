#!/usr/bin/env python3
"""v208 selected-special static L, app-local, one physical SimC Native on miss.

Reuse v098's exact generated representative profile and v046 Native JSON2
variant cache. NEVER silently infer L, replace old static snapshots, run DPS
optimizer, or make the user provide source/filler/seed files.
The /plan endpoint never invokes this; /start is explicit user action.
"""
from __future__ import annotations
import copy,hashlib,json,os,pathlib,subprocess,tempfile
import v046_static_item_cache as item_cache
import v062_static_budget_bridge as budget
import v098_target_user_scenario_bootstrap as bootstrap
import v122_common_profile_format as profile_format

SCHEMA="v208_one_bounded_native_special_L_snapshot_v1"
MAX_SECONDS=180
MAX_SPECIALS=8
REMOVABLE=("gear_crit_rating=","gear_haste_rating=",
           "gear_mastery_rating=","gear_versatility_rating=")

class StaticLBlocked(ValueError):pass
def need(ok,code):
    if not ok:raise StaticLBlocked(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def sha_file(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open("rb") as src:
        for raw in iter(lambda:src.read(1024*1024),b""):
            h.update(raw)
    return h.hexdigest()

def canonical(obj):
    return item_cache.canonical(obj).encode("utf8")

def source_cache(root,requested):
    """Optional historic cache is NEVER modified; immutable snapshots preferred."""
    root=pathlib.Path(root).resolve()
    if requested is not None:
        path=pathlib.Path(requested).expanduser().resolve()
        need(path.is_file(),"EXPLICIT_STATIC_CACHE_NOT_PRESENT")
        return path
    root_dir=root.parent
    pointer=root_dir/"static-item-caches"/"latest.json"
    if pointer.is_file():
        data=json.loads(pointer.read_text("utf8"))
        name=data.get("filename")
        need(type(name) is str and
             len(name)==76 and name.startswith("static-") and
             name.endswith(".json") and
             all(k in "0123456789abcdef" for k in name[7:-5]),
             "STATIC_L_SNAPSHOT_POINTER_INVALID")
        path=pointer.parent/name
        need(path.is_file(),"STATIC_L_SNAPSHOT_FILE_MISSING")
        cache=item_cache.load(path)
        need(name=="static-"+sha(canonical(cache))+".json",
             "STATIC_L_SNAPSHOT_CONTENT_CHANGED")
        return path
    legacy=root_dir/"static-item-cache.json"
    return legacy if legacy.is_file() else None

def missing_specials(saved,staged):
    need(type(staged) is dict and
         staged.get("schema")=="v208_exact_current_special_static_source_v1"
         and staged.get("native_calls")==0,
         "PREBUDGET_SOURCE_INVALID")
    rows=staged["special_rows"]
    need(type(rows) is list and 1<=len(rows)<=MAX_SPECIALS,
         "SELECTED_SPECIAL_COUNT_INVALID")
    missing=[]
    for row in rows:
        need(type(row) is dict and type(row.get("options")) is dict,
             "PREBUDGET_SPECIAL_ROW_INVALID")
        stat=budget.get_native_secondary(saved,row)
        if stat is None and budget.primary_only_head_gem(row):
            bare={**row,"options":{k:v for k,v in row["options"].items()
                                  if k!="gem_id"}}
            stat=budget.get_native_secondary(saved,bare)
        if stat is None:missing.append(row)
    return missing

def physical_input(profile,json_path):
    """Equivalent narrow physical-input transformation to existing v140."""
    lines=profile.splitlines()
    for prefix in REMOVABLE:
        need(sum(x.startswith(prefix) for x in lines)==1,
             "EXACT_ONE_GEAR_OVERRIDE_REQUIRED")
    need(lines.count("json2="+profile_format.JSON2_PLACEHOLDER)==1
         and sum(x.startswith("iterations=") for x in lines)==1,
         "PHYSICAL_PROFILE_PLACEHOLDERS_MISSING")
    out=[]
    for line in lines:
        if any(line.startswith(p) for p in REMOVABLE):continue
        if line.startswith("json2="):out.append("json2="+str(json_path.resolve()))
        elif line.startswith("iterations="):out.append("iterations=1")
        elif line.startswith("max_time="):out.append("max_time=2")
        else:out.append(line)
    need(any(x.startswith("default_actions=1") for x in out)
         and not any(x.startswith("load_default_gear=") for x in out),
         "PHYSICAL_GEAR_OR_APL_NOT_INTERNAL")
    return "\n".join(out)+"\n"

def selected_records(raw,missing,revision):
    """Parse only relevant gear records using exact v046 Native parser."""
    doc=json.loads(raw)
    need(doc.get("report_version")=="2.0.0" and
         str(doc.get("git_revision","")).startswith(revision[:7]),
         "SIMC_JSON2_REVISION_NOT_MATCHED")
    people=(doc.get("sim") or {}).get("players")
    need(type(people) is list and len(people)==1,"EXPECTED_SINGLE_SIMC_ACTOR")
    gear=people[0].get("gear")
    need(type(gear) is dict,"NATIVE_GEAR_MISSING")
    slots={r["slot"] for r in missing}
    need(len(slots)==len(missing) and slots<=set(gear),
         "NATIVE_EXACT_SPECIAL_SLOTS_MISSING")
    filtered=copy.deepcopy(doc)
    filtered["sim"]["players"][0]["gear"]={s:gear[s] for s in sorted(slots)}
    records=item_cache.native_records(canonical(filtered),
                                       artifact_id="V208_USER_LOCAL_EXACT_STATIC_L")
    expected={item_cache.digest(budget.exact_identity(x)):x for x in missing}
    need(len(expected)==len(missing),"DUPLICATE_NORMALIZED_SPECIAL_VARIANT")
    found={}
    for record in records:
        key=item_cache.digest(record["identity"])
        need(key in expected and key not in found,
             "NATIVE_SPECIAL_ID_ILVL_OPTIONS_MISMATCH")
        need(record["static"]["secondary"] is not None,
             "NATIVE_SPECIAL_STATIC_NOT_OBSERVED")
        record["metadata"]["native_json_sha256"]=sha(raw)
        found[key]=record
    need(set(found)==set(expected),"NATIVE_ALL_MISSING_SPECIAL_VARIANTS_REQUIRED")
    return list(found.values())

def snapshot(root,cache):
    """Append-only immutable content-addressed snapshots, old session files stable."""
    folder=pathlib.Path(root).resolve().parent/"static-item-caches"
    folder.mkdir(parents=True,exist_ok=True)
    key=sha(canonical(cache))
    name="static-"+key+".json"
    target=folder/name
    if target.exists():
        need(item_cache.load(target)==cache,"EXISTING_STATIC_L_SNAPSHOT_DRIFT")
    else:
        item_cache.write_atomic(target,cache)
    # Verify exact content before changing the unsealed "latest" advisory.
    need(item_cache.load(target)==cache,"NEW_STATIC_L_SNAPSHOT_NOT_EQUAL")
    pointer=folder/"latest.json"
    value=json.dumps({"schema":SCHEMA,"filename":name},sort_keys=True)+"\n"
    fd,temp=tempfile.mkstemp(prefix=".static-L-latest-",dir=folder)
    try:
        with os.fdopen(fd,"w",encoding="utf8") as f:
            f.write(value);f.flush();os.fsync(f.fileno())
        os.replace(temp,pointer)
    finally:
        if os.path.exists(temp):os.unlink(temp)
    return target

def hydrate(user,root,binary,revision,existing=None,*,timeout=MAX_SECONDS):
    """Return snapshot path and Native count; NEVER mutate earlier cache bytes."""
    root=pathlib.Path(root).expanduser().resolve()
    binary=pathlib.Path(binary).expanduser().resolve()
    need(type(user) is dict and bool(user.get("special_items")),
         "EXPLICIT_SELECTED_SPECIAL_REQUIRED")
    need(binary.is_file(),"SIMC_BINARY_NOT_PRESENT")
    need(type(revision) is str and len(revision)>=7,"SIMC_REVISION_REQUIRED")
    need(type(timeout) is int and 1<=timeout<=MAX_SECONDS,"STATIC_NATIVE_TIMEOUT_BOUND")
    staged=bootstrap.build(user,root.parent/"static-item-prebudget-no-write",
                           binary,revision,static_special_probe_only=True,
                           current_season_product=True)
    initial=item_cache.load(pathlib.Path(existing)) if existing else item_cache.empty_cache()
    missing=missing_specials(initial,staged)
    if not missing:
        # Reuse proven historical file path/content, not gratuitous snapshot.
        need(existing is not None,"NATIVE_L_CACHE_HIT_PATH_REQUIRED")
        return {"static_cache_path":str(pathlib.Path(existing).resolve()),
                "native_new_calls":0,"cache_reused":len(staged["special_rows"]),
                "source":"EXACT_STATIC_CACHE_REUSED"}
    ident={"schema":SCHEMA,
           "source_profile_sha256":staged["source_profile_sha256"],
           "binary_sha256":sha_file(binary),"revision":revision,
           "missing":[budget.exact_identity(r) for r in missing]}
    probe_dir=root.parent/"static-item-probes"/sha(canonical(ident))[:24]
    probe_dir.mkdir(parents=True,exist_ok=True)
    case=probe_dir/"native.json"
    native_input=physical_input(staged["profile"],case)
    source_file=probe_dir/"physical.simc"
    if source_file.is_file():
        need(source_file.read_bytes()==native_input.encode("utf8"),
             "EXISTING_STATIC_INPUT_BYTES_DRIFT")
    else:source_file.write_text(native_input,encoding="utf8")
    calls=0
    if not case.is_file():
        # One physical Native resolves every missing special in the SAME
        # current user equipment, rather than 1 run per item or spec.
        with (probe_dir/"native.log").open("ab") as log:
            log.write(b"\n=== V208 ONE SELECTED USER STATIC NATIVE ===\n")
            try:
                completed=subprocess.run([str(binary),str(source_file)],
                       cwd=probe_dir,stdin=subprocess.DEVNULL,
                       stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
            except subprocess.TimeoutExpired as exc:
                raise StaticLBlocked("ONE_NATIVE_STATIC_L_TIMEOUT") from exc
        need(completed.returncode==0 and case.is_file(),
             "ONE_NATIVE_STATIC_L_SIMC_FAILED")
        calls=1
    raw=case.read_bytes()
    need(0<len(raw)<=item_cache.MAX_NATIVE_BYTES,
         "ONE_NATIVE_STATIC_L_JSON_SIZE")
    records=selected_records(raw,missing,revision)
    merged=copy.deepcopy(initial)
    item_cache.merge_native(merged,records)
    target=snapshot(root,merged)
    return {"static_cache_path":str(target),"native_new_calls":calls,
            "cache_reused":len(staged["special_rows"])-len(missing),
            "native_json2_sha256":sha(raw),
            "observed_selected_variants":len(records),
            "source":"EXACT_SIMC_NATIVE_L_RESOLVED_WITHOUT_USER_CACHE"}
