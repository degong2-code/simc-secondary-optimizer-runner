"""Minimal live Retail build identity from Blizzard's public product versions.

Used only when the season-wide web Build omits a game_build. This is source
identity, not a declaration that the game's new season, items or SimC sources
are independently ready. The original v216 source and installer still decide.
"""
from __future__ import annotations

import hashlib
import re
from urllib.request import Request, urlopen

URL="https://us.version.battle.net/wow/versions"
VERSION=re.compile(r"[0-9]+(?:\.[0-9]+){3}\Z")
MAX_RESPONSE=65536

class RetailVersionBlocked(ValueError):
    pass

def parse(payload, *, region="KR"):
    if type(payload) is not bytes or not 0<len(payload)<=MAX_RESPONSE:
        raise RetailVersionBlocked("RETAIL_VERSION_SOURCE_BYTES_INVALID")
    try:
        lines=payload.decode("utf-8-sig").splitlines()
        header=[x.split("!",1)[0].strip() for x in lines[0].split("|")]
        fields={name:i for i,name in enumerate(header)}
        version_key=next(
            name for name in ("VersionsName","VersionName")
            if name in fields)
        for name in ("Region","BuildId",version_key):
            if name not in fields:
                raise KeyError(name)
        rows=[]
        for line in lines[1:]:
            # Official Blizzard BPSV has a typed header and ## seqn comment.
            if not line or line.startswith("#"):
                continue
            cols=[x.strip() for x in line.split("|")]
            if len(cols)!=len(header) or cols[fields["Region"]].upper()!=region:
                continue
            version=cols[fields[version_key]]
            build_id=cols[fields["BuildId"]]
            if VERSION.fullmatch(version) is None or (
                    not build_id.isdigit() or
                    int(build_id)!=int(version.rsplit(".",1)[-1])):
                raise RetailVersionBlocked(
                    "RETAIL_VERSION_REGION_BUILD_ID_MISMATCH")
            rows.append(version)
        if len(rows)!=1:
            raise RetailVersionBlocked(
                "RETAIL_VERSION_REGION_MISSING_OR_AMBIGUOUS")
    except (UnicodeError,IndexError,StopIteration,KeyError,ValueError) as e:
        if isinstance(e,RetailVersionBlocked):
            raise
        raise RetailVersionBlocked(
            "RETAIL_VERSION_SOURCE_FORMAT_INVALID") from e
    return {
        "schema":"v289_blizzard_public_retail_version_v1",
        "status":"LIVE_RETAIL_BUILD_SOURCE_OBSERVED",
        "game_build":rows[0],"region":region,
        "product":"wow","source_url":URL,
        "source_sha256":hashlib.sha256(payload).hexdigest(),
        "season_and_item_evidence_verified":False,
        "simc_binary_matched":False,
        "environment_ready":False}

def discover(*,fetch=None,region="KR"):
    if region not in ("KR","US","EU"):
        raise RetailVersionBlocked("RETAIL_VERSION_REGION_UNSUPPORTED")
    getter=fetch or urlopen
    request=Request(URL,headers={
        "User-Agent":"SIMC-Secondary-Optimizer/1.0",
        "Accept":"text/plain"})
    try:
        with getter(request,timeout=15) as response:
            if getattr(response,"status",200)!=200:
                raise RetailVersionBlocked(
                    "RETAIL_VERSION_HTTP_STATUS_NOT_SUCCESS")
            raw=response.read(MAX_RESPONSE+1)
    except (OSError,TimeoutError) as e:
        raise RetailVersionBlocked(
            "RETAIL_VERSION_LIVE_SOURCE_UNAVAILABLE") from e
    return parse(raw,region=region)
