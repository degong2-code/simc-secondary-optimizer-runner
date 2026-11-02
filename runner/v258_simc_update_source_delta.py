#!/usr/bin/env python3
"""Advisory SimC revision update check against existing SAME-SEASON source.

Four Git tree metadata requests only (plus optional one short SHA resolver);
no DB2 download, generated-file body download, Native, cache or session writes.
An unchanged generated-file blob is NOT proof that other generated tables,
spell effects, APL, scaling, or the active season have stayed identical.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
try:
    from . import v229_simc_only_source_seed as source
except ImportError:
    import v229_simc_only_source_seed as source

SCHEMA="v258_advisory_simc_update_generated_blob_delta_v1"
TRACKED=tuple(source.SOURCE_FILES)+(source.OPTIONAL_ITEM_FILE,)
IMPACT={
    "item_set_bonus.inc":"TIER_SOURCE_METADATA_REVIEW_IF_SELECTED_SET_AFFECTED",
    "gem_data.inc":"GEM_PROPERTY_J_CANDIDATE_REVIEW_IF_SELECTED_GEM_AFFECTED",
    "temporary_enchant.inc":"WEAPON_OIL_TOKEN_O_CANDIDATE_REVIEW_IF_SELECTED_OIL_AFFECTED",
    "item_data.inc":"SELECTED_PHYSICAL_ITEM_IDS_G_REVIEW_IF_AFFECTED",
}

def compare(*, previous_receipt, next_revision_hint, transport=None):
    """Compare exactly the four pinned v229 generated-file blob identities.

    Fail closed for unsealed / unverified previous seed. Do not infer
    *season* from SimC commits, or infer whether changed files change one
    user's selected items. Do not invalidate previously measured static data.
    """
    need=source.need
    need(type(previous_receipt) is dict and
         previous_receipt.get("schema")==source.SCHEMA and
         previous_receipt.get("provenance_tree_blob_authenticated") is True and
         previous_receipt.get("environment_ready") is False and
         previous_receipt.get("native_calls")==0,
         "V258_PRIOR_GIT_PINNED_SOURCE_RECEIPT_REQUIRED")
    clean={k:v for k,v in previous_receipt.items() if k!="receipt_sha256"}
    need(previous_receipt.get("receipt_sha256")==source.digest(
         source.canonical(clean).encode("utf8")),
         "V258_PRIOR_RECEIPT_DIGEST_MISMATCH")
    oldrev=previous_receipt.get("simc_revision")
    records=previous_receipt.get("source_files")
    need(type(oldrev) is str and source.REV.fullmatch(oldrev) is not None
         and type(records) is dict and
         set(records) in (set(source.SOURCE_FILES),set(TRACKED)),
         "V258_PRIOR_REVISION_OR_TRACKED_FILES_INVALID")
    for name,rec in records.items():
        need(type(rec) is dict and
             type(rec.get("git_blob_sha1")) is str and
             source.HEX.fullmatch(rec["git_blob_sha1"]) is not None and
             type(rec.get("bytes")) is int and rec["bytes"]>0,
             "V258_PRIOR_FILE_GIT_BLOB_INVALID")
    calls=[0]
    def fetch(req,timeout):
        calls[0]+=1
        return (source.urlopen if transport is None else transport)(
            req,timeout=timeout)
    nextrev=source.resolve_exact_commit(next_revision_hint,transport=fetch)
    if oldrev==nextrev:
        changes={name:("SAME_PINNED_REVISION" if name in records else
                        "NOT_IN_PRIOR_RECEIPT") for name in TRACKED}
    else:
        remote=source.discover_generated_tree(nextrev,transport=fetch)
        changes={}
        for name in TRACKED:
            old=records.get(name)
            if old is None:
                changes[name]="NOT_IN_PRIOR_RECEIPT"
            elif (old["git_blob_sha1"]==remote[name]["sha"] and
                  old["bytes"]==remote[name]["size"]):
                changes[name]="UNCHANGED_EXACT_GIT_BLOB"
            else:
                changes[name]="CHANGED_GENERATED_FILE_NOT_SELECTED_ITEM_PROOF"
    changed=[name for name in TRACKED if changes[name].startswith("CHANGED_")]
    unknown=[name for name in TRACKED if changes[name]=="NOT_IN_PRIOR_RECEIPT"]
    return {
        "schema":SCHEMA,
        "status":("TRACKED_FILE_CHANGE_REQUIRES_SELECTED_SOURCE_REVIEW"
                  if changed else
                  "TRACKED_ITEM_DATA_NOT_PREVIOUSLY_PINNED"
                  if unknown else
                  "FOUR_TRACKED_FILES_UNCHANGED_NOT_ENTIRE_SIMC_EQUIVALENCE"),
        "previous_revision":oldrev,"next_revision":nextrev,
        "previous_generated_game_build":previous_receipt["simc_generated_build"],
        "new_generated_game_build":"NOT_FETCHED_METADATA_ONLY",
        "tracked_file_status":changes,
        "changed_files":changed,"unobserved_files":unknown,
        "potentially_affected_sources":{name:IMPACT[name] for name in changed},
        "requests_used":calls[0],"body_downloads":0,"native_calls":0,
        "static_environment_mutated":False,
        "dps_cache_reuse_across_distinct_binaries":False,
        "full_simc_equivalence_proven":False,
        "season_membership_verified_by_this_check":False,
        "environment_rebuild_required_by_revision_change_alone":False,
    }

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--previous-v229-receipt",type=Path,required=True)
    p.add_argument("--next-revision",required=True)
    a=p.parse_args(argv)
    # A trusted invocation uses a local v217-verified source receipt. This
    # CLI cannot authenticate user-supplied JSON to upstream bytes on its own.
    need=source.need
    root=a.previous_v229_receipt
    need(root.is_file() and not root.is_symlink() and
         0<root.stat().st_size<=2_000_000,
         "V258_PRIOR_RECEIPT_FILE_UNSAFE")
    data=json.loads(root.read_text("utf8"))
    report=compare(previous_receipt=data,next_revision_hint=a.next_revision)
    print(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
