"""One isolated Windows v278 baseline path comparison. No season collection,
user setup, G/J/F/O approval, or DPS optimization. Exact failed binary.
The old public representative weapon is a test input, never a season budget.
"""
from __future__ import annotations
import json
import pathlib
import sys
import tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v278_sealed_simc_consumable_native_pair as pair
import v659_simc_self_built_artifact as artifact
import v660_simc_one_click_provision as provision
import v193_simc_local_updater as updater

REV="6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7"
BUILD="12.1.5.70961"
BIN_SHA="1195a3401a716c9f28b4de113d228cc3a669aebf83c0c47e5989db521d87c3c9"
CANDIDATE={
    "archive_url":"https://github.com/degong2-code/simc-secondary-optimizer-runner/releases/download/simc-cli-source-"+REV+"/simc-win64-cli-6924096-"+BUILD+".zip",
    "artifact_sha256":"8f94209f1b7013da23fca47ada972630d18a371abd0e3d86f491bbad27dec2fd",
    "artifact_bytes":8834290,
}
PROFILE=("paladin=path_probe\nrace=dwarf\nspec=retribution\nposition=back\n"
         "main_hand=simc_source_268213,id=268213,ilevel=334,source=local\n")

def main():
    out=pathlib.Path(sys.argv[1]).resolve()
    out.mkdir(parents=True,exist_ok=True)
    receipt=out/"V691_NATIVE_PATH_COMPARISON.json"
    result={"schema":"v691_existing_v278_windows_path_comparison_v1",
            "scope":"BASELINE_PATH_REPAIR_ONLY_NOT_SEASON_ADMISSION",
            "prior_control_receipt_artifact_id":14885606192,
            "simc_revision":REV,"binary_sha256":BIN_SHA,
            "season_collection_calls":0,"dps_optimizer_calls":0,
            "native_calls":0,"observations":[],"status":"PENDING"}
    def save():
        receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n","utf8")
    save()
    with tempfile.TemporaryDirectory(prefix="v691-") as td:
        base=pathlib.Path(td).resolve()
        z=base/"release.zip"
        provision.download_release_zip(CANDIDATE,z)
        meta=artifact.inspect_artifact(z)
        assert (meta["source_sha"],meta["game_build"],meta["cli_sha256"])==(REV,BUILD,BIN_SHA)
        inner=base/"cli.7z"
        artifact.copy_inner_archive(z,inner,meta)
        extracted=base/"cli";extracted.mkdir()
        binary=pathlib.Path(updater.extract_py7zr_safe(inner,extracted))
        assert pair.file_sha(binary)==BIN_SHA
        # 197-character stage root is a reconstruction of the observed
        # v690 CI directory layout, not a captured historical absolute path.
        pad=197-len(str(base))-1
        assert 0<pad<200
        long=base/("p"*pad)
        assert len(str(long))==197
        for label,stage in (("long_fixed",long),):
            stage.mkdir()
            case=pair.run_case(stage_root=stage,profile=PROFILE,
                source_identity=pair.sha(PROFILE.encode("utf8")),
                binary=binary,binary_sha256=BIN_SHA,revision=REV,
                variant="baseline",timeout_seconds=90)
            r=case["receipt"];folder=case["folder"]
            # This is a deliberately constructed public test profile, never
            # user data. Preserve actual SimC error rather than only a code.
            log=pair.log_excerpt(folder) or ""
            log=log.replace(str(base),"<PROBE_ROOT>")
            row={"case":label,"stage_root_chars":len(str(stage)),
                 "input_chars":len(str(folder/"input.simc")),
                 "json2_chars":len(str(folder/"native.json")),
                 "status":r["status"],"returncode":r["native_returncode"],
                 "io_mode":r["identity"].get("io_mode"),
                 "error":r["error"],"simc_log":log,
                 "new_native_calls":case["new_native_calls"]}
            result["observations"].append(row)
            result["native_calls"]+=case["new_native_calls"]
            save()
        result["status"]=("LONG_PATH_RELATIVE_IO_REPAIR_PASS"
            if result["observations"][0]["status"]=="NATIVE_JSON2_CAPTURED"
            else "LONG_PATH_RELATIVE_IO_REPAIR_FAILED")
        save()
        if result["status"]!="LONG_PATH_RELATIVE_IO_REPAIR_PASS":
            raise SystemExit(2)

if __name__=="__main__":
    main()
