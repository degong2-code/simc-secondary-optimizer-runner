#!/usr/bin/env python3
"""v158: create a fresh seasonal acquisition-ID index from API reports alone.

All item IDs must originate from new Blizzard item/loot/recipe fields.
Prior WEQUIP/v047/v057 data, seeded item ID lists, and old SimC profiles
are neither read nor required. This is acquisition metadata, not gear stats.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

SCHEMA="v158_source_first_season_acquisition_index_v1"
ACCEPTED={
    "v154_source_first_blizzard_encounter_loot_v2",
    "v156_one_blizzard_journal_raid_loot_smoke_v1",
    "v157_source_first_blizzard_profession_recipes_v2",
    "v155_season_discovery_provider_probe_v1",
}
MAX_INPUTS=100
MAX_ITEM_IDS=30000


class CatalogBlocked(ValueError):
    pass


def need(value,code):
    if not value:
        raise CatalogBlocked(code)


def valid_id(value):
    need(type(value) is int and value>0,"ITEM_ID_INVALID")
    return value


def ingest(reports):
    """Rebuild deterministically from provider snapshots; no inherited state."""
    need(type(reports) is list and 1<=len(reports)<=MAX_INPUTS,
         "INPUT_REPORT_COUNT")
    seen,items,collections,metadata={}, {}, [], {}
    unknown=[]
    def store(item_id, provenance):
        valid_id(item_id)
        data=items.setdefault(item_id,{"item_id":item_id,"acquisition_sources":[]})
        if provenance not in data["acquisition_sources"]:
            data["acquisition_sources"].append(provenance)
        need(len(items)<=MAX_ITEM_IDS,"CATALOG_ITEM_LIMIT")
    for report in reports:
        need(type(report) is dict,"REPORT_NOT_OBJECT")
        schema=report.get("schema")
        need(schema in ACCEPTED,"UNAPPROVED_PROVIDER_REPORT_SCHEMA")
        if schema=="v155_season_discovery_provider_probe_v1":
            section=(report.get("blizzard") or {}).get("endpoints") or {}
            metadata["blizzard_keystone_season_id"]=(
                (section.get("keystone_season_index") or {})
                .get("data",{}).get("current_season_id"))
            metadata["blizzard_keystone_season_id_status"]=(
                "OBSERVED" if type(metadata["blizzard_keystone_season_id"]) is int
                else "NOT_EXPOSED")
            collections.append({"type":"season_metadata",
                 "data_origin":"BLIZZARD_WCL_API_PROBE",
                 "acquisition_item_ids_observed":0})
        elif schema=="v154_source_first_blizzard_encounter_loot_v2":
            authority=report.get("source_authority")
            need(authority in ("BLIZZARD_API_RESPONSE","UNVERIFIED_SAVED_INPUT"),
                 "LOOT_SOURCE_AUTHORITY_INVALID")
            sources=report.get("encounter_sources")
            need(type(sources) is list and len(sources)<=48,
                 "ENCOUNTER_SOURCES_INVALID")
            for e in sources:
                need(type(e) is dict,"ENCOUNTER_SOURCE_INVALID")
                eid=valid_id(e.get("encounter_id"))
                kind=e.get("kind")
                need(kind in ("raid","mplus","delve"),"ENCOUNTER_KIND_INVALID")
                ids=e.get("observed_item_ids")
                if ids is None:
                    unknown.append({"type":"encounter_loot_unknown",
                                    "encounter_id":eid,"kind":kind})
                    continue
                need(type(ids) is list and len(ids)<=400,"ENCOUNTER_ITEMS_INVALID")
                for item_id in ids:
                    store(item_id,{"source":"blizzard_journal_encounter",
                                   "authority":authority,"kind":kind,
                                   "encounter_id":eid,
                                   "instance_id":valid_id(e.get("instance_id"))})
            collections.append({"type":"encounter_loot",
                 "source_authority":authority,
                 "encounters_queried":len(sources),
                 "encounters_with_explicit_loot":sum(
                     e.get("observed_item_ids") is not None for e in sources)})
        elif schema=="v156_one_blizzard_journal_raid_loot_smoke_v1":
            if report.get("status")!="BOUNDED_JOURNAL_SMOKE_COMPLETE":
                unknown.append({"type":"single_boss_query_incomplete",
                                "status":report.get("status")})
                continue
            boss=report.get("boss")
            raid=report.get("raid")
            need(type(boss) is dict and type(raid) is dict,
                 "JOURNAL_SOURCE_MISSING")
            eid=valid_id(boss.get("journal_encounter_id"))
            iid=valid_id(raid.get("journal_instance_id"))
            loot=report.get("loot")
            need(type(loot) is dict,"BOSS_LOOT_MISSING")
            ids=loot.get("observed_item_ids")
            if ids is None:
                unknown.append({"type":"single_boss_loot_unknown",
                                "encounter_id":eid})
            else:
                need(type(ids) is list and len(ids)<=400,"BOSS_LOOT_ITEMS_INVALID")
                for item_id in ids:
                    store(item_id,{"source":"blizzard_journal_encounter",
                                   "authority":"BLIZZARD_API_RESPONSE",
                                   "kind":"raid",
                                   "encounter_id":eid,"instance_id":iid})
            collections.append({"type":"single_raid_boss",
                "journal_encounter_id":eid,"loot_field_exposed":ids is not None})
        elif schema=="v157_source_first_blizzard_profession_recipes_v2":
            profession=report.get("profession_id")
            tier=report.get("skill_tier_id")
            refs=report.get("discovered_recipe_references")
            details=report.get("sampled_recipe_details")
            need(type(refs) is list and type(details) is list
                 and len(refs)<=4000 and len(details)<=6,
                 "RECIPE_REPORT_INVALID")
            catalog_ids=set()
            for ref in refs:
                need(type(ref) is dict,"RECIPE_REF_INVALID")
                rid=valid_id(ref.get("id"))
                need(rid not in catalog_ids,"DUPLICATE_RECIPE_REF")
                catalog_ids.add(rid)
            for detail in details:
                need(type(detail) is dict,"RECIPE_DETAIL_INVALID")
                rid=valid_id(detail.get("recipe_id"))
                need(rid in catalog_ids,"RECIPE_DETAIL_NOT_IN_DISCOVERY")
                output=detail.get("crafted_output_item_ids")
                if output is None:
                    unknown.append({"type":"recipe_output_unknown",
                                    "recipe_id":rid})
                    continue
                need(type(output) is list and len(output)<=30,
                     "RECIPE_OUTPUT_LIST_INVALID")
                need(type(profession) is int and profession>0 and
                     type(tier) is int and tier>0,"PROFESSION_TIER_MISSING")
                for item_id in output:
                    store(item_id,{"source":"blizzard_recipe_explicit_output",
                                   "authority":"BLIZZARD_API_RESPONSE",
                                   "profession_id":profession,
                                   "skill_tier_id":tier,"recipe_id":rid})
            collections.append({"type":"profession_recipes",
                "profession_id":profession,"skill_tier_id":tier,
                "recipe_refs_observed":len(refs),
                "recipe_details_queried":len(details),
                "recipe_details_with_explicit_outputs":sum(
                    x.get("crafted_output_item_ids") is not None for x in details)})
    for item in items.values():
        item["acquisition_sources"].sort(
            key=lambda source:json.dumps(source,sort_keys=True))
    return {
        "schema":SCHEMA,
        "status":"PARTIAL_COLLECTION_WITH_UNKNOWN_GAPS",
        "season_data":metadata,
        "observed_unique_item_ids":len(items),
        "item_ids":sorted(items),
        "items":[items[i] for i in sorted(items)],
        "collection_receipts":collections,
        "unresolved_provider_fields":unknown,
        "full_season_completeness_confirmed":False,
        "old_item_catalog_imported":False,
        "legacy_comparison_performed":False,
        "simc_native_calls":0,
        "static_L_generated":False,
        "special_effects_classified":False}


def main(argv=None):
    p=argparse.ArgumentParser(description="Build fresh ID index from provider reports only")
    p.add_argument("--report",type=Path,action="append",required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args(argv)
    try:
        need(len(args.report)<=MAX_INPUTS,"INPUT_REPORT_COUNT")
        payload=[]
        for path in args.report:
            need(path.is_file() and path.stat().st_size<=5_000_000,
                 "REPORT_FILE_MISSING_OR_TOO_LARGE")
            payload.append(json.loads(path.read_text(encoding="utf8")))
        catalog=ingest(payload)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(catalog,sort_keys=True,
                    ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        print(json.dumps({"status":catalog["status"],
              "item_ids":catalog["observed_unique_item_ids"],
              "unresolved":len(catalog["unresolved_provider_fields"]),
              "native":0},sort_keys=True))
        return 0
    except Exception as exc:
        code=str(exc) if isinstance(exc,CatalogBlocked) else type(exc).__name__
        print(json.dumps({"status":"BLOCKED","code":code}),file=sys.stderr)
        return 3


if __name__=="__main__":
    raise SystemExit(main())
