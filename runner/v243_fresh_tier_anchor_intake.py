#!/usr/bin/env python3
"""v243: new-season tier title intake for EXISTING v168, not a new gear DB.

Fetch a current public class-set publication and a pinned-build Wago ItemSet
table. Match every *full set title* to a single ItemSet.Name_lang and class
label, then let the original v168 prove all 65 physical pieces from the
already sealed v161 ItemSparse/Item snapshot. Never seed old set/item IDs.
"""
from __future__ import annotations

import csv
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import v168_current_season_tier_discovery as tier
import v217_stage_execution_engine as stages

SOURCE_URL = "https://guildloot.de/en/set/retail/"
SET_CSV_URL = "https://wago.tools/db2/ItemSet/csv"
MAX_PUBLISHER_BYTES = 4_000_000
MAX_ITEMSET_BYTES = 24_000_000
SCHEMA = "v243_fresh_season_tier_title_intake_v1"
ALIASES = {
    "deathknight": "Death Knight", "demonhunter": "Demon Hunter",
    "druid": "Druid", "evoker": "Evoker", "hunter": "Hunter",
    "mage": "Mage", "monk": "Monk", "paladin": "Paladin",
    "priest": "Priest", "rogue": "Rogue", "shaman": "Shaman",
    "warlock": "Warlock", "warrior": "Warrior",
}

class TierSourceBlocked(ValueError):
    pass

def need(ok, reason):
    if not ok:
        raise TierSourceBlocked(reason)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def compact(text):
    return re.sub(r"[^a-z0-9]", "", text.casefold())

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.hidden += 1
        if not self.hidden and tag in ("div","section","p","li","h1","h2",
                                        "h3","h4","br","article"):
            self.parts.append(" ")
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self.hidden:
            self.hidden -= 1
        elif not self.hidden and tag in ("div","section","p","li","h1","h2",
                                        "h3","h4","br","article"):
            self.parts.append(" ")
    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(" ")
            self.parts.append(data)

def visible(raw):
    try:
        parser=VisibleText()
        parser.feed(raw.decode("utf-8-sig"))
    except (UnicodeError,ValueError) as exc:
        raise TierSourceBlocked("TIER_PUBLISHER_HTML_UNREADABLE") from exc
    return " ".join("".join(parser.parts).split())

def itemset_rows(raw):
    need(0 < len(raw) <= MAX_ITEMSET_BYTES,"TIER_ITEMSET_CSV_SIZE_INVALID")
    try:
        source=io.StringIO(raw.decode("utf-8-sig"),newline="")
        reader=csv.DictReader(source)
        need(reader.fieldnames and {"ID","Name_lang"}<=set(reader.fieldnames),
             "TIER_ITEMSET_CSV_SCHEMA_INVALID")
        parsed={}
        for n,row in enumerate(reader):
            need(n<100000,"TIER_ITEMSET_ROW_LIMIT")
            try:
                iid=int(row["ID"])
            except (TypeError,ValueError) as exc:
                raise TierSourceBlocked("TIER_ITEMSET_ID_INVALID") from exc
            if iid>0 and row["Name_lang"].strip():
                need(iid not in parsed,"TIER_ITEMSET_DUPLICATE_ID")
                parsed[iid]=row["Name_lang"].strip()
        return parsed
    except (UnicodeError,csv.Error) as exc:
        raise TierSourceBlocked("TIER_ITEMSET_CSV_UNREADABLE") from exc

def parse_anchor(*,publisher_raw,itemset_raw,build,expansion_id,mplus_zone):
    need(type(build) is str and re.fullmatch(
        r"[0-9]+(?:\.[0-9]+){3}", build) is not None,
        "TIER_EXPLICIT_BUILD_INVALID")
    need(type(expansion_id) is int and expansion_id>0,
         "TIER_EXPANSION_ID_REQUIRED")
    need(type(mplus_zone) is str and mplus_zone,
         "TIER_CURRENT_SEASON_ZONE_REQUIRED")
    body=visible(publisher_raw)
    # Deliberately require independently named M+ season to agree with the
    # publisher's current-season headline, not with historic item IDs.
    mplus=re.search(r"\bseason\s*(\d+)\b",mplus_zone,re.I)
    header=re.search(r"\bseason\s*(\d+)\b",body[:1200],re.I)
    need(mplus is not None and header is not None and
         mplus.group(1)==header.group(1),
         "TIER_PUBLISHER_SEASON_MISMATCH_OR_UNPROVEN")
    names=itemset_rows(itemset_raw)
    needle=compact(body)
    chosen={};labels={}
    for cl,alias in ALIASES.items():
        possibles=[(iid,name) for iid,name in names.items()
                   if compact(alias)+compact(name) in needle]
        need(len(possibles)==1,
             "TIER_PUBLISHER_CLASS_ITEMSET_NOT_UNIQUE:"+cl)
        chosen[cl],labels[cl]=possibles[0]
    need(len(set(chosen.values()))==len(ALIASES),
         "TIER_ITEMSET_CLASS_COLLISION")
    return {
        "schema":tier.SOURCE_SCHEMA,
        "season":"fresh_retail_s"+mplus.group(1),
        "retail_build":build,"expansion_id":expansion_id,
        "source_url":SOURCE_URL,
        "source_description":"Fresh live publisher class-name and exact pinned ItemSet.Name_lang title relation",
        "classes":labels,"verified_item_set_ids":chosen,
        "publisher_html_sha256":digest(publisher_raw),
        "itemset_csv_sha256":digest(itemset_raw),
        "publisher_season":int(mplus.group(1)),
        "policy":"SOURCE_FIRST_SAME_BUILD_MATCH_CLASS_NAME_AND_ITEMSET_NOT_OLD_PROFILE_IDS",
        "native_item_set_effect_certified":False,
    }

