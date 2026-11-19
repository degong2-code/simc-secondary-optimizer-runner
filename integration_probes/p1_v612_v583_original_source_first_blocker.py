#!/usr/bin/env python3
"""v612: one real 70961 source-only v583 first-blocker diagnosis; NO Native.

Reuse original v216.collect_wago_new_season_source and all its stage seals.
Fresh workspace because prior one-shot Windows M1/M2 ephemeral stage bytes
were not included in artifact. Do not forge product_input or E=0.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v216_environment_build_coordinator as build
from p1_v524_m1_m2_source_owner_once import EphemeralActionsCredentials,bounded_code

BUILD="12.1.5.70961"
REV="9933ffb946fb55b1fa66657b848f519ac19006e1"
SCHEMA="p1_v612_real_70961_v583_original_first_missing_dependency_v1"
DEPS={
    "wago":"source_stage",
    "v254_gear":"fresh_ordinary_gear",
    "v280_item_effect":"fresh_consumable_item_spell_source",
    "v281_spell_effect":"fresh_consumable_simc_effect_relation",
    "v275_simc_compiler":"fresh_pinned_v211_source",
    "v256_full_simc":"fresh_lazy_full_pinned_simc_item_source",
    "v583_permanent_quality":"fresh_permanent_enchant_item_source",
    "season_join":"season_join",
}


def run(out):
    folder=Path(out).resolve()
    folder.mkdir(parents=True,exist_ok=True)
    target=folder/"V612_REAL_70961_V583_SOURCE_BLOCKER.json"
    doc={"schema":SCHEMA,"status":"STARTED",
        "game_build":BUILD,"simc_revision":REV,
        "normal_v216_source_collector_used":False,
        "exact_Policy_A_product_input_not_fabricated":True,
        "actual_enchant_ui_promotion":False,
        "actual_enchant_native_calls":0,
        "user_dps_native_calls":0,
        "source_only_not_user_environment_installed":True}
    def save():
        target.write_text(json.dumps(doc,ensure_ascii=False,indent=2,
            sort_keys=True,default=str,allow_nan=False)+"\n",encoding="utf8")
    save()
    try:
        if (os.getenv("SIMC_PINNED_SOURCE_COMMIT")!=REV
            or os.getenv("SIMC_PINNED_GAME_BUILD")!=BUILD):
            raise RuntimeError("V612_SOURCE_BUILD_REVISION_PIN_MISMATCH")
        cred=EphemeralActionsCredentials().load()
        if cred is None:
            doc["status"]="PENDING_SEASON_SOURCE_CREDENTIALS"
            save()
            return 2
        with tempfile.TemporaryDirectory(prefix="v612-wago-",dir=folder) as temp:
            result=build.collect_wago_new_season_source(
                sessions_root=Path(temp)/"runs",
                expected_game_build=BUILD,
                credentials=cred,
                simc_revision_hint=REV,
                representative_request={
                    "class":"paladin","spec":"retribution","target_ilevel":334},
                g_probe_character={"race":"dwarf"})
            doc["normal_v216_source_collector_used"]=True
            doc["collector_status"]=result.get("status")
            doc["network_calls_by_stage"]=result.get("network_calls_by_stage")
            doc["native_calls"]=result.get("native_calls")
            for label,key in DEPS.items():
                val=result.get(key) or {}
                if key=="source_stage":
                    val=result.get("source_stage") or {}
                row={"status":val.get("status"),"reason":val.get("reason"),
                     "stage_status":(val.get("source_stage") or {}).get("status"),
                     "source_stage_receipt_sha256":
                         (val.get("source_stage") or {}).get("receipt_sha256"),
                     "network_calls_by_stage":val.get("network_calls_by_stage")}
                if label=="season_join":
                    # v163's signed candidate has auto_source_scope INSIDE
                    # the file; its outward collection result exposes
                    # the same authenticated data as source_scope.
                    row["expansion_id"]=(
                        val.get("source_scope") or {}).get("expansion_id")
                    row["season_source_scope"]=(
                        val.get("source_scope") or {}).get("source_basis")
                doc[label]=row
            v583=result.get("fresh_permanent_enchant_item_source") or {}
            doc["v583_first_blocker"]=v583.get("reason")
            doc["v583_source_counts"]=v583.get("counts")
            doc["v583_exact_candidate_present"]=(
                v583.get("status")==
                    "PERMANENT_ENCHANT_EXACT_WAGO_SIMC_SOURCE_ONLY"
                and type(v583.get("candidate_path")) is str)
            if doc["v583_exact_candidate_present"]:
                # Verify exact original stage output is genuinely sealed; do
                # not convert SOURCE_ONLY to a published user option.
                p=Path(v583["candidate_path"])
                data=json.loads(p.read_text("utf8"))
                doc["v583_exact_game_build"]=data.get("game_build")
                doc["v583_original_match_count"]=len(data.get("matches") or [])
                doc["status"]="PASS_REAL_V583_SOURCE_ONLY"
            else:
                doc["status"]="PENDING_REAL_V583_SOURCE_FIRST_BLOCKER_IDENTIFIED"
            save()
            return 0
    except Exception as exc:
        doc["status"]="BLOCKED_"+type(exc).__name__
        doc["first_blocker"]=bounded_code(exc)
        save()
        return 2


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    sys.exit(run(args.out))


if __name__=="__main__":
    main()
