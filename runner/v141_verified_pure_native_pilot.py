#!/usr/bin/env python3
"""Reuse exact v140 or v145 physical receipts for a selected v096 stage.

NO new Native test, automatic spec promotion or effects/proc certification.
A v140 witness still applies only to two historical exact cases; a v145 witness
applies only to ONE staged profile with identical user, binary and JSON2 bytes.
The EXISTING v096/v094 adaptive runner alone does candidate DPS statistics.
"""
from __future__ import annotations
import hashlib
import json
import math
import pathlib

import v122_common_profile_format as profile_format
import v063_numeric_injection as numeric
import v143_specialization_contracts as contracts

SCHEMA="v140_pure_profile_physical_smoke_v1"
PILOT_SPECS=frozenset(("druid/balance","evoker/devastation"))
GEAR_PREFIXES=("gear_crit_rating=","gear_haste_rating=",
               "gear_mastery_rating=","gear_versatility_rating=")

class AcceptanceBlocked(ValueError): pass
def need(ok,code):
    if not ok:raise AcceptanceBlocked("V141_"+code)
def sha(raw):return hashlib.sha256(raw).hexdigest()

def verify_v145(profile,binary_sha256,revision,spec,physical_root):
    """Reuse ONE exact v145 physical result; NEVER authorize a whole spec.

    The caller passes the exact v145 per-user output folder, not a directory
    of possible witnesses. All proof stays local and hash-rechecked. No SimC
    call or extra runtime gate; same existing v096 -> v094 optimizer.
    """
    need(spec in contracts.CONTRACTS and spec not in PILOT_SPECS,
         "V145_SPEC_IS_NOT_A_STAGED_PREVIEW")
    folder=pathlib.Path(physical_root).resolve()
    paths={name:folder/name for name in
           ("user.json","receipt.json","physical.simc",
            "physical.json","stage/profile.simc")}
    need(all(p.is_file() for p in paths.values()),
         "V145_EXACT_PHYSICAL_RECEIPT_FILES_REQUIRED")
    receipt=json.loads(paths["receipt.json"].read_text(encoding="utf8"))
    need(type(receipt) is dict and
         receipt.get("schema")=="v145_one_spec_source_free_physical_diagnostic_v1" and
         receipt.get("spec")==spec and
         receipt.get("status")=="PASS_PHYSICAL_SIMC" and
         receipt.get("native_calls")==1 and
         receipt.get("physical_sample_only") is True and
         receipt.get("CHMV_optimization_completed") is False and
         receipt.get("user_optimizer_ready") is False,
         "V145_NATIVE_PHYSICAL_RECEIPT_NOT_PASS")
    ident=receipt.get("identity")
    need(type(ident) is dict and ident.get("spec")==spec and
         ident.get("simc_binary_sha256")==binary_sha256 and
         ident.get("simc_revision")==revision and
         ident.get("CHMV_numeric_overrides_removed") is True and
         type(ident.get("iterations")) is int and
         1<=ident["iterations"]<=35,
         "V145_EXACT_BINARY_REVISION_OR_OPTIONS_DRIFT")
    user_raw=paths["user.json"].read_bytes()
    user_sha=sha(user_raw)
    need(ident.get("user_sha256")==user_sha and
         folder.name==spec.replace("/","__")+"__"+user_sha[:16],
         "V145_USER_INPUT_IDENTITY_OR_FOLDER_DRIFT")
    user=json.loads(user_raw)
    character=user.get("character") if type(user) is dict else None
    need(type(character) is dict and
         type(character.get("class")) is str and
         type(character.get("spec")) is str and
         character["class"]+"/"+character["spec"]==spec and
         user.get("target")=={"ilevel":334,"final_T":None} and
         user.get("oil_hands")==[] and
         "import_simc_profile" not in user,
         "V145_USER_PHYSICAL_SCOPE_DRIFT")
    profile_raw=profile.encode("utf8")
    need(paths["stage/profile.simc"].read_bytes()==profile_raw and
         ident.get("profile_sha256")==sha(profile_raw),
         "V145_STAGED_PROFILE_BYTES_CHANGED")
    lines=profile.splitlines()
    need("default_actions=1" in lines and
         "json2="+profile_format.JSON2_PLACEHOLDER in lines and
         sum(l.startswith("json2=") for l in lines)==1 and
         sum(l.startswith("iterations=") for l in lines)==1 and
         all(sum(l.startswith(prefix) for l in lines)==1
             for prefix in GEAR_PREFIXES),
         "V145_PHYSICAL_PROFILE_NOT_SOURCE_INDEPENDENT")
    physical=[]
    for line in lines:
        if line.startswith(GEAR_PREFIXES):
            continue
        if line.startswith("json2="):
            physical.append("json2="+str(paths["physical.json"].resolve()))
        elif line.startswith("iterations="):
            physical.append("iterations="+str(ident["iterations"]))
        else:
            physical.append(line)
    physical_raw=("\n".join(physical)+"\n").encode("utf8")
    need(paths["physical.simc"].read_bytes()==physical_raw and
         sha(physical_raw)==ident.get("physical_sha256"),
         "V145_PHYSICAL_SIMC_BYTES_DRIFT")
    native_raw=paths["physical.json"].read_bytes()
    need(sha(native_raw)==receipt.get("json2_sha256"),
         "V145_JSON2_SHA256_DRIFT")
    native=json.loads(native_raw)
    need(native.get("report_version")=="2.0.0" and
         numeric.same_simc_commit_revision(native.get("git_revision"),revision),
         "V145_JSON2_REPORTED_SIMC_REVISION_OR_FORMAT_DRIFT")
    players=(native.get("sim") or {}).get("players") or []
    need(len(players)==1 and type(players[0]) is dict,
         "V145_NATIVE_SINGLE_PLAYER_REQUIRED")
    value=((players[0].get("collected_data") or {}).get("dps") or {}).get("mean")
    need(type(value) in (int,float) and math.isfinite(value) and value>0,
         "V145_NATIVE_DPS_NOT_POSITIVE")
    details=receipt.get("native_json2")
    need(type(details) is dict and
         details.get("observed_git_revision")==native.get("git_revision") and
         type(details.get("json2")) is dict and
         details["json2"].get("dps_mean")==value,
         "V145_RECEIPT_SUMMARY_NOT_JSON2")
    return {"schema":"v141_verified_reuse_of_v145_one_spec_physical_receipt_v1",
            "spec":spec,"binary_sha256":binary_sha256,
            "profile_sha256":sha(profile_raw),
            "physical_input_sha256":sha(physical_raw),
            "json2_sha256":sha(native_raw),"simc_revision":revision,
            "physical_native_already_executed":True,"new_native_calls":0,
            "source_free_4pc_effect_certified":False,
            "full_chmv_optimization_completed":False}

def verify(profile,binary_sha256,revision,spec,physical_root):
    """Check the prior local Native receipt against *this exact* staged profile.

    Receipts are local reproducibility evidence, not signed attestations;
    actual SimC DPS/stat checks still belong to the shared v096/v094 runner.
    """
    if spec not in PILOT_SPECS:
        return verify_v145(profile,binary_sha256,revision,spec,physical_root)
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
