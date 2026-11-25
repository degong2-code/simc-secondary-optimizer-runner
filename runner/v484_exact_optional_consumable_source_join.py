#!/usr/bin/env python3
"""Read-only exact food/potion item join using ALREADY SEALED source owners.

v190/v216 has authenticated the same-build DB2 physical candidate stage.
v229/v230 already authenticates and parses the pinned SimC item_data.inc.
This on-demand join is independent of the sealed v281 flask/oil stage and
NEVER certifies a SimC runtime option, the highest-quality effect, user
eligibility, CHMV budget, or Policy A publication.

Only an internal caller may provide the previously sealed v217 stage summary
and pinned SimC seed directory. No HTTP, Native, cache writes or new stage.
"""
from __future__ import annotations

import json
import pathlib
import re

import v190_consumable_item_snapshot_join as physical
import v217_stage_execution_engine as stage_engine
import v230_simc_item_metadata as item_metadata

STAGE_ID="fresh-v189-v190-consumable-physical-other"
STAGE_VERSION="same-build-real-other-consumable-v3"
PREFIX="source/v282_same_season_consumable_"
OUTPUTS={
    "simc_source":PREFIX+"unique_gear_midnight.cpp",
    "v189":PREFIX+"v189_handlers.json",
    "candidate":PREFIX+"v190_items.json"}
SUBCLASS={"food":5,"potion":1}
TOKEN=re.compile(r"[a-z0-9]+(?:_[a-z0-9]+)*\Z")
HEX40=re.compile(r"[a-f0-9]{40}\Z")
HEX64=re.compile(r"[a-f0-9]{64}\Z")


class OptionalConsumableSourceBlocked(ValueError):
    pass


def need(condition, code):
    if not condition:
        raise OptionalConsumableSourceBlocked(code)


def reviewed_apl_default_groups(game_build,simc_revision):
    """Exact reviewed level-90 APL input defaults (not numerical quality proof).

    Same pinned revision: engine/class_modules/apl and class overrides.
    Unknown build/revision has no source evidence; never guess next season.
    The same owner serves source joining and public default preferences.
    """
    if (game_build!="12.1.5.70961" or
        simc_revision!="9933ffb946fb55b1fa66657b848f519ac19006e1"):
        return {}
    groups={
        "food":{
            "harandar_celebration":(
                "druid/balance druid/feral monk/windwalker "
                "rogue/assassination rogue/outlaw rogue/subtlety "
                "shaman/elemental shaman/enhancement warlock/affliction "
                "warlock/demonology warlock/destruction warrior/arms warrior/fury"),
            "silvermoon_parade":(
                "deathknight/frost deathknight/unholy evoker/devastation "
                "hunter/beast_mastery hunter/marksmanship hunter/survival "
                "mage/arcane mage/fire mage/frost priest/shadow"),
            "blooming_feast":"demonhunter/havoc demonhunter/devourer",
            "royal_roast":"paladin/retribution"},
        "potion":{
            "lights_potential_2":(
                "druid/balance evoker/devastation mage/arcane mage/fire "
                "paladin/retribution priest/shadow rogue/assassination "
                "rogue/outlaw rogue/subtlety shaman/elemental "
                "shaman/enhancement warrior/arms warrior/fury"),
            "potion_of_recklessness_2":(
                "deathknight/frost deathknight/unholy demonhunter/havoc "
                "demonhunter/devourer hunter/beast_mastery hunter/marksmanship "
                "hunter/survival mage/frost monk/windwalker warlock/destruction"),
            "liquid_luster_2":"druid/feral warlock/affliction warlock/demonology"}}
    return groups


def candidate_token(name, rank):
    """Conservative SimC parser spelling, NOT proof that a token selects an item.

    Pinned SimC 12.1.5.70961 engine/util/util.cpp::tokenize removes ASCII
    punctuation (including hyphens and apostrophes) instead of replacing it
    with underscores; spaces become underscores. consumable.cpp reads only a
    single-digit crafting-quality suffix. Names with supported SimC punctuation
    that cannot fit the existing installed-token grammar stay unadmitted.
    """
    if (type(name) is not str or not name.isascii() or
            type(rank) is not int or not 0<=rank<=9):
        return None
    stem=parser_name_stem(name)
    if (stem is None or TOKEN.fullmatch(stem) is None or
            (rank==0 and re.search(r"_[0-9]$",stem))):
        return None
    return stem+("_"+str(rank) if rank else "")


def parser_name_stem(name):
    """Pinned util::tokenize name projection, including non-input names.

    SimC removes bytes >= 0x80. Such a DBC name may still shadow a valid
    ASCII needle, even though it is not itself an eligible product token.
    """
    if type(name) is not str:
        return None
    chars=[]
    for char in name.lstrip("_+"):
        if not char.isascii():
            continue
        if char.isalpha():
            chars.append(char.lower())
        elif char==" ":
            chars.append("_")
        elif char.isdecimal() or char in "_+.%":
            chars.append(char)
        # SimC removes other ASCII punctuation rather than inserting '_'.
    return "".join(chars)


