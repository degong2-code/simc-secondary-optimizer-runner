#!/usr/bin/env python3
"""v064 exact replay of existing v063 REAL Native inputs + JSON2.

Zero new SimC calls. This checks that the scheduler-neutral candidate port
can consume byte-verified prior SimC measurements; no new DPS assertions,
proc research, or actual v015/v016 product merge.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys

import v063_numeric_injection as inject
import v063_official_T_two_native as prior
import v064_adaptive_evaluator_port as port

def main(argv=None):
    cli=argparse.ArgumentParser()
    cli.add_argument("--evidence",type=pathlib.Path,required=True)
    cli.add_argument("--output",type=pathlib.Path,required=True)
    args=cli.parse_args(argv)
    root=args.evidence.resolve()
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=True)
    evidence=prior.read_evidence(root)
    proof=prior.plan_from_previous(evidence)
    targets=[]
    for x in evidence:
        targets.append(inject.read_rating(x["native"]["sim"]["players"][0]))
    proposed=[{"target":t,"iterations":60} for t in targets]
    reqs=port.plan_queue(proposed,proof["contract"],proof["static"],
             proof["calibration"],proof["reference"],prior.BINARY_SHA,out)
    assert len(reqs)==2
    observations=[]
    for i,(req,witness) in enumerate(zip(reqs,evidence)):
        origin=inject.input_parts(witness["input"])
        rerendered=inject.input_parts(req["input"])
        # Original execution's actual source must equal candidate source
        # after removing ONLY the output path. Otherwise refuse replay.
        assert origin["stable_sha256"]==rerendered["stable_sha256"]
        assert origin["gear_override"]==rerendered["gear_override"]
        native_path=root/("case_%02d"%i)/"result.json"
        data=native_path.read_bytes()
        assert json.loads(data)==witness["native"]
        observation=port.ingest_native(req,witness["native"],
                                       proof["calibration"],data)
        cache_case=out/("case_%02d"%i)
        cache_case.mkdir(parents=True,exist_ok=True)
        (cache_case/"port_request.json").write_text(
            json.dumps({k:v for k,v in req.items() if k!="input"},
                       indent=2,sort_keys=True)+"\n")
        (cache_case/"port_observation.json").write_text(
            json.dumps(observation,indent=2,sort_keys=True)+"\n")
        assert port.verify_disk_cache(req,proof["calibration"],
                                      observation,data)==observation
        observations.append(observation)
    report=port.summarize(observations,3152)
    assert report["status"]=="BOUNDED_OBSERVED_RANKING_NOT_GLOBAL_OPTIMUM"
    assert report["evaluated"]==2
    assert len(report["materially_distinct_near_performing"])==0
    result={"schema":"v064_prior_real_native_scheduler_port_replay_v1",
            "status":"PASS_OFFLINE_REAL_NATIVE_JSON2_REPLAY",
            "native_calls_new":0,
            "prior_native_run_id":40165729165,
            "old_real_json2_consumed":2,
            "official_T":proof["static"]["budget"]["T_official"],
            "G":proof["static"]["G_if_complete"],
            "measured_net_offset":proof["calibration"]["net_input_to_json2_rating_offset"],
            "simc_binary_sha256":prior.BINARY_SHA,
            "candidate_port_status":report["status"],
            "original_product_v015_v016_merged":False,
            "external_scheduler_attached":False,
            "no_item_effect_modeling_or_proc_gate":True,
            "per_case":[{"case_key":o["case_key"],
                 "actual_rating":o["rating_actual"],
                 "dps_mean":o["dps_mean"],"dps_sem":o["dps_sem"],
                 "real_native_json2_sha256":o["native_json_sha256"]}
                 for o in observations],
            "result":report}
    assert result["official_T"]==3152 and result["G"]==2849
    (out/"V064_REPLAY_RECEIPT.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V064",result["status"],"new_simc_calls",0)
    return 0

if __name__=="__main__":
    sys.exit(main())
