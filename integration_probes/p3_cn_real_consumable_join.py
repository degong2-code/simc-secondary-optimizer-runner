#!/usr/bin/env python3
"""P3-CN: one-shot REAL pinned Wago/SimC source integration observation.

Exercise ORIGINAL v161/v189/v190/v229/v230/v280/v281 code on matching
Retail build 12.1.5.70575, source-only. A source diagnostic, NOT a parallel
environment builder, a season/weapon-quality certification or a Native test.
The installed product path remains v216→v274→v191/v211/v213→v212.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import tempfile
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from runner import v161_wago_db2_snapshot as wago
from runner import v189_simc_consumable_embellishment_discovery as handlers
from runner import v190_consumable_item_snapshot_join as physical
from runner import v191_unified_season_data_update as compiler
from runner import v229_simc_only_source_seed as seed
from runner import v230_simc_item_metadata as item_meta
from runner import v280_consumable_item_use_spell_source as use_spell
from runner import v281_consumable_simc_relation as simc_join

BUILD = "12.1.5.70575"
REVISION = "710c2408bfd3ae4df71b8cd55cdf01f63fd6c926"
EXPANSION_ID = 11
MAX_BYTES = {
    "ItemXItemEffect": 32_000_000,
    "ItemEffect": 32_000_000,
    "SpellEffect": 150_000_000,
}
PROOF = "p3_cn_real_same_build_consumable_source_only_v1"

def fetch_table(root, name):
    uri = "https://wago.tools/db2/" + name + "/csv?" + urlencode(
        {"build": BUILD, "locale": "enUS"})
    request = Request(uri, headers={
        "User-Agent": "SIMC-Secondary-P3-CN-Evidence/1.0", "Accept": "text/csv"})
    h = hashlib.sha256()
    used = 0
    file = root / (name + ".csv")
    with urlopen(request, timeout=90) as response, file.open("wb") as output:
        if response.status != 200:
            raise ValueError("P3_CN_"+name+"_HTTP_NON200")
        while True:
            part = response.read(262144)
            if not part:
                break
            used += len(part)
            if used > MAX_BYTES[name]:
                raise ValueError("P3_CN_"+name+"_SIZE_CAP_EXCEEDED")
            h.update(part)
            output.write(part)
    if not used:
        raise ValueError("P3_CN_"+name+"_EMPTY")
    print("P3_CN_REAL_WAGO", name, "bytes", used,
          "sha256", h.hexdigest(), flush=True)
    return file, {"bytes": used, "sha256": h.hexdigest()}

def run():
    with tempfile.TemporaryDirectory(prefix="p3-cn-real-sources-") as temp:
        root = pathlib.Path(temp)
        folder = root / "wago"
        # The original v161 downloader is reused with a LOCAL two-table
        # test-only selection; never rewrite v161.TABLES in repository.
        original_tables = wago.TABLES
        try:
            wago.TABLES = ("Item", "ItemSparse")
            snapshot = wago.snapshot(folder, build=BUILD, make_archive=False)
        finally:
            wago.TABLES = original_tables
        assert set(snapshot["tables"]) == {"Item", "ItemSparse"}
        print("P3_CN_REAL_WAGO_REUSED_V161",json.dumps({
            n:{"bytes":v["bytes"],"sha256":v["sha256"]}
            for n,v in snapshot["tables"].items()},sort_keys=True),flush=True)

        # Existing registration extractor + real v190 physical ID source.
        registration_raw = handlers.read_source(commit=REVISION)
        registration = handlers.discover(registration_raw,REVISION)
        physical_candidates = physical.build(
            registration, folder, expected_build=BUILD,
            expansion_id=EXPANSION_ID)
        print("P3_CN_PHYSICAL_IDS",json.dumps(
            physical_candidates["counts"],sort_keys=True),flush=True)

        # Existing v229 authenticated pinned SimC source, not old budget.
        simc_folder = root / "pinned_simc"
        pinned = seed.collect(
            revision=REVISION, expected_build=BUILD,
            previous_game_build=None,season_event="cold_start",
            include_item_data=True,dest=simc_folder)
        assert pinned["provenance_tree_blob_authenticated"] is True
        assert pinned["item_data_present"] is True
        temps = compiler.parse_generated(
            "temporary_enchant",(simc_folder/"temporary_enchant.inc").read_bytes())
        all_items = item_meta.parse_exact(
            (simc_folder/"item_data.inc").read_bytes(),
            build=BUILD,candidate_filter=lambda f:
                f[11] == "0" and f[12] == "3",candidate_limit=5000)
        print("P3_CN_REAL_SIMC",REVISION,
              "verified_item_source",pinned["receipt_sha256"],
              "flask_dbc_candidates",len(all_items["items"]),
              "temp_enchant_rows",len(temps["rows"]),flush=True)

        relation_file,relation_id=fetch_table(root,"ItemXItemEffect")
        effect_file,effect_id=fetch_table(root,"ItemEffect")
        observed_use=use_spell.join(
            physical_candidates,relation_file.read_bytes(),
            effect_file.read_bytes(),build=BUILD,
            relation_sha256=relation_id["sha256"],
            effect_sha256=effect_id["sha256"])
        info=observed_use["item_use_spell_join"]
        print("P3_CN_REAL_USE_RELATION",json.dumps({
            k:info[k] for k in ("candidate_count",
                "exact_on_use_source_count","pending_count")},sort_keys=True),flush=True)

        spell_file,spell_id=fetch_table(root,"SpellEffect")
        wanted={sid for item in observed_use["items"]
            if item.get("kind") in ("flask","item_enhancement")
            for sid in item.get("item_effect_source",{}).get(
                "on_use_spell_ids",[])}
        observed_spells=simc_join.scan_spell_effects(spell_file,wanted)
        result=simc_join.correlate(
            observed_use, observed_spells,temps["rows"],
            build=BUILD,flask_dbc_rows=all_items["items"])
        matched={
            "flasks":[{"item_id":x["item_id"],
                "simc":x["simc_flask_item_source"]}
                for x in result["items"]
                if x.get("simc_flask_item_source",{}).get(
                  "simc_flask_option_candidate") is not None],
            "temporary":[{"item_id":x["item_id"],
                "simc":x["simc_temporary_enchant_source"]}
                for x in result["items"]
                if x.get("simc_temporary_enchant_source",{}).get(
                  "status")=="EXACT_SIMC_TEMP_ENCHANT_ID_CANDIDATE"],
        }
        evidence={
            "schema":PROOF,"build":BUILD,"pinned_simc_revision":REVISION,
            "source_only":True,"source_retrieval":"REAL_PINNED_HTTP",
            "source_manifest_sha256":pinned["receipt_sha256"],
            "wago":{
                **{name:{"bytes":row["bytes"],"sha256":row["sha256"]}
                   for name,row in snapshot["tables"].items()},
                "ItemXItemEffect":relation_id,
                "ItemEffect":effect_id,
                "SpellEffect":spell_id},
            "physical_counts":physical_candidates["counts"],
            "on_use_counts":{k:info[k] for k in (
                "candidate_count","exact_on_use_source_count","pending_count")},
            "simc_relation_counts":result["simc_relation_source"],
            "matched_candidate_counts":{
                "flask":len(matched["flasks"]),
                "temporary":len(matched["temporary"])},
            "bounded_examples":{
                "flask":matched["flasks"][:8],
                "temporary":matched["temporary"][:8]},
            "native_calls":0,"G":None,"J":None,
            "F":None,"O":None,"B":None,"T":None,
            "environment_ready":False,
            "game_weapon_eligibility_verified":False,
            "highest_quality_verified":False,
            "user_selection_enabled":False,
        }
        return evidence

if __name__=="__main__":
    result=run()
    pathlib.Path("p3_cn_receipt.json").write_text(
        json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)
        +"\n",encoding="utf8")
    print("P3_CN_REAL_JOIN_COUNTS",json.dumps({
        "physical":result["physical_counts"],
        "on_use":result["on_use_counts"],
        "simc":result["matched_candidate_counts"]},sort_keys=True),flush=True)
    for kind,examples in result["bounded_examples"].items():
        for row in examples:
            print("P3_CN_SOURCE_EXAMPLE",kind,json.dumps(
                row,sort_keys=True,ensure_ascii=False),flush=True)
    print("P3_CN_NO_USER_SELECTION_NO_NATIVE_NO_READY",flush=True)