def ordered_consumable_parser_index(parser_rows):
    """Same generated order as SimC's filtered_dbc_index_t."""
    need(type(parser_rows) is list and
         len(parser_rows)<=20000,
         "V764_OPTIONAL_PARSER_NAME_SOURCE_PENDING")
    parser_names={}
    for row in parser_rows:
        need(type(row) is dict and
             type(row.get("item_id")) is int and row["item_id"]>0 and
             row.get("subclass_id") in (1,5,8) and
             type(row.get("crafting_quality")) is int and
             row["crafting_quality"]>=0 and
             type(row.get("name")) is str,
             "V764_OPTIONAL_PARSER_NAME_ROW_INVALID")
        stem=parser_name_stem(row["name"])
        if stem is not None:
            # filtered_dbc_index_t::init appends in source order;
            # ::get returns range::find_if, not all possible matches.
            key="food" if row["subclass_id"]==5 else "potion"
            parser_names.setdefault(key,[]).append(
                (row["item_id"],stem,row["crafting_quality"]))
    return parser_names


def first_consumable_match(parser_names,kind,stem,rank):
    """Return the actual first matching physical ID, not a uniqueness guess."""
    return next((i for i,name,q in parser_names.get(kind,[])
                 if stem in name and (q==rank or (rank==0 and q==1))),
                None)


