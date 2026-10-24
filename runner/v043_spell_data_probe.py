#!/usr/bin/env python3
"""v043: bounded pinned-SimC spell DBC query of Venomcursed effect records.

No combat run, no item/bonus attestation, no final applied stat delta.
The resulting text is a captured DBC view at requested query level, NOT a
validated in-combat stat effect or real-game scaling proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

SCHEMA = "v043_venomcursed_spell_query_v1"
BINARY_SHA256 = "64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"
QUERIES = (("buff_1307922", 1307922), ("driver_1307923", 1307923))
MAX_QUERY_CALLS = 2

class Refused(ValueError):
    pass

def require(value, code):
    if not value:
        raise Refused(code)

def sha(buf):
    return hashlib.sha256(buf).hexdigest()

def validate_output(raw, spell_id):
    require(type(raw) is bytes and len(raw) > 30 and len(raw) <= 250_000,
            "DBC_QUERY_OUTPUT_SIZE")
    s = raw.decode("utf-8", "replace")
    require(re.search(r"\b" + str(spell_id) + r"\b", s) is not None,
            "DBC_SPELL_ID_NOT_FOUND")
    require(not re.search(r"(?im)^\s*(error|invalid spell query|unknown option)\s*[:!]", s),
            "DBC_QUERY_ERROR")
    return {"spell_id": spell_id, "text_bytes": len(raw), "output_sha256": sha(raw),
            "spell_identifier_visible": True,
            "query_level_is_not_item_effect_attestation": True,
            "applied_positive_rating": None,
            "applied_negative_rating": None,
            "actual_334_item_proc_scaling_proven": False}

def run(binary, output):
    output.mkdir(parents=True, exist_ok=True)
    receipt = {"schema": SCHEMA, "status": "BLOCKED", "test_success": False,
        "product_code_integrated": False, "official_policy_promoted": False,
        "native_combat_runs": 0, "spell_query_calls": 0,
        "spell_query_calls_max": MAX_QUERY_CALLS, "queries": [],
        "item_catalyst_bonus_334_attested": False,
        "effect_dynamic_rating_delta_applied_proven": False,
        "actual_G_T_budget_proven": False,
        "v016_product_baseline_integrated": False,
        "dps_comparison_authorized": False,
        "product_admission": "BLOCKED_MISSING_INDEPENDENT_EVIDENCE"}
    try:
        require(binary.is_file() and sha(binary.read_bytes()) == BINARY_SHA256,
                "PINNED_BINARY_SHA_INVALID")
        for label, spell_id in QUERIES:
            require(receipt["spell_query_calls"] < MAX_QUERY_CALLS,
                    "SPELL_QUERY_LIMIT_EXCEEDED")
            arg = "spell_query=spell.id=" + str(spell_id) + "@334"
            receipt["spell_query_calls"] += 1
            proc = subprocess.run([str(binary), arg], cwd=binary.parent,
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, timeout=30)
            (output / (label + ".txt")).write_bytes(proc.stdout)
            (output / (label + ".stderr.txt")).write_bytes(proc.stderr)
            entry = {"label": label, "query": arg, "returncode": proc.returncode,
                     "stdout_sha256": sha(proc.stdout),
                     "stderr_sha256": sha(proc.stderr)}
            receipt["queries"].append(entry)
            require(proc.returncode == 0, "SPELL_QUERY_EXIT_FAILURE")
            entry["dbc_capture"] = validate_output(proc.stdout, spell_id)
        receipt["test_success"] = True
        receipt["status"] = "PASS_TWO_PINNED_DBC_QUERIES_NO_APPLIED_STAT_CLAIM"
    except Exception as err:
        receipt["error_code"] = type(err).__name__ + ":" + str(err)
    (output / "V043_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("V043_STATUS", receipt["status"], "DBC_calls", receipt["spell_query_calls"], flush=True)
    return 0 if receipt["test_success"] else 3

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--binary", required=True, type=pathlib.Path)
    p.add_argument("--output", required=True, type=pathlib.Path)
    a = p.parse_args()
    sys.exit(run(a.binary.resolve(), a.output.resolve()))
