#!/usr/bin/env python3
"""v225: artifact-only intake of future-season G/J/F/O core source bundles.

One SOURCE ENTRY per gear, tier and consumable candidate file. Each entry
has a declared primary origin and exact snapshot identity; this module
authenticates bytes and consistency, NOT the correctness of the remote
publisher's claims, quantitative stat values or quality equivalence.
Never downloads arbitrary URLs, rewrites installed season data, calls Native,
publishes UI choices, or promotes a ready budget.

GitHub Actions downloads the explicitly requested same-run artifact into a
private work directory; this code validates *fixed named* contents only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re
from urllib.parse import urlsplit, parse_qs

try:
    from . import v224_season_gjfo_evidence_inventory as preflight
except ImportError:  # script entrypoint from runner/
    import v224_season_gjfo_evidence_inventory as preflight

SCHEMA = "v225_season_core_source_bundle_v2"
SOURCE_FILES = {
    "gear": "gear.json",
    "tier": "tier.json",
    "budget": "budget.json",
}
COMPONENT_INPUTS = {
    "G": ("gear", "tier"),
    "J": ("budget",),
    "F": ("budget",),
    "O": ("budget",),
}
SOURCE_SYSTEMS = frozenset((
    "blizzard_game_data_api",
    "wago_db2_build_snapshot",
    "simulationcraft_revision_source",
    "verified_public_item_source",
))
EVENTS = ("season_change", "expansion_change", "mid_patch")
REV = re.compile(r"[a-f0-9]{40}\Z")
SHA = re.compile(r"[a-f0-9]{64}\Z")
BUILD = re.compile(r"[0-9]+(?:\.[0-9]+){3}\Z")
SEASON = re.compile(r"[a-z0-9][a-z0-9_-]{2,55}\Z")
MAX_MANIFEST = 64_000
SOURCE_HOSTS = {
    "blizzard_game_data_api":
        frozenset(("us.api.blizzard.com", "eu.api.blizzard.com",
                   "kr.api.blizzard.com", "tw.api.blizzard.com")),
    "wago_db2_build_snapshot": frozenset(("wago.tools",)),
    "simulationcraft_revision_source":
        frozenset(("raw.githubusercontent.com",)),
    "verified_public_item_source":
        frozenset(("wowhead.com", "www.wowhead.com")),
}
SOURCE_ROLE_SYSTEMS = {
    "gear": frozenset(("blizzard_game_data_api", "wago_db2_build_snapshot")),
    "tier": frozenset(("blizzard_game_data_api", "wago_db2_build_snapshot")),
    "budget": frozenset(("blizzard_game_data_api", "wago_db2_build_snapshot",
                          "verified_public_item_source")),
}


def _origin_url(system, raw, build, revision):
    """Validate recognizable source locators, not their claimed contents."""
    try:
        parsed = urlsplit(raw)
        host = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise SourceBundleBlocked("V225_SOURCE_URL_INVALID") from exc
    need(parsed.scheme == "https" and port in (None, 443) and
         host in SOURCE_HOSTS[system] and not parsed.username and
         not parsed.password and not parsed.fragment and
         not any(ord(c) < 32 or ord(c) == 127 for c in raw),
         "V225_SOURCE_ORIGIN_HOST_OR_PROTOCOL_NOT_ALLOWED")
    if system == "wago_db2_build_snapshot":
        need(parsed.path.startswith("/db2/") and
             parse_qs(parsed.query).get("build") == [build],
             "V225_DB2_SOURCE_EXPLICIT_BUILD_REQUIRED")
    elif system == "simulationcraft_revision_source":
        need(parsed.path.startswith(
            "/simulationcraft/simc/" + revision + "/"),
            "V225_SIMC_PINNED_REVISION_REQUIRED")
    elif system == "blizzard_game_data_api":
        need(parsed.path.startswith("/data/wow/") and
             bool(parsed.query), "V225_BLIZZARD_GAME_DATA_RESOURCE_REQUIRED")
    else:
        need(parsed.path.startswith("/item=") or
             parsed.path.startswith("/spell="),
             "V225_PUBLIC_ITEM_OR_SPELL_ID_RESOURCE_REQUIRED")
    return True


class SourceBundleBlocked(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise SourceBundleBlocked(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _safe_file(directory, filename):
    path = directory / filename
    need(not directory.is_symlink() and not path.is_symlink() and
         path.is_file() and path.parent == directory,
         "V225_UNSAFE_OR_MISSING_FIXED_SOURCE_FILE")
    return path


def _manifest(path):
    need(path.stat().st_size > 0 and path.stat().st_size <= MAX_MANIFEST,
         "V225_SOURCE_MANIFEST_SIZE")
    try:
        doc = json.loads(path.read_text(encoding="utf8"))
    except (ValueError, UnicodeError) as exc:
        raise SourceBundleBlocked("V225_SOURCE_MANIFEST_JSON_INVALID") from exc
    need(type(doc) is dict and set(doc) == {
        "schema", "event", "game_build", "previous_game_build",
        "expansion_id", "season", "simc_revision", "sources",
        "component_origins",
    } and doc["schema"] == SCHEMA and
         doc["event"] in EVENTS and
         type(doc["game_build"]) is str and BUILD.fullmatch(doc["game_build"]) and
         type(doc["previous_game_build"]) is str and
         BUILD.fullmatch(doc["previous_game_build"]) and
         type(doc["season"]) is str and SEASON.fullmatch(doc["season"]) and
         type(doc["simc_revision"]) is str and
         REV.fullmatch(doc["simc_revision"]) and
         type(doc["expansion_id"]) is int and
         doc["expansion_id"] > 0,
         "V225_SOURCE_MANIFEST_FIELDS_INVALID")
    return doc


def verify_bundle(*, folder, event, previous_game_build,
                  target_ilevel):
    """Return a provenance/inventory receipt, with all G/J/F/O still blocked.

    Trust boundary: source location metadata are declarations until compared
    with upstream Blizzard/DB2/SimC byte receipts by an independent verifier.
    """
    folder_path = pathlib.Path(folder).expanduser()
    need(not folder_path.is_symlink(),
         "V225_SOURCE_BUNDLE_FOLDER_SYMLINK")
    directory = folder_path.resolve()
    need(directory.is_dir() and not directory.is_symlink(),
         "V225_SOURCE_BUNDLE_FOLDER_MISSING")
    manifest_path = _safe_file(directory, "source_manifest.json")
    manifest = _manifest(manifest_path)
    need(manifest["event"] == event and
         manifest["previous_game_build"] == previous_game_build,
         "V225_REQUEST_EVENT_OR_PREVIOUS_BUILD_MISMATCH")
    sources = manifest["sources"]
    need(type(sources) is dict and set(sources) == set(SOURCE_FILES),
         "V225_GEAR_TIER_BUDGET_SOURCE_MANIFEST_REQUIRED")
    inputs = {}
    source_origins = {}
    for name, filename in SOURCE_FILES.items():
        row = sources[name]
        need(type(row) is dict and set(row) == {
            "filename", "sha256", "source_system", "source_locator",
            "source_build", "retrieval_receipt_sha256",
        } and row["filename"] == filename and
             type(row["sha256"]) is str and SHA.fullmatch(row["sha256"]) and
             row["source_system"] in SOURCE_ROLE_SYSTEMS[name] and
             type(row["source_build"]) is str and
             row["source_build"] == manifest["game_build"] and
             type(row["retrieval_receipt_sha256"]) is str and
             SHA.fullmatch(row["retrieval_receipt_sha256"]) and
             type(row["source_locator"]) is str and
             10 <= len(row["source_locator"]) <= 2048 and
             row["source_locator"].startswith("https://") and
             all(x not in row["source_locator"] for x in
                 ("\n", "\r", "\x00", "@")),
             "V225_SOURCE_ORIGIN_DECLARATION_INCOMPLETE:" + name)
        _origin_url(row["source_system"], row["source_locator"],
                    manifest["game_build"], manifest["simc_revision"])
        doc, file_sha = preflight.load(_safe_file(directory, filename))
        need(row["sha256"] == file_sha,
             "V225_SOURCE_BYTES_CHANGED_AFTER_RETRIEVAL:" + name)
        inputs[name] = (doc, file_sha)
        source_origins[name] = {
            "system": row["source_system"],
            "declared_locator": row["source_locator"],
            "declared_retrieval_receipt_sha256":
                row["retrieval_receipt_sha256"],
        }
    # A composite budget.json may derive J, F and O from DIFFERENT IDs,
    # source tables, and effect conditions. Record their paths separately;
    # one budget-file link is never evidence for all three components.
    component_origins = manifest["component_origins"]
    need(type(component_origins) is dict and
         set(component_origins) == set(COMPONENT_INPUTS),
         "V225_GJFO_COMPONENT_ORIGINS_REQUIRED")
    mapped_origins = {}
    for component, source_files in COMPONENT_INPUTS.items():
        row = component_origins[component]
        need(type(row) is dict and set(row) ==
             {"source_files", "candidate_sources"} and
             row["source_files"] == list(source_files) and
             type(row["candidate_sources"]) is list and
             1 <= len(row["candidate_sources"]) <= 6,
             "V225_GJFO_COMPONENT_INPUT_ROUTE_INVALID:" + component)
        mapped = []
        for source in row["candidate_sources"]:
            need(type(source) is dict and set(source) == {
                "source_system", "source_locator", "source_build",
                "retrieval_receipt_sha256", "item_ids",
            } and source.get("source_system") in SOURCE_SYSTEMS and
                 type(source.get("source_build")) is str and
                 source["source_build"] == manifest["game_build"] and
                 type(source.get("retrieval_receipt_sha256")) is str and
                 SHA.fullmatch(source["retrieval_receipt_sha256"]) and
                 type(source.get("source_locator")) is str and
                 10 <= len(source["source_locator"]) <= 2048 and
                 type(source.get("item_ids")) is list and
                 1 <= len(source["item_ids"]) <= 25 and
                 all(type(n) is int and n > 0 for n in
                     source["item_ids"]) and
                 len(set(source["item_ids"])) == len(source["item_ids"]),
                 "V225_GJFO_COMPONENT_SOURCE_RECORD_INVALID:" + component)
            _origin_url(source["source_system"], source["source_locator"],
                        manifest["game_build"], manifest["simc_revision"])
            mapped.append({
                "system": source["source_system"],
                "declared_locator": source["source_locator"],
                "item_ids": list(source["item_ids"]),
                "declared_retrieval_receipt_sha256":
                    source["retrieval_receipt_sha256"],
            })
        mapped_origins[component] = {
            "source_files": list(source_files),
            "candidate_sources": mapped,
            "source_identity_only_not_effect_proof": True,
        }
    try:
        checked = preflight.core_source_preflight(
            inputs=inputs, event=event,
            previous_game_build=previous_game_build,
            target_ilevel=target_ilevel)
    except preflight.SeasonEvidenceBlocked as exc:
        raise SourceBundleBlocked(
            "V225_CORE_SOURCE_PREFLIGHT_BLOCKED:" + str(exc)) from exc
    need(checked["game_build"] == manifest["game_build"] and
         inputs["gear"][0]["expansion_id"] == manifest["expansion_id"],
         "V225_MANIFEST_VS_SOURCE_BUILD_OR_EXPANSION_MISMATCH")
    output = {
        "schema": "v225_core_source_bundle_intake_receipt_v1",
        "status": "BYTES_LINKED_ORIGIN_AND_GJFO_RATINGS_NOT_AUTHENTICATED",
        "source_manifest_sha256": sha(manifest_path.read_bytes()),
        "event": event, "game_build": checked["game_build"],
        "previous_game_build": previous_game_build,
        "season": manifest["season"],
        "expansion_id": manifest["expansion_id"],
        "simc_revision": manifest["simc_revision"],
        "target_ilevel": target_ilevel,
        "source_input_sha256": checked["source_input_sha256"],
        "source_origins": source_origins,
        "component_origin_routes": mapped_origins,
        "core_preflight_sha256": checked["receipt_sha256"],
        "source_origin_independently_authenticated": False,
        "same_season_native_G_authenticated": False,
        "highest_quality_J_F_and_oil_O_authenticated": False,
        "verified_components": [],
        "missing_components": list(preflight.COMPONENTS),
        "G": None, "J": None, "F": None, "O": None,
        "B": None, "T": None,
        "ready": False, "user_options_auto_admitted": False,
        "native_calls": 0, "network_calls": 0,
        "cache_mutations": 0,
    }
    return {**output, "receipt_sha256": sha(canonical(output).encode("utf8"))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-dir", type=pathlib.Path, required=True)
    parser.add_argument("--event", choices=EVENTS, required=True)
    parser.add_argument("--previous-game-build", required=True)
    parser.add_argument("--target-ilevel", type=int, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args(argv)
    result = verify_bundle(
        folder=args.bundle_dir, event=args.event,
        previous_game_build=args.previous_game_build,
        target_ilevel=args.target_ilevel)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, sort_keys=True, indent=2,
                   ensure_ascii=False) + "\n", encoding="utf8")
    print("V225_CORE_SOURCE_BYTES_PINNED_GJFO_NOT_YET_VERIFIED",
          result["game_build"], result["source_manifest_sha256"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