def fetch_bytes(url,limit,*,transport=urlopen):
    need(url==SOURCE_URL or url.startswith(SET_CSV_URL+"?"),
         "TIER_REMOTE_URL_NOT_ALLOWED")
    req=Request(url,headers={"User-Agent":"SIMC-Secondary-Season-Source/1.0",
                             "Accept":"text/html,text/csv"})
    try:
        with transport(req,timeout=45) as response:
            need(response.status==200,"TIER_REMOTE_HTTP_NOT_200")
            out=io.BytesIO()
            while True:
                block=response.read(262144)
                if not block:
                    break
                need(out.tell()+len(block)<=limit,
                     "TIER_REMOTE_SOURCE_SIZE_LIMIT")
                out.write(block)
            need(out.tell()>0,"TIER_REMOTE_SOURCE_EMPTY")
            return out.getvalue()
    except (HTTPError,URLError,TimeoutError,OSError) as exc:
        raise TierSourceBlocked("TIER_REMOTE_TRANSPORT_FAILED") from exc

def build_from_public_source(*,stage_root,wago_folder,build,expansion_id,
                             mplus_zone,wago_receipt_sha256,transport=None):
    root=Path(stage_root).expanduser()
    need(root.is_dir() and not root.is_symlink(),
         "TIER_STAGE_ROOT_INVALID")
    folder=Path(wago_folder).expanduser()
    need(folder.is_dir() and not folder.is_symlink(),
         "TIER_WAGO_FOLDER_INVALID")
    need(type(wago_receipt_sha256) is str and
         re.fullmatch(r"[0-9a-f]{64}",wago_receipt_sha256) is not None,
         "TIER_WAGO_RECEIPT_SHA_INVALID")
    csv_url=SET_CSV_URL+"?"+urlencode({"build":build,"locale":"enUS"})
    output={
        "publisher":"source/tier_publisher.html",
        "itemset":"source/ItemSet.csv",
        "anchors":"source/tier_anchors.json",
        "tier":"source/v168_current_tier_candidates.json",
    }
    paths={k:root/v for k,v in output.items()}
    fingerprint=stages.module_dependency_fingerprint(
        [Path(__file__),Path(tier.__file__),Path(stages.__file__)])
    def execute():
        opts={} if transport is None else {"transport":transport}
        publisher=fetch_bytes(SOURCE_URL,MAX_PUBLISHER_BYTES,**opts)
        itemset=fetch_bytes(csv_url,MAX_ITEMSET_BYTES,**opts)
        anchor=parse_anchor(publisher_raw=publisher,itemset_raw=itemset,
                            build=build,expansion_id=expansion_id,
                            mplus_zone=mplus_zone)
        for p in paths.values():
            p.parent.mkdir(parents=True,exist_ok=True)
        paths["publisher"].write_bytes(publisher)
        paths["itemset"].write_bytes(itemset)
        paths["anchors"].write_text(json.dumps(anchor,sort_keys=True,
            ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        # Existing v216 sealed/checked v161 snapshot before this call.
        # v168 remains authoritative for all 65 actual physical item IDs.
        physical=tier.discover(anchor,folder/"ItemSparse.csv",
                               folder/"Item.csv",receipt=None)
        paths["tier"].write_text(json.dumps(physical,sort_keys=True,
            ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    def validate(files):
        anchor=json.loads(files["anchors"].read_text("utf8"))
        physical=json.loads(files["tier"].read_text("utf8"))
        return (anchor.get("schema")==tier.SOURCE_SCHEMA
                and anchor.get("retail_build")==build
                and anchor.get("expansion_id")==expansion_id
                and anchor.get("publisher_html_sha256")==
                    digest(files["publisher"].read_bytes())
                and anchor.get("itemset_csv_sha256")==
                    digest(files["itemset"].read_bytes())
                and physical.get("status")==
                    "SOURCE_VERIFIED_13_CLASS_FIVE_PIECE_IDS"
                and physical.get("class_count")==13
                and physical.get("item_count")==65
                and physical.get("retail_build")==build
                and physical.get("native_calls")==0
                and physical.get("production_profile_promoted") is False)
    try:
        stage=stages.execute_stage(
            root=root,stage_id="fresh-tier-publisher-itemset-v168",
            stage_version="v243-exact-set-name-v1",
            inputs={"game_build":build,"expansion_id":expansion_id,
                    "mplus_zone":mplus_zone,
                    "wago_receipt_sha256":wago_receipt_sha256,
                    "publisher_url":SOURCE_URL,"itemset_url":csv_url,
                    "code_sha256":fingerprint["sha256"]},
            outputs=output,execute=execute,validate=validate)
    except stages.StageExecutionBlocked as exc:
        raise TierSourceBlocked("TIER_SOURCE_STAGE_BLOCKED:"+str(exc)) from exc
    return {
        "schema":SCHEMA,"status":"CURRENT_SET_NAMES_AND_65_PHYSICAL_IDS_VERIFIED",
        "anchors_path":str(paths["anchors"].resolve()),
        "tier_candidate_path":str(paths["tier"].resolve()),
        "publisher_url":SOURCE_URL,"itemset_url":csv_url,
        "source_stage":{k:v for k,v in stage.items() if k!="result"},
        "network_calls_by_stage":2 if stage["executed"] else 0,
        "native_calls":0,"environment_ready":False,
        "environment_installed":False,
        "no_previous_season_item_ids_used":True,
        "season_membership_completely_verified":False,
    }
