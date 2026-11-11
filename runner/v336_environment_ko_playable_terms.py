#!/usr/bin/env python3
"""v336: official Retail ko_KR playable terminology for Environment Build.

Game Data API English/Korean indices are cross-joined by physical Blizzard ID.
Specializations additionally require exact playable_class.id from individual
detail endpoints. This is DISPLAY metadata, not a new character acceptance
rule, SimC token alias, expansion/season discovery or DPS cache identity.
"""
from __future__ import annotations
import hashlib
import json
import os
import pathlib
import re
import tempfile
from concurrent.futures import ThreadPoolExecutor

import v106_user_session_controller as sessions
import v155_season_api_probe as blizzard

SCHEMA="v336_verified_official_playable_terms_ko_KR_v1"
BASE=blizzard.BLIZZARD_BASE+"/data/wow/"
QUERY="?namespace=static-kr&locale="
KINDS={"class":("playable-class","classes"),
       "spec":("playable-specialization","character_specializations"),
       "race":("playable-race","races")}
# SimC-supported race tokens already shown in the product. No new races are
# admitted from Blizzard names; dracthyr_visage is a SimC presentation alias
# and does NOT claim an independent API physical race ID.
RACES=("human","dwarf","night_elf","gnome","draenei","worgen",
       "pandaren","orc","undead","tauren","troll","blood_elf",
       "goblin","dracthyr","void_elf","lightforged_draenei",
       "dark_iron_dwarf","kul_tiran","mechagnome","earthen",
       "nightborne","highmountain_tauren","maghar_orc",
       "zandalari_troll","vulpera")
BUILD=re.compile(r"\d+(?:\.\d+){3}\Z")
KOREAN=re.compile(r"[가-힣]")
SHA=re.compile(r"[a-f0-9]{64}\Z")
MAX_DOC=750_000
MAX_INDEX_ROWS=350
SOURCE="BLIZZARD_OFFICIAL_GAME_DATA_API"

class TermBlocked(ValueError):
    pass

def need(ok,code):
    if not ok:raise TermBlocked(code)

def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False)

def sha(value):
    return hashlib.sha256(value if type(value) is bytes else
                           canonical(value).encode("utf8")).hexdigest()

def normalize(value):
    need(type(value) is str,"EN_NAME_NOT_STRING")
    return re.sub(r"[^a-z0-9]","",value.casefold())

def roster():
    pairs=sorted("/".join(pair) for pair in sessions.SUPPORTED)
    classes=sorted({x.split("/")[0] for x in pairs})
    need(len(pairs)==26 and len(classes)==13,
         "CURRENT_DPS_PRODUCT_ROSTER_NOT_26_13")
    return {"class":classes,"spec":pairs,"race":sorted(RACES)}

def roster_sha():
    return sha(roster())

def path_for(root,build):
    need(type(build) is str and BUILD.fullmatch(build) is not None,
         "GAME_BUILD_FORMAT")
    return (pathlib.Path(root).resolve()/"_fresh_season_sources"/
            ("wago_"+build)/"localization"/"v336_official_playable_ko_KR.json")

def url_for(kind,locale,detail_id=None):
    need(kind in KINDS and locale in ("en_US","ko_KR"),"REQUEST_KIND_OR_LOCALE")
    part=KINDS[kind][0]
    if detail_id is None:part+="/index"
    else:
        need(kind=="spec" and type(detail_id) is int and
             1<=detail_id<=999999,"DETAIL_NOT_SPECIALIZATION")
        part+="/"+str(detail_id)
    return BASE+part+QUERY+locale

def index_rows(kind,doc):
    need(kind in KINDS and type(doc) is dict,"INDEX_NOT_OBJECT")
    rows=doc.get(KINDS[kind][1])
    need(type(rows) is list and 1<=len(rows)<=MAX_INDEX_ROWS,
         "INDEX_ROWS_INVALID")
    by_id={}
    for row in rows:
        need(type(row) is dict and type(row.get("id")) is int and
             1<=row["id"]<=999999 and row["id"] not in by_id and
             type(row.get("name")) is str and
             1<=len(row["name"].strip())<=120,
             "INDEX_ROW_ID_OR_NAME_INVALID")
        by_id[row["id"]]=row["name"].strip()
    return by_id

