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
import v055_simc_item_selection as selector
import v213_source_to_catalog as source_bridge

SCHEMA="v208_one_bounded_native_special_L_snapshot_v1"
START_RECEIPT_SCHEMA="v208_selected_special_start_receipt_v1"
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
        bare=budget.undecorated_special(row)
        stat=budget.get_native_secondary(saved,bare)
        if stat is None:missing.append(bare)
    return missing

def physical_input(profile,json_path,source_rows=None,query_rows=None):
    """One real physical profile; strip ONLY selected special J/E for L.

    All other gear/consumables remain the exact user's selected inputs.
    This temporary Native source is never the DPS execution profile.
    """
    lines=profile.splitlines()
    originals={r["slot"]:r for r in (source_rows or [])}
    queries={r["slot"]:r for r in (query_rows or [])}
    need(len(originals)==len(source_rows or []) and
         len(queries)==len(query_rows or []) and
         set(queries)<=set(originals),
         "SOURCE_AND_BARE_SPECIAL_SLOTS_MISMATCH")
    observed=set()
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
        elif line.split("=",1)[0] in queries:
            slot=line.split("=",1)[0]
            name,encoded=item_cache.parse_encoded(line.split("=",1)[1])
            orig=originals[slot]
            need(slot not in observed and
                 int(encoded["id"])==orig["item_id"] and
                 int(encoded["ilevel"])==orig["ilevel"] and
                 {k:v for k,v in encoded.items()
                  if k not in ("id","ilevel","source")}==orig["options"],
                 "SPECIAL_PHYSICAL_SOURCE_NOT_EXACT_USER_VARIANT")
            observed.add(slot)
            bare=queries[slot]
            need(bare==budget.undecorated_special(orig),
                 "SPECIAL_BARE_VARIANT_NOT_EXACT_PROJECTION")
            if bare==orig:
                out.append(line)
            else:
                out.append(selector.equipment_line(slot,bare["item_id"],
                               bare["ilevel"],bare["options"]))
        else:out.append(line)
    need(observed==set(queries),"SELECTED_BARE_SLOTS_NOT_IN_PROFILE")
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

def valid_sha(value):
    return (type(value) is str and len(value)==64 and
            all(ch in "0123456789abcdef" for ch in value))

def source_catalog_identity(path):
    if path is None:
        return None
    path=pathlib.Path(path).resolve()
    need(path.is_file(),"V213_SOURCE_CATALOG_MISSING_FOR_START_RECEIPT")
    raw=path.read_bytes()
    try:
        document=json.loads(raw.decode("utf8"))
        source_bridge.verify_catalog(document)
    except Exception as exc:
        raise StaticLBlocked("V213_SOURCE_CATALOG_INVALID_FOR_START_RECEIPT:"+
                             type(exc).__name__) from exc
    return {"schema":document["schema"],
            "artifact_sha256":sha(raw),
            "manifest_sha256":document["manifest_sha256"],
            "game_build":document["game_build"],
            "simc_revision":document["simc_revision"]}

