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