def validated_indexes(source):
    """All 6 indices must match identity by ID across locale, not by order."""
    need(type(source) is dict and set(source)==
         {(k,loc) for k in KINDS for loc in ("en_US","ko_KR")},
         "SIX_LOCALE_INDEXES_REQUIRED")
    rows={}
    for kind in KINDS:
        en=index_rows(kind,source[kind,"en_US"])
        ko=index_rows(kind,source[kind,"ko_KR"])
        need(set(en)==set(ko),"CROSS_LOCALE_INDEX_ID_DRIFT")
        rows[kind]=(en,ko)
    return rows

def _display(name):
    need(type(name) is str and 1<=len(name)<=120 and
         KOREAN.search(name) is not None,"NOT_OFFICIAL_KOREAN_NAME")
    return name

def compile_terms(build,source,details):
    """Pure trusted-index → display projection, never SimC control rewrite."""
    roster_now=roster()
    all_indexes=validated_indexes(source)
    # English names are a candidate join only. Blizzard's immutable IDs are
    # the owner. Any missing/ambiguous mapping stays unverified/pending.
    class_en,class_ko=all_indexes["class"]
    class_matches={}
    for token in roster_now["class"]:
        hits=[i for i,name in class_en.items()
              if normalize(name)==normalize(token)]
        if len(hits)==1 and KOREAN.search(class_ko[hits[0]]):
            class_matches[token]={"id":hits[0],
                "name_ko":_display(class_ko[hits[0]])}
    need(len({x["id"] for x in class_matches.values()})==
         len(class_matches),"CLASS_CROSS_ID_COLLISION")

    spec_en,spec_ko=all_indexes["spec"]
    need(type(details) is dict,"DETAILS_NOT_OBJECT")
    candidates={}
    for key in roster_now["spec"]:
        cls,spec=key.split("/")
        if cls not in class_matches:continue
        hits=[i for i,name in spec_en.items()
              if normalize(name)==normalize(spec)]
        accepted=[]
        for i in hits:
            detail=details.get(i)
            if type(detail) is not dict or detail.get("id")!=i:continue
            owner=detail.get("playable_class")
            if (type(owner) is dict and type(owner.get("id")) is int and
                owner["id"]==class_matches[cls]["id"] and
                KOREAN.search(spec_ko[i])):
                accepted.append(i)
        if len(accepted)==1:
            candidates[key]={"id":accepted[0],"class_id":
                class_matches[cls]["id"],
                "name_ko":_display(spec_ko[accepted[0]])}
    need(len({x["id"] for x in candidates.values()})==
         len(candidates),"SPECIALIZATION_CROSS_ID_COLLISION")

    race_en,race_ko=all_indexes["race"]
    races={}
    for token in roster_now["race"]:
        hits=[i for i,name in race_en.items()
              if normalize(name)==normalize(token)]
        localized={race_ko[i] for i in hits}
        if hits and len(localized)==1 and
           KOREAN.search(next(iter(localized))):
            races[token]={"ids":sorted(hits),
                          "name_ko":_display(next(iter(localized)))}
    out={"schema":SCHEMA,"game_build":build,"locale":"ko_KR",
         "provider":SOURCE,"namespace":"static-kr",
         "roster_sha256":roster_sha(),
         "names":{"class":class_matches,"spec":candidates,"race":races},
         "missing":{kind:sorted(set(keys)-set({"class":class_matches,
             "spec":candidates,"race":races}[kind]))
             for kind,keys in roster_now.items()},
         "index_response_sha256":{
             kind:{loc:sha(source[kind,loc])
                   for loc in ("en_US","ko_KR")} for kind in KINDS},
         "spec_detail_response_sha256":{
             str(i):sha(doc) for i,doc in sorted(details.items())
             if type(i) is int and type(doc) is dict},
         "source_only_not_new_character_admission":True,
         "new_native_calls":0}
    out["status"]=("COMPLETE" if
                  all(not out["missing"][key] for key in KINDS)
                  else "PARTIAL_VERIFIED_NAMES")
    return {**out,"manifest_sha256":sha(out)}

