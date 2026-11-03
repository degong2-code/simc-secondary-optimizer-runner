#!/usr/bin/env python3
"""Extend the ORIGINAL zero-history v216 source collector with missing SimC files.

Reuse sealed v229 generated seeds, sealed v189 unique-gear source, v229 Git
tree/blob verification, v217 execute_stage and v211/v191 parsers. No parallel
season engine, no native/quality claims, no installed-season reference.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.request import Request

import v189_simc_consumable_embellishment_discovery as handlers
import v191_unified_season_data_update as season
import v211_enchant_source_effect_classification as classifier
import v217_stage_execution_engine as stages
import v229_simc_only_source_seed as seed

SCHEMA="v275_pinned_simc_compiler_inputs_v1"
STATUS_PENDING="PINNED_SIMC_COMPILER_INPUTS_SOURCE_PENDING"
OUTPUT_DIR="source/v275_pinned_simc_compiler_inputs"
COMPILER_INPUTS={
    "permanent_enchant.inc":classifier.FRESH_FIXED_PATHS["permanent_enchant.inc"],
    "spell_item_enchantment.inc":classifier.FRESH_FIXED_PATHS[
        "spell_item_enchantment.inc"],
    "spelltext_data.inc":classifier.FRESH_FIXED_PATHS["spelltext_data.inc"],
    "data_enums.hh":classifier.FRESH_FIXED_PATHS["data_enums.hh"],
    "enchants.cpp":classifier.FRESH_FIXED_PATHS["enchants.cpp"],
}
SOURCE_NAMES=(*classifier.FRESH_REQUIRED,"temporary_enchant.inc","gem_data.inc")
OUTPUTS={name:OUTPUT_DIR+"/"+name for name in SOURCE_NAMES}
OUTPUTS["manifest"]=OUTPUT_DIR+"/simc_source_manifest.json"

class SimCCompilerInputBlocked(ValueError):pass

def need(ok,reason):
    if not ok:raise SimCCompilerInputBlocked(reason)

def pending(reason):
    return {"schema":SCHEMA,"status":STATUS_PENDING,"reason":reason,
            "source_dir":None,"manifest_path":None,
            "network_calls_by_stage":0,"native_calls":0,
            "environment_ready":False}

def safe_file(root,relative):
    need(type(relative) is str and bool(relative) and
         not Path(relative).is_absolute() and
         ".." not in Path(relative).parts,
         "V275_SOURCE_PATH_INVALID")
    p=root/relative
    need(p.is_file() and not p.is_symlink() and
         p.resolve().is_relative_to(root),
         "V275_SOURCE_FILE_MISSING_OR_SYMLINK")
    return p

def original_sources(*,stage_root,pinned,consumables,build):
    """Read only original v217-sealed metadata; do not mutate v229/v189."""
    root=Path(stage_root).expanduser().resolve()
    need(root.is_dir() and not root.is_symlink(),
         "V275_SOURCE_STAGE_ROOT_INVALID")
    need(type(pinned) is dict and type(consumables) is dict and
         type(pinned.get("source_stage")) is dict and
         pinned["source_stage"].get("stage_id")==
         "fresh-v229-pinned-simc-generated" and
         pinned["source_stage"].get("status") in (
             "EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED") and
         type(consumables.get("source_stage")) is dict and
         consumables["source_stage"].get("stage_id") in (
            "fresh-v189-v190-consumable-source",
            "fresh-v189-v190-consumable-physical-four-class") and
         consumables["source_stage"].get("status") in (
             "EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED"),
         "V275_PINNED_EXISTING_V229_V189_STAGES_REQUIRED")
    seed_rel=pinned["source_stage"].get("output_paths",{}).get(seed.RECEIPT)
    seed_doc=json.loads(safe_file(root,seed_rel).read_text("utf8"))
    revision=seed_doc.get("simc_revision")
    need(seed_doc.get("schema")==seed.SCHEMA and
         seed_doc.get("simc_generated_build")==build and
         type(revision) is str and seed.REV.fullmatch(revision) is not None and
         seed_doc.get("provenance_tree_blob_authenticated") is True and
         seed_doc.get("receipt_sha256")==pinned.get("simc_receipt_sha256"),
         "V275_PINNED_V229_RECEIPT_IDENTITY_REQUIRED")
    reused={}
    for name in ("gem_data.inc","temporary_enchant.inc"):
        rel=pinned["source_stage"].get("output_paths",{}).get(name)
        raw=safe_file(root,rel).read_bytes()
        record=seed_doc.get("source_files",{}).get(name,{})
        need(record.get("sha256")==seed.digest(raw) and
             record.get("git_blob_sha1")==seed.git_blob(raw),
             "V275_V229_ORIGINAL_GENERATED_BYTES_DRIFT")
        reused[name]=raw
    raw_path=consumables["source_stage"].get(
        "output_paths",{}).get("simc_source")
    unique=safe_file(root,raw_path).read_bytes()
    item_path=consumables["source_stage"].get(
        "output_paths",{}).get("v189")
    discovered=json.loads(safe_file(root,item_path).read_text("utf8"))
    need(discovered.get("schema")==handlers.SCHEMA and
         discovered.get("source",{}).get("commit")==revision and
         discovered["source"].get("sha256")==seed.digest(unique),
         "V275_V189_ORIGINAL_HANDLER_BYTES_OR_REVISION_DRIFT")
    need(handlers.SOURCE.startswith("engine/player/unique_gear_") and
         handlers.SOURCE.endswith(".cpp"),
         "V275_SIMC_UNIQUE_GEAR_SOURCE_PATH_INVALID")
    return root,revision,reused,unique

def pinned_git_blobs(*,revision,paths,transport):
    """The existing v229 Git tree protocol with shared directory reads."""
    cache={}
    def get_tree(tree_sha):
        if tree_sha not in cache:
            # 'transport' wraps the only HTTP counter: count each Git tree
            # request exactly once, just like each raw blob fetch.
            doc=seed._http_json(seed.BASE+tree_sha,transport=transport)
            need(type(doc) is dict and doc.get("truncated") is not True and
                 type(doc.get("tree")) is list,
                 "V275_SIMC_GIT_TREE_INCOMPLETE")
            cache[tree_sha]=doc["tree"]
        return cache[tree_sha]
    found={}
    for name,full_path in paths.items():
        parts=full_path.split("/")
        need(len(parts)>=3 and all(p and p not in (".","..") for p in parts),
             "V275_SIMC_SOURCE_FIXED_PATH_INVALID")
        cursor=revision
        for part in parts[:-1]:
            rows=[r for r in get_tree(cursor)
                  if r.get("path")==part and r.get("type")=="tree"]
            need(len(rows)==1 and type(rows[0].get("sha")) is str and
                 seed.HEX.fullmatch(rows[0]["sha"]),
                 "V275_SIMC_TREE_DIRECTORY_MISSING:"+part)
            cursor=rows[0]["sha"]
        rows=[r for r in get_tree(cursor)
              if r.get("path")==parts[-1] and r.get("type")=="blob"]
        need(len(rows)==1 and type(rows[0].get("sha")) is str and
             seed.HEX.fullmatch(rows[0]["sha"]) and
             type(rows[0].get("size")) is int and
             0<rows[0]["size"]<=classifier.MAX_SOURCE,
             "V275_SIMC_SOURCE_BLOB_NOT_PINNED:"+name)
        found[name]={"path":full_path,"sha":rows[0]["sha"],
                     "size":rows[0]["size"]}
    return found

def reuse_verified_first_party_bytes(*,root,revision,build,reused,unique):
    """Reuse v275's prior verified Git blobs if only the DB2 item scope grew.

    v279 changes v190's *physical item candidates*, not the pinned SimC
    revision or unique_gear.cpp. Revalidate original v217 output bytes
    against its immutable completed receipt and exact present upstream bytes
    rather than downloading five identical SimC files again.
    """
    stage_id="fresh-pinned-v211-and-permanent-inputs"
    receipt_path=root/".stage_receipts"/(stage_id+".json")
    if not receipt_path.is_file():
        return None
    try:
        paths,_=stages._safe_paths(root,stage_id,OUTPUTS)
        old=stages._read_receipt(receipt_path)
        need(old.get("status")=="COMPLETE"
             and old.get("stage_id")==stage_id
             and old.get("stage_version")=="v275-git-tree-reuse-v1"
             and old.get("output_paths")=={
                 key:relative for key,(relative,_) in paths.items()},
             "V275_HISTORICAL_STAGE_IDENTITY_INVALID")
        total=stages._verify_outputs(old,paths)
        folder=root/OUTPUT_DIR
        manifest=json.loads((folder/"simc_source_manifest.json")
                            .read_text("utf8"))
        classifier.load_fresh_sources(
            folder,manifest,game_build=build,simc_revision=revision)
        need((folder/"unique_gear.cpp").read_bytes()==unique
             and all((folder/name).read_bytes()==raw
                     for name,raw in reused.items()),
             "V275_HISTORICAL_SIMC_INPUT_BYTES_DIFFER")
        for name,kind in (("temporary_enchant.inc","temporary_enchant"),
                          ("gem_data.inc","gem_property"),
                          ("permanent_enchant.inc","permanent_enchant")):
            need(season.parse_generated(
                kind,(folder/name).read_bytes())["source_build"]==build,
                "V275_HISTORICAL_GENERATED_BUILD_INVALID")
        stage=stages._summary(old,"REUSED_VERIFIED",False,False,0,total)
    except (stages.StageExecutionBlocked,SimCCompilerInputBlocked,
            classifier.SourceBlocked,season.CatalogBlocked,
            OSError,ValueError,KeyError,TypeError) as exc:
        raise SimCCompilerInputBlocked(
            "V275_HISTORICAL_SOURCE_REUSE_INVALID:"
            +str(exc).split(":",1)[0]) from exc
    return {"schema":SCHEMA,"status":"PINNED_V211_AND_GENERATED_SOURCES_SEALED",
            "source_dir":str(folder.resolve()),
            "manifest_path":str((folder/"simc_source_manifest.json").resolve()),
            "simc_revision":revision,"source_stage":stage,
            "network_calls_by_stage":0,"native_calls":0,
            "source_season_verified":False,
            "user_options_approved":False,"environment_ready":False}


def collect(*,stage_root,build,pinned_simc,consumables,transport=None):
    """One incremental v217 stage; return PENDING for missing producers.

    Current v189 only knows unique_gear_midnight.cpp; other expansion
    registrations require source-producer work, never guessed from names.
    """
    if not (type(pinned_simc) is dict and
            pinned_simc.get("source_dir") and
            type(consumables) is dict and consumables.get("candidate_path")):
        return pending("V275_V229_OR_V189_SOURCE_PRODUCER_PENDING")
    root,revision,reused,unique=original_sources(
        stage_root=stage_root,pinned=pinned_simc,
        consumables=consumables,build=build)
    cached=reuse_verified_first_party_bytes(
        root=root,revision=revision,build=build,
        reused=reused,unique=unique)
    if cached is not None:
        return cached
    # Fresh v279 physical candidate scope is a successor receipt, never
    # a rewrite of v275's original immutable source-stage identity.
    newer=consumables["source_stage"]["stage_id"]==(
        "fresh-v189-v190-consumable-physical-four-class")
    compiler_stage_id=("fresh-pinned-v211-from-four-subclass-consumables"
                       if newer else
                       "fresh-pinned-v211-and-permanent-inputs")
    compiler_version=("v275-git-tree-reuse-four-class-v1"
                      if newer else "v275-git-tree-reuse-v1")
    source_paths={**COMPILER_INPUTS,
                  "unique_gear.cpp":handlers.SOURCE}
    code=stages.module_dependency_fingerprint([
        Path(__file__),Path(seed.__file__),Path(classifier.__file__),
        Path(season.__file__),Path(stages.__file__)])
    calls=[0]
    def fetch(req,timeout):
        calls[0]+=1
        return (seed.urlopen if transport is None else transport)(
            req,timeout=timeout)
    def execute():
        # v229-proven original v189 source is additionally checked against
        # the actual pinned tree blob; never silently trust a name/URL alone.
        meta=pinned_git_blobs(
            revision=revision,paths=source_paths,transport=fetch)
        need(seed.git_blob(unique)==meta["unique_gear.cpp"]["sha"] and
             len(unique)==meta["unique_gear.cpp"]["size"],
             "V275_V189_SOURCE_NOT_IN_PINNED_GIT_TREE")
        contents={"unique_gear.cpp":unique,**reused}
        for name,path in COMPILER_INPUTS.items():
            row=meta[name]
            need(row["size"]<=classifier.MAX_SOURCE,
                 "V275_SOURCE_SIZE_LIMIT:"+name)
            req=Request(seed.RAW_BASE+revision+"/"+path,headers={
                "User-Agent":"SIMC-Secondary-v275-source-collector/1.0",
                "Accept":"text/plain"})
            with fetch(req,timeout=90) as response:
                need(response.status==200,
                     "V275_PINNED_SOURCE_HTTP_NON_200:"+name)
                raw=response.read(classifier.MAX_SOURCE+1)
            need(len(raw)==row["size"] and
                 seed.git_blob(raw)==row["sha"],
                 "V275_PINNED_SOURCE_BLOB_SHA_MISMATCH:"+name)
            contents[name]=raw
        manifest={"schema":classifier.FRESH_SOURCE_SCHEMA,
                  "game_build":build,"simc_revision":revision,"files":{}}
        for name in classifier.FRESH_REQUIRED:
            raw=contents[name]
            manifest["files"][name]={
                "source_path":source_paths[name],
                "size_bytes":len(raw),
                "sha256":seed.digest(raw),
                "git_blob_sha1":seed.git_blob(raw)}
        for name,raw in contents.items():
            file=root/OUTPUTS[name]
            file.parent.mkdir(parents=True,exist_ok=True)
            file.write_bytes(raw)
        (root/OUTPUTS["manifest"]).write_text(
            json.dumps(manifest,sort_keys=True,ensure_ascii=False,
                       indent=2,allow_nan=False)+"\n",encoding="utf8")
    def validate(files):
        manifest=json.loads(files["manifest"].read_text("utf8"))
        source_dir=files["manifest"].parent
        classifier.load_fresh_sources(
            source_dir,manifest,game_build=build,simc_revision=revision)
        for name in season.GENERATED.values():
            parsed=season.parse_generated(
                {v:k for k,v in season.GENERATED.items()}[name],
                files[name].read_bytes())
            need(parsed["source_build"]==build,
                 "V275_GENERATED_SOURCE_BUILD_DRIFT:"+name)
        return True
    try:
        stage=stages.execute_stage(
            root=root,stage_id=compiler_stage_id,
            stage_version=compiler_version,
            inputs={"game_build":build,"simc_revision":revision,
                    "v229_source_stage_sha256":
                        pinned_simc["source_stage"]["receipt_sha256"],
                    "v189_source_stage_sha256":
                        consumables["source_stage"]["receipt_sha256"],
                    "v229_seed_receipt_sha256":
                        pinned_simc["simc_receipt_sha256"],
                    "code_sha256":code["sha256"]},
            outputs=OUTPUTS,execute=execute,validate=validate)
    except (seed.SimCSourceBlocked,SimCCompilerInputBlocked,
            classifier.SourceBlocked,season.CatalogBlocked,
            OSError,ValueError) as exc:
        # A sealed byte tamper is not a missing source: keep integrity fail
        # visible. Network/unknown compiler format stays pending, not READY.
        reason=str(exc).split(":",1)[0]
        if reason in ("STAGE_OUTPUT_HASH_MISMATCH",
                      "STAGE_INPUT_FINGERPRINT_MISMATCH",
                      "V275_V189_SOURCE_NOT_IN_PINNED_GIT_TREE",
                      "V275_PINNED_SOURCE_BLOB_SHA_MISMATCH"):
            raise SimCCompilerInputBlocked(reason) from exc
        return {**pending(reason),"network_calls_by_stage":calls[0]}
    folder=root/OUTPUT_DIR
    return {"schema":SCHEMA,"status":"PINNED_V211_AND_GENERATED_SOURCES_SEALED",
            "source_dir":str(folder.resolve()),
            "manifest_path":str((folder/"simc_source_manifest.json").resolve()),
            "simc_revision":revision,
            "source_stage":{k:v for k,v in stage.items() if k!="result"},
            "network_calls_by_stage":calls[0],"native_calls":0,
            "source_season_verified":False,
            "user_options_approved":False,"environment_ready":False}
