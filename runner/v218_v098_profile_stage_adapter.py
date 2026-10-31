#!/usr/bin/env python3
"""Adapter to existing v098 builder; no new profile generator."""
from __future__ import annotations
import functools,hashlib,json,pathlib
import v098_target_user_scenario_bootstrap as bootstrap
import v217_stage_execution_engine as engine

SCHEMA="v218_v098_profile_stage_adapter_v1"
STAGE_ID="v098_target_profile"
STAGE_VERSION="v098_profile_stage_v1"
OUTPUTS={"profile":"profile.simc","scenario":"scenario.json",
         "fillers":"fillers.json","manifest":"manifest.json",
         "bootstrap_result":"v098_bootstrap_result.json"}

def _sha_file(path):
    path=pathlib.Path(path).expanduser()
    if not path.is_file() or path.is_symlink():
        raise engine.StageExecutionBlocked("V218_PROFILE_DATA_INPUT_MISSING")
    raw=path.read_bytes()
    return {"sha256":hashlib.sha256(raw).hexdigest(),"size":len(raw)}

@functools.lru_cache(maxsize=1)
def _code_contract():
    api_file=pathlib.Path(__file__).with_name("v113_local_web_api.py")
    return engine.module_dependency_fingerprint([__file__,api_file])

def profile_data_fingerprints(user,*,independent_334=False,
        independent_target_level=False,source_first_stage=False,
        current_season_product=False,source_catalog_path=None):
    character=user.get("character") if type(user) is dict else None
    key=((character.get("class"),character.get("spec"))
         if type(character) is dict else None)
    data={}
    pure_mode=bool(key is not None and
        (key in bootstrap.PURE_PRODUCT_SPECS or independent_334 or
         independent_target_level or source_first_stage or current_season_product))
    catalog=None
    if pure_mode:
        catalog=bootstrap.pure.catalog()
        data["pure_season_catalog"]=_sha_file(bootstrap.pure.DEFAULT_CATALOG)
    source_free=bool(pure_mode and catalog is not None and
                     "/".join(key) in catalog["specializations"])
    if source_first_stage or current_season_product:
        data["season_gear"]=_sha_file(bootstrap.source_first.gear.DEFAULT)
        data["season_tier"]=_sha_file(bootstrap.source_first.TIER_PATH)
        data["season_budget"]=_sha_file(bootstrap.source_first.BUDGET_PATH)
    if source_catalog_path is not None:
        data["v213_source_catalog"]=_sha_file(source_catalog_path)
    if not source_free and key is not None:
        entry=next((row for row in bootstrap.common.metadata.SOURCE_BACKED
                    if row.key==key),None)
        if entry is not None:
            data["legacy_profile_fixture"]=_sha_file(
                bootstrap.common.FIXTURES/entry.source_fixture)
    return {name:data[name] for name in sorted(data)}

def session_identity(user,*,independent_334=False,independent_target_level=False,
        source_first_stage=False,current_season_product=False,source_catalog_path=None):
    code=_code_contract()
    payload={"schema":SCHEMA,"stage_id":STAGE_ID,"stage_version":STAGE_VERSION,
        "code_sha256":code["sha256"],"code_module_count":code["module_count"],
        "data_fingerprints":profile_data_fingerprints(
            user,independent_334=independent_334,
            independent_target_level=independent_target_level,
            source_first_stage=source_first_stage,
            current_season_product=current_season_product,
            source_catalog_path=source_catalog_path),
        "mode":{"independent_334":bool(independent_334),
                "independent_target_level":bool(independent_target_level),
                "source_first_stage":bool(source_first_stage),
                "current_season_product":bool(current_season_product)}}
    return {**payload,"identity_sha256":
            engine.digest(engine.canonical(payload).encode("utf8"))}

def _inputs(identity):
    return {"session_identity_sha256":
            engine.digest(engine.canonical(identity).encode("utf8")),
            "profile_stage_identity_sha256":
            identity["profile_stage"]["identity_sha256"]}

