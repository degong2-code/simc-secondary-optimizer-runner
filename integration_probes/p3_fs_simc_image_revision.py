"""Read an exact SimC source-revision HINT from the matching official Docker tag.

This is a source pointer for the existing v229 Git-tree verification, not
a statement that the binary, generated tables or active game season match.
Only an identical immutable image digest can identify a release tag. No
latest-Git or old-season fallback is allowed.
"""
from __future__ import annotations

import json
import re
from urllib.request import Request, urlopen

API="https://hub.docker.com/v2/repositories/simulationcraftorg/simc/tags/?page_size=40"
DIGEST=re.compile(r"sha256:[a-f0-9]{64}\Z")
IMAGE=re.compile(r"simulationcraftorg/simc@(sha256:[a-f0-9]{64})\Z")
TAG=re.compile(r"(\d{3,4})-\d{4}-\d{2}-\d{2}-([a-f0-9]{7,12})\Z")
BUILD=re.compile(r"(\d+)\.(\d+)\.(\d+)\.(\d+)\Z")
MAX_BYTES=500_000


class SimCImageRevisionPending(ValueError):
    pass


def select_from_tags(*,document,image_ref,game_build):
    """O(number of tags); never guesses a revision from the date."""
    image=IMAGE.fullmatch(image_ref)
    build=BUILD.fullmatch(game_build)
    if image is None or build is None:
        raise SimCImageRevisionPending("SIMC_PINNED_IMAGE_OR_BUILD_REQUIRED")
    image_digest=image.group(1)
    expected_prefix="".join(str(int(x)) for x in build.groups()[:3])
    if type(document) is not dict or type(document.get("results")) is not list:
        raise SimCImageRevisionPending("SIMC_DOCKER_TAG_SOURCE_INVALID")
    matches=[]
    for row in document["results"]:
        if type(row) is not dict:
            raise SimCImageRevisionPending("SIMC_DOCKER_TAG_ROW_INVALID")
        name=row.get("name")
        tag=TAG.fullmatch(name) if type(name) is str else None
        if tag is None:
            continue
        digests=[row.get("digest")]
        for arch in row.get("images",[]) if type(row.get("images")) is list else []:
            if (type(arch) is dict and arch.get("architecture")=="amd64"
                and arch.get("os")=="linux"):
                digests.append(arch.get("digest"))
        if image_digest in digests and tag.group(1)==expected_prefix:
            matches.append((name,tag.group(2)))
    revisions={r for _,r in matches}
    if len(revisions)!=1:
        raise SimCImageRevisionPending(
            "SIMC_IMAGE_MATCHING_TAG_REVISION_NOT_UNIQUE_OR_MISSING")
    selected=sorted(matches)[-1]
    return {
        "status":"SIMC_IMAGE_DIGEST_TAG_SOURCE_POINTER_ONLY",
        "image_digest":image_digest,
        "source_tag":selected[0],
        "revision_hint":selected[1],
        "game_build_requested":game_build,
        "source_identity_not_binary_or_season_attestation":True,
    }


def discover(*,image_ref,game_build,fetch=urlopen):
    req=Request(API,headers={"Accept":"application/json",
                             "User-Agent":"simc-secondary-p3-fs/1"})
    try:
        with fetch(req,timeout=25) as reply:
            if reply.status!=200:
                raise SimCImageRevisionPending(
                    "SIMC_DOCKER_TAG_HTTP_STATUS_NOT_SUCCESS")
            raw=reply.read(MAX_BYTES+1)
        if not 0<len(raw)<=MAX_BYTES:
            raise SimCImageRevisionPending("SIMC_DOCKER_TAG_SIZE_INVALID")
        document=json.loads(raw)
    except (OSError,TimeoutError,UnicodeError,ValueError) as exc:
        if isinstance(exc,SimCImageRevisionPending):
            raise
        raise SimCImageRevisionPending(
            "SIMC_DOCKER_TAG_SOURCE_NOT_AVAILABLE") from exc
    return select_from_tags(document=document,image_ref=image_ref,
                            game_build=game_build)
