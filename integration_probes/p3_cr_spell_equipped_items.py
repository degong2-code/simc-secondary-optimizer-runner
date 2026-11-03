#!/usr/bin/env python3
"""P3-CR same-build Wago SpellEquippedItems exact scope (ONE csv GET).

Print only schemas/rows for known same-build Phoenix Oil 1237006/1237008
and Dawn Oil 1237001. No game effect implementation, Native or item DB.
"""
import csv
import hashlib
import io
import json
from urllib.request import Request,urlopen
from urllib.parse import urlencode

BUILD="12.1.5.70575"
TABLE="SpellEquippedItems"
SPELLS=(1237006,1237008,1237001)
CAP=8_000_000

def scan(transport=urlopen):
    url="https://wago.tools/db2/"+TABLE+"/csv?"+urlencode(
        {"build":BUILD,"locale":"enUS"})
    req=Request(url,headers={
        "Accept":"text/csv",
        "User-Agent":"SIMC-Secondary-P3-CR-ExactSourceOnly/1.0"})
    chunks=[];size=0
    with transport(req,timeout=75) as response:
        if response.status!=200:
            raise ValueError("P3_CR_HTTP_NON200")
        while True:
            chunk=response.read(262144)
            if not chunk:break
            size+=len(chunk)
            if size>CAP:raise ValueError("P3_CR_SOURCE_SIZE_LIMIT")
            chunks.append(chunk)
    raw=b"".join(chunks)
    digest=hashlib.sha256(raw).hexdigest()
    text=raw.decode("utf-8-sig")
    reader=csv.DictReader(io.StringIO(text))
    header=tuple(reader.fieldnames or ())
    required={"ID","SpellID","EquippedItemClass",
              "EquippedItemInvTypes","EquippedItemSubclass"}
    if not required.issubset(header):
        raise ValueError("P3_CR_SCHEMA_FIELD_MISMATCH:"+str(header))
    observed=[]
    for row in reader:
        if row.get("SpellID") in {str(v) for v in SPELLS}:
            observed.append({k:row[k] for k in (
                "ID","SpellID","EquippedItemClass",
                "EquippedItemInvTypes","EquippedItemSubclass")})
    result={"schema":"p3_cr_same_build_spell_equipped_items_probe_v1",
            "game_build":BUILD,"table":TABLE,"sha256":digest,
            "source_bytes":size,"http_calls":1,
            "header":header,"queried_spells":SPELLS,
            "exact_rows":observed,"no_native":True,
            "F":None,"O":None,"environment_ready":False}
    return result

if __name__=="__main__":
    result=scan()
    with open("p3_cr_spell_equipped_items_receipt.json","w",
              encoding="utf8") as output:
        json.dump(result,output,ensure_ascii=False,sort_keys=True,indent=2)
    print("P3_CR_REAL_SPELL_EQUIPPED_ITEMS",
          json.dumps(result,ensure_ascii=False,sort_keys=True),flush=True)
