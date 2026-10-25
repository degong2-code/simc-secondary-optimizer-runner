#!/usr/bin/env python3
"""v067: thin profile-neutral CLI around the SINGLE v065 scheduler/executor.

Uses v066 explicit scenario + selected standard filler + Native static cache +
full SimC profile + two Native JSON2 numeric witnesses; delegates search,
execution, verified cache, cancellation and confirmation to v065 unchanged.
No SimC effect/proc analysis and no separate search algorithm.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys

import v046_static_item_cache as cache
import v066_profile_neutral_preflight as preflight
import v065_original_scheduler_native_bridge as engine

SCHEMA="v067_generic_v065_execution_route_v1"

def route(scenario_file,filler_file,cache_file,profile_file,witness_dir,
          binary_sha256,output,binary=None,cancel_file=None):
    scenario=json.loads(pathlib.Path(scenario_file).read_text(encoding="utf8"))
    filler=json.loads(pathlib.Path(filler_file).read_text(encoding="utf8"))
    static=cache.load(pathlib.Path(cache_file))
    profile=pathlib.Path(profile_file).read_text(encoding="utf8")
    witnesses=preflight.load_witnesses(witness_dir)
    prepared=preflight.prepare(scenario,filler,static,profile,witnesses,
                               binary_sha256)
    out=pathlib.Path(output)
    out.mkdir(parents=True,exist_ok=True)
    meta=prepared["summary"]
    (out/"V067_PROFILE_PREFLIGHT.json").write_text(
       json.dumps(meta,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
       encoding="utf8")
    status=engine.start(None,out,binary=binary,cancel_file=cancel_file,
                        prepared=prepared)
    return status

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--scenario",required=True,type=pathlib.Path)
    ap.add_argument("--filler",required=True,type=pathlib.Path)
    ap.add_argument("--static-cache",required=True,type=pathlib.Path)
    ap.add_argument("--profile",required=True,type=pathlib.Path)
    ap.add_argument("--witness-root",required=True,type=pathlib.Path)
    ap.add_argument("--binary-sha256",required=True)
    ap.add_argument("--binary",type=pathlib.Path)
    ap.add_argument("--output",required=True,type=pathlib.Path)
    ap.add_argument("--cancel-file",type=pathlib.Path)
    a=ap.parse_args(argv)
    try:
        return route(a.scenario,a.filler,a.static_cache,a.profile,
                     a.witness_root,a.binary_sha256,a.output,
                     a.binary,a.cancel_file)
    except Exception as exc:
        a.output.mkdir(parents=True,exist_ok=True)
        receipt={"schema":SCHEMA,"status":"BLOCKED_NO_SILENT_GUESS",
                 "error":type(exc).__name__+":"+str(exc),
                 "new_simc_calls_from_this_wrapper":0,
                 "effect_modeling_owner":"SimC",
                 "original_v015_v016_sources_modified":False}
        (a.output/"V067_BLOCKED.json").write_text(
            json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
        print("V067_BLOCKED",receipt["error"],file=sys.stderr)
        return 3

if __name__=="__main__":
    sys.exit(main())