def validate(doc,build):
    need(type(doc) is dict and doc.get("schema")==SCHEMA and
         doc.get("game_build")==build and doc.get("locale")=="ko_KR"
         and doc.get("provider")==SOURCE and
         doc.get("namespace")=="static-kr" and
         doc.get("roster_sha256")==roster_sha() and
         doc.get("source_only_not_new_character_admission") is True and
         doc.get("new_native_calls")==0 and
         doc.get("status") in ("COMPLETE","PARTIAL_VERIFIED_NAMES"),
         "TERMS_SCOPE_DRIFT")
    names=doc.get("names")
    need(type(names) is dict and set(names)==set(KINDS),"TERMS_GROUPS")
    expected=roster()
    for kind in KINDS:
        data=names[kind]
        need(type(data) is dict and set(data)<=set(expected[kind]),
             "TERM_OUTSIDE_PRODUCT_ROSTER")
        for key,value in data.items():
            need(type(value) is dict and
                 _display(value.get("name_ko")) is not None,
                 "TERM_DISPLAY_INVALID")
            if kind=="race":
                need(set(value)=={"ids","name_ko"} and
                     type(value["ids"]) is list and
                     1<=len(value["ids"])<=5 and
                     all(type(i) is int and i>0 for i in value["ids"]) and
                     value["ids"]==sorted(set(value["ids"])),
                     "RACE_PHYSICAL_IDS_INVALID")
            else:
                need(set(value)==({"id","name_ko"} if kind=="class"
                                  else {"id","class_id","name_ko"}) and
                     type(value["id"]) is int and value["id"]>0,
                     "CLASS_SPEC_PHYSICAL_ID_INVALID")
                if kind=="spec":
                    cls=key.split("/")[0]
                    need(cls in names["class"] and
                         value["class_id"]==names["class"][cls]["id"],
                         "SPEC_OWNER_NOT_MATCHED_TO_CLASS")
    missing=doc.get("missing")
    need(type(missing) is dict and set(missing)==set(KINDS) and
         all(missing[k]==sorted(set(expected[k])-set(names[k]))
             for k in KINDS),"MISSING_NOT_EXACT")
    need(doc["status"]==("COMPLETE" if all(not missing[k] for k in KINDS)
         else "PARTIAL_VERIFIED_NAMES"),"COMPLETENESS_FALSE")
    proofs=doc.get("index_response_sha256")
    need(type(proofs) is dict and set(proofs)==set(KINDS) and
         all(type(proofs[k]) is dict and set(proofs[k])==
             {"en_US","ko_KR"} and
             all(type(x) is str and SHA.fullmatch(x)
                 for x in proofs[k].values()) for k in KINDS),
         "INDEX_PROOF_SHAS_INVALID")
    details=doc.get("spec_detail_response_sha256")
    need(type(details) is dict and len(details)<=100 and
         all(type(k) is str and k.isdecimal() and type(v) is str
             and SHA.fullmatch(v) for k,v in details.items()),
         "SPEC_DETAIL_PROOF_SHAS_INVALID")
    signature=doc.get("manifest_sha256")
    need(type(signature) is str and SHA.fullmatch(signature) and
         signature==sha({k:v for k,v in doc.items()
                         if k!="manifest_sha256"}),"TERM_MANIFEST_INVALID")
    return doc

def read(root,build):
    try:
        path=path_for(root,build)
        if not path.is_file() or path.is_symlink() or \
           not 0<path.stat().st_size<=MAX_DOC:return None
        doc=json.loads(path.read_text(encoding="utf8"))
        return validate(doc,build)
    except (TermBlocked,TypeError,ValueError,OSError,KeyError):return None

def public(root,build):
    # Read-only; never expose physical evidence JSON or credentials in HTTP.
    need(type(build) is str and BUILD.fullmatch(build) is not None,
         "GAME_BUILD_FORMAT")
    doc=read(root,build)
    if doc is None:
        return {"schema":SCHEMA,"game_build":build,
                "status":"NO_VERIFIED_OFFICIAL_TERMS",
                "names":{"class":{},"spec":{},"race":{}},
                "native_calls_now":0,"network_calls_now":0}
    return {"schema":SCHEMA,"game_build":build,"status":doc["status"],
            "names":{kind:{key:value["name_ko"]
                 for key,value in doc["names"][kind].items()}
                 for kind in KINDS},
            "verified_count":sum(len(doc["names"][kind]) for kind in KINDS),
            "missing_count":sum(len(doc["missing"][kind]) for kind in KINDS),
            "native_calls_now":0,"network_calls_now":0}