def match_selected_physical_items(*, stage_root, v190_stage,
                                  simc_seed_dir, game_build,
                                  simc_revision, selected_item_ids):
    """Join only selected IDs to a pinned generated SimC DBC, source-only.

    Reusing a v217 receipt includes SHA verification of its original three
    outputs. The v230 owner rechecks its own v229 receipt, generated file SHA
    and Git blob before a single streaming exact-ID parse. This function is
    NOT the remaining three Policy A proof families or the UI choice owner.
    """
    need(type(game_build) is str and
         re.fullmatch(r"\d+(?:\.\d+){3}",game_build) is not None and
         type(simc_revision) is str and
         HEX40.fullmatch(simc_revision) is not None,
         "V484_EXACT_BUILD_SIMC_IDENTITY_REQUIRED")
    need(type(selected_item_ids) in (list,tuple) and
         1<=len(selected_item_ids)<=16 and
         all(type(i) is int and i>0 for i in selected_item_ids) and
         len(set(selected_item_ids))==len(selected_item_ids),
         "V484_SELECTED_EXACT_ITEM_IDS_REQUIRED")
    need(type(v190_stage) is dict and
         v190_stage.get("status") in (
             "EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED") and
         v190_stage.get("stage_id")==STAGE_ID and
         v190_stage.get("stage_version")==STAGE_VERSION and
         type(v190_stage.get("receipt_sha256")) is str and
         HEX64.fullmatch(v190_stage["receipt_sha256"]) is not None,
         "V484_ORIGINAL_V190_STAGE_REQUIRED")
    origin=pathlib.Path(stage_root)
    seed=pathlib.Path(simc_seed_dir)
    need(origin.is_dir() and not origin.is_symlink() and
         seed.is_dir() and not seed.is_symlink(),
         "V484_ORIGINAL_SOURCE_DIRECTORY_REQUIRED")
    try:
        paths,receipt_path=stage_engine._safe_paths(
            origin,STAGE_ID,OUTPUTS)
        receipt=stage_engine._read_receipt(receipt_path)
        need(receipt.get("status")=="COMPLETE" and
             receipt.get("stage_id")==STAGE_ID and
             receipt.get("stage_version")==STAGE_VERSION and
             receipt.get("receipt_sha256")==
                 v190_stage["receipt_sha256"] and
             receipt.get("input_fingerprint")==
                 v190_stage.get("input_fingerprint") and
             receipt.get("output_paths")==OUTPUTS and
             v190_stage.get("output_paths")==OUTPUTS,
             "V484_ORIGINAL_STAGE_RECEIPT_DRIFT")
        # Original v217 output hashes, not just a JSON file supplied by user.
        stage_engine._verify_outputs(receipt,paths)
        candidate=paths["candidate"][1]
        need(0<candidate.stat().st_size<=5_000_000,
             "V484_ORIGINAL_V190_CANDIDATE_SIZE_INVALID")
        source=json.loads(candidate.read_text(encoding="utf8"))
    except (stage_engine.StageExecutionBlocked,OSError,ValueError,
            UnicodeError,TypeError,KeyError) as exc:
        if isinstance(exc,OptionalConsumableSourceBlocked):
            raise
        raise OptionalConsumableSourceBlocked(
            "V484_V217_ORIGINAL_SOURCE_NOT_VERIFIED") from exc
    need(type(source) is dict and
         source.get("schema")==physical.SCHEMA and
         source.get("status")==
             "DB2_CONSUMABLE_CANDIDATES_PENDING_SIMC_DBC_JOIN" and
         source.get("automatic_ui_promotion") is False and
         source.get("source",{}).get("wago_snapshot_build")==game_build and
         source["source"].get("simc_revision")==simc_revision and
         type(source.get("items")) is list,
         "V484_V190_SOURCE_BUILD_OR_CANDIDATE_DRIFT")
    selected=set(selected_item_ids)
    db2={}
    for row in source["items"]:
        if type(row) is not dict or row.get("item_id") not in selected:
            continue
        item_id=row["item_id"]
        need(item_id not in db2 and row.get("kind") in SUBCLASS and
             row.get("item_class")==0 and
             row.get("item_subclass")==SUBCLASS[row["kind"]] and
             # Food/potion is consumed, never equipped. Two sources
             # agreeing on the same nonzero inventory slot is still invalid.
             type(row.get("inventory_type")) is int and
             row["inventory_type"]==0 and
             row.get("source")=="SAME_BUILD_DB2_ITEM_AND_ITEMSPARSE" and
             row.get("ui_selectable") is False and
             row.get("simc_token")=="UNRESOLVED",
             "V484_SELECTED_PHYSICAL_ITEM_SCOPE_MISMATCH")
        db2[item_id]=row
    # Fail before opening/rehashing the large item_data.inc when the
    # requested physical ID is not a source-authenticated food/potion.
    need(set(db2)==selected,
         "V484_SELECTED_FOOD_POTION_ITEM_ID_NOT_IN_SOURCE")
    try:
        generated=item_metadata.from_seed(
            directory=seed,item_ids=sorted(selected))
    except (item_metadata.ItemMetadataBlocked,OSError,ValueError,
            UnicodeError,TypeError,KeyError) as exc:
        raise OptionalConsumableSourceBlocked(
            "V484_PINNED_SIMC_EXACT_ITEM_SOURCE_PENDING") from exc
    need(generated.get("game_build")==game_build and
         generated.get("simc_revision")==simc_revision and
         generated.get("selection_mode")=="EXACT_REQUESTED_IDS" and
         HEX64.fullmatch(generated.get("source_sha256","")) is not None and
         HEX64.fullmatch(generated.get("source_receipt_sha256","")) is not None,
         "V484_SIMC_ITEM_DATA_BUILD_OR_REVISION_DRIFT")
    simc={row["item_id"]:row for row in generated["items"]}
    need(set(simc)==selected,
         "V484_SIMC_ITEM_ID_COVERAGE_DRIFT")
    joined=[]
    for item_id in sorted(selected):
        origin_row=db2[item_id]
        row=simc[item_id]
        need(row.get("source")=="SIMC_GENERATED_ITEM_DATA_EXACT_ROW" and
             row.get("class_id")==0 and
             row.get("subclass_id")==SUBCLASS[origin_row["kind"]] and
             row.get("inventory_type")==origin_row["inventory_type"]==0 and
             type(row.get("crafting_quality")) is int and
             row["crafting_quality"]>=0,
             "V484_SAME_ID_ITEM_CLASS_OR_QUALITY_DRIFT")
        joined.append({
            "kind":origin_row["kind"],
            "physical_item_id":item_id,
            "game_build":game_build,
            "simc_revision":simc_revision,
            "crafting_quality_candidate":row["crafting_quality"],
            "simc_input_token_candidate":candidate_token(
                row["name"],row["crafting_quality"]),
            "v190_v217_receipt_sha256":receipt["receipt_sha256"],
            "simc_item_data_sha256":generated["source_sha256"],
            "simc_v229_seed_receipt_sha256":
                generated["source_receipt_sha256"],
            "exact_item_id_and_class_source_join":True,
            "source_only":True,
            "simc_token_native_verified":False,
            "same_effect_quality_group_verified":False,
            "use_conditions_verified":False,
            "chmv_budget_owner_verified":False,
            "policy_A_eligible":False,
            "ui_selectable":False,
        })
    return {
        "schema":"v484_selected_optional_consumable_source_join_v1",
        "status":"EXACT_PHYSICAL_SIMC_DBC_ITEM_CANDIDATES_UNADMITTED",
        "game_build":game_build,
        "simc_revision":simc_revision,
        "items":joined,
        "candidate_count":len(joined),
        "requires_existing_policy_A_proofs":True,
        "user_selectable":False,
        "environment_ready":False,
        "native_calls":0,
        "network_calls":0,
        "source_files_written":0,
    }
