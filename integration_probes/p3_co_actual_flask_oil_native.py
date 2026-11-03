#!/usr/bin/env python3
"""P3-CO: one real SimC F/O pair via existing v269/v278 (max 3 Native).

The physical item→spell→SimC ID joins are REUSED_HISTORY from P3-CN
Actions #41661212083, build 12.1.5.70575, revision 710c2408b.
Do not infer highest quality, hand applicability or F/O budget approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from runner import v269_simc_chmv_effect_snapshot as snapshot
from runner import v278_sealed_simc_consumable_native_pair as pair

SCHEMA="p3_co_original_native_f_o_source_only_v1"
REVISION="710c2408bfd3ae4df71b8cd55cdf01f63fd6c926"
BUILD="12.1.5.70575"
PROFILE="integration_probes/fixtures/v084_upstream_mid2_mage_frost_reference.simc"
UPSTREAM_BLOB="b787824a95020a7cdd0934ed5e004695726db138"
PROOF_RUN="https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/41661212083"
CASES=(
    {"kind":"flask","item_id":241326,
     "token":"flask_of_the_shattered_sun_2","quality_rank":2},
    {"kind":"temporary_enchant","item_id":243736,
     "enchant_id":8054,"effect_spell_id":1237001,
     "token":"main_hand:oil_of_dawn_2","quality_rank":2},
)
# Different exact-source candidates run separately without rechecking
# already-measured options. Each two-option case shares one baseline.
FOLLOWUP_CASES=(
    {"kind":"flask","item_id":241327,
     "token":"flask_of_the_shattered_sun_1","quality_rank":1},
    {"kind":"temporary_enchant","item_id":243734,
     "enchant_id":8052,"effect_spell_id":1237006,
     "token":"main_hand:thalassian_phoenix_oil_2","quality_rank":2},
)
MAX_NEW_NATIVE=3

def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def profile_from_source(raw,*,cases=CASES):
    if git_blob(raw)!=UPSTREAM_BLOB:
        raise ValueError("P3_CO_PINNED_SOURCE_PROFILE_SHA_DRIFT")
    text=raw.decode("utf8")
    needle="actions.precombat=arcane_intellect\n"
    if text.count(needle)!=1:
        raise ValueError("P3_CO_PRECOMBAT_HEADER_MISSING")
    profile=text.replace(needle,
        "actions.precombat=flask\n"
        "actions.precombat+=/arcane_intellect\n")
    for candidate in cases:
        snapshot.prepare(profile=profile,kind=candidate["kind"],
                         token=candidate["token"])
    return profile

def run(*,root,source,binary,simc_revision=REVISION,measure=None,
        cases=CASES,mode="primary"):
    if simc_revision!=REVISION:
        raise ValueError("P3_CO_PINNED_SIMC_REVISION_REQUIRED")
    if ((cases,mode) not in ((CASES,"primary"),(FOLLOWUP_CASES,"followup"))):
        raise ValueError("P3_CO_UNSUPPORTED_NATIVE_SOURCE_CASES")
    folder=Path(root).resolve()
    folder.mkdir(parents=True,exist_ok=True)
    profile=profile_from_source(Path(source).read_bytes(),cases=cases)
    path=folder/"source_profile.simc"
    if path.exists():
        if path.read_text("utf8")!=profile:
            raise ValueError("P3_CO_EXISTING_SOURCE_PROFILE_DRIFT")
    else:
        path.write_text(profile,encoding="utf8")
    measure=measure or pair.measure
    results=[]
    total=0
    for candidate in cases:
        try:
            original=measure(stage_root=folder,
                             source_profile_path=path,
                             binary=binary,simc_revision=simc_revision,
                             kind=candidate["kind"],token=candidate["token"])
        except (pair.NativePairBlocked,OSError,ValueError) as exc:
            original={"status":"NATIVE_OBSERVATION_EXCEPTION",
                      "native_error":str(exc),"new_native_calls":0}
        count=original["new_native_calls"]
        if type(count) is not int or count<0:
            raise ValueError("P3_CO_NATIVE_CALL_COUNT_INVALID")
        total+=count
        if total>MAX_NEW_NATIVE:
            raise ValueError("P3_CO_NATIVE_BUDGET_EXCEEDED")
        results.append({
            "item":candidate,"status":original["status"],
            "observed_rating_delta":(original.get("observed") or {}).get(
                "observed_rating_delta"),
            "static_CHMV_candidate":original.get("static_CHMV_candidate"),
            "native_case_receipts":original.get("native_case_receipts",[]),
            "native_error":original.get("native_error"),
            "native_log_excerpt":original.get("native_log_excerpt"),
            "new_native_calls":count,
            "same_effect_quality_group_verified":False,
            "weapon_and_hand_applicability_verified":False,
            "user_selectable":False})
        if original["status"] not in (
           "SIMC_STATIC_CHMV_EFFECT_OBSERVED_NOT_ADMITTED",
           "SIMC_CONDITIONAL_OR_NONSTATIC_EFFECT_PENDING"):
            break
    outcome=("OBSERVATIONS_SOURCE_ONLY" if
            len(results)==len(cases) and all(row["status"] in (
                "SIMC_STATIC_CHMV_EFFECT_OBSERVED_NOT_ADMITTED",
                "SIMC_CONDITIONAL_OR_NONSTATIC_EFFECT_PENDING")
                for row in results)
            else "NATIVE_SOURCE_PROBE_FAILED")
    receipt={
        "schema":SCHEMA,"game_build":BUILD,"simc_revision":REVISION,
        "observation_mode":mode,
        "prior_source_proof":PROOF_RUN,
        "source_profile_git_blob_sha1":UPSTREAM_BLOB,
        "source_profile_sha256":hashlib.sha256(
            profile.encode("utf8")).hexdigest(),
        "max_new_native_calls":MAX_NEW_NATIVE,"new_native_calls":total,
        "observations":results,"F":None,"O":None,"B":None,"T":None,
        "quality_group_verified":False,"oil_game_applicability_verified":False,
        "environment_ready":False,"ui_auto_registered":False,
        "status":outcome}
    (folder/"P3_CO_RECEIPT.json").write_text(
        json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2,
                   allow_nan=False)+"\n",encoding="utf8")
    return receipt

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--binary",type=Path,required=True)
    p.add_argument("--source",type=Path,default=Path(PROFILE))
    p.add_argument("--out",type=Path,default=Path("out/p3-co"))
    p.add_argument("--mode",choices=("primary","followup"),default="primary")
    args=p.parse_args()
    result=run(root=args.out,source=args.source,binary=args.binary,
               cases=CASES if args.mode=="primary" else FOLLOWUP_CASES,
               mode=args.mode)
    for row in result["observations"]:
        print("P3_CO_ACTUAL_NATIVE",row["item"]["kind"],
              "item",row["item"]["item_id"],"status",row["status"],
              "delta",json.dumps(row["observed_rating_delta"],sort_keys=True),
              "new_native",row["new_native_calls"],flush=True)
    print("P3_CO_FINAL_STATUS",result["status"],
          "new_native",result["new_native_calls"],
          "F_O_UNADMITTED",flush=True)
    if result["status"]=="NATIVE_SOURCE_PROBE_FAILED":
        raise SystemExit(3)
if __name__=="__main__":
    main()