def _save(root,build,doc):
    path=path_for(root,build)
    raw=(json.dumps(validate(doc,build),sort_keys=True,
                    ensure_ascii=False,indent=2)+"\n").encode("utf8")
    need(len(raw)<=MAX_DOC,"TERMS_SOURCE_TOO_LARGE")
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.is_file() and path.read_bytes()==raw:return
    with tempfile.NamedTemporaryFile(mode="wb",dir=path.parent,
                   prefix=".v336-",delete=False) as output:
        tmp=pathlib.Path(output.name)
        output.write(raw);output.flush();os.fsync(output.fileno())
    try:os.replace(tmp,path)
    finally:tmp.unlink(missing_ok=True)

def build_for_environment(root,build,*,token=None,request_json=None):
    """Incremental once-per-game-build official-source refresh; zero Native."""
    need(type(build) is str and BUILD.fullmatch(build) is not None,
         "GAME_BUILD_FORMAT")
    cached=read(root,build)
    if cached is not None:
        return {"schema":SCHEMA,"game_build":build,"status":cached["status"],
                "verified_count":sum(len(x) for x in cached["names"].values()),
                "missing_count":sum(len(x) for x in cached["missing"].values()),
                "reused_same_build_cache":True,"network_calls_now":0,
                "native_calls_now":0}
    fetch=request_json or blizzard.request_json
    if not token:token=os.getenv("BLIZZARD_ACCESS_TOKEN")
    network_calls=0
    if not token:
        client=os.getenv("BLIZZARD_CLIENT_ID")
        secret=os.getenv("BLIZZARD_CLIENT_SECRET")
        if not client or not secret:
            return {"schema":SCHEMA,"game_build":build,
                    "status":"CREDENTIALS_UNAVAILABLE_TERMS_PENDING",
                    "reused_same_build_cache":False,
                    "network_calls_now":0,"native_calls_now":0}
        try:token=blizzard.oauth_token(blizzard.BLIZZARD_TOKEN_URL,
                                      client,secret)
        except Exception:
            return {"schema":SCHEMA,"game_build":build,
                    "status":"OFFICIAL_TERMS_SOURCE_UNAVAILABLE",
                    "network_calls_now":1,"native_calls_now":0}
        network_calls+=1
    source={}
    for kind in KINDS:
        for locale in ("en_US","ko_KR"):
            try:
                source[kind,locale]=fetch(url_for(kind,locale),headers={
                    "Authorization":"Bearer "+token})
            except Exception:
                return {"schema":SCHEMA,"game_build":build,
                        "status":"OFFICIAL_TERMS_SOURCE_UNAVAILABLE",
                        "network_calls_now":network_calls+1,
                        "native_calls_now":0}
            network_calls+=1
    en=validated_indexes(source)
    specs=en["spec"][0]
    requested_specs={key.split("/")[1] for key in roster()["spec"]}
    matched=sorted(i for i,name in specs.items()
                   if normalize(name) in {normalize(k)
                                          for k in requested_specs})
    need(len(matched)<=100,"SPEC_DETAIL_CALL_BOUND")
    def get(i):
        try:
            return (i,fetch(url_for("spec","en_US",i),headers={
                "Authorization":"Bearer "+token}),None)
        except Exception as exc:
            return (i,None,type(exc).__name__)
    with ThreadPoolExecutor(max_workers=4) as pool:
        answers=list(pool.map(get,matched))
    details={i:doc for i,doc,error in answers if doc is not None}
    document=compile_terms(build,source,details)
    validate(document,build)
    _save(root,build,document)
    return {"schema":SCHEMA,"game_build":build,
            "status":document["status"],
            "verified_count":sum(len(x) for x in document["names"].values()),
            "missing_count":sum(len(x) for x in document["missing"].values()),
            "reused_same_build_cache":False,
            "network_calls_now":network_calls+len(matched),
            "native_calls_now":0,
            "detail_failures":sum(error is not None
                                  for _,_,error in answers)}
