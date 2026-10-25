#!/usr/bin/env python3
"""v068: user-confirmed 334 Void Elf Subtlety Rogue -> bounded SimC profile.

Exact USER choices are constants only for this SINGLE acceptance fixture. This
module is not a full season gear DB, multi-item recommender, manual equip
optimizer, new APL or independent proc-effect verifier. The original official
SimC Rogue APL is copied unchanged from the SHA-pinned project fixture; only
character settings, explicitly chosen gear and combat/consumable lines change.

The initial crafted 36/49 stat selection is *not* a locked optimization floor.
Native G, fixed special L, candidate rating and all effects remain SimC/P2/P3
responsibilities. This stage is PROFILE CONSTRUCTION ONLY.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,re,sys
import v055_simc_item_selection as selector

SCHEMA="v068_user_subtlety_native_profile_334_v1"
HERE=pathlib.Path(__file__).resolve().parents[1]
REFERENCE=HERE/"integration_probes/fixtures/v068_upstream_mid2_rogue_subtlety_reference.simc"
UPSTREAM_GIT_BLOB_SHA="b704e6326959432a82d14a6b774c79183d5b2af4"
USER_TALENTS="CUQAAAAAAAAAAAAAAAAAAAAAAAgx2MAAAAAwsMGLTMbLjxMjZgZmZGzMbzYGbLzMzMzMjBjZ2GAAAAGMGwYWMMwAzCL0iNMDYmBzYA"
DEFAULT_T=334
SPECIAL_GEM_B=240967
NORMAL_GEM=240900
OMNIUM_FOURTH="rune_of_masterful_cunning"
TIER={"shoulders":271508,"chest":271513,"hands":271511,"legs":271509}
SPECIAL={"head":271875,"main_hand":271093}
CRAFTED={
 "wrists":(244576,"arcanoweave_lining","36/49"),
 "off_hand":(237837,"hunters_ritual_stone","36/49")}
TRINKETS={"trinket1":270175,"trinket2":281215}
ALL_SLOTS=selector.SLOTS
STAT_ORDER=("crit_rating","haste_rating","mastery_rating","versatility_rating")
EXPECTED_GEM_SLOTS={"neck":2,"wrists":1,"waist":1,"finger1":2,"finger2":1}
CANONICAL_OPTIONS={"back":{"crafted_stats":"36/49"},
    "neck":{"gem_id":"240967/240900"},
   "wrists":{"gem_id":"240900"},"waist":{"gem_id":"240900"},
   "finger1":{"gem_id":"240900/240900"},"finger2":{"gem_id":"240900"}}
EXISTING_DEFAULTS={
    "potion":"lights_potential_2",
    "flask":"flask_of_the_shattered_sun_2",
    "food":"harandar_celebration",
    "augmentation":"void_touched",
    "temporary_enchant":"main_hand:thalassian_phoenix_oil_2/off_hand:thalassian_phoenix_oil_2"}
PROBE_A={"crit_rating":550,"haste_rating":930,"mastery_rating":1080,"versatility_rating":380}
PROBE_B={"crit_rating":650,"haste_rating":830,"mastery_rating":1080,"versatility_rating":380}
class ProfileBlocked(ValueError):pass
def need(x,msg):
    if not x:raise ProfileBlocked(msg)
def sha(raw):
    return hashlib.sha256(raw if isinstance(raw,bytes) else raw.encode("utf-8")).hexdigest()
def settings(parsed):
    """Verify source class, baseline APL and all 16 slots before replacement."""
    need("rogue" in parsed and parsed.get("spec")=="subtlety","NOT_ROGUE_SUBTLETY_REFERENCE")
    need(parsed.get("omnium_talents") is not None,"NO_UPSTREAM_OMNIUM")
    need(parsed.get("actions") is not None and parsed.get("actions.precombat") is not None,
         "OFFICIAL_APL_MISSING")
    need(set(ALL_SLOTS).issubset(parsed),"REFERENCE_MISSING_FULL_EQUIPMENT")
def all_parts(reference):
    parsed={}
    for raw in reference.splitlines():
        if not raw or raw.startswith("#") or "=" not in raw:continue
        k,v=raw.split("=",1)
        if k not in parsed:parsed[k]=v
    return parsed
def item_line(slot,number,ilevel=334,option=None):
    selector.checked_id(number)
    if option is None:option={}
    selector.checked_options(option)
    seg=[slot+"=selected_"+str(number),"id="+str(number),"ilevel="+str(ilevel),"source=local"]
    seg.extend(k+"="+v for k,v in sorted(option.items()))
    return ",".join(seg)
def assemble(reference,output,iterations=35,probe="A"):
    """Return candidate source and receipt, no Native run."""
    need(type(reference) is str and len(reference)<200000,"BAD_UPSTREAM_SIMC_SOURCE")
    parsed=all_parts(reference);settings(parsed)
    need(probe in ("A","B"),"PROBE_UNKNOWN")
    need(type(iterations) is int and 30<=iterations<=200,
         "NATIVE_PROBE_ITERATIONS_CAP")
    target=PROBE_A if probe=="A" else PROBE_B
    equip={}
    equip.update({k:item_line(k,v) for k,v in TIER.items()})
    equip.update({k:item_line(k,v) for k,v in SPECIAL.items()})
    equip.update({k:item_line(k,v,option={"embellishment":eff,
                                           "crafted_stats":crafted,
                                           **({"gem_id":"240900"} if k=="wrists" else {})})
                  for k,(v,eff,crafted) in CRAFTED.items()})
    equip.update({k:item_line(k,v) for k,v in TRINKETS.items()})
    for slot in sorted(ALL_SLOTS-set(equip)):
        raw=parsed[slot]
        match=re.search(r"(?:^|,)id=([0-9]+)",raw)
        need(match is not None,"UPSTREAM_ITEM_MISSING_ID:"+slot)
        equip[slot]=item_line(slot,int(match.group(1)),
                               option=CANONICAL_OPTIONS.get(slot,{}))
    # The base profile’s entire APL remains byte-for-byte identical, as do
    # unsupported/unknown SimC effect internals. Only exact named settings
    # and equipment lines are replaced.
    choices={"race":"void_elf","talents":USER_TALENTS,
     "omnium_talents":"/".join([
        *parsed["omnium_talents"].split("/")[:3],
        OMNIUM_FOURTH,parsed["omnium_talents"].split("/")[-1]]),
     **EXISTING_DEFAULTS,
     "fight_style":"Patchwerk","desired_targets":"1","max_time":"300",
     "vary_combat_length":"0","fixed_time":"1","optimal_raid":"1",
     "iterations":str(iterations),"threads":"1",
     "json2":str(pathlib.Path(output).resolve())}
    choices.update({f"gear_{k}":str(target[k]) for k in STAT_ORDER})
    omit_keys=set(equip)|set(choices)
    source=[]
    for line in reference.splitlines():
        if line.startswith("# Gear Summary"):break
        k,sep,_=line.partition("=")
        if sep and not line.startswith("#") and k in omit_keys:continue
        source.append(line)
    # Deterministic output order; do not alter upstream action lines.
    source.extend("")
    source.extend(k+"="+str(v) for k,v in choices.items())
    source.extend(equip[k] for k in [
        "head","neck","shoulders","back","chest","wrists","hands","waist",
        "legs","feet","finger1","finger2","trinket1","trinket2",
        "main_hand","off_hand"])
    rendered="\n".join(source).rstrip()+"\n"
    need(rendered.count("omnium_talents=")==1,"OMNIUM_DUPLICATE")
    need(rendered.count("embellishment=")==2,"TWO_EMBELLISHMENTS_NOT_TRANSFERRED")
    need(rendered.count("gear_crit_rating=")==1,"RATING_OVERRIDE_DUPLICATE")
    need(sum(1 for ln in rendered.splitlines() if ln.startswith("actions"))==
         sum(1 for ln in reference.splitlines() if ln.startswith("actions")),
         "UPSTREAM_APL_ACTION_COUNT_CHANGED")
    # Roundtrip selected IDs and slots only, no proc logic.
    for k,v in equip.items():
        need(rendered.count(k+"=")==1,"EQUIPMENT_SLOT_COLLISION:"+k)
    special_bag=sum(len(x.split("/")) for x in [
        CANONICAL_OPTIONS[s]["gem_id"] for s in CANONICAL_OPTIONS])
    need(special_bag==7 and
         sum(CANONICAL_OPTIONS[s]["gem_id"].count(str(SPECIAL_GEM_B))
             for s in CANONICAL_OPTIONS)==1,"GEM_COUNT_POLICY")
    receipt={"schema":SCHEMA,"status":"GENERATED_NOT_NATIVE_TESTED",
        "upstream_git_blob_sha":UPSTREAM_GIT_BLOB_SHA,
        "user":{"class":"rogue","spec":"subtlety","race":"void_elf",
           "talents":USER_TALENTS,"ilevel":334,
           "special":dict(SPECIAL),"tier_four":dict(TIER),
           "trinkets":dict(TRINKETS),
           "embellishment_1":{"effect":"hunters_ritual_stone","slot":"off_hand","item_id":237837},
           "embellishment_2":{"effect":"arcanoweave_lining","slot":"wrists","item_id":244576},
           "omnium_column_4":"mastery","omnium_selected_name":OMNIUM_FOURTH,
           "special_gem_type":"B","special_gem_id":SPECIAL_GEM_B},
        "gear_slots":len(equip),"user_selected_item_slots_preserved":True,
        "probe_kind":probe,"probe_raw_gear_override":target,"iterations":iterations,
        "input_sha256":sha(rendered),
        "item_static_G":None,"locked_special_L":None,
        "official_T":None,"rating_calibration":None,
        "native_calls":0,"native_json2_dps_verified":False,
        "same_season_static_cache_not_reset":True,
        "item_proc_apl_dps_owner":"SimC"}
    return rendered,receipt
def main(argv=None):
    cli=argparse.ArgumentParser()
    cli.add_argument("--reference",type=pathlib.Path,default=REFERENCE)
    cli.add_argument("--out",type=pathlib.Path,required=True)
    cli.add_argument("--iterations",type=int,default=35)
    cli.add_argument("--probe",choices=["A","B"],default="A")
    a=cli.parse_args(argv)
    a.out.mkdir(parents=True,exist_ok=True)
    doc={"schema":SCHEMA,"status":"BLOCKED_NO_INPUT_FABRICATION"}
    try:
        src=a.reference.read_text(encoding="utf-8")
        dest=a.out/"result.json"
        source,doc=assemble(src,dest,a.iterations,a.probe)
        (a.out/"input.simc").write_text(source,encoding="utf-8")
    except Exception as exc:
        doc["error"]=type(exc).__name__+":"+str(exc)
    (a.out/"V068_PROFILE_RECEIPT.json").write_text(
       json.dumps(doc,indent=2,sort_keys=True,ensure_ascii=False)+"\n",
       encoding="utf-8")
    print("V068",doc["status"],flush=True)
    return 0 if doc["status"]=="GENERATED_NOT_NATIVE_TESTED" else 3
if __name__=="__main__":sys.exit(main())
