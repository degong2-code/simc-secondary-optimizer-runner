#!/usr/bin/env python3
"""P1 v342: inspect an exact official Windows SimC nightly, no DPS simulation.

The upstream GitHub Actions run and artifact are fixed in the one-time workflow;
archive/exe SHA are saved. No user profile, output=json2, iterations or DPS.
A banner match by itself does NOT certify the current season's G/J/F/O.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,re,subprocess,sys
RUN_ID=42956947906
ARTIFACT_ID=13827649795
ARTIFACT_ZIP_SHA="f4ddea2bf7825749e4063cacbae65d5f2177fa56dc0bcbdbf5173016101f91be"
UPSTREAM_COMMIT="17e4d74676a0b45525906b5cb1acdb1af2c851e1"
SCHEMA="p1_v342_official_windows_nightly_source_inspection_v1"

def sha256(p):
    h=hashlib.sha256()
    with pathlib.Path(p).open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def run(archive,binary,target):
    if sys.platform!="win32":raise RuntimeError("WINDOWS_ONLY")
    archive=pathlib.Path(archive).resolve(strict=True)
    binary=pathlib.Path(binary).resolve(strict=True)
    m=re.fullmatch(r"simc-\d+\.\d+\.([0-9a-f]{7,12})-win64\.7z",
                   archive.name,re.I)
    if (m is None or binary.name.lower()!="simc.exe" or
        not UPSTREAM_COMMIT.startswith(m.group(1).lower())):
        raise RuntimeError("OFFICIAL_SOURCE_FILENAME_OR_REVISION_DRIFT")
    # The executable receives no SimC profile or simulation options.
    p=subprocess.run([str(binary)],input="",text=True,
       capture_output=True,errors="replace",cwd=binary.parent,timeout=25)
    banner=[line.strip()[:220] for line in
            (p.stdout+"\n"+p.stderr).splitlines() if line.strip()][:15]
    recognized=bool(re.search(r"(?<!\d)12\.1\.5\.70783(?!\d)",
                              "\n".join(banner)))
    result={
       "schema":SCHEMA,
       "status":"OFFICIAL_WINDOWS_EXE_SOURCE_INSPECTED_NO_DPS",
       "repository":"simulationcraft/simc-publish",
       "upstream_run_id":RUN_ID,
       "upstream_artifact_id":ARTIFACT_ID,
       "upstream_artifact_zip_digest_sha256":ARTIFACT_ZIP_SHA,
       "upstream_commit":UPSTREAM_COMMIT,
       "archive_filename":archive.name,
       "archive_sha256":sha256(archive),
       "binary_sha256":sha256(binary),
       "binary_revision_short_from_filename":m.group(1).lower(),
       "cli_no_profile_exit_code":p.returncode,
       "cli_banner_lines":banner,
       "exact_70783_mentioned_in_cli_banner":recognized,
       "same_build_gjfo_and_profile_validated":False,
       "new_native_dps_simulations":0,
       "new_environment_native_simulations":0,
       "new_season_ready_proven":False
    }
    dest=pathlib.Path(target)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",
                    encoding="utf8")
    print("V342_OFFICIAL_SOURCE "+json.dumps({k:result[k] for k in
           ("status","archive_filename","archive_sha256",
            "binary_sha256","upstream_run_id",
            "exact_70783_mentioned_in_cli_banner",
            "same_build_gjfo_and_profile_validated",
            "new_native_dps_simulations")},sort_keys=True),flush=True)

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--archive",required=True)
    cli.add_argument("--simc",required=True)
    cli.add_argument("--out",required=True)
    args=cli.parse_args()
    run(args.archive,args.simc,args.out)
