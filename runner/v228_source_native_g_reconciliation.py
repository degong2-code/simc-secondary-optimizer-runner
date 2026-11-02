#!/usr/bin/env python3
"""v228: independent source/profile/Native-JSON2 equipment reconciliation.

A single requested G work order is checked against byte-pinned v225 sources,
the *provided* SimC profile, actual Native JSON2 gear observations and v046's
existing exact static parser/sum (through v227). These checks are read-only.

A JSON2 gear match does NOT prove that the profile bytes were the executed
input, nor independently prove the binary's compiled game build. Therefore
the numeric G observation is NOT an approved new-season G/B/T budget.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re

try:
    from . import v046_static_item_cache as cache_mod
    from . import v226_representative_native_g_work_order as work_mod
    from . import v227_cached_native_g_observation as observation_mod
    from . import v225_season_source_bundle_intake as bundle_mod
except ImportError:
    import v046_static_item_cache as cache_mod
    import v226_representative_native_g_work_order as work_mod
    import v227_cached_native_g_observation as observation_mod
    import v225_season_source_bundle_intake as bundle_mod

SCHEMA = "v228_representative_G_native_json2_reconciliation_v1"
SHA = re.compile(r"[a-f0-9]{64}\Z")
PROFILE_MAX = 2_000_000
NATIVE_MAX = cache_mod.MAX_NATIVE_BYTES


class NativeGBlocked(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise NativeGBlocked(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw, title):
    need(type(raw) is bytes and 0 < len(raw) <=
         (PROFILE_MAX if title == "PROFILE" else NATIVE_MAX),
         "V228_" + title + "_BYTES_MISSING_OR_OVERSIZED")
    try:
        return raw.decode("utf8")
    except UnicodeError as exc:
        raise NativeGBlocked("V228_" + title + "_UTF8_INVALID") from exc


def parse_profile(raw, work_order):
    text = decode(raw, "PROFILE")
    rows = {}
    attrs = {}
    ignored = {"actions", "actions.precombat"}
    equipment_keys=set(work_mod.representative.contracts.SLOT_ORDER) | set(cache_mod.SLOT_ALIASES)
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        need("=" in line, "V228_PROFILE_LINE_INVALID")
        key,value = line.split("=", 1)
        key=key.strip()
        value=value.strip()
        # A static *bare representative* G request must not hide a second
        # set of fake rating overrides or selected enchant/gem/food/oil.
        need(not (key.startswith("gear_") or
                  key in ("flask", "food", "potion", "augmentation",
                          "temporary_enchant", "ilevel", "gem",
                          "gems", "gem_id", "socket", "sockets",
                          "enchant", "enchants", "enchant_id") or
                  key.startswith("profileset.")),
             "V228_PROFILE_NONBARE_G_RATING_OR_CONSUMABLE_OVERRIDE")
        if key in equipment_keys:
            need(key in work_order["selected_source_slots"] and
                 key not in rows, "V228_PROFILE_EXTRA_OR_DUPLICATE_EQUIPMENT")
            try:
                _, options = cache_mod.parse_encoded(value)
            except cache_mod.CacheBlocked as exc:
                raise NativeGBlocked("V228_PROFILE_ITEM_SYNTAX_INVALID") from exc
            need(set(options) == {"id", "ilevel", "source"} and
                 options["source"] == "local" and
                 int(options["id"]) == work_order["selected_source_slots"][key] and
                 int(options["ilevel"]) == work_order["target_ilevel"],
                 "V228_PROFILE_ITEM_ID_ILVL_OR_MODIFIER_MISMATCH")
            rows[key]=(int(options["id"]),int(options["ilevel"]))
        else:
            need(key not in attrs or key in ignored,
                 "V228_PROFILE_DUPLICATE_SCALAR_ASSIGNMENT")
            attrs[key]=value
    char=work_order["character"]
    all_classes={key.split("/")[0] for key in
                 work_mod.representative.contracts.CONTRACTS}
    need(not ((set(attrs) & all_classes) - {char["class"]}),
         "V228_PROFILE_MULTIPLE_CLASS_ASSIGNMENTS")
    need(char["class"] in attrs and
         attrs.get("spec") == char["spec"] and
         set(rows) == set(work_order["selected_source_slots"]),
         "V228_PROFILE_CLASS_SPEC_OR_FULL_G_EQUIPMENT_MISMATCH")
    return rows


def reconcile(*, bundle_dir, work_order, profile_raw, native_raw):
    """Compare actual Native JSON2 against one exact requested source G set.

    No source/proc reimplementation and no acceptance based on supplied
    proof flags. SHA hashes alone bind bytes, not their causal execution.
    """
    need(type(work_order) is dict and
         work_order.get("schema") == work_mod.SCHEMA and
         work_order.get("receipt_sha256") ==
             work_mod.digest({k:v for k,v in work_order.items()
                              if k != "receipt_sha256"}),
         "V228_WORK_ORDER_INVALID_OR_TAMPERED")
    # Reconstruct the work order from the same source artifact. This detects
    # substituted gear/tier/season bytes instead of trusting the old receipt.
    source_manifest_path=pathlib.Path(bundle_dir)/"source_manifest.json"
    try:
        manifest=bundle_mod._manifest(source_manifest_path)
    except (ValueError,KeyError,OSError) as exc:
        raise NativeGBlocked("V228_SOURCE_MANIFEST_INVALID") from exc
    expected=work_mod.make_work_order(
        bundle_dir=bundle_dir, event=manifest["event"],
        previous_game_build=manifest["previous_game_build"],
        target_ilevel=work_order["target_ilevel"],
        character_class=work_order["character"]["class"],
        specialization=work_order["character"]["spec"])
    need(expected == work_order,
         "V228_REGENERATED_SOURCE_WORK_ORDER_DRIFT")
    parsed_profile=parse_profile(profile_raw,work_order)
    text=decode(native_raw,"NATIVE_JSON2")
    try:
        payload=json.loads(text)
    except ValueError as exc:
        raise NativeGBlocked("V228_NATIVE_JSON2_JSON_INVALID") from exc
    git_revision=payload.get("git_revision") if type(payload) is dict else None
    need(type(git_revision) is str and
         re.fullmatch(r"[a-f0-9]{7,40}",git_revision) is not None and
         manifest["simc_revision"].startswith(git_revision),
         "V228_NATIVE_SIMC_REVISION_NOT_PINNED_SOURCE")
    try:
        records=cache_mod.native_records(
            native_raw,season=work_order["season"],
            artifact_id="SOURCE_BOUND_UNPROMOTED_NATIVE_JSON2")
    except (cache_mod.CacheBlocked,ValueError,TypeError,KeyError) as exc:
        raise NativeGBlocked(
            "V228_V046_NATIVE_JSON2_PARSER_BLOCKED:" + str(exc)) from exc
    actual_slots={}
    for record in records:
        slot=record["observed_slot"]
        need(slot in parsed_profile and slot not in actual_slots,
             "V228_NATIVE_UNEXPECTED_OR_DUPLICATE_GEAR_SLOT")
        identity=record["identity"]
        need(identity["item_id"] == parsed_profile[slot][0] and
             identity["ilevel"] == parsed_profile[slot][1] and
             identity["options"] == {} and
             identity["slot"] == cache_mod.normalize_slot(slot) and
             record["modifiers_present"] is False,
             "V228_NATIVE_ITEM_VARIANT_OR_MODIFIER_DRIFT")
        actual_slots[slot]=record["static_digest"]
    need(set(actual_slots) == set(parsed_profile),
         "V228_NATIVE_FULL_REPRESENTATIVE_EQUIPMENT_MISMATCH")
    observed_cache=cache_mod.empty_cache(work_order["season"])
    cache_mod.merge_native(observed_cache,records)
    observed=observation_mod.observe(work_order=work_order,
                                     cache=observed_cache)
    need(observed["status"] ==
         "EXACT_NATIVE_STATIC_CACHE_G_OBSERVED_PENDING_BUILD_PROOF" and
         observed["missing_variant_requests"] == [] and
         type(observed["observed_G_total_if_complete"]) is int and
         observed["observed_G_total_if_complete"] > 0,
         "V228_NATIVE_EXACT_STATIC_G_NOT_COMPLETE")
    result={
        "schema": SCHEMA,
        "status": "EXACT_PROFILE_NATIVE_EQUIPMENT_MATCHED_BUILD_AND_EXECUTION_UNATTESTED",
        "work_identity_sha256": work_order["work_identity_sha256"],
        "work_receipt_sha256": work_order["receipt_sha256"],
        "source_bundle_receipt_sha256": work_order[
            "source_bundle_receipt_sha256"],
        "game_build_declared_by_source": work_order["game_build"],
        "season": work_order["season"],
        "target_ilevel": work_order["target_ilevel"],
        "simc_git_revision_from_json2": git_revision,
        "simc_source_revision_prefix_matches": True,
        "profile_sha256": sha(profile_raw),
        "native_json2_sha256": sha(native_raw),
        "matching_equipment_slot_count": len(actual_slots),
        "observed_G_vector": observed[
            "observed_G_vector_if_complete"],
        "observed_G_total": observed[
            "observed_G_total_if_complete"],
        "provenance_limitations": [
            "PROFILE_EXECUTION_INPUT_HASH_NOT_EMBEDDED_IN_NATIVE_JSON2",
            "NATIVE_BINARY_COMPILED_GAME_BUILD_NOT_INDEPENDENTLY_ATTESTED",
            "SOURCE_BUNDLE_ORIGIN_DECLARATIONS_NOT_REMOTE_AUTHENTICATION",
            "SIMC_GAME_MECHANICS_AND_EFFECTS_NOT_REIMPLEMENTED",
        ],
        "G": None, "J": None, "F": None, "O": None,
        "B": None, "T": None,
        "authenticated_new_season_G": False,
        "environment_ready": False,
        "native_calls_by_validator": 0,
        "cache_mutations": 0,
    }
    return {**result,"receipt_sha256":work_mod.digest(result)}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bundle-dir",type=pathlib.Path,required=True)
    p.add_argument("--work-order",type=pathlib.Path,required=True)
    p.add_argument("--profile",type=pathlib.Path,required=True)
    p.add_argument("--native-json2",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    args=p.parse_args(argv)
    work=json.loads(args.work_order.read_text("utf8"))
    result=reconcile(bundle_dir=args.bundle_dir,work_order=work,
                     profile_raw=args.profile.read_bytes(),
                     native_raw=args.native_json2.read_bytes())
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(
        result,sort_keys=True,ensure_ascii=False,indent=2)+"\n",
        encoding="utf8")
    print("V228_NATIVE_JSON2_EQUIPMENT_MATCH",result[
        "matching_equipment_slot_count"],"G_NOT_PROMOTED_NATIVE0",flush=True)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
