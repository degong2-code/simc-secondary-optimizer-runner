#!/usr/bin/env python3
"""v661: cache-hit gate and verified experimental release ZIP for the v658 builder.

Runs only in repository-owned Actions with an ephemeral GITHUB_TOKEN. This
does NOT expose a public build-request broker or install anything on user PCs.
The release is a source-pinned, self-built cache, never an official SimC build.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
from v193_simc_local_updater import MAX_ARCHIVE, nightly_identity
from v659_simc_self_built_artifact import inspect_artifact
from v660_simc_one_click_provision import REPO, published_candidates
from v658_generic_simc_win64_build import read_request

MAX_RELEASE_JSON = 300_000
FIXED = ("build_receipt.json", "source_proof.json", "display_build.txt")


class CacheBlocked(ValueError):
    pass


def need(condition, reason):
    if not condition:
        raise CacheBlocked(reason)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise CacheBlocked("CACHE_API_REDIRECT_BLOCKED")


def get_published_release(source_sha, *, opener=None):
    """404 means absent; TLS, HTTP, auth, redirect and data failures are fatal."""
    tag = "simc-cli-source-" + source_sha
    url = "https://api.github.com/repos/" + REPO + "/releases/tags/" + tag
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "SIMC-Secondary-SelfBuilt-Cache-Publisher/1.0",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers)
    open_request = opener or urllib.request.build_opener(_NoRedirect()).open
    try:
        with open_request(request, timeout=12) as response:
            need(response.status == 200 and response.geturl() == url,
                 "CACHE_API_ORIGIN_INVALID")
            raw = response.read(MAX_RELEASE_JSON + 1)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise CacheBlocked("CACHE_API_HTTP_" + str(exc.code)) from exc
    need(0 < len(raw) <= MAX_RELEASE_JSON, "CACHE_API_BODY_SIZE_INVALID")
    try:
        result = json.loads(raw)
    except (UnicodeError, ValueError) as exc:
        raise CacheBlocked("CACHE_API_JSON_INVALID") from exc
    need(type(result) is dict, "CACHE_API_SCHEMA_INVALID")
    return result


def cache_status(request, *, loader=None):
    """A malformed existing release blocks builds; never overwrite a tag."""
    doc = read_request(request)
    release = (loader or get_published_release)(doc["source_sha"])
    if release is None:
        return "CACHE_MISS"
    need(type(release) is dict
         and release.get("tag_name") == "simc-cli-source-" + doc["source_sha"]
         and release.get("draft") is False
         and release.get("prerelease") is True,
         "CACHE_EXISTING_RELEASE_UNTRUSTED")
    candidates = published_candidates(
        doc["game_build"], release_loader=lambda url: [release])
    need(len(candidates) == 1
         and candidates[0]["source_sha"] == doc["source_sha"]
         and candidates[0]["game_build"] == doc["game_build"],
         "CACHE_EXISTING_RELEASE_ASSET_INVALID")
    return "CACHE_HIT"


def make_release_zip(request, source_dir, output):
    """Package exactly the four v659-approved members; recheck every receipt."""
    doc = read_request(request)
    folder = pathlib.Path(source_dir)
    target = pathlib.Path(output)
    name = "simc-win64-cli-" + doc["source_sha"][:7] + "-" + doc["game_build"] + ".zip"
    need(target.name == name and not target.exists(),
         "CACHE_OUTPUT_PATH_OR_COLLISION")
    need(folder.is_dir() and not folder.is_symlink(),
         "CACHE_INPUT_DIRECTORY_INVALID")
    receipt_path = folder / "build_receipt.json"
    need(receipt_path.is_file() and not receipt_path.is_symlink()
         and 0 < receipt_path.stat().st_size <= 16_384,
         "CACHE_BUILD_RECEIPT_FILE_INVALID")
    try:
        receipt = json.loads(receipt_path.read_text("utf8"))
    except (UnicodeError, ValueError) as exc:
        raise CacheBlocked("CACHE_BUILD_RECEIPT_JSON_INVALID") from exc
    need(type(receipt) is dict
         and receipt.get("source_sha") == doc["source_sha"]
         and receipt.get("source_game_build") == doc["game_build"],
         "CACHE_BUILD_RECEIPT_IDENTITY_INVALID")
    archive = receipt.get("archive_name")
    need(type(archive) is str and nightly_identity(archive) is not None
         and archive.startswith("simc-") and archive.endswith("-win64.7z"),
         "CACHE_BUILD_ARCHIVE_NAME_INVALID")
    names = set(FIXED) | {archive}
    need({entry.name for entry in folder.iterdir()} == names,
         "CACHE_BUILD_EXTRA_OR_MISSING_MEMBERS")
    for member in names:
        path = folder / member
        bound = MAX_ARCHIVE if member == archive else 16_384
        need(path.is_file() and not path.is_symlink()
             and 0 < path.stat().st_size <= bound,
             "CACHE_BUILD_MEMBER_INVALID")
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_STORED) as packed:
            for member in sorted(names):
                packed.write(folder / member, arcname=member)
        proof = inspect_artifact(target)
        need(proof["source_sha"] == doc["source_sha"]
             and proof["game_build"] == doc["game_build"]
             and proof["origin_authenticated"] is False,
             "CACHE_PACKAGED_PROOF_INVALID")
        return proof["artifact_sha256"]
    except Exception:
        target.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("status", "package"))
    parser.add_argument("--request", required=True)
    parser.add_argument("--source-dir")
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.command == "status":
        print(cache_status(args.request))
    else:
        need(args.source_dir and args.output, "CACHE_PACKAGE_ARGUMENTS_MISSING")
        print("CACHE_PACKAGE_VERIFIED_SHA256",
              make_release_zip(args.request, args.source_dir, args.output))


if __name__ == "__main__":
    try:
        main()
    except (CacheBlocked, ValueError, OSError, TypeError, KeyError,
            urllib.error.URLError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
