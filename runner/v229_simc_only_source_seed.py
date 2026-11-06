#!/usr/bin/env python3
"""v229 SimC-only source-first collector and *candidate* inventory.

Cold-start capable: no historical gear/consumable data, installed references,
old Native evidence, cached DPS/static outputs, Blizzard or Wago network.
The only permitted network origins are GitHub's simulationcraft/simc Git trees
and raw generated files at one exact 40-hex commit.

The SimC-generated set rows establish IDs/relationships; they do NOT on their
own select the active season, determine slot/type, prove any item level's G,
identify gem item IDs, or quantify highest-quality J/F/O. This module never
promotes the product environment or executes Native.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.error import HTTPError
from urllib.request import Request, urlopen

try:
    from . import v191_unified_season_data_update as generated_parser
except ImportError:
    import v191_unified_season_data_update as generated_parser

SCHEMA = "v229_simc_only_first_party_source_seed_v1"
RECEIPT = "simc_seed_receipt.json"
SOURCE_FILES = {
    "item_set_bonus.inc": 600_000,
    "gem_data.inc": 600_000,
    "temporary_enchant.inc": 100_000,
}
OPTIONAL_ITEM_FILE = "item_data.inc"
MAX_ITEM_FILE = 32_000_000
REV = re.compile(r"[a-f0-9]{40}\Z")
BUILD = re.compile(r"\d+(?:\.\d+){3}\Z")
HEX = re.compile(r"[a-f0-9]{40}\Z")
SET_HEAD = re.compile(r"^// Set bonus data, wow build (\d+(?:\.\d+){3})$")
SET_COUNT = re.compile(r"std::array<item_set_bonus_t,\s*(\d+)>")
SET_ROW = re.compile(
    r'^\s*\{\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*'
    r'(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*'
    r'(-?\d+)\s*,\s*(-?\d+)\s*,\s*(\d+)\s*,\s*'
    r'\{\s*([\d,\s]+)\s*\}\s*\}\s*,?\s*$')
ITEM_HEAD = re.compile(rb"(?m)^// Items, ilevel [0-9]+-[0-9]+, wow build ([0-9]+(?:\.[0-9]+){3})\r?$")
BASE = "https://api.github.com/repos/simulationcraft/simc/git/trees/"
RAW_BASE = "https://raw.githubusercontent.com/simulationcraft/simc/"
# Same exact Git tree blob, no repo/branch/content search or guessed source.
GIT_BLOB_BASE = "https://api.github.com/repos/simulationcraft/simc/git/blobs/"


class SimCSourceBlocked(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise SimCSourceBlocked(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(data):
    return json.dumps(data,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False)


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") +
                        b"\x00" + raw).hexdigest()


def bounded_read(path, limit):
    path=Path(path)
    need(path.is_file() and not path.is_symlink() and
         0 < path.stat().st_size <= limit,
         "V229_SIMC_SOURCE_MISSING_OR_SIZE_UNSAFE:" + path.name)
    raw=path.read_bytes()
    need(len(raw) <= limit, "V229_SIMC_FILE_CHANGED_DURING_READ")
    return raw


def parse_set_bonus(raw, build):
    try:
        text=raw.decode("utf8")
    except UnicodeError as exc:
        raise SimCSourceBlocked("V229_SET_SOURCE_NON_UTF8") from exc
    lines=text.splitlines()
    need(len(lines)>=3 and (m:=SET_HEAD.fullmatch(lines[0])) is not None and
         m.group(1)==build and
         (n:=SET_COUNT.search(lines[1])) is not None,
         "V229_SET_BONUS_BUILD_OR_HEADER_MISMATCH")
    declared=int(n.group(1))
    need(0<declared<=20000, "V229_SET_ROWS_UNSAFE")
    rows=[]
    for line in lines:
        if not line.lstrip().startswith("{"):
            continue
        m=SET_ROW.fullmatch(line)
        need(m is not None, "V229_SET_BONUS_ROW_UNRECOGNIZED")
        name,opt,tier,enum,setid,bns,cls,spec,trait,spell,ids=m.groups()
        item_ids=[int(i.strip()) for i in ids.split(",")]
        need(len(item_ids)>=3 and item_ids[-1]==0 and
             all(x>=0 for x in item_ids) and
             len(set(x for x in item_ids if x))==len(item_ids)-1,
             "V229_SET_BONUS_ITEM_IDS_INVALID")
        need(int(setid)>0 and int(bns)>0 and int(spell)>0,
             "V229_SET_BONUS_NUMERIC_INVALID")
        rows.append({"set_name":name,"set_opt":opt,"tier":tier,
                     "enum":int(enum),"set_id":int(setid),
                     "bonus":int(bns),"class_id":int(cls),
                     "spec_id":int(spec),"trait":int(trait),
                     "spell_id":int(spell),"item_ids":item_ids[:-1]})
    need(len(rows)==declared, "V229_SET_BONUS_ROW_COUNT_DRIFT")
    # Dedup a class's 2pc/4pc/spec variants without erasing the class/IDs.
    groups={}
    for row in rows:
        key=(row["set_opt"],row["set_id"],row["class_id"])
        k="|".join(map(str,key))
        val=groups.setdefault(k,{"set_opt":row["set_opt"],
            "set_id":row["set_id"],"class_id":row["class_id"],
            "tier":row["tier"],"item_ids":row["item_ids"],
            "observed_bonus_sizes":[]})
        need(val["tier"]==row["tier"] and
             val["item_ids"]==row["item_ids"],
             "V229_SET_BONUS_CLASS_GROUP_CONFLICT")
        val["observed_bonus_sizes"].append(row["bonus"])
    results=[]
    for value in groups.values():
        value["observed_bonus_sizes"]=sorted(set(value["observed_bonus_sizes"]))
        results.append(value)
    return {"raw_rows":len(rows),"distinct_class_set_candidates":len(results),
            "candidate_groups":sorted(results,key=lambda v:(
                v["set_opt"],v["class_id"],v["set_id"]))}


def inventory(source_bytes, *, simc_revision, expected_build,
              expected_git_blob=None, previous_game_build=None,
              season_event="season_change"):
    """Identify only SimC first-party source facts; never auto-approve stats."""
    need(type(simc_revision) is str and REV.fullmatch(simc_revision) and
         type(expected_build) is str and BUILD.fullmatch(expected_build) and
         season_event in ("season_change","expansion_change","mid_patch",
                          "cold_start"),
         "V229_PINNED_SIMC_REVISION_BUILD_OR_EVENT_INVALID")
    # A previous local client-build record is optional and only historical.
    # Same-season SimC updates and even a new season can share a game build.
    # The generated SimC source's OWN build is still verified strictly below.
    need(previous_game_build is None or
         (type(previous_game_build) is str and
          BUILD.fullmatch(previous_game_build) is not None),
         "V229_PREVIOUS_GAME_BUILD_RECORD_INVALID")
    if season_event == "cold_start":
        # Preserve the legacy source-only label for already issued receipts.
        # It denotes no LOCAL record, not a missing WoW historical build.
        need(previous_game_build is None,
             "V229_COLD_START_MUST_HAVE_NO_PRIOR_BUILD")
    need(type(source_bytes) is dict and
         set(SOURCE_FILES)<=set(source_bytes) and
         set(source_bytes)<=set(SOURCE_FILES)|{OPTIONAL_ITEM_FILE},
         "V229_FIXED_SIMC_GENERATED_FILES_ONLY")
    if expected_git_blob is not None:
        need(type(expected_git_blob) is dict and
             set(expected_git_blob)==set(source_bytes),
             "V229_SIMC_TREE_BLOB_PROOF_MISSING")
    provenance={}
    for name,raw in source_bytes.items():
        lim=SOURCE_FILES.get(name,MAX_ITEM_FILE)
        need(type(raw) is bytes and 0<len(raw)<=lim,
             "V229_UNSAFE_SIMC_GENERATED_FILE:"+name)
        blob=git_blob(raw)
        if expected_git_blob is not None:
            need(type(expected_git_blob[name]) is str and
                 HEX.fullmatch(expected_git_blob[name]) and
                 blob==expected_git_blob[name],
                 "V229_PINNED_SIMC_GIT_BLOB_MISMATCH:"+name)
        provenance[name]={"sha256":digest(raw),"git_blob_sha1":blob,
                          "bytes":len(raw),
                          "pinned_url":RAW_BASE+simc_revision+
                            "/engine/dbc/generated/"+name}
    sets=parse_set_bonus(source_bytes["item_set_bonus.inc"],expected_build)
    for key,kind in (("gem_data.inc","gem_property"),
                     ("temporary_enchant.inc","temporary_enchant")):
        try:
            doc=generated_parser.parse_generated(
                kind,source_bytes[key])
        except (generated_parser.CatalogBlocked,UnicodeError,
                KeyError,ValueError) as exc:
            raise SimCSourceBlocked(
                "V229_SIMC_GENERATED_PARSER_REJECTED:"+key) from exc
        need(doc["source_build"]==expected_build,
             "V229_GENERATED_SIMC_COMPILED_BUILD_MISMATCH:"+key)
        provenance[key]["source_build"]=doc["source_build"]
        provenance[key]["source_row_count"]=doc["declared_rows"]
    if OPTIONAL_ITEM_FILE in source_bytes:
        # The generated item source starts with a potentially huge stat
        # array. Its genuine item-level/build header occurs afterward.
        # Scan raw bytes once, without allocating another decoded copy.
        found=ITEM_HEAD.search(source_bytes[OPTIONAL_ITEM_FILE])
        need(found is not None and
             found.group(1)==expected_build.encode("ascii"),
             "V229_ITEM_DATA_BUILT_FOR_DIFFERENT_GAME_BUILD")
        provenance[OPTIONAL_ITEM_FILE]["source_build"]=expected_build
    # Never select 'newest' season by lexicographic tier token or item IDs.
    # SimC's set tables contain historic sets as well as current sets.
    output={
        "schema":SCHEMA,
        "status":"SIMC_ONLY_SOURCE_CANDIDATES_NOT_ENVIRONMENT_BUILT",
        "simc_revision":simc_revision,
        "simc_generated_build":expected_build,
        "previous_game_build":previous_game_build,
        "season_event":season_event,
        "source_files":provenance,
        "set_bonus_source_rows":sets["raw_rows"],
        "candidate_class_set_count":sets["distinct_class_set_candidates"],
        "set_bonus_candidate_groups":sets["candidate_groups"],
        "gem_property_candidate_count":
            provenance["gem_data.inc"]["source_row_count"],
        "temporary_enchant_candidate_count":
            provenance["temporary_enchant.inc"]["source_row_count"],
        "item_data_present":OPTIONAL_ITEM_FILE in source_bytes,
        "active_season_not_automatically_inferred":True,
        "G":None,"J":None,"F":None,"O":None,"B":None,"T":None,
        "environment_ready":False,"user_options_auto_admitted":False,
        "native_calls":0,
        "provenance_tree_blob_authenticated":
            expected_git_blob is not None,
        "missing_proofs":[
            "CURRENT_SEASON_CLASS_TIER_SELECTION_AND_SLOT_RELATION",
            "REPRESENTATIVE_NONTRINKET_EQUIPMENT_CANDIDATES",
            "NATIVE_STATIC_TARGET_ILVL_G",
            "GEM_ITEM_ID_QUALITY_SOCKET_J",
            "FLASK_EFFECT_QUALITY_F",
            "WEAPON_OIL_ITEM_ID_HANDS_RATING_O",
            "VALIDATED_B_T_PRODUCT_PROFILE",
        ],
    }
    return {**output,"receipt_sha256":digest(
        canonical(output).encode("utf8"))}


def _github_api_headers(accept):
    """Optional ephemeral read token for GitHub API only, never raw/Wago.

    Actions supplies this through the step environment; no token is logged,
    serialized, hashed into static cache identity or sent to other hosts.
    """
    headers={"User-Agent":"SIMC-Secondary-source-cold-start/1.0",
             "Accept":accept}
    token=os.environ.get("SIMC_SOURCE_GITHUB_API_TOKEN","")
    if token:
        need(len(token)<=2048 and token==token.strip() and
             "\\r" not in token and "\\n" not in token,
             "V229_GITHUB_API_TOKEN_FORMAT_INVALID")
        headers["Authorization"]="Bearer "+token
    return headers


def _http_json(url, transport=urlopen):
    req=Request(url,headers=_github_api_headers(
        "application/vnd.github+json"))
    with transport(req,timeout=25) as res:
        need(res.status==200,"V229_UPSTREAM_GIT_TREE_HTTP_INVALID")
        raw=res.read(600_001)
    need(0<len(raw)<=600_000,"V229_GIT_TREE_JSON_SIZE")
    try:
        return json.loads(raw)
    except (UnicodeError,ValueError) as exc:
        raise SimCSourceBlocked("V229_UPSTREAM_GIT_TREE_JSON_INVALID") from exc



def resolve_exact_commit(revision_hint, *, transport=urlopen):
    """Resolve a user/installed SimC 7-12 hex revision to ONE Git commit.

    The exact 40-hex source tree is independently rechecked by the caller's
    existing discover_generated_tree/inventory. This does NOT authenticate a
    separately supplied binary or infer a season from a commit's timestamp.
    """
    need(type(revision_hint) is str and
         re.fullmatch(r"[a-f0-9]{7,12}|[a-f0-9]{40}",
                      revision_hint) is not None,
         "V229_SOURCE_REVISION_HINT_INVALID")
    if REV.fullmatch(revision_hint):
        return revision_hint
    url=("https://api.github.com/repos/simulationcraft/simc/commits/"
         +revision_hint)
    request=Request(url,headers=_github_api_headers(
        "application/vnd.github+json"))
    with transport(request,timeout=25) as response:
        need(response.status==200,"V229_REVISION_LOOKUP_HTTP_INVALID")
        raw=response.read(120_001)
    need(0<len(raw)<=120_000,"V229_REVISION_LOOKUP_RESPONSE_TOO_LARGE")
    try:
        doc=json.loads(raw)
    except (UnicodeError,ValueError) as exc:
        raise SimCSourceBlocked("V229_REVISION_LOOKUP_JSON_INVALID") from exc
    exact=doc.get("sha") if type(doc) is dict else None
    need(type(exact) is str and REV.fullmatch(exact) is not None
         and exact.startswith(revision_hint),
         "V229_REVISION_LOOKUP_IDENTITY_MISMATCH")
    return exact


def discover_generated_tree(revision, *, transport=urlopen):
    """Walk 4 fixed first-party Git tree levels, not whole repo/history."""
    need(type(revision) is str and REV.fullmatch(revision),
         "V229_IMMUTABLE_SIMC_COMMIT_REQUIRED")
    tree=revision
    for component in ("engine","dbc","generated"):
        doc=_http_json(BASE+tree,transport)
        rows=doc.get("tree") if type(doc) is dict else None
        need(type(rows) is list and doc.get("truncated") is not True,
             "V229_SIMC_GIT_TREE_INCOMPLETE")
        matches=[x for x in rows if x.get("path")==component and
                 x.get("type")=="tree"]
        need(len(matches)==1 and type(matches[0].get("sha")) is str and
             HEX.fullmatch(matches[0]["sha"]),
             "V229_SIMC_GIT_TREE_PATH_MISSING:"+component)
        tree=matches[0]["sha"]
    doc=_http_json(BASE+tree,transport)
    rows=doc.get("tree") if type(doc) is dict else None
    need(type(rows) is list and doc.get("truncated") is not True,
         "V229_SIMC_GENERATED_TREE_INCOMPLETE")
    known={}
    for name in (*SOURCE_FILES,OPTIONAL_ITEM_FILE):
        matches=[x for x in rows if x.get("path")==name and
                 x.get("type")=="blob"]
        need(len(matches)==1 and type(matches[0].get("sha")) is str and
             HEX.fullmatch(matches[0]["sha"]),
             "V229_SIMC_GENERATED_FILE_NOT_IN_PINNED_TREE:"+name)
        known[name]={"sha":matches[0]["sha"],"size":matches[0]["size"]}
    return known



def fetch_generated_blob(*, revision, name, expected_sha, expected_size,
                         transport=urlopen, timeout=90):
    """Only raw HTTP 403 may use GitHub's SAME verified git-tree blob.

    The exact 40-hex SHA and size must have come from discover_generated_tree,
    not from a 403 response or caller-selected filename. Original callers
    retain their final Git-blob/build checks. No general retry or new mirror.
    """
    need(type(revision) is str and REV.fullmatch(revision) is not None and
         name in (*SOURCE_FILES, OPTIONAL_ITEM_FILE) and
         type(expected_sha) is str and HEX.fullmatch(expected_sha) is not None and
         type(expected_size) is int and
         0 < expected_size <= SOURCE_FILES.get(name,MAX_ITEM_FILE),
         "V229_PINNED_BLOB_REQUEST_INVALID")
    raw_url=RAW_BASE+revision+"/engine/dbc/generated/"+name
    request=Request(raw_url,headers={
        "User-Agent":"SIMC-Secondary-source-cold-start/1.0"})
    try:
        with transport(request,timeout=timeout) as response:
            need(response.status==200,"V229_UPSTREAM_SIMC_SOURCE_HTTP")
            return response.read(expected_size+1)
    except HTTPError as exc:
        if exc.code!=403:
            raise
    # Raw host rejected the request, not the provenance. GitHub's canonical
    # git-blobs API supports raw+json; some intermediaries return JSON anyway.
    # Both representations are accepted ONLY if the exact pinned blob matches.
    request=Request(GIT_BLOB_BASE+expected_sha,headers=_github_api_headers(
        "application/vnd.github.raw+json"))
    max_encoded=((expected_size+2)//3)*4+8192
    with transport(request,timeout=timeout) as response:
        need(response.status==200,"V229_EXACT_GIT_BLOB_API_HTTP")
        candidate=response.read(max_encoded+1)
    need(0<len(candidate)<=max_encoded,
         "V229_EXACT_GIT_BLOB_API_RESPONSE_SIZE_INVALID")
    if (len(candidate)==expected_size and git_blob(candidate)==expected_sha):
        return candidate
    try:
        document=json.loads(candidate)
        need(type(document) is dict and
             document.get("sha")==expected_sha and
             document.get("size")==expected_size and
             document.get("encoding")=="base64" and
             type(document.get("content")) is str and
             len(document["content"])<=((expected_size+2)//3)*4+4096,
             "V229_EXACT_GIT_BLOB_API_IDENTITY_INVALID")
        data=base64.b64decode(document["content"],validate=False)
    except (ValueError,TypeError,UnicodeError,binascii.Error) as exc:
        raise SimCSourceBlocked(
            "V229_EXACT_GIT_BLOB_API_CONTENT_INVALID") from exc
    need(len(data)==expected_size and git_blob(data)==expected_sha,
         "V229_EXACT_GIT_BLOB_API_CONTENT_SHA_MISMATCH")
    return data


def collect(*, revision, expected_build, dest, previous_game_build,
            season_event="season_change", include_item_data=False,
            transport=urlopen):
    """Explicit request only. Atomic new folder; no historical references."""
    need(type(include_item_data) is bool,"V229_ITEM_DATA_OPT_IN_BOOLEAN")
    dest=Path(dest)
    need(not dest.exists() and dest.parent.is_dir(),
         "V229_COLLECTION_DESTINATION_MUST_BE_NEW")
    candidates=discover_generated_tree(revision,transport=transport)
    names=list(SOURCE_FILES)
    if include_item_data:
        names.append(OPTIONAL_ITEM_FILE)
    raws={}
    git_shas={}
    with tempfile.TemporaryDirectory(prefix="simc-source-new-",dir=dest.parent) as tmp:
        root=Path(tmp)
        for name in names:
            size=candidates[name]["size"]
            limit=SOURCE_FILES.get(name,MAX_ITEM_FILE)
            need(type(size) is int and 0<size<=limit,
                 "V229_UPSTREAM_SIMC_SOURCE_SIZE_LIMIT:"+name)
            data=fetch_generated_blob(
                revision=revision,name=name,
                expected_sha=candidates[name]["sha"],expected_size=size,
                transport=transport,timeout=90)
            need(len(data)==size and len(data)<=limit and
                 git_blob(data)==candidates[name]["sha"],
                 "V229_UPSTREAM_SIMC_SOURCE_BLOB_CHANGED:"+name)
            (root/name).write_bytes(data)
            raws[name]=data
            git_shas[name]=candidates[name]["sha"]
        receipt=inventory(raws,simc_revision=revision,
            expected_build=expected_build,expected_git_blob=git_shas,
            previous_game_build=previous_game_build,
            season_event=season_event)
        (root/RECEIPT).write_text(
            json.dumps(receipt,sort_keys=True,ensure_ascii=False,indent=2)+"\n",
            encoding="utf8")
        os.rename(root,dest)
    return receipt


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--revision",required=True)
    p.add_argument("--game-build",required=True)
    p.add_argument("--previous-game-build")
    p.add_argument("--event",choices=("mid_patch","season_change","expansion_change",
                                     "cold_start"),
                   default="season_change")
    p.add_argument("--out-dir",type=Path,required=True)
    p.add_argument("--include-item-data",action="store_true")
    args=p.parse_args(argv)
    result=collect(revision=args.revision,expected_build=args.game_build,
        previous_game_build=args.previous_game_build,
        season_event=args.event,dest=args.out_dir,
        include_item_data=args.include_item_data)
    print("V229_SIMC_PINNED_SOURCE_COLLECTED",result["simc_generated_build"],
          result["candidate_class_set_count"],"GJFO_UNVERIFIED_NATIVE0")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
