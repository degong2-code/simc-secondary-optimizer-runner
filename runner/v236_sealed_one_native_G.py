#!/usr/bin/env python3
"""One explicit Native subprocess for a byte-sealed v233 SimC-source probe.

Consumes prior v235's immutable small source-only receipt/profile. Does NOT
redownload item_data.inc, read a prior season database or restore a static
cache. Reuses v234.observe -> v046 for exact Native static ratings.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

try:
    from . import v229_simc_only_source_seed as source
    from . import v233_source_only_G_probe_profile as compiler
    from . import v234_source_only_one_native_G as native
except ImportError:
    import v229_simc_only_source_seed as source
    import v233_source_only_G_probe_profile as compiler
    import v234_source_only_one_native_G as native

SCHEMA="v236_one_real_sealed_source_native_G_probe_v1"
HEX64=re.compile("[a-f0-9]{64}\\Z")


class SealedNativeBlocked(ValueError):pass


def need(ok,reason):
    if not ok:raise SealedNativeBlocked(reason)


def digest(raw):return hashlib.sha256(raw).hexdigest()


def check(profile_bytes,receipt,*,expected_source_revision,expected_game_build):
    need(type(receipt) is dict and receipt.get("schema")==compiler.SCHEMA and
         receipt.get("status")=="EXACT_SIMC_SOURCE_PROFILE_PREPARED_NOT_EXECUTED" and
         receipt.get("receipt_sha256")==source.digest(source.canonical({
             k:v for k,v in receipt.items() if k!="receipt_sha256"
             }).encode("utf8")) and
         receipt.get("G") is None and receipt.get("environment_ready") is False
         and receipt.get("native_calls")==0,
         "V236_V233_SOURCE_SEALED_RECEIPT_INVALID")
    need(type(profile_bytes) is bytes and 0<len(profile_bytes)<=10000 and
         digest(profile_bytes)==receipt["physical_profile_sha256"] and
         len(profile_bytes)==receipt["physical_profile_bytes"],
         "V236_PHYSICAL_PROFILE_BYTES_NOT_SEALED")
    try:
        text=profile_bytes.decode("utf8")
    except UnicodeError as exc:
        raise SealedNativeBlocked("V236_PROFILE_NON_UTF8") from exc
    contract=compiler.contracts.lookup(receipt["class"],receipt["spec"])
    need(contract is not None,"V236_DPS_SPEC_UNKNOWN")
    items=receipt["selected_G_slot_ids"]
    need(type(items) is dict and len(items) in (13,14) and
         not set(items)&{"trinket1","trinket2"} and
         set(items)<=set(compiler.contracts.SLOT_ORDER) and
         len(set(items.values()))==len(items) and
         all(type(n) is int and n>0 for n in items.values()),
         "V236_SOURCE_G_SLOT_IDS_INVALID")
    expected=[
        "# v233 generated, SimC-only physical G measurement candidate",
        receipt["class"]+"="+compiler.NAME,
        "level="+str(receipt["level"]),
        "race="+receipt["race"],"spec="+receipt["spec"],
        "position="+contract["position"]]
    lines=text.splitlines()
    need(lines[:len(expected)]==expected and
         text.endswith("\n"),
         "V236_SOURCE_CHARACTER_PROFILE_CHANGED")
    remainder=lines[len(expected):]
    if receipt["talents_supplied"]:
        need(bool(remainder) and remainder[0].startswith("talents=") and
             compiler.TALENTS.fullmatch(remainder[0][8:]) is not None,
             "V236_SOURCE_TALENTS_CHANGED")
        remainder=remainder[1:]
    need(remainder==[
        f"{slot}=simc_source_{items[slot]},id={items[slot]},"
        f"ilevel={receipt['target_ilevel']},source=local"
        for slot in compiler.contracts.SLOT_ORDER if slot in items],
         "V236_SOURCE_EQUIPMENT_OR_OVERRIDES_CHANGED")
    need(type(expected_source_revision) is str and
         re.fullmatch("[a-f0-9]{40}",expected_source_revision) and
         type(expected_game_build) is str and
         source.BUILD.fullmatch(expected_game_build),
         "V236_EXPLICIT_IMMUTABLE_SOURCE_PIN_REQUIRED")
    need(receipt["current_season_membership_certified"] is False and
         receipt["game_build_declared_by_simc_source"]==expected_game_build
         and receipt["simc_revision"]==expected_source_revision,
         "V236_SOURCE_REVISION_OR_GAME_BUILD_NOT_PINNED")
    return text


def run(*, profile_path, receipt_path, binary, binary_sha256,
        expected_source_revision, expected_game_build,
        output_dir, max_new=0, iterations=1, timeout_seconds=180):
    need(type(max_new) is int and max_new in (0,1) and
         type(iterations) is int and 1<=iterations<=35 and
         type(timeout_seconds) is int and 1<=timeout_seconds<=900 and
         type(binary_sha256) is str and HEX64.fullmatch(binary_sha256),
         "V236_EXACT_BINARY_AND_NATIVE_CAP_REQUIRED")
    receipt=json.loads(Path(receipt_path).read_text(encoding="utf8"))
    profile_bytes=Path(profile_path).read_bytes()
    profile=check(profile_bytes,receipt,
                  expected_source_revision=expected_source_revision,
                  expected_game_build=expected_game_build)
    binpath=Path(binary).resolve(strict=True)
    need(binpath.is_file() and digest(binpath.read_bytes())==binary_sha256,
         "V236_EXECUTABLE_SHA256_MISMATCH")
    folder=Path(output_dir).resolve()
    need(not folder.exists(),"V236_NEW_OUTPUT_REQUIRED_PREVENT_DOUBLE_NATIVE")
    folder.mkdir(parents=True)
    input_bytes=(profile+f"iterations={iterations}\n"+"threads=1\n"+
                 f"json2={folder/'native.json'}\n").encode("utf8")
    (folder/"input.simc").write_bytes(input_bytes)
    identity={
        "source_receipt_sha256":receipt["receipt_sha256"],
        "source_profile_sha256":receipt["physical_profile_sha256"],
        "executed_input_sha256":digest(input_bytes),
        "executable_sha256":binary_sha256,
        "simc_source_revision":receipt["simc_revision"],
        "source_game_build":expected_game_build,
        "compiled_game_build_not_proven":True,
        "target_ilevel":receipt["target_ilevel"],
        "iterations":iterations}
    result={"schema":SCHEMA,"identity":identity,"new_native_calls":0,
            "status":"PREPARED_NOT_EXECUTED","returncode":None,
            "error":None,"observed_G":None,
            "G":None,"B":None,"T":None,"environment_ready":False}
    if max_new:
        result["new_native_calls"]=1
        try:
            with (folder/"simc.log").open("wb") as log:
                p=subprocess.run([str(binpath),str(folder/"input.simc")],
                    cwd=str(folder),stdout=log,stderr=subprocess.STDOUT,
                    check=False,timeout=timeout_seconds)
            result["returncode"]=p.returncode
            if p.returncode!=0:
                result["status"]="FAIL_NATIVE_EXIT"
                result["error"]="returncode="+str(p.returncode)
            elif not (folder/"native.json").is_file():
                result["status"]="FAIL_NATIVE_JSON2_MISSING"
            else:
                result["observed_G"]=native.observe(
                    native_raw=(folder/"native.json").read_bytes(),
                    profile_receipt=receipt,native_binary_sha256=binary_sha256,
                    executed_profile_sha256=digest(input_bytes))
                result["status"]="PASS_NATIVE_OBSERVED_G_UNPROMOTED"
        except (OSError,ValueError,TypeError,KeyError,subprocess.TimeoutExpired,
                native.PhysicalNativeBlocked) as exc:
            result["status"]="FAIL_NATIVE_ERROR_OR_STATIC_MISMATCH"
            result["error"]=type(exc).__name__+":"+str(exc)
    for filename,key in (("simc.log","native_log_sha256"),
                         ("native.json","native_json2_sha256")):
        f=folder/filename
        result[key]=digest(f.read_bytes()) if f.is_file() else None
    (folder/"receipt.json").write_text(
        json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n",
        encoding="utf8")
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profile",type=Path,required=True)
    p.add_argument("--receipt",type=Path,required=True)
    p.add_argument("--simc-binary",type=Path,required=True)
    p.add_argument("--simc-sha256",required=True)
    p.add_argument("--source-revision",required=True)
    p.add_argument("--source-game-build",required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--max-new",type=int,choices=(0,1),default=0)
    args=p.parse_args(argv)
    result=run(profile_path=args.profile,receipt_path=args.receipt,
        binary=args.simc_binary,binary_sha256=args.simc_sha256,
        expected_source_revision=args.source_revision,
        expected_game_build=args.source_game_build,
        output_dir=args.output_dir,max_new=args.max_new)
    print("V236_ONE_SEALED_SOURCE_NATIVE",result["status"],
          "calls",result["new_native_calls"])
    return 0 if result["status"] in (
        "PASS_NATIVE_OBSERVED_G_UNPROMOTED","PREPARED_NOT_EXECUTED") else 3


if __name__=="__main__":raise SystemExit(main())
