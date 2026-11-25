#!/usr/bin/env python3
"""Read-only exact food/potion item join using ALREADY SEALED source owners.

v190/v216 has authenticated the same-build DB2 physical candidate stage.
v229/v230 already authenticates and parses the pinned SimC item_data.inc.
This on-demand join is independent of the sealed v281 flask/oil stage and
NEVER certifies a SimC runtime option, the highest-quality effect, user
eligibility, CHMV budget, or Policy A publication.

Only an internal caller may provide the previously sealed v217 stage summary
and pinned SimC seed directory. The item join has no HTTP, Native, cache writes or new stage. The separate
profile-default observer is an explicit one-process caller-owned operation.
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



def extract_simc_profile_defaults(*, binary, season, receipt, allow_partial=False):
    """Observe SimC's own defaults with caller-supplied representative weapons.

    Caller owns exact binary identity, season/weapon provenance and caching.
    Profiles are ephemeral inputs, never executable user profiles.
    No DPS or item-effect admission. Preserve SimC diagnostics on failure.
    """
    import subprocess
    import tempfile
    import v106_user_session_controller as sessions
    import v139_pure_target_profile_composer as representative

    binary=pathlib.Path(binary).resolve()
    need(binary.is_file(),"V784_BINARY_MISSING")
    full_roster={"/".join(k) for k in sessions.SUPPORTED}
    level=season.get("character_level")
    need((level is None or type(level) is int and 1<=level<=100) and
         type(season.get("target_ilevel")) is int and
         1<=season["target_ilevel"]<=1000 and
         type(season.get("specializations")) is dict and
         bool(season["specializations"]) and
         (set(season["specializations"])<=full_roster if allow_partial
          else set(season["specializations"])==full_roster),
         "V785_REPRESENTATIVE_CATALOG_SCOPE_INVALID")
    roster=sorted(tuple(key.split("/")) for key in season["specializations"])
    doc=receipt
    doc.update(character_level=level,
               weapon_target_ilevel=season["target_ilevel"],
               profile_generation_processes=0,dps_simulations=0)
    with tempfile.TemporaryDirectory(prefix="v784-") as td:
        root=pathlib.Path(td)
        lines=["save_profiles=1","save_profile_with_actions=0",
               "offline=1","threads=1"]
        files={}
        for n,(cls,spec) in enumerate(roster):
            controls=sessions.standard_controls((cls,spec))
            actor="defaults_"+str(n)
            file=actor+".simc"
            key=cls+"/"+spec
            contract=representative.contracts.lookup(cls,spec)
            info=season["specializations"][key]
            hands=representative.contracts.WEAPON_FORMS[contract["weapon_form"]]
            need(set(info["weapons"])==set(hands),
                 "V785_REPRESENTATIVE_WEAPON_FORM_DRIFT")
            files[key]=(file,spec)
            lines.extend([cls+"="+actor,"spec="+spec]+
                          (["level="+str(level)] if level is not None else [])+
                          ["race="+controls["race"],"load_default_talents=1",
                          "role="+contract["role"],"position="+contract["position"],
                          "flask=disabled","augmentation=disabled",
                          "temporary_enchant=disabled","save="+file])
            lines.extend(representative.items.equipment_line(
                hand,info["weapons"][hand],season["target_ilevel"],
                info.get("item_options",{}).get(hand,{})) for hand in hands)
        input_path=root/"defaults_input.simc"
        input_path.write_text("\n".join(lines)+"\n",encoding="utf8")
        doc["profile_generation_processes"]=1
        process=subprocess.run([str(binary),input_path.name],cwd=root,
            capture_output=True,text=True,errors="replace",timeout=120)
        output=process.stdout+"\n"+process.stderr
        doc["returncode"]=process.returncode
        doc["generation_branch_observed"]="Generating profiles" in output
        doc["simulation_branch_observed"]="Simulating..." in output
        if doc["simulation_branch_observed"]:
            doc["dps_simulations"]=None
            raise RuntimeError("V784_UNEXPECTED_SIMULATION_BRANCH")
        doc["generated_profile_count"]=sum((root/f).is_file()
                                            for f,_ in files.values())
        doc["diagnostic_tail"]=output[-1800:]
        observed={}
        missing=[]
        observed_levels=set()
        for key,(file,spec) in files.items():
            path=root/file
            if not path.is_file() or path.stat().st_size>500_000:
                missing.append(key)
                continue
            values={}
            for line in path.read_text(encoding="utf8").splitlines():
                if "=" not in line or line.startswith("#"):
                    continue
                name,value=line.split("=",1)
                if name in ("spec","level","food","potion"):
                    if name in values:
                        raise RuntimeError("V784_DUPLICATE_PROFILE_FIELD")
                    values[name]=value.strip()
            actual_level=values.get("level","")
            if (values.get("spec")!=spec or
                    not re.fullmatch(r"[1-9][0-9]{0,2}",actual_level) or
                    not 1<=int(actual_level)<=100 or
                    (level is not None and actual_level!=str(level)) or
                    not all(re.fullmatch(r"[a-z0-9_]{1,100}",values.get(k,""))
                            for k in ("food","potion"))):
                missing.append(key)
                continue
            observed_levels.add(int(actual_level))
            observed[key]={k:values[k] for k in ("food","potion")}
        need(len(observed_levels)==1,"V788_SIMC_CHARACTER_LEVEL_DRIFT")
        doc["character_level"]=next(iter(observed_levels))
        doc["observed_defaults"]=observed
        doc["missing_specs"]=missing
        need(process.returncode==0 and doc["generation_branch_observed"]
             and not missing and len(observed)==len(roster),
             "V784_PROFILE_GENERATION_INCOMPLETE")
        return observed


def current_source_profile_default_weapons(*, gear, seed_directory,
                                          game_build, simc_revision):
    """Prepare only initialisation weapons from current sealed source data.

    One exact v230 parse for the entire bounded weapon pool, then reuse
    v169's weapon shape, primary and proficiency constraints. This is NOT
    full representative gear, G, item admission or a Native proof.
    """
    import v169_source_first_representative_stage as chooser
    import v231_simc_tier_item_join as tier
    import v232_simc_only_ordinary_representative as representative

    verified=chooser.gear.validate(gear)
    need(verified["season_build"]==game_build and
         verified.get("no_old_catalog_seed") is True,
         "V787_CURRENT_WEAPON_SOURCE_BUILD_REQUIRED")
    inventory=frozenset(inv for hands in
        chooser.contracts.SELECTED_WEAPON_INVENTORY.values()
        for types in hands.values() for inv in types)
    providers={row["item_id"]:row for row in
        verified["items"]+verified.get(
            "internal_conditional_mplus_plain_candidates",[])
        if row.get("category")=="plain_representative_candidate"
        and row.get("source_kinds") and row.get("item_set_id")==0
        and row.get("inventory_type") in inventory}
    need(0<len(providers)<=item_metadata.MAX_REQUEST_IDS,
         "V787_CURRENT_WEAPON_SOURCE_SCOPE_INVALID")
    metadata=item_metadata.from_seed(directory=seed_directory,
        item_ids=sorted(providers),allow_missing=True)
    need(metadata.get("game_build")==game_build and
         metadata.get("simc_revision")==simc_revision and
         type(metadata.get("source_receipt_sha256")) is str and
         HEX64.fullmatch(metadata["source_receipt_sha256"]) is not None and
         metadata.get("selection_mode")=="EXACT_REQUESTED_IDS_ALLOW_MISSING",
         "V787_CURRENT_WEAPON_SIMC_IDENTITY_DRIFT")
    rows=[]
    mismatched=[]
    for row in metadata["items"]:
        iid=row["item_id"]
        need(iid in providers,"V787_CURRENT_WEAPON_UNREQUESTED_ID")
        physical=providers[iid]
        if (any(row.get(k)!=physical.get(k) for k in
                ("inventory_type","class_id","subclass_id"))
                or row.get("item_set_id")!=0):
            mismatched.append(iid)
            continue
        # ItemSparse AllowableClass is signed; SimC DBC emits an unsigned
        # mask. In particular DB2 -1 means all bits set, not malformed.
        # Preserve the existing v169 per-class bit semantics, including
        # zero as no matching class, and intersect both original masks.
        simc_mask=row.get("allowed_class_mask")
        db2_mask=physical.get("allowed_class_mask")
        if not (type(simc_mask) is int and 0<=simc_mask<=0xffffffff and
                (db2_mask is None or type(db2_mask) is int and
                 -(1<<31)<=db2_mask<=0xffffffff)):
            mismatched.append(iid)
            continue
        mask=simc_mask if db2_mask is None else simc_mask & (db2_mask & 0xffffffff)
        if not mask:
            mismatched.append(iid)
            continue
        rows.append({**row,"category":"plain_representative_candidate",
                     "allowed_class_mask":mask})
    season=verified.get("db2_display_season_id")
    scopes={r["item_id"]:representative._source_scope_diagnostic(
        providers[r["item_id"]],season) for r in rows}
    explicit=[r for r in rows if
              scopes[r["item_id"]]["explicit_db2_match_no_world_state"]]
    conditional=[r for r in rows if
        scopes[r["item_id"]]["explicit_db2_match_no_world_state"] or
        (scopes[r["item_id"]]["status"]=="WORLD_STATE_EXPRESSION_PENDING"
         and scopes[r["item_id"]]["same_display_season_worldstate_pending"])]
    pools=((explicit,False),(conditional,False),(rows,True))
    selected={}
    pending={}
    for key,contract in sorted(chooser.contracts.CONTRACTS.items()):
        cls=key.split("/")[0]
        mask=1<<(tier.CLASS_ID[cls]-1)
        for pool,allow_fallback in pools:
            try:
                weapons=chooser.shape_weapons({"items":pool},
                    contract["weapon_form"],mask,spec_key=key,
                    allow_observed_offhand_fallback=allow_fallback)
            except chooser.RepresentativeBlocked as exc:
                pending[key]=str(exc)
            else:
                selected[key]={"weapons":weapons}
                pending.pop(key,None)
                break
    return {"schema":"v787_current_source_profile_default_weapons_v1",
            "game_build":game_build,"simc_revision":simc_revision,
            "source_receipt_sha256":metadata["source_receipt_sha256"],
            "item_data_sha256":metadata["source_sha256"],
            "specializations":selected,"missing_specializations":pending,
            "requested_weapon_count":len(providers),
            "matched_weapon_count":len(rows),
            "mismatched_item_ids":sorted(mismatched),
            "native_calls":0,"network_calls":0}



def observed_default_groups(observation):
    groups={"food":{},"potion":{}}
    for spec,choices in sorted(observation.get("observed_defaults",{}).items()):
        for kind,token in choices.items():
            if token not in ("disabled","source_default"):
                groups[kind].setdefault(token,[]).append(spec)
    return {kind:{token:" ".join(specs) for token,specs in values.items()}
            for kind,values in groups.items()}


def verify_default_observation(doc, *, game_build, simc_revision):
    import v143_specialization_contracts as contracts
    need(type(doc) is dict and
         doc.get("schema")=="v788_simc_default_observation_v1" and
         doc.get("game_build")==game_build and
         doc.get("simc_revision")==simc_revision and
         all(type(doc.get(k)) is str and HEX64.fullmatch(doc[k])
             for k in ("binary_sha256","weapon_source_receipt_sha256",
                       "initialization_sha256")) and
         doc.get("compiled_game_build_verified") is True and
         type(doc.get("character_level")) is int and
         1<=doc["character_level"]<=100 and
         type(doc.get("observed_defaults")) is dict and
         bool(doc["observed_defaults"]) and
         set(doc["observed_defaults"])<=set(contracts.CONTRACTS) and
         all(type(row) is dict and set(row)=={"food","potion"} and
             all(type(t) is str and re.fullmatch(r"[a-z0-9_]{1,100}",t)
                 for t in row.values())
             for row in doc["observed_defaults"].values()),
         "V788_DEFAULT_OBSERVATION_SCOPE_INVALID")
    return True


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


# Reviewed source evidence, NOT a runtime spell calculator. Keep this
# revision-bound snapshot alongside the existing reviewed APL input owner.
# Git blobs: item_effect f1d6075fd0649be30cc555284e71fc2add112ec0;
# sc_spell_data a18f81b125eb775651c8db27354030399a12e730;
# rand_prop_points 7923a7ca1fc975a26a9e160059930256ac07dca8;
# sc_scale_data f9f4386ff4e4d074a8340dc847db8dc65befbf69.
# Signed magnitudes from those exact source rows, rounded here ONLY for
# comparison. Same driver, duration (30s), cooldown (300s), physical
# requirements and identical item-effect fields for each pair. Liquid
# Luster shares its 6s period/5 stack trigger; Recklessness has four
# positive and four negative rating effects (crit penalty differs slightly).
# No claim about relative DPS, or reuse on another build/revision.
_REVIEWED_ITEM_DATA_SHA = "52bdeaeaf67992680f9b873c77181fe96f14f862a1e4a944b4b272c0f3fe0588"
_REVIEWED_QUALITY_FAMILIES = (
    ("Light's Potential", "lights_potential", "simc:reviewed_apl_input:spell:1236616",
     ((241309, 278, (593.190106,)), (241308, 295, (695.000005,)))),
    ("Potion of Recklessness", "potion_of_recklessness",
     "simc:consumables::potion_of_recklessness:spell:1236994",
     ((241289, 278, (1584.980031,)*4+(-213.462422, -213.168311, -213.168311, -213.168311)),
      (241288, 295, (1724.999824,)*4+(-232.320050, -231.999957, -231.999957, -231.999957)))),
    ("Liquid Luster", "liquid_luster", "simc:consumables::liquid_luster:spell:1295132",
     ((271886, 278, (358.474601,)), (271887, 295, (420.000009,)))),
)


def _reviewed_quality_scope(game_build, simc_revision):
    return (game_build=="12.1.5.70961" and
            simc_revision=="9933ffb946fb55b1fa66657b848f519ac19006e1")


def reviewed_quality_item_evidence(game_build, simc_revision, rows, metadata):
    """Bind the reviewed numerical source to the EXISTING exact item join.

    No raw file read, source download, Native or extra item scan. A source
    mismatch leaves the corresponding quality comparison pending.
    """
    if (not _reviewed_quality_scope(game_build, simc_revision) or
            metadata.get("source_sha256") != _REVIEWED_ITEM_DATA_SHA):
        return None
    by_id = {row["item_id"]: row for row in metadata["items"]}
    joined = {row["physical_item_id"] for row in rows}
    levels = {}
    for name, stem, effect, variants in _REVIEWED_QUALITY_FAMILIES:
        for rank, (iid, level, _) in enumerate(variants, 1):
            row = by_id.get(iid, {})
            if (iid in joined and row.get("name") == name and
                    row.get("ilevel_unscaled") == level and
                    row.get("crafting_quality") == rank and
                    row.get("class_id") == 0 and row.get("subclass_id") == 1 and
                    row.get("inventory_type") == 0):
                levels[str(iid)] = level
    return {"item_data_sha256": _REVIEWED_ITEM_DATA_SHA, "item_levels": levels}


def _reviewed_quality_family_components(game_build, simc_revision, rows, evidence):
    """Adapt the old exact reviewed snapshot; never extend its source scope."""
    if (not _reviewed_quality_scope(game_build, simc_revision) or
            type(evidence) is not dict or
            evidence.get("item_data_sha256") != _REVIEWED_ITEM_DATA_SHA or
            type(evidence.get("item_levels")) is not dict):
        return None
    for name, stem, effect, variants in _REVIEWED_QUALITY_FAMILIES:
        expected = {iid: (rank, level, vector)
                    for rank, (iid, level, vector) in enumerate(variants, 1)}
        if len(rows) != len(expected) or {r["physical_item_id"] for r in rows} != set(expected):
            continue
        for row in rows:
            iid = row["physical_item_id"]
            rank, level, vector = expected[iid]
            if (row["kind"] != "potion" or row["name_enUS"] != name or
                    row["simc_input_token"] != stem+"_"+str(rank) or
                    row["crafting_quality"] != rank or row["effect_identity"] != effect or
                    row["use_condition_identity"] != "wago_on_use_0" or
                    evidence["item_levels"].get(str(iid)) != level):
                return None
        # Positional component identities are confined to this exact
        # reviewed family. No guessed stat/effect meaning for future data.
        return {str(iid):{"reviewed_component_"+str(n):v
                          for n,v in enumerate(values[2])}
                for iid,values in expected.items()}
    return None


def signed_quality_family_winners(rows, components):
    """Compare complete, direction-normalized signed component maps.

    Internal source owners establish equivalent effects/use scope and
    complete component coverage before calling this function. Every
    component is oriented so a greater value is noninferior (penalties
    are negative). Never infer the orientation from a tooltip or name.
    No numerical rounding/tolerance, no DPS/effect simulation.
    """
    import math
    if (type(rows) is not list or len(rows)<2 or type(components) is not dict):
        return None
    ids=[str(row["physical_item_id"]) for row in rows]
    ranks=[row["crafting_quality"] for row in rows]
    if (len(set(ids))!=len(ids) or len(set(ranks))!=len(ranks) or
            any(type(rank) is not int or rank<1 for rank in ranks) or
            set(components)!=set(ids)):
        return None
    keys=None
    for values in components.values():
        if (type(values) is not dict or not values or
                any(type(k) is not str or not 0<len(k)<=160 for k in values) or
                any(type(v) not in (int,float) or abs(v)>1e15 or
                    not math.isfinite(v) for v in values.values())):
            return None
        if keys is None:
            keys=set(values)
        elif set(values)!=keys:
            return None
    return [row for row in rows if not any(
        other["crafting_quality"] > row["crafting_quality"] and
        all(components[str(other["physical_item_id"])][key] >=
            components[str(row["physical_item_id"])][key] for key in keys)
        for other in rows)]


QUALITY_EVIDENCE_SCHEMA="v792_optional_signed_quality_source_v1"


def source_quality_family_winners(game_build, simc_revision, rows, evidence):
    """Consume one source-owned comparable family, not a caller rank guess.

    v216 seals this internal evidence with the exact item/effect source.
    The consumer rechecks complete row identity and component coverage.
    A missing/mismatched family is optional PENDING, not BASE failure.
    """
    if (type(evidence) is not dict or
            evidence.get("schema")!=QUALITY_EVIDENCE_SCHEMA or
            evidence.get("game_build")!=game_build or
            evidence.get("simc_revision")!=simc_revision or
            any(type(evidence.get(k)) is not str or not HEX64.fullmatch(evidence[k])
                for k in ("item_data_sha256","item_source_receipt_sha256")) or
            type(evidence.get("families")) is not list):
        return None
    ordered=sorted(rows,key=lambda row:row["physical_item_id"])
    matches=[family for family in evidence["families"]
             if type(family) is dict and family.get("rows")==ordered]
    if len(matches)!=1:
        return None
    family=matches[0]
    if (family.get("effect_and_use_scope_verified") is not True or
            family.get("signed_component_coverage_complete") is not True or
            type(family.get("source_evidence_sha256")) is not str or
            not HEX64.fullmatch(family["source_evidence_sha256"])):
        return None
    return signed_quality_family_winners(rows,family.get("signed_components"))


def reviewed_quality_family_winners(game_build, simc_revision, rows, evidence):
    """Legacy exact-source adapter; preserve historical installed choices."""
    return signed_quality_family_winners(rows,
        _reviewed_quality_family_components(game_build,simc_revision,rows,evidence))


def reviewed_as_source_quality_evidence(game_build,simc_revision,rows,metadata,
                                        reviewed):
    """Convert only the already-proven exact snapshot into the shared shape.

    This is the first source owner of the v792 format. Future-season
    numeric extraction must supply its own actual authenticated proof;
    never synthesize this proof from same-name, ilvl or quality alone.
    """
    import hashlib
    receipt=metadata.get("source_receipt_sha256")
    if (type(reviewed) is not dict or
            type(receipt) is not str or not HEX64.fullmatch(receipt)):
        return None
    by_id={row["physical_item_id"]:row for row in rows}
    families=[]
    for _,_,_,variants in _REVIEWED_QUALITY_FAMILIES:
        if any(v[0] not in by_id for v in variants):
            continue
        group=sorted((by_id[v[0]] for v in variants),
                     key=lambda row:row["physical_item_id"])
        components=_reviewed_quality_family_components(
            game_build,simc_revision,group,reviewed)
        if signed_quality_family_winners(group,components) is None:
            continue
        proof={"rows":group,"signed_components":components,
               "reviewed_item_evidence":reviewed,
               "game_build":game_build,"simc_revision":simc_revision}
        proof_sha=hashlib.sha256(json.dumps(proof,sort_keys=True,
            separators=(",",":"),ensure_ascii=False,allow_nan=False).encode("utf8")).hexdigest()
        families.append({"rows":group,"signed_components":components,
            "effect_and_use_scope_verified":True,
            "signed_component_coverage_complete":True,
            "source_evidence_sha256":proof_sha})
    return {"schema":QUALITY_EVIDENCE_SCHEMA,"game_build":game_build,
            "simc_revision":simc_revision,"item_data_sha256":metadata["source_sha256"],
            "item_source_receipt_sha256":receipt,"families":families} if families else None



# Direct generic potion stat auras only. These are static source values,
# not a recreation of custom proc/APL/effect behavior.
_QUALITY_DIRECT_POTION=re.compile(r"simc:reviewed_apl_input:spell:([1-9][0-9]*)\Z")
_QUALITY_RATING_MASK=0x00000700|0x000e0000|0x02000000|0x70000000


def pending_direct_quality_families(rows,metadata,known):
    """Do not collect extra source for already-proven or unrelated items."""
    known_rows=[f["rows"] for f in (known or {}).get("families",[])]
    by_id={row["item_id"]:row for row in metadata["items"]}
    groups={}
    for row in rows:
        rank=row["crafting_quality"]
        token=row["simc_input_token"]
        suffix="_"+str(rank)
        stem=token[:-len(suffix)] if 1<=rank<=9 and token.endswith(suffix) else token
        key=(row["kind"],row["effect_identity"],row["use_condition_identity"],stem)
        groups.setdefault(key,[]).append(row)
    pending=[]
    for (kind,effect,use,stem),group in groups.items():
        ordered=sorted(group,key=lambda row:row["physical_item_id"])
        if (kind!="potion" or not _QUALITY_DIRECT_POTION.fullmatch(effect) or
                use!="wago_on_use_0" or len(group)<2 or ordered in known_rows or
                len({row["crafting_quality"] for row in group})!=len(group) or
                any(not 1<=row["crafting_quality"]<=9 or
                    row["simc_input_token"]!=stem+"_"+str(row["crafting_quality"])
                    for row in group)):
            continue
        items=[by_id.get(row["physical_item_id"],{}) for row in group]
        scopes=[metadata.get("consumable_quality_physical_scopes",{}).get(
            str(row["physical_item_id"])) for row in group]
        if (any(type(s) is not str or not HEX64.fullmatch(s) for s in scopes) or
                len(set(scopes))!=1 or
                any(row.get("stat_modifier_codes") or row.get("item_set_id")!=0 or
                    row.get("intrinsic_socket_count_from_simc_source")!=0
                    for row in items)):
            continue
        pending.append(ordered)
    return pending


def _quality_float(raw):
    import math
    import struct
    value=float(raw.rstrip("fF"))
    if raw.endswith(("f","F")):
        value=struct.unpack("f",struct.pack("f",value))[0]
    need(math.isfinite(value),"V794_NONFINITE_SOURCE_VALUE")
    return value


def _quality_array(raw,build,header,head,row_pattern,decode,wanted,*,closing):
    """Scan exactly the declared generated array; parse only selected rows."""
    import io
    lines=io.BytesIO(raw)
    found={}
    active=False
    expected=None
    seen=0
    header_seen=False
    for line in lines:
        line=line.decode("utf8").strip()
        if not active:
            if re.fullmatch(header,line):
                header_seen=True
                need(line.endswith(build),"V794_QUALITY_SOURCE_BUILD_DRIFT")
            m=re.fullmatch(head,line)
            if m:
                need(header_seen,"V794_QUALITY_SOURCE_HEADER_MISSING")
                expected=int(m.group(1))
                active=True
            continue
        if line==closing:
            need(seen==expected,"V794_QUALITY_ARRAY_COUNT_DRIFT")
            return found
        if not line or line.startswith("//"):
            continue
        m=re.match(row_pattern,line)
        need(m is not None,"V794_QUALITY_ARRAY_ROW_LAYOUT")
        seen+=1
        key=int(m.group(1))
        if key in wanted:
            record=decode(line)
            found.setdefault(key,[]).append(record)
    raise OptionalConsumableSourceBlocked("V794_QUALITY_ARRAY_NOT_COMPLETE")


def _quality_fields(line,count):
    # Generated comments follow a complete row; do not split a quoted name.
    return item_metadata.split_cpp_record(
        re.sub(r"\s*(?:/\*.*\*/|//[^\n]*)$","",line).strip(),field_count=count)


def _quality_int(raw):
    return int(raw,16 if raw.lower().startswith("0x") else 10)


def _quality_spell_fields(raw,build,spells):
    spell_rows=_quality_array(raw,build,r"// \d+ spells, wow build level [0-9.]+",
        r"static spell_data_t __spell_data\[(\d+)\] = \{",
        r'\{\s*"(?:\\.|[^"\\])*"\s*,\s*(\d+)\s*,',
        lambda line:_quality_fields(line,56),spells,closing="};")
    effects=_quality_array(raw,build,r"// \d+ effects, wow build level [0-9.]+",
        r"static spelleffect_data_t __spelleffect_data\[(\d+)\] = \{",
        r"\{\s*\d+\s*,\s*(\d+)\s*,",
        lambda line:_quality_fields(line,31),spells,closing="};")
    return spell_rows,effects


def _direct_item_stat_components(spell, spell_effects, budget, trinket_multiplier):
    """Bounded source-data average, not combat behavior.

    Exact 70961 spell_data.cpp average(item) uses item_budget for -1
    (and other ordinary classes), special branches for -7/-8/-9/0.
    Restrict to observed direct stat rows, no clamp/override/delta.
    Identical rarity first-column budgets avoid assuming the synthetic
    consumable item's quality. Unsupported shape returns None.
    """
    import math
    attrs=[_quality_int(v.strip()) for v in spell[39][1:-1].split(",")]
    if (len(attrs)!=17 or not attrs[11]&(1<<2) or
            any(_quality_int(spell[n])!=0 for n in (8,9,10)) or
            _quality_int(spell[52])!=len(spell_effects) or
            not 1<=len(spell_effects)<=16 or
            len({e[2] for e in spell_effects})!=len(spell_effects)):
        return None
    rarities=[_quality_float(budget[n][1:-1].split(",")[0].strip())
              for n in (3,4,5)]
    if len(set(rarities))!=1 or rarities[0]<=0:
        return None
    values={}
    for e in spell_effects:
        etype,subtype,scaling=map(_quality_int,e[3:6])
        misc=_quality_int(e[16])
        if (etype!=6 or subtype not in (29,189) or
                (subtype==29 and misc not in (-2,0,1,3)) or
                (subtype==189 and (misc<=0 or misc&~_QUALITY_RATING_MASK)) or
                scaling not in (-1,-7,-8,-9,0) or
                _quality_int(e[19])!=0 or
                any(_quality_float(e[n])!=0 for n in (8,9,10,11,12,14,21,22))):
            return None
        coefficient=_quality_float(e[7])
        if coefficient==0:
            return None
        if scaling==-1:
            scale_value=rarities[0]
        elif scaling==-7:
            scale_value=rarities[0]*(trinket_multiplier or 1)
        else:
            scale_value=_quality_float(budget[1 if scaling==-8 else 2])
        value=coefficient*scale_value
        if scale_value<=0 or not math.isfinite(value):
            return None
        values["spell_effect:"+e[0]+":"+str(subtype)+":"+str(misc)]=value
    return values if len(values)==len(spell_effects) else None


def direct_quality_source_families(*,game_build,simc_revision,rows,metadata,
                                  families,source_bytes):
    """Extract complete signed static stat components for exact direct auras.

    Unknown spell/scale shapes remain pending. This supports item-level
    average branches -1/-7/-8/-9/0 only, with no clamp/override/delta, and
    requires exact full same-driver ItemEffect rows and physical scope.
    """
    import hashlib
    import math
    by_id={row["item_id"]:row for row in metadata["items"]}
    spell_ids={int(_QUALITY_DIRECT_POTION.fullmatch(g[0]["effect_identity"]).group(1))
               for g in families}
    item_ids={r["physical_item_id"] for g in families for r in g}
    levels={by_id[i]["ilevel_unscaled"] for i in item_ids}
    if not spell_ids:
        return []
    effects_by_item=_quality_array(source_bytes["item_effect.inc"],game_build,
        r"// Item effects, wow build [0-9.]+",
        r"static constexpr std::array<item_effect_t, (\d+)> __item_effect_data \{ \{",
        r"\{\s*\d+\s*,\s*\d+\s*,\s*(\d+)\s*,",
        lambda line:tuple(map(_quality_int,_quality_fields(line,8))),
        item_ids,closing="} };")
    spells,effects=_quality_spell_fields(source_bytes["sc_spell_data.inc"],
                                         game_build,spell_ids)
    budget_rows=_quality_array(source_bytes["rand_prop_points.inc"],game_build,
        r"// Random property points for item levels 1-\d+, wow build [0-9.]+",
        r"static constexpr std::array<random_prop_data_t, (\d+)> __rand_prop_points_data \{ \{",
        r"\{\s*(\d+)\s*,",lambda line:_quality_fields(line,6),
        levels,closing="} };")
    scale=source_bytes["sc_scale_data.inc"].decode("utf8")
    match=re.search(r"(?m)^// Combat rating multipliers for item level 1 - (\d+), wow build ([0-9.]+)\s*\n"
                    r"static constexpr double __combat_ratings_mult_by_ilvl\[\]\[\1\] = \{",scale)
    need(match is not None and match.group(2)==game_build,
         "V794_CR_SCALE_HEADER_DRIFT")
    end=scale.find("\n};",match.end())
    need(end>=0,"V794_CR_SCALE_ARRAY_NOT_COMPLETE")
    groups=re.findall(r"// ([^\n]+) Multiplier\s*\n\s*\{([^{}]*)\}",
                      scale[match.end():end])
    need([name for name,_ in groups]==["Armor","Weapon","Trinket","Jewelry"],
         "V794_CR_SCALE_TYPE_ORDER_DRIFT")
    trinket=[_quality_float(v.strip()) for v in
             re.sub(r"//[^\n]*","",groups[2][1]).split(",") if v.strip()]
    need(len(trinket)==int(match.group(1)),"V794_CR_SCALE_LENGTH_DRIFT")
    source_hashes={name:hashlib.sha256(raw).hexdigest()
                   for name,raw in source_bytes.items()}
    output=[]
    for group in families:
        try:
            sid=int(_QUALITY_DIRECT_POTION.fullmatch(group[0]["effect_identity"]).group(1))
            ids=[row["physical_item_id"] for row in group]
            links=[effects_by_item.get(i,[]) for i in ids]
            # All ItemEffect fields except record ID and ItemID identical.
            if (any(len(link)!=1 for link in links) or
                    any(link[0][1]!=sid or link[0][4]!=0 for link in links) or
                    len({(l[0][1],*l[0][3:]) for l in links})!=1 or
                    len(spells.get(sid,[]))!=1):
                continue
            spell=spells[sid][0]
            spell_effects=effects.get(sid,[])
            components={}
            for iid in ids:
                level=by_id[iid]["ilevel_unscaled"]
                if not 1<=level<=len(trinket) or len(budget_rows.get(level,[]))!=1:
                    break
                values=_direct_item_stat_components(spell,spell_effects,
                    budget_rows[level][0],trinket[level-1])
                if values is None:
                    break
                components[str(iid)]=values
            if signed_quality_family_winners(group,components) is None:
                continue
            proof={"game_build":game_build,"simc_revision":simc_revision,
                   "rows":group,"signed_components":components,
                   "physical_scope_sha256":metadata[
                       "consumable_quality_physical_scopes"][str(ids[0])],
                   "source_hashes":source_hashes,"spell_id":sid}
            output.append({"rows":group,"signed_components":components,
                # APL-input identity plus identical physical source rows
                # does not establish absence of a custom effect override.
                # These are DBC observations, NOT an admission receipt.
                "effect_and_use_scope_verified":False,
                "signed_component_coverage_complete":True,
                "source_evidence_sha256":hashlib.sha256(
                    stage_engine.canonical(proof).encode("utf8")).hexdigest()})
        except (ValueError,TypeError,KeyError,IndexError,OverflowError):
            continue
    return output


def collect_direct_quality_source(*,stage_root,game_build,simc_revision,
                                  rows,metadata,known,transport=None):
    """On demand, exact immutable Git bytes via existing v229 and v217.

    Never fetch for an already-proven family. Store the raw source once per
    build/revision, independently of optimizer code/target ilvl. No Native.
    """
    import v229_simc_only_source_seed as seed
    groups=pending_direct_quality_families(rows,metadata,known)
    if not groups:
        return known,{"status":"NO_ELIGIBLE_UNRESOLVED_DIRECT_FAMILY",
                      "network_calls":0,"new_families":0}
    root=pathlib.Path(stage_root)
    calls=[0]
    try:
        need(seed.REV.fullmatch(simc_revision) and seed.BUILD.fullmatch(game_build),
             "V794_EXACT_SOURCE_IDENTITY_REQUIRED")
        key=seed.digest((game_build+":"+simc_revision).encode("utf8"))[:24]
        outputs={name:"source/v794_quality_"+key+"/"+name
                 for name in seed.OPTIONAL_QUALITY_FILES}
        def fetch(req,timeout):
            calls[0]+=1
            return (seed.urlopen if transport is None else transport)(req,timeout=timeout)
        def execute():
            tree=seed.discover_generated_tree(simc_revision,transport=fetch,quality_files=True)
            for name,relative in outputs.items():
                meta=tree[name]
                raw=seed.fetch_generated_blob(revision=simc_revision,name=name,
                    expected_sha=meta["sha"],expected_size=meta["size"],transport=fetch)
                need(len(raw)==meta["size"] and seed.git_blob(raw)==meta["sha"],
                     "V794_PINNED_SOURCE_BLOB_DRIFT:"+name)
                path=root/relative
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(raw)
        def validate(files):
            return all(0<files[name].stat().st_size<=limit and
                       game_build.encode("ascii") in
                       seed.bounded_read(files[name],limit)[:256]
                       for name,limit in seed.OPTIONAL_QUALITY_FILES.items())
        stage=stage_engine.execute_stage(root=root,stage_id="fresh-v794-quality-raw-"+key,
            stage_version="v794-exact-generated-source-v1",
            inputs={"game_build":game_build,"simc_revision":simc_revision},
            outputs=outputs,execute=execute,validate=validate)
        raw={name:seed.bounded_read(root/outputs[name],limit)
             for name,limit in seed.OPTIONAL_QUALITY_FILES.items()}
        found=direct_quality_source_families(game_build=game_build,
            simc_revision=simc_revision,rows=rows,metadata=metadata,
            families=groups,source_bytes=raw)
        # Do not replace previously reviewed choices with a DBC-only
        # result. Keep compact observations for the existing source owner.
        return known,{"status":"DIRECT_SOURCE_NUMERICS_UNADMITTED",
                      "network_calls":calls[0],"new_families":0,
                      "observed_family_count":len(found),
                      "observed_families_unadmitted":found,
                      "candidate_families":len(groups),
                      "raw_source_stage_sha256":stage["receipt_sha256"]}
    except (ValueError,KeyError,TypeError,OSError,OverflowError) as exc:
        return known,{"status":"DIRECT_QUALITY_SOURCE_PENDING",
                      "reason":str(exc)[:200],"network_calls":calls[0],
                      "new_families":0}


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
