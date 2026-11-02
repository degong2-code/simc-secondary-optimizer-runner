#!/usr/bin/env python3
"""Offline only: check exact installed v213 artifact against existing season inputs.

Reuses a previously published artifact; no network fetch within this script,
Native, user option publication or new-season budget approval. This probes
source identity with a minimal oil-serialization fixture, not a SimC-run profile.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
import v222_season_budget_contract as budget_contract
import v223_installed_season_budget_source as source_proof

CATALOG = ROOT / "data/current_season_source_to_catalog.json"
FILES = {
    "gear": ROOT / "data/current_season_product_gear_db.json",
    "tier": ROOT / "data/current_season_tier_itemsets.json",
    "budget": ROOT / "data/current_season_chmv_consumables.json",
    "reference": ROOT / "integration_probes/data/midnight_s2_ilvl_chmv_reference_v1.json",
}


def main():
    raw = CATALOG.read_bytes()
    catalog = json.loads(raw.decode("utf8"))
    artifact_sha = hashlib.sha256(raw).hexdigest()
    O = {"crit_rating": 16, "haste_rating": 16,
         "mastery_rating": 0, "versatility_rating": 0}
    plan = {"base_B": 3150, "final_T": 3182, "fixed_O": O}
    user = {
        "character": {"class": "paladin", "spec": "retribution"},
        "target": {"ilevel": 334, "final_T": None},
        "oil_hands": ["main_hand"],
        "special_items": [], "embellishments": [],
    }
    profile = (
        "main_hand=source_fixture,id=158373,ilevel=334\n"
        "temporary_enchant=main_hand:thalassian_phoenix_oil_2\n")
    proof = source_proof.produce(
        catalog=catalog, catalog_sha=artifact_sha,
        source_paths=FILES, user=user,
        bootstrap={"target_ilevel": 334, "weapon_form": "single_two_hand",
                   "plan": plan},
        physical_profile=profile)
    result = budget_contract.reconcile(
        source_catalog=catalog, source_artifact_sha256=artifact_sha,
        evidence=proof["evidence"], plan=plan, target_ilevel=334)
    assert result["base_B"] == 3150 and result["final_T"] == 3182
    assert proof["reference_rounded"] is True
    assert proof["native_calls"] == result["native_calls"] == 0
    assert proof["status"].endswith("NOT_REFRESHED")
    print("V223_REAL_V213_SOURCE_LINK_PASS_NO_NATIVE",
          catalog["game_build"], catalog["manifest_sha256"],
          proof["source_input_sha256"], "G_APPROX", result["reference_G"],
          "B", result["base_B"], "T", result["final_T"])
    print("V223_SYNTHETIC_OIL_SERIALIZATION_FIXTURE_NOT_NATIVE_ACCEPTANCE")


if __name__ == "__main__":
    main()
