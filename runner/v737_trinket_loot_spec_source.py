"""Same-build explicit loot specialization metadata, not an equipment gate.

Pure parser shared by research and the product catalog projection. The
caller authenticates the source bytes and build. Missing or unresolved
overrides remain unknown; never remove any candidate or rank DPS.
"""
from __future__ import annotations
import csv
from collections import defaultdict
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urlencode

# Stable DB2 role enum: TrinityCore DBCEnums.h ChrSpecializationRole.
ROLES={0:"TANK",1:"HEALER",2:"DPS"}
TABLES={"ChrSpecialization":(5_000_000,{"ID","ClassID","Role","Name_lang"}),
        "ItemSpecOverride":(32_000_000,{"ID","ItemID","SpecID"})}

def need(ok,code):
    if not ok:raise ValueError(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def read_rows(raw,table):
    bound,columns=TABLES[table]
    need(type(raw) is bytes and 0<len(raw)<=bound,"ROLE_SOURCE_SIZE:"+table)
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    need(reader.fieldnames and len(set(reader.fieldnames))==len(reader.fieldnames)
         and columns<=set(reader.fieldnames),"ROLE_SOURCE_COLUMNS:"+table)
    seen=set()
    for n,row in enumerate(reader):
        need(n<1_000_000 and None not in row,"ROLE_SOURCE_ROW_LIMIT_OR_SHAPE:"+table)
        rid=int(row["ID"])
        need(rid>0 and rid not in seen,"ROLE_SOURCE_ROW_ID:"+table)
        seen.add(rid)
        yield row
    need(bool(seen),"ROLE_SOURCE_EMPTY:"+table)

def classify(cohort,sources):
    """Return one row per supplied current-season item ID, in stable order."""
    need(type(cohort) is dict and 0<len(cohort)<=2000 and
         all(type(i) is int and i>0 and type(n) is str and bool(n)
             for i,n in cohort.items()),"ROLE_COHORT_INVALID")
    need(type(sources) is dict and set(sources)==set(TABLES),"ROLE_TABLES_INVALID")
    specs={}
    for row in read_rows(sources["ChrSpecialization"],"ChrSpecialization"):
        sid=int(row["ID"]);cid=int(row["ClassID"]);role=int(row["Role"])
        specs[sid]={"spec_id":sid,"class_id":cid,"name":row["Name_lang"],
                    "role_code":role,"role":ROLES.get(role,"UNKNOWN")}
    links=defaultdict(set)
    for row in read_rows(sources["ItemSpecOverride"],"ItemSpecOverride"):
        iid=int(row["ItemID"])
        if iid in cohort:
            links[iid].add(int(row["SpecID"]))
    rows=[]
    for iid,name in sorted(cohort.items()):
        spec_ids=sorted(links.get(iid,()))
        known=[specs[s] for s in spec_ids if s in specs]
        unresolved=sorted(set(spec_ids)-set(specs))
        roles=sorted({s["role"] for s in known if 1<=s["class_id"]<=13})
        incomplete=(bool(unresolved) or any(s["class_id"] not in range(1,14)
                                         or s["role"]=="UNKNOWN" for s in known))
        if not spec_ids:status="NO_EXPLICIT_OVERRIDE_UNKNOWN"
        elif incomplete:status="OVERRIDE_REFERENCE_OR_ROLE_PENDING"
        elif roles==["DPS"]:status="EXPLICIT_DPS_ROLE_ONLY"
        elif "DPS" in roles:status="EXPLICIT_SHARED_WITH_DPS"
        else:status="EXPLICIT_NON_DPS_ROLES_ONLY"
        rows.append({"item_id":iid,"name":name,"spec_ids":spec_ids,
                     "observed_specs":known,"unknown_spec_ids":unresolved,
                     "observed_roles":roles,"status":status})
    return rows


def annotate_trinkets(choices,build,source):
    """Optional display projection only, on caller-authenticated same-build bytes.

    Mutates the new public choice rows only. Existing physical compatibility,
    source catalog, budget and selections do not change.
    """
    if source is None:return
    need(type(source) is dict and set(source)=={"game_build","tables"}
         and source["game_build"]==build,"ROLE_SOURCE_BUILD_DRIFT")
    cohort={x["item_id"]:x["name"] for x in choices}
    need(len(cohort)==len(choices),"ROLE_CHOICE_DUPLICATE_ID")
    if not cohort:return
    records={row["item_id"]:row for row in classify(cohort,source["tables"])}
    for choice in choices:
        row=records[choice["item_id"]]
        choice["loot_spec_metadata"]={
            "status":row["status"],"roles":row["observed_roles"],
            "spec_ids":row["spec_ids"],
            "unknown_spec_ids":row["unknown_spec_ids"],
            "source":"SAME_BUILD_DB2_EXPLICIT_LOOT_SPEC_OVERRIDE",
            "equipment_eligibility_proven":False,
            "dps_effect_usefulness_proven":False}


TIER_STAGE_ID="fresh-db2-class-tier-candidates-ilvl"
TIER_STAGE_VERSION="v245-physical-base-ilvl-roster-1"
OVERRIDE_STAGE_ID="season-trinket-role-raw-ItemSpecOverride"
OVERRIDE_RELATIVE="source/raw_ItemSpecOverride.csv"


def source_url(table,build):
    need(table in TABLES,"ROLE_SOURCE_TABLE_UNKNOWN")
    return "https://wago.tools/db2/"+table+"/csv?"+urlencode(
        {"build":build,"locale":"enUS"})


def valid_raw(raw,table):
    """Check a newly acquired source once before sealing, not each UI event."""
    try:
        for row in read_rows(raw,table):
            if table=="ItemSpecOverride":
                int(row["ItemID"]);int(row["SpecID"])
            else:
                int(row["ClassID"]);int(row["Role"])
        return True
    except (ValueError,TypeError,KeyError,UnicodeError,csv.Error):
        return False


def _sealed_raw(root,stage_id,version,outputs,*,input_fingerprint=None):
    import v217_stage_execution_engine as stages
    paths,receipt_path=stages._safe_paths(root,stage_id,outputs)
    if not receipt_path.is_file():return None
    receipt=stages._read_receipt(receipt_path)
    if receipt.get("status")=="RUNNING":return None
    need(receipt.get("status")=="COMPLETE" and
         receipt.get("stage_id")==stage_id and receipt.get("stage_version")==version
         and all(receipt.get("output_paths",{}).get(k)==v for k,v in outputs.items())
         and (input_fingerprint is None or
              receipt.get("input_fingerprint")==input_fingerprint),
         "ROLE_SEALED_SOURCE_IDENTITY_DRIFT")
    result={}
    for key,(relative,path) in paths.items():
        limit=(TABLES["ItemSpecOverride"][0] if key=="raw"
               else TABLES.get(key,(2_000_000,None))[0])
        record=receipt.get("outputs",{}).get(key,{})
        need(path.is_file() and 0<path.stat().st_size<=limit and
             path.stat().st_size==record.get("size"),
             "ROLE_SEALED_SOURCE_SIZE_DRIFT")
        raw=path.read_bytes()
        need(record=={"path":relative,"size":len(raw),"sha256":sha(raw)},
             "ROLE_SEALED_SOURCE_HASH_DRIFT")
        result[key]=raw
    return result


def read_tier_specialization(root,build):
    """Reuse v245's same-build original, without changing its stage identity.

    Verify both consumed files against the sealed receipt and the original
    tier document's build and raw evidence. Other tier outputs are not read.
    """
    sources=_sealed_raw(root,TIER_STAGE_ID,TIER_STAGE_VERSION,{
        "ChrSpecialization":"source/db2_tier_ilvl_ChrSpecialization.csv",
        "candidates":"source/v245_db2_tier_candidates_ilvl.json"})
    if sources is None:return None
    doc=json.loads(sources["candidates"])
    raw=sources["ChrSpecialization"]
    need(doc.get("schema")=="v245_db2_first_class_tier_candidates_v1"
         and doc.get("game_build")==build and doc.get("evidence",{}).get(
             "chr_specialization_sha256")==sha(raw),
         "ROLE_TIER_SOURCE_BUILD_OR_EVIDENCE_DRIFT")
    # Historical/synthetic sources lacking Role columns are not evidence.
    if not valid_raw(raw,"ChrSpecialization"):return None
    return raw


def read_sources(root,build):
    """Read only existing sealed sources; no network or cache mutation."""
    import v217_stage_execution_engine as stages
    expected=stages._input_sha(OVERRIDE_STAGE_ID,"same-build-raw-v1",
        {"game_build":build,"source_url":source_url("ItemSpecOverride",build)})
    override=_sealed_raw(root,OVERRIDE_STAGE_ID,"same-build-raw-v1",
        {"raw":OVERRIDE_RELATIVE},input_fingerprint=expected)
    if override is None:return None
    spec=read_tier_specialization(root,build)
    if spec is None:return None
    return {"game_build":build,"tables":{"ChrSpecialization":spec,
                                        "ItemSpecOverride":override["raw"]}}
