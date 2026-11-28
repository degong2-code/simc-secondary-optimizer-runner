#!/usr/bin/env python3
"""v665: optional, source-bound official item ICONS for displayed gear only.

This is presentation metadata. It neither certifies an item's season membership
nor changes source catalogues, CHMV, profiles, cache identity or SimC execution.
Uses the user's existing local Blizzard credentials; no browser token exposure.
"""
from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit

import v155_season_api_probe as blizzard

SCHEMA="v665_official_blizzard_item_media_icons_v1"
MEDIA="https://kr.api.blizzard.com/data/wow/media/item/"
SUFFIX="?namespace=static-kr"
MAX_ITEMS=80
MAX_VISIBLE_ITEMS=2048
MAX_NEW_MEDIA_PER_REQUEST=160
ICON_PATH=re.compile(r"/[a-z]{2}/icons/(?:18|36|56|64|128)/[a-z0-9_/-]+\.(?:jpg|png|webp)\Z")

class IconBlocked(ValueError):pass

def need(value,why):
    if not value:raise IconBlocked(why)

def media_url(item_id):
    need(type(item_id) is int and 1<=item_id<=999999999,
         "ICON_ITEM_ID_INVALID")
    return MEDIA+str(item_id)+SUFFIX

def verified_icon_url(item_id,document):
    need(type(document) is dict and document.get("id")==item_id,
         "ICON_PROVIDER_ITEM_ID_MISMATCH")
    assets=document.get("assets")
    need(type(assets) is list and len(assets)<=16,
         "ICON_PROVIDER_ASSETS_INVALID")
    icons=[x.get("value") for x in assets if type(x) is dict
           and x.get("key")=="icon"]
    need(len(icons)==1 and type(icons[0]) is str and len(icons[0])<=320,
         "ICON_PROVIDER_ICON_MISSING")
    url=icons[0]
    parsed=urlsplit(url)
    need(parsed.scheme=="https" and parsed.hostname=="render.worldofwarcraft.com"
         and parsed.port is None and parsed.username is None
         and parsed.password is None and not parsed.query and
         not parsed.fragment and ICON_PATH.fullmatch(parsed.path) is not None,
         "ICON_MEDIA_URL_NOT_OFFICIAL")
    return url

def collect(item_ids,credentials,*,token_loader=None,reader=None):
    """One bounded batch; partial icon failure never blocks real product use."""
    ids=sorted(set(item_ids))
    need(0<len(ids)<=MAX_ITEMS and all(type(i) is int and
         1<=i<=999999999 for i in ids),"ICON_ITEM_BATCH_INVALID")
    return _collect_validated(ids,credentials,token_loader=token_loader,reader=reader)

def collect_display(item_ids,credentials,cache,*,token_loader=None,reader=None):
    """Exact visible IDs, successful same-build cache, bounded missing-only fetch.

    Caller owns season scoping and the lock. A partial result is never cached
    as a completed list: missing IDs may be retried on a subsequent request.
    """
    ids=sorted(set(item_ids))
    need(0<len(ids)<=MAX_VISIBLE_ITEMS and all(type(i) is int and
         1<=i<=999999999 for i in ids),"ICON_VISIBLE_IDS_INVALID")
    missing=[i for i in ids if str(i) not in cache]
    query=missing[:MAX_NEW_MEDIA_PER_REQUEST]
    fresh=(_collect_validated(query,credentials,token_loader=token_loader,reader=reader)
           if query else {"icons":{},"network_calls_now":0,"status":"COMPLETE"})
    cache.update(fresh["icons"])
    visible={str(i):cache[str(i)] for i in ids if str(i) in cache}
    status=("COMPLETE" if len(visible)==len(ids) else
            fresh["status"] if not visible and fresh["status"] in
                ("CREDENTIALS_NOT_CONFIGURED","MEDIA_PROVIDER_UNAVAILABLE") else "PARTIAL")
    return {"schema":SCHEMA,"status":status,"icons":visible,
            "requested":len(ids),"pending":len(ids)-len(visible),
            "network_calls_now":fresh["network_calls_now"],"native_calls":0,
            "display_only":True,"cached":not missing}

def _collect_validated(ids,credentials,*,token_loader=None,reader=None):
    expected=("BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET")
    if not isinstance(credentials,dict) or not all(
            type(credentials.get(k)) is str and credentials[k] for k in expected):
        return {"schema":SCHEMA,"status":"CREDENTIALS_NOT_CONFIGURED",
                "icons":{},"requested":len(ids),"network_calls_now":0,
                "native_calls":0,"display_only":True}
    acquire=token_loader or (
        lambda cid,secret:blizzard.oauth_token(
            blizzard.BLIZZARD_TOKEN_URL,cid,secret))
    fetch=reader or blizzard.request_json
    try:
        token=acquire(credentials[expected[0]],credentials[expected[1]])
        need(type(token) is str and bool(token),"ICON_OAUTH_TOKEN_MISSING")
    except (Exception,):
        return {"schema":SCHEMA,"status":"MEDIA_PROVIDER_UNAVAILABLE",
                "icons":{},"requested":len(ids),"network_calls_now":1,
                "native_calls":0,"display_only":True}
    def one(item_id):
        try:
            document=fetch(media_url(item_id),headers={
                "Authorization":"Bearer "+token})
            return item_id,verified_icon_url(item_id,document)
        except Exception:
            return item_id,None
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(one,ids))
    icons={str(i):url for i,url in results if url is not None}
    return {"schema":SCHEMA,
            "status":"COMPLETE" if len(icons)==len(ids) else "PARTIAL",
            "icons":icons,"requested":len(ids),
            "network_calls_now":1+len(ids),
            "native_calls":0,"display_only":True}