def build_start_receipt(staged,before_cache,after_cache,result,cache_path,
                        binary,revision,source_catalog_path=None):
    """Seal exact selected bare-L identities, cache evidence and Native JSON2 provenance."""
    item_cache.check_cache(before_cache)
    item_cache.check_cache(after_cache)
    rows=staged.get("special_rows")
    need(type(rows) is list and 1<=len(rows)<=MAX_SPECIALS,
         "V208_RECEIPT_SELECTED_SPECIAL_ROWS_INVALID")
    selected=[]
    hits=0
    misses=0
    native_calls=result.get("native_new_calls")
    need(type(native_calls) is int and 0<=native_calls<=1,
         "V208_RECEIPT_NATIVE_CALL_COUNT_INVALID")
    for row in rows:
        selected_identity=budget.exact_identity(row)
        bare_identity=budget.exact_identity(budget.undecorated_special(row))
        key=item_cache.digest(bare_identity)
        was_hit=key in before_cache["variants"]
        record=after_cache["variants"].get(key)
        need(type(record) is dict and record.get("identity")==bare_identity,
             "V208_RECEIPT_EXACT_BARE_VARIANT_MISSING")
        need(record.get("static_digest")==item_cache.digest(record.get("static")),
             "V208_RECEIPT_STATIC_DIGEST_INVALID")
        source_kind=record.get("source_kind")
        need(source_kind in ("NATIVE_JSON2_RESOLVED_VARIANT",
                             "USER_REQUESTED_MANUAL_CORRECTION"),
             "V208_RECEIPT_STATIC_SOURCE_INVALID")
        metadata=record.get("metadata") or {}
        native_sha=metadata.get("native_json_sha256")
        native_revision=metadata.get("native_revision")
        artifact=metadata.get("artifact")
        if source_kind=="NATIVE_JSON2_RESOLVED_VARIANT":
            need(valid_sha(native_sha) and type(native_revision) is str and
                 native_revision.startswith(revision[:7]),
                 "V208_RECEIPT_NATIVE_JSON2_PROVENANCE_MISSING")
        else:
            native_sha=None
            native_revision=None
            artifact=None
        measured=record.get("static",{}).get("secondary")
        need(type(measured) is dict and set(measured)==set(item_cache.STATS)
             and all(type(v) is int and 0<=v<=100000
                     for v in measured.values()),
             "V208_RECEIPT_MEASURED_L_INVALID")
        if was_hit:
            hits+=1
            cache_status="HIT"
        else:
            misses+=1
            cache_status=("MISS_NEW_NATIVE_JSON2" if native_calls
                          else "MISS_REUSED_NATIVE_JSON2")
            need(source_kind=="NATIVE_JSON2_RESOLVED_VARIANT",
                 "V208_RECEIPT_MISS_WITHOUT_NATIVE_JSON2")
        selected.append({
            "selected_identity":selected_identity,
            "selected_identity_sha256":item_cache.digest(selected_identity),
            "bare_identity":bare_identity,
            "bare_identity_sha256":key,
            "cache_status":cache_status,
            "source_kind":source_kind,
            "static_digest":record["static_digest"],
            "measured_L":dict(measured),
            "native_json2":{
                "sha256":native_sha,
                "revision":native_revision,
                "source":artifact,
            },
        })
    new_misses=sum(row["cache_status"]=="MISS_NEW_NATIVE_JSON2"
                    for row in selected)
    need(native_calls==(1 if new_misses else 0) and
         not (native_calls and new_misses!=misses),
         "V208_RECEIPT_NATIVE_CALL_COUNT_MISMATCH")
    need(result.get("cache_reused")==hits,
         "V208_RECEIPT_CACHE_HIT_COUNT_MISMATCH")
    if misses:
        fresh_hash=result.get("native_json2_sha256")
        need(valid_sha(fresh_hash) and all(
            row["native_json2"]["sha256"]==fresh_hash
            for row in selected if row["cache_status"] in (
                "MISS_NEW_NATIVE_JSON2","MISS_REUSED_NATIVE_JSON2")),
            "V208_RECEIPT_FRESH_NATIVE_JSON2_SHA_MISMATCH")
    cache_path=pathlib.Path(cache_path).resolve()
    need(cache_path.is_file(),"V208_RECEIPT_STATIC_CACHE_MISSING")
    cache_raw=cache_path.read_bytes()
    payload={
        "schema":START_RECEIPT_SCHEMA,
        "status":"VERIFIED",
        "source_catalog":source_catalog_identity(source_catalog_path),
        "simc":{"revision":revision,"binary_sha256":sha_file(binary)},
        "static_cache":{"basename":cache_path.name,
                        "size_bytes":len(cache_raw),"sha256":sha(cache_raw)},
        "selected_special_count":len(selected),
        "selected_specials":selected,
        "cache_summary":{"hits":hits,"misses":misses,
                         "native_calls_this_start":native_calls},
        "native_calls_this_start":native_calls,
        "native_json2_sha256s":sorted({row["native_json2"]["sha256"]
                                       for row in selected
                                       if row["native_json2"]["sha256"]}),
    }
    payload["receipt_sha256"]=sha(canonical(payload))
    return payload

