#!/usr/bin/env python3
"""v583: same-build Wago crafted permanent-enchant item → pinned SimC ID.

An OPTIONAL, source-only stage of the ORIGINAL v216 Environment Build.
Reuse v161 Item/ItemSparse/CraftingData, v254 ItemXItemEffect,
v280 ItemEffect, v281 SpellEffect and v275 permanent_enchant.inc.
Download just CraftingDataEnchantQuality once per game build through v217.
The raw Wago table is revision-independent; only the compact exact-ID
projection is revision/source-receipt scoped. No Native, E, UI or Policy A.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import v190_consumable_item_snapshot_join as csvsource
import v191_unified_season_data_update as simc
import v217_stage_execution_engine as stages
import v281_consumable_simc_relation as spells
import v584_supplemental_permanent_enchant_classification as supplemental

SCHEMA = "v583_same_build_permanent_enchant_item_relation_v1"
QUALITY_CSV = "source/v583_CraftingDataEnchantQuality.csv"
QUALITY_STAGE = "fresh-v583-enchant-quality-csv"
MAX_BYTES = 40_000_000
SEALS = frozenset(("EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED"))
EFFECT_CRAFT = 301
EFFECT_LEGACY = 53
TYPE_ENCHANT = 3


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def need(ok, why):
    if not ok:
        raise ValueError(why)


def pending(reason, calls=0):
    return {"schema": SCHEMA, "status": "PERMANENT_ENCHANT_SOURCE_PENDING",
            "reason": reason, "candidate_path": None,
            "network_calls_by_stage": calls, "native_calls": 0,
            "environment_ready": False, "automatic_ui_promotion": False}


def _source_path(root, stage, key):
    need(type(stage) is dict and stage.get("status") in SEALS,
         "V583_UPSTREAM_STAGE_PENDING")
    rel = stage.get("output_paths", {}).get(key)
    need(type(rel) is str and rel and not Path(rel).is_absolute()
         and ".." not in Path(rel).parts, "V583_SOURCE_RELATIVE_PATH_REQUIRED")
    path = root / rel
    need(path.resolve().is_relative_to(root)
         and path.is_file() and not path.is_symlink(),
         "V583_UPSTREAM_OUTPUT_MISSING")
    return path


def _identity(root, stage):
    need(type(stage) is dict and stage.get("status") in SEALS
         and type(stage.get("receipt_sha256")) is str
         and len(stage["receipt_sha256"]) == 64, "V583_UPSTREAM_RECEIPT_MISSING")
    path = root / ".stage_receipts" / (stage["stage_id"] + ".json")
    need(path.is_file() and not path.is_symlink()
         and path.resolve().is_relative_to(root),
         "V583_UPSTREAM_SEAL_MISSING")
    receipt = stages._read_receipt(path)
    need(receipt.get("status") == "COMPLETE"
         and receipt.get("receipt_sha256") == stage["receipt_sha256"],
         "V583_UPSTREAM_SEAL_CHANGED")
    return stage["receipt_sha256"]


def _quality_table(*, root, build, transport=None, attempted=None):
    outputs = {"csv": QUALITY_CSV}
    source_url = "https://wago.tools/db2/CraftingDataEnchantQuality/csv?" + urlencode(
        {"build": build, "locale": "enUS"})
    # Do not key this immutable game-build snapshot by the SimC revision.
    # Raw immutable CSV identity: game build + URL + explicit fetch contract.
    # Parser/SimC revision changes must not invalidate these Wago bytes.
    calls = attempted if attempted is not None else [0]

    def execute():
        request = Request(source_url, headers={
            "User-Agent": "SIMC-Secondary-v583-EnchantSource/1.0",
            "Accept": "text/csv"})
        calls[0] += 1
        target = root / QUALITY_CSV
        target.parent.mkdir(parents=True, exist_ok=True)
        total = 0
        with (urlopen if transport is None else transport)(
                request, timeout=90) as response:
            need(response.status == 200, "V583_WAGO_QUALITY_HTTP_NON200")
            with target.open("wb") as out:
                while True:
                    chunk = response.read(262144)
                    if not chunk: break
                    total += len(chunk)
                    need(total <= MAX_BYTES, "V583_WAGO_QUALITY_SIZE_LIMIT")
                    out.write(chunk)
        need(total > 0, "V583_WAGO_QUALITY_EMPTY")

    def validate(paths):
        path = paths["csv"]
        if not (path.is_file() and 0 < path.stat().st_size <= MAX_BYTES):
            return False
        with path.open("r", encoding="utf-8-sig") as stream:
            import csv
            header = next(csv.reader(stream))
        return set(("ID","Rank","SpellItemEnchantmentID","ItemID",
                    "CraftingDataID")) <= set(header)

    summary = stages.execute_stage(
        root=root, stage_id=QUALITY_STAGE, stage_version="single-db2-by-build-v1",
        inputs={"build":build,"table":"CraftingDataEnchantQuality",
                "source_url":source_url,"fetch_contract":"WAGO_CSV_BOUNDED_V1"},
        outputs=outputs,execute=execute,validate=validate)
    return summary,calls[0]


def _additional_scope_from_original_simc(rows):
    """Discover combat-gear types from SimC class/masks, NEVER token spelling.

    Physical Wago expansion membership has already been proven separately.
    A SimC class 19 is a profession tool, not DPS character gear. A Wago
    scroll with no exact SimC source record is UNRESOLVED rather than guessed
    from its English name or physical item subclass.
    """
    if not rows:
        return {"scope":"SIMC_PERMANENT_EQUIPMENT_SCOPE_UNRESOLVED",
                "gear_kind":None,"applicability_source":None}
    types=set()
    for row in rows:
        if row["item_class"]==4 and row["inventory_type_mask"]>0:
            types.add("armor")
        elif row["item_class"]==2 and row["item_subclass_mask"]>0:
            types.add("weapon")
        elif row["item_class"]==19:
            types.add("profession")
        else:
            types.add("other")
    if types=={"profession"}:
        return {"scope":"PROFESSION_TOOL_OUTSIDE_DPS_EQUIPMENT",
                "gear_kind":None,"applicability_source":"SIMC_ITEM_CLASS_19"}
    if types=={"armor"} or types=={"weapon"}:
        return {"scope":"DPS_EQUIPMENT_PERMANENT_CANDIDATE_UNADMITTED",
                "gear_kind":next(iter(types)),
                "applicability_source":"SIMC_EQUIPMENT_CLASS_AND_MASK"}
    return {"scope":"SIMC_EQUIPMENT_APPLICABILITY_AMBIGUOUS",
            "gear_kind":None,"applicability_source":"SIMC_MIXED_OR_OTHER_MASKS"}


def join_existing_sources(*, item, sparse, crafting, relation, effect,
                          spell_effect, quality, simc_enchants, build, expansion_id):
    """Single source-only exact-FK join, using only previously sealed files.

    Wago effect 301 carries a CraftingData ID, NOT an enchant ID. A physical
    ItemID must equal the CraftingDataEnchantQuality ItemID. Effect 53 is
    permitted only as an exact legacy direct-ID path, never rank inference.
    """
    generated=simc.parse_generated("permanent_enchant",simc_enchants.read_bytes())
    need(generated["source_build"]==build, "V583_SIMC_SOURCE_BUILD_MISMATCH")
    all_rows=[r for r in generated["rows"] if r["simc_token"].startswith("enchant_")
              and r["item_class"] in (2,4)]
    highest=simc.current_season_enchant_candidates(generated)
    by_id={}
    for row in all_rows:
        by_id.setdefault(row["enchant_id"],[]).append(row)
    all_source_by_id={}
    for row in generated["rows"]:
        all_source_by_id.setdefault(row["enchant_id"],[]).append(row)

    candidates={}
    for row in csvsource.csvrows(item,("ID","ClassID","SubclassID")):
        cls,sub=int(row["ClassID"]),int(row["SubclassID"])
        if cls==8 or (cls==0 and sub in (6,8)):
            iid=int(row["ID"])
            need(iid>0 and iid not in candidates,"V583_DUPLICATE_ITEM_ID")
            candidates[iid]={"item_class":cls,"item_subclass":sub}
    physical={}
    for row in csvsource.csvrows(sparse,("ID","ExpansionID","Display_lang")):
        iid=int(row["ID"])
        if iid in candidates and int(row["ExpansionID"])==expansion_id:
            need(iid not in physical,"V583_DUPLICATE_SPARSE_ITEM_ID")
            name=row["Display_lang"].strip()
            need(name and len(name)<=250,"V583_ITEM_NAME_MISSING")
            physical[iid]={**candidates[iid],"item_id":iid,
                           "expansion_id":expansion_id,"name_enUS":name}

    item_effect_ids={}
    for row in csvsource.csvrows(relation,("ItemID","ItemEffectID")):
        iid=int(row["ItemID"])
        if iid in physical and int(row["ItemEffectID"])>0:
            item_effect_ids.setdefault(int(row["ItemEffectID"]),set()).add(iid)
    spells_by_id={}
    for row in csvsource.csvrows(effect,("ID","SpellID","TriggerType")):
        eid=int(row["ID"])
        if eid in item_effect_ids:
            sid=int(row["SpellID"])
            if sid>0:
                spells_by_id.setdefault(sid,[]).extend(
                    (iid,eid,int(row["TriggerType"]))
                    for iid in item_effect_ids[eid])
    craft_types=set()
    for row in csvsource.csvrows(crafting,("ID","Type")):
        if int(row["Type"])==TYPE_ENCHANT:
            craft_types.add(int(row["ID"]))
    quality_by_craft={}
    for row in csvsource.csvrows(
            quality,("ID","Rank","SpellItemEnchantmentID","ItemID","CraftingDataID")):
        cid=int(row["CraftingDataID"])
        iid=int(row["ItemID"])
        ench=int(row["SpellItemEnchantmentID"])
        if cid in craft_types and iid in physical and ench>0:
            quality_by_craft.setdefault(cid,[]).append({
                "item_id":iid,"enchant_id":ench,"wago_rank":int(row["Rank"]),
                "source_quality_row_id":int(row["ID"])})

    found={}
    additional={}
    missing_simc_ids=set()
    seen=set()
    for entry in spells.scan_spell_effects(spell_effect,set(spells_by_id)):
        effect_code=entry["effect"]
        if effect_code not in (EFFECT_CRAFT,EFFECT_LEGACY):
            continue
        for iid,eid,trigger in spells_by_id[entry["spell_id"]]:
            if effect_code==EFFECT_CRAFT:
                rows=(q for q in quality_by_craft.get(entry["enchant_id"],())
                      if q["item_id"]==iid)
            else:
                rows=({"item_id":iid,"enchant_id":entry["enchant_id"],
                       "wago_rank":None,"source_quality_row_id":None},)
            for q in rows:
                target=q["enchant_id"]
                outside_original=target not in by_id
                if outside_original:
                    missing_simc_ids.add(target)
                key=(target,iid,entry["spell_id"],eid,trigger,
                     entry["effect_index"],q["source_quality_row_id"])
                if key in seen:continue
                seen.add(key)
                (additional if outside_original else found).setdefault(target,[]).append({
                    **physical[iid],"apply_spell_id":entry["spell_id"],
                    "item_effect_id":eid,"item_effect_trigger_type":trigger,
                    "quality_rank_wago":q["wago_rank"],
                    "crafting_data_id":(entry["enchant_id"]
                                        if effect_code==EFFECT_CRAFT else None),
                    "wago_quality_row_id":q["source_quality_row_id"],
                    "exact_join":("WAGO_301_CRAFTDATA_QUALITY_TO_SIMC_ID"
                                  if effect_code==EFFECT_CRAFT else
                                  "WAGO_53_DIRECT_TO_SIMC_ID")})

    # Classify all other same-expansion enchant IDs by actual SimC gear
    # class/masks, including names without an enchant_ prefix. Preserve
    # physically linked no-SimC rows for optional module/scope review.
    additional_rows=[]
    additional_gear=[]
    for eid in sorted(additional):
        source_rows=all_source_by_id.get(eid,[])
        scope=_additional_scope_from_original_simc(source_rows)
        if scope["scope"]=="DPS_EQUIPMENT_PERMANENT_CANDIDATE_UNADMITTED":
            additional_gear.extend(source_rows)
        additional_rows.append({
            "enchant_id":eid,**scope,
            "simc_source_rows":source_rows,
            "physical_items":sorted(additional[eid],
                                    key=lambda x:(x["item_id"],
                                                  x["apply_spell_id"])),
            "ui_selectable":False,
            "effect_and_quality_not_approved":True})
    # Source highest-rank is a candidate only; same-effect dominance and
    # applicable slot/hand proof remain owned by v211/v196, not this stage.
    gear_high=simc.highest_known_quality(
        additional_gear,"permanent_enchant") if additional_gear else []
    scope_counts={}
    for row in additional_rows:
        tag=row["scope"]
        scope_counts[tag]=scope_counts.get(tag,0)+1
    additional_gear_ids={r["enchant_id"] for r in additional_gear}
    additional_high_ids={r["enchant_id"] for r in gear_high}
    high_ids={r["enchant_id"] for r in highest}
    # Do not claim 38/38 for an unmeasured future expansion/build.
    return {"schema":SCHEMA,
            "status":"PERMANENT_ENCHANT_EXACT_WAGO_SIMC_SOURCE_ONLY",
            "game_build":build,"expansion_id":expansion_id,
            "simc_generated_sha256":generated["sha256"],
            "highest_simc_candidate_count":len(highest),
            "highest_simc_candidate_linked":len(high_ids&set(found)),
            "highest_simc_candidate_missing_ids":sorted(high_ids-set(found)),
            "all_rank_simc_id_linked":len(found),
            "physical_item_ids_linked":len({row["item_id"] for group in found.values()
                                           for row in group}),
            # Historical field name means outside original enchant_ token
            # subset; many IDs DO exist in full SimC generated data.
            "other_wago_enchant_ids_not_in_simc_source":sorted(missing_simc_ids),
            "additional_wago_id_classification_counts":scope_counts,
            "additional_dps_gear_candidate_count":len(additional_gear_ids),
            "additional_dps_gear_highest_source_rank_candidate_count":
                len(additional_high_ids),
            "additional_dps_gear_highest_source_rank_candidate_ids":
                sorted(additional_high_ids),
            "additional_enchants_unadmitted":additional_rows,

            "source_only":True,"automatic_ui_promotion":False,
            "same_expansion_not_season_specific":True,
            "highest_quality_effect_equivalence_verified":False,
            "static_E_measured":False,"native_calls":0,
            "matches":[{"enchant_id":i,
                        "simc_rank_rows":by_id[i],
                        "physical_items":sorted(found[i],key=lambda x:x["item_id"])}
                       for i in sorted(found)]}


def collect(*, stage_root, build, expansion_id, wago_stage, fresh_gear,
            item_spells, simc_effects, pinned_simc, transport=None):
    """Optional v217 source stage; no new request unless all old sources exist."""
    root=Path(stage_root).resolve()
    deps={"wago":wago_stage,"gear":(fresh_gear or {}).get("source_stage"),
          "item_effect":(item_spells or {}).get("source_stage"),
          "spell_effect":(simc_effects or {}).get("source_stage"),
          "simc":(pinned_simc or {}).get("source_stage")}
    if (type(build) is not str or type(expansion_id) is not int or
            expansion_id<=0 or any(type(s) is not dict or
            s.get("status") not in SEALS for s in deps.values())):
        return pending("V583_EXISTING_SEALED_SOURCES_OR_EXPANSION_PENDING")
    calls=[0]
    try:
        identity={k:_identity(root,s) for k,s in deps.items()}
        wago=root/"wago"
        source_receipt=json.loads((wago/"receipt.json").read_text("utf8"))
        need(source_receipt.get("build")==build and
             source_receipt.get("source")=="wago.tools/db2",
             "V583_WAGO_GAME_BUILD_MISMATCH")
        original={
            "item":wago/"Item.csv","sparse":wago/"ItemSparse.csv",
            "crafting":wago/"CraftingData.csv",
            "relation":_source_path(root,deps["gear"],"effect"),
            "effect":_source_path(root,deps["item_effect"],"item_effect"),
            "spell_effect":_source_path(root,deps["spell_effect"],"spell_effect"),
            "simc_enchants":_source_path(root,deps["simc"],"permanent_enchant.inc")}
        need(all(p.is_file() and not p.is_symlink()
                 and p.resolve().is_relative_to(root) for p in original.values()),
             "V583_ORIGINAL_SOURCE_PATH_INVALID")
        for kind,path in (("Item",original["item"]),
                          ("ItemSparse",original["sparse"]),
                          ("CraftingData",original["crafting"])):
            # Immutable v161 receipt describes these same-build bytes.
            meta=source_receipt.get("tables",{}).get(kind,{})
            need(meta.get("bytes")==path.stat().st_size and
                 type(meta.get("sha256")) is str,
                 "V583_ORIGINAL_WAGO_TABLE_IDENTITY_MISSING:"+kind)
        quality_stage,network_calls=_quality_table(
            root=root,build=build,transport=transport,attempted=calls)
        original["quality"]=root/QUALITY_CSV
        quality_sha=quality_stage["receipt_sha256"]
        code=stages.module_dependency_fingerprint([
            Path(__file__),Path(simc.__file__),Path(stages.__file__),
            Path(supplemental.__file__),Path(supplemental.effect.__file__),
            Path(supplemental.slots.__file__)])
        # Output identity includes parser code. Updating the connector
        # reprojects a small manifest, never overwrites a sealed old output
        # or forces a second Wago download within the same build.
        projection_identity=sha(json.dumps({
            "build":build,"expansion":expansion_id,"upstream":identity,
            "quality":quality_sha,"projection_code":code["sha256"]},
            sort_keys=True).encode())[:20]
        stage_id="fresh-v583-enchant-join-"+projection_identity
        output="source/v583_permanent_join_"+projection_identity+".json"
        def execute():
            data=join_existing_sources(**original,build=build,
                                       expansion_id=expansion_id)
            data["source_stage_receipts"]=identity
            data["quality_csv_stage_receipt_sha256"]=quality_sha
            data["simc_revision"]=pinned_simc.get("simc_revision")
            # Original v191→v211→v213 helpers, reused only for newly
            # Wago-linked extra gear families. Source-only optional output:
            # no impact on the existing base catalog or budget.
            data["supplemental_gear_effects_source_only"]=supplemental.classify(
                relation=data,
                source_dir=pinned_simc.get("source_dir"),
                manifest_path=pinned_simc.get("manifest_path"),
                game_build=build,
                simc_revision=pinned_simc.get("simc_revision"))
            target=root/output
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(json.dumps(
                data,sort_keys=True,ensure_ascii=False,
                indent=2,allow_nan=False)+"\n",encoding="utf8")
        def validate(paths):
            row=json.loads(paths["candidate"].read_text("utf8"))
            return (row.get("schema")==SCHEMA and
                    row.get("status")==
                    "PERMANENT_ENCHANT_EXACT_WAGO_SIMC_SOURCE_ONLY"
                    and row.get("game_build")==build
                    and row.get("expansion_id")==expansion_id
                    and row.get("source_stage_receipts")==identity
                    and row.get("quality_csv_stage_receipt_sha256")==quality_sha
                    and row.get("source_only") is True
                    and row.get("automatic_ui_promotion") is False
                    and row.get("native_calls")==0)
        projection=stages.execute_stage(
            root=root,stage_id=stage_id,stage_version="v583-source-only-join-v1",
            inputs={"build":build,"expansion_id":expansion_id,
                    "receipts":identity,"quality_receipt":quality_sha,
                    "code_sha256":code["sha256"]},
            outputs={"candidate":output},execute=execute,validate=validate)
        row=json.loads((root/output).read_text("utf8"))
        supplementary=row.get("supplemental_gear_effects_source_only",{})
        return {"schema":SCHEMA,"status":row["status"],
                "supplemental_gear_effects_status":supplementary.get("status"),
                "supplemental_gear_effects_candidate_count":
                    supplementary.get("candidate_count",0),
                "candidate_path":str((root/output).resolve()),
                "counts":{key:row[key] for key in (
                    "highest_simc_candidate_count",
                    "highest_simc_candidate_linked",
                    "highest_simc_candidate_missing_ids",
                    "all_rank_simc_id_linked","physical_item_ids_linked",
                    "other_wago_enchant_ids_not_in_simc_source",
                    "additional_wago_id_classification_counts",
                    "additional_dps_gear_candidate_count",
                    "additional_dps_gear_highest_source_rank_candidate_count",
                    "additional_dps_gear_highest_source_rank_candidate_ids")},
                "quality_source_stage":{k:v for k,v in quality_stage.items()
                                        if k!="result"},
                "source_stage":{k:v for k,v in projection.items()
                                if k!="result"},
                "network_calls_by_stage":network_calls,"native_calls":0,
                "environment_ready":False,"automatic_ui_promotion":False}
    except (OSError, ValueError, TypeError, KeyError,
            stages.StageExecutionBlocked) as exc:
        return pending(str(exc).split(":",1)[0],calls[0])
