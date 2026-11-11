#!/usr/bin/env python3
"""Fresh Havoc, auto T, 12 source CHMV, 3 independent seeds at N32/48/64/96.
Two separate N640 per candidate form a finite 12-CHMV reference, NOT truth.
Existing v319 product Build and v326 Native/ZIP runner are reused unchanged.
"""
from __future__ import annotations
import os,pathlib
from integration_probes import p2_v319_new_windwalker_v290_v318_real_once as fresh
from integration_probes import p2_v326_new_devastation_heldout_N_real_once as old
from runner import v325_independent_holdout_quality_arrival as quality

CASE="havoc_demonhunter_4ordinary_auto_T"
SPEC=("demonhunter","havoc")
ROOT=pathlib.Path("out/p2_v327_havoc_autoT_three_seed_n").resolve()
SCHEMA="p2_v327_fresh_havoc_autoT_three_seed_n32_48_64_96_v1"
SCREEN_N=(32,48,64,96)
SCREEN_REPS=(0,1,2)
HOLDOUT_REPS=(0,1)
TOTAL_RESEARCH_NATIVE=12*(len(SCREEN_N)*len(SCREEN_REPS)+len(HOLDOUT_REPS))
TOTAL_RESEARCH_ITERATIONS=12*(sum(SCREEN_N)*len(SCREEN_REPS)+640*len(HOLDOUT_REPS))

class HavocBlocked(ValueError):pass
def need(ok,reason):
    if not ok:raise HavocBlocked("V327_"+reason)

def select_fresh_pool(left,right):
    """Pre-register 2 top confirmations per policy, four spaced scout points
    per policy, then CHMV L1-diverse fallback; never consult N640 holdout.
    """
    arms={"v290_original":left,"v318_idea001":right}
    sources={}
    chosen=[];seen=set()
    for arm,rows in arms.items():
        need(len(rows)==64
             and sum(x.get("phase")=="scout" and x.get("iterations")==35
                     for x in rows)==56
             and sum(x.get("phase")=="precision" and x.get("iterations")==320
                     for x in rows)==8,"REAL_56_8_JOURNAL_REQUIRED")
        for row in rows:
            if row["phase"]!="scout":continue
            v=quality.key(row["target"])
            candidate={"vector":v,"row":row,"arm":arm,"index":row["index"]}
            if v not in sources or (row["index"],arm)<(
                    sources[v]["index"],sources[v]["arm"]):
                sources[v]=candidate
    def add(v):
        if v in sources and v not in seen and len(chosen)<12:
            chosen.append(sources[v]);seen.add(v)
    for arm,rows in arms.items():
        precision=sorted((r for r in rows if r["phase"]=="precision"),
                         key=lambda r:(-r["dps_mean"],r["case_key"]))
        for x in precision[:2]:add(quality.key(x["target"]))
    for pos in (7,19,37,53):
        for arm,rows in arms.items():
            scouts=[x for x in rows if x["phase"]=="scout"]
            add(quality.key(scouts[pos]["target"]))
    need(len(sources)>=12 and len(chosen)>0,"VALID_CURRENT_SOURCE_POOL")
    while len(chosen)<12:
        remaining=(x for v,x in sources.items() if v not in seen)
        winner=min(remaining,key=lambda x:(
           -min(sum(abs(a-b) for a,b in zip(x["vector"],c["vector"]))
                for c in chosen),x["vector"]))
        add(winner["vector"])
    need(len(chosen)==12 and len(seen)==12,"TWELVE_UNIQUE_CHMV_REQUIRED")
    return sorted(chosen,key=lambda x:(x["index"],x["vector"]))

def callback(doc,binary,root):
    return old.finish_new_profile(
        doc,binary,root,expected_spec=SPEC,
        screen_ns=SCREEN_N,screen_reps=SCREEN_REPS,
        holdout_reps=HOLDOUT_REPS,selector=select_fresh_pool,
        research_schema=SCHEMA+"_original_native",
        selection_label="top2_both_policies_scout7_19_37_53_diversity_fill",
        archive_name="research_168_original.zip",shuffle_seed=20261438)

def main():
    need(os.getenv("P2_V327_FRESH_HAVOC_N_ONCE")=="1",
         "NEW_DPS_PROFILE_EXPLICIT_NATIVE_ONCE_REQUIRED")
    need(TOTAL_RESEARCH_NATIVE==168 and TOTAL_RESEARCH_ITERATIONS==24000,
         "RESEARCH_BUDGET_DRIFT")
    return fresh.main(
        case_id=CASE,expected_spec=SPEC,
        output_root=ROOT,receipt_path=ROOT/"receipt.json",
        required_env="P2_V327_FRESH_HAVOC_N_ONCE",
        campaign_schema=SCHEMA,post_run_hook=callback)
if __name__=="__main__":main()
