"""v660: one-click SimC binary provisioner (no credentials or compiler on user PC).

Official compatible nightly -> validated local managed binary reuse -> trusted
public *self-built* release cache -> explicit unmet remote-builder state.
There is deliberately NO anonymous GitHub Actions dispatch: the API requires
repository-write credentials and must never ship a token to local clients.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

import v193_simc_local_updater as updater
from v659_simc_self_built_artifact import inspect_artifact, MAX_ARTIFACT

REPO="degong2-code/simc-secondary-optimizer-runner"
API="https://api.github.com/repos/"+REPO+"/releases?per_page=20"
MAX_RELEASE_INDEX=300_000
MAX_RELEASE_SCAN=20
RELEASE_TAG=re.compile(r"simc-cli-source-([a-f0-9]{40})\Z")
ASSET_NAME=re.compile(r"simc-win64-cli-([a-f0-9]{7})-(\d+(?:\.\d+){3})\.zip\Z")
DIGEST=re.compile(r"sha256:([a-f0-9]{64})\Z")
ALLOWED_REDIRECTS={"github.com","release-assets.githubusercontent.com",
                   "objects.githubusercontent.com"}
SCHEMA="v660_simc_one_click_provision_v1"

class ProvisionBlocked(ValueError):pass
def need(ok,code):
    if not ok:raise ProvisionBlocked(code)

def _url_secure(url, *, must_api=False):
    parts=urllib.parse.urlsplit(url)
    need(parts.scheme=="https" and parts.hostname in
         ({"api.github.com"} if must_api else ALLOWED_REDIRECTS)
         and parts.username is None and parts.password is None
         and (parts.port is None or parts.port==443),
         "SELF_BUILT_RELEASE_URL_UNTRUSTED")

class _RedirectGuard(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        _url_secure(newurl)
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def _get_json(url,*,opener=None):
    _url_secure(url,must_api=True)
    need(url==API,"SELF_BUILT_RELEASE_API_INVALID")
    req=urllib.request.Request(url,headers={
        "Accept":"application/vnd.github+json",
        "User-Agent":"SIMC-Secondary-Update-Manager/1.0"})
    request=open_url(opener)
    with request(req,timeout=12) as response:
        need(response.status==200 and response.geturl()==url,
             "SELF_BUILT_RELEASE_API_REDIRECT_INVALID")
        data=response.read(MAX_RELEASE_INDEX+1)
    need(0<len(data)<=MAX_RELEASE_INDEX,
         "SELF_BUILT_RELEASE_INDEX_SIZE_INVALID")
    try:out=json.loads(data)
    except (ValueError,UnicodeError) as exc:
        raise ProvisionBlocked("SELF_BUILT_RELEASE_INDEX_JSON_INVALID") from exc
    need(type(out) is list,"SELF_BUILT_RELEASE_INDEX_SCHEMA_INVALID")
    return out[:MAX_RELEASE_SCAN]

def open_url(opener):
    if opener is None:
        return urllib.request.build_opener(_RedirectGuard()).open
    return opener

def published_candidates(game_build,*,release_loader=None):
    """An index item only; the source SHA and ZIP remain separately unverified."""
    need(type(game_build) is str and updater.EXACT_BUILD.fullmatch(game_build),
         "SELF_BUILT_GAME_BUILD_INVALID")
    releases=(release_loader or _get_json)(API)
    need(type(releases) is list,"SELF_BUILT_RELEASE_INDEX_SCHEMA_INVALID")
    out=[]
    for release in releases[:MAX_RELEASE_SCAN]:
        if type(release) is not dict or release.get("draft") is not False:
            continue
        tag=release.get("tag_name")
        match=RELEASE_TAG.fullmatch(tag) if type(tag) is str else None
        if match is None:continue
        full=match.group(1)
        assets=release.get("assets",[])
        if type(assets) is not list:continue
        target="simc-win64-cli-"+full[:7]+"-"+game_build+".zip"
        for asset in assets[:30]:
            if type(asset) is not dict or asset.get("name")!=target:
                continue
            digest=asset.get("digest")
            check=DIGEST.fullmatch(digest) if type(digest) is str else None
            url=asset.get("browser_download_url")
            expected=("https://github.com/"+REPO+"/releases/download/"+
                      tag+"/"+target)
            if (check is None or type(url) is not str or url!=expected or
                asset.get("state")!="uploaded" or
                type(asset.get("size")) is not int or
                not 100000<asset["size"]<=MAX_ARTIFACT):
                continue
            out.append({"source_sha":full,"game_build":game_build,
                        "archive_url":url,"artifact_sha256":check.group(1),
                        "artifact_bytes":asset["size"],
                        "asset_id":asset.get("id"),
                        "origin":"PUBLIC_REPO_SELF_BUILT_RELEASE_NOT_SIMC_OFFICIAL"})
    return out

def download_release_zip(candidate,target,*,open_url_override=None):
    """Bounded HTTPS public GitHub asset, digest from separate GitHub API."""
    url=candidate["archive_url"]
    need(type(url) is str and url.startswith("https://github.com/"+REPO+
         "/releases/download/"),"SELF_BUILT_DOWNLOAD_URL_INVALID")
    _url_secure(url)
    need(type(candidate["artifact_sha256"]) is str and
         re.fullmatch(r"[a-f0-9]{64}",candidate["artifact_sha256"]),
         "SELF_BUILT_DOWNLOAD_SHA_INVALID")
    req=urllib.request.Request(url,headers={
        "User-Agent":"SIMC-Secondary-Update-Manager/1.0"})
    h=hashlib.sha256();length=0
    with open_url(open_url_override)(req,timeout=90) as response,open(target,"wb") as dst:
        _url_secure(response.geturl())
        need(response.status==200,"SELF_BUILT_DOWNLOAD_HTTP_INVALID")
        while True:
            blob=response.read(1024*1024)
            if not blob:break
            length+=len(blob)
            need(length<=MAX_ARTIFACT,
                 "SELF_BUILT_DOWNLOAD_TOO_LARGE")
            h.update(blob);dst.write(blob)
    need(length==candidate["artifact_bytes"] and
         h.hexdigest()==candidate["artifact_sha256"],
         "SELF_BUILT_DOWNLOAD_DIGEST_MISMATCH")
    return str(target)

def _match_live(live):
    need(type(live) is dict
         and live.get("status")=="LIVE_RETAIL_BUILD_SOURCE_OBSERVED"
         and live.get("region")=="KR"
         and type(live.get("game_build")) is str and
         updater.EXACT_BUILD.fullmatch(live["game_build"]),
         "SIMC_LIVE_GAME_BUILD_UNKNOWN")
    return live["game_build"]

def prepare_one_click(manager,*,live_loader=None,
                      release_loader=None,archive_loader=None,
                      official_checker=None,source_loader=None,
                      sevenzip=None,cli_probe=None):
    """Synchronous, explicit-user-action only. No background build or Native DPS."""
    need(manager.platform=="win32","SIMC_UPDATER_WINDOWS_ONLY")
    from v289_retail_live_build_source import discover
    live=(live_loader or discover)(region="KR")
    current_build=_match_live(live)
    current=manager.status()
    installed=current.get("installed") or {}
    # Existing managed self-built source was checked at its first installation.
    # Never trust a saved label alone; re-run actual CLI display_build.
    if (current.get("active_binary") and
        installed.get("source_game_build")==current_build and
        re.fullmatch(r"[a-f0-9]{40}",
                     str(installed.get("source_revision_full","")))):
        (cli_probe or updater.probe_cli)(current["active_binary"],
                                         expected_build=current_build)
        return {"schema":SCHEMA,"status":"ALREADY_COMPATIBLE_MANAGED",
                "active_binary":current["active_binary"],
                "installed":installed,"game_build":current_build,
                "native_dps_calls_now":0,"new_compilation":False}
    # The stock candidate selection maintains its existing time-limited offer.
    if official_checker is None:
        checked=manager.check_for_retail_compatibility(
            live_loader=lambda region:live,source_loader=source_loader)
    else:
        checked=official_checker(live)
    comp=checked.get("retail_compatibility") or {}
    official=checked.get("candidate")
    if (comp.get("status")=="SOURCE_BUILD_MATCHED_BINARY_UNVERIFIED"
         and type(official) is dict):
        filename=official["filename"]
        result=manager.install(
            filename,sevenzip=sevenzip,
            probe=lambda exe:(cli_probe or updater.probe_cli)(
                exe,expected_build=current_build))
        return {"schema":SCHEMA,"status":"OFFICIAL_BINARY_INSTALLED",
                "installed":result.get("installed"),
                "active_binary":result.get("active_binary"),
                "game_build":current_build,
                "native_dps_calls_now":0,"new_compilation":False,
                "provision_origin":"OFFICIAL_HTTPS_NIGHTLY"}
    # A public repo release is a *cache*, never SimulationCraft's own release.
    errors=0
    try:
        candidates=published_candidates(current_build,release_loader=release_loader)
    except (ProvisionBlocked,OSError,TimeoutError,urllib.error.URLError,ValueError):
        candidates=[];errors+=1
    for candidate in candidates[:8]:
        try:
            proof=manager._candidate_source_proof(
                candidate["source_sha"],current_build,source_loader=source_loader)
            if (proof.get("source_build")!=current_build
                or proof.get("source_headers_checked")!=3):
                continue
            with tempfile.TemporaryDirectory(prefix="simc-public-build-") as td:
                file=pathlib.Path(td)/"simc-win64-cli.zip"
                (archive_loader or download_release_zip)(candidate,file)
                inner=inspect_artifact(file)
                need(inner["source_sha"]==candidate["source_sha"] and
                     inner["game_build"]==current_build,
                     "SELF_BUILT_RELEASE_RECEIPT_SOURCE_MISMATCH")
                result=manager.install_self_built(
                    str(file),sevenzip=sevenzip,probe=cli_probe)
            return {"schema":SCHEMA,"status":"PUBLIC_SELF_BUILT_BINARY_INSTALLED",
                    "installed":result.get("installed"),
                    "active_binary":result.get("active_binary"),
                    "game_build":current_build,
                    "native_dps_calls_now":0,"new_compilation":False,
                    "provision_origin":"PUBLIC_REPO_SELF_BUILT_RELEASE_NOT_SIMC_OFFICIAL"}
        except (ProvisionBlocked,updater.UpdateBlocked,OSError,TimeoutError,
                urllib.error.URLError,ValueError,KeyError):
            errors+=1
            continue
    # No anonymous GitHub write authority exists in a user's clean install.
    # Do not pretend this schedules or executes a build.
    source=comp.get("source_only_candidate")
    return {"schema":SCHEMA,
            "status":"SOURCE_BUILD_REQUIRES_REMOTE_BUILDER" if source else
                     "NO_COMPATIBLE_BINARY_AVAILABLE",
            "active_binary":current.get("active_binary"),
            "installed":installed or None,
            "game_build":current_build,
            "source_only_candidate":source if isinstance(source,dict) else None,
            "public_release_candidates_checked":len(candidates),
            "public_release_errors":errors,
            "server_build_trigger_available":False,
            "reason":"NO_ANONYMOUS_GITHUB_ACTIONS_DISPATCH",
            "native_dps_calls_now":0,"new_compilation":False}
