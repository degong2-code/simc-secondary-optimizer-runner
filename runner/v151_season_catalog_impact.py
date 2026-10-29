#!/usr/bin/env python3
"""Reusable P1 season-data change planner. NO network, SimC or file writes.

Reuse the one v139 season catalog validator and stable v143 spec contracts.
Compare the INPUT DATA, not an entire previous executable/proprietary profile.
This computes *scope*, not fresh evidence or automatic permission to run Native.
Other external change streams (SimC binary, APL, budget reference table, static
item records, selected trinkets) require their own identities and are NOT
implicitly certified by a comparison of v144 catalog files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

import v139_pure_target_profile_composer as composer

SCHEMA="v151_season_catalog_change_impact_v1"
# These are annotations / provenance, NOT the actual gear or numeric budget.
ANNOTATIONS=frozenset(("schema","status","provenance","provenance_note"))
GLOBAL_PHYSICAL=frozenset(("season","target_ilevel","character_level",
                           "common_gear","gems","simc_item_db_source"))
GLOBAL_DPS=frozenset(("default_consumables",))
PER_SPEC_PHYSICAL=frozenset(("tier_ids","four_tier_slots","ordinary",
                             "weapons","item_options"))
BUDGET_FIELDS=frozenset(("gem_budget_J","flask_budget_F","flask_fixed_stat"))
EXPECTED=frozenset(GLOBAL_PHYSICAL|GLOBAL_DPS|ANNOTATIONS|
                   {"specializations"})

def canonical(doc):
    return json.dumps(doc,ensure_ascii=False,sort_keys=True,
                      separators=(",",":"),allow_nan=False)

def sha(doc):
    return hashlib.sha256(canonical(doc).encode("utf8")).hexdigest()

def compare(before,after):
    """Pure data→bounded impact advisory, with explicit unknown-key escalation.

    No per-spec physical SimC execution is prescribed for DPS-only changes.
    No changed catalog is accepted for product runtime merely by calling here.
    """
    before=composer.validate_season(before)
    after=composer.validate_season(after)
    old=set(before["specializations"])
    new=set(after["specializations"])
    all_specs=old|new
    added=new-old
    removed=old-new
    physical=set(added|removed)
    dps=set(added|removed)
    physical_reasons={key:set(["SPEC_ADDED_OR_REMOVED"])
                      for key in (added|removed)}
    dps_reasons={key:set(["SPEC_ADDED_OR_REMOVED"])
                 for key in (added|removed)}
    changed_globals=sorted(k for k in set(before)|set(after)
                           if before.get(k)!=after.get(k)
                           and k!="specializations")
    unknown=[k for k in changed_globals if k not in EXPECTED]
    for k in changed_globals:
        if k in GLOBAL_PHYSICAL or k in unknown:
            physical.update(all_specs);dps.update(all_specs)
            for spec in all_specs:
                physical_reasons.setdefault(spec,set()).add(
                    k if k not in unknown else "UNCLASSIFIED_"+k)
                dps_reasons.setdefault(spec,set()).add(
                    k if k not in unknown else "UNCLASSIFIED_"+k)
        elif k in GLOBAL_DPS:
            dps.update(all_specs)
            for spec in all_specs:
                dps_reasons.setdefault(spec,set()).add(k)
    changed_by_spec={}
    for spec in sorted(old&new):
        a=before["specializations"][spec]
        z=after["specializations"][spec]
        keys=set(a)|set(z)
        changed=sorted(k for k in keys if a.get(k)!=z.get(k))
        if not changed:continue
        changed_by_spec[spec]=changed
        physical.add(spec);dps.add(spec)
        physical_reasons.setdefault(spec,set()).update(changed)
        dps_reasons.setdefault(spec,set()).update(changed)
    # Unknown modifications are NOT silently treated as harmless metadata.
    unclassified_specs=sorted(spec for spec,keys in
        changed_by_spec.items() if any(k not in PER_SPEC_PHYSICAL for k in keys))
    if unclassified_specs:
        unknown.extend("spec:"+s for s in unclassified_specs)
    consume_before=before["default_consumables"]
    consume_after=after["default_consumables"]
    budget_changed=sorted(k for k in BUDGET_FIELDS
                          if consume_before.get(k)!=consume_after.get(k))
    actual_change=(bool(physical) or bool(dps) or bool(unknown))
    metadata_only=(not actual_change and sha(before)!=sha(after))
    return {
        "schema":SCHEMA,
        "before_sha256":sha(before),"after_sha256":sha(after),
        "before_season":before["season"],"after_season":after["season"],
        "before_target_ilevel":before["target_ilevel"],
        "after_target_ilevel":after["target_ilevel"],
        "added_specs":sorted(added),"removed_specs":sorted(removed),
        "changed_global_fields":changed_globals,
        "changed_specialization_fields":changed_by_spec,
        "needs_physical_acceptance_review":sorted(physical),
        "needs_adaptive_dps_review":sorted(dps),
        "physical_reasons":{s:sorted(physical_reasons[s]) for s in sorted(physical)},
        "dps_reasons":{s:sorted(dps_reasons[s]) for s in sorted(dps)},
        "budget_policy_review_required":bool(
            budget_changed or {"season","target_ilevel"}&
            set(changed_globals)),
        "changed_consumable_budget_fields":budget_changed,
        "unclassified_changes_require_human_review":sorted(set(unknown)),
        "metadata_only_change":metadata_only,
        "actual_profile_or_dps_inputs_changed":actual_change,
        "same_season_static_records_always_invalidated":False,
        "may_reuse_unchanged_static_cache_records":True,
        "dps_cache_reuse_of_affected_scenarios_without_identity_recheck":False,
        "native_calls_performed":0,
        "native_calls_auto_authorized":0,
        "product_support_for_new_level_or_season_granted":False,
        "scope":"CATALOG_SELECTION_ONLY_NOT_SIMC_BINARY_APL_OR_REFERENCE_B",
        "simc_is_authority_for_item_stats_and_effects":True,
        "item_roster_selection_requires_grounded_ids":True,
        "bundled_simc_item_source_policy":
            after.get("simc_item_db_source","SIMC_DEFAULT_COMPATIBILITY"),
        "automatic_item_roster_discovery_implemented":False,
        "next_action":(
            "REVIEW_UNCLASSIFIED_FIELDS_BEFORE_RELEASE" if unknown else
            "REVIEW_CHANGED_SPEC_CATALOG_AND_RUN_SCOPED_NATIVE_ONLY_IF_NEEDED"
            if actual_change else
            "NO_NATIVE_FOR_METADATA_OR_IDENTICAL_CATALOG")
    }

def main(argv=None):
    p=argparse.ArgumentParser(
        description="Diff two existing validated season catalogs; read-only/Native 0")
    p.add_argument("--before",type=pathlib.Path,required=True)
    p.add_argument("--after",type=pathlib.Path,required=True)
    a=p.parse_args(argv)
    try:
        old=json.loads(a.before.read_text(encoding="utf8"))
        new=json.loads(a.after.read_text(encoding="utf8"))
        result=compare(old,new)
        print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
        return 0 if not result["unclassified_changes_require_human_review"] else 4
    except (ValueError,TypeError,KeyError,OSError) as e:
        print("V151_DATA_BLOCKED:",type(e).__name__,str(e),file=sys.stderr)
        return 3

if __name__=="__main__":
    sys.exit(main())
