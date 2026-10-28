#!/usr/bin/env python3
"""Reuse existing v140 physical receipts for an explicitly selected v096 pilot.

NO new Native test or effect/proc certification. An exact v140 source-free
profile, unchanged user gear/inputs, identical SimC binary/revision, and its
previous actual JSON2 are required before activating the EXISTING adaptive
runner. No unverified or default user session can use the witness.
"""
from __future__ import annotations
import hashlib
import json
import pathlib

import v122_common_profile_format as profile_format
import v063_numeric_injection as numeric

SCHEMA="v140_pure_profile_physical_smoke_v1"
PILOT_SPECS=frozenset(("druid/balance","evoker/devastation"))
GEAR_PREFIXES=("gear_crit_rating=","gear_haste_rating=",
               "gear_mastery_rating=","gear_versatility_rating=")

class AcceptanceBlocked(ValueError): pass
def need(ok,code):
    if not ok:raise AcceptanceBlocked("V141_"+code)
def sha(raw):return hashlib.sha256(raw).hexdigest()

def verify(profile,binary_sha256,revision,spec,physical_root):
    """Check the prior local Native receipt against *this exact* staged profile.

    Receipts are local reproducibility evidence, not signed attestations;
    actual SimC DPS/stat checks still belong to the shared v096/v094 runner.
    """
    need(spec in PILOT_SPECS,"ONLY_TWO_PHYSICALLY_WITNESSED_SPECS")
    need(type(profile) is str and type(revision) is str
         and len(revision)>=7,"REPLAY_PROFILE_OR_REVISION")
    base=pathlib.Path(physical_root).resolve()/spec.replace("/","__")
    paths={n:base/n for n in ("receipt.json","physical.simc",
                               "physical.json","stage/profile.simc")}
    need(all(p.is_file() for p in paths.values()),
         "VERIFIED_PHYSICAL_RECEIPT_FILES_REQUIRED")
    witness=json.loads(paths["receipt.json"].read_text(encoding="utf8"))
    need(type(witness) is dict and witness.get("schema")==SCHEMA
         and witness.get("status")=="PASS_PHYSICAL_SIMC"
         and witness.get("new_native_calls")==1
         and witness.get("spec")==spec
         and witness.get("physical_profile_only") is True
         and witness.get("chmv_optimization_completed") is False,
         "NATIVE_PHYSICAL_ACCEPTANCE_REQUIRED")
    identity=witness.get("identity")
    need(type(identity) is dict
         and identity.get("scenario_spec")==spec
         and identity.get("source_free_composer") is True
         and identity.get("gear_rating_override_removed") is True
         and type(identity.get("iterations")) is int
         and 1<=identity["iterations"]<=35
         and identity.get("simc_revision")==revision,
         "RECEIPT_IDENTITY_OR_REVISION_DRIFT")
    # v096 already checked the real binary and calculated its SHA once.
    need(type(binary_sha256) is str and
         binary_sha256==identity.get("binary_sha256"),
         "PHYSICAL_BINARY_SHA256_CHANGED")
    # Compare all user inputs and physical rows to the original v140 plan,
    # not just the specialization. Different trinkets/gems/talents/oil or
    # a newly chosen season variant cannot borrow an old acceptance.
    need(paths["stage/profile.simc"].read_bytes()==profile.encode("utf8"),
         "STAGED_PROFILE_BYTES_CHANGED_SINCE_PHYSICAL_NATIVE")
    lines=profile.splitlines()
    need("default_actions=1" in lines
         and "json2="+profile_format.JSON2_PLACEHOLDER in lines
         and sum(x.startswith("json2=") for x in lines)==1
         and sum(x.startswith("iterations=") for x in lines)==1
         and all(sum(x.startswith(p) for x in lines)==1
                 for p in GEAR_PREFIXES),
         "PURE_PROFILE_NATIVE_INPUT_CONTRACT")
    physical=[]
    for line in lines:
        if line.startswith(GEAR_PREFIXES):
            continue
        if line.startswith("json2="):
            physical.append("json2="+str(paths["physical.json"].resolve()))
        elif line.startswith("iterations="):
            physical.append("iterations="+str(identity["iterations"]))
        else:
            physical.append(line)
    expected=("\n".join(physical)+"\n").encode("utf8")
    need(paths["physical.simc"].read_bytes()==expected
         and sha(expected)==identity.get("input_sha256"),
         "PHYSICAL_INPUT_OR_RECEIPT_SHA256_DRIFT")
    raw=paths["physical.json"].read_bytes()
    need(sha(raw)==witness.get("json2_sha256"),
         "PHYSICAL_NATIVE_JSON2_SHA256_DRIFT")
    native=json.loads(raw)
    # v140's old receipt recorded the caller-declared revision, but did
    # not compare it with the actual SimC git_revision. Read the already
    # hashed original JSON2 now, before ANY adaptive candidate runs.
    need(numeric.same_simc_commit_revision(native.get("git_revision"),revision),
         "V140_JSON2_REPORTED_SIMC_REVISION_DRIFT:reported="+
         str(native.get("git_revision"))+";declared="+str(revision))
    players=(native.get("sim") or {}).get("players") or []
    need(len(players)==1 and type(players[0]) is dict,
         "PHYSICAL_JSON2_SINGLE_PLAYER_REQUIRED")
    return {"schema":"v141_verified_reuse_of_v140_physical_receipt_v1",
            "spec":spec,"binary_sha256":identity["binary_sha256"],
            "profile_sha256":sha(profile.encode("utf8")),
            "physical_input_sha256":sha(expected),
            "json2_sha256":witness["json2_sha256"],
            "simc_revision":revision,"physical_native_already_executed":True,
            "new_native_calls":0,"source_free_4pc_effect_certified":False,
            "full_chmv_optimization_completed":False}
