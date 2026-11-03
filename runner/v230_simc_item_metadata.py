#!/usr/bin/env python3
"""v230: parse pinned SimC item_data.inc for EXACT requested physical item IDs.

Uses the generated C++ layout from the same SimC source revision's
dbc_extract3/dbc/generator.py and engine/dbc/item_data.hpp. Not a game
mechanics reimplementation or general loot database. Never infer an item's
active-season membership, scaling rating or SimC Native acceptance.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import pathlib
import re

try:
    from . import v229_simc_only_source_seed as seed
except ImportError:
    import v229_simc_only_source_seed as seed

SCHEMA="v230_simc_generated_exact_item_metadata_v1"
BUILD_HEADER=re.compile(r"^// Items, ilevel (\d+)-(\d+), wow build (\d+(?:\.\d+){3})$")
STATS_HEAD=re.compile(r"^static const dbc_item_data_t::stats_t\s+(__[a-zA-Z0-9_]+)\[(\d+)\]\s*=\s*\{")
CHUNK_HEAD=re.compile(r"^static const std::array<dbc_item_data_t,\s*(\d+)>\s+__[a-zA-Z0-9_]+_data_chunk(\d+)\s*\{\s*\{")
STAT_ROW=re.compile(r"^\s*\{\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*([-+.0-9eE]+[fF]?)\s*\},?\s*(?://.*)?$")
POINTER=re.compile(r"^&(__[a-zA-Z0-9_]+)\[(\d+)\]$")
NON_NEG_INT=re.compile(r"(?:0[xX][0-9a-fA-F]+|[0-9]+)\Z")
MAX_REQUEST_IDS=750


class ItemMetadataBlocked(ValueError):
    pass


def need(ok,code):
    if not ok:
        raise ItemMetadataBlocked(code)


def number(raw,code):
    need(type(raw) is str and NON_NEG_INT.fullmatch(raw) is not None,code)
    return int(raw,16 if raw.lower().startswith("0x") else 10)


def split_cpp_record(line):
    """Single generated C++ item row; preserve socket braces/quoted commas."""
    row=line.strip()
    need(row.startswith("{") and (row.endswith("},") or row.endswith("}")),
         "V230_ITEM_RECORD_SYNTAX")
    if row.endswith(","):row=row[:-1]
    row=row[1:-1].strip()
    fields=[];part=[];quoted=False;escape=False;depth=0
    for c in row:
        if escape:
            part.append(c);escape=False;continue
        if c=="\\" and quoted:
            part.append(c);escape=True;continue
        if c=='"':
            quoted=not quoted;part.append(c);continue
        if not quoted and c=="{":depth+=1
        if not quoted and c=="}":
            depth-=1
            need(depth>=0,"V230_ITEM_RECORD_NESTED_BRACES")
        if not quoted and depth==0 and c==",":
            fields.append("".join(part).strip());part=[]
        else:part.append(c)
    fields.append("".join(part).strip())
    need(not quoted and depth==0 and len(fields)==28,
         "V230_ITEM_RECORD_FIELD_COUNT_OR_QUOTE")
    return fields


def parse_exact(raw, *, build, item_ids=None, candidate_filter=None,
                candidate_limit=4000, max_bytes=seed.MAX_ITEM_FILE):
    """One streaming pass for either exact IDs or bounded candidate selection.

    Candidate mode reuses all existing C++ layout, generated-stat pointer and
    chunk-count checks. A candidate is not an approved in-season item.
    """
    need(type(raw) is bytes and 0<len(raw)<=max_bytes and
         type(build) is str and seed.BUILD.fullmatch(build),
         "V230_ITEM_DATA_BYTES_OR_BUILD_INVALID")
    candidate_mode=item_ids is None
    need((candidate_mode and callable(candidate_filter) and
          type(candidate_limit) is int and 1<=candidate_limit<=5000) or
         (not candidate_mode and candidate_filter is None and
          type(item_ids) in (list,tuple,set) and
          0<len(item_ids)<=MAX_REQUEST_IDS and
          all(type(x) is int and 0<x<10**10 for x in item_ids) and
          len(set(item_ids))==len(item_ids)),
         "V230_EXACT_ITEM_REQUEST_IDS_INVALID")
    wanted=None if candidate_mode else set(item_ids)
    try:
        lines=io.StringIO(raw.decode("utf8"))  # no massive list of C++ lines
    except UnicodeError as exc:
        raise ItemMetadataBlocked("V230_ITEM_DATA_NON_UTF8") from exc
    stats=[];stat_name=None;stat_total=None;inside_stats=False
    chunks=0;item_count=0;declared_items=0;current_items=0
    inside_chunk=False;built=False;min_ilevel=None;max_ilevel=None
    found={}
    for raw_line in lines:
        line=raw_line.rstrip("\r\n")
        if (m:=BUILD_HEADER.fullmatch(line)):
            need(not built and m.group(3)==build,
                 "V230_ITEM_DATA_GENERATED_BUILD_MISMATCH")
            min_ilevel,max_ilevel=int(m.group(1)),int(m.group(2))
            need(0<min_ilevel<=max_ilevel<=2000,
                 "V230_ITEM_DATA_LEVEL_RANGE_INVALID")
            built=True
            continue
        if (m:=STATS_HEAD.fullmatch(line)):
            need(not inside_stats and stat_name is None,
                 "V230_ITEM_STATS_ARRAY_DUPLICATE")
            stat_name,stat_total=m.group(1),int(m.group(2))
            need(stat_total>0 and stat_total<=500_000,
                 "V230_ITEM_STATS_COUNT_UNSAFE")
            inside_stats=True
            continue
        if inside_stats:
            if line.strip()=="};":
                need(len(stats)==stat_total,"V230_ITEM_STATS_COUNT_MISMATCH")
                inside_stats=False
                continue
            if not line.strip() or line.lstrip().startswith("//"):
                continue
            m=STAT_ROW.fullmatch(line)
            need(m is not None,
                 "V230_ITEM_STATS_ROW_UNRECOGNIZED:"+repr(line[:100]))
            # Stat alloc/third factor do NOT establish the scaled rating.
            try:
                float(m.group(3).rstrip("fF"))
            except ValueError as exc:
                raise ItemMetadataBlocked("V230_BAD_ITEM_STAT_SOCKET_MULTIPLIER") from exc
            stats.append(int(m.group(1)))
            continue
        if (m:=CHUNK_HEAD.fullmatch(line)):
            need(built and not inside_chunk and int(m.group(2))==chunks,
                 "V230_ITEM_CHUNK_START_INVALID")
            current_items=0
            chunks+=1
            inside_chunk=True
            current_declared=int(m.group(1))
            need(0<current_declared<=16384,
                 "V230_ITEM_CHUNK_SIZE_INVALID")
            declared_items+=current_declared
            continue
        if inside_chunk:
            if line.strip()=="} };":
                need(current_items==current_declared,
                     "V230_ITEM_CHUNK_DECLARED_COUNT_DRIFT")
                inside_chunk=False
                continue
            # Only rows belonging to the generated item chunks are parsed;
            # reject malformed/unrecognized rows before filtering wanted IDs.
            fields=split_cpp_record(line)
            current_items+=1
            item_count+=1
            iid=number(fields[1],"V230_ITEM_ID_UNRECOGNIZED")
            if candidate_mode:
                try:
                    include=candidate_filter(fields)
                except (ValueError,TypeError,KeyError,IndexError) as exc:
                    raise ItemMetadataBlocked(
                        "V230_CANDIDATE_FILTER_REJECTED") from exc
                need(type(include) is bool,
                     "V230_CANDIDATE_FILTER_MUST_RETURN_BOOL")
                if not include:continue
                need(len(found)<candidate_limit,
                     "V230_SOURCE_CANDIDATE_LIMIT_REACHED")
            elif iid not in wanted:
                continue
            need(iid not in found,"V230_DUPLICATE_ITEM_ID")
            name=fields[0]
            need(name.startswith('"') and name.endswith('"') and len(name)<=300,
                 "V230_ITEM_NAME_INVALID")
            stats_ptr=fields[17]
            count=number(fields[18],"V230_ITEM_STAT_COUNT_INVALID")
            need(count<=10,"V230_ITEM_STAT_COUNT_EXCEEDS_ENGINE_MAX")
            codes=[]
            if count:
                p=POINTER.fullmatch(stats_ptr)
                need(p is not None and p.group(1)==stat_name,
                     "V230_ITEM_STAT_POINTER_INVALID")
                start=int(p.group(2))
                need(start+count<=len(stats),
                     "V230_ITEM_STAT_POINTER_OUTSIDE_GENERATED_TABLE")
                codes=stats[start:start+count]
            else:
                need(stats_ptr=="0", "V230_ZERO_STATS_POINTER_NOT_ZERO")
            found[iid]={
                "item_id":iid,"name":name[1:-1],
                "ilevel_unscaled":number(fields[5],"V230_ITEM_ILEVEL_INVALID"),
                "quality":number(fields[9],"V230_ITEM_QUALITY_INVALID"),
                "crafting_quality":number(fields[27],
                    "V230_ITEM_CRAFTING_QUALITY_INVALID"),
                "inventory_type":number(fields[10],"V230_ITEM_INVENTORY_INVALID"),
                "class_id":number(fields[11],"V230_ITEM_CLASS_INVALID"),
                "subclass_id":number(fields[12],"V230_ITEM_SUBCLASS_INVALID"),
                "allowed_class_mask":number(fields[19],"V230_ITEM_MASK_INVALID"),
                "stat_modifier_codes":codes,
                "item_set_id":number(fields[24],"V230_ITEM_SET_ID_INVALID"),
                "source":"SIMC_GENERATED_ITEM_DATA_EXACT_ROW",
            }
    need(built and chunks>0 and not inside_stats and not inside_chunk and
         declared_items==item_count and
         stat_total==len(stats) and
         (bool(found) if candidate_mode else set(found)==wanted),
         "V230_GENERATED_ITEM_DATA_INCOMPLETE_OR_REQUEST_MISSING")
    return {
        "schema":SCHEMA,"status":"SOURCE_ITEM_METADATA_ONLY_NO_G_PROOF",
        "game_build":build,
        "source_sha256":hashlib.sha256(raw).hexdigest(),
        "source_bytes":len(raw),
        "full_generated_item_rows_scanned":item_count,
        "requested_item_count":len(found) if candidate_mode else len(wanted),
        "selection_mode":"SOURCE_CANDIDATE_UNAPPROVED" if candidate_mode
                         else "EXACT_REQUESTED_IDS",
        "items":sorted(found.values(),key=lambda row:row["item_id"]),
        "native_calls":0,"G":None,"environment_ready":False,
    }


def from_seed(*, directory, item_ids):
    root=pathlib.Path(directory)
    receipt=json.loads(seed.bounded_read(root/seed.RECEIPT,2_000_000))
    need(receipt.get("schema")==seed.SCHEMA and
         receipt.get("provenance_tree_blob_authenticated") is True and
         receipt.get("environment_ready") is False and
         receipt.get("G") is None,
         "V230_PINNED_SIMC_SEED_RECEIPT_REQUIRED")
    original={k:v for k,v in receipt.items() if k!="receipt_sha256"}
    need(receipt.get("receipt_sha256")==seed.digest(
        seed.canonical(original).encode("utf8")),
         "V230_SEED_RECEIPT_HASH_MISMATCH")
    meta=receipt.get("source_files",{}).get("item_data.inc")
    need(type(meta) is dict,"V230_ITEM_DATA_NOT_FETCHED_OPT_IN_REQUIRED")
    raw=seed.bounded_read(root/"item_data.inc",seed.MAX_ITEM_FILE)
    need(hashlib.sha256(raw).hexdigest()==meta.get("sha256") and
         seed.git_blob(raw)==meta.get("git_blob_sha1"),
         "V230_ITEM_DATA_BYTES_NOT_IN_PINNED_SEED")
    value=parse_exact(raw,build=receipt["simc_generated_build"],
                      item_ids=item_ids)
    value.update({"source_receipt_sha256":receipt["receipt_sha256"],
                  "simc_revision":receipt["simc_revision"]})
    return value


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed-dir",type=pathlib.Path,required=True)
    p.add_argument("--ids",required=True,
                   help="Comma-separated *source-observed* exact item IDs, at most 750")
    p.add_argument("--out",type=pathlib.Path,required=True)
    args=p.parse_args(argv)
    try:
        ids=[int(v) for v in args.ids.split(",")]
        result=from_seed(directory=args.seed_dir,item_ids=ids)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        if isinstance(exc,ItemMetadataBlocked): raise
        raise ItemMetadataBlocked("V230_INPUT_OR_SOURCE_INVALID") from exc
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2,
                                    ensure_ascii=False)+"\n",encoding="utf8")
    print("V230_EXACT_SIMC_ITEMS",result["requested_item_count"],
          "G_NOT_MEASURED_NATIVE0")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
