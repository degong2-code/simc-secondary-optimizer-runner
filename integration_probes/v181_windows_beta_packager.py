#!/usr/bin/env python3
"""v181: deterministic minimal Windows web beta ZIP, source only; no SimC or caches.

Explicit allowlist; no ZIP of full repo, .git, historical artifacts, test
results, personal profiles outside tracked source, or third-party executables.
Runs entirely offline; SHA manifest for exact extracted bytes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import zipfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
PREFIX="SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA"
SCHEMA="v181_windows_local_web_beta_source_package_v1"
BASE_FILES=(
    "START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd",
    "requirements-web.txt",
    "WINDOWS_BETA_START_HERE.md",
)
CATEGORIES=(
    ("runner", {".py", ".html", ".js", ".css"}),
    ("data",{".json"}),
    ("integration_probes/catalog",{".json"}),
    ("integration_probes/data",{".json"}),
    ("integration_probes/fixtures",{".simc"}),
    ("fixtures",{".json"}),
    ("inputs",{".simc"}),
)
BANNED=(".env",".key",".pfx",".pem",".exe",".dll",".zip",".log",".db",".sqlite")
MANDATORY=(
    "runner/v113_local_web_api.py",
    "runner/v106_user_session_controller.py",
    "runner/v098_target_user_scenario_bootstrap.py",
    "runner/v094_durable_inclusive_adaptive_runner.py",
    "runner/v169_source_first_representative_stage.py",
    "runner/webui/index.html",
    "runner/webui/app.js",
    "data/current_season_product_gear_db.json",
    "data/current_season_tier_itemsets.json",
    "data/current_season_chmv_consumables.json",
    "integration_probes/catalog/v144_mid2_season_items.json",
    "integration_probes/catalog/v146_character_starter_examples.json",
    "integration_probes/data/midnight_s2_ilvl_chmv_reference_v1.json",
)
class PackageBlocked(ValueError):pass

def need(value,reason):
    if not value:raise PackageBlocked("V181_"+reason)

def select(root=ROOT):
    root=pathlib.Path(root).resolve()
    choices={}
    for name in BASE_FILES:
        p=root/name
        need(p.is_file() and not p.is_symlink(),"REQUIRED_FILE_MISSING:"+name)
        choices[name]=p
    for folder,extensions in CATEGORIES:
        base=root/folder
        need(base.is_dir() and not base.is_symlink(),
             "SOURCE_FOLDER_MISSING:"+folder)
        for p in sorted(base.rglob("*")):
            if not p.is_file():continue
            relative=p.relative_to(root).as_posix()
            need(not p.is_symlink(),"SYMLINK_REFUSED:"+relative)
            if ("__pycache__" in p.parts or p.name.startswith(".")
                or p.suffix.lower() not in extensions):
                continue
            choices[relative]=p
    need(all(k in choices for k in MANDATORY),
         "MINIMUM_PRODUCT_RUNTIME_FILES_MISSING")
    need(not any(path.endswith(BANNED) or "/runs/" in path or
                 path.startswith(("tests/",".github/","docs/"))
                 for path in choices),
         "BANNED_PAYLOAD_PATH")
    need(len(choices)>=75,"ABNORMALLY_SMALL_PRODUCT_PACKAGE")
    return choices

def build(target,root=ROOT):
    target=pathlib.Path(target).resolve()
    choices=select(root)
    need(target.suffix.lower()==".zip","ZIP_EXTENSION_REQUIRED")
    target.parent.mkdir(parents=True,exist_ok=True)
    records=[]
    contents=[]
    for rel,p in sorted(choices.items()):
        raw=p.read_bytes()
        need(len(raw)<=2_000_000,"UNEXPECTED_LARGE_SOURCE:"+rel)
        records.append({"path":rel,"size":len(raw),
                        "sha256":hashlib.sha256(raw).hexdigest()})
        contents.append((rel,raw))
    manifest={"schema":SCHEMA,"archive_root":PREFIX,
              "files":records,"file_count":len(records),
              "native_executable_bundled":False,
              "dependency_auto_install":False,
              "historical_native_json2_bundled":False,
              "sessions_bundled":False,
              "runtime_identity_bytes_unchanged":True}
    manifest_raw=(json.dumps(manifest,ensure_ascii=False,
            indent=2,sort_keys=True)+"\n").encode("utf8")
    # DOS epoch permits reproducible metadata even across Linux/Windows.
    with zipfile.ZipFile(target,"w",compression=zipfile.ZIP_DEFLATED,
                         compresslevel=8,allowZip64=False) as archive:
        for rel,raw in contents+[("V181_PACKAGE_MANIFEST.json",manifest_raw)]:
            entry=zipfile.ZipInfo(PREFIX+"/"+rel,
                date_time=(1980,1,1,0,0,0))
            entry.compress_type=zipfile.ZIP_DEFLATED
            entry.external_attr=0o100644<<16
            archive.writestr(entry,raw,compress_type=zipfile.ZIP_DEFLATED,
                             compresslevel=8)
    need(target.stat().st_size<=4_000_000,"UNEXPECTED_ARCHIVE_BLOAT")
    return manifest

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=pathlib.Path)
    args=parser.parse_args(argv)
    manifest=build(args.out)
    print("V181_WINDOWS_SOURCE_ZIP_PASS",args.out,
          "files",manifest["file_count"],
          "no_simc_no_user_cache",flush=True)

if __name__=="__main__":main()
