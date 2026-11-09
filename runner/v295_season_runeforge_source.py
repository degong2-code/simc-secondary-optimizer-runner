#!/usr/bin/env python3
"""Versioned, source-pinned DK runeforges for the existing Season Build.

Discover exact IDs from SimC's own DK class module, not a per-season list in
the UI or a copied character's equipment. Does not model rune mechanics,
certify DPS, or admit any ordinary/temporary enchant.
"""
from __future__ import annotations
import hashlib,json,pathlib,re
from urllib.request import Request
import v217_stage_execution_engine as stages
import v229_simc_only_source_seed as seed
import v275_pinned_simc_compiler_inputs as pinned

SCHEMA="v295_season_dk_runeforge_source_v1"
SOURCE_PATH="engine/class_modules/sc_death_knight.cpp"
OUT="fresh_source/v295_dk_runeforge_source.json"
LIMIT=6_000_000
SHA40=re.compile(r"[0-9a-f]{40}\Z")
ID=re.compile(r"\bRUNEFORGE_ID_([A-Z][A-Z0-9_]*)\s*=\s*(\d+)\s*,")
ENUM=re.compile(r"\benum\s+runeforges_e\s*\{([^}]*)\}",re.S)

class RuneforgeSourceBlocked(ValueError):pass
def need(condition,code):
    if not condition:raise RuneforgeSourceBlocked(code)
def canonical(data):
    return json.dumps(data,ensure_ascii=False,sort_keys=True,
                      separators=(",",":"),allow_nan=False)
def digest(raw):return hashlib.sha256(raw).hexdigest()

def compile_source(raw,*,game_build,simc_revision):
    need(type(raw) is bytes and 0<len(raw)<=LIMIT,
         "DK_PINNED_SOURCE_SIZE_INVALID")
    need(type(game_build) is str and bool(game_build) and
         type(simc_revision) is str and SHA40.fullmatch(simc_revision),
         "DK_SEASON_SOURCE_IDENTITY_REQUIRED")
    try:text=raw.decode("utf8")
    except UnicodeError as exc:
        raise RuneforgeSourceBlocked("DK_SOURCE_UTF8_REQUIRED") from exc
    matches=ENUM.findall(text)
    need(len(matches)==1,"DK_RUNEFORGE_SOURCE_ENUM_MISSING_OR_AMBIGUOUS")
    entries=ID.findall(matches[0])
    need(1<=len(entries)<=32,"DK_RUNEFORGE_ENUM_IDS_REQUIRED")
    names=[name for name,_ in entries]
    numbers=[int(value) for _,value in entries]
    need(len(set(names))==len(names) and len(set(numbers))==len(numbers)
         and all(0<value<10_000_000 for value in numbers),
         "DK_RUNEFORGE_ENUM_DUPLICATE_OR_INVALID")
    # No source-independent list of rune IDs. Future additions/removals are
    # discovered at the next pinned SimC source build.
    items=[{"enchant_id":value,"token":name.lower(),
            "display_name":"Rune of "+name.replace("_"," ").title(),
            "class":"deathknight","weapon_hands":["main_hand","off_hand"]}
           for name,value in entries]
    items.sort(key=lambda item:item["enchant_id"])
    data={"schema":SCHEMA,
          "status":"PINNED_SIMC_DK_RUNEFORGE_SOURCE_OPTIONS",
          "game_build":game_build,"simc_revision":simc_revision,
          "source_path":SOURCE_PATH,"source_sha256":digest(raw),
          "source_git_blob_sha1":seed.git_blob(raw),
          "items":items,"count":len(items),
          "class_scope":"deathknight","selection_requires_weapon":True,
          "simc_owns_rune_effects":True,"source_profile_gear_copied":False,
          "native_calls":0}
    return {**data,"manifest_sha256":digest(canonical(data).encode("utf8"))}

