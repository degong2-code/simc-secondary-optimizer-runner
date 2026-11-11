#!/usr/bin/env python3
"""v335: official ko_KR names as an incremental Environment Build stage.

Only item IDs from already installed v212 original source/Policy-A choices and
validated *user-visible* seasonal gear can enter the worklist.  Name retrieval
never approves an item or alters G/J/F/O, SimC tokens or DPS-cache identity.
Unresolved optional names never turn a valid numeric environment into BLOCKED.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import tempfile
from concurrent.futures import ThreadPoolExecutor

import v212_environment_manifest as manifests
import v167_product_season_gear_adapter as gear
import v332_blizzard_ko_item_labels as official
import v155_season_api_probe as blizzard

SCHEMA="v335_incremental_environment_ko_KR_names_v1"
BUILD=re.compile(r"\d+(?:\.\d+){3}\Z")
MAX_IDS=2048
MAX_FETCH=128
MAX_FILE=900_000
ROLES=frozenset((
    "trinket","special_effect_gear_candidate","selectable_stat_craft",
    "flask","ordinary_gem","special_gem","weapon_oil",
    "verified_enchant","verified_other_item"))
NAME_FIELDS=frozenset(("item_id","name_ko","api_url",
                       "response_canonical_sha256"))
STATUS_READY="VERIFIED_OFFICIAL_NAMES_COMPLETE"
STATUS_PARTIAL="VERIFIED_NAMES_PARTIAL_PENDING"

class LocalizationBlocked(ValueError):
    pass

def need(ok,code):
    if not ok:raise LocalizationBlocked(code)

def canonical(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,
                      separators=(",",":"),allow_nan=False)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def _path(root,build):
    need(type(build) is str and BUILD.fullmatch(build) is not None,
         "GAME_BUILD_INVALID")
    root=pathlib.Path(root).resolve()
    return (root/"_fresh_season_sources"/("wago_"+build)/
            "localization"/"v335_official_ko_KR.json")

def _validate_row(row,allowed=None):
    need(type(row) is dict and set(row)==NAME_FIELDS,"ROW_FIELDS")
    i=row["item_id"]
    need(type(i) is int and 0<i<=999999999 and
         (allowed is None or i in allowed) and
         type(row["name_ko"]) is str and
         1<=len(row["name_ko"].strip())<=200 and
         row["name_ko"]==row["name_ko"].strip() and
         row["api_url"]==official.url_for(i) and
         type(row["response_canonical_sha256"]) is str and
         re.fullmatch("[a-f0-9]{64}",
                      row["response_canonical_sha256"]) is not None,
         "ROW_OFFICIAL_ID_OR_PROVENANCE_INVALID")
    return i

def _read(root,build):
    path=_path(root,build)
    if not path.exists():return None
    need(path.is_file() and not path.is_symlink() and
         0<path.stat().st_size<=MAX_FILE,"CACHE_FILE_INVALID")
    try:doc=json.loads(path.read_text(encoding="utf8"))
    except (OSError,ValueError) as exc:
        raise LocalizationBlocked("CACHE_JSON_INVALID") from exc
    need(type(doc) is dict and doc.get("schema")==SCHEMA and
         doc.get("game_build")==build and
         doc.get("locale")=="ko_KR" and
         doc.get("provider")=="BLIZZARD_OFFICIAL_GAME_DATA_API" and
         doc.get("api_namespace")=="static-kr" and
         type(doc.get("items")) is list and
         len(doc["items"])<=MAX_IDS and
         type(doc.get("requested_item_ids")) is list and
         type(doc.get("source_membership_sha256")) is str,
         "CACHE_SCHEMA_INVALID")
    seen=set()
    for row in doc["items"]:
        i=_validate_row(row)
        need(i not in seen,"CACHE_DUPLICATE_ITEM")
        seen.add(i)
    need(doc["items"]==sorted(doc["items"],key=lambda r:r["item_id"]) and
         doc["requested_item_ids"]==
             sorted(set(doc["requested_item_ids"])) and
         all(type(i) is int and 0<i<=999999999
             for i in doc["requested_item_ids"]),
         "CACHE_ORDER_OR_IDS_INVALID")
    digest=doc.get("manifest_sha256")
    body={k:v for k,v in doc.items() if k!="manifest_sha256"}
    need(type(digest) is str and digest==sha(canonical(body).encode("utf8")),
         "CACHE_MANIFEST_DRIFT")
    return doc

def read_names(root,build,ids):
    """Read-only ID/name projection. Corruption fails closed, no network."""
    try:
        need(type(ids) in (set,list,tuple) and len(ids)<=MAX_IDS,
             "REQUESTED_IDS_INVALID")
        allowed=set(ids)
        need(all(type(i) is int and 0<i<=999999999 for i in allowed),
             "REQUESTED_ID_INVALID")
        doc=_read(root,build)
        if doc is None:return {}
        return {r["item_id"]:r["name_ko"] for r in doc["items"]
                if r["item_id"] in allowed}
    except (LocalizationBlocked,OSError,TypeError,ValueError):
        return {}

def verified_environment_items(installed,physical_layout=None,
                               *,catalog=None):
    """Worklist is source-owned; *no* new selection/admission from names."""
    manifests.verify_fresh_installed_environment(installed)
    roles={}
    def add(role,i):
        need(role in ROLES and type(i) is int and 0<i<=999999999,
             "SOURCE_ITEM_ID_INVALID")
        roles.setdefault(i,set()).add(role)
    f=installed.get("official_F_physical_source")
    if type(f) is dict:add("flask",f["physical_item_id"])
    oil=installed.get("official_O_physical_source")
    if type(oil) is dict:
        for i in oil["selected_oil_item_ids_by_hand"].values():
            add("weapon_oil",i)
    if type(physical_layout) is dict:
        for i in physical_layout.get("ordinary_gem_ids") or []:
            add("ordinary_gem",i)
        special=physical_layout.get("special_gem_id")
        if special is not None:add("special_gem",special)
    for opt in installed["published_verified_options"]:
        if type(opt) is dict and opt.get("ui_selectable") is True:
            i=opt.get("physical_item_id",opt.get("item_id"))
            if type(i) is int:add("verified_enchant",i)
    if catalog is not None:
        need(type(catalog) is dict and
             catalog.get("status")=="CURRENT_SEASON_CANDIDATE_SELECTION_ONLY" and
             catalog.get("season_build")==installed["game_build"],
             "GEAR_CATALOG_BUILD_OR_STATUS_MISMATCH")
        for role in ("trinket","special_effect_gear_candidate",
                     "selectable_stat_craft"):
            for row in catalog["choices"][role]:
                add(role,row["item_id"])
    need(len(roles)<=MAX_IDS,"LOCALIZATION_WORKLIST_TOO_LARGE")
    return {i:sorted(value) for i,value in sorted(roles.items())}

def exact_product_catalog(game_build):
    """Optional current-season *validated* user-visible roles only."""
    try:
        doc=gear.read()
        if doc["season_build"]!=game_build:return None
        result=gear.public_options(doc)
        if result["status"]!="CURRENT_SEASON_CANDIDATE_SELECTION_ONLY":
            return None
        return result
    except (gear.GearBlocked,ValueError,OSError,KeyError):
        return None

def _static_seed(build,roles):
    """Historical 77/77 is reused only in its matching source/build scope."""
    if build!=_static_build():return []
    # Static 77 receipt is sealed to ITS original 77-item selection set.
    # Intersect later with the build worklist; never spoof its expected IDs.
    source_build,source_ids=official.selected_ids()
    need(source_build==build,"STATIC_SOURCE_BUILD_DRIFT")
    names=official.installed_names(build,set(source_ids))
    try:
        doc=json.loads(official.DEST.read_text(encoding="utf8"))
        rows=doc.get("items") if names else []
        return [row for row in rows if row["item_id"] in names and
                row["item_id"] in roles]
    except (OSError,ValueError,TypeError,KeyError):
        return []

def _static_build():
    try:
        doc=gear.read()
        return doc["season_build"]
    except (gear.GearBlocked,OSError,ValueError,KeyError):
        return None

def _fetch_ids(ids,*,token=None):
    """No automatic auth call when the worklist is already fully cached."""
    need(len(ids)<=MAX_FETCH,"FETCH_LIMIT")
    if not ids:return [],[],0
    if not token:
        token=os.environ.get("BLIZZARD_ACCESS_TOKEN")
    if not token:
        client=os.environ.get("BLIZZARD_CLIENT_ID")
        secret=os.environ.get("BLIZZARD_CLIENT_SECRET")
        if not client or not secret:return [],[{"item_id":i,
                               "code":"CREDENTIALS_UNAVAILABLE"} for i in ids],0
        try:token=blizzard.oauth_token(blizzard.BLIZZARD_TOKEN_URL,
                                      client,secret)
        except Exception:return [],[{"item_id":i,
                               "code":"OAUTH_UNAVAILABLE"} for i in ids],1
        auth_calls=1
    else:auth_calls=0
    def work(i):
        try:
            doc=blizzard.request_json(official.url_for(i),
                headers={"Authorization":"Bearer "+token})
            row=official.row_from_api(i,doc)
            _validate_row(row,{i})
            return row,None
        except Exception as exc:
            # No HTTP error contents or tokens in the receipt.
            return None,{"item_id":i,"code":type(exc).__name__}
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses=list(pool.map(work,ids))
    return ([x for x,e in responses if x is not None],
            [e for x,e in responses if e is not None],
            auth_calls+len(ids))

def _store(root,build,rows,requested,roles):
    """Atomic, source-sealed local receipt; only mutate on actual changes."""
    path=_path(root,build)
    body={"schema":SCHEMA,"game_build":build,
          "locale":"ko_KR","provider":"BLIZZARD_OFFICIAL_GAME_DATA_API",
          "api_namespace":"static-kr",
          "requested_item_ids":sorted(requested),
          "source_membership_sha256":sha(canonical(roles).encode("utf8")),
          "items":sorted(rows,key=lambda r:r["item_id"])}
    payload={**body,"manifest_sha256":sha(canonical(body).encode("utf8"))}
    data=(json.dumps(payload,indent=2,ensure_ascii=False,sort_keys=True)+"\n").encode("utf8")
    need(len(data)<=MAX_FILE,"CACHE_SIZE_EXCEEDED")
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.read_bytes()==data:return False
    with tempfile.NamedTemporaryFile(mode="wb",dir=path.parent,
                                    prefix=".v335-",delete=False) as output:
        tmp=pathlib.Path(output.name)
        try:
            output.write(data);output.flush();os.fsync(output.fileno())
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
    try:os.replace(tmp,path)
    finally:tmp.unlink(missing_ok=True)
    return True

def build_from_verified_install(root,installed,physical_layout=None,
                                *,catalog=None,allow_network=True):
    """Automatic Environment Build stage: never another item-admission gate."""
    game_build=installed["game_build"]
    roles=verified_environment_items(installed,physical_layout,catalog=catalog)
    chosen=set(roles)
    cached=_read(root,game_build)
    old={r["item_id"]:r for r in cached["items"]} if cached else {}
    # Preserve identical-season historical name records even if currently
    # not selected, for incremental same-season future option updates.
    for r in _static_seed(game_build,roles):
        old.setdefault(r["item_id"],r)
    needed=sorted(chosen-set(old))
    query=needed[:MAX_FETCH] if allow_network else []
    collected,errors,network_calls=_fetch_ids(query) if query else ([],[],0)
    for row in collected:old[row["item_id"]]=row
    if chosen or old:
        _store(root,game_build,list(old.values()),chosen,roles)
    complete=sum(i in old for i in chosen)
    status=(STATUS_READY if complete==len(chosen) and chosen else
            "PENDING_VERIFIED_CHOICE_SOURCE" if not chosen else STATUS_PARTIAL)
    return {"schema":SCHEMA,"status":status,"game_build":game_build,
            "selected_item_count":len(chosen),"verified_names":complete,
            "pending_names":len(chosen)-complete,
            "pending_item_ids":sorted(chosen-set(old)),
            "selected_categories":{k:sum(k in value for value in roles.values())
                 for k in sorted({r for v in roles.values() for r in v})},
            "source_membership_sha256":sha(canonical(roles).encode("utf8")),
            "existing_same_build_name_records_reused":
                len(chosen.intersection(old))-len(collected),
            "new_official_name_records":len(collected),
            "network_calls_now":network_calls,"native_calls_now":0,
            "source_only_names_not_item_approval":True,
            "errors":errors[:MAX_FETCH]}


def cache_status(root,build):
    """No network: provider/status/count metadata only, not raw item contents."""
    try:
        doc=_read(root,build)
        if doc is None:
            return {"schema":SCHEMA,"status":"OFFICIAL_KO_CACHE_NOT_INSTALLED",
                    "game_build":build,"verified_item_names":0,
                    "native_calls_now":0,"network_calls_now":0}
        return {"schema":SCHEMA,"status":"READ_ONLY_VERIFIED_OFFICIAL_NAMES",
                "game_build":build,"verified_item_names":len(doc["items"]),
                "source_membership_sha256":doc["source_membership_sha256"],
                "native_calls_now":0,"network_calls_now":0}
    except (LocalizationBlocked,OSError,ValueError,TypeError):
        return {"schema":SCHEMA,"status":"OFFICIAL_KO_CACHE_INVALID",
                "game_build":build,"verified_item_names":0,
                "native_calls_now":0,"network_calls_now":0}

def build_for_environment(root,game_build,result,*,target_ilevel):
    """v113 bridge for an already verified v212 installation or reuse.

    Verifies the existing original v212 receipt again only to obtain its
    official IDs; does not reconstruct a G/J/F/O or effects engine.
    """
    if result.get("environment_ready") is not True or \
       result.get("environment_installed") is not True:
        return {"schema":SCHEMA,"status":"WAITING_FOR_VERIFIED_ENVIRONMENT",
                "game_build":game_build,"native_calls_now":0,"network_calls_now":0}
    compilation=result.get("source_compilation") or {}
    install=compilation.get("verified_environment_install") or {}
    path=install.get("stage_output_path")
    if not path:
        manifest=result.get("installed_manifest_sha256")
        if type(manifest) is str and re.fullmatch("[a-f0-9]{64}",manifest):
            path=(pathlib.Path(root)/"_fresh_season_sources"/
                  ("wago_"+game_build)/"fresh_source"/
                  ("v212_installed_"+manifest[:20]+".json"))
    if not path:
        return {"schema":SCHEMA,"status":"WAITING_FOR_INSTALLED_ITEM_SOURCE",
                "game_build":game_build,"native_calls_now":0,"network_calls_now":0}
    path=pathlib.Path(path)
    need(path.is_file() and not path.is_symlink() and
         path.stat().st_size<=MAX_FILE,"V212_SOURCE_FILE_INVALID")
    doc=json.loads(path.read_text(encoding="utf8"))
    manifests.verify_fresh_installed_environment(doc)
    need(doc["game_build"]==game_build and
         doc["target_ilevel"]==target_ilevel,
         "V212_INSTALLED_SCOPE_DRIFT")
    source=result.get("installed_manifest_sha256") or install.get("manifest_sha256")
    need(source==doc["manifest_sha256"],"V212_SOURCE_MANIFEST_DRIFT")
    physical=compilation.get("physical_gem_layout_unadmitted")
    catalog=exact_product_catalog(game_build)
    return build_from_verified_install(root,doc,physical,catalog=catalog)
