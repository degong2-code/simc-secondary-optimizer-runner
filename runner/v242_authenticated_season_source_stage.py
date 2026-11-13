#!/usr/bin/env python3
"""v242: existing v155 Blizzard/WCL probe as a sealed normal Build stage.

No new provider implementation and no second Environment Builder. Exact
provider request identity, immutable stage receipts, and no credential bytes
in artifacts/cache keys. This report is NOT proof of current raid/rotation.
"""
from __future__ import annotations

import json
import pathlib
import re

import v155_season_api_probe as probe
import v217_stage_execution_engine as stages

SCHEMA="v242_authenticated_season_discovery_stage_v1"
BUILD_RE=re.compile(r"[0-9]+(?:\.[0-9]+){3}\Z")
FIELDS=("BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
        "WCL_CLIENT_ID","WCL_CLIENT_SECRET")

class DiscoveryBlocked(ValueError):pass

def need(ok,code):
    if not ok:raise DiscoveryBlocked(code)

def collect(*, stage_root, expected_game_build, credentials,
            transport=None):
    """Return explicit pending without credentials; no prior-season seed.

    v155 collects bounded WCL zones with expansion IDs (not active-season
    proof); v163 same-build sources must establish an unambiguous current
    scope. Received HTTP provenance and season membership remain separate.
    """
    need(type(expected_game_build) is str and
         BUILD_RE.fullmatch(expected_game_build) is not None,
         "V242_EXPECTED_GAME_BUILD_REQUIRED")
    need(type(credentials) is dict and set(credentials)==set(FIELDS)
         and all(type(credentials[x]) is str for x in FIELDS),
         "V242_CREDENTIAL_INPUT_INVALID")
    configured={key for key in FIELDS if credentials[key]}
    if not configured:
        return {"schema":SCHEMA,"status":"AUTHENTICATED_SEASON_CREDENTIALS_MISSING",
                "source_report_path":None,"stage":None,
                "network_calls_by_stage":0,
                "authenticated_provider_response":False,
                "current_season_membership_verified":False}
    need(configured==set(FIELDS),"V242_INCOMPLETE_BLIZZARD_WCL_CREDENTIAL_PAIRS")
    base=pathlib.Path(stage_root).expanduser()
    need(base.is_dir() and not base.is_symlink(),
         "V242_STAGE_ROOT_MISSING_OR_SYMLINK")
    # Source/provenance only: do not hash or persist credentials into cache.
    fingerprint=stages.module_dependency_fingerprint(
        [pathlib.Path(probe.__file__),pathlib.Path(stages.__file__)])
    relative="source/season_api_report.json"
    path=base/relative
    def execute():
        options={} if transport is None else {"transport":transport}
        report=probe.run_probe(
            credentials["BLIZZARD_CLIENT_ID"],
            credentials["BLIZZARD_CLIENT_SECRET"],
            credentials["WCL_CLIENT_ID"],
            credentials["WCL_CLIENT_SECRET"],**options)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(report,sort_keys=True,indent=2,
            ensure_ascii=False,allow_nan=False)+"\n",encoding="utf8")
    def validate(outputs):
        doc=json.loads(outputs["report"].read_text(encoding="utf8"))
        return (doc.get("schema")==probe.SCHEMA
            and doc.get("mode")=="LIVE_AUTHENTICATED_BOUNDED"
            and doc.get("native_simc_calls")==0
            and doc.get("item_catalog_generated") is False
            and doc.get("season_loot_complete") is False
            and doc.get("blizzard",{}).get("requests")==4
            and doc.get("wcl",{}).get("requests") in (1,2)
            and "access_token" not in json.dumps(doc)
            and all(credentials[k] not in outputs["report"].read_text("utf8")
                    for k in ("BLIZZARD_CLIENT_SECRET","WCL_CLIENT_SECRET")))
    try:
        stage=stages.execute_stage(
            root=base,stage_id="fresh-v155",stage_version="1",
            inputs={"expected_game_build":expected_game_build,
                    "provider_contract":"v155-blizzard-wcl-fixed-bounded",
                    "code_sha256":fingerprint["sha256"]},
            outputs={"report":relative},execute=execute,validate=validate)
    except stages.StageExecutionBlocked as exc:
        raise DiscoveryBlocked("V242_SOURCE_RECEIPT_BLOCKED:"+str(exc)) from exc
    doc=json.loads(path.read_text(encoding="utf8"))
    joined=(doc.get("wcl",{}).get("status")
            =="ZONES_WITH_JOURNAL_IDS_RETURNED"
            and doc.get("blizzard",{}).get("endpoints",{})
              .get("keystone_season_index",{}).get("status")=="HTTP_200")
    # The probe is explicitly scoped to Midnight zones; a good HTTP
    # response does not establish what raid/rotation is in season.
    return {"schema":SCHEMA,
        "status":("AUTHENTICATED_SOURCE_DISCOVERED_SEASON_JOIN_PENDING"
                  if joined else
                  "AUTHENTICATED_SOURCE_INCOMPLETE_SEASON_JOIN_PENDING"),
        "source_report_path":str(path.resolve()),
        "stage":{k:v for k,v in stage.items() if k!="result"},
        "network_calls_by_stage":(
            doc["blizzard"]["requests"]+doc["wcl"]["requests"]+
            2 if stage["executed"] else 0),
        "authenticated_provider_response":True,
        "current_season_membership_verified":False,
        "provider_zone_scope":"ALL_WCL_EXPANSIONS_PENDING_DB2_JOIN",
        "season_join_ready":bool(joined),
        "native_calls":0,
        "environment_installed":False}