def _validate(paths,user):
    try:
        manifest=json.loads(paths["manifest"].read_text(encoding="utf8"))
        json.loads(paths["scenario"].read_text(encoding="utf8"))
        json.loads(paths["fillers"].read_text(encoding="utf8"))
        bootstrap_result=json.loads(paths["bootstrap_result"].read_text(encoding="utf8"))
        if (type(manifest) is not dict or type(bootstrap_result) is not dict or
            bootstrap_result.get("schema")!=bootstrap.SCHEMA or
            bootstrap_result.get("generated_manifest")!=str(paths["manifest"])):
            return False
        plan=bootstrap.entry.run_manifest(paths["manifest"],plan_only=True)
        character=user.get("character")
        if type(character) is dict:
            if plan.get("class")!=character.get("class") or plan.get("spec")!=character.get("spec"):
                return False
        return True
    except Exception:return False

def build_or_reuse(*,user,session_folder,binary,revision,static_cache,
        independent_334=False,independent_target_level=False,
        current_season_product=False,source_catalog_path=None):
    folder=pathlib.Path(session_folder).expanduser().resolve()
    generated=folder/"generated"
    generated.mkdir(parents=True,exist_ok=True)
    identity_path=folder/"V106_SESSION_IDENTITY.json"
    if not identity_path.is_file() or identity_path.is_symlink():
        raise engine.StageExecutionBlocked("V218_SESSION_IDENTITY_MISSING")
    try:identity=json.loads(identity_path.read_text(encoding="utf8"))
    except (OSError,ValueError,TypeError) as exc:
        raise engine.StageExecutionBlocked("V218_SESSION_IDENTITY_INVALID") from exc
    if type(identity) is not dict or type(identity.get("profile_stage")) is not dict:
        raise engine.StageExecutionBlocked("V218_PROFILE_STAGE_IDENTITY_MISSING")
    paths={name:generated/relative for name,relative in OUTPUTS.items()}
    def execute():
        result=bootstrap.build(user,generated,binary,revision,static_cache,
            independent_334=independent_334,
            independent_target_level=independent_target_level,
            current_season_product=current_season_product,
            source_catalog_path=(source_catalog_path if current_season_product else None))
        encoded=json.dumps(result,sort_keys=True,ensure_ascii=False,
                           indent=2,allow_nan=False)+"\n"
        bootstrap.put_once(paths["bootstrap_result"],encoded)
        return result
    result=engine.execute_stage(root=generated,stage_id=STAGE_ID,
        stage_version=STAGE_VERSION,inputs=_inputs(identity),outputs=OUTPUTS,
        execute=execute,validate=lambda output_paths:_validate(output_paths,user))
    bootstrap_result=(result["result"] if result["result"] is not None else
        json.loads(paths["bootstrap_result"].read_text(encoding="utf8")))
    summary={"schema":SCHEMA,"stage_id":STAGE_ID,"status":result["status"],
        "executed":result["executed"],"reused":result["reused"],
        "recovered":result["recovered"],"input_fingerprint":result["input_fingerprint"],
        "receipt_sha256":result["receipt_sha256"],"output_count":result["output_count"],
        "output_bytes":result["output_bytes"],"receipt_writes":result["receipt_writes"],
        "native_calls":0,"network_calls":0,"cache_mutations":0}
    return bootstrap_result,summary

def verify_existing(session_folder,identity):
    if type(identity) is not dict or type(identity.get("profile_stage")) is not dict:
        raise engine.StageExecutionBlocked("V218_PROFILE_STAGE_IDENTITY_MISSING")
    folder=pathlib.Path(session_folder).expanduser().resolve()
    return engine.verify_stage(root=folder/"generated",stage_id=STAGE_ID,
        stage_version=STAGE_VERSION,inputs=_inputs(identity),outputs=OUTPUTS)