def write_start_receipt(session_folder,receipt):
    need(type(receipt) is dict and receipt.get("schema")==START_RECEIPT_SCHEMA
         and valid_sha(receipt.get("receipt_sha256")),
         "V208_START_RECEIPT_INVALID")
    payload={k:v for k,v in receipt.items() if k!="receipt_sha256"}
    need(receipt["receipt_sha256"]==sha(canonical(payload)),
         "V208_START_RECEIPT_DIGEST_INVALID")
    path=pathlib.Path(session_folder).resolve()/"start-receipts"/(
        "v208-start-"+receipt["receipt_sha256"]+".json")
    path.parent.mkdir(parents=True,exist_ok=True)
    encoded=json.dumps(receipt,sort_keys=True,ensure_ascii=False,
                       indent=2,allow_nan=False)+"\n"
    if path.exists():
        need(path.read_text(encoding="utf8")==encoded,
             "V208_START_RECEIPT_CONTENT_DRIFT")
    else:
        fd,temp=tempfile.mkstemp(prefix=".v208-start-",dir=path.parent)
        try:
            with os.fdopen(fd,"w",encoding="utf8") as out:
                out.write(encoded);out.flush();os.fsync(out.fileno())
            os.replace(temp,path)
        finally:
            if os.path.exists(temp):os.unlink(temp)
    return {"schema":START_RECEIPT_SCHEMA,
            "receipt_sha256":receipt["receipt_sha256"],
            "path":path.relative_to(pathlib.Path(session_folder).resolve()).as_posix(),
            "native_calls_this_start":receipt["native_calls_this_start"],
            "selected_special_count":receipt["selected_special_count"]}

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

def hydrate(user,root,binary,revision,existing=None,*,timeout=MAX_SECONDS,
            source_catalog_path=None):
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
                           current_season_product=True,
                           source_catalog_path=source_catalog_path)
    initial=item_cache.load(pathlib.Path(existing)) if existing else item_cache.empty_cache()
    missing=missing_specials(initial,staged)
    if not missing:
        # Reuse proven historical file path/content, not gratuitous snapshot.
        need(existing is not None,"NATIVE_L_CACHE_HIT_PATH_REQUIRED")
        result={"static_cache_path":str(pathlib.Path(existing).resolve()),
                "native_new_calls":0,"cache_reused":len(staged["special_rows"]),
                "source":"EXACT_STATIC_CACHE_REUSED"}
        result["start_receipt"]=build_start_receipt(
            staged,initial,initial,result,existing,binary,revision,
            source_catalog_path)
        return result
    ident={"schema":SCHEMA,
           "source_profile_sha256":staged["source_profile_sha256"],
           "binary_sha256":sha_file(binary),"revision":revision,
           "missing":[budget.exact_identity(r) for r in missing]}
    probe_dir=root.parent/"static-item-probes"/sha(canonical(ident))[:24]
    probe_dir.mkdir(parents=True,exist_ok=True)
    case=probe_dir/"native.json"
    native_input=physical_input(staged["profile"],case,
                                staged["special_rows"],missing)
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
    result={"static_cache_path":str(target),"native_new_calls":calls,
            "cache_reused":len(staged["special_rows"])-len(missing),
            "native_json2_sha256":sha(raw),
            "observed_selected_variants":len(records),
            "source":"EXACT_SIMC_NATIVE_L_RESOLVED_WITHOUT_USER_CACHE"}
    result["start_receipt"]=build_start_receipt(
        staged,initial,merged,result,target,binary,revision,
        source_catalog_path)
    return result