def verify(doc,*,game_build=None,simc_revision=None):
    need(type(doc) is dict and doc.get("schema")==SCHEMA and
         doc.get("status")=="PINNED_SIMC_DK_RUNEFORGE_SOURCE_OPTIONS" and
         doc.get("source_path")==SOURCE_PATH and
         (game_build is None or doc.get("game_build")==game_build) and
         (simc_revision is None or doc.get("simc_revision")==simc_revision) and
         type(doc.get("simc_revision")) is str and
         SHA40.fullmatch(doc["simc_revision"]) and
         type(doc.get("game_build")) is str and bool(doc["game_build"]) and
         type(doc.get("source_sha256")) is str and
         re.fullmatch(r"[0-9a-f]{64}",doc["source_sha256"]) and
         type(doc.get("source_git_blob_sha1")) is str and
         SHA40.fullmatch(doc["source_git_blob_sha1"]) and
         doc.get("class_scope")=="deathknight" and
         doc.get("selection_requires_weapon") is True and
         doc.get("simc_owns_rune_effects") is True and
         doc.get("source_profile_gear_copied") is False and
         doc.get("native_calls")==0 and
         type(doc.get("items")) is list and
         type(doc.get("count")) is int and
         doc["count"]==len(doc["items"]) and 1<=doc["count"]<=32,
         "DK_RUNEFORGE_SOURCE_SCOPE_DRIFT")
    ids=[]
    for row in doc["items"]:
        need(type(row) is dict and set(row)=={
            "enchant_id","token","display_name","class","weapon_hands"}
            and type(row["enchant_id"]) is int and
            0<row["enchant_id"]<10_000_000 and
            type(row["token"]) is str and
            re.fullmatch(r"[a-z][a-z0-9_]*",row["token"]) and
            row["display_name"]=="Rune of "+row["token"].replace("_"," ").title() and
            row["class"]=="deathknight" and
            row["weapon_hands"]==["main_hand","off_hand"],
            "DK_RUNEFORGE_SOURCE_OPTION_DRIFT")
        ids.append(row["enchant_id"])
    need(ids==sorted(set(ids)) and
         doc.get("manifest_sha256")==digest(canonical(
             {k:v for k,v in doc.items() if k!="manifest_sha256"}).encode("utf8")),
         "DK_RUNEFORGE_SOURCE_MANIFEST_DRIFT")
    return True

def collect(*,stage_root,game_build,pinned_source,transport=None):
    """Optional v217-cached source, not a gate on G/J/F/O environment READY."""
    if not(type(pinned_source) is dict and
           pinned_source.get("status")=="PINNED_V211_AND_GENERATED_SOURCES_SEALED"
           and type(pinned_source.get("source_stage")) is dict and
           pinned_source["source_stage"].get("status") in
               ("EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED")):
        return {"status":"DK_RUNEFORGE_PINNED_SOURCE_PENDING",
                "items":[],"native_calls":0,"network_calls":0}
    revision=pinned_source.get("simc_revision")
    need(type(revision) is str and SHA40.fullmatch(revision) and
         type(game_build) is str and bool(game_build),
         "DK_RUNEFORGE_PINNED_REVISION_INVALID")
    root=pathlib.Path(stage_root).resolve()
    source_dir=pathlib.Path(pinned_source["source_dir"]).resolve()
    need(root.is_dir() and source_dir.is_dir() and
         source_dir.is_relative_to(root) and not source_dir.is_symlink(),
         "DK_RUNEFORGE_SOURCE_STAGE_OUTSIDE_ROOT")
    fingerprint=stages.module_dependency_fingerprint(
        [pathlib.Path(__file__),pathlib.Path(pinned.__file__),
         pathlib.Path(stages.__file__)])
    calls=[0]
    def fetch(request,timeout):
        calls[0]+=1
        return (seed.urlopen if transport is None else transport)(
            request,timeout=timeout)
    def execute():
        meta=pinned.pinned_git_blobs(
            revision=revision,paths={"dk":SOURCE_PATH},transport=fetch)["dk"]
        need(0<meta["size"]<=LIMIT,"DK_SOURCE_PINNED_SIZE_LIMIT")
        req=Request(seed.RAW_BASE+revision+"/"+SOURCE_PATH,headers={
            "User-Agent":"SIMC-Secondary-v295-runeforge-source/1.0",
            "Accept":"text/plain"})
        with fetch(req,timeout=90) as response:
            need(response.status==200,"DK_SOURCE_PINNED_HTTP_INVALID")
            raw=response.read(LIMIT+1)
        need(len(raw)==meta["size"] and seed.git_blob(raw)==meta["sha"],
             "DK_SOURCE_PINNED_BLOB_MISMATCH")
        doc=compile_source(raw,game_build=game_build,simc_revision=revision)
        path=root/output
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(canonical(doc)+"\n",encoding="utf8")
    def validate(outputs):
        doc=json.loads(outputs["catalog"].read_text(encoding="utf8"))
        return verify(doc,game_build=game_build,simc_revision=revision)
    output="fresh_source/v295_dk_runeforge_"+revision[:16]+".json"
    stage=stages.execute_stage(
        root=root,stage_id="fresh-dk-runeforge-options-"+revision[:16],
        stage_version="source-pinned-v1",
        inputs={"game_build":game_build,"simc_revision":revision,
                "v275_stage_receipt_sha256":
                    pinned_source["source_stage"]["receipt_sha256"],
                "code_sha256":fingerprint["sha256"]},
        outputs={"catalog":output},execute=execute,validate=validate)
    doc=json.loads((root/output).read_text(encoding="utf8"))
    verify(doc,game_build=game_build,simc_revision=revision)
    return {"status":"PINNED_SIMC_DK_RUNEFORGE_OPTIONS_SEALED",
            "catalog_path":str((root/output).resolve()),
            "manifest_sha256":doc["manifest_sha256"],
            "source_stage_receipt_sha256":stage["receipt_sha256"],
            "items":doc["items"],"game_build":game_build,
            "simc_revision":revision,
            "native_calls":0,"network_calls":calls[0]}
